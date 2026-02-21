"""Encounter generation service - bridges engine and database.

Phase 11B: When difficulty is None (default), the Director AI automatically
computes the optimal difficulty based on party state, intensity curve,
party strength, affix costs, and run-local PPC.
"""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.encounter.pipeline import (
    EncounterProposal,
    PipelineInput,
    generate_encounter,
)
from app.engine.narrative.floor_narrative import generate_encounter_narrative
from app.models.arena import Arena
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.floor import Floor
from app.models.monster import Monster
from app.models.run import Run
from app.schemas.campaign import CampaignSettings
from app.services.difficulty_service import compute_arena_difficulty


async def get_monsters_as_dicts(db: AsyncSession) -> list[dict]:
    """Load all monsters as dicts for the encounter engine."""
    result = await db.execute(select(Monster))
    monsters = result.scalars().all()
    return [
        {
            "id": m.id,
            "slug": m.slug,
            "name": m.name,
            "cr": m.cr,
            "xp": m.xp,
            "hp": m.hp,
            "ac": m.ac,
            "tactical_role": m.tactical_role,
            "secondary_role": m.secondary_role,
            "vulnerabilities": m.vulnerabilities or [],
            "weak_saves": m.weak_saves or [],
            "environments": m.environments or [],
            "creature_type": m.creature_type,
            "size": m.size,
            "mechanical_signature": m.mechanical_signature or {},
            "statblock": m.statblock or {},
        }
        for m in monsters
    ]


def _get_campaign_settings(campaign: Campaign) -> CampaignSettings:
    """Parse campaign settings with defaults."""
    raw = campaign.settings or {}
    return CampaignSettings(**raw)


async def generate_encounter_for_arena(
    db: AsyncSession,
    arena: Arena,
    floor: Floor,
    run: Run,
    campaign_id: str,
    difficulty: str | None = None,
    template_name: str | None = None,
    environment: str | None = None,
    objective: str | None = None,
) -> EncounterProposal:
    """Generate an encounter for a specific arena.

    When difficulty is None, the Director AI computes the optimal difficulty
    using intensity curves, health snapshots, party strength, affix costs,
    and run-local PPC adjustments.
    """
    # Load campaign settings
    campaign = await db.get(Campaign, campaign_id)
    settings = _get_campaign_settings(campaign) if campaign else CampaignSettings()

    # Get party info
    char_result = await db.execute(select(Character).where(Character.campaign_id == campaign_id))
    characters = char_result.scalars().all()
    party_size = len(characters)
    party_level = run.starting_level

    # Director AI notes to pass through to the proposal
    difficulty_notes: list[str] = []
    base_intensity = 0.0
    adjusted_intensity = 0.0
    effective_multiplier = settings.difficulty_multiplier

    # Phase 11B: Auto-compute difficulty via Director AI when not specified
    if difficulty is None and campaign:
        target = await compute_arena_difficulty(db, arena, floor, run, campaign)
        difficulty = target.difficulty
        effective_multiplier = settings.difficulty_multiplier * target.xp_multiplier
        difficulty_notes = target.notes
        base_intensity = target.base_intensity
        adjusted_intensity = target.adjusted_intensity

        # Phase 11C: Use effective party level from strength computation
        try:
            from app.engine.difficulty.party_strength import compute_party_strength

            strength = await compute_party_strength(db, campaign_id, run.starting_level)
            party_level = strength.effective_level
            effective_multiplier *= strength.strength_multiplier
            difficulty_notes.extend(strength.notes)
        except Exception:
            pass  # Fall back to starting_level if strength computation fails

        # Phase 11D: Apply affix XP cost offset
        active_affixes = floor.active_affixes or []
        if active_affixes:
            try:
                from app.engine.difficulty.affix_cost import compute_affix_difficulty_offset

                affix_offset = compute_affix_difficulty_offset(active_affixes)
                if affix_offset != 0.0:
                    effective_multiplier *= 1.0 + affix_offset
                    difficulty_notes.append(
                        f"Affix cost offset: {affix_offset:+.0%} "
                        f"(affixes make creatures harder, reducing budget)"
                    )
            except Exception:
                pass

        # Phase 11E: Run-local PPC adjustment
        try:
            from app.engine.difficulty.party_power import compute_run_local_adjustment
            from app.models.snapshot import HealthSnapshot

            # Load all snapshots from current run (across all floors)
            snap_result = await db.execute(
                select(HealthSnapshot)
                .join(Floor, HealthSnapshot.floor_id == Floor.id)
                .where(Floor.run_id == run.id)
                .order_by(HealthSnapshot.after_arena_number)
            )
            run_snapshots = snap_result.scalars().all()
            if run_snapshots:
                snapshot_dicts = [
                    {
                        "dm_combat_perception": getattr(s, "dm_combat_perception", None),
                        "average_hp_percentage": s.average_hp_percentage,
                        "any_dead": s.any_dead,
                    }
                    for s in run_snapshots
                ]
                run_local = compute_run_local_adjustment(snapshot_dicts)
                if abs(run_local) > 0.001:
                    # Apply run-local as a multiplier: positive = harder, negative = easier
                    effective_multiplier *= 1.0 + run_local
                    difficulty_notes.append(f"Run-local PPC adjustment: {run_local:+.3f}")
        except Exception:
            pass
    else:
        # Manual difficulty override — use as-is
        if difficulty is None:
            difficulty = "moderate"

    # Gather party damage types for exploit scoring
    party_damage_types = []
    for char in characters:
        if char.damage_types:
            party_damage_types.extend(char.damage_types)
    party_damage_types = list(set(party_damage_types))

    # Get templates already used this floor
    templates_used = floor.templates_used or []

    # Get objectives already used this floor (Phase 7A)
    used_objectives = floor.objectives_used or []

    # Get active affixes for this floor (Phase 7B)
    active_affixes = floor.active_affixes or []

    # Detect boss encounter (last arena of last floor)
    is_boss = arena.arena_number == floor.arena_count and floor.floor_number == run.floor_count

    # Load monsters
    monsters = await get_monsters_as_dicts(db)

    # Floor biome: select once per floor, then persist
    biome_constraint: str | None = None
    used_environments: list[str] = []

    if not floor.floor_biome:
        from app.engine.encounter.environment_selector import select_floor_biome

        floor.floor_biome = select_floor_biome(
            floor.floor_number,
            party_level,
            monsters,
        )
        await db.flush()

    biome_constraint = floor.floor_biome

    # Floor theme: select once per floor, then persist (strict enforcement)
    if not floor.floor_theme:
        from app.data.encounter_themes import select_theme_for_floor

        # Get themes used on recent floors
        recent_floors = await db.execute(
            select(Floor)
            .where(Floor.run_id == run.id, Floor.floor_number < floor.floor_number)
            .order_by(Floor.floor_number.desc())
            .limit(3)
        )
        used_themes = [
            f.floor_theme for f in recent_floors.scalars().all() if f.floor_theme
        ]
        theme_def = select_theme_for_floor(
            biome=floor.floor_biome,
            floor_number=floor.floor_number,
            used_themes=used_themes,
        )
        if theme_def:
            floor.floor_theme = theme_def.id
        await db.flush()

    # Build used_environments from existing arenas on this floor
    existing_arenas_result = await db.execute(select(Arena).where(Arena.floor_id == floor.id))
    for existing_arena in existing_arenas_result.scalars().all():
        if existing_arena.environment and existing_arena.id != arena.id:
            used_environments.append(existing_arena.environment)

    # Use environment preference from settings if not explicitly overridden
    effective_environment = environment or settings.environment_preference

    # Compute arena arc position
    if arena.arena_number == 1:
        arc_position = "opener"
    elif arena.arena_number == floor.arena_count:
        arc_position = "climax"
    else:
        arc_position = "middle"

    # Build pipeline input
    inp = PipelineInput(
        party_level=party_level,
        party_size=max(party_size, 1),
        difficulty=difficulty,
        floor_number=floor.floor_number,
        arena_number=arena.arena_number,
        template_name=template_name,
        environment=effective_environment,
        templates_used=templates_used,
        party_damage_types=party_damage_types,
        difficulty_multiplier=effective_multiplier,
        xp_budget_multiplier=settings.xp_budget_multiplier,
        early_game_scaling_factor=settings.early_game_scaling_factor,
        objective=objective,
        used_objectives=used_objectives,
        is_boss=is_boss,
        active_affixes=active_affixes,
        biome_constraint=biome_constraint,
        used_environments=used_environments,
        floor_theme=floor.floor_theme,
        arena_arc_position=arc_position,
    )

    # Seed RNG for reproducible encounters based on run seed
    if run.seed:
        encounter_seed = run.seed + floor.floor_number * 1000 + arena.arena_number
        random.seed(encounter_seed)

    proposal = generate_encounter(inp, monsters)

    # Restore default random state
    if run.seed:
        random.seed()

    # Attach Director notes to proposal
    proposal.difficulty_notes = difficulty_notes
    proposal.base_intensity = base_intensity
    proposal.adjusted_intensity = adjusted_intensity

    # Generate narrative content
    _attach_narrative(
        proposal, floor.floor_number, arena.arena_number,
        floor.arena_count, arc_position,
    )

    return proposal


