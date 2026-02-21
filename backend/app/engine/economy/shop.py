"""Between-floor shop system for meaningful gold spending.

The shop refreshes each floor with tier-appropriate items across
four categories, giving players significant choices:
- Individual upgrades (long-term power for one character)
- Consumables (immediate single-use tactical options)
- Party buffs (temporary bonuses for the whole group)
- Long-term investments (permanent but smaller party-wide benefits)
"""

import random
from dataclasses import dataclass
from enum import Enum


class ShopCategory(str, Enum):
    INDIVIDUAL = "individual"
    CONSUMABLE = "consumable"
    PARTY_BUFF = "party_buff"
    INVESTMENT = "investment"
    PRESTIGE = "prestige"


@dataclass
class ShopItem:
    id: str
    name: str
    description: str
    category: ShopCategory
    base_price: int
    tier: int  # 1-4, which tier of play this item is available in
    effect: dict


# Individual upgrades — lasting power for one character
INDIVIDUAL_ITEMS: list[ShopItem] = [
    ShopItem("shop_whetstone", "Whetstone of Sharpening", "+1 to weapon damage for the rest of the run", ShopCategory.INDIVIDUAL, 300, 1, {"damage_bonus": 1}),
    ShopItem("shop_minor_enchant", "Minor Enchantment", "+1 to spell save DC for the rest of the run", ShopCategory.INDIVIDUAL, 400, 1, {"spell_dc_bonus": 1}),
    ShopItem("shop_reinforced_armor", "Reinforced Armor Kit", "+1 AC for the rest of the run", ShopCategory.INDIVIDUAL, 500, 1, {"ac_bonus": 1}),
    ShopItem("shop_amulet_vitality", "Amulet of Vitality", "+10 max HP for the rest of the run", ShopCategory.INDIVIDUAL, 600, 2, {"max_hp_bonus": 10}),
    ShopItem("shop_greater_enchant", "Greater Enchantment", "+2 to weapon attack rolls for the rest of the run", ShopCategory.INDIVIDUAL, 1500, 2, {"attack_bonus": 2}),
    ShopItem("shop_mithral_weave", "Mithral Weave", "+2 AC for the rest of the run", ShopCategory.INDIVIDUAL, 2000, 3, {"ac_bonus": 2}),
    ShopItem("shop_soulbound_weapon", "Soulbound Weapon", "+2 to attack and damage for the rest of the run", ShopCategory.INDIVIDUAL, 3000, 3, {"attack_bonus": 2, "damage_bonus": 2}),
    ShopItem("shop_arcane_focus_sup", "Superior Arcane Focus", "+2 spell save DC and +1 spell attack for the rest of the run", ShopCategory.INDIVIDUAL, 3500, 4, {"spell_dc_bonus": 2, "spell_attack_bonus": 1}),
]

# Consumables — immediate single-use items
CONSUMABLE_ITEMS: list[ShopItem] = [
    ShopItem("shop_potion_healing", "Potion of Healing", "Heal 2d4+2 HP", ShopCategory.CONSUMABLE, 50, 1, {"heal": "2d4+2"}),
    ShopItem("shop_potion_greater", "Potion of Greater Healing", "Heal 4d4+4 HP", ShopCategory.CONSUMABLE, 150, 1, {"heal": "4d4+4"}),
    ShopItem("shop_scroll_fireball", "Scroll of Fireball", "Cast Fireball (8d6 fire, DEX save)", ShopCategory.CONSUMABLE, 200, 2, {"spell": "fireball", "damage": "8d6"}),
    ShopItem("shop_potion_superior", "Potion of Superior Healing", "Heal 8d4+8 HP", ShopCategory.CONSUMABLE, 400, 2, {"heal": "8d4+8"}),
    ShopItem("shop_potion_resistance", "Potion of Resistance", "Resistance to one damage type for 1 hour", ShopCategory.CONSUMABLE, 250, 2, {"resistance": True}),
    ShopItem("shop_scroll_revivify", "Scroll of Revivify", "Revive a character dead less than 1 minute", ShopCategory.CONSUMABLE, 500, 2, {"spell": "revivify"}),
    ShopItem("shop_potion_supreme", "Potion of Supreme Healing", "Heal 10d4+20 HP", ShopCategory.CONSUMABLE, 800, 3, {"heal": "10d4+20"}),
    ShopItem("shop_bead_force", "Bead of Force", "5d4 force damage in 10ft sphere, DEX save or trapped", ShopCategory.CONSUMABLE, 600, 3, {"damage": "5d4", "trap": True}),
]

# Party buffs — temporary bonuses lasting one floor
PARTY_BUFF_ITEMS: list[ShopItem] = [
    ShopItem("shop_blessing_ward", "Blessing of Warding", "Party gains +1 to all saves for one floor", ShopCategory.PARTY_BUFF, 200, 1, {"save_bonus": 1, "duration": "1_floor"}),
    ShopItem("shop_war_drum", "War Drum of Vigor", "Party gains +5 temporary HP at start of each arena", ShopCategory.PARTY_BUFF, 300, 1, {"temp_hp": 5, "duration": "1_floor"}),
    ShopItem("shop_banner_courage", "Banner of Courage", "Party is immune to frightened for one floor", ShopCategory.PARTY_BUFF, 400, 2, {"immunity": "frightened", "duration": "1_floor"}),
    ShopItem("shop_incense_clarity", "Incense of Clarity", "Party gains advantage on concentration saves for one floor", ShopCategory.PARTY_BUFF, 500, 2, {"concentration_advantage": True, "duration": "1_floor"}),
    ShopItem("shop_totem_resilience", "Totem of Resilience", "Party gains resistance to one damage type for one floor", ShopCategory.PARTY_BUFF, 800, 3, {"resistance_choice": True, "duration": "1_floor"}),
    ShopItem("shop_horn_valor", "Horn of Valor", "Party gains +2 to attack rolls for one floor", ShopCategory.PARTY_BUFF, 1500, 3, {"attack_bonus": 2, "duration": "1_floor"}),
]

