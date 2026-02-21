"""Gacha banner definitions per GDD 7.1."""

import random
from dataclasses import dataclass, field


@dataclass
class BannerItem:
    id: str
    name: str
    rarity: str
    item_type: str  # "variant", "weapon", "identity"
    description: str
    effect: dict
    source: str = "srd"


@dataclass
class Banner:
    key: str
    name: str
    description: str
    item_type: str
    pool: list[BannerItem] = field(default_factory=list)


# The Armory - Weapons & Armor
ARMORY_POOL: list[BannerItem] = [
    BannerItem("wep_weapon_plus_1", "Weapon +1", "uncommon", "weapon", "+1 to attack and damage rolls", {"attack": 1, "damage": 1}),
    BannerItem("wep_weapon_plus_2", "Weapon +2", "rare", "weapon", "+2 to attack and damage rolls", {"attack": 2, "damage": 2}),
    BannerItem("wep_weapon_plus_3", "Weapon +3", "very_rare", "weapon", "+3 to attack and damage rolls", {"attack": 3, "damage": 3}),
    BannerItem("wep_armor_plus_1", "Armor +1", "rare", "weapon", "+1 bonus to AC", {"ac": 1}),
    BannerItem("wep_armor_plus_2", "Armor +2", "very_rare", "weapon", "+2 bonus to AC", {"ac": 2}),
    BannerItem("wep_flame_tongue", "Flame Tongue", "rare", "weapon", "While activated, +2d6 fire damage on hit", {"fire_damage": "2d6"}),
    BannerItem("wep_frost_brand", "Frost Brand", "very_rare", "weapon", "+1d6 cold damage, fire resistance", {"cold_damage": "1d6", "fire_resistance": True}),
    BannerItem("wep_vorpal_sword", "Vorpal Sword", "legendary", "weapon", "On a nat 20 vs creatures with heads, decapitate", {"vorpal": True}),
    BannerItem("wep_dancing_sword", "Dancing Sword", "very_rare", "weapon", "Toss into the air; it fights on its own within 30ft", {"animated": True, "attack": 0, "damage": 0}),
    BannerItem("wep_defender", "Defender", "legendary", "weapon", "Transfer up to +3 between attack/damage and AC each turn", {"transfer_bonus": 3}),
    BannerItem("wep_dwarven_thrower", "Dwarven Thrower", "very_rare", "weapon", "+3 to attack/damage, returns when thrown, +2d8 vs giants", {"attack": 3, "damage": 3, "thrown_return": True, "giant_bonus": "2d8"}),
    BannerItem("wep_holy_avenger", "Holy Avenger", "legendary", "weapon", "+3 to attack/damage; 10ft aura of +2 saves vs spells for allies", {"attack": 3, "damage": 3, "aura_save_bonus": 2}),
    BannerItem("wep_oathbow", "Oathbow", "very_rare", "weapon", "Swear enemy; +3d6 damage against sworn enemy, advantage on attacks", {"sworn_enemy_damage": "3d6", "sworn_advantage": True}),
    BannerItem("wep_sun_blade", "Sun Blade", "rare", "weapon", "+2 to attack/damage, 1d8 radiant, finesse, emits sunlight", {"attack": 2, "damage": 2, "radiant": True, "sunlight": True}),
    BannerItem("wep_dragon_slayer", "Dragon Slayer", "rare", "weapon", "+1 to attack/damage, +3d6 vs dragons", {"attack": 1, "damage": 1, "dragon_bonus": "3d6"}),
    BannerItem("wep_giant_slayer", "Giant Slayer", "rare", "weapon", "+1 to attack/damage, +2d6 vs giants, knock prone", {"attack": 1, "damage": 1, "giant_bonus": "2d6", "giant_prone": True}),
    BannerItem("wep_javelin_lightning", "Javelin of Lightning", "uncommon", "weapon", "Throw to become lightning bolt (4d6 lightning, DEX save half)", {"lightning_bolt": "4d6"}),
    BannerItem("wep_mace_disruption", "Mace of Disruption", "rare", "weapon", "+2d6 radiant vs fiends/undead, may destroy if under 25 HP", {"radiant_vs_undead": "2d6", "destroy_threshold": 25}),
    BannerItem("wep_staff_striking", "Staff of Striking", "very_rare", "weapon", "+3 attack, expend charges for +1d6 per charge", {"attack": 3, "charges": 10, "charge_damage": "1d6"}),
    BannerItem("wep_shield_plus_1", "Shield +1", "uncommon", "weapon", "+1 bonus to AC (on top of normal shield)", {"ac": 1}),
]

