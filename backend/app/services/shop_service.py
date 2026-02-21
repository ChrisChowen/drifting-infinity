"""Shop service per GDD 6.4.

30% chance of shop appearing between arenas.
Shop offers 4-6 items for purchase with gold.
Prices scale by tier to maintain balanced spend ratios.
"""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.enhancement_definitions import ENHANCEMENTS
from app.data.reward_pool import REWARD_POOL
from app.engine.economy.gold import LEVEL_MULTIPLIERS
from app.engine.economy.shop import PRESTIGE_ITEMS
from app.models.magic_item import MagicItem

SHOP_CHANCE = 0.30
SHOP_MIN_ITEMS = 4
SHOP_MAX_ITEMS = 6

# Gold prices for shop items (rewards are cheaper in shop)
SHOP_PRICES: dict[str, int] = {
    "common": 50,
    "uncommon": 120,
    "rare": 250,
}


def should_shop_appear(frequency: float | None = None) -> bool:
    """Roll to see if the shop appears."""
    chance = frequency if frequency is not None else SHOP_CHANCE
    return random.random() < chance


async def generate_shop_inventory(
    floor_number: int,
    db: AsyncSession,
    party_level: int = 1,
) -> list[dict]:
    """Generate shop inventory.

    Mix of consumable rewards, tier 1 enhancements, magic items, and
    prestige items (floor 6+). All prices scale by party level tier.
    """
    multiplier = LEVEL_MULTIPLIERS.get(party_level, 1)
    item_count = random.randint(SHOP_MIN_ITEMS, SHOP_MAX_ITEMS)
    inventory: list[dict] = []

    # Add consumable rewards
    available_rewards = [
        r for r in REWARD_POOL
        if r.floor_min <= floor_number and r.category in ("consumable", "gold")
    ]
    random.shuffle(available_rewards)

    for reward in available_rewards[:item_count - 1]:
        inventory.append({
            "id": reward.id,
            "name": reward.name,
            "type": "consumable",
            "rarity": reward.rarity,
            "description": reward.description,
            "effect": reward.effect,
            "price": SHOP_PRICES.get(reward.rarity, 100) * multiplier,
        })

    # Add 1-2 enhancements (tier 1 only in shop)
    tier1 = [e for e in ENHANCEMENTS if e.tier == 1]
    random.shuffle(tier1)
    for enh in tier1[:min(2, max(1, item_count - len(inventory)))]:
        inventory.append({
            "id": enh.id,
            "name": enh.name,
            "type": "enhancement",
            "rarity": f"tier_{enh.tier}",
            "description": enh.description,
            "effect": enh.effect,
            "price": enh.base_cost * multiplier,
        })

    # Add 2-3 magic items from DB
    try:
        result = await db.execute(
            select(MagicItem).where(MagicItem.floor_min <= floor_number)
        )
        magic_items = list(result.scalars().all())
    except Exception:
        magic_items = []

    if magic_items:
        mi_count = random.randint(2, min(3, len(magic_items)))
        sampled = random.sample(magic_items, mi_count)
        for item in sampled:
            inventory.append({
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "rarity": item.rarity,
                "description": item.description,
                "effect": {"type": "magic_item", "item_type": item.type},
                "price": item.gold_value * multiplier,
            })

    # Add 1-2 prestige items for floor 6+ (big gold sinks)
    from app.engine.scaling import get_tier
    tier = get_tier(party_level)
    if floor_number >= 6:
        eligible_prestige = [
            p for p in PRESTIGE_ITEMS if p.tier <= tier
        ]
        if eligible_prestige:
            p_count = random.randint(1, min(2, len(eligible_prestige)))
            for p in random.sample(eligible_prestige, p_count):
                inventory.append({
                    "id": p.id,
                    "name": p.name,
                    "type": "prestige",
                    "rarity": "legendary",
                    "description": p.description,
                    "effect": p.effect,
                    "price": p.base_price * multiplier,
                })
                item_count += 1  # prestige items are extra slots

    return inventory[:item_count]
