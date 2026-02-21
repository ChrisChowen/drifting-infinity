"""Enhancement system API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.enhancement_definitions import ENHANCEMENTS, TIER_CAPS, get_enhancements_by_tier
from app.database import get_db
from app.services.enhancement_service import (
    get_character_enhancements,
    purchase_enhancement,
)

router = APIRouter(prefix="/campaigns/{campaign_id}/enhancements", tags=["enhancements"])


class EnhancementDefResponse(BaseModel):
    id: str
    name: str
    tier: int
    base_cost: int
    effect_type: str
    effect: dict
    description: str
    power_rating: float
    max_stacks: int


class PurchaseRequest(BaseModel):
    character_id: str
    enhancement_id: str


@router.get("/catalog", response_model=list[EnhancementDefResponse])
async def get_catalog(tier: int | None = None):
    """Get the enhancement catalog (optionally filtered by tier)."""
    if tier:
        enhancements = get_enhancements_by_tier(tier)
    else:
        enhancements = ENHANCEMENTS

    return [
        EnhancementDefResponse(
            id=e.id, name=e.name, tier=e.tier,
            base_cost=e.base_cost, effect_type=e.effect_type,
            effect=e.effect, description=e.description,
            power_rating=e.power_rating, max_stacks=e.max_stacks,
        )
        for e in enhancements
    ]


@router.get("/caps")
async def get_tier_caps():
    """Get enhancement tier caps."""
    return TIER_CAPS


@router.get("/character/{character_id}")
async def get_character_enhancement_list(
    campaign_id: str, character_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all enhancements for a character."""
    enhancements = await get_character_enhancements(db, character_id)
    return [
        {
            "id": e["id"],
            "character_id": e["character_id"],
            "enhancement_id": e["enhancement_id"],
            "slot_index": e["slot_index"],
            "name": e["definition"].name if e["definition"] else "Unknown",
            "tier": e["definition"].tier if e["definition"] else 0,
            "description": e["definition"].description if e["definition"] else "",
        }
        for e in enhancements
    ]


@router.post("/purchase")
async def purchase(
    campaign_id: str, request: PurchaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """Purchase an enhancement for a character."""
    result = await purchase_enhancement(
        db, campaign_id, request.character_id, request.enhancement_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
