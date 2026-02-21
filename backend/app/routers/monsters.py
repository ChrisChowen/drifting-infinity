from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.monster_ingest import ingest_srd_monsters
from app.database import get_db
from app.models.monster import Monster

router = APIRouter(prefix="/monsters", tags=["monsters"])


@router.get("")
async def list_monsters(
    cr_min: float | None = None,
    cr_max: float | None = None,
    role: str | None = None,
    search: str | None = None,
    source: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Monster)

    if cr_min is not None:
        query = query.where(Monster.cr >= cr_min)
    if cr_max is not None:
        query = query.where(Monster.cr <= cr_max)
    if role:
        query = query.where(Monster.tactical_role == role)
    if search:
        query = query.where(Monster.name.ilike(f"%{search}%"))
    if source:
        query = query.where(Monster.source == source)

    query = query.order_by(Monster.cr, Monster.name).offset(offset).limit(limit)
    result = await db.execute(query)
    monsters = result.scalars().all()

    # Also get total count
    count_query = select(func.count(Monster.id))
    if cr_min is not None:
        count_query = count_query.where(Monster.cr >= cr_min)
    if cr_max is not None:
        count_query = count_query.where(Monster.cr <= cr_max)
    if role:
        count_query = count_query.where(Monster.tactical_role == role)
    if search:
        count_query = count_query.where(Monster.name.ilike(f"%{search}%"))
    if source:
        count_query = count_query.where(Monster.source == source)

    total = (await db.execute(count_query)).scalar() or 0

    return {
        "total": total,
        "monsters": [
            {
                "id": m.id,
                "slug": m.slug,
                "name": m.name,
                "cr": m.cr,
                "xp": m.xp,
                "hp": m.hp,
                "ac": m.ac,
                "size": m.size,
                "creature_type": m.creature_type,
                "tactical_role": m.tactical_role,
                "secondary_role": m.secondary_role,
                "vulnerabilities": m.vulnerabilities,
                "weak_saves": m.weak_saves,
                "environments": m.environments,
            }
            for m in monsters
        ],
    }


@router.get("/{monster_id}")
async def get_monster(monster_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Monster).where(Monster.id == monster_id))
    monster = result.scalar_one_or_none()
    if not monster:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Monster not found")

    return {
        "id": monster.id,
        "slug": monster.slug,
        "name": monster.name,
        "source": monster.source,
        "cr": monster.cr,
        "xp": monster.xp,
        "hp": monster.hp,
        "hit_dice": monster.hit_dice,
        "ac": monster.ac,
        "size": monster.size,
        "creature_type": monster.creature_type,
        "alignment": monster.alignment,
        "tactical_role": monster.tactical_role,
        "secondary_role": monster.secondary_role,
        "intelligence_tier": monster.intelligence_tier,
        "mechanical_signature": monster.mechanical_signature,
        "behaviour_profile": monster.behaviour_profile,
        "vulnerabilities": monster.vulnerabilities,
        "weak_saves": monster.weak_saves,
        "environments": monster.environments,
        "statblock": monster.statblock,
        "tagging_source": monster.tagging_source,
        "tagging_confidence": monster.tagging_confidence,
    }


@router.post("/ingest")
async def ingest_monsters(db: AsyncSession = Depends(get_db)):
    """Trigger SRD monster ingestion from Open5e API."""
    count = await ingest_srd_monsters(db)
    return {"message": f"Ingested {count} monsters", "count": count}
