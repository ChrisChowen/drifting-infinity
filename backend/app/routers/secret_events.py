"""Secret events API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.secret_events import check_secret_event_triggers, get_secret_event
from app.database import get_db
from app.models.run import Run

router = APIRouter(prefix="/runs/{run_id}/secret-events", tags=["secret-events"])


class SecretEventResponse(BaseModel):
    id: str
    name: str
    description: str
    dm_instructions: str
    trigger_type: str
    content_type: str
    rewards: dict
    lore_fragment_id: str | None = None
    is_floor_event: bool


class SecretEventCheckRequest(BaseModel):
    floor_number: int
    arena_number: int = 1
    trigger_type: str = "floor_transition"


@router.post("/check", response_model=SecretEventResponse | None)
async def check_secret_events(
    run_id: str,
    body: SecretEventCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """Check if a secret event triggers at this point in the run."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    from app.models.campaign import Campaign

    campaign = await db.get(Campaign, run.campaign_id)
    campaign_runs = campaign.total_runs if campaign else 0

    run_stats = {
        "total_deaths": run.total_deaths,
        "floors_completed": run.floors_completed,
        "total_gold_earned": run.total_gold_earned,
    }

    # Check already-triggered events this run to avoid repeats
    already_triggered = run.secret_events or []
    event = check_secret_event_triggers(
        floor_number=body.floor_number,
        arena_number=body.arena_number,
        run_stats=run_stats,
        campaign_runs_completed=campaign_runs,
        trigger_type=body.trigger_type,
    )

    if not event or event.id in already_triggered:
        return None

    # Record that this event triggered
    triggered = list(already_triggered)
    triggered.append(event.id)
    run.secret_events = triggered
    await db.flush()

    return SecretEventResponse(
        id=event.id,
        name=event.name,
        description=event.description,
        dm_instructions=event.dm_instructions,
        trigger_type=event.trigger_type,
        content_type=event.content_type,
        rewards=event.rewards,
        lore_fragment_id=event.lore_fragment_id,
        is_floor_event=event.is_floor_event,
    )


@router.get("/{event_id}", response_model=SecretEventResponse)
async def get_event(
    run_id: str,
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific secret event."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    event = get_secret_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Secret event not found")

    return SecretEventResponse(
        id=event.id,
        name=event.name,
        description=event.description,
        dm_instructions=event.dm_instructions,
        trigger_type=event.trigger_type,
        content_type=event.content_type,
        rewards=event.rewards,
        lore_fragment_id=event.lore_fragment_id,
        is_floor_event=event.is_floor_event,
    )
