"""Meta-progression API: essence, talents, achievements, lore."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.lore_beats import get_lore_beats_for_floor
from app.data.lore_fragments import LORE_FRAGMENTS, get_lore_fragment
from app.database import get_db
from app.engine.meta.achievements import ACHIEVEMENTS, check_achievements, get_achievement
from app.engine.meta.essence import compute_run_essence
from app.engine.meta.run_reset import decay_ppc_between_runs

# Engine imports
from app.engine.meta.talents import TALENT_TREE, can_unlock, get_talent, unlock_talent
from app.models.campaign import Campaign
from app.models.campaign_meta import CampaignMeta
from app.models.run import Run
from app.schemas.meta import (
    AchievementResponse,
    LoreBeatResponse,
    LoreFragmentResponse,
    MetaResponse,
    RunEndMetaResponse,
    TalentResponse,
    TalentTreeResponse,
)

router = APIRouter(tags=["meta-progression"])


# ── Helpers ────────────────────────────────────────────────────────────


async def _get_or_create_meta(
    campaign_id: str, db: AsyncSession
) -> CampaignMeta:
    """Get existing CampaignMeta or create one."""
    result = await db.execute(
        select(CampaignMeta).where(CampaignMeta.campaign_id == campaign_id)
    )
    meta = result.scalar_one_or_none()
    if meta:
        return meta

    # Verify campaign exists
    camp = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    if not camp.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    meta = CampaignMeta(
        id=str(ULID()),
        campaign_id=campaign_id,
    )
    db.add(meta)
    try:
        await db.flush()
    except Exception:
        await db.rollback()
        # Race condition: another request created it
        result = await db.execute(
            select(CampaignMeta).where(
                CampaignMeta.campaign_id == campaign_id
            )
        )
        meta = result.scalar_one_or_none()
        if not meta:
            raise
    return meta


def _meta_to_response(meta: CampaignMeta) -> MetaResponse:
    return MetaResponse(
        essence_balance=meta.essence_balance,
        essence_lifetime=meta.essence_lifetime,
        unlocked_talents=meta.unlocked_talents or [],
        achievements=meta.achievements or [],
        total_runs_completed=meta.total_runs_completed,
        total_runs_won=meta.total_runs_won,
        highest_floor_reached=meta.highest_floor_reached,
        total_floors_cleared=meta.total_floors_cleared,
        total_deaths_all_runs=meta.total_deaths_all_runs,
        secret_floors_discovered=meta.secret_floors_discovered or [],
        lore_fragments_found=meta.lore_fragments_found or [],
        antagonist_encounters=meta.antagonist_encounters,
    )


# ── Campaign Meta Overview ─────────────────────────────────────────────


@router.get(
    "/campaigns/{campaign_id}/meta",
    response_model=MetaResponse,
)
async def get_meta(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Get campaign meta-progression state (auto-creates if missing)."""
    meta = await _get_or_create_meta(campaign_id, db)
    await db.commit()
    return _meta_to_response(meta)


# ── Talent Tree ────────────────────────────────────────────────────────


