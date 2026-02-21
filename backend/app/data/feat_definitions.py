"""
D&D 2024 Feat Definitions for the Drifting Infinity combat arena.

Defines feats that can be offered as rewards to players via the DM companion UI.
Categories: origin (level 1+), general (level 4+), fighting_style (level 4+),
epic_boon (level 19+).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FeatDef:
    id: str
    name: str
    category: str  # "origin", "general", "fighting_style", "epic_boon"
    prerequisite_level: int  # 1, 4, or 19
    description: str  # Abbreviated mechanical description
    mechanics: dict = field(default_factory=dict)  # Structured effect data
    source: str = "phb-2024"
    power_rating: float = 1.0  # For reward weighting (1.0 = baseline)


# ---------------------------------------------------------------------------
# Origin Feats (Level 1+)
# ---------------------------------------------------------------------------

ORIGIN_FEATS: list[FeatDef] = [
    FeatDef(
        id="alert",
        name="Alert",
        category="origin",
        prerequisite_level=1,
        description=(
            "Add proficiency bonus to initiative. Cannot be surprised."
            " Swap initiative with a willing ally at start of combat."
        ),
        mechanics={
            "initiative_bonus": "proficiency_bonus",
            "immune_to_surprise": True,
            "swap_initiative": True,
        },
        power_rating=1.1,
    ),
    FeatDef(
        id="crafter",
        name="Crafter",
        category="origin",
        prerequisite_level=1,
        description=(
            "Proficiency with three artisan's tools of your choice."
            " 20% discount on nonmagical items. Craft items during a long rest."
        ),
        mechanics={
            "tool_proficiencies": 3,
            "purchase_discount": 0.20,
            "fast_crafting": True,
        },
        power_rating=0.6,
    ),
    FeatDef(
        id="healer",
        name="Healer",
        category="origin",
        prerequisite_level=1,
        description=(
            "Use a Healer's Kit as a Utilize action to restore 1d6 + 4 + target's"
            " HD. Reroll any 1 on healing dice you roll."
        ),
        mechanics={
            "battle_medic": {"heal": "1d6+4+target_hd", "action": "utilize"},
            "reroll_healing_ones": True,
        },
        power_rating=0.9,
    ),
    FeatDef(
        id="lucky",
        name="Lucky",
        category="origin",
        prerequisite_level=1,
        description=(
            "Gain Luck Points equal to proficiency bonus, refreshed on long rest."
            " Spend a point to gain advantage or impose disadvantage on a roll."
        ),
        mechanics={
            "luck_points": "proficiency_bonus",
            "recharge": "long_rest",
            "effect": "advantage_or_impose_disadvantage",
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="magic_initiate",
        name="Magic Initiate",
        category="origin",
        prerequisite_level=1,
        description=(
            "Learn two cantrips and one 1st-level spell from Cleric, Druid, or"
            " Wizard list. Cast the 1st-level spell once per long rest or with"
            " spell slots."
        ),
        mechanics={
            "cantrips": 2,
            "spells_1st": 1,
            "spell_list_choice": ["cleric", "druid", "wizard"],
            "free_cast": "long_rest",
        },
        power_rating=1.0,
    ),
    FeatDef(
        id="musician",
        name="Musician",
        category="origin",
        prerequisite_level=1,
        description=(
            "Proficiency with three musical instruments. After a short or long"
            " rest, grant Heroic Inspiration to allies who hear you perform."
        ),
        mechanics={
            "instrument_proficiencies": 3,
            "grant_inspiration_on_rest": True,
        },
        power_rating=0.7,
    ),
    FeatDef(
        id="savage_attacker",
        name="Savage Attacker",
        category="origin",
        prerequisite_level=1,
        description=(
            "Once per turn, roll weapon or unarmed damage dice twice and use"
            " either roll."
        ),
        mechanics={
            "reroll_weapon_damage": True,
            "frequency": "once_per_turn",
        },
        power_rating=0.9,
    ),
    FeatDef(
        id="skilled",
        name="Skilled",
        category="origin",
        prerequisite_level=1,
        description=(
            "Gain proficiency in any combination of three skills or tools."
        ),
        mechanics={
            "skill_or_tool_proficiencies": 3,
        },
        power_rating=0.6,
    ),
    FeatDef(
        id="tavern_brawler",
        name="Tavern Brawler",
        category="origin",
        prerequisite_level=1,
        description=(
            "Enhanced unarmed strikes deal 1d4 + STR. Push a creature 5 ft on"
            " unarmed hit. Proficiency with improvised weapons. Reroll damage 1s."
        ),
        mechanics={
            "unarmed_damage": "1d4+str",
            "push_on_hit": 5,
            "improvised_weapon_proficiency": True,
            "reroll_damage_ones": True,
        },
        power_rating=0.8,
    ),
    FeatDef(
        id="tough",
        name="Tough",
        category="origin",
        prerequisite_level=1,
        description=(
            "HP maximum increases by 2 per level. Retroactive for all existing"
            " levels."
        ),
        mechanics={
            "hp_per_level": 2,
        },
        power_rating=1.0,
    ),
]


# ---------------------------------------------------------------------------
# General Feats (Level 4+)
# ---------------------------------------------------------------------------

GENERAL_FEATS: list[FeatDef] = [
    FeatDef(
        id="athlete",
        name="Athlete",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or DEX. Climbing doesn't cost extra movement. Running"
            " long/high jumps need only 5 ft of movement."
        ),
        mechanics={
            "asi": {"choices": ["str", "dex"], "amount": 1},
            "climb_speed": "walking",
            "reduced_jump_approach": 5,
        },
        power_rating=0.7,
    ),
    FeatDef(
        id="charger",
        name="Charger",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or DEX. When you Dash, you can make one melee attack or"
            " shove as a bonus action with +1d8 damage on hit."
        ),
        mechanics={
            "asi": {"choices": ["str", "dex"], "amount": 1},
            "dash_bonus_attack": True,
            "bonus_damage": "1d8",
        },
        power_rating=0.8,
    ),
    FeatDef(
        id="crossbow_expert",
        name="Crossbow Expert",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 DEX. Ignore loading property of crossbows. No disadvantage on"
            " ranged attacks within 5 ft. Bonus action hand crossbow attack."
        ),
        mechanics={
            "asi": {"choices": ["dex"], "amount": 1},
            "ignore_loading": True,
            "no_close_range_disadvantage": True,
            "bonus_action_hand_crossbow": True,
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="defensive_duelist",
        name="Defensive Duelist",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 DEX. Use a reaction when hit by a melee attack while wielding a"
            " finesse weapon: add proficiency bonus to AC for that attack."
        ),
        mechanics={
            "asi": {"choices": ["dex"], "amount": 1},
            "reaction_ac_bonus": "proficiency_bonus",
            "requires": "finesse_weapon",
        },
        power_rating=0.9,
    ),
    FeatDef(
        id="dual_wielder",
        name="Dual Wielder",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or DEX. When two-weapon fighting, can use non-light weapons."
            " Draw or stow two weapons at once."
        ),
        mechanics={
            "asi": {"choices": ["str", "dex"], "amount": 1},
            "twf_non_light": True,
            "quick_draw_two": True,
        },
        power_rating=0.9,
    ),
    FeatDef(
        id="great_weapon_master",
        name="Great Weapon Master",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR. On a heavy weapon hit, deal extra damage equal to proficiency"
            " bonus. Bonus action attack on crit or reducing a creature to 0 HP."
        ),
        mechanics={
            "asi": {"choices": ["str"], "amount": 1},
            "extra_damage_heavy": "proficiency_bonus",
            "bonus_attack_on_crit_or_kill": True,
        },
        power_rating=1.4,
    ),
    FeatDef(
        id="heavily_armored",
        name="Heavily Armored",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or CON. Gain proficiency with heavy armor. Prerequisite:"
            " medium armor proficiency."
        ),
        mechanics={
            "asi": {"choices": ["str", "con"], "amount": 1},
            "armor_proficiency": "heavy",
            "prerequisite_proficiency": "medium_armor",
        },
        power_rating=0.8,
    ),
    FeatDef(
        id="heavy_armor_master",
        name="Heavy Armor Master",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or CON. While wearing heavy armor, reduce nonmagical B/P/S"
            " damage by proficiency bonus."
        ),
        mechanics={
            "asi": {"choices": ["str", "con"], "amount": 1},
            "damage_reduction": {
                "types": ["bludgeoning", "piercing", "slashing"],
                "nonmagical_only": True,
                "amount": "proficiency_bonus",
            },
            "requires": "heavy_armor",
        },
        power_rating=1.1,
    ),
    FeatDef(
        id="inspiring_leader",
        name="Inspiring Leader",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 WIS or CHA. After a short or long rest, grant up to 6 allies"
            " temporary HP equal to your level + CHA modifier."
        ),
        mechanics={
            "asi": {"choices": ["wis", "cha"], "amount": 1},
            "temp_hp_grant": "level+cha_mod",
            "targets": 6,
            "recharge": "short_rest",
        },
        power_rating=1.0,
    ),
    FeatDef(
        id="mage_slayer",
        name="Mage Slayer",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or DEX. When you damage a concentrating creature, it has"
            " disadvantage on the save. Reaction attack when a creature within"
            " 5 ft casts a spell."
        ),
        mechanics={
            "asi": {"choices": ["str", "dex"], "amount": 1},
            "concentration_disadvantage": True,
            "reaction_attack_on_cast": {"range": 5},
        },
        power_rating=1.1,
    ),
    FeatDef(
        id="mobile",
        name="Mobile",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 DEX. Speed increases by 10 ft. When you make a melee attack, you"
            " don't provoke opportunity attacks from that target."
        ),
        mechanics={
            "asi": {"choices": ["dex"], "amount": 1},
            "speed_bonus": 10,
            "no_opportunity_attack_after_melee": True,
        },
        power_rating=1.1,
    ),
    FeatDef(
        id="observant",
        name="Observant",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 INT or WIS. +5 bonus to passive Perception and passive"
            " Investigation. Can read lips if you can see a creature's mouth."
        ),
        mechanics={
            "asi": {"choices": ["int", "wis"], "amount": 1},
            "passive_perception_bonus": 5,
            "passive_investigation_bonus": 5,
            "lip_reading": True,
        },
        power_rating=0.7,
    ),
    FeatDef(
        id="polearm_master",
        name="Polearm Master",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR. Bonus action 1d4 butt-end attack with glaive, halberd,"
            " quarterstaff, or spear. Opportunity attack when a creature enters"
            " your reach."
        ),
        mechanics={
            "asi": {"choices": ["str"], "amount": 1},
            "bonus_action_butt_attack": "1d4",
            "opportunity_attack_on_enter": True,
            "weapons": ["glaive", "halberd", "quarterstaff", "spear"],
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="resilient",
        name="Resilient",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 to one ability score. Gain proficiency in saving throws of that"
            " ability."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1},
            "saving_throw_proficiency": "chosen_ability",
        },
        power_rating=1.1,
    ),
    FeatDef(
        id="ritual_caster",
        name="Ritual Caster",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 INT, WIS, or CHA. Learn two ritual spells. Can cast ritual spells"
            " you have without preparing them."
        ),
        mechanics={
            "asi": {"choices": ["int", "wis", "cha"], "amount": 1},
            "ritual_spells_known": 2,
            "ritual_casting": True,
        },
        power_rating=0.7,
    ),
    FeatDef(
        id="sentinel",
        name="Sentinel",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR or DEX. Opportunity attacks reduce speed to 0. Reaction"
            " attack when an ally within 5 ft is hit."
        ),
        mechanics={
            "asi": {"choices": ["str", "dex"], "amount": 1},
            "opportunity_attack_stops_movement": True,
            "reaction_attack_ally_hit": {"range": 5},
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="sharpshooter",
        name="Sharpshooter",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 DEX. Ignore half and three-quarters cover on ranged attacks."
            " No disadvantage at long range. Can trade -5 to hit for +10 damage."
        ),
        mechanics={
            "asi": {"choices": ["dex"], "amount": 1},
            "ignore_cover": ["half", "three_quarters"],
            "no_long_range_disadvantage": True,
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="shield_master",
        name="Shield Master",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 STR. Bonus action shove when you take the Attack action with a"
            " shield. Add shield AC bonus to DEX saves vs. single-target effects."
        ),
        mechanics={
            "asi": {"choices": ["str"], "amount": 1},
            "bonus_action_shove": True,
            "shield_to_dex_saves": True,
            "requires": "shield",
        },
        power_rating=1.0,
    ),
    FeatDef(
        id="spell_sniper",
        name="Spell Sniper",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 in spellcasting ability. Attack roll spells have doubled range and"
            " ignore half and three-quarters cover. Learn one attack-roll cantrip."
        ),
        mechanics={
            "asi": {"choices": ["int", "wis", "cha"], "amount": 1},
            "double_spell_range": True,
            "ignore_cover": ["half", "three_quarters"],
            "bonus_cantrip": 1,
        },
        power_rating=1.0,
    ),
    FeatDef(
        id="war_caster",
        name="War Caster",
        category="general",
        prerequisite_level=4,
        description=(
            "+1 in spellcasting ability. Advantage on CON saves for concentration."
            " Perform somatic components with hands full. Cast a spell as an"
            " opportunity attack."
        ),
        mechanics={
            "asi": {"choices": ["int", "wis", "cha"], "amount": 1},
            "concentration_advantage": True,
            "somatic_hands_full": True,
            "spell_opportunity_attack": True,
        },
        power_rating=1.3,
    ),
]


# ---------------------------------------------------------------------------
# Fighting Style Feats (Level 4+)
# ---------------------------------------------------------------------------

FIGHTING_STYLE_FEATS: list[FeatDef] = [
    FeatDef(
        id="fs_archery",
        name="Fighting Style: Archery",
        category="fighting_style",
        prerequisite_level=4,
        description="+2 bonus to attack rolls with ranged weapons.",
        mechanics={"ranged_attack_bonus": 2},
        power_rating=1.1,
    ),
    FeatDef(
        id="fs_blind_fighting",
        name="Fighting Style: Blind Fighting",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "Gain 10 ft of blindsight. You can effectively see invisible"
            " creatures within that range."
        ),
        mechanics={"blindsight": 10},
        power_rating=0.8,
    ),
    FeatDef(
        id="fs_defense",
        name="Fighting Style: Defense",
        category="fighting_style",
        prerequisite_level=4,
        description="+1 bonus to AC while wearing armor.",
        mechanics={"ac_bonus": 1, "requires": "armor"},
        power_rating=1.0,
    ),
    FeatDef(
        id="fs_dueling",
        name="Fighting Style: Dueling",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "+2 bonus to damage rolls with a melee weapon held in one hand"
            " when no other weapon is held."
        ),
        mechanics={"melee_damage_bonus": 2, "requires": "one_handed_only"},
        power_rating=1.1,
    ),
    FeatDef(
        id="fs_great_weapon_fighting",
        name="Fighting Style: Great Weapon Fighting",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "Reroll 1s and 2s on damage dice with two-handed or versatile melee"
            " weapons (must use the new roll)."
        ),
        mechanics={
            "reroll_damage": {"threshold": 2, "weapons": "two_handed_or_versatile"},
        },
        power_rating=0.9,
    ),
    FeatDef(
        id="fs_interception",
        name="Fighting Style: Interception",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "Use reaction when an ally within 5 ft is hit: reduce damage by"
            " 1d10 + proficiency bonus. Requires a shield or weapon."
        ),
        mechanics={
            "reaction_damage_reduction": "1d10+proficiency_bonus",
            "range": 5,
        },
        power_rating=1.0,
    ),
    FeatDef(
        id="fs_protection",
        name="Fighting Style: Protection",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "Use reaction when an ally within 5 ft is attacked: impose"
            " disadvantage on the attack roll. Requires a shield."
        ),
        mechanics={
            "reaction_impose_disadvantage": True,
            "range": 5,
            "requires": "shield",
        },
        power_rating=1.0,
    ),
    FeatDef(
        id="fs_superior_technique",
        name="Fighting Style: Superior Technique",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "Learn one Battle Master maneuver. Gain one d6 superiority die,"
            " refreshed on short or long rest."
        ),
        mechanics={
            "maneuvers": 1,
            "superiority_dice": {"count": 1, "size": "d6"},
            "recharge": "short_rest",
        },
        power_rating=0.8,
    ),
    FeatDef(
        id="fs_thrown_weapon_fighting",
        name="Fighting Style: Thrown Weapon Fighting",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "+2 bonus to damage with thrown weapons. Draw a thrown weapon as part"
            " of the attack."
        ),
        mechanics={"thrown_damage_bonus": 2, "quick_draw_thrown": True},
        power_rating=0.8,
    ),
    FeatDef(
        id="fs_two_weapon_fighting",
        name="Fighting Style: Two-Weapon Fighting",
        category="fighting_style",
        prerequisite_level=4,
        description=(
            "Add ability modifier to the damage of the bonus action attack when"
            " two-weapon fighting."
        ),
        mechanics={"twf_ability_mod_damage": True},
        power_rating=0.9,
    ),
]


# ---------------------------------------------------------------------------
# Epic Boon Feats (Level 19+)
# All Epic Boons also grant +1 to one ability score (up to 30).
# ---------------------------------------------------------------------------

EPIC_BOON_FEATS: list[FeatDef] = [
    FeatDef(
        id="boon_combat_prowess",
        name="Boon of Combat Prowess",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). When you miss with an attack,"
            " you can hit instead. Usable proficiency bonus times per long rest."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "turn_miss_to_hit": True,
            "uses": "proficiency_bonus",
            "recharge": "long_rest",
        },
        power_rating=1.5,
    ),
    FeatDef(
        id="boon_dimensional_travel",
        name="Boon of Dimensional Travel",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). You can cast Misty Step without"
            " a spell slot proficiency bonus times per long rest."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "free_misty_step": True,
            "uses": "proficiency_bonus",
            "recharge": "long_rest",
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="boon_energy_resistance",
        name="Boon of Energy Resistance",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Gain resistance to two damage"
            " types: acid, cold, fire, lightning, necrotic, poison, psychic,"
            " radiant, or thunder."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "damage_resistance_choices": 2,
            "resistance_options": [
                "acid", "cold", "fire", "lightning", "necrotic",
                "poison", "psychic", "radiant", "thunder",
            ],
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="boon_fate",
        name="Boon of Fate",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). When you or an ally within 60 ft"
            " fails a d20 roll, add or subtract 2d4. Usable proficiency bonus"
            " times per long rest."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "modify_roll": "2d4",
            "range": 60,
            "uses": "proficiency_bonus",
            "recharge": "long_rest",
        },
        power_rating=1.4,
    ),
    FeatDef(
        id="boon_fortitude",
        name="Boon of Fortitude",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). HP maximum increases by 40."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "hp_increase": 40,
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="boon_irresistible_offense",
        name="Boon of Irresistible Offense",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Your attacks ignore resistance."
            " When you deal damage, you can treat immunity as resistance"
            " (proficiency bonus times per long rest)."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "ignore_resistance": True,
            "immunity_to_resistance": True,
            "uses": "proficiency_bonus",
            "recharge": "long_rest",
        },
        power_rating=1.5,
    ),
    FeatDef(
        id="boon_recovery",
        name="Boon of Recovery",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). As a bonus action, regain"
            " half your HP if you have half or fewer remaining. Once per long"
            " rest."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "bonus_action_heal_half": True,
            "trigger": "at_or_below_half_hp",
            "uses": 1,
            "recharge": "long_rest",
        },
        power_rating=1.4,
    ),
    FeatDef(
        id="boon_skill",
        name="Boon of Skill",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Gain proficiency in all skills."
            " Proficiency bonus applies to initiative as well."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "all_skill_proficiency": True,
            "initiative_proficiency": True,
        },
        power_rating=1.2,
    ),
    FeatDef(
        id="boon_speed",
        name="Boon of Speed",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Speed increases by 30 ft."
            " Opportunity attacks against you have disadvantage."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "speed_bonus": 30,
            "opportunity_attack_disadvantage": True,
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="boon_spell_recall",
        name="Boon of Spell Recall",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Once per short rest, you can cast"
            " a spell of 5th level or lower without expending a spell slot."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "free_spell_cast": {"max_level": 5},
            "uses": 1,
            "recharge": "short_rest",
        },
        power_rating=1.5,
    ),
    FeatDef(
        id="boon_night_spirit",
        name="Boon of the Night Spirit",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Gain darkvision 300 ft. While"
            " in dim light or darkness, you can become invisible (until you"
            " attack, cast a spell, or enter bright light)."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "darkvision": 300,
            "shadow_invisibility": True,
        },
        power_rating=1.3,
    ),
    FeatDef(
        id="boon_truesight",
        name="Boon of Truesight",
        category="epic_boon",
        prerequisite_level=19,
        description=(
            "+1 to any ability score (max 30). Gain truesight out to 60 ft."
        ),
        mechanics={
            "asi": {"choices": ["any"], "amount": 1, "max": 30},
            "truesight": 60,
        },
        power_rating=1.2,
    ),
]


# ---------------------------------------------------------------------------
# Combined registry
# ---------------------------------------------------------------------------

ALL_FEATS: list[FeatDef] = (
    ORIGIN_FEATS + GENERAL_FEATS + FIGHTING_STYLE_FEATS + EPIC_BOON_FEATS
)

_FEAT_INDEX: dict[str, FeatDef] = {feat.id: feat for feat in ALL_FEATS}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_feats_for_level(party_level: int) -> list[FeatDef]:
    """Return all feats whose prerequisite level is met by *party_level*."""
    return [f for f in ALL_FEATS if f.prerequisite_level <= party_level]


def get_feats_by_category(category: str) -> list[FeatDef]:
    """Return feats matching the given category string.

    Valid categories: ``"origin"``, ``"general"``, ``"fighting_style"``,
    ``"epic_boon"``.
    """
    return [f for f in ALL_FEATS if f.category == category]


def get_feat(feat_id: str) -> Optional[FeatDef]:
    """Look up a single feat by its unique *feat_id*.

    Returns ``None`` if the ID is not found.
    """
    return _FEAT_INDEX.get(feat_id)
