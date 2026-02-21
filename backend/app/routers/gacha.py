"""Gacha system API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.engine.gacha.banners import BANNERS
from app.models.gacha import GachaIdentity, GachaPull, GachaVariant, GachaWeapon
from app.services.gacha_service import get_or_create_banner_state, pull_gacha

router = APIRouter(prefix="/campaigns/{campaign_id}/gacha", tags=["gacha"])


class BannerResponse(BaseModel):
    key: str
    name: str
    description: str
    item_type: str


class PullHistoryEntry(BaseModel):
    id: str
    banner: str
    rarity: str
    pull_number: int
    result_name: str
    was_pity: bool
    was_duplicate: bool


@router.get("/banners", response_model=list[BannerResponse])
async def list_banners():
    """List available gacha banners."""
    return [
        BannerResponse(
            key=b.key, name=b.name,
            description=b.description, item_type=b.item_type,
        )
        for b in BANNERS.values()
    ]


@router.post("/pull")
async def do_pull(
    campaign_id: str, banner: str,
    db: AsyncSession = Depends(get_db),
):
    """Perform a gacha pull."""
    result = await pull_gacha(db, campaign_id, banner)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/history", response_model=list[PullHistoryEntry])
async def pull_history(
    campaign_id: str, limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get pull history."""
    result = await db.execute(
        select(GachaPull)
        .where(GachaPull.campaign_id == campaign_id)
        .order_by(GachaPull.created_at.desc())
        .limit(limit)
    )
    pulls = result.scalars().all()
    return [
        PullHistoryEntry(
            id=p.id, banner=p.banner, rarity=p.rarity,
            pull_number=p.pull_number, result_name=p.result_name,
            was_pity=p.was_pity, was_duplicate=p.was_duplicate,
        )
        for p in pulls
    ]


@router.get("/pity")
async def pity_state(
    campaign_id: str, banner: str,
    db: AsyncSession = Depends(get_db),
):
    """Get pity counter state for a banner."""
    state = await get_or_create_banner_state(db, campaign_id, banner)
    return {
        "total_pulls": state.total_pulls,
        "pulls_since_rare": state.pulls_since_rare,
        "pulls_since_very_rare": state.pulls_since_very_rare,
        "pulls_since_legendary": state.pulls_since_legendary,
        "next_rare_guaranteed_at": 5 - state.pulls_since_rare,
        "next_very_rare_guaranteed_at": 15 - state.pulls_since_very_rare,
        "next_legendary_guaranteed_at": 40 - state.pulls_since_legendary,
    }


@router.get("/collection")
async def collection(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the player's full gacha collection."""
    variants = await db.execute(
        select(GachaVariant).where(GachaVariant.campaign_id == campaign_id)
    )
    weapons = await db.execute(
        select(GachaWeapon).where(GachaWeapon.campaign_id == campaign_id)
    )
    identities = await db.execute(
        select(GachaIdentity).where(GachaIdentity.campaign_id == campaign_id)
    )

    def _item_dict(item):
        return {
            "id": item.id, "name": item.name, "rarity": item.rarity,
            "description": item.description, "is_equipped": item.is_equipped,
        }

    return {
        "variants": [_item_dict(v) for v in variants.scalars().all()],
        "weapons": [_item_dict(w) for w in weapons.scalars().all()],
        "identities": [_item_dict(i) for i in identities.scalars().all()],
    }
