from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.database import get_db
from app.models.campaign import Campaign
from app.models.economy import AstralShardLedger, GoldLedger
from app.schemas.economy import (
    EconomyBalance,
    GoldAward,
    GoldLedgerEntry,
    ShardAward,
    ShardLedgerEntry,
)

router = APIRouter(prefix="/campaigns/{campaign_id}/economy", tags=["economy"])


@router.get("/balance", response_model=EconomyBalance)
async def get_balance(campaign_id: str, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return EconomyBalance(
        gold_balance=campaign.gold_balance,
        astral_shard_balance=campaign.astral_shard_balance,
    )


@router.get("/gold", response_model=list[GoldLedgerEntry])
async def get_gold_ledger(
    campaign_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(GoldLedger)
        .where(GoldLedger.campaign_id == campaign_id)
        .order_by(GoldLedger.created_at.desc())
        .limit(limit)
    )
    entries = result.scalars().all()
    return [
        GoldLedgerEntry(
            id=e.id, campaign_id=e.campaign_id, amount=e.amount,
            reason=e.reason, run_id=e.run_id, arena_id=e.arena_id,
            created_at=e.created_at,
        )
        for e in entries
    ]


@router.post("/gold")
async def award_gold(
    campaign_id: str, data: GoldAward, db: AsyncSession = Depends(get_db)
):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    entry = GoldLedger(
        id=str(ULID()),
        campaign_id=campaign_id,
        amount=data.amount,
        reason=data.reason,
        run_id=data.run_id,
        arena_id=data.arena_id,
    )
    db.add(entry)
    campaign.gold_balance += data.amount
    await db.flush()
    return {"gold_balance": campaign.gold_balance}


@router.get("/shards", response_model=list[ShardLedgerEntry])
async def get_shard_ledger(
    campaign_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AstralShardLedger)
        .where(AstralShardLedger.campaign_id == campaign_id)
        .order_by(AstralShardLedger.created_at.desc())
        .limit(limit)
    )
    entries = result.scalars().all()
    return [
        ShardLedgerEntry(
            id=e.id, campaign_id=e.campaign_id, amount=e.amount,
            reason=e.reason, run_id=e.run_id, created_at=e.created_at,
        )
        for e in entries
    ]


@router.post("/shards")
async def award_shards(
    campaign_id: str, data: ShardAward, db: AsyncSession = Depends(get_db)
):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    entry = AstralShardLedger(
        id=str(ULID()),
        campaign_id=campaign_id,
        amount=data.amount,
        reason=data.reason,
        run_id=data.run_id,
    )
    db.add(entry)
    campaign.astral_shard_balance += data.amount
    await db.flush()
    return {"astral_shard_balance": campaign.astral_shard_balance}