@router.get(
    "/campaigns/{campaign_id}/meta/talents",
    response_model=TalentTreeResponse,
)
async def get_talents(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Get the full talent tree with unlock/affordability status."""
    meta = await _get_or_create_meta(campaign_id, db)
    await db.commit()
    unlocked = meta.unlocked_talents or []
    essence = meta.essence_balance

    talents: list[TalentResponse] = []
    for t in TALENT_TREE:
        # Check prerequisite: all lower tiers in same branch unlocked
        prereq_met = all(
            bt.id in unlocked
            for bt in TALENT_TREE
            if bt.branch == t.branch and bt.tier < t.tier
        )
        talents.append(
            TalentResponse(
                id=t.id,
                name=t.name,
                branch=t.branch,
                tier=t.tier,
                cost=t.cost,
                effect_key=t.effect_key,
                description=t.description,
                is_unlocked=t.id in unlocked,
                can_afford=t.cost <= essence,
                prerequisite_met=prereq_met,
            )
        )

    return TalentTreeResponse(talents=talents, essence_balance=essence)


@router.post(
    "/campaigns/{campaign_id}/meta/talents/{talent_id}/unlock",
    response_model=TalentTreeResponse,
)
async def unlock_talent_endpoint(
    campaign_id: str, talent_id: str, db: AsyncSession = Depends(get_db)
):
    """Spend essence to unlock a talent."""
    meta = await _get_or_create_meta(campaign_id, db)
    unlocked = list(meta.unlocked_talents or [])
    essence = meta.essence_balance

    talent = get_talent(talent_id)
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    if not can_unlock(talent_id, unlocked, essence):
        raise HTTPException(
            status_code=400,
            detail="Cannot unlock: insufficient essence or prerequisite not met",
        )

    new_unlocked, new_essence = unlock_talent(talent_id, unlocked, essence)
    meta.unlocked_talents = new_unlocked
    meta.essence_balance = new_essence
    await db.commit()

    # Return updated tree
    return await get_talents(campaign_id, db)


# ── Achievements ───────────────────────────────────────────────────────


@router.get(
    "/campaigns/{campaign_id}/meta/achievements",
    response_model=list[AchievementResponse],
)
async def get_achievements(
    campaign_id: str, db: AsyncSession = Depends(get_db)
):
    """Get all achievements with earned/unearned status."""
    meta = await _get_or_create_meta(campaign_id, db)
    await db.commit()
    earned = set(meta.achievements or [])

    return [
        AchievementResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            category=a.category,
            essence_reward=a.essence_reward,
            is_earned=a.id in earned,
        )
        for a in ACHIEVEMENTS
    ]


# ── Lore ───────────────────────────────────────────────────────────────


@router.get(
    "/campaigns/{campaign_id}/meta/lore",
    response_model=list[LoreFragmentResponse],
)
async def get_lore(campaign_id: str, db: AsyncSession = Depends(get_db)):
    """Get all lore fragments with discovered/undiscovered status."""
    meta = await _get_or_create_meta(campaign_id, db)
    await db.commit()
    found = set(meta.lore_fragments_found or [])

    return [
        LoreFragmentResponse(
            id=f.id,
            title=f.title if f.id in found else "???",
            text=f.text if f.id in found else "",
            category=f.category,
            source=f.source if f.id in found else "",
            is_discovered=f.id in found,
        )
        for f in LORE_FRAGMENTS
    ]


@router.get(
    "/campaigns/{campaign_id}/meta/lore-beats/{floor_number}",
    response_model=list[LoreBeatResponse],
)
async def get_lore_beats_endpoint(
    campaign_id: str,
    floor_number: int,
    trigger: str = "floor_end",
    db: AsyncSession = Depends(get_db),
):
    """Get lore beats for a specific floor and trigger."""
    meta = await _get_or_create_meta(campaign_id, db)
    await db.commit()
    run_number = meta.total_runs_completed + 1

    beats = get_lore_beats_for_floor(
        floor_number=floor_number,
        run_number=run_number,
        trigger=trigger,
        context={"deaths_this_run": 0},
    )

    return [
        LoreBeatResponse(
            id=b.id,
            floor=b.floor,
            act=b.act,
            trigger=b.trigger,
            arbiter_text=b.arbiter_text,
            aethon_text=b.aethon_text,
            dm_stage_direction=b.dm_stage_direction,
            lore_fragment_id=b.lore_fragment_id,
        )
        for b in beats
    ]


# ── Run Completion with Meta ───────────────────────────────────────────


@router.post(
    "/campaigns/{campaign_id}/runs/{run_id}/complete-meta",
    response_model=RunEndMetaResponse,
)
async def complete_run_meta(
    campaign_id: str, run_id: str, db: AsyncSession = Depends(get_db)
):
    """Complete a run and compute meta-progression rewards.

    This handles: essence computation, achievement checking, CampaignMeta
    updates, and PPC decay.
    """
    # Load run
    result = await db.execute(
        select(Run).where(Run.id == run_id, Run.campaign_id == campaign_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    meta = await _get_or_create_meta(campaign_id, db)

    # Compute essence
    run_won = run.outcome == "completed"
    boss_kills = 0  # Simplified: count from floors
    for i in range(run.floors_completed):
        if (i + 1) % 4 == 0:  # Boss every 4 floors
            boss_kills += 1

    essence_earned = compute_run_essence(
        floors_completed=run.floors_completed,
        boss_kills=boss_kills,
        achievements_earned=0,  # Counted separately below
        run_won=run_won,
    )

    # Build run stats for achievement checking
    run_stats = {
        "floors_completed": run.floors_completed,
        "total_deaths": run.total_deaths,
        "run_won": run_won,
        "had_deathless_floor": True,  # Simplified assumption
        "templates_used": [],
        "gold_spent": 0,
        "secret_events": run.secret_events or [],
        "collector_killed": False,
        "total_social_successes": 0,
        "total_runs_completed": meta.total_runs_completed + 1,
        "total_shards_lifetime": run.total_shards_earned,
        "total_lore_fragments": len(meta.lore_fragments_found or []),
        "tpk_saved": False,
        "aethon_defeated": run_won and run.floors_completed >= 19,
    }

    new_achievement_ids = check_achievements(run_stats, meta.achievements or [])
    achievement_essence = sum(
        (get_achievement(aid).essence_reward if get_achievement(aid) else 0)
        for aid in new_achievement_ids
    )
    essence_earned += achievement_essence

    # Update meta
    meta.essence_balance += essence_earned
    meta.essence_lifetime += essence_earned
    meta.total_runs_completed += 1
    if run_won:
        meta.total_runs_won += 1
    if run.floors_completed > meta.highest_floor_reached:
        meta.highest_floor_reached = run.floors_completed
    meta.total_floors_cleared += run.floors_completed
    meta.total_deaths_all_runs += run.total_deaths

    # Merge achievements
    existing_achievements = list(meta.achievements or [])
    for aid in new_achievement_ids:
        if aid not in existing_achievements:
            existing_achievements.append(aid)
    meta.achievements = existing_achievements

    # Merge lore from run
    existing_lore = list(meta.lore_fragments_found or [])
    run_lore_beats = run.lore_beats_triggered or []
    new_lore_ids = []
    for beat_id in run_lore_beats:
        # Extract fragment_id if the beat carried one
        if beat_id not in existing_lore:
            existing_lore.append(beat_id)
            new_lore_ids.append(beat_id)
    meta.lore_fragments_found = existing_lore

    # Decay PPC on the campaign
    camp_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = camp_result.scalar_one_or_none()
    if campaign:
        campaign.party_power_coefficient = decay_ppc_between_runs(
            campaign.party_power_coefficient
        )

    # Update run with essence
    run.essence_earned = essence_earned

    await db.commit()

    # Count affordable talents
    unlocked = meta.unlocked_talents or []
    affordable = sum(
        1 for t in TALENT_TREE
        if can_unlock(t.id, unlocked, meta.essence_balance)
    )

    # Build response
    new_achievements = [
        AchievementResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            category=a.category,
            essence_reward=a.essence_reward,
            is_earned=True,
        )
        for aid in new_achievement_ids
        if (a := get_achievement(aid))
    ]

    new_lore_fragments = [
        LoreFragmentResponse(
            id=frag.id,
            title=frag.title,
            text=frag.text,
            category=frag.category,
            source=frag.source,
            is_discovered=True,
        )
        for fid in new_lore_ids
        if (frag := get_lore_fragment(fid))
    ]

    return RunEndMetaResponse(
        essence_earned=essence_earned,
        new_achievements=new_achievements,
        lore_fragments_discovered=new_lore_fragments,
        total_essence=meta.essence_balance,
        talents_affordable=affordable,
    )
