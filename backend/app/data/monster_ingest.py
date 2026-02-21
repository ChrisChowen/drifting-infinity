"""Transform Open5e monster data into internal Monster schema and store in DB."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.behaviour_profiles import build_behaviour_profile
from app.data.open5e_client import Open5eClient
from app.data.role_classifier import classify_tactical_role
from app.data.signature_builder import build_mechanical_signature
from app.data.xp_thresholds import cr_to_xp, parse_cr
from app.models.monster import Monster

logger = logging.getLogger(__name__)


def _parse_ability_scores(raw: dict) -> dict[str, int]:
    return {
        "str": raw.get("strength", 10),
        "dex": raw.get("dexterity", 10),
        "con": raw.get("constitution", 10),
        "int": raw.get("intelligence", 10),
        "wis": raw.get("wisdom", 10),
        "cha": raw.get("charisma", 10),
    }


def _parse_saves(raw: dict, abilities: dict[str, int]) -> dict[str, int]:
    """Parse saves - use proficient values if available, else derive from ability."""
    save_map = {
        "strength_save": "str",
        "dexterity_save": "dex",
        "constitution_save": "con",
        "intelligence_save": "int",
        "wisdom_save": "wis",
        "charisma_save": "cha",
    }
    saves = {}
    for field, short in save_map.items():
        val = raw.get(field)
        if val is not None:
            saves[short] = val
        else:
            saves[short] = (abilities[short] - 10) // 2
    return saves


# Vulnerability overrides based on D&D lore for creatures that typically
# have well-known vulnerabilities but may not list them in the SRD data.
# Keyed by creature_type or specific name patterns.
VULNERABILITY_OVERRIDES_BY_TYPE: dict[str, list[str]] = {
    "undead": ["radiant"],
    "fiend": ["radiant"],
    "plant": ["fire"],
}

VULNERABILITY_OVERRIDES_BY_NAME: dict[str, list[str]] = {
    "troll": ["fire", "acid"],
    "treant": ["fire"],
    "ice mephit": ["fire"],
    "ice elemental": ["fire"],
    "fire elemental": ["cold"],
    "magma mephit": ["cold"],
    "shadow": ["radiant"],
    "shadow demon": ["radiant"],
    "wraith": ["radiant"],
    "specter": ["radiant"],
    "vampire": ["radiant"],
    "mummy": ["fire"],
    "flesh golem": ["fire"],
    "iron golem": ["lightning"],
    "clay golem": ["acid"],
}


def _parse_vulnerabilities(vuln_string: str) -> list[str]:
    """Parse vulnerability string into list of damage types."""
    if not vuln_string:
        return []
    return [v.strip().lower() for v in vuln_string.split(",") if v.strip()]


def _infer_vulnerabilities(
    explicit_vulns: list[str],
    creature_type: str,
    name: str,
) -> list[str]:
    """Combine explicit vulnerabilities with lore-based inferences.

    Only adds inferred vulnerabilities if there are no explicit ones,
    to avoid overriding the actual data.
    """
    if explicit_vulns:
        return explicit_vulns

    inferred: list[str] = []
    name_lower = name.lower()

    # Check name-based overrides first (more specific)
    for pattern, vulns in VULNERABILITY_OVERRIDES_BY_NAME.items():
        if pattern in name_lower:
            inferred.extend(vulns)
            break

    # If no name match, check type-based overrides
    if not inferred:
        creature_type_lower = creature_type.lower()
        for ctype, vulns in VULNERABILITY_OVERRIDES_BY_TYPE.items():
            if ctype in creature_type_lower:
                inferred.extend(vulns)
                break

    return inferred


def _identify_weak_saves(saves: dict[str, int]) -> list[dict[str, int | str]]:
    """Identify the 2 lowest saves as 'weak' for weakness exploit purposes.

    Previously only identified negative modifiers, which meant high-CR
    creatures (all positive saves) had no weak saves. Now always returns
    the 2 lowest regardless of sign.
    """
    sorted_saves = sorted(saves.items(), key=lambda x: x[1])
    return [
        {"ability": ability, "modifier": mod}
        for ability, mod in sorted_saves[:2]
    ]


def _classify_intelligence_tier(int_score: int) -> str:
    """Classify intelligence tier from INT ability score."""
    if int_score <= 2:
        return "mindless"
    elif int_score <= 7:
        return "instinctual"
    elif int_score <= 14:
        return "cunning"
    else:
        return "mastermind"


ENVIRONMENT_INFERENCE_BY_TYPE: dict[str, list[str]] = {
    "beast": ["forest", "grassland"],
    "plant": ["forest", "swamp"],
    "undead": ["underdark", "haunted_ruins"],
    "elemental": ["planar", "elemental_nexus"],
    "fiend": ["planar"],
    "celestial": ["planar"],
    "aberration": ["underdark", "planar"],
    "construct": ["urban", "temple_interior"],
    "dragon": ["mountain", "volcanic_caldera"],
    "monstrosity": ["cave", "mountain"],
    "ooze": ["underdark", "cave"],
    "fey": ["forest", "feywild"],
    "giant": ["mountain", "arctic"],
    "humanoid": ["urban", "grassland"],
}


def _infer_environments_from_type(creature_type: str) -> list[str]:
    """Infer plausible environments from creature type when none are tagged."""
    ct = creature_type.lower().strip()
    for key, envs in ENVIRONMENT_INFERENCE_BY_TYPE.items():
        if key in ct:
            return list(envs)
    return []


def transform_open5e_monster(raw: dict) -> dict:
    """Transform Open5e JSON into internal Monster fields."""
    cr = parse_cr(raw.get("challenge_rating", "0"))
    xp = cr_to_xp(cr)
    abilities = _parse_ability_scores(raw)
    saves = _parse_saves(raw, abilities)

    statblock = {
        # Identity
        "name": raw.get("name", "Unknown"),
        "size": raw.get("size", "Medium"),
        "type": raw.get("type", ""),
        "alignment": raw.get("alignment", ""),
        # Core stats
        "armor_class": raw.get("armor_class", 10),
        "hit_points": raw.get("hit_points", 1),
        "hit_dice": raw.get("hit_dice", ""),
        "speed": raw.get("speed", {}),
        "challenge_rating": str(cr),
        # Ability scores (individual for frontend stat block rendering)
        "strength": abilities["str"],
        "dexterity": abilities["dex"],
        "constitution": abilities["con"],
        "intelligence": abilities["int"],
        "wisdom": abilities["wis"],
        "charisma": abilities["cha"],
        # Saves
        "strength_save": saves.get("str"),
        "dexterity_save": saves.get("dex"),
        "constitution_save": saves.get("con"),
        "intelligence_save": saves.get("int"),
        "wisdom_save": saves.get("wis"),
        "charisma_save": saves.get("cha"),
        # Defenses & senses
        "senses": raw.get("senses", ""),
        "languages": raw.get("languages", ""),
        "damage_vulnerabilities": raw.get("damage_vulnerabilities", ""),
        "damage_resistances": raw.get("damage_resistances", ""),
        "damage_immunities": raw.get("damage_immunities", ""),
        "condition_immunities": raw.get("condition_immunities", ""),
        # Skills
        "skills": raw.get("skills") or {},
        # Actions & abilities
        "actions": raw.get("actions") or [],
        "bonus_actions": raw.get("bonus_actions") or [],
        "special_abilities": raw.get("special_abilities") or [],
        "legendary_actions": raw.get("legendary_actions") or [],
        "legendary_desc": raw.get("legendary_desc", ""),
        "reactions": raw.get("reactions") or [],
        # Legacy (kept for internal use)
        "abilities": abilities,
        "saves": saves,
    }

    explicit_vulns = _parse_vulnerabilities(raw.get("damage_vulnerabilities", ""))
    creature_type = raw.get("type", "")
    name = raw.get("name", "Unknown")
    vulnerabilities = _infer_vulnerabilities(explicit_vulns, creature_type, name)
    weak_saves = _identify_weak_saves(saves)
    intelligence_tier = _classify_intelligence_tier(abilities["int"])

    # Build mechanical signature
    signature = build_mechanical_signature(statblock, cr)

    # Classify tactical role
    role, secondary = classify_tactical_role(statblock, cr)

    # Build behaviour profile
    profile = build_behaviour_profile(role, statblock, intelligence_tier)

    # Infer environments from creature type for monsters with no environment tags
    environments = raw.get("environments") or []
    if not environments and creature_type:
        environments = _infer_environments_from_type(creature_type)

    source_doc = raw.get("_source_document", raw.get("document__slug", "srd-5.2"))

    return {
        "id": str(ULID()),
        "slug": raw.get("slug", raw.get("name", "unknown").lower().replace(" ", "-")),
        "name": name,
        "source": source_doc,
        "cr": cr,
        "xp": xp,
        "hp": raw.get("hit_points", 1),
        "hit_dice": raw.get("hit_dice", ""),
        "ac": raw.get("armor_class", 10),
        "size": raw.get("size", "Medium"),
        "creature_type": raw.get("type", ""),
        "alignment": raw.get("alignment", ""),
        "tactical_role": role,
        "secondary_role": secondary,
        "intelligence_tier": intelligence_tier,
        "mechanical_signature": signature,
        "behaviour_profile": profile,
        "vulnerabilities": vulnerabilities,
        "weak_saves": weak_saves,
        "environments": environments,
        "statblock": statblock,
        "tagging_source": "automated",
        "tagging_confidence": 0.7,
        "last_tagged_at": datetime.now(timezone.utc),
    }


async def ingest_srd_monsters(db: AsyncSession) -> int:
    """Fetch all SRD monsters from Open5e and store in database."""
    client = Open5eClient()
    try:
        raw_monsters = await client.fetch_srd_monsters()
    finally:
        await client.close()

    return await _ingest_raw_monsters(db, raw_monsters)


async def ingest_curated_monsters(db: AsyncSession) -> int:
    """Fetch monsters from curated sources (SRD + Kobold Press) and store.

    Safe to call on existing databases — dedup by slug in _ingest_raw_monsters
    prevents re-adding monsters that are already present.
    """
    client = Open5eClient()
    try:
        raw_monsters = await client.fetch_curated_monsters()
    finally:
        await client.close()

    return await _ingest_raw_monsters(db, raw_monsters)


async def ingest_all_monsters(db: AsyncSession) -> int:
    """Fetch monsters from all available Open5e sources and store in database."""
    client = Open5eClient()
    try:
        raw_monsters = await client.fetch_all_available_monsters()
    finally:
        await client.close()

    return await _ingest_raw_monsters(db, raw_monsters)


async def _ingest_raw_monsters(db: AsyncSession, raw_monsters: list[dict]) -> int:
    """Ingest a list of raw monster dicts into the database."""
    count = 0
    for raw in raw_monsters:
        # Normalize fields from different sources
        raw = _normalize_source_fields(raw)

        slug = raw.get("slug", "")
        # Check if already exists
        existing = await db.execute(select(Monster).where(Monster.slug == slug))
        if existing.scalar_one_or_none():
            logger.debug(f"Skipping existing monster: {slug}")
            continue

        try:
            data = transform_open5e_monster(raw)
            monster = Monster(**data)
            db.add(monster)
            count += 1
        except Exception as e:
            logger.error(f"Failed to ingest monster '{raw.get('name', '?')}': {e}")
            continue

    await db.commit()
    logger.info(f"Ingested {count} new monsters")
    return count


def _normalize_source_fields(raw: dict) -> dict:
    """Normalize field names from different Open5e document sources.

    Different sources may use slightly different field names.
    This maps them to the standard schema we expect.
    """
    # Some sources use 'cr' instead of 'challenge_rating'
    if "challenge_rating" not in raw and "cr" in raw:
        raw["challenge_rating"] = raw["cr"]

    # Some sources use 'hit_points' vs 'hp'
    if "hit_points" not in raw and "hp" in raw:
        raw["hit_points"] = raw["hp"]

    # Some sources use 'armor_class' as int vs dict
    ac = raw.get("armor_class")
    if isinstance(ac, list) and ac:
        raw["armor_class"] = ac[0].get("value", 10) if isinstance(ac[0], dict) else ac[0]
    elif isinstance(ac, dict):
        raw["armor_class"] = ac.get("value", 10)

    # Ensure environments is a list
    envs = raw.get("environments")
    if isinstance(envs, str):
        raw["environments"] = [e.strip() for e in envs.split(",") if e.strip()]

    return raw
