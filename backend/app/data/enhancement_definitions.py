"""Enhancement catalog per GDD 6.3."""

from dataclasses import dataclass


@dataclass
class EnhancementDef:
    id: str
    name: str
    tier: int  # 1, 2, or 3
    base_cost: int  # Gold cost
    effect_type: str  # "stat_boost", "damage_boost", "defense", "utility"
    effect: dict  # Effect details
    description: str
    power_rating: float  # 1.0 = baseline power
    max_stacks: int  # How many times this can be purchased per character
    d20_source: str = ""  # D&D mechanic this enhancement mirrors


# Tier caps: max enhancements per tier per character
TIER_CAPS: dict[int, int] = {
    1: 3,
    2: 2,
    3: 1,
}


ENHANCEMENTS: list[EnhancementDef] = [
    # === TIER 1 (cheap, small boosts) ===
    EnhancementDef(
        id="enh_hp_boost_1", name="Vitality I", tier=1, base_cost=100,
        effect_type="stat_boost", effect={"max_hp": 5},
        description="+5 maximum HP.", power_rating=1.0, max_stacks=3,
        d20_source="Tough feat",
    ),
    EnhancementDef(
        id="enh_ac_boost_1", name="Iron Skin I", tier=1, base_cost=150,
        effect_type="defense", effect={"ac": 1},
        description="+1 AC.", power_rating=1.2, max_stacks=2,
        d20_source="Defense Fighting Style",
    ),
    EnhancementDef(
        id="enh_save_boost_1", name="Resilience I", tier=1, base_cost=120,
        effect_type="stat_boost", effect={"save_bonus": 1},
        description="+1 to all saving throws.", power_rating=1.1, max_stacks=2,
        d20_source="Cloak of Protection",
    ),
    EnhancementDef(
        id="enh_damage_boost_1", name="Sharpness I", tier=1, base_cost=130,
        effect_type="damage_boost", effect={"damage_bonus": 1},
        description="+1 damage to all weapon attacks.", power_rating=1.0, max_stacks=3,
        d20_source="Dueling Fighting Style",
    ),
    EnhancementDef(
        id="enh_speed_boost_1", name="Swiftness I", tier=1, base_cost=80,
        effect_type="stat_boost", effect={"speed": 5},
        description="+5 ft. movement speed.", power_rating=0.8, max_stacks=2,
        d20_source="Mobile feat (partial)",
    ),
    EnhancementDef(
        id="enh_initiative_1", name="Quick Reflexes I", tier=1, base_cost=100,
        effect_type="stat_boost", effect={"initiative": 2},
        description="+2 to initiative rolls.", power_rating=0.9, max_stacks=2,
        d20_source="Alert feat (partial)",
    ),
    EnhancementDef(
        id="enh_ferocity_1", name="Ferocity I", tier=1, base_cost=130,
        effect_type="stat_boost", effect={"attack_bonus": 1},
        description="+1 to attack rolls.", power_rating=1.1, max_stacks=2,
        d20_source="Archery Fighting Style",
    ),
    EnhancementDef(
        id="enh_tough_hide_1", name="Tough Hide I", tier=1, base_cost=140,
        effect_type="defense", effect={"damage_reduction_bps": 1},
        description="Reduce nonmagical bludgeoning, piercing, and slashing damage by 1.",
        power_rating=1.0, max_stacks=2,
        d20_source="Heavy Armor Master feat",
    ),
    EnhancementDef(
        id="enh_lucky_charm", name="Lucky Charm", tier=1, base_cost=80,
        effect_type="utility", effect={"death_save_bonus": 1},
        description="+1 to death saving throws.", power_rating=0.8, max_stacks=1,
        d20_source="Lucky feat",
    ),
    EnhancementDef(
        id="enh_spell_focus_1", name="Spell Focus I", tier=1, base_cost=130,
        effect_type="stat_boost", effect={"spell_attack_bonus": 1},
        description="+1 to spell attack rolls.", power_rating=1.1, max_stacks=2,
        d20_source="Wand of the War Mage +1",
    ),
    EnhancementDef(
        id="enh_battle_awareness", name="Battle Awareness", tier=1, base_cost=90,
        effect_type="stat_boost", effect={"passive_perception": 2},
        description="+2 to passive Perception.", power_rating=0.8, max_stacks=1,
        d20_source="Observant feat",
    ),
    EnhancementDef(
        id="enh_constitution_1", name="Constitution I", tier=1, base_cost=150,
        effect_type="utility", effect={"concentration_advantage": True},
        description="Advantage on concentration checks.", power_rating=1.2, max_stacks=1,
        d20_source="War Caster feat",
    ),
    EnhancementDef(
        id="enh_swift_recovery", name="Swift Recovery", tier=1, base_cost=110,
        effect_type="utility", effect={"short_rest_heal_bonus": "1d8"},
        description="Heal an extra 1d8 when spending Hit Dice on a short rest.",
        power_rating=0.9, max_stacks=2,
        d20_source="Healer feat",
    ),
    EnhancementDef(
        id="enh_sentinel_reflexes", name="Sentinel's Reflexes", tier=1, base_cost=100,
        effect_type="stat_boost", effect={"initiative": 2, "no_surprise": True},
        description="+2 initiative and cannot be surprised.",
        power_rating=1.0, max_stacks=1,
        d20_source="Alert feat",
    ),
    EnhancementDef(
        id="enh_arcane_sensitivity", name="Arcane Sensitivity", tier=1, base_cost=90,
        effect_type="utility", effect={"detect_magic_at_will": True, "range": 10},
        description="Detect magic at will within 10 ft.",
        power_rating=0.8, max_stacks=1,
        d20_source="Magic Initiate",
    ),
    EnhancementDef(
        id="enh_durable", name="Durable", tier=1, base_cost=120,
        effect_type="stat_boost", effect={"max_hp_per_level": 1},
        description="+1 max HP per character level.",
        power_rating=1.1, max_stacks=1,
        d20_source="Tough feat (per-level)",
    ),
    EnhancementDef(
        id="enh_focused_mind", name="Focused Mind", tier=1, base_cost=130,
        effect_type="defense", effect={"mental_save_bonus": 1},
        description="+1 to Intelligence, Wisdom, and Charisma saving throws.",
        power_rating=1.0, max_stacks=2,
        d20_source="Resilient feat",
    ),
    EnhancementDef(
        id="enh_opportunist", name="Opportunist", tier=1, base_cost=130,
        effect_type="damage_boost", effect={"opportunity_damage_bonus": 2},
        description="+2 damage on opportunity attacks.",
        power_rating=1.0, max_stacks=2,
        d20_source="Sentinel feat",
    ),

    # === TIER 2 (moderate cost, notable boosts) ===
    EnhancementDef(
        id="enh_hp_boost_2", name="Vitality II", tier=2, base_cost=300,
        effect_type="stat_boost", effect={"max_hp": 15},
        description="+15 maximum HP.", power_rating=1.5, max_stacks=2,
        d20_source="Tough feat (scaled)",
    ),
    EnhancementDef(
        id="enh_resist_element", name="Elemental Ward", tier=2, base_cost=350,
        effect_type="defense", effect={"resistance": "choose_one"},
        description="Gain resistance to one damage type (chosen at purchase).",
        power_rating=1.6, max_stacks=2,
        d20_source="Absorb Elements / Ring of Resistance",
    ),
    EnhancementDef(
        id="enh_spell_slot", name="Arcane Reserve", tier=2, base_cost=400,
        effect_type="utility", effect={"bonus_spell_slot": 2},
        description="Gain one additional 2nd-level spell slot per run.",
        power_rating=1.7, max_stacks=1,
        d20_source="Pearl of Power",
    ),
    EnhancementDef(
        id="enh_crit_range", name="Keen Edge", tier=2, base_cost=350,
        effect_type="damage_boost", effect={"crit_range": 1},
        description="Critical hit range expands by 1 (e.g., 19-20).",
        power_rating=1.8, max_stacks=1,
        d20_source="Champion Fighter Improved Critical",
    ),
    EnhancementDef(
        id="enh_damage_boost_2", name="Sharpness II", tier=2, base_cost=280,
        effect_type="damage_boost", effect={"damage_bonus": 2},
        description="+2 damage to all weapon attacks.", power_rating=1.4, max_stacks=2,
        d20_source="Great Weapon Fighting Style (scaled)",
    ),
    EnhancementDef(
        id="enh_second_wind", name="Second Wind", tier=2, base_cost=300,
        effect_type="utility", effect={"heal_once": "1d10+level", "action_type": "bonus"},
        description="Heal 1d10 + character level HP once per arena as a bonus action.",
        power_rating=1.5, max_stacks=1,
        d20_source="Fighter Second Wind feature",
    ),
    EnhancementDef(
        id="enh_ferocity_2", name="Ferocity II", tier=2, base_cost=280,
        effect_type="stat_boost", effect={"attack_bonus": 2},
        description="+2 to attack rolls.", power_rating=1.6, max_stacks=1,
        d20_source="Archery Fighting Style (scaled)",
    ),
    EnhancementDef(
        id="enh_momentum_mastery", name="Momentum Mastery", tier=2, base_cost=250,
        effect_type="utility", effect={"bonus_action_disengage": True, "bonus_action_dash": True},
        description="You can Disengage or Dash as a bonus action.",
        power_rating=1.3, max_stacks=1,
        d20_source="Mobile feat / Rogue Cunning Action",
    ),
    EnhancementDef(
        id="enh_arcane_reservoir_2", name="Arcane Reservoir II", tier=2, base_cost=400,
        effect_type="utility", effect={"bonus_spell_slot": 3},
        description="Gain one additional 3rd-level spell slot per run.",
        power_rating=1.8, max_stacks=1,
        d20_source="Pearl of Power (greater)",
    ),
    EnhancementDef(
        id="enh_evasive_footwork", name="Evasive Footwork", tier=2, base_cost=300,
        effect_type="defense", effect={"ac_vs_opportunity": 2},
        description="+2 AC against opportunity attacks.",
        power_rating=1.4, max_stacks=1,
        d20_source="Defensive Duelist feat",
    ),
    EnhancementDef(
        id="enh_elemental_infusion", name="Elemental Infusion", tier=2, base_cost=350,
        effect_type="damage_boost",
        effect={"bonus_elemental_damage": "1d4", "element": "choose_one"},
        description="Add 1d4 elemental damage to weapon attacks. Choose element at purchase.",
        power_rating=1.6, max_stacks=1,
        d20_source="Elemental Weapon spell",
    ),
    EnhancementDef(
        id="enh_spell_reservoir", name="Spell Reservoir", tier=2, base_cost=380,
        effect_type="utility", effect={"recover_spell_slot": 2, "uses_per_arena": 1},
        description="Recover one 2nd-level spell slot per arena.",
        power_rating=1.6, max_stacks=1,
        d20_source="Arcane Recovery",
    ),
    EnhancementDef(
        id="enh_battle_medic", name="Battle Medic", tier=2, base_cost=300,
        effect_type="utility", effect={"heal_bonus_action": "1d6+level", "uses_per_arena": 1},
        description="Heal 1d6 + character level as a bonus action once per arena.",
        power_rating=1.4, max_stacks=1,
        d20_source="Healer feat",
    ),
    EnhancementDef(
        id="enh_relentless_endurance", name="Relentless Endurance", tier=2, base_cost=350,
        effect_type="defense", effect={"drop_to_1hp": True, "uses_per_floor": 1},
        description="When reduced to 0 HP, drop to 1 HP instead (once per floor).",
        power_rating=1.7, max_stacks=1,
        d20_source="Half-Orc Relentless Endurance",
    ),
    EnhancementDef(
        id="enh_phase_step", name="Phase Step", tier=2, base_cost=350,
        effect_type="utility",
        effect={"teleport_ft": 10, "action_type": "bonus", "uses_per_arena": 1},
        description="Teleport 10 ft as a bonus action once per arena.",
        power_rating=1.5, max_stacks=1,
        d20_source="Misty Step spell",
    ),
    EnhancementDef(
        id="enh_counterstrike", name="Counterstrike", tier=2, base_cost=280,
        effect_type="damage_boost", effect={"riposte_on_miss": True, "reaction": True},
        description="When a creature misses you with a melee attack, use your reaction to make a melee attack.",
        power_rating=1.5, max_stacks=1,
        d20_source="Battle Master Riposte",
    ),
    EnhancementDef(
        id="enh_elemental_mastery", name="Elemental Mastery", tier=2, base_cost=320,
        effect_type="damage_boost",
        effect={"bonus_element_damage": "1d6", "element": "choose_one", "once_per_turn": True},
        description="Once per turn, deal an extra 1d6 damage of a chosen element.",
        power_rating=1.6, max_stacks=1,
        d20_source="Elemental Adept feat",
    ),
    EnhancementDef(
        id="enh_spell_sniper", name="Spell Sniper", tier=2, base_cost=260,
        effect_type="stat_boost",
        effect={"spell_range_bonus_ft": 30, "ignore_half_cover": True},
        description="+30 ft spell range and ignore half cover.",
        power_rating=1.3, max_stacks=1,
        d20_source="Spell Sniper feat",
    ),
    EnhancementDef(
        id="enh_iron_will", name="Iron Will", tier=2, base_cost=300,
        effect_type="defense", effect={"mental_save_bonus": 2},
        description="+2 to Intelligence, Wisdom, and Charisma saving throws.",
        power_rating=1.5, max_stacks=1,
        d20_source="Resilient feat (scaled)",
    ),

    # === TIER 3 (expensive, powerful) ===
    EnhancementDef(
        id="enh_extra_attack", name="War Surge", tier=3, base_cost=800,
        effect_type="damage_boost", effect={"extra_attack": 1},
        description="Gain one additional attack per turn (once per arena).",
        power_rating=2.5, max_stacks=1,
        d20_source="Fighter Extra Attack",
    ),
    EnhancementDef(
        id="enh_death_ward", name="Death Ward", tier=3, base_cost=700,
        effect_type="defense", effect={"death_ward": True},
        description="Once per run, when you drop to 0 HP, instead drop to 1 HP.",
        power_rating=2.2, max_stacks=1,
        d20_source="Death Ward spell",
    ),
    EnhancementDef(
        id="enh_ac_boost_3", name="Adamantine Skin", tier=3, base_cost=750,
        effect_type="defense", effect={"ac": 2, "resist_critical": True},
        description="+2 AC and critical hits against you become normal hits.",
        power_rating=2.8, max_stacks=1,
        d20_source="Adamantine Armor",
    ),
    EnhancementDef(
        id="enh_hp_boost_3", name="Vitality III", tier=3, base_cost=600,
        effect_type="stat_boost", effect={"max_hp": 30},
        description="+30 maximum HP.", power_rating=2.0, max_stacks=1,
        d20_source="Tough feat (greater)",
    ),
    EnhancementDef(
        id="enh_legendary_resilience", name="Legendary Resilience", tier=3, base_cost=900,
        effect_type="defense", effect={"auto_save_success": 1},
        description="Automatically succeed on one saving throw per run.",
        power_rating=3.0, max_stacks=1,
        d20_source="Legendary Resistance",
    ),
    EnhancementDef(
        id="enh_avatar_of_war", name="Avatar of War", tier=3, base_cost=850,
        effect_type="damage_boost",
        effect={"extra_attack": 1, "damage_bonus": 2, "uses_per_arena": 1},
        description="One additional attack per turn and +2 damage, once per arena.",
        power_rating=2.8, max_stacks=1,
        d20_source="Fighter Action Surge",
    ),
    EnhancementDef(
        id="enh_phoenix_soul", name="Phoenix Soul", tier=3, base_cost=800,
        effect_type="defense",
        effect={"death_to_1hp": True, "fire_burst": "2d6", "burst_radius": 10},
        description="On dropping to 0 HP, instead drop to 1 HP and deal 2d6 fire damage in a 10 ft. radius (once per run).",
        power_rating=2.5, max_stacks=1,
        d20_source="Half-Orc Relentless Endurance / Phoenix Sorcery",
    ),
    EnhancementDef(
        id="enh_fate_weaver", name="Fate Weaver", tier=3, base_cost=600,
        effect_type="utility", effect={"bonus_favour_per_floor": 1},
        description="Gain +1 Armillary's Favour per floor.",
        power_rating=2.0, max_stacks=1,
        d20_source="Divination Wizard Portent",
    ),
    EnhancementDef(
        id="enh_mythic_recovery", name="Mythic Recovery", tier=3, base_cost=650,
        effect_type="utility",
        effect={"regain_all_hit_dice": True, "trigger": "floor_completion"},
        description="Regain all Hit Dice when completing a floor.",
        power_rating=2.0, max_stacks=1,
        d20_source="Durable feat (greater)",
    ),
    EnhancementDef(
        id="enh_time_stop", name="Time Stop", tier=3, base_cost=900,
        effect_type="utility", effect={"extra_turn": True, "uses_per_run": 1},
        description="Take an extra turn immediately (once per run).",
        power_rating=3.0, max_stacks=1,
        d20_source="Time Stop spell",
    ),
    EnhancementDef(
        id="enh_spell_immunity", name="Spell Immunity", tier=3, base_cost=750,
        effect_type="defense",
        effect={"immune_school": "choose_one", "uses_per_arena": 1},
        description="Become immune to one spell school for 1 round (once per arena).",
        power_rating=2.5, max_stacks=1,
        d20_source="Globe of Invulnerability",
    ),
    EnhancementDef(
        id="enh_true_polymorph", name="True Polymorph", tier=3, base_cost=850,
        effect_type="utility",
        effect={"transform_cr": "equal_to_level", "uses_per_run": 1},
        description="Transform into a creature with CR equal to your level (once per run).",
        power_rating=2.8, max_stacks=1,
        d20_source="True Polymorph spell",
    ),
]


def get_enhancement(enhancement_id: str) -> EnhancementDef | None:
    for e in ENHANCEMENTS:
        if e.id == enhancement_id:
            return e
    return None


def get_enhancements_by_tier(tier: int) -> list[EnhancementDef]:
    return [e for e in ENHANCEMENTS if e.tier == tier]