# Long-term investments — permanent but smaller party-wide benefits
INVESTMENT_ITEMS: list[ShopItem] = [
    ShopItem("shop_cartographer", "Cartographer's Kit", "Reveal encounter types before entering arenas (permanent)", ShopCategory.INVESTMENT, 500, 1, {"reveal_encounters": True}),
    ShopItem("shop_healer_kit_adv", "Advanced Healer's Kit", "Momentum healing options restore +2 HP permanently", ShopCategory.INVESTMENT, 800, 1, {"momentum_heal_bonus": 2}),
    ShopItem("shop_lucky_coin", "Lucky Coin", "Party gains 1 reroll per floor (permanent)", ShopCategory.INVESTMENT, 1500, 2, {"reroll_per_floor": 1}),
    ShopItem("shop_merchant_ring", "Merchant's Ring", "10% discount at shop (permanent)", ShopCategory.INVESTMENT, 2000, 2, {"shop_discount": 0.10}),
    ShopItem("shop_phylactery_xp", "Phylactery of Growth", "+15% XP from all encounters (permanent)", ShopCategory.INVESTMENT, 3000, 2, {"xp_bonus": 0.15}),
    ShopItem("shop_wellspring", "Wellspring Stone", "One extra momentum recovery option per arena (permanent)", ShopCategory.INVESTMENT, 4000, 3, {"extra_momentum": 1}),
    ShopItem("shop_aegis_fate", "Aegis of Fate", "Party survives one TPK per run with 1 HP each (permanent)", ShopCategory.INVESTMENT, 8000, 3, {"tpk_save": True}),
]

# Prestige items — expensive gold sinks for endgame wealth
PRESTIGE_ITEMS: list[ShopItem] = [
    ShopItem(
        "shop_arbiters_blessing", "Arbiter's Blessing",
        "Reroll one failed death save per floor",
        ShopCategory.PRESTIGE, 15000, 3,
        {"reroll_death_save": 1, "duration": "per_floor"},
    ),
    ShopItem(
        "shop_essence_amplifier", "Essence Amplifier",
        "+50% essence from next run completion",
        ShopCategory.PRESTIGE, 25000, 3,
        {"shard_bonus": 0.5, "duration": "next_run"},
    ),
    ShopItem(
        "shop_golden_gacha_token", "Golden Gacha Token",
        "One free gacha pull",
        ShopCategory.PRESTIGE, 10000, 2,
        {"gacha_pull": 1},
    ),
    ShopItem(
        "shop_party_fortification", "Party Fortification",
        "+10 temp HP to all party members at start of each arena",
        ShopCategory.PRESTIGE, 20000, 3,
        {"temp_hp_all": 10, "duration": "per_arena"},
    ),
    ShopItem(
        "shop_cartographers_insight", "Cartographer's Insight",
        "Reveal all encounter details on the next floor",
        ShopCategory.PRESTIGE, 12000, 2,
        {"reveal_floor": True},
    ),
]

ALL_SHOP_ITEMS = (
    INDIVIDUAL_ITEMS + CONSUMABLE_ITEMS + PARTY_BUFF_ITEMS
    + INVESTMENT_ITEMS + PRESTIGE_ITEMS
)


@dataclass
class ShopInventory:
    """The shop inventory available between floors."""
    items: list[ShopItem]
    discount: float = 0.0  # 0.0-1.0, applied to all prices


def generate_shop_inventory(
    party_level: int,
    floor_number: int,
    owned_investment_ids: set[str] | None = None,
    discount: float = 0.0,
) -> ShopInventory:
    """Generate shop inventory for the current floor.

    Filters items by tier and removes already-owned investments.
    Selects a random subset to keep choices manageable.
    """
    from app.engine.scaling import get_tier
    tier = get_tier(party_level)
    owned = owned_investment_ids or set()

    # Filter to items available at this tier
    available = [item for item in ALL_SHOP_ITEMS if item.tier <= tier]

    # Remove already-owned investments
    available = [item for item in available if item.id not in owned]

    # Select a manageable subset: 2-3 per category
    selected: list[ShopItem] = []
    for category in ShopCategory:
        category_items = [i for i in available if i.category == category]
        count = min(3, len(category_items))
        if count > 0:
            selected.extend(random.sample(category_items, count))

    return ShopInventory(items=selected, discount=discount)


def compute_item_price(
    item: ShopItem,
    discount: float = 0.0,
    party_level: int = 1,
) -> int:
    """Compute the final price of an item after discount and tier scaling.

    Prices scale with the same LEVEL_MULTIPLIERS used for gold payouts,
    keeping the earn-to-spend ratio balanced across all tiers.
    """
    from app.engine.economy.gold import LEVEL_MULTIPLIERS
    multiplier = LEVEL_MULTIPLIERS.get(party_level, 1)
    return max(1, int(item.base_price * multiplier * (1.0 - discount)))
