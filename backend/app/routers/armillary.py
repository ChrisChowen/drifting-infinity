"""Armillary system API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.armillary_effects_data import get_effect_by_key
from app.database import get_db
from app.engine.armillary.roller import DEFAULT_CATEGORY_WEIGHTS, reroll_armillary_effect
from app.engine.armillary.weight_adjuster import adjust_weights
from app.models.arena import Arena, ArmillaryEffect
from app.models.campaign import Campaign
from app.models.floor import Floor
from app.models.run import Run
from app.schemas.campaign import CampaignSettings
from app.services.armillary_service import (
    get_party_state_for_weights,
    roll_effect_for_arena,
    save_armillary_effect,
)

router = APIRouter(prefix="/arenas/{arena_id}/armillary", tags=["armillary"])


class ArmillaryEffectResponse(BaseModel):
    id: str
    arena_id: str
    round_number: int
    category: str
    effect_key: str
    effect_name: str
    effect_description: str
    xp_cost: int
    was_overridden: bool
    was_rerolled: bool


def _to_response(e: ArmillaryEffect) -> ArmillaryEffectResponse:
    effect_def = get_effect_by_key(e.effect_key)
    return ArmillaryEffectResponse(
        id=e.id,
        arena_id=e.arena_id,
        round_number=e.round_number,
        category=e.category,
        effect_key=e.effect_key,
        effect_name=effect_def.name if effect_def else e.effect_key,
        effect_description=e.effect_description,
        xp_cost=e.xp_cost,
        was_overridden=e.was_overridden,
        was_rerolled=e.was_rerolled,
    )


@router.get("", response_model=list[ArmillaryEffectResponse])
async def list_effects(arena_id: str, db: AsyncSession = Depends(get_db)):
    """List all Armillary effects for this arena."""
    result = await db.execute(
        select(ArmillaryEffect)
        .where(ArmillaryEffect.arena_id == arena_id)
        .order_by(ArmillaryEffect.round_number)
    )
    return [_to_response(e) for e in result.scalars().all()]


@router.post("/roll", response_model=ArmillaryEffectResponse)
async def roll_effect(
    arena_id: str,
    round_number: int,
    db: AsyncSession = Depends(get_db),
):
    """Roll a new Armillary effect for the given round."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    # Get floor for context
    floor = await db.get(Floor, arena.floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    # Load campaign settings for armillary_aggression
    run = await db.get(Run, floor.run_id)
    armillary_aggression = 1.0
    if run:
        campaign = await db.get(Campaign, run.campaign_id)
        if campaign:
            settings = CampaignSettings(**(campaign.settings or {}))
            armillary_aggression = settings.armillary_aggression

    # Roll effect
    roll_result = await roll_effect_for_arena(
        db=db,
        arena=arena,
        floor_id=floor.id,
        round_number=round_number,
        floor_number=floor.floor_number,
        armillary_aggression=armillary_aggression,
    )

    # Save to DB
    saved = await save_armillary_effect(db, arena_id, round_number, roll_result)
    return _to_response(saved)


@router.post("/reroll", response_model=ArmillaryEffectResponse)
async def reroll_effect(
    arena_id: str,
    effect_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Reroll an Armillary effect (costs 1 Armillary Favour)."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    # Get the existing effect
    old_effect = await db.get(ArmillaryEffect, effect_id)
    if not old_effect:
        raise HTTPException(status_code=404, detail="Effect not found")

    # Check Favour balance (get from run)
    floor = await db.get(Floor, arena.floor_id)
    run_result = await db.execute(select(Run).where(Run.id == floor.run_id))
    run = run_result.scalar_one_or_none()
    if not run or run.armillary_favour < 1:
        raise HTTPException(status_code=400, detail="Not enough Armillary Favour")

    # Spend Favour
    run.armillary_favour -= 1

    # Mark old effect as overridden
    old_effect.was_overridden = True

    # Reroll
    roll_result = reroll_armillary_effect(
        current_effect_key=old_effect.effect_key,
        round_number=old_effect.round_number,
        category_weights=DEFAULT_CATEGORY_WEIGHTS,
    )

    # Save new effect
    saved = await save_armillary_effect(
        db, arena_id, old_effect.round_number, roll_result,
    )

    return _to_response(saved)


@router.get("/forecast")
async def forecast_weights(
    arena_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the current adjusted category weights for this arena."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    floor = await db.get(Floor, arena.floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    party_state = await get_party_state_for_weights(db, floor.id)
    weights = adjust_weights(
        base_weights=DEFAULT_CATEGORY_WEIGHTS,
        average_hp_percentage=party_state["average_hp_percentage"],
        any_dead=party_state["any_dead"],
        cumulative_stress=party_state["cumulative_stress"],
        arena_number=arena.arena_number,
        floor_number=floor.floor_number,
    )

    return {
        "base_weights": DEFAULT_CATEGORY_WEIGHTS,
        "adjusted_weights": weights,
        "party_state": party_state,
    }
