"""Reward definitions per GDD 6.2.

Tiered consumables based on real D&D 5e SRD items.  Magic-item equipment
now comes exclusively from the SRD database; the old ``equipment``
category has been removed.

Categories
----------
consumable  Real D&D potions and scrolls, unlocked by floor tier.
gold        Flat gold-per-player payouts (3 tiers).
ability     One-off mechanical benefits (extra hit die, inspiration, etc.).
feat        Placeholders that tell the frontend/DM to open the feat catalog.
"""

import random
from dataclasses import dataclass


@dataclass
class RewardDef:
    id: str
    name: str
    rarity: str  # "common", "uncommon", "rare"
    category: str  # "consumable", "gold", "ability", "feat"
    effect: dict
    description: str
    floor_min: int  # Minimum floor to appear


REWARD_POOL: list[RewardDef] = [
    # ── Consumables T1 (floor 1+) ────────────────────────────────────
    RewardDef(
        "rew_potion_healing", "Potion of Healing", "common", "consumable",
        {"heal": "2d4+2"},
        "Regain 2d4+2 hit points when you drink this potion.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_shield", "Scroll of Shield", "common", "consumable",
        {"spell": "shield"},
        "Cast Shield as a reaction (+5 AC until the start of your next turn).",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_climbing", "Potion of Climbing", "common", "consumable",
        {"climbing_speed": "equal_to_walking", "advantage": "athletics_climbing"},
        "Gain a climbing speed equal to your walking speed and advantage on "
        "Athletics checks made to climb for 1 hour.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_detect_magic", "Scroll of Detect Magic", "common", "consumable",
        {"spell": "detect_magic"},
        "Cast Detect Magic (concentration, up to 10 minutes).",
        floor_min=1,
    ),
    RewardDef(
        "rew_antitoxin", "Antitoxin", "common", "consumable",
        {"advantage": "poison_saves", "duration": "1 hour"},
        "Advantage on saving throws against poison for 1 hour.",
        floor_min=1,
    ),
    RewardDef(
        "rew_oil_slipperiness", "Oil of Slipperiness", "common", "consumable",
        {"spell_effect": "freedom_of_movement", "duration": "8 hours"},
        "Coat yourself or a surface. Grants the effect of Freedom of Movement "
        "for 8 hours, or creates a 10-ft square of difficult terrain.",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_animal_friendship", "Potion of Animal Friendship", "common",
        "consumable",
        {"spell": "animal_friendship", "dc": 13, "duration": "24 hours"},
        "Cast Animal Friendship (DC 13) when you drink this potion. "
        "The effect lasts 24 hours.",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_growth", "Potion of Growth", "common", "consumable",
        {"spell_effect": "enlarge", "duration": "1d4 hours"},
        "You grow as if under the Enlarge effect of the Enlarge/Reduce spell "
        "for 1d4 hours (no concentration required).",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_diminution", "Potion of Diminution", "common", "consumable",
        {"spell_effect": "reduce", "duration": "1d4 hours"},
        "You shrink as if under the Reduce effect of the Enlarge/Reduce spell "
        "for 1d4 hours (no concentration required).",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_water_breathing", "Potion of Water Breathing", "common",
        "consumable",
        {"grant": "water_breathing", "duration": "1 hour"},
        "You can breathe underwater for 1 hour after drinking this potion.",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_resistance_cold", "Potion of Resistance (Cold)", "common",
        "consumable",
        {"resistance": "cold", "duration": "1 hour"},
        "Resistance to cold damage for 1 hour.",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_resistance_lightning", "Potion of Resistance (Lightning)",
        "common", "consumable",
        {"resistance": "lightning", "duration": "1 hour"},
        "Resistance to lightning damage for 1 hour.",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_resistance_acid", "Potion of Resistance (Acid)", "common",
        "consumable",
        {"resistance": "acid", "duration": "1 hour"},
        "Resistance to acid damage for 1 hour.",
        floor_min=1,
    ),
    RewardDef(
        "rew_potion_resistance_poison", "Potion of Resistance (Poison)", "common",
        "consumable",
        {"resistance": "poison", "duration": "1 hour"},
        "Resistance to poison damage for 1 hour.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_cure_wounds", "Scroll of Cure Wounds", "common", "consumable",
        {"spell": "cure_wounds", "heal": "1d8+3"},
        "Cast Cure Wounds, restoring 1d8+3 hit points to a creature you touch.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_bless", "Scroll of Bless", "common", "consumable",
        {"spell": "bless", "targets": 3, "duration": "1 minute"},
        "Cast Bless on up to three creatures (concentration, up to 1 minute). "
        "Each target adds 1d4 to attack rolls and saving throws.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_faerie_fire", "Scroll of Faerie Fire", "common", "consumable",
        {"spell": "faerie_fire", "dc": 13, "duration": "1 minute"},
        "Cast Faerie Fire (DC 13). Affected creatures shed dim light and "
        "attacks against them have advantage for 1 minute.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_thunderwave", "Scroll of Thunderwave", "common", "consumable",
        {"spell": "thunderwave", "damage": "2d8", "damage_type": "thunder", "dc": 13},
        "Cast Thunderwave (2d8 thunder damage, DC 13 Constitution save). "
        "Creatures that fail are pushed 10 feet away.",
        floor_min=1,
    ),
    RewardDef(
        "rew_scroll_mage_armor", "Scroll of Mage Armor", "common", "consumable",
        {"spell": "mage_armor", "ac_base": 13, "duration": "8 hours"},
        "Cast Mage Armor on a willing creature. Its base AC becomes "
        "13 + Dexterity modifier for 8 hours.",
        floor_min=1,
    ),
    RewardDef(
        "rew_holy_water", "Holy Water", "common", "consumable",
        {"damage": "2d6", "damage_type": "radiant", "range": "20 ft",
         "targets": "fiend_or_undead"},
        "Splash as an improvised ranged weapon (20 ft). A fiend or undead "
        "hit takes 2d6 radiant damage.",
        floor_min=1,
    ),
    RewardDef(
        "rew_alchemists_fire", "Alchemist's Fire", "common", "consumable",
        {"damage": "1d4", "damage_type": "fire", "range": "20 ft",
         "ongoing": "1d4 fire per turn", "escape_dc": 10},
        "Hurl as an improvised ranged weapon (20 ft). On a hit, the target "
        "takes 1d4 fire damage at the start of each of its turns until "
        "it uses an action to douse the flames (DC 10 Dexterity).",
        floor_min=1,
    ),
    RewardDef(
        "rew_acid_flask", "Acid Flask", "common", "consumable",
        {"damage": "2d6", "damage_type": "acid", "range": "20 ft"},
        "Hurl as an improvised ranged weapon (20 ft). On a hit, the target "
        "takes 2d6 acid damage.",
        floor_min=1,
    ),

    # ── Consumables T2 (floor 2+) ────────────────────────────────────
    RewardDef(
        "rew_potion_greater_healing", "Potion of Greater Healing", "uncommon",
        "consumable",
        {"heal": "4d4+4"},
        "Regain 4d4+4 hit points when you drink this potion.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_heroism", "Potion of Heroism", "uncommon", "consumable",
        {"temp_hp": 10, "spell_effect": "bless", "duration": "1 hour"},
        "Gain 10 temporary hit points and the effect of Bless for 1 hour.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_fire_resistance", "Potion of Fire Resistance", "uncommon",
        "consumable",
        {"resistance": "fire", "duration": "1 hour"},
        "Resistance to fire damage for 1 hour.",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_fireball", "Scroll of Fireball", "uncommon", "consumable",
        {"spell": "fireball", "damage": "8d6", "damage_type": "fire", "dc": 15},
        "Cast Fireball (8d6 fire damage, DC 15 Dexterity save).",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_revivify_t2", "Scroll of Revivify", "uncommon", "consumable",
        {"spell": "revivify"},
        "Cast Revivify on a creature that has died within the last minute, "
        "restoring it to 1 hit point.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_cold_resistance", "Potion of Cold Resistance", "uncommon",
        "consumable",
        {"resistance": "cold", "duration": "1 hour"},
        "Resistance to cold damage for 1 hour.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_poison_resistance", "Potion of Poison Resistance", "uncommon",
        "consumable",
        {"resistance": "poison", "duration": "1 hour"},
        "Resistance to poison damage for 1 hour.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_speed", "Potion of Speed", "uncommon", "consumable",
        {"spell_effect": "haste", "duration": "1 minute"},
        "You gain the effect of the Haste spell for 1 minute "
        "(no concentration required).",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_hill_giant_strength", "Potion of Hill Giant Strength",
        "uncommon", "consumable",
        {"set_ability": {"ability": "STR", "value": 21}, "duration": "1 hour"},
        "Your Strength score becomes 21 for 1 hour.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_gaseous_form", "Potion of Gaseous Form", "uncommon",
        "consumable",
        {"spell_effect": "gaseous_form", "duration": "1 hour"},
        "You gain the effect of the Gaseous Form spell for 1 hour "
        "(no concentration required). You can end the effect early as a bonus action.",
        floor_min=2,
    ),
    RewardDef(
        "rew_potion_invisibility_short", "Potion of Invisibility (Short)",
        "uncommon", "consumable",
        {"condition": "invisible", "duration": "10 minutes"},
        "You become invisible for 10 minutes. The effect ends early "
        "if you attack or cast a spell.",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_counterspell", "Scroll of Counterspell", "uncommon",
        "consumable",
        {"spell": "counterspell", "level": 3},
        "Cast Counterspell as a reaction to interrupt a creature casting "
        "a spell of 3rd level or lower. Higher-level spells require an "
        "ability check (DC 10 + spell level).",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_dispel_magic", "Scroll of Dispel Magic", "uncommon",
        "consumable",
        {"spell": "dispel_magic", "level": 3},
        "Cast Dispel Magic, automatically ending spells of 3rd level or lower "
        "on one target. Higher-level spells require an ability check "
        "(DC 10 + spell level).",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_fly", "Scroll of Fly", "uncommon", "consumable",
        {"spell": "fly", "flying_speed": 60, "duration": "10 minutes"},
        "Cast Fly on a willing creature (concentration, up to 10 minutes). "
        "The target gains a flying speed of 60 feet.",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_spirit_guardians", "Scroll of Spirit Guardians", "uncommon",
        "consumable",
        {"spell": "spirit_guardians", "damage": "3d8",
         "damage_type": "radiant_or_necrotic", "dc": 15, "duration": "10 minutes"},
        "Cast Spirit Guardians (concentration, up to 10 minutes). Hostile "
        "creatures within 15 feet take 3d8 radiant or necrotic damage "
        "(DC 15 Wisdom save for half).",
        floor_min=2,
    ),
    RewardDef(
        "rew_scroll_lesser_restoration", "Scroll of Lesser Restoration", "uncommon",
        "consumable",
        {"spell": "lesser_restoration"},
        "Cast Lesser Restoration, ending one disease or one condition "
        "(blinded, deafened, paralyzed, or poisoned) on a creature you touch.",
        floor_min=2,
    ),
    RewardDef(
        "rew_dust_of_disappearance", "Dust of Disappearance", "uncommon",
        "consumable",
        {"condition": "invisible", "targets": "all_in_10ft", "duration": "2d4 minutes"},
        "Toss into the air. Each creature within 10 feet becomes invisible "
        "for 2d4 minutes. The effect ends early for a creature that attacks "
        "or casts a spell.",
        floor_min=2,
    ),
    RewardDef(
        "rew_bead_of_force", "Bead of Force", "uncommon", "consumable",
        {"damage": "5d4", "damage_type": "force", "dc": 15, "range": "60 ft",
         "sphere_duration": "1 minute"},
        "Hurl up to 60 feet. Each creature within 10 feet of the impact "
        "takes 5d4 force damage (DC 15 Dexterity save). On a failure, "
        "a creature is trapped in a sphere of force for 1 minute.",
        floor_min=2,
    ),
    RewardDef(
        "rew_elemental_gem", "Elemental Gem", "uncommon", "consumable",
        {"summon": "elemental", "duration": "1 hour",
         "types": ["air", "earth", "fire", "water"]},
        "Break this gem to summon an elemental as if you had cast "
        "Conjure Elemental. The type of elemental depends on the gem color.",
        floor_min=2,
    ),
    RewardDef(
        "rew_oil_of_sharpness", "Oil of Sharpness", "uncommon", "consumable",
        {"weapon_bonus": "+3", "duration": "1 hour"},
        "Coat one slashing or piercing weapon or up to 5 pieces of ammunition. "
        "The coated item gains a +3 bonus to attack and damage rolls for 1 hour.",
        floor_min=2,
    ),

    # ── Consumables T3 (floor 3+) ────────────────────────────────────
    RewardDef(
        "rew_potion_superior_healing", "Potion of Superior Healing", "rare",
        "consumable",
        {"heal": "8d4+8"},
        "Regain 8d4+8 hit points when you drink this potion.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_giant_strength", "Potion of Giant Strength", "rare",
        "consumable",
        {"set_ability": {"ability": "STR", "value": 21}, "duration": "1 hour"},
        "Your Strength score becomes 21 for 1 hour.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_invisibility", "Potion of Invisibility", "rare", "consumable",
        {"condition": "invisible", "duration": "1 hour"},
        "You become invisible for 1 hour. The effect ends early if you attack "
        "or cast a spell.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_flying", "Potion of Flying", "rare", "consumable",
        {"flying_speed": 60, "duration": "1 hour"},
        "Gain a flying speed of 60 feet for 1 hour.",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_haste", "Scroll of Haste", "rare", "consumable",
        {"spell": "haste"},
        "Cast Haste on one willing creature (concentration, up to 1 minute).",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_revivify_t3", "Scroll of Revivify", "rare", "consumable",
        {"spell": "revivify"},
        "Cast Revivify on a creature that has died within the last minute, "
        "restoring it to 1 hit point.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_supreme_healing", "Potion of Supreme Healing", "rare",
        "consumable",
        {"heal": "10d4+20"},
        "Regain 10d4+20 hit points when you drink this potion.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_storm_giant_strength", "Potion of Storm Giant Strength",
        "rare", "consumable",
        {"set_ability": {"ability": "STR", "value": 29}, "duration": "1 hour"},
        "Your Strength score becomes 29 for 1 hour.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_invulnerability", "Potion of Invulnerability", "rare",
        "consumable",
        {"resistance": "all_damage", "duration": "1 minute"},
        "You have resistance to all damage for 1 minute.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_vitality", "Potion of Vitality", "rare", "consumable",
        {"remove": ["exhaustion", "poison", "disease"],
         "hit_dice_maximize": "24 hours"},
        "Removes all exhaustion, cures all poison and disease, and for the "
        "next 24 hours you regain the maximum number of hit points from any "
        "Hit Die you spend.",
        floor_min=3,
    ),
    RewardDef(
        "rew_potion_longevity", "Potion of Longevity", "rare", "consumable",
        {"age_reduction": "1d6+6 years"},
        "Your physical age is reduced by 1d6+6 years, to a minimum of 13.",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_banishment", "Scroll of Banishment", "rare", "consumable",
        {"spell": "banishment", "dc": 15, "duration": "1 minute"},
        "Cast Banishment (DC 15 Charisma save). On a failure, the target is "
        "banished to a harmless demiplane for up to 1 minute (concentration).",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_wall_of_force", "Scroll of Wall of Force", "rare",
        "consumable",
        {"spell": "wall_of_force", "duration": "10 minutes"},
        "Cast Wall of Force (concentration, up to 10 minutes). Creates an "
        "invisible wall of force that nothing can physically pass through.",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_raise_dead", "Scroll of Raise Dead", "rare", "consumable",
        {"spell": "raise_dead"},
        "Cast Raise Dead on a creature that has been dead for no more than "
        "10 days, restoring it to 1 hit point.",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_greater_restoration", "Scroll of Greater Restoration", "rare",
        "consumable",
        {"spell": "greater_restoration"},
        "Cast Greater Restoration, ending one of the following: a reduction to "
        "an ability score, a curse, petrification, one exhaustion level, or "
        "a charm/frightened effect.",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_cone_of_cold", "Scroll of Cone of Cold", "rare", "consumable",
        {"spell": "cone_of_cold", "damage": "8d8", "damage_type": "cold", "dc": 17},
        "Cast Cone of Cold (8d8 cold damage in a 60-foot cone, "
        "DC 17 Constitution save for half).",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_chain_lightning", "Scroll of Chain Lightning", "rare",
        "consumable",
        {"spell": "chain_lightning", "damage": "10d8", "damage_type": "lightning",
         "dc": 17, "targets": 4},
        "Cast Chain Lightning (10d8 lightning damage to one target, arcing to "
        "up to 3 additional targets; DC 17 Dexterity save for half).",
        floor_min=3,
    ),
    RewardDef(
        "rew_necklace_of_fireballs", "Necklace of Fireballs (3-Bead)", "rare",
        "consumable",
        {"charges": 3, "spell": "fireball", "damage": "8d6",
         "damage_type": "fire", "dc": 15},
        "This necklace has 3 beads. As an action, detach a bead and hurl it "
        "up to 60 feet; it detonates as a Fireball (8d6 fire damage, "
        "DC 15 Dexterity save).",
        floor_min=3,
    ),
    RewardDef(
        "rew_feather_token_anchor", "Feather Token (Anchor)", "rare", "consumable",
        {"effect": "anchor", "target": "vessel"},
        "Touch this token to a boat or ship. The vessel cannot be moved by "
        "any means for 24 hours, after which the token is expended.",
        floor_min=3,
    ),
    RewardDef(
        "rew_chime_of_opening", "Chime of Opening", "rare", "consumable",
        {"charges": 10, "effect": "unlock"},
        "Strike this chime and point it at a locked object within 120 feet. "
        "One lock or latch on the object opens. Has 10 charges; the chime "
        "shatters when the last charge is used.",
        floor_min=3,
    ),
    RewardDef(
        "rew_scroll_teleportation_circle", "Scroll of Teleportation Circle",
        "rare", "consumable",
        {"spell": "teleportation_circle"},
        "Cast Teleportation Circle, creating a portal linked to a permanent "
        "teleportation circle whose sigil sequence you know.",
        floor_min=3,
    ),

    # ── Gold ──────────────────────────────────────────────────────────
    RewardDef(
        "rew_gold_small", "Coin Purse", "common", "gold",
        {"gold": 50},
        "50 gold per player.",
        floor_min=1,
    ),
    RewardDef(
        "rew_gold_medium", "Treasure Chest", "uncommon", "gold",
        {"gold": 150},
        "150 gold per player.",
        floor_min=2,
    ),
    RewardDef(
        "rew_gold_large", "Dragon's Hoard", "rare", "gold",
        {"gold": 300},
        "300 gold per player.",
        floor_min=3,
    ),

    # ── Ability ───────────────────────────────────────────────────────
    RewardDef(
        "rew_extra_hit_die", "Extra Hit Die", "common", "ability",
        {"hit_dice": 1},
        "Gain 1 extra Hit Die for recovery.",
        floor_min=1,
    ),
    RewardDef(
        "rew_inspiration", "Heroic Inspiration", "common", "ability",
        {"inspiration": True},
        "One character gains Inspiration.",
        floor_min=1,
    ),
    RewardDef(
        "rew_spell_slot", "Arcane Recovery", "uncommon", "ability",
        {"spell_slot": 1},
        "Recover one expended spell slot (up to 3rd level).",
        floor_min=1,
    ),
    RewardDef(
        "rew_temp_hp", "Fortifying Tonic", "common", "ability",
        {"temp_hp": 10},
        "One character gains 10 temporary HP.",
        floor_min=1,
    ),

    # ── Feats (frontend/DM selects from feat catalog) ─────────────────
    RewardDef(
        "rew_feat_origin", "Origin Feat", "common", "feat",
        {"feat_type": "origin"},
        "The Armillary grants insight. Choose an Origin feat.",
        floor_min=1,
    ),
    RewardDef(
        "rew_feat_general", "General Feat", "uncommon", "feat",
        {"feat_type": "general"},
        "The arena's challenges teach new techniques. Choose a General feat.",
        floor_min=2,
    ),
    RewardDef(
        "rew_feat_fighting_style", "Fighting Style", "uncommon", "feat",
        {"feat_type": "fighting_style"},
        "Combat experience crystallizes. Choose a Fighting Style.",
        floor_min=2,
    ),
    RewardDef(
        "rew_feat_epic_boon", "Epic Boon", "rare", "feat",
        {"feat_type": "epic_boon", "min_party_level": 19},
        "The Armillary bestows ultimate power. Choose an Epic Boon.",
        floor_min=4,
    ),
]


