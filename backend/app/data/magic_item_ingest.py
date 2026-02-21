"""Fetch SRD magic items from Open5e and store in the database."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.open5e_client import Open5eClient
from app.models.magic_item import MagicItem

logger = logging.getLogger(__name__)

# Rarity mapping (Open5e uses various formats)
RARITY_MAP: dict[str, str] = {
    "common": "common",
    "uncommon": "uncommon",
    "rare": "rare",
    "very rare": "very_rare",
    "very-rare": "very_rare",
    "legendary": "legendary",
    "artifact": "legendary",  # Treat artifacts as legendary
}

# Gold values by rarity
GOLD_VALUES: dict[str, int] = {
    "common": 50,
    "uncommon": 150,
    "rare": 500,
    "very_rare": 2000,
    "legendary": 5000,
}

# Minimum floor by rarity
FLOOR_MINS: dict[str, int] = {
    "common": 1,
    "uncommon": 1,
    "rare": 2,
    "very_rare": 3,
    "legendary": 4,
}


def _categorize_type(type_str: str) -> str:
    """Categorize a magic item type for roguelike integration."""
    t = type_str.lower()
    if "potion" in t or "scroll" in t:
        return "consumable"
    elif "armor" in t or "weapon" in t or "shield" in t:
        return "equipment"
    else:
        return "wondrous"


def transform_magic_item(raw: dict) -> dict:
    """Transform Open5e magic item JSON into internal MagicItem fields."""
    rarity_raw = (raw.get("rarity") or "common").lower().strip()
    rarity = RARITY_MAP.get(rarity_raw, "common")
    type_str = raw.get("type", "Wondrous item") or "Wondrous item"

    attunement_str = raw.get("requires_attunement") or ""
    requires_attunement = bool(
        attunement_str and attunement_str.lower() not in ("", "no", "false")
    )

    desc = raw.get("desc", "") or ""
    # Truncate very long descriptions
    if len(desc) > 1000:
        desc = desc[:997] + "..."

    return {
        "id": str(ULID()),
        "slug": raw.get("slug", ""),
        "name": raw.get("name", "Unknown Item"),
        "rarity": rarity,
        "type": type_str,
        "requires_attunement": requires_attunement,
        "description": desc,
        "source": "srd-5.2",
        "category": _categorize_type(type_str),
        "floor_min": FLOOR_MINS.get(rarity, 1),
        "gold_value": GOLD_VALUES.get(rarity, 100),
    }


async def ingest_srd_magic_items(db: AsyncSession) -> int:
    """Fetch SRD magic items from Open5e and store in database."""
    client = Open5eClient()
    try:
        raw_items = await client.fetch_srd_magic_items()
    finally:
        await client.close()

    count = 0
    for raw in raw_items:
        slug = raw.get("slug", "")
        if not slug:
            continue
        # Check for existing
        existing = await db.execute(select(MagicItem).where(MagicItem.slug == slug))
        if existing.scalar_one_or_none():
            continue

        try:
            data = transform_magic_item(raw)
            item = MagicItem(**data)
            db.add(item)
            count += 1
        except Exception as e:
            logger.error(f"Failed to ingest magic item '{raw.get('name', '?')}': {e}")
            continue

    await db.commit()
    logger.info(f"Ingested {count} new magic items")
    return count
