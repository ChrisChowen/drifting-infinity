"""Social encounter definitions for non-combat arenas.

Social encounters replace one combat arena per floor (~40% chance on
arena 1 or 2 of non-boss floors).  They use skill checks instead of
initiative and offer difficulty reduction, loot, or information.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class SkillCheck:
    skill: str
    dc_base: int          # Base DC; actual DC = dc_base + floor_scaling
    success_text: str
    failure_text: str


@dataclass
class SocialEncounterDef:
    id: str
    name: str
    description: str
    dm_prompt: str
    skill_checks: list[SkillCheck]
    success_rewards: dict = field(default_factory=dict)
    failure_consequences: dict = field(default_factory=dict)
    lore_fragment_id: str | None = None
    min_floor: int = 1
    weight: float = 1.0


# ---------------------------------------------------------------------------
# Encounter catalogue
# ---------------------------------------------------------------------------

SOCIAL_ENCOUNTERS: list[SocialEncounterDef] = [
    SocialEncounterDef(
        id="desperate_prisoner",
        name="The Desperate Prisoner",
        description="A creature imprisoned by the Armillary begs for help.",
        dm_prompt=(
            "The party enters a chamber where a cage of arcane energy holds a creature. "
            "It pleads: 'Please — I've been trapped here since the last expedition. "
            "Help me and I'll fight alongside you.' The creature seems genuine, but "
            "the Armillary has been known to set traps."
        ),
        skill_checks=[
            SkillCheck("insight", 12, "The creature is telling the truth.", "You can't read it clearly."),
            SkillCheck("persuasion", 13, "You convince it to share intel on the next arena.", "It clams up, suspicious."),
            SkillCheck("arcana", 14, "You disable the cage safely.", "The cage sparks — the Armillary notices."),
        ],
        success_rewards={"ally_for_one_arena": True, "reveal_vulnerabilities": True, "gold_bonus": 200},
        failure_consequences={"hostile_armillary_effect": True},
        lore_fragment_id="frag_prisoner_tale",
    ),
    SocialEncounterDef(
        id="broken_mechanism",
        name="The Broken Mechanism",
        description="A section of the Armillary's machinery is exposed and malfunctioning.",
        dm_prompt=(
            "Gears and crystalline conduits are exposed through a crack in the arena wall. "
            "The machinery hums erratically. A skilled hand could sabotage it to the party's "
            "advantage — or make things worse."
        ),
        skill_checks=[
            SkillCheck("arcana", 14, "You understand the mechanism's purpose.", "It's too complex."),
            SkillCheck("thieves_tools", 13, "You sabotage it — one floor affix is disabled!", "Your tools spark. The mechanism retaliates."),
            SkillCheck("athletics", 15, "You force the mechanism open, revealing a cache.", "The mechanism holds firm."),
        ],
        success_rewards={"disable_affix": True, "difficulty_reduction": 1, "gold_bonus": 300},
        failure_consequences={"affix_intensify": True},
    ),
    SocialEncounterDef(
        id="armillarys_bargain",
        name="The Armillary's Bargain",
        description="The Armillary itself offers a deal through the Arbiter's voice.",
        dm_prompt=(
            "The Arbiter's voice shifts — deeper, more resonant. 'I have a proposition,' "
            "it says. 'A sacrifice for a boon. The Armillary always honors its deals.' "
            "Present the party with a genuine choice: sacrifice something for a reward."
        ),
        skill_checks=[
            SkillCheck("insight", 12, "You sense the deal is genuine — no hidden catch.", "You're unsure if there's a catch."),
            SkillCheck("persuasion", 15, "You negotiate better terms!", "The Armillary's terms stand."),
        ],
        success_rewards={"negotiated_deal": True, "bonus_lives": 1, "gold_bonus": 500},
        failure_consequences={},  # Bargains always have a choice, never a pure loss
        lore_fragment_id="frag_armillary_honesty",
        weight=0.8,
    ),
    SocialEncounterDef(
        id="lost_explorer",
        name="The Lost Explorer",
        description="A previous challenger's ghost wanders the halls.",
        dm_prompt=(
            "A translucent figure stumbles through the arena, muttering about 'the way out.' "
            "It's the echo of a previous challenger who died in the Armillary. It can be "
            "calmed, questioned, or put to rest."
        ),
        skill_checks=[
            SkillCheck("history", 11, "You recognize the explorer from the Chronicle.", "The figure is unfamiliar."),
            SkillCheck("persuasion", 13, "You calm the ghost. It shares what it learned.", "The ghost grows agitated."),
            SkillCheck("religion", 14, "You put the spirit to rest. It leaves a gift.", "The spirit lingers, disturbed."),
        ],
        success_rewards={"gold_bonus": 250, "consumable": True, "essence_bonus": 10},
        failure_consequences={"mini_combat": True, "combat_budget_pct": 0.5},
        lore_fragment_id="frag_lost_explorer",
    ),
    SocialEncounterDef(
        id="merchants_request",
        name="The Merchant's Request",
        description="The Wandering Merchant asks for help with a personal matter.",
        dm_prompt=(
            "The Wandering Merchant approaches between arenas with an unusual request. "
            "'I need a favor,' they say, eyes darting. 'There's something in this place "
            "I need retrieved. Help me, and I'll make it worth your while.' "
            "The task involves a minor fetch/puzzle/negotiation."
        ),
        skill_checks=[
            SkillCheck("investigation", 12, "You find the item the Merchant seeks.", "You search but come up empty."),
            SkillCheck("persuasion", 13, "You negotiate a generous reward.", "The Merchant offers standard terms."),
        ],
        success_rewards={"shop_discount_pct": 5, "unique_item": True, "gold_bonus": 400},
        failure_consequences={"shop_markup_pct": 10},
        lore_fragment_id="frag_merchant_past",
        min_floor=3,
    ),
    SocialEncounterDef(
        id="arenas_memory",
        name="The Arena's Memory",
        description="A psychic echo replays a past event. Interact with the memory.",
        dm_prompt=(
            "The arena shimmers and the party sees a ghostly replay of a past event: "
            "a previous expedition's triumph or failure. The memory can be studied for "
            "tactical advantage. This encounter is always safe — there's no penalty for failure."
        ),
        skill_checks=[
            SkillCheck("arcana", 11, "You understand the tactical patterns in the memory.", "The memory is too fragmented."),
            SkillCheck("history", 12, "You identify the expedition and what they faced.", "The details are unclear."),
            SkillCheck("insight", 13, "You find hidden meaning — a clue about the arena's master.", "Nothing deeper reveals itself."),
        ],
        success_rewards={"choose_next_template": True, "gold_bonus": 150},
        failure_consequences={},  # Always safe
        lore_fragment_id="frag_arena_past",
    ),
    SocialEncounterDef(
        id="the_deserter",
        name="The Deserter",
        description="A creature that was supposed to fight the party has defected.",
        dm_prompt=(
            "A creature approaches with hands raised. 'I'm done fighting for this machine,' "
            "it says. 'I'll tell you everything about what's coming if you let me go.' "
            "The creature offers information about upcoming encounters in exchange for freedom."
        ),
        skill_checks=[
            SkillCheck("insight", 13, "The creature is genuine — it truly wants out.", "Hard to tell if this is a ruse."),
            SkillCheck("intimidation", 14, "You pressure it into revealing more.", "It's already telling you everything it knows."),
        ],
        success_rewards={"reveal_next_encounter": True, "difficulty_reduction": 1, "gold_bonus": 100},
        failure_consequences={"creature_attacks": True, "combat_budget_pct": 0.3},
        min_floor=2,
        weight=0.7,
    ),
    SocialEncounterDef(
        id="the_wager",
        name="The Wager",
        description="A voice from the arena challenges the party to a game of chance.",
        dm_prompt=(
            "The arena presents a magical game: three crystalline orbs hover in the air. "
            "Each contains a different fate. The party must choose one — and live with "
            "the consequences. This is pure choice with no skill check, but Insight can "
            "help read which orbs are favorable."
        ),
        skill_checks=[
            SkillCheck("insight", 14, "You sense which orb holds the best outcome.", "They all look the same to you."),
        ],
        success_rewards={"random_boon": True, "gold_bonus": 300},
        failure_consequences={"random_penalty": True},
        weight=0.6,
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_ENCOUNTER_INDEX: dict[str, SocialEncounterDef] = {e.id: e for e in SOCIAL_ENCOUNTERS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_social_encounter(encounter_id: str) -> SocialEncounterDef | None:
    """Return a social encounter definition by id."""
    return _ENCOUNTER_INDEX.get(encounter_id)


def select_social_encounter(
    floor_number: int,
    used_encounters: list[str] | None = None,
) -> SocialEncounterDef:
    """Select a social encounter for the given floor.

    Prefers encounters not yet used this run, filtered by min_floor.
    Uses weight-based random selection.
    """
    used = set(used_encounters or [])
    eligible = [
        e for e in SOCIAL_ENCOUNTERS
        if e.min_floor <= floor_number and e.id not in used
    ]

    if not eligible:
        # All used — allow repeats but prefer unseen
        eligible = [e for e in SOCIAL_ENCOUNTERS if e.min_floor <= floor_number]

    if not eligible:
        eligible = list(SOCIAL_ENCOUNTERS)

    weights = [e.weight for e in eligible]
    return random.choices(eligible, weights=weights, k=1)[0]


def compute_social_dc(base_dc: int, party_level: int, floor_number: int) -> int:
    """Scale a skill check DC based on progression.

    Adds +1 per 4 party levels and +1 per 5 floors (capped at +5 total).
    """
    level_bonus = party_level // 4
    floor_bonus = floor_number // 5
    return base_dc + min(5, level_bonus + floor_bonus)


def should_place_social_encounter(
    floor_number: int,
    arena_number: int,
    total_arenas: int,
    is_boss_floor: bool = False,
    social_placed_this_floor: bool = False,
) -> bool:
    """Determine if a social encounter should replace this arena.

    Rules:
    - Never on boss floors (floor 20 or designated boss floors)
    - Never on the last arena of a floor
    - Only on arena 1 or 2
    - Max 1 social encounter per floor
    - 40% base chance
    """
    if is_boss_floor:
        return False
    if arena_number > 2:
        return False
    if arena_number >= total_arenas:
        return False
    if social_placed_this_floor:
        return False
    return random.random() < 0.40
