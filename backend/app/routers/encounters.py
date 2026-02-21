"""Encounter generation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.floor_affixes import get_affix
from app.database import get_db
from app.models.arena import Arena, ArenaCreatureStatus
from app.models.floor import Floor
from app.models.monster import Monster
from app.models.run import Run
from app.services.encounter_service import generate_encounter_for_arena

router = APIRouter(prefix="/arenas/{arena_id}/encounter", tags=["encounters"])


class EncounterCreatureResponse(BaseModel):
    monster_id: str
    name: str
    cr: float
    hp: int
    ac: int
    tactical_role: str
    count: int
    xp_each: int
    statblock: dict = {}


class EncounterWarningResponse(BaseModel):
    level: str
    message: str
    creature_id: str = ""


class AffixDetail(BaseModel):
    id: str
    name: str
    category: str
    description: str
    flavor_text: str = ""


class EncounterProposalResponse(BaseModel):
    creatures: list[EncounterCreatureResponse]
    template: str
    xp_budget: int
    adjusted_xp: int
    difficulty_tier: str
    tactical_brief: str
    warnings: list[EncounterWarningResponse]
    creature_count: int
    environment: str = ""
    environment_name: str = ""
    terrain_features: list[str] = []
    map_suggestions: list[str] = []
    # Objective (Phase 7A)
    objective_id: str = ""
    objective_name: str = ""
    objective_description: str = ""
    objective_dm_instructions: str = ""
    objective_win_conditions: list[str] = []
    objective_special_rules: list[str] = []
    objective_bonus_rewards: dict = {}
    # Floor affixes (Phase 7B)
    active_affixes: list[str] = []
    affix_details: list[AffixDetail] = []
    affix_modified_stats: dict = {}
    # Director AI notes (Phase 11B)
    difficulty_notes: list[str] = []
    base_intensity: float = 0.0
    adjusted_intensity: float = 0.0
    # Encounter theme (Phase 12I)
    theme_id: str = ""
    theme_name: str = ""
    # Danger rating (tiered label replacing binary warning)
    danger_rating: str = ""
    # Narrative content (Dynamic Sourcebook)
    read_aloud_text: str = ""
    encounter_hook: str = ""
    dm_guidance_boxes: list[dict] = []
    creature_flavor: list[dict] = []
    weakness_tips: list[str] = []
    roguelike_reference: dict = {}


class ObjectiveProgressUpdate(BaseModel):
    """Body for updating objective progress mid-combat."""

    progress: dict


@router.post("/generate", response_model=EncounterProposalResponse)
async def generate_encounter(
    arena_id: str,
    difficulty: str | None = Query(default=None),
    template: str | None = None,
    environment: str | None = None,
    objective: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Generate an encounter proposal for this arena."""
    # Get arena -> floor -> run -> campaign chain
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    floor = await db.get(Floor, arena.floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run_result = await db.execute(select(Run).where(Run.id == floor.run_id))
    run = run_result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Generate encounter
    proposal = await generate_encounter_for_arena(
        db=db,
        arena=arena,
        floor=floor,
        run=run,
        campaign_id=run.campaign_id,
        difficulty=difficulty,
        template_name=template,
        environment=environment,
        objective=objective,
    )

    # Look up statblocks for all creatures in the proposal
    creature_ids = list({c.monster_id for c in proposal.creatures})
    statblock_map: dict[str, dict] = {}
    if creature_ids:
        monster_result = await db.execute(
            select(Monster.id, Monster.statblock).where(Monster.id.in_(creature_ids))
        )
        for mid, sb in monster_result.all():
            statblock_map[mid] = sb or {}

    return EncounterProposalResponse(
        creatures=[
            EncounterCreatureResponse(
                monster_id=c.monster_id,
                name=c.name,
                cr=c.cr,
                hp=c.hp,
                ac=c.ac,
                tactical_role=c.tactical_role,
                count=c.count,
                xp_each=c.xp,
                statblock=statblock_map.get(c.monster_id, {}),
            )
            for c in proposal.creatures
        ],
        template=proposal.template,
        xp_budget=proposal.xp_budget,
        adjusted_xp=proposal.adjusted_xp,
        difficulty_tier=proposal.difficulty_tier,
        tactical_brief=proposal.tactical_brief,
        warnings=[
            EncounterWarningResponse(
                level=w.level,
                message=w.message,
                creature_id=w.creature_id,
            )
            for w in proposal.warnings
        ],
        creature_count=proposal.creature_count,
        environment=proposal.environment,
        environment_name=proposal.environment_name,
        terrain_features=proposal.terrain_features,
        map_suggestions=proposal.map_suggestions,
        objective_id=proposal.objective_id,
        objective_name=proposal.objective_name,
        objective_description=proposal.objective_description,
        objective_dm_instructions=proposal.objective_dm_instructions,
        objective_win_conditions=proposal.objective_win_conditions,
        objective_special_rules=proposal.objective_special_rules,
        objective_bonus_rewards=proposal.objective_bonus_rewards,
        active_affixes=proposal.active_affixes,
        affix_details=[
            AffixDetail(
                id=affix_def.id,
                name=affix_def.name,
                category=affix_def.category,
                description=affix_def.description,
                flavor_text=affix_def.flavor_text,
            )
            for aid in (proposal.active_affixes or [])
            if (affix_def := get_affix(aid)) is not None
        ],
        affix_modified_stats=proposal.affix_modified_stats,
        difficulty_notes=proposal.difficulty_notes,
        base_intensity=proposal.base_intensity,
        adjusted_intensity=proposal.adjusted_intensity,
        theme_id=proposal.theme_id,
        theme_name=proposal.theme_name,
        danger_rating=proposal.danger_rating,
        read_aloud_text=proposal.read_aloud_text,
        encounter_hook=proposal.encounter_hook,
        dm_guidance_boxes=proposal.dm_guidance_boxes,
        creature_flavor=proposal.creature_flavor,
        weakness_tips=proposal.weakness_tips,
        roguelike_reference=proposal.roguelike_reference,
    )


@router.post("/approve")
async def approve_encounter(
    arena_id: str,
    encounter: EncounterProposalResponse,
    db: AsyncSession = Depends(get_db),
):
    """Approve an encounter proposal and populate the arena with creatures."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    # Update arena metadata
    arena.encounter_template = encounter.template
    arena.xp_budget = encounter.xp_budget
    arena.adjusted_xp = encounter.adjusted_xp
    arena.tactical_brief = encounter.tactical_brief
    arena.environment = encounter.environment

    # Store objective on arena (Phase 7A)
    arena.objective = encounter.objective_id or None
    arena.objective_progress = {}

    # Create ArenaCreatureStatus entries
    for creature in encounter.creatures:
        for i in range(creature.count):
            label = creature.name if creature.count == 1 else f"{creature.name} {i + 1}"
            arena_creature = ArenaCreatureStatus(
                id=str(ULID()),
                arena_id=arena_id,
                monster_id=creature.monster_id,
                instance_label=label,
            )
            db.add(arena_creature)

    # Update floor's templates_used and objectives_used
    floor = await db.get(Floor, arena.floor_id)
    if floor:
        used = floor.templates_used or []
        if encounter.template not in used:
            used.append(encounter.template)
            floor.templates_used = used

        # Track objectives used this floor (Phase 7A)
        if encounter.objective_id:
            obj_used = floor.objectives_used or []
            if encounter.objective_id not in obj_used:
                obj_used.append(encounter.objective_id)
                floor.objectives_used = obj_used

    await db.flush()
    return {"message": "Encounter approved", "creatures_created": encounter.creature_count}


@router.post("/objective/progress")
async def update_objective_progress(
    arena_id: str,
    body: ObjectiveProgressUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update objective progress during combat (e.g., pillars activated, rounds survived)."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    if not arena.objective:
        raise HTTPException(status_code=400, detail="No objective set for this arena")

    # Merge progress: existing values updated with new ones
    current = arena.objective_progress or {}
    current.update(body.progress)
    arena.objective_progress = current

    await db.flush()
    return {"message": "Objective progress updated", "progress": arena.objective_progress}
