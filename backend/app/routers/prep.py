"""Session prep API endpoints.

Lets DMs generate and review an entire floor before a session.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.arena import Arena, ArenaCreatureStatus
from app.models.floor import Floor
from app.models.run import Run
from app.schemas.arena import ArenaResponse
from app.services.prep_service import generate_full_floor, regenerate_arena_encounter

router = APIRouter(prefix="/prep", tags=["prep"])


def _arena_to_response(a: Arena) -> ArenaResponse:
    return ArenaResponse(
        id=a.id,
        floor_id=a.floor_id,
        arena_number=a.arena_number,
        encounter_template=a.encounter_template,
        difficulty_target=a.difficulty_target,
        xp_budget=a.xp_budget,
        adjusted_xp=a.adjusted_xp,
        actual_difficulty=a.actual_difficulty,
        gold_earned_per_player=a.gold_earned_per_player,
        tactical_brief=a.tactical_brief,
        map_id=a.map_id,
        environment=a.environment,
        is_active=a.is_active,
        is_complete=a.is_complete,
        momentum_bonus_earned=a.momentum_bonus_earned,
        dm_notes=a.dm_notes,
        custom_read_aloud=a.custom_read_aloud,
        narrative_content=a.narrative_content,
    )


@router.post("/floor/{floor_id}/generate")
async def generate_floor_encounters(
    floor_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate encounters for all arenas on a floor at once."""
    floor = await db.get(Floor, floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run_result = await db.execute(select(Run).where(Run.id == floor.run_id))
    run = run_result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    summaries = await generate_full_floor(db=db, floor=floor, run=run, campaign_id=run.campaign_id)

    return {
        "floor_id": floor_id,
        "floor_number": floor.floor_number,
        "arena_count": floor.arena_count,
        "arenas": summaries,
    }


@router.get("/floor/{floor_id}")
async def get_floor_prep(
    floor_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full floor prep data with all arenas and narrative content."""
    floor = await db.get(Floor, floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    arenas_result = await db.execute(
        select(Arena).where(Arena.floor_id == floor_id).order_by(Arena.arena_number)
    )
    arenas = arenas_result.scalars().all()

    arena_data = []
    for arena in arenas:
        creatures_result = await db.execute(
            select(ArenaCreatureStatus).where(ArenaCreatureStatus.arena_id == arena.id)
        )
        creatures = creatures_result.scalars().all()

        arena_data.append(
            {
                "arena": _arena_to_response(arena).model_dump(),
                "creatures": [
                    {
                        "id": c.id,
                        "monster_id": c.monster_id,
                        "instance_label": c.instance_label,
                        "status": c.status,
                        "is_reinforcement": c.is_reinforcement,
                    }
                    for c in creatures
                ],
            }
        )

    return {
        "floor_id": floor_id,
        "floor_number": floor.floor_number,
        "arena_count": floor.arena_count,
        "arenas_completed": floor.arenas_completed,
        "is_complete": floor.is_complete,
        "active_affixes": floor.active_affixes or [],
        "templates_used": floor.templates_used or [],
        "objectives_used": floor.objectives_used or [],
        "arenas": arena_data,
    }


@router.post("/floor/{floor_id}/regenerate/{arena_number}")
async def regenerate_arena(
    floor_id: str,
    arena_number: int,
    difficulty: str | None = Query(default=None),
    template: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate a specific arena's encounter."""
    floor = await db.get(Floor, floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run_result = await db.execute(select(Run).where(Run.id == floor.run_id))
    run = run_result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    arena_result = await db.execute(
        select(Arena).where(
            Arena.floor_id == floor_id,
            Arena.arena_number == arena_number,
        )
    )
    arena = arena_result.scalar_one_or_none()
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    if arena.is_complete:
        raise HTTPException(status_code=400, detail="Cannot regenerate a completed arena")

    summary = await regenerate_arena_encounter(
        db=db,
        arena=arena,
        floor=floor,
        run=run,
        campaign_id=run.campaign_id,
        difficulty=difficulty,
        template=template,
        environment=environment,
    )

    return summary


@router.patch("/floor/{floor_id}/arenas/{arena_id}/notes")
async def update_arena_notes(
    floor_id: str,
    arena_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Save DM notes for an arena."""
    arena = await db.get(Arena, arena_id)
    if not arena or arena.floor_id != floor_id:
        raise HTTPException(status_code=404, detail="Arena not found")

    if "dm_notes" in body:
        arena.dm_notes = body["dm_notes"]
    if "custom_read_aloud" in body:
        arena.custom_read_aloud = body["custom_read_aloud"]

    await db.flush()
    return {"message": "Notes updated"}
