"""Archive service - run history and statistics."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.models.run import Run


async def get_campaign_stats(db: AsyncSession, campaign_id: str) -> dict:
    """Get aggregate campaign statistics."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    # Run counts by outcome
    runs = await db.execute(
        select(Run).where(Run.campaign_id == campaign_id)
    )
    all_runs = runs.scalars().all()

    completed = sum(1 for r in all_runs if r.outcome == "completed")
    abandoned = sum(1 for r in all_runs if r.outcome == "abandoned")
    tpk = sum(1 for r in all_runs if r.outcome == "tpk")
    active = sum(1 for r in all_runs if r.outcome is None)

    total_gold = sum(r.total_gold_earned for r in all_runs)
    total_shards = sum(r.total_shards_earned for r in all_runs)
    total_floors = sum(r.floors_completed for r in all_runs)

    # Average floors per run
    completed_runs = [r for r in all_runs if r.outcome is not None]
    avg_floors = (
        sum(r.floors_completed for r in completed_runs) / len(completed_runs)
        if completed_runs else 0
    )

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "party_power_coefficient": campaign.party_power_coefficient,
        "total_runs": len(all_runs),
        "runs_completed": completed,
        "runs_abandoned": abandoned,
        "runs_tpk": tpk,
        "runs_active": active,
        "total_gold_earned": total_gold,
        "total_shards_earned": total_shards,
        "total_floors_cleared": total_floors,
        "average_floors_per_run": round(avg_floors, 1),
        "gold_balance": campaign.gold_balance,
        "astral_shard_balance": campaign.astral_shard_balance,
    }


async def get_run_history(
    db: AsyncSession, campaign_id: str, limit: int = 20
) -> list[dict]:
    """Get run history for a campaign."""
    result = await db.execute(
        select(Run)
        .where(Run.campaign_id == campaign_id)
        .order_by(Run.started_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()

    return [
        {
            "id": r.id,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "ended_at": r.ended_at.isoformat() if r.ended_at else None,
            "starting_level": r.starting_level,
            "floor_count": r.floor_count,
            "floors_completed": r.floors_completed,
            "total_gold_earned": r.total_gold_earned,
            "total_shards_earned": r.total_shards_earned,
            "outcome": r.outcome,
            "difficulty_curve": r.difficulty_curve or [],
        }
        for r in runs
    ]


async def get_difficulty_curves(
    db: AsyncSession, campaign_id: str, last_n_runs: int = 5
) -> list[dict]:
    """Get difficulty curve data from recent runs for comparison."""
    result = await db.execute(
        select(Run)
        .where(Run.campaign_id == campaign_id, Run.outcome.isnot(None))
        .order_by(Run.started_at.desc())
        .limit(last_n_runs)
    )
    runs = result.scalars().all()

    return [
        {
            "run_id": r.id,
            "starting_level": r.starting_level,
            "outcome": r.outcome,
            "difficulty_curve": r.difficulty_curve or [],
        }
        for r in runs
    ]
