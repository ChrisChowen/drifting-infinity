"""Party Strength Computation (Phase 11C).

Computes the party's effective combat power beyond just level,
accounting for enhancements, gacha items, and level-ups.
This feeds into the Director AI to scale encounter difficulty.
"""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character


@dataclass
class PartyStrengthResult:
    effective_level: int
    enhancement_power: float
    item_power: float
    strength_multiplier: float
    notes: list[str] = field(default_factory=list)


# Rarity → estimated power contribution per item
RARITY_POWER: dict[str, float] = {
    "common": 0.5,
    "uncommon": 1.0,
    "rare": 2.0,
    "very_rare": 3.0,
    "legendary": 5.0,
}


async def compute_party_strength(
    db: AsyncSession,
    campaign_id: str,
    starting_level: int,
) -> PartyStrengthResult:
    """Compute the party's effective strength for difficulty scaling.

    Returns an effective level and XP budget multiplier that accounts for:
    - Mid-run level-ups (current level vs starting level)
    - Enhancement power_rating totals
    - Gacha item power estimates

    The strength_multiplier is applied to the XP budget, capped at 1.30.
    """
    # Get all living characters
    char_result = await db.execute(
        select(Character).where(Character.campaign_id == campaign_id)
    )
    characters = char_result.scalars().all()
    notes: list[str] = []

    if not characters:
        return PartyStrengthResult(
            effective_level=starting_level,
            enhancement_power=0.0,
            item_power=0.0,
            strength_multiplier=1.0,
        )

    # Effective level: average current level of all characters
    avg_level = sum(c.level for c in characters) / len(characters)
    effective_level = round(avg_level)
    level_delta = effective_level - starting_level

    # Enhancement power: sum of power_rating across all characters' enhancements
    total_enhancement_power = 0.0
    try:
        from app.data.enhancement_definitions import get_enhancement
        from app.models.character_enhancement import CharacterEnhancement

        enh_result = await db.execute(
            select(CharacterEnhancement).where(
                CharacterEnhancement.character_id.in_([c.id for c in characters])
            )
        )
        enhancements = enh_result.scalars().all()
        for enh in enhancements:
            enh_def = get_enhancement(enh.enhancement_id)
            if enh_def:
                total_enhancement_power += enh_def.power_rating
    except Exception:
        pass  # CharacterEnhancement model may not exist yet

    per_char_enh_power = total_enhancement_power / len(characters) if characters else 0.0

    # Gacha item power: estimate from character inventory
    total_item_power = 0.0
    try:
        from app.models.character_item import CharacterItem

        item_result = await db.execute(
            select(CharacterItem).where(
                CharacterItem.character_id.in_([c.id for c in characters])
            )
        )
        items = item_result.scalars().all()
        for item in items:
            rarity = getattr(item, "rarity", "common")
            total_item_power += RARITY_POWER.get(rarity, 1.0)
    except Exception:
        pass  # CharacterItem model may not exist yet

    per_char_item_power = total_item_power / len(characters) if characters else 0.0

    # Compute strength multiplier
    multiplier = 1.0

    # Level-ups: +5% per level above starting, capped at +20%
    if level_delta > 0:
        level_bonus = min(0.20, level_delta * 0.05)
        multiplier += level_bonus
        notes.append(f"Level-up bonus: +{level_bonus:.0%} ({level_delta} levels above start)")

    # Enhancement power: +3% per point of per-character power, capped at +30%
    if per_char_enh_power > 0:
        enh_bonus = min(0.30, per_char_enh_power * 0.03)
        multiplier += enh_bonus
        notes.append(
            f"Enhancement bonus: +{enh_bonus:.0%} "
            f"(avg {per_char_enh_power:.1f} power/char)"
        )

    # Item power: +2% per point of per-character item power, capped at +15%
    if per_char_item_power > 0:
        item_bonus = min(0.15, per_char_item_power * 0.02)
        multiplier += item_bonus
        notes.append(f"Item bonus: +{item_bonus:.0%} (avg {per_char_item_power:.1f} power/char)")

    # Final cap
    multiplier = min(1.30, multiplier)

    return PartyStrengthResult(
        effective_level=effective_level,
        enhancement_power=total_enhancement_power,
        item_power=total_item_power,
        strength_multiplier=round(multiplier, 3),
        notes=notes,
    )
