from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.database import get_db
from app.models.arena import Arena
from app.models.floor import Floor
from app.models.snapshot import HealthSnapshot
from app.schemas.snapshot import HealthSnapshotCreate, HealthSnapshotResponse

router = APIRouter(prefix="/floors/{floor_id}/snapshots", tags=["snapshots"])


def _compute_snapshot_stats(data: HealthSnapshotCreate) -> dict:
    """Compute derived fields from character snapshot data."""
    if not data.character_snapshots:
        return {
            "average_hp_percentage": 1.0,
            "lowest_hp_percentage": 1.0,
            "any_dead": False,
            "estimated_resource_depletion": 0.0,
        }

    hp_pcts = [cs.hp_percentage for cs in data.character_snapshots]
    return {
        "average_hp_percentage": sum(hp_pcts) / len(hp_pcts),
        "lowest_hp_percentage": min(hp_pcts),
        "any_dead": any(cs.is_dead for cs in data.character_snapshots),
        "estimated_resource_depletion": sum(
            cs.resources_depleted for cs in data.character_snapshots
        ) / len(data.character_snapshots),
    }


def _compute_cumulative_stress(
    dm_assessment: str, any_dead: bool, lowest_hp: float, prev_stress: float
) -> float:
    """Compute cumulative stress from snapshot."""
    stress_map = {"healthy": 0.0, "strained": 0.25, "critical": 0.5, "dire": 0.75}
    base = stress_map.get(dm_assessment, 0.0)
    if any_dead:
        base += 0.3
    if lowest_hp < 0.25:
        base += 0.1
    return min(1.0, prev_stress + base * 0.5)


@router.get("", response_model=list[HealthSnapshotResponse])
async def list_snapshots(floor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HealthSnapshot)
        .where(HealthSnapshot.floor_id == floor_id)
        .order_by(HealthSnapshot.after_arena_number)
    )
    snapshots = result.scalars().all()
    return [
        HealthSnapshotResponse(
            id=s.id, floor_id=s.floor_id,
            after_arena_number=s.after_arena_number,
            dm_assessment=s.dm_assessment,
            dm_combat_perception=s.dm_combat_perception,
            any_on_final_stand=s.any_on_final_stand,
            character_snapshots=s.character_snapshots,
            average_hp_percentage=s.average_hp_percentage,
            lowest_hp_percentage=s.lowest_hp_percentage,
            any_dead=s.any_dead,
            estimated_resource_depletion=s.estimated_resource_depletion,
            cumulative_stress=s.cumulative_stress,
        )
        for s in snapshots
    ]


@router.post("", response_model=HealthSnapshotResponse)
async def submit_snapshot(
    floor_id: str, data: HealthSnapshotCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify floor exists
    floor = await db.get(Floor, floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    # Determine arena number from latest completed arena
    arena_result = await db.execute(
        select(Arena).where(
            Arena.floor_id == floor_id,
            Arena.is_complete.is_(True),
        ).order_by(Arena.arena_number.desc())
    )
    latest_arena = arena_result.scalars().first()
    after_arena = latest_arena.arena_number if latest_arena else 0

    # Compute stats
    stats = _compute_snapshot_stats(data)

    # Get previous snapshot for cumulative stress
    prev_result = await db.execute(
        select(HealthSnapshot)
        .where(HealthSnapshot.floor_id == floor_id)
        .order_by(HealthSnapshot.after_arena_number.desc())
    )
    prev = prev_result.scalars().first()
    prev_stress = prev.cumulative_stress if prev else 0.0

    cumulative_stress = _compute_cumulative_stress(
        data.dm_assessment, stats["any_dead"],
        stats["lowest_hp_percentage"], prev_stress,
    )

    snapshot = HealthSnapshot(
        id=str(ULID()),
        floor_id=floor_id,
        after_arena_number=after_arena,
        dm_assessment=data.dm_assessment,
        dm_combat_perception=data.dm_combat_perception,
        any_on_final_stand=data.any_on_final_stand,
        character_snapshots=[cs.model_dump() for cs in data.character_snapshots],
        average_hp_percentage=stats["average_hp_percentage"],
        lowest_hp_percentage=stats["lowest_hp_percentage"],
        any_dead=stats["any_dead"],
        estimated_resource_depletion=stats["estimated_resource_depletion"],
        cumulative_stress=cumulative_stress,
    )
    db.add(snapshot)
    await db.flush()

    return HealthSnapshotResponse(
        id=snapshot.id, floor_id=snapshot.floor_id,
        after_arena_number=snapshot.after_arena_number,
        dm_assessment=snapshot.dm_assessment,
        dm_combat_perception=snapshot.dm_combat_perception,
        any_on_final_stand=snapshot.any_on_final_stand,
        character_snapshots=snapshot.character_snapshots,
        average_hp_percentage=snapshot.average_hp_percentage,
        lowest_hp_percentage=snapshot.lowest_hp_percentage,
        any_dead=snapshot.any_dead,
        estimated_resource_depletion=snapshot.estimated_resource_depletion,
        cumulative_stress=snapshot.cumulative_stress,
    )