# The Reliquary - Wondrous Items
RELIQUARY_POOL: list[BannerItem] = [
    BannerItem("var_cloak_protection", "Cloak of Protection", "uncommon", "variant", "+1 to AC and saving throws", {"ac": 1, "saving_throws": 1}),
    BannerItem("var_boots_elvenkind", "Boots of Elvenkind", "uncommon", "variant", "Advantage on Stealth checks", {"stealth_advantage": True}),
    BannerItem("var_gauntlets_ogre", "Gauntlets of Ogre Power", "uncommon", "variant", "STR becomes 19", {"str_set": 19}),
    BannerItem("var_belt_giant_str", "Belt of Hill Giant Strength", "rare", "variant", "STR becomes 21", {"str_set": 21}),
    BannerItem("var_cloak_displacement", "Cloak of Displacement", "rare", "variant", "Disadvantage on attack rolls against you", {"displacement": True}),
    BannerItem("var_ring_protection", "Ring of Protection", "rare", "variant", "+1 to AC and saving throws", {"ac": 1, "saving_throws": 1}),
    BannerItem("var_amulet_health", "Amulet of Health", "rare", "variant", "CON becomes 19", {"con_set": 19}),
    BannerItem("var_wings_flying", "Wings of Flying", "very_rare", "variant", "60 ft flying speed", {"fly_speed": 60}),
    BannerItem("var_staff_power", "Staff of Power", "very_rare", "variant", "+2 to attack, damage, AC, saving throws, and spell attacks", {"attack": 2, "damage": 2, "ac": 2, "saving_throws": 2, "spell_attack": 2}),
    BannerItem("var_robe_archmagi", "Robe of the Archmagi", "legendary", "variant", "+2 AC, advantage on saves vs magic, spell DC +2", {"ac": 2, "magic_save_advantage": True, "spell_dc": 2}),
    BannerItem("var_bag_holding", "Bag of Holding", "uncommon", "variant", "Holds up to 500 lbs; interior is extradimensional", {"storage": 500}),
    BannerItem("var_boots_speed", "Boots of Speed", "rare", "variant", "Double walking speed for 10 min/day", {"speed_double": True, "duration_min": 10}),
    BannerItem("var_bracers_defense", "Bracers of Defense", "rare", "variant", "+2 AC when wearing no armor and no shield", {"ac": 2, "requires_no_armor": True}),
    BannerItem("var_cape_mountebank", "Cape of the Mountebank", "rare", "variant", "Cast Dimension Door once per day", {"spell": "dimension_door", "uses_per_day": 1}),
    BannerItem("var_circlet_blasting", "Circlet of Blasting", "uncommon", "variant", "Cast Scorching Ray once per day", {"spell": "scorching_ray", "uses_per_day": 1}),
    BannerItem("var_cloak_bat", "Cloak of the Bat", "rare", "variant", "Advantage on Stealth, fly in dim/dark, polymorph into bat", {"stealth_advantage": True, "fly_in_dark": True}),
    BannerItem("var_eyes_minute_seeing", "Eyes of Minute Seeing", "uncommon", "variant", "Advantage on Investigation checks within 1 ft", {"investigation_advantage": True}),
    BannerItem("var_gem_seeing", "Gem of Seeing", "rare", "variant", "Truesight 120 ft for 10 min, 3 charges/day", {"truesight": 120, "charges": 3}),
    BannerItem("var_gloves_missile_snaring", "Gloves of Missile Snaring", "uncommon", "variant", "Reduce ranged weapon damage by 1d10+DEX", {"missile_reduction": "1d10+DEX"}),
    BannerItem("var_hat_disguise", "Hat of Disguise", "uncommon", "variant", "Cast Disguise Self at will", {"spell": "disguise_self", "at_will": True}),
    BannerItem("var_helm_telepathy", "Helm of Telepathy", "uncommon", "variant", "Telepathy 30 ft, cast Detect Thoughts once/day", {"telepathy_range": 30, "detect_thoughts": True}),
    BannerItem("var_ioun_fortitude", "Ioun Stone of Fortitude", "very_rare", "variant", "CON becomes 19", {"con_set": 19}),
    BannerItem("var_ioun_insight", "Ioun Stone of Insight", "very_rare", "variant", "WIS becomes 19", {"wis_set": 19}),
    BannerItem("var_pearl_power", "Pearl of Power", "uncommon", "variant", "Recover one 3rd-level or lower spell slot per day", {"spell_slot_recovery": 3}),
    BannerItem("var_ring_spell_storing", "Ring of Spell Storing", "rare", "variant", "Store up to 5 levels of spells for later casting", {"spell_levels_stored": 5}),
]

