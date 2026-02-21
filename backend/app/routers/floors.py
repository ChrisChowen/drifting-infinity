from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.floor_affixes import roll_affixes
from app.database import get_db
from app.models.floor import Floor
from app.models.run import Run
from app.schemas.floor import FloorCreate, FloorResponse

router = APIRouter(prefix="/runs/{run_id}/floors", tags=["floors"])


def _to_response(f: Floor) -> FloorResponse:
    return FloorResponse(
        id=f.id, run_id=f.run_id,
        floor_number=f.floor_number, arena_count=f.arena_count,
        arenas_completed=f.arenas_completed,
        cr_minimum_offset=f.cr_minimum_offset,
        is_complete=f.is_complete,
        templates_used=f.templates_used or [],
        objectives_used=f.objectives_used or [],
        active_affixes=f.active_affixes or [],
    )


@router.get("", response_model=list[FloorResponse])
async def list_floors(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Floor).where(Floor.run_id == run_id).order_by(Floor.floor_number)
    )
    return [_to_response(f) for f in result.scalars().all()]


@router.post("", response_model=FloorResponse)
async def start_floor(
    run_id: str, data: FloorCreate, db: AsyncSession = Depends(get_db)
):
    # Get run
    run_result = await db.execute(select(Run).where(Run.id == run_id))
    run = run_result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.outcome is not None:
        raise HTTPException(status_code=400, detail="Run already ended")

    # Calculate floor number
    existing = await db.execute(
        select(Floor).where(Floor.run_id == run_id)
    )
    floor_number = len(existing.scalars().all()) + 1

    if floor_number > run.floor_count:
        raise HTTPException(status_code=400, detail="All floors already created")

    # Roll floor affixes (Phase 7B)
    # Roll floor affixes
    existing_affix_ids = run.affix_history or []
    rolled = roll_affixes(floor_number, existing_affix_ids)
    affix_ids = [a.id for a in rolled]
    run.affix_history = existing_affix_ids + affix_ids

    floor = Floor(
        id=str(ULID()),
        run_id=run_id,
        floor_number=floor_number,
        arena_count=data.arena_count,
        active_affixes=affix_ids,
    )
    db.add(floor)
    await db.flush()
    return _to_response(floor)


@router.get("/active", response_model=FloorResponse | None)
async def get_active_floor(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Floor).where(
            Floor.run_id == run_id,
            Floor.is_complete.is_(False),
        ).order_by(Floor.floor_number)
    )
    floor = result.scalars().first()
    if not floor:
        return None
    return _to_response(floor)


@router.get("/{floor_id}", response_model=FloorResponse)
async def get_floor(
    run_id: str, floor_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Floor).where(Floor.id == floor_id, Floor.run_id == run_id)
    )
    floor = result.scalar_one_or_none()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return _to_response(floor)


@router.post("/{floor_id}/complete")
async def complete_floor(
    run_id: str, floor_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Floor).where(Floor.id == floor_id, Floor.run_id == run_id)
    )
    floor = result.scalar_one_or_none()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    if floor.is_complete:
        raise HTTPException(status_code=400, detail="Floor already complete")

    floor.is_complete = True

    # Update run's floors_completed
    run = await db.get(Run, run_id)
    if run:
        run.floors_completed += 1

    await db.flush()
    return {"message": f"Floor {floor.floor_number} completed"}
