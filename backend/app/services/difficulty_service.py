"""Difficulty service — integrates Director AI with database state.

The Director uses a between-floor calibration model:
- Floor difficulty is set once per floor from the intensity curve + PPC
- Within a floor, arenas share the same base difficulty with pacing variation
- Intra-floor pacing is attrition-aware: the rest schedule is passed to the
  intensity curve so XP budgets account for expected resource drain
- PPC adjusts between floors based on DM assessment and party state
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.combat.rest import rest_schedule_for_floor
from app.engine.difficulty.intensity_curve import compute_intensity_curve
from app.engine.difficulty.target_computer import DifficultyTarget, compute_difficulty_target
from app.engine.scaling import get_scaling_params
from app.models.arena import Arena
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.floor import Floor
from app.models.run import Run
from app.models.snapshot import HealthSnapshot


async def compute_arena_difficulty(
    db: AsyncSession,
    arena: Arena,
    floor: Floor,
    run: Run,
    campaign: Campaign,
) -> DifficultyTarget:
    """Compute the difficulty target for an arena using the Director AI.

    Uses the intensity curve for floor-level base difficulty + intra-floor
    pacing (attrition-aware), then applies between-floor calibration from
    the PREVIOUS floor's health snapshot.
    """
    # Step 0: Build rest schedule for this floor so the intensity curve
    # can model expected attrition at each arena position.
    party_size_result = await db.scalar(
        select(func.count()).select_from(Character).where(
            Character.campaign_id == campaign.id
        )
    )
    party_size = party_size_result or 1
    scaling = get_scaling_params(party_size)
    rest_schedule = rest_schedule_for_floor(
        floor.arena_count, scaling.short_rests_per_floor,
    )

    # Step 1: Get intensity from curve (floor base + attrition-aware pacing)
    intensity = compute_intensity_curve(
        arena_number=arena.arena_number,
        total_arenas=floor.arena_count,
        floor_number=floor.floor_number,
        party_power_coefficient=campaign.party_power_coefficient,
        rest_schedule=rest_schedule,
    )

    # Step 2: Get health snapshot from the PREVIOUS floor (between-floor calibration)
    # We look for the last snapshot from any floor before this one in the same run.
    previous_floor_snapshot = None
    if floor.floor_number > 1:
        snapshot_result = await db.execute(
            select(HealthSnapshot)
            .join(Floor, HealthSnapshot.floor_id == Floor.id)
            .where(
                Floor.run_id == run.id,
                Floor.floor_number < floor.floor_number,
            )
            .order_by(Floor.floor_number.desc(), HealthSnapshot.after_arena_number.desc())
        )
        previous_floor_snapshot = snapshot_result.scalars().first()

    # Step 3: Compute adjusted target using between-floor data
    if previous_floor_snapshot:
        target = compute_difficulty_target(
            base_intensity=intensity.intensity,
            previous_floor_avg_hp=previous_floor_snapshot.average_hp_percentage,
            previous_floor_deaths=previous_floor_snapshot.deaths_count,
            previous_floor_tpk=previous_floor_snapshot.was_tpk,
            resource_depletion=previous_floor_snapshot.estimated_resource_depletion,
            party_power_coefficient=campaign.party_power_coefficient,
            dm_assessment=previous_floor_snapshot.dm_assessment,
        )
    else:
        # First floor or no snapshots yet — use base intensity only
        target = compute_difficulty_target(
            base_intensity=intensity.intensity,
            party_power_coefficient=campaign.party_power_coefficient,
        )

    return target
