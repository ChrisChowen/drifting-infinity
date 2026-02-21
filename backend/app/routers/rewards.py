"""Reward and shop API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.database import get_db
from app.models.arena import Arena
from app.models.campaign import Campaign
from app.models.floor import Floor
from app.models.inventory import RunInventory
from app.models.run import Run
from app.schemas.campaign import CampaignSettings
from app.services.reward_service import generate_arena_rewards
from app.services.shop_service import generate_shop_inventory, should_shop_appear

router = APIRouter(tags=["rewards"])


class RewardChoice(BaseModel):
    id: str
    name: str
    rarity: str
    category: str
    description: str
    effect: dict
    scope: str = "party"


class ShopItem(BaseModel):
    id: str
    name: str
    type: str
    rarity: str
    description: str
    effect: dict
    price: int


class ClaimRequest(BaseModel):
    reward_id: str
    reward_name: str
    reward_rarity: str
    reward_category: str


class PurchaseRequest(BaseModel):
    item_id: str
    item_name: str
    item_rarity: str
    item_type: str
    price: int


@router.get("/arenas/{arena_id}/rewards", response_model=list[RewardChoice])
async def get_reward_choices(
    arena_id: str,
    floor_number: int = 1,
    db: AsyncSession = Depends(get_db),
):
    """Get 3 reward choices for post-arena selection."""
    # Derive party_level from arena -> floor -> run chain
    party_level = 1
    arena = await db.get(Arena, arena_id)
    if arena:
        floor = await db.get(Floor, arena.floor_id)
        if floor:
            run_result = await db.execute(select(Run).where(Run.id == floor.run_id))
            run = run_result.scalar_one_or_none()
            if run:
                party_level = run.starting_level

    rewards = await generate_arena_rewards(floor_number, party_level, db)

    # Infer scope from category: consumable/gold = party, feat/equipment/ability = character
    char_categories = {"feat", "ability", "equipment"}
    return [
        RewardChoice(
            **{k: v for k, v in r.items() if k != "scope" and k != "source_type"},
            scope=r.get(
                "scope",
                "character" if r.get("category") in char_categories else "party",
            ),
        )
        for r in rewards
    ]


@router.post("/arenas/{arena_id}/rewards/claim")
async def claim_reward(
    arena_id: str,
    data: ClaimRequest,
    db: AsyncSession = Depends(get_db),
):
    """Claim a selected reward after arena completion."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    floor = await db.get(Floor, arena.floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run = (await db.execute(select(Run).where(Run.id == floor.run_id))).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    item = RunInventory(
        id=str(ULID()),
        run_id=run.id,
        item_name=data.reward_name,
        item_type=data.reward_category,
        item_rarity=data.reward_rarity,
        source="reward",
    )
    db.add(item)
    await db.flush()
    return {"message": f"Claimed {data.reward_name}", "inventory_id": item.id}


@router.get("/floors/{floor_id}/shop")
async def check_shop(
    floor_id: str,
    floor_number: int = 1,
    db: AsyncSession = Depends(get_db),
):
    """Check if shop appears and get inventory."""
    # Load campaign settings for shop_frequency and party level
    floor = await db.get(Floor, floor_id)
    shop_freq = 0.30
    party_level = 1
    if floor:
        run = (await db.execute(select(Run).where(Run.id == floor.run_id))).scalar_one_or_none()
        if run:
            party_level = run.starting_level
            campaign = await db.get(Campaign, run.campaign_id)
            if campaign:
                settings = CampaignSettings(**(campaign.settings or {}))
                shop_freq = settings.shop_frequency

    appears = should_shop_appear(shop_freq)
    if not appears:
        return {"shop_available": False, "inventory": []}

    inventory = await generate_shop_inventory(floor_number, db, party_level=party_level)
    return {
        "shop_available": True,
        "inventory": [ShopItem(**item).model_dump() for item in inventory],
    }


@router.post("/floors/{floor_id}/shop/purchase")
async def purchase_item(
    floor_id: str,
    data: PurchaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """Purchase an item from the shop."""
    floor = await db.get(Floor, floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run = (await db.execute(select(Run).where(Run.id == floor.run_id))).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    campaign = await db.get(Campaign, run.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.gold_balance < data.price:
        raise HTTPException(status_code=400, detail="Not enough gold")

    campaign.gold_balance -= data.price

    item = RunInventory(
        id=str(ULID()),
        run_id=run.id,
        item_name=data.item_name,
        item_type=data.item_type,
        item_rarity=data.item_rarity,
        source="shop",
    )
    db.add(item)
    await db.flush()
    return {
        "message": f"Purchased {data.item_name}",
        "inventory_id": item.id,
        "gold_remaining": campaign.gold_balance,
    }