def _attach_narrative(
    proposal: EncounterProposal,
    floor_number: int,
    arena_number: int,
    total_arenas: int,
    arc_position: str = "middle",
) -> None:
    """Generate and attach narrative content to an encounter proposal."""
    # Build creature dicts for the narrative engine
    creature_dicts = [
        {
            "monster_id": c.monster_id,
            "name": c.name,
            "tactical_role": c.tactical_role,
            "creature_type": c.creature_type,
            "count": c.count,
            "vulnerabilities": c.vulnerabilities,
            "weak_saves": c.weak_saves,
        }
        for c in proposal.creatures
    ]

    # Classify objective category from objective name
    obj_category = "combat"
    obj_name_lower = proposal.objective_name.lower()
    if any(kw in obj_name_lower for kw in ("defend", "escort", "protect", "hold", "survive")):
        obj_category = "tactical"
    elif any(kw in obj_name_lower for kw in ("explore", "find", "collect", "retrieve", "puzzle")):
        obj_category = "exploration"

    narrative = generate_encounter_narrative(
        template_name=proposal.template,
        danger_rating=proposal.danger_rating,
        environment_key=proposal.environment,
        floor_number=floor_number,
        arena_number=arena_number,
        total_arenas=total_arenas,
        creatures=creature_dicts,
        objective_category=obj_category,
        theme_name=proposal.theme_name,
        theme_id=proposal.theme_id,
        arc_position=arc_position,
    )

    # Attach to proposal
    proposal.read_aloud_text = narrative.read_aloud.full_text
    proposal.encounter_hook = narrative.encounter_hook
    proposal.dm_guidance_boxes = [
        {"title": box.title, "content": box.content, "category": box.category}
        for box in narrative.dm_guidance_boxes
    ]
    proposal.creature_flavor = [
        {
            "monster_id": cf.monster_id,
            "name": cf.name,
            "personality": cf.personality,
            "behavior": cf.behavior,
            "arena_reason": cf.arena_reason,
        }
        for cf in narrative.creature_flavor
    ]
    proposal.weakness_tips = [tip.tip_text for tip in narrative.weakness_tips]
    proposal.roguelike_reference = narrative.roguelike_reference
