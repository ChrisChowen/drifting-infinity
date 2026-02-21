"""Floor affix definitions for the Armillary's procedural floor modifiers.

Each affix modifies a floor's encounters, environment, Armillary behaviour,
or economy.  Affixes are rolled when a floor is generated and may stack
across floors (creature buffs compound as the party descends).

Categories:
- creature_buff : stat boosts applied to all arena creatures on the floor
- environment   : arena layout / hazard modifiers
- armillary     : tweaks to Armillary activation and severity
- economy       : gold, shard, XP, and shop-price modifiers
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class FloorAffixDef:
    id: str
    name: str
    category: str  # "creature_buff", "environment", "armillary", "economy"
    description: str
    flavor_text: str
    stacks: bool = True
    modifier: dict = field(default_factory=dict)
    min_floor: int = 1
    weight: float = 1.0


# ---------------------------------------------------------------------------
# Affix catalogue
# ---------------------------------------------------------------------------

FLOOR_AFFIXES: list[FloorAffixDef] = [
    # === CREATURE BUFFS (stack across floors) ===
    FloorAffixDef(
        id="fortified",
        name="Fortified",
        category="creature_buff",
        description="+10% HP to all creatures on this floor.",
        flavor_text="The Armillary reinforces its champions.",
        modifier={"hp_percent": 10, "attack_bonus": 0},
    ),
    FloorAffixDef(
        id="emboldened",
        name="Emboldened",
        category="creature_buff",
        description="+1 to attack rolls for all creatures on this floor.",
        flavor_text="The arena emboldens its defenders.",
        modifier={"attack_bonus": 1},
    ),
    FloorAffixDef(
        id="empowered",
        name="Empowered",
        category="creature_buff",
        description="+1 damage per hit for all creatures on this floor.",
        flavor_text="The Armillary channels power into its creatures.",
        modifier={"damage_bonus": 1},
    ),
    FloorAffixDef(
        id="quickened",
        name="Quickened",
        category="creature_buff",
        description="+10 ft speed for all creatures on this floor.",
        flavor_text="The arena accelerates its denizens.",
        modifier={"speed": 10},
    ),
    FloorAffixDef(
        id="resolute",
        name="Resolute",
        category="creature_buff",
        description="Creatures gain advantage on saves vs one condition (random: frightened, charmed, or stunned).",
        flavor_text="The Armillary steels its warriors' minds.",
        modifier={"save_advantage_condition": "random"},
    ),
    FloorAffixDef(
        id="armored",
        name="Armored",
        category="creature_buff",
        description="+1 AC to all creatures on this floor.",
        flavor_text="Arcane plating manifests on the arena's creatures.",
        modifier={"ac_bonus": 1},
    ),
    FloorAffixDef(
        id="regenerating",
        name="Regenerating",
        category="creature_buff",
        description="Creatures regain 2 HP at the start of their turn.",
        flavor_text="The Armillary sustains its champions.",
        modifier={"regen_hp": 2},
    ),

    # === ENVIRONMENT ===
    FloorAffixDef(
        id="dim_light",
        name="Dim Light",
        category="environment",
        description="Dim light throughout the arena. Disadvantage on Perception checks relying on sight.",
        flavor_text="Shadows gather in the Armillary's depths.",
        stacks=False,
        modifier={"light_level": "dim", "perception_sight_disadvantage": True},
    ),
    FloorAffixDef(
        id="difficult_terrain",
        name="Difficult Terrain",
        category="environment",
        description="25% of the arena is difficult terrain.",
        flavor_text="The arena floor shifts and buckles.",
        stacks=False,
        modifier={"difficult_terrain_percent": 25},
    ),
    FloorAffixDef(
        id="hazard_zones",
        name="Hazard Zones",
        category="environment",
        description="2 hazard zones (10 ft radius) that deal 1d6 damage to creatures entering.",
        flavor_text="The Armillary's defenses activate.",
        stacks=False,
        modifier={"hazard_count": 2, "hazard_radius_ft": 10, "hazard_damage": "1d6"},
    ),
    FloorAffixDef(
        id="antimagic_pockets",
        name="Antimagic Pockets",
        category="environment",
        description="1-2 antimagic zones (10 ft radius) where magic does not function.",
        flavor_text="The Armillary dampens the weave.",
        stacks=False,
        modifier={"antimagic_zones": 2, "zone_radius_ft": 10},
        min_floor=2,
    ),
    FloorAffixDef(
        id="wind_tunnels",
        name="Wind Tunnels",
        category="environment",
        description="Strong winds in corridors; ranged attacks have disadvantage in affected areas.",
        flavor_text="Gales howl through the arena's passages.",
        stacks=False,
        modifier={"ranged_disadvantage_zones": True},
    ),
    FloorAffixDef(
        id="shifting_walls",
        name="Shifting Walls",
        category="environment",
        description="Arena layout changes every 3 rounds.",
        flavor_text="The Armillary reshapes itself.",
        stacks=False,
        modifier={"layout_shift_rounds": 3},
        min_floor=2,
    ),

    # === ARMILLARY ===
    FloorAffixDef(
        id="volatile_favour",
        name="Volatile Favour",
        category="armillary",
        description="+1 to hostile Armillary effect selection weight on this floor.",
        flavor_text="The Armillary's mood darkens.",
        stacks=True,
        modifier={"hostile_weight_bonus": 1},
    ),
    FloorAffixDef(
        id="hyperactive",
        name="Hyperactive",
        category="armillary",
        description="One extra Armillary activation per arena on this floor.",
        flavor_text="The Armillary asserts its dominance.",
        stacks=True,
        modifier={"extra_activations": 1},
    ),
    FloorAffixDef(
        id="favour_drain",
        name="Favour Drain",
        category="armillary",
        description="Lose 1 Armillary Favour per arena completed on this floor.",
        flavor_text="The Armillary feeds on your success.",
        stacks=True,
        modifier={"favour_loss_per_arena": 1},
    ),
    FloorAffixDef(
        id="empowered_effects",
        name="Empowered Effects",
        category="armillary",
        description="Armillary effects have +50% severity (e.g., damage dice increase).",
        flavor_text="The arena's interventions intensify.",
        stacks=False,
        modifier={"severity_multiplier": 1.5},
        min_floor=2,
    ),
    FloorAffixDef(
        id="cascading_effects",
        name="Cascading Effects",
        category="armillary",
        description="Each Armillary effect has a 25% chance to trigger a second effect.",
        flavor_text="The arena's magic becomes unstable.",
        stacks=False,
        modifier={"cascade_chance": 0.25},
        min_floor=3,
    ),

    # === ECONOMY ===
    FloorAffixDef(
        id="golden_floor",
        name="Golden Floor",
        category="economy",
        description="+25% gold rewards on this floor.",
        flavor_text="Gold seeps from the Armillary's walls.",
        stacks=True,
        modifier={"gold_percent": 25},
    ),
    FloorAffixDef(
        id="shard_resonance",
        name="Shard Resonance",
        category="economy",
        description="+1 bonus Astral Shard per arena on this floor.",
        flavor_text="The planes align, amplifying shard resonance.",
        stacks=True,
        modifier={"bonus_shards": 1},
    ),
    FloorAffixDef(
        id="merchant_favour",
        name="Merchant's Favour",
        category="economy",
        description="Shop prices are reduced by 15% on this floor.",
        flavor_text="The Wandering Merchant takes a liking to you.",
        stacks=False,
        modifier={"shop_price_percent": -15},
    ),
    FloorAffixDef(
        id="merchant_markup",
        name="Merchant's Markup",
        category="economy",
        description="Shop prices are increased by 20% on this floor.",
        flavor_text="The Wandering Merchant senses your desperation.",
        stacks=False,
        modifier={"shop_price_percent": 20},
    ),
    FloorAffixDef(
        id="bounty_hunter",
        name="Bounty Hunter",
        category="economy",
        description="+50% XP from creatures on this floor.",
        flavor_text="The Armillary values the data from this floor.",
        stacks=True,
        modifier={"xp_percent": 50},
    ),

    # === NEW CREATURE BUFFS ===
    FloorAffixDef(
        id="relentless",
        name="Relentless",
        category="creature_buff",
        description="Creatures keep fighting at 0 HP for 1 round before dying.",
        flavor_text="Death comes slowly in the Armillary's embrace.",
        stacks=False,
        modifier={"undying_rounds": 1},
        min_floor=2,
        weight=0.8,
    ),
    FloorAffixDef(
        id="spellguard",
        name="Spellguard",
        category="creature_buff",
        description="Creatures have advantage on saving throws against spells.",
        flavor_text="The weave bends to shield the arena's champions.",
        stacks=False,
        modifier={"spell_save_advantage": True},
        min_floor=2,
        weight=0.8,
    ),
    FloorAffixDef(
        id="pack_tactics",
        name="Pack Tactics",
        category="creature_buff",
        description="Creatures gain advantage on attack rolls when an ally is within 5 ft of the target.",
        flavor_text="The Armillary teaches its creatures to hunt in packs.",
        stacks=False,
        modifier={"pack_tactics": True},
        min_floor=1,
        weight=0.9,
    ),

    # === NEW ENVIRONMENT ===
    FloorAffixDef(
        id="magical_darkness",
        name="Magical Darkness",
        category="environment",
        description="Magical darkness fills select zones. Darkvision does not function in these areas.",
        flavor_text="A deeper darkness settles over the arena.",
        stacks=False,
        modifier={"magical_darkness_zones": 2, "darkvision_blocked": True},
        min_floor=2,
        weight=0.7,
    ),
    FloorAffixDef(
        id="gravity_wells",
        name="Gravity Wells",
        category="environment",
        description="Two zones of intense gravity pull creatures 10 ft toward their center at initiative count 20.",
        flavor_text="The laws of nature bend at the Armillary's whim.",
        stacks=False,
        modifier={"gravity_well_count": 2, "pull_distance_ft": 10},
        min_floor=2,
        weight=0.8,
    ),
    FloorAffixDef(
        id="temporal_flux",
        name="Temporal Flux",
        category="environment",
        description="Initiative is rerolled at the start of each round.",
        flavor_text="Time stutters and skips within the arena.",
        stacks=False,
        modifier={"reroll_initiative_each_round": True},
        min_floor=3,
        weight=0.6,
    ),
    FloorAffixDef(
        id="ley_line_surges",
        name="Ley Line Surges",
        category="environment",
        description="Spells deal an extra 1d4 force damage when cast within ley line zones.",
        flavor_text="Raw magical energy courses through the arena floor.",
        stacks=False,
        modifier={"spell_bonus_damage": "1d4", "damage_type": "force"},
        min_floor=2,
        weight=0.8,
    ),

    # === NEW ARMILLARY ===
    FloorAffixDef(
        id="armillary_wrath",
        name="Armillary's Wrath",
        category="armillary",
        description="Hostile Armillary effects trigger twice as often.",
        flavor_text="The Armillary's patience has run out.",
        stacks=False,
        modifier={"hostile_frequency_multiplier": 2.0},
        min_floor=3,
        weight=0.6,
    ),
    FloorAffixDef(
        id="armillary_mercy",
        name="Armillary's Mercy",
        category="armillary",
        description="Beneficial Armillary effects trigger twice as often.",
        flavor_text="The Armillary shows unexpected kindness.",
        stacks=False,
        modifier={"beneficial_frequency_multiplier": 2.0},
        min_floor=2,
        weight=0.7,
    ),

    # === NEW ECONOMY ===
    FloorAffixDef(
        id="treasure_trove",
        name="Treasure Trove",
        category="economy",
        description="Each arena has a 50% chance to drop an additional consumable reward.",
        flavor_text="The arena's vaults spill open.",
        stacks=False,
        modifier={"bonus_consumable_chance": 0.5},
        min_floor=2,
        weight=0.8,
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_AFFIX_INDEX: dict[str, FloorAffixDef] = {a.id: a for a in FLOOR_AFFIXES}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_affix(affix_id: str) -> FloorAffixDef | None:
    """Return a single affix definition by *id*, or ``None``."""
    return _AFFIX_INDEX.get(affix_id)


def get_affixes_for_floor(floor_number: int) -> list[FloorAffixDef]:
    """Return every affix whose *min_floor* allows it on *floor_number*."""
    return [a for a in FLOOR_AFFIXES if a.min_floor <= floor_number]


def roll_affixes(
    floor_number: int,
    existing_affixes: list[str] | None = None,
) -> list[FloorAffixDef]:
    """Select random affixes for a new floor.

    Rules
    -----
    - Floor 1       : 1 affix
    - Floors 2-3    : 1-2 affixes
    - Floor 4+      : 2 affixes
    - Affixes whose *id* is already in *existing_affixes* (from prior floors)
      are excluded from the pool so the same affix is not rolled twice in a
      single run.
    - Selection uses weight-based random sampling.
    """
    existing: set[str] = set(existing_affixes) if existing_affixes else set()

    pool = [
        a for a in get_affixes_for_floor(floor_number)
        if a.id not in existing
    ]

    if not pool:
        return []

    # Determine how many affixes to roll.
    if floor_number <= 1:
        count = 1
    elif floor_number <= 3:
        count = random.randint(1, 2)
    else:
        count = 2

    count = min(count, len(pool))

    weights = [a.weight for a in pool]
    selected: list[FloorAffixDef] = []

    for _ in range(count):
        if not pool:
            break
        chosen = random.choices(pool, weights=weights, k=1)[0]
        selected.append(chosen)
        # Remove chosen from pool to avoid duplicates within the same floor.
        idx = pool.index(chosen)
        pool.pop(idx)
        weights.pop(idx)

    return selected
