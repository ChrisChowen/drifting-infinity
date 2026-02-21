"""Armillary effect definitions per GDD 5.0.

Each effect has:
- key: unique identifier
- category: hostile | beneficial | environmental | wild
- name: display name
- description: what happens when this effect activates
- xp_cost: XP budget this effect "costs" (for budget tracking in Phase 2)
- severity: 1-3 (minor, moderate, major)
- min_round: earliest round this can appear (0 = any)
"""

from dataclasses import dataclass


@dataclass
class ArmillaryEffectDef:
    key: str
    category: str
    name: str
    description: str
    xp_cost: int
    severity: int
    min_round: int = 0


ARMILLARY_EFFECTS: list[ArmillaryEffectDef] = [
    # === HOSTILE (bad for party) ===
    ArmillaryEffectDef(
        key="hostile_rallying_cry",
        category="hostile",
        name="Rallying Cry",
        description="All enemy creatures gain +2 to attack rolls until end of next round.",
        xp_cost=50, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_dark_surge",
        category="hostile",
        name="Dark Surge",
        description="Each enemy creature heals 1d6 HP.",
        xp_cost=40, severity=1,
    ),
    ArmillaryEffectDef(
        key="hostile_shadow_veil",
        category="hostile",
        name="Shadow Veil",
        description="All enemy creatures gain half cover (+2 AC) until end of next round.",
        xp_cost=45, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_bloodlust",
        category="hostile",
        name="Bloodlust",
        description="All enemy creatures deal an extra 1d4 damage on their next attack.",
        xp_cost=55, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_reinforcements",
        category="hostile",
        name="Reinforcements Inbound",
        description="A CR 1/4 creature joins the fight next round (DM chooses type).",
        xp_cost=60, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="hostile_arcane_interference",
        category="hostile",
        name="Arcane Interference",
        description="All spell attack rolls have disadvantage until end of next round.",
        xp_cost=50, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_tremor",
        category="hostile",
        name="Ground Tremor",
        description="Each party member must succeed on a DC 12 DEX save or fall prone.",
        xp_cost=40, severity=1,
    ),
    ArmillaryEffectDef(
        key="hostile_empowered_boss",
        category="hostile",
        name="Empowered Boss",
        description="The highest-CR creature gains resistance to all damage until end of next round.",
        xp_cost=70, severity=3, min_round=3,
    ),
    ArmillaryEffectDef(
        key="hostile_drain_aura",
        category="hostile",
        name="Draining Aura",
        description="Each party member takes 1d4 necrotic damage (no save).",
        xp_cost=45, severity=1,
    ),
    ArmillaryEffectDef(
        key="hostile_haste_enemies",
        category="hostile",
        name="Surge of Speed",
        description="All enemy creatures gain +10 ft. movement speed this round.",
        xp_cost=30, severity=1,
    ),
    ArmillaryEffectDef(
        key="hostile_necrotic_chains",
        category="hostile",
        name="Necrotic Chains",
        description="Each party member must succeed on a WIS save DC 13 or be restrained until end of next turn.",
        xp_cost=50, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_empowered_minions",
        category="hostile",
        name="Empowered Minions",
        description="All non-boss enemy creatures gain 5 temporary HP.",
        xp_cost=35, severity=1,
    ),
    ArmillaryEffectDef(
        key="hostile_blinding_flash",
        category="hostile",
        name="Blinding Flash",
        description="Each party member must succeed on a CON save DC 13 or be blinded for 1 round.",
        xp_cost=45, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_armor_corrosion",
        category="hostile",
        name="Armor Corrosion",
        description="One random party member gains -1 AC until end of combat.",
        xp_cost=40, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_frenzied_assault",
        category="hostile",
        name="Frenzied Assault",
        description="All enemy creatures can take a bonus action attack this round.",
        xp_cost=65, severity=3, min_round=2,
    ),
    ArmillaryEffectDef(
        key="hostile_gravity_well",
        category="hostile",
        name="Gravity Well",
        description="All party members are pulled 15 ft toward a point in the center of the arena. STR DC 14 resists.",
        xp_cost=45, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_silence_field",
        category="hostile",
        name="Silence Field",
        description="A 20 ft radius zone of silence appears. No spells with verbal components can be cast within it for 1 round.",
        xp_cost=55, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="hostile_fear_aura",
        category="hostile",
        name="Fear Aura",
        description="Each party member must succeed on a WIS DC 13 save or be frightened of the nearest enemy for 1 round.",
        xp_cost=50, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_life_drain",
        category="hostile",
        name="Life Drain",
        description="Each party member must succeed on a CON DC 13 save or have their max HP reduced by 1d6 until end of combat.",
        xp_cost=60, severity=3, min_round=2,
    ),
    ArmillaryEffectDef(
        key="hostile_mirror_trap",
        category="hostile",
        name="Mirror Trap",
        description="A duplicate of one random party member appears and fights for the enemies (same stats, half HP, lasts 2 rounds).",
        xp_cost=65, severity=3, min_round=3,
    ),
    ArmillaryEffectDef(
        key="hostile_cursed_ground",
        category="hostile",
        name="Cursed Ground",
        description="When any creature dies, all creatures within 10 ft take 1d6 necrotic damage.",
        xp_cost=40, severity=2,
    ),
    ArmillaryEffectDef(
        key="hostile_arcane_overload",
        category="hostile",
        name="Arcane Overload",
        description="Each spellcaster must succeed on an INT DC 13 save or lose their lowest remaining spell slot.",
        xp_cost=55, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="hostile_chain_lightning",
        category="hostile",
        name="Chain Lightning",
        description="Lightning strikes a random party member for 2d6 lightning damage, then chains to the nearest ally for 1d6 (DEX DC 13 half).",
        xp_cost=50, severity=2,
    ),

    # === BENEFICIAL (good for party) ===
    ArmillaryEffectDef(
        key="beneficial_healing_pulse",
        category="beneficial",
        name="Healing Pulse",
        description="Each party member heals 1d6 HP.",
        xp_cost=0, severity=1,
    ),
    ArmillaryEffectDef(
        key="beneficial_inspiration",
        category="beneficial",
        name="Arcane Inspiration",
        description="Each party member gains +2 to their next attack roll.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_vulnerability_reveal",
        category="beneficial",
        name="Vulnerability Revealed",
        description="One random enemy's vulnerability is revealed to the party.",
        xp_cost=0, severity=1,
    ),
    ArmillaryEffectDef(
        key="beneficial_shield_aura",
        category="beneficial",
        name="Protective Aura",
        description="Each party member gains +1 AC until end of next round.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_second_wind",
        category="beneficial",
        name="Second Wind",
        description="One party member (lowest HP%) regains a use of a short rest ability.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_elemental_weapon",
        category="beneficial",
        name="Elemental Weapon",
        description="Each party member's next weapon attack deals an extra 1d4 fire damage.",
        xp_cost=0, severity=1,
    ),
    ArmillaryEffectDef(
        key="beneficial_clarity",
        category="beneficial",
        name="Moment of Clarity",
        description="All party members gain advantage on their next saving throw.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_speed_boost",
        category="beneficial",
        name="Swift Feet",
        description="Each party member gains +10 ft. movement speed this round.",
        xp_cost=0, severity=1,
    ),
    ArmillaryEffectDef(
        key="beneficial_arcane_shield",
        category="beneficial",
        name="Arcane Shield",
        description="Each party member gains 1d6+2 temporary HP.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_true_sight",
        category="beneficial",
        name="True Sight",
        description="All invisibility and illusion effects are dispelled this round.",
        xp_cost=0, severity=1,
    ),
    ArmillaryEffectDef(
        key="beneficial_mana_surge",
        category="beneficial",
        name="Mana Surge",
        description="Each spellcaster in the party recovers one 1st-level spell slot.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_coordinated_strike",
        category="beneficial",
        name="Coordinated Strike",
        description="The next attack by each party member has advantage.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_battle_hymn",
        category="beneficial",
        name="Battle Hymn",
        description="Each party member gains 1d8 temporary HP and advantage on saving throws until end of next round.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_arcane_wellspring",
        category="beneficial",
        name="Arcane Wellspring",
        description="One random spellcaster in the party recovers a 2nd-level spell slot.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_heroic_inspiration",
        category="beneficial",
        name="Heroic Inspiration",
        description="Each party member gains Inspiration (if they don't already have it).",
        xp_cost=0, severity=1,
    ),
    ArmillaryEffectDef(
        key="beneficial_sanctuary_bubble",
        category="beneficial",
        name="Sanctuary Bubble",
        description="A 10 ft radius zone of protection appears for 1 round. Creatures inside have +2 AC and advantage on saves.",
        xp_cost=0, severity=2,
    ),
    ArmillaryEffectDef(
        key="beneficial_foresight_flash",
        category="beneficial",
        name="Foresight Flash",
        description="One random party member gains advantage on all attack rolls, ability checks, and saves for 1 round.",
        xp_cost=0, severity=3,
    ),
    ArmillaryEffectDef(
        key="beneficial_radiant_dawn",
        category="beneficial",
        name="Radiant Dawn",
        description="Each party member heals 2d6 HP and one condition (blinded, frightened, or poisoned) is removed.",
        xp_cost=0, severity=2,
    ),

    # === ENVIRONMENTAL ===
    ArmillaryEffectDef(
        key="env_difficult_terrain",
        category="environmental",
        name="Shifting Ground",
        description="A 20 ft. radius area becomes difficult terrain until end of next round.",
        xp_cost=25, severity=1,
    ),
    ArmillaryEffectDef(
        key="env_darkness",
        category="environmental",
        name="Creeping Darkness",
        description="A 15 ft. radius area becomes heavily obscured until end of next round.",
        xp_cost=35, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_wind_gust",
        category="environmental",
        name="Wind Gust",
        description="All ranged attacks have disadvantage until end of next round.",
        xp_cost=30, severity=1,
    ),
    ArmillaryEffectDef(
        key="env_fire_eruption",
        category="environmental",
        name="Fire Eruption",
        description="A 10 ft. square erupts in flame. Creatures in the area take 2d6 fire damage (DEX DC 13 half).",
        xp_cost=40, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_fog_cloud",
        category="environmental",
        name="Fog Bank",
        description="A 20 ft. radius fog cloud appears (lightly obscured). Lasts 2 rounds.",
        xp_cost=20, severity=1,
    ),
    ArmillaryEffectDef(
        key="env_gravity_shift",
        category="environmental",
        name="Gravity Flux",
        description="All creatures' jump distances are doubled and falling damage is halved this round.",
        xp_cost=15, severity=1,
    ),
    ArmillaryEffectDef(
        key="env_pillar_rise",
        category="environmental",
        name="Stone Pillars",
        description="1d4 stone pillars (5 ft. wide, 10 ft. tall) erupt from the ground, providing full cover.",
        xp_cost=25, severity=1,
    ),
    ArmillaryEffectDef(
        key="env_magnetic_pull",
        category="environmental",
        name="Magnetic Pull",
        description="All metal armor wearers are pulled 10 ft. toward arena center. STR DC 13 resists.",
        xp_cost=35, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_temporal_stasis",
        category="environmental",
        name="Temporal Stasis",
        description="One random creature skips its next turn. WIS DC 14 negates.",
        xp_cost=50, severity=3, min_round=2,
    ),
    ArmillaryEffectDef(
        key="env_lava_fissure",
        category="environmental",
        name="Lava Fissure",
        description="A 5 ft. wide, 30 ft. long fissure opens in the ground. Creatures crossing it take 3d6 fire damage.",
        xp_cost=40, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_antimagic_pocket",
        category="environmental",
        name="Antimagic Pocket",
        description="A 15 ft. radius zone appears where magic does not function for 1 round.",
        xp_cost=55, severity=3, min_round=2,
    ),
    ArmillaryEffectDef(
        key="env_resonance_crystal",
        category="environmental",
        name="Resonance Crystal",
        description="A crystal appears (AC 13, 10 HP). Destroying it heals all creatures within 15 ft. for 2d6 HP.",
        xp_cost=15, severity=1,
    ),
    ArmillaryEffectDef(
        key="env_lava_flow",
        category="environmental",
        name="Lava Flow",
        description="A 5 ft wide, 40 ft long line of lava flows across the arena. Creatures starting their turn in it take 3d6 fire damage.",
        xp_cost=45, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_ice_storm",
        category="environmental",
        name="Ice Storm",
        description="A 20 ft radius area is pelted with ice. Creatures in the area take 2d6 cold damage and the ground becomes difficult terrain (DEX DC 13 half damage).",
        xp_cost=40, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_thornwall",
        category="environmental",
        name="Thornwall",
        description="A 30 ft long, 10 ft high wall of thorns bisects the arena. Moving through it costs 4x movement and deals 2d4 piercing.",
        xp_cost=35, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_fog_of_war",
        category="environmental",
        name="Fog of War",
        description="Heavy obscurement covers a 30 ft radius area for 2 rounds. All creatures inside are heavily obscured.",
        xp_cost=30, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_quicksand",
        category="environmental",
        name="Quicksand",
        description="A 15 ft radius patch becomes quicksand. Creatures entering must succeed on STR DC 14 or be restrained. Escape requires an action and STR DC 14.",
        xp_cost=40, severity=2,
    ),
    ArmillaryEffectDef(
        key="env_arcane_storm",
        category="environmental",
        name="Arcane Storm",
        description="Wild magic surges through the arena. Each spell cast this round triggers a random effect (roll on wild magic table).",
        xp_cost=35, severity=2, min_round=2,
    ),

    # === WILD (unpredictable) ===
    ArmillaryEffectDef(
        key="wild_swap_positions",
        category="wild",
        name="Dimensional Shuffle",
        description="Two random creatures (any side) swap positions.",
        xp_cost=20, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_size_change",
        category="wild",
        name="Size Flux",
        description="One random creature becomes Large (or Small if already Large) until end of next round.",
        xp_cost=25, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_gravity_reverse",
        category="wild",
        name="Gravity Reversal",
        description="All creatures must succeed on DC 12 STR save or fall 20 ft. upward, then fall back down.",
        xp_cost=45, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="wild_time_hiccup",
        category="wild",
        name="Time Hiccup",
        description="The current creature gets an extra action this turn (like Action Surge).",
        xp_cost=50, severity=3,
    ),
    ArmillaryEffectDef(
        key="wild_polymorph_burst",
        category="wild",
        name="Polymorph Burst",
        description="One random creature transforms into a sheep (1 HP) until hit or end of next round.",
        xp_cost=35, severity=2,
    ),
    ArmillaryEffectDef(
        key="wild_mirror_image",
        category="wild",
        name="Mirror Images",
        description="The current creature gains the effects of Mirror Image (3 duplicates).",
        xp_cost=30, severity=2,
    ),
    ArmillaryEffectDef(
        key="wild_element_shift",
        category="wild",
        name="Elemental Shift",
        description="All damage dealt this round changes to a random type (roll d8: 1-fire, 2-cold, 3-lightning, 4-acid, 5-thunder, 6-poison, 7-radiant, 8-necrotic).",
        xp_cost=20, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_deja_vu",
        category="wild",
        name="Deja Vu",
        description="The last Armillary effect that occurred repeats immediately.",
        xp_cost=30, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="wild_body_swap",
        category="wild",
        name="Body Swap",
        description="Two random creatures swap positions and sizes for 1 round.",
        xp_cost=30, severity=2,
    ),
    ArmillaryEffectDef(
        key="wild_miniaturize",
        category="wild",
        name="Miniaturize",
        description="One random creature becomes Tiny for 1 round (disadvantage on STR checks, advantage on DEX checks).",
        xp_cost=20, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_echo_clone",
        category="wild",
        name="Echo Clone",
        description="One random creature splits into two copies (half HP each) for 1 round.",
        xp_cost=40, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="wild_treasure_goblin",
        category="wild",
        name="Treasure Goblin",
        description="A CR 1/4 goblin carrying 50 gold appears and tries to flee. It escapes after 2 rounds.",
        xp_cost=10, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_paradox",
        category="wild",
        name="Paradox",
        description="Initiative order reverses for this round.",
        xp_cost=25, severity=2,
    ),
    ArmillaryEffectDef(
        key="wild_planar_rift",
        category="wild",
        name="Planar Rift",
        description="One random creature is banished for 1 round. CHA DC 14 negates.",
        xp_cost=50, severity=3, min_round=3,
    ),
    ArmillaryEffectDef(
        key="wild_ability_swap",
        category="wild",
        name="Ability Swap",
        description="Two random creatures swap their highest and lowest ability scores for 1 round.",
        xp_cost=25, severity=2,
    ),
    ArmillaryEffectDef(
        key="wild_size_shift",
        category="wild",
        name="Size Shift",
        description="All creatures randomly become one size larger or smaller for 1 round.",
        xp_cost=30, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_plane_shift",
        category="wild",
        name="Plane Shift",
        description="One random creature teleports to a random unoccupied space on the map.",
        xp_cost=15, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_fortunes_wheel",
        category="wild",
        name="Fortune's Wheel",
        description="Roll 1d6 for each creature: 1-2 disadvantage on next roll, 3-4 no effect, 5-6 advantage on next roll.",
        xp_cost=20, severity=1,
    ),
    ArmillaryEffectDef(
        key="wild_clone_echo",
        category="wild",
        name="Clone Echo",
        description="One random ally is duplicated for 1 round (the clone has half HP, acts on the same initiative, then vanishes).",
        xp_cost=35, severity=2, min_round=2,
    ),
    ArmillaryEffectDef(
        key="wild_chaos_bolt",
        category="wild",
        name="Chaos Bolt",
        description="A bolt of chaotic energy hits a random creature for 2d8 damage of a random type (roll d8 for type).",
        xp_cost=30, severity=2,
    ),
]


def get_effects_by_category(category: str) -> list[ArmillaryEffectDef]:
    return [e for e in ARMILLARY_EFFECTS if e.category == category]


def get_effect_by_key(key: str) -> ArmillaryEffectDef | None:
    for e in ARMILLARY_EFFECTS:
        if e.key == key:
            return e
    return None
