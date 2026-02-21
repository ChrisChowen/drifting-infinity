"""Fetch SRD spells from Open5e and store in the database."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.open5e_client import Open5eClient
from app.models.spell import Spell

logger = logging.getLogger(__name__)


def transform_spell(raw: dict) -> dict:
    """Transform Open5e spell JSON into internal Spell fields."""
    # Open5e level_int field, or parse from level string
    level = raw.get("level_int")
    if level is None:
        level_str = raw.get("level", "0")
        try:
            level = int(level_str)
        except (ValueError, TypeError):
            level = 0

    desc = raw.get("desc", "") or ""
    if len(desc) > 2000:
        desc = desc[:1997] + "..."

    return {
        "id": str(ULID()),
        "slug": raw.get("slug", ""),
        "name": raw.get("name", "Unknown Spell"),
        "level": level,
        "school": raw.get("school", "unknown").lower(),
        "casting_time": raw.get("casting_time", "") or "",
        "spell_range": raw.get("range", "") or "",
        "components": raw.get("components", "") or "",
        "duration": raw.get("duration", "") or "",
        "description": desc,
        "source": "srd-5.2",
    }


async def ingest_srd_spells(db: AsyncSession) -> int:
    """Fetch SRD spells from Open5e and store in database."""
    client = Open5eClient()
    try:
        raw_spells = await client.fetch_srd_spells()
    finally:
        await client.close()

    count = 0
    for raw in raw_spells:
        slug = raw.get("slug", "")
        if not slug:
            continue
        # Check for existing
        existing = await db.execute(select(Spell).where(Spell.slug == slug))
        if existing.scalar_one_or_none():
            continue

        try:
            data = transform_spell(raw)
            spell = Spell(**data)
            db.add(spell)
            count += 1
        except Exception as e:
            logger.error(f"Failed to ingest spell '{raw.get('name', '?')}': {e}")
            continue

    await db.commit()
    logger.info(f"Ingested {count} new spells")
    return count