# Echoes of Power - Boons
ECHOES_POOL: list[BannerItem] = [
    BannerItem("id_boon_speed", "Boon of Speed", "rare", "identity", "Speed +30 ft, opportunity attacks have disadvantage against you", {"speed": 30, "opp_attack_disadvantage": True}),
    BannerItem("id_boon_skill", "Boon of Skill", "rare", "identity", "Proficiency in all skills, proficiency bonus to initiative", {"all_skill_proficiency": True, "initiative_proficiency": True}),
    BannerItem("id_boon_resilience", "Boon of Resilience", "rare", "identity", "Resistance to two damage types of your choice", {"damage_resistance_choices": 2}),
    BannerItem("id_boon_combat", "Boon of Combat Prowess", "very_rare", "identity", "Turn a miss into a hit (proficiency bonus times/long rest)", {"miss_to_hit": True}),
    BannerItem("id_boon_irresistible", "Boon of Irresistible Offense", "very_rare", "identity", "Attacks ignore resistance, treat immunity as resistance", {"ignore_resistance": True, "immunity_as_resistance": True}),
    BannerItem("id_boon_fate", "Boon of Fate", "very_rare", "identity", "Add/subtract 2d4 to failed d20 rolls within 60 ft", {"fate_dice": "2d4", "fate_range": 60}),
    BannerItem("id_boon_fortitude", "Boon of Fortitude", "legendary", "identity", "+40 maximum HP", {"max_hp": 40}),
    BannerItem("id_boon_spell_recall", "Boon of Spell Recall", "legendary", "identity", "Cast a 5th-level or lower spell without slot (1/short rest)", {"spell_recall_level": 5, "spell_recall_recharge": "short_rest"}),
    BannerItem("id_boon_night_spirit", "Boon of the Night Spirit", "rare", "identity", "Darkvision 300 ft, invisible in darkness while motionless", {"darkvision": 300, "darkness_invisible": True}),
    BannerItem("id_boon_truesight", "Boon of Truesight", "very_rare", "identity", "Truesight 60 ft permanently", {"truesight": 60}),
    BannerItem("id_boon_dimensional", "Boon of Dimensional Travel", "very_rare", "identity", "Cast Misty Step at will", {"spell": "misty_step", "at_will": True}),
    BannerItem("id_boon_recovery", "Boon of Recovery", "rare", "identity", "Regain all HP on short rest once per day", {"full_heal_short_rest": True, "uses_per_day": 1}),
    BannerItem("id_boon_high_magic", "Boon of High Magic", "legendary", "identity", "Gain one additional 9th-level spell slot", {"bonus_spell_slot": 9}),
    BannerItem("id_boon_luck", "Boon of Luck", "rare", "identity", "Reroll one d20 per short rest, take either result", {"reroll_per_rest": 1}),
    BannerItem("id_boon_energy_resist", "Boon of Energy Resistance", "rare", "identity", "Resistance to acid, cold, fire, lightning, and thunder damage", {"resistance": ["acid", "cold", "fire", "lightning", "thunder"]}),
]


BANNERS: dict[str, Banner] = {
    "the_armory": Banner(
        key="the_armory",
        name="The Armory",
        description="The Armillary yields weapons and armor from fallen challengers.",
        item_type="weapon",
        pool=ARMORY_POOL,
    ),
    "the_reliquary": Banner(
        key="the_reliquary",
        name="The Reliquary",
        description="Wondrous items crystallized from the arena's essence.",
        item_type="variant",
        pool=RELIQUARY_POOL,
    ),
    "echoes_of_power": Banner(
        key="echoes_of_power",
        name="Echoes of Power",
        description="Boons granted by the Armillary to those who prove worthy.",
        item_type="identity",
        pool=ECHOES_POOL,
    ),
}


def get_banner(banner_key: str) -> Banner | None:
    return BANNERS.get(banner_key)


def select_item_from_banner(
    banner: Banner,
    rarity: str,
    owned_item_ids: set[str] | None = None,
    party_level: int = 1,
) -> BannerItem | None:
    """Select a random item of the given rarity from the banner pool.

    Excludes already-owned items. If all items at the target rarity are
    owned, upgrades to the next rarity tier instead of giving a duplicate.

    Tier gating: legendary items require party_level >= 10.
    """
    owned = owned_item_ids or set()

    # Tier gating
    available_pool = list(banner.pool)
    if party_level < 10:
        available_pool = [i for i in available_pool if i.rarity != "legendary"]
    if party_level < 5:
        available_pool = [i for i in available_pool if i.rarity != "very_rare"]

    rarity_order = ["common", "uncommon", "rare", "very_rare", "legendary"]

    # Try target rarity first, excluding owned items
    matching = [item for item in available_pool if item.rarity == rarity and item.id not in owned]

    if not matching:
        # All items at this rarity are owned — try upgrading rarity
        idx = rarity_order.index(rarity) if rarity in rarity_order else 0
        for search_rarity in rarity_order[idx + 1:]:
            matching = [item for item in available_pool if item.rarity == search_rarity and item.id not in owned]
            if matching:
                break

    if not matching:
        # Try downgrading rarity
        idx = rarity_order.index(rarity) if rarity in rarity_order else 0
        for search_rarity in reversed(rarity_order[:idx]):
            matching = [item for item in available_pool if item.rarity == search_rarity and item.id not in owned]
            if matching:
                break

    if not matching:
        # Last resort: allow duplicates from the full pool at target rarity
        matching = [item for item in available_pool if item.rarity == rarity]
        if not matching:
            matching = available_pool

    return random.choice(matching) if matching else None
