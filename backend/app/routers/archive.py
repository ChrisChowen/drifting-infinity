"""Archive and statistics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.archive_service import (
    get_campaign_stats,
    get_difficulty_curves,
    get_run_history,
)

router = APIRouter(prefix="/campaigns/{campaign_id}/archive", tags=["archive"])


@router.get("/stats")
async def campaign_stats(
    campaign_id: str, db: AsyncSession = Depends(get_db)
):
    """Get aggregate campaign statistics."""
    result = await get_campaign_stats(db, campaign_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/runs")
async def run_history(
    campaign_id: str, limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get run history."""
    return await get_run_history(db, campaign_id, limit)


@router.get("/difficulty-curves")
async def difficulty_curves(
    campaign_id: str, last_n: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """Get difficulty curve comparisons from recent runs."""
    return await get_difficulty_curves(db, campaign_id, last_n)
