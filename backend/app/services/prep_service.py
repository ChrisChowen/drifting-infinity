"""Session prep service — generate an entire floor's encounters at once.

Lets DMs pre-generate and review all arenas for a floor before the session,
like reading a chapter of a published adventure.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.models.arena import Arena, ArenaCreatureStatus
from app.models.floor import Floor
from app.models.run import Run
from app.services.encounter_service import generate_encounter_for_arena


async def generate_full_floor(
    db: AsyncSession,
    floor: Floor,
    run: Run,
    campaign_id: str,
) -> list[dict]:
    """Generate encounters for all arenas on a floor.

    Creates Arena records and populates each with a generated encounter
    including full narrative content. Returns a list of arena summaries.
    """
    results = []

    for arena_num in range(1, floor.arena_count + 1):
        # Check if arena already exists
        existing = await db.execute(
            select(Arena).where(
                Arena.floor_id == floor.id,
                Arena.arena_number == arena_num,
            )
        )
        arena = existing.scalar_one_or_none()

        if not arena:
            arena = Arena(
                id=str(ULID()),
                floor_id=floor.id,
                arena_number=arena_num,
            )
            db.add(arena)
            await db.flush()

        # Generate encounter for this arena
        proposal = await generate_encounter_for_arena(
            db=db,
            arena=arena,
            floor=floor,
            run=run,
            campaign_id=campaign_id,
        )

        # Populate arena metadata from proposal
        arena.encounter_template = proposal.template
        arena.xp_budget = proposal.xp_budget
        arena.adjusted_xp = proposal.adjusted_xp
        arena.tactical_brief = proposal.tactical_brief
        arena.environment = proposal.environment

        # Store objective
        arena.objective = proposal.objective_id or None
        arena.objective_progress = {}

        # Store narrative content as JSON on the arena
        arena.narrative_content = {
            "read_aloud_text": proposal.read_aloud_text,
            "encounter_hook": proposal.encounter_hook,
            "dm_guidance_boxes": proposal.dm_guidance_boxes,
            "creature_flavor": proposal.creature_flavor,
            "weakness_tips": proposal.weakness_tips,
            "roguelike_reference": proposal.roguelike_reference,
        }

        # Create creature status entries
        existing_creatures = await db.execute(
            select(ArenaCreatureStatus).where(ArenaCreatureStatus.arena_id == arena.id)
        )
        if not existing_creatures.scalars().all():
            for creature in proposal.creatures:
                for i in range(creature.count):
                    label = creature.name if creature.count == 1 else f"{creature.name} {i + 1}"
                    db.add(
                        ArenaCreatureStatus(
                            id=str(ULID()),
                            arena_id=arena.id,
                            monster_id=creature.monster_id,
                            instance_label=label,
                        )
                    )

        # Track templates and objectives used
        used = floor.templates_used or []
        if proposal.template not in used:
            used.append(proposal.template)
            floor.templates_used = used

        if proposal.objective_id:
            obj_used = floor.objectives_used or []
            if proposal.objective_id not in obj_used:
                obj_used.append(proposal.objective_id)
                floor.objectives_used = obj_used

        await db.flush()

        results.append(_arena_summary(arena, proposal))

    return results


async def regenerate_arena_encounter(
    db: AsyncSession,
    arena: Arena,
    floor: Floor,
    run: Run,
    campaign_id: str,
    difficulty: str | None = None,
    template: str | None = None,
    environment: str | None = None,
) -> dict:
    """Regenerate the encounter for a specific arena.

    Deletes existing creatures and generates a fresh encounter.
    """
    # Delete existing creatures
    existing = await db.execute(
        select(ArenaCreatureStatus).where(ArenaCreatureStatus.arena_id == arena.id)
    )
    for c in existing.scalars().all():
        await db.delete(c)

    # Generate new encounter
    proposal = await generate_encounter_for_arena(
        db=db,
        arena=arena,
        floor=floor,
        run=run,
        campaign_id=campaign_id,
        difficulty=difficulty,
        template_name=template,
        environment=environment,
    )

    # Update arena
    arena.encounter_template = proposal.template
    arena.xp_budget = proposal.xp_budget
    arena.adjusted_xp = proposal.adjusted_xp
    arena.tactical_brief = proposal.tactical_brief
    arena.environment = proposal.environment
    arena.objective = proposal.objective_id or None
    arena.objective_progress = {}
    arena.narrative_content = {
        "read_aloud_text": proposal.read_aloud_text,
        "encounter_hook": proposal.encounter_hook,
        "dm_guidance_boxes": proposal.dm_guidance_boxes,
        "creature_flavor": proposal.creature_flavor,
        "weakness_tips": proposal.weakness_tips,
        "roguelike_reference": proposal.roguelike_reference,
    }

    # Create new creatures
    for creature in proposal.creatures:
        for i in range(creature.count):
            label = creature.name if creature.count == 1 else f"{creature.name} {i + 1}"
            db.add(
                ArenaCreatureStatus(
                    id=str(ULID()),
                    arena_id=arena.id,
                    monster_id=creature.monster_id,
                    instance_label=label,
                )
            )

    await db.flush()
    return _arena_summary(arena, proposal)


def _arena_summary(arena: Arena, proposal) -> dict:
    """Build a compact summary dict for an arena."""
    return {
        "arena_id": arena.id,
        "arena_number": arena.arena_number,
        "template": proposal.template,
        "difficulty_tier": proposal.difficulty_tier,
        "danger_rating": proposal.danger_rating,
        "environment": proposal.environment,
        "environment_name": proposal.environment_name,
        "creature_count": proposal.creature_count,
        "xp_budget": proposal.xp_budget,
        "objective_name": proposal.objective_name,
        "read_aloud_text": proposal.read_aloud_text,
        "encounter_hook": proposal.encounter_hook,
        "creatures": [
            {
                "name": c.name,
                "count": c.count,
                "cr": c.cr,
                "tactical_role": c.tactical_role,
            }
            for c in proposal.creatures
        ],
    }