def get_rewards_for_floor(floor_number: int) -> list[RewardDef]:
    """Get all valid rewards for a given floor number."""
    return [r for r in REWARD_POOL if r.floor_min <= floor_number]


def generate_reward_choices(
    floor_number: int,
    count: int = 3,
    *,
    categories: list[str] | None = None,
    exclude_ids: set[str] | None = None,
) -> list[RewardDef]:
    """Generate *count* random reward choices (Slay-the-Spire style).

    Parameters
    ----------
    floor_number:
        Current arena floor (determines which items are unlocked).
    count:
        How many choices to return.
    categories:
        If provided, only sample from these categories.
    exclude_ids:
        Reward IDs to exclude (avoids duplicates when called multiple
        times for the same reward screen).

    Rarity weights: common 50 %, uncommon 35 %, rare 15 %.
    Deeper floors increase rare/uncommon chances slightly.
    """
    available = get_rewards_for_floor(floor_number)

    if categories:
        available = [r for r in available if r.category in categories]
    if exclude_ids:
        available = [r for r in available if r.id not in exclude_ids]
    if not available:
        # Ultimate fallback: first three items in the pool
        available = REWARD_POOL[:3]

    # Weight by rarity
    weighted: list[tuple[RewardDef, int]] = []
    for r in available:
        if r.rarity == "common":
            weight = 50
        elif r.rarity == "uncommon":
            weight = 35 + (floor_number * 2)
        else:
            weight = 15 + (floor_number * 5)
        weighted.append((r, weight))

    selected: list[RewardDef] = []
    pool = list(weighted)
    for _ in range(min(count, len(pool))):
        if not pool:
            break
        items, weights = zip(*pool)
        choice = random.choices(items, weights=weights, k=1)[0]
        selected.append(choice)
        pool = [(r, w) for r, w in pool if r.id != choice.id]

    return selected
