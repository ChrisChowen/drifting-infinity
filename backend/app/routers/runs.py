import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ulid import ULID

from app.database import get_db
from app.engine.combat.respawn import get_lives_remaining
from app.engine.combat.rest import rest_schedule_for_floor
from app.engine.difficulty.intensity_curve import compute_intensity_curve
from app.engine.meta.lives import compute_starting_lives
from app.engine.scaling import get_scaling_params
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.floor import Floor
from app.models.run import Run
from app.schemas.campaign import CampaignSettings
from app.schemas.run import RunCreate, RunResponse

router = APIRouter(prefix="/campaigns/{campaign_id}/runs", tags=["runs"])


def _to_response(r: Run) -> RunResponse:
    return RunResponse(
        id=r.id, campaign_id=r.campaign_id,
        started_at=r.started_at, ended_at=r.ended_at,
        starting_level=r.starting_level, floor_count=r.floor_count,
        seed=r.seed or 0,
        floors_completed=r.floors_completed,
        total_gold_earned=r.total_gold_earned,
        total_shards_earned=r.total_shards_earned,
        outcome=r.outcome, difficulty_curve=r.difficulty_curve or [],
        armillary_favour=r.armillary_favour,
        affix_history=r.affix_history or [],
        lives_remaining=r.lives_remaining,
        total_deaths=r.total_deaths,
        death_log=r.death_log or [],
    )


@router.get("", response_model=list[RunResponse])
async def list_runs(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Run).where(Run.campaign_id == campaign_id).order_by(Run.started_at.desc())
    )
    return [_to_response(r) for r in result.scalars().all()]


@router.post("", response_model=RunResponse)
async def start_run(
    campaign_id: str, data: RunCreate, db: AsyncSession = Depends(get_db)
):
    # Verify campaign exists
    camp_result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = camp_result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Load campaign settings
    settings = CampaignSettings(**(campaign.settings or {}))

    # Auto-derive party level from characters if not provided
    char_result = await db.execute(
        select(Character).where(Character.campaign_id == campaign_id)
    )
    chars = char_result.scalars().all()
    if not chars:
        raise HTTPException(
            status_code=400,
            detail="No characters in party. Add characters before starting a run.",
        )

    computed_level = max(1, sum(c.level for c in chars) // len(chars))
    effective_level = data.starting_level if data.starting_level is not None else computed_level

    # Auto-compute floor_count based on party level when not explicitly set
    effective_floor_count = data.compute_floor_count(effective_level)

    run_seed = data.seed or random.randint(1, 999_999)

    # Compute starting lives based on meta-talents and first-run bonus
    # TODO: Load actual meta-talents from campaign meta when available
    meta_talents: list[str] = []
    is_first_run = campaign.total_runs == 0
    first_run_bonus = settings.first_run_bonus_lives if is_first_run else 0
    starting_lives = compute_starting_lives(meta_talents, first_run_bonus=first_run_bonus)

    run = Run(
        id=str(ULID()),
        campaign_id=campaign_id,
        starting_level=effective_level,
        floor_count=effective_floor_count,
        seed=run_seed,
        lives_remaining=starting_lives,
    )
    db.add(run)
    await db.flush()
    return _to_response(run)


@router.get("/active", response_model=RunResponse | None)
async def get_active_run(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Run).where(
            Run.campaign_id == campaign_id,
            Run.outcome.is_(None),
        ).order_by(Run.started_at.desc())
    )
    run = result.scalar_one_or_none()
    if not run:
        return None
    return _to_response(run)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    campaign_id: str, run_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Run).where(Run.id == run_id, Run.campaign_id == campaign_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _to_response(run)


@router.post("/{run_id}/end")
async def end_run(
    campaign_id: str, run_id: str, outcome: str = "completed",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Run).where(Run.id == run_id, Run.campaign_id == campaign_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.outcome is not None:
        raise HTTPException(status_code=400, detail="Run already ended")

    from datetime import datetime, timezone
    run.outcome = outcome
    run.ended_at = datetime.now(timezone.utc)

    # Increment campaign run count
    campaign = await db.get(Campaign, campaign_id)
    if campaign:
        campaign.total_runs += 1

    await db.flush()
    return {"message": f"Run ended with outcome: {outcome}"}


@router.get("/{run_id}/lives")
async def get_run_lives(
    campaign_id: str, run_id: str, db: AsyncSession = Depends(get_db),
):
    """Get current lives status for a run."""
    try:
        return await get_lives_remaining(run_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{run_id}/intensity-curve")
async def get_intensity_curve(
    campaign_id: str, run_id: str, db: AsyncSession = Depends(get_db),
):
    """Return planned intensity curve and actual arena difficulties for a run."""
    result = await db.execute(
        select(Run).where(Run.id == run_id, Run.campaign_id == campaign_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Get party size for rest schedule computation
    party_size = await db.scalar(
        select(func.count()).select_from(Character).where(
            Character.campaign_id == campaign_id
        )
    ) or 1
    scaling = get_scaling_params(party_size)

    # Load floors with arenas eagerly
    floors_result = await db.execute(
        select(Floor)
        .where(Floor.run_id == run_id)
        .options(selectinload(Floor.arenas))
        .order_by(Floor.floor_number)
    )
    floors = floors_result.scalars().all()

    curve: list[dict] = []
    for fl in floors:
        total_arenas = fl.arena_count
        rest_schedule = rest_schedule_for_floor(
            total_arenas, scaling.short_rests_per_floor,
        )
        sorted_arenas = sorted(fl.arenas, key=lambda a: a.arena_number)
        for arena in sorted_arenas:
            state = compute_intensity_curve(
                arena_number=arena.arena_number,
                total_arenas=total_arenas,
                floor_number=fl.floor_number,
                rest_schedule=rest_schedule,
            )
            curve.append({
                "floor": fl.floor_number,
                "arena": arena.arena_number,
                "phase": state.phase.value,
                "planned_intensity": state.intensity,
                "planned_difficulty": state.difficulty,
                "actual_difficulty": arena.actual_difficulty,
                "difficulty_target": arena.difficulty_target,
                "is_complete": arena.is_complete,
            })

    return {
        "run_id": run_id,
        "floor_count": run.floor_count,
        "curve": curve,
    }
