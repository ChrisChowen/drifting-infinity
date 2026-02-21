"""Secret floor and rare event definitions.

Memorable surprises that break the pattern: treasure rooms, ghostly
replays, super-shops, meta-challenges, bonus bosses, and loot goblins.
Follows the floor_affixes.py pattern: dataclass catalog + index + helpers.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class SecretEventDef:
    id: str
    name: str
    description: str
    dm_instructions: str
    trigger_type: str           # "floor_transition", "arena_mid", "post_deaths", "conditional"
    trigger_chance: float       # 0.0-1.0
    min_floor: int = 1
    min_runs: int = 0           # Minimum campaign runs to unlock
    content_type: str = "special"  # "treasure", "combat", "shop", "puzzle", "mixed"
    rewards: dict = field(default_factory=dict)
    lore_fragment_id: str | None = None
    is_floor_event: bool = True  # True = replaces a floor, False = occurs within an arena


# ---------------------------------------------------------------------------
# Event catalogue
# ---------------------------------------------------------------------------

SECRET_EVENTS: list[SecretEventDef] = [
    SecretEventDef(
        id="shattered_vault",
        name="The Shattered Vault",
        description="A hidden treasure room — trapped chests guard riches beyond imagination.",
        dm_instructions=(
            "The party discovers a crumbling chamber filled with crystalline chests. "
            "Each chest requires a DC 14 Thieves' Tools or Arcana check to open safely. "
            "Failure triggers a trap (2d6 damage). The largest chest is actually a Mimic "
            "(use CR appropriate to party level). Award 3-5x normal floor gold on success."
        ),
        trigger_type="floor_transition",
        trigger_chance=0.05,
        min_floor=3,
        content_type="treasure",
        rewards={"gold_multiplier": 4, "guaranteed_gacha_pull": True, "bonus_shards": 5},
        lore_fragment_id="frag_vault_origin",
    ),
    SecretEventDef(
        id="crucible_of_echoes",
        name="The Crucible of Echoes",
        description="Ghostly versions of fallen party members test the living.",
        dm_instructions=(
            "Spectral copies of characters who died during this run appear. They use "
            "the same class abilities and stats as the originals at time of death. "
            "This is non-lethal combat — defeated echoes dissipate and grant insight. "
            "Award +1 life and an essence bonus on victory."
        ),
        trigger_type="post_deaths",
        trigger_chance=0.03,
        min_floor=2,
        content_type="combat",
        rewards={"bonus_life": 1, "essence_bonus": 25, "lore_fragment": True},
        lore_fragment_id="frag_echoes_truth",
    ),
    SecretEventDef(
        id="merchants_sanctum",
        name="The Merchant's Sanctum",
        description="The Wandering Merchant reveals a hidden chamber of legendary wares.",
        dm_instructions=(
            "The Wandering Merchant beckons the party through a hidden door. Inside: "
            "legendary items normally unavailable, at 2x standard price. The Merchant "
            "drops cryptic hints about the Armillary's true nature. Include 2-3 items "
            "one tier above what the shop normally offers."
        ),
        trigger_type="floor_transition",
        trigger_chance=0.08,
        min_floor=2,
        content_type="shop",
        rewards={"shop_tier_bonus": 1, "unique_consumables": 2},
        lore_fragment_id="frag_merchant_secret",
    ),
    SecretEventDef(
        id="arbiters_trial",
        name="The Arbiter's Trial",
        description="The Arbiter poses three riddles — solve them for great reward.",
        dm_instructions=(
            "The arena goes silent. The Arbiter's voice echoes with unusual clarity: "
            "'I have a test of my own.' Present 3 riddles or logic puzzles to the party. "
            "Each solved riddle earns a reward. All 3 = massive bonus. Riddles should "
            "reference Armillary lore and the nature of the arena."
        ),
        trigger_type="floor_transition",
        trigger_chance=0.02,
        min_floor=5,
        min_runs=5,
        content_type="puzzle",
        rewards={"essence_per_riddle": 50, "max_essence": 150, "title": "Riddlemaster"},
        lore_fragment_id="frag_arbiter_truth",
    ),
    SecretEventDef(
        id="the_rift",
        name="The Rift",
        description="A portal tears open — something from OUTSIDE the Armillary enters.",
        dm_instructions=(
            "Reality cracks. A creature not from the Armillary's catalogue appears — "
            "it doesn't follow the arena's rules (immune to Armillary effects, ignores "
            "floor affixes). Use a CR appropriate to party + 2 levels. This creature "
            "should feel alien and wrong. On defeat, it drops a rare item and a major "
            "lore fragment about the entity behind the Armillary."
        ),
        trigger_type="arena_mid",
        trigger_chance=0.01,
        min_floor=15,
        content_type="combat",
        rewards={"xp_multiplier": 2.0, "rare_gacha_item": True},
        lore_fragment_id="frag_beyond_armillary",
        is_floor_event=False,
    ),
    SecretEventDef(
        id="the_collector",
        name="The Collector",
        description="A strange fey creature appears — kill it before it escapes!",
        dm_instructions=(
            "A small, chittering fey creature materializes mid-combat, clutching "
            "a sack of treasures. It has high AC (16 + party_level // 4), low HP "
            "(20 + party_level * 2), and uses its action to Dash toward the exit. "
            "It flees after 3 rounds. If killed: excellent loot. If it escapes: nothing. "
            "The creature cackles and taunts as it runs."
        ),
        trigger_type="arena_mid",
        trigger_chance=0.10,
        min_floor=1,
        content_type="mixed",
        rewards={"gold_multiplier": 5, "bonus_shards": 3, "rare_consumable_chance": 0.5},
        is_floor_event=False,
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_EVENT_INDEX: dict[str, SecretEventDef] = {e.id: e for e in SECRET_EVENTS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_secret_event(event_id: str) -> SecretEventDef | None:
    """Return a secret event definition by id."""
    return _EVENT_INDEX.get(event_id)


def check_secret_event_triggers(
    floor_number: int,
    arena_number: int,
    run_stats: dict,
    campaign_runs_completed: int = 0,
    trigger_type: str = "floor_transition",
) -> SecretEventDef | None:
    """Check if a secret event should trigger at this point.

    Args:
        floor_number: Current floor number.
        arena_number: Current arena number (for arena_mid triggers).
        run_stats: Dict with keys like total_deaths, floors_completed, etc.
        campaign_runs_completed: Total runs the campaign has completed.
        trigger_type: Which trigger phase we're checking.

    Returns:
        A SecretEventDef if one triggers, or None.
    """
    # Gather eligible events for this trigger type
    eligible = [
        e for e in SECRET_EVENTS
        if e.trigger_type == trigger_type
        and e.min_floor <= floor_number
        and e.min_runs <= campaign_runs_completed
    ]

    # Special condition: Crucible of Echoes only after 2+ deaths
    if trigger_type == "post_deaths":
        if run_stats.get("total_deaths", 0) < 2:
            eligible = [e for e in eligible if e.id != "crucible_of_echoes"]

    # Roll for each eligible event (first hit wins)
    for event in eligible:
        if random.random() < event.trigger_chance:
            return event

    return None


def roll_collector_spawn(arena_number: int, floor_number: int) -> bool:
    """Roll to see if The Collector spawns in this arena.

    The Collector has a 10% base chance, slightly higher on deeper floors.
    """
    base_chance = 0.10
    floor_bonus = min(0.05, floor_number * 0.002)
    return random.random() < (base_chance + floor_bonus)
