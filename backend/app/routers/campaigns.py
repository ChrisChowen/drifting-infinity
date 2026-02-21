from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignSettings, CampaignUpdate

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    return [
        CampaignResponse(
            id=c.id, name=c.name,
            party_power_coefficient=c.party_power_coefficient,
            total_runs=c.total_runs,
            gold_balance=c.gold_balance,
            astral_shard_balance=c.astral_shard_balance,
            settings=c.settings or {},
        )
        for c in campaigns
    ]


@router.post("", response_model=CampaignResponse)
async def create_campaign(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = Campaign(id=str(ULID()), name=data.name, settings={})
    db.add(campaign)
    await db.flush()
    return CampaignResponse(
        id=campaign.id, name=campaign.name,
        party_power_coefficient=campaign.party_power_coefficient,
        total_runs=campaign.total_runs,
        gold_balance=campaign.gold_balance,
        astral_shard_balance=campaign.astral_shard_balance,
        settings=campaign.settings or {},
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse(
        id=campaign.id, name=campaign.name,
        party_power_coefficient=campaign.party_power_coefficient,
        total_runs=campaign.total_runs,
        gold_balance=campaign.gold_balance,
        astral_shard_balance=campaign.astral_shard_balance,
        settings=campaign.settings or {},
    )


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str, data: CampaignUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if data.name is not None:
        campaign.name = data.name
    if data.settings is not None:
        # Validate through CampaignSettings schema
        try:
            validated = CampaignSettings(**data.settings)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
        campaign.settings = validated.model_dump()
    await db.flush()
    return CampaignResponse(
        id=campaign.id, name=campaign.name,
        party_power_coefficient=campaign.party_power_coefficient,
        total_runs=campaign.total_runs,
        gold_balance=campaign.gold_balance,
        astral_shard_balance=campaign.astral_shard_balance,
        settings=campaign.settings or {},
    )


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await db.delete(campaign)
    return {"message": "Campaign deleted"}
