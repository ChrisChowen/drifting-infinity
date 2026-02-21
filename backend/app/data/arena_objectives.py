"""Arena objective definitions for the Armillary encounter system.

Each objective defines a win/fail condition set, DM instructions,
and selection parameters that control when and how the objective
appears across arena floors.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class ArenaObjectiveDef:
    id: str
    name: str
    category: str  # "combat", "tactical", or "exploration"
    description: str  # Read-aloud text for players
    dm_instructions: str  # DM-facing tactical instructions
    win_conditions: list[str]
    fail_conditions: list[str]
    bonus_rewards: dict  # e.g. {"gold_multiplier": 1.25, "bonus_shard": 1}
    min_floor: int = 1
    weight: float = 1.0
    special_rules: list[str] = field(default_factory=list)
    compatible_templates: list[str] | None = None  # None = all templates


# ---------------------------------------------------------------------------
# Objective catalogue
# ---------------------------------------------------------------------------

ARENA_OBJECTIVES: list[ArenaObjectiveDef] = [
    # -- COMBAT ---------------------------------------------------------------
    ArenaObjectiveDef(
        id="extermination",
        name="Extermination",
        category="combat",
        description=(
            "The Armillary's voice rumbles through the stone beneath your feet: "
            "\"No mercy shall be granted. Destroy every creature I have called "
            "forth, or be destroyed in turn.\" The arena walls pulse with a dull "
            "crimson light as hostile forms materialise around you."
        ),
        dm_instructions=(
            "Standard combat encounter. All hostile creatures must be reduced "
            "to 0 HP for the party to succeed. No special setup required."
        ),
        win_conditions=["All hostile creatures reduced to 0 HP"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={},
        min_floor=1,
        weight=2.0,
        special_rules=[],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="destruction",
        name="Destruction",
        category="combat",
        description=(
            "A crystalline nexus descends from the vaulted ceiling, thrumming "
            "with unstable energy. The Armillary speaks in a strained harmonic: "
            "\"One of my own anchors has grown corrupt. Shatter the Nexus before "
            "its guardians overwhelm you—but know that it will not break "
            "easily.\" Arcane sentinels flicker into existence around the pulsing "
            "structure, weapons already raised."
        ),
        dm_instructions=(
            "Place an Armillary Nexus object on the map (AC 15, HP = 40 + 10 * "
            "floor_number). The Nexus has resistance to all damage types. "
            "Guardian creatures protect it and gain +2 to attack rolls while the "
            "Nexus is intact. The Nexus emits a harmful energy pulse (2d6 force "
            "damage, DC 13 CON save for half) to all creatures within 20 ft at "
            "the end of every 3rd round."
        ),
        win_conditions=["Armillary Nexus reduced to 0 HP"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.3, "bonus_shard": 2},
        min_floor=3,
        weight=0.8,
        special_rules=[
            "Nexus: AC 15, resistance to all damage, HP scales with floor",
            "Guardians gain +2 attack while Nexus lives",
            "Nexus emits a harmful pulse every 3 rounds",
        ],
        compatible_templates=["boss_and_minions", "focus_fire"],
    ),
    ArenaObjectiveDef(
        id="gauntlet",
        name="Gauntlet",
        category="combat",
        description=(
            "The Armillary's tone turns cold and relentless: \"You will face "
            "wave after wave with no quarter given. Each foe you fell only "
            "heralds the next. Endure—or be ground to nothing.\" A war horn "
            "sounds from somewhere beyond the arena walls, and the first rank "
            "of enemies charges through the gates."
        ),
        dm_instructions=(
            "Generate N waves of enemies (2 waves on floor 3, 3 waves on "
            "floor 4+). Each wave enters combat when the previous wave is fully "
            "defeated. No short rest is permitted between waves. Each wave's XP "
            "budget is 60% of the normal encounter budget."
        ),
        win_conditions=["All waves defeated"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.25, "bonus_shard": 1},
        min_floor=3,
        weight=0.7,
        special_rules=[
            "Wave count: 2 on floor 3, 3 on floor 4+",
            "Each wave's XP budget is 60% of normal",
            "No rest between waves",
        ],
        compatible_templates=["hold_and_flank", "swarm", "skirmish"],
    ),

    # -- TACTICAL -------------------------------------------------------------
    ArenaObjectiveDef(
        id="survival",
        name="Survival",
        category="tactical",
        description=(
            "The Armillary's voice reverberates with grim amusement: \"Let us "
            "test your resilience. I shall unleash wave upon wave—survive long "
            "enough and you earn your passage. Fall, and the stones will "
            "swallow what remains.\" Runes ignite along the arena floor, "
            "counting down to the first surge."
        ),
        dm_instructions=(
            "The party must survive a specified number of rounds (typically "
            "3 + floor_number). Reinforcement creatures arrive at the start of "
            "each round at initiative count 20. Track the round count openly. "
            "All surviving enemies despawn once the required rounds are "
            "completed."
        ),
        win_conditions=["Party survives the specified number of rounds"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.15},
        min_floor=1,
        weight=1.0,
        special_rules=[
            "Reinforcements arrive at initiative count 20 each round",
            "Surviving creatures despawn when rounds complete",
        ],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="protection",
        name="Protection",
        category="tactical",
        description=(
            "A pillar of pale light erupts from the arena floor, and within it "
            "floats a delicate Ward Crystal, rotating slowly. The Armillary's "
            "voice softens to an urgent whisper: \"This crystal sustains the "
            "barrier between floors. Guard it with your lives—the creatures I "
            "summon will seek its destruction above all else.\""
        ),
        dm_instructions=(
            "Place a Ward Crystal on the map (AC 10, HP = 20 + 5 * "
            "floor_number). At least one enemy each round must use its turn to "
            "attack the Ward Crystal if it can reach it. The party wins if the "
            "Ward Crystal still stands when all hostile creatures are defeated."
        ),
        win_conditions=["Ward Crystal survives the encounter"],
        fail_conditions=[
            "Ward Crystal reduced to 0 HP",
            "All party members reduced to 0 HP",
        ],
        bonus_rewards={"gold_multiplier": 1.2, "bonus_shard": 1},
        min_floor=2,
        weight=1.0,
        special_rules=[
            "Ward Crystal: AC 10, HP varies by floor",
            "At least one enemy targets the Ward each round",
        ],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="king_of_the_hill",
        name="King of the Hill",
        category="tactical",
        description=(
            "The centre of the arena blazes with a ring of golden sigils. The "
            "Armillary commands: \"Claim the Crucible—stand upon it, hold it "
            "against all challengers, and prove your dominion. Cede it, and you "
            "cede everything.\" Enemies close in from every direction, intent "
            "on driving you from the circle."
        ),
        dm_instructions=(
            "Mark a 15 ft radius zone in the centre of the arena. Track how "
            "many rounds the majority of living party members occupy the zone. "
            "The party needs a cumulative number of qualifying rounds (typically "
            "2 + floor_number // 2) to win. Enemies should actively try to "
            "push or lure party members out of the zone."
        ),
        win_conditions=[
            "Party holds the central zone for the required number of rounds",
        ],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.2},
        min_floor=2,
        weight=0.8,
        special_rules=[
            "Central zone: 15 ft radius",
            "Party must have majority of living members in zone to count a round",
            "Required rounds scale with floor",
        ],
        compatible_templates=None,
    ),

    # -- EXPLORATION ----------------------------------------------------------
    ArenaObjectiveDef(
        id="activation",
        name="Activation",
        category="exploration",
        description=(
            "Slender arcane pillars rise from hidden recesses in the arena "
            "floor, each capped with a dormant runestone. The Armillary "
            "intones: \"These conduits have fallen silent. Rekindle every one "
            "and the path forward opens. Fail, and the silence becomes your "
            "tomb.\" Hostile creatures stalk the spaces between the pillars, "
            "eager to keep you from your task."
        ),
        dm_instructions=(
            "Place N arcane pillars around the arena (N = party_size - 1, "
            "minimum 2). A character can activate a pillar by spending an "
            "action while within 5 ft of it. Activated pillars glow and no "
            "longer require attention. The encounter ends in victory when all "
            "pillars are activated and all hostile creatures are defeated."
        ),
        win_conditions=["All arcane pillars activated"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.1},
        min_floor=2,
        weight=1.0,
        special_rules=[
            "Activating a pillar requires an action within 5 ft",
            "Pillar count scales with party size",
        ],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="extraction",
        name="Extraction",
        category="exploration",
        description=(
            "Shards of crystallised memory litter the arena, each pulsing with "
            "a faint inner light. The Armillary's voice carries an edge of "
            "urgency: \"Gather every relic before the arena's foundation "
            "gives way. Anything left behind will be lost to the Drift "
            "forever.\" The ground trembles faintly—a reminder that time is "
            "not on your side."
        ),
        dm_instructions=(
            "Place N relics around the arena (N = party_size, minimum 2). "
            "Collecting a relic requires an action within 5 ft. All relics "
            "must be collected AND all hostile creatures defeated for victory. "
            "IMPORTANT: if the last creature is killed before all relics are "
            "collected, the remaining relics shatter and the objective fails."
        ),
        win_conditions=[
            "All relics collected AND all hostile creatures defeated",
        ],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.15, "bonus_shard": 1},
        min_floor=2,
        weight=0.8,
        special_rules=[
            "Collecting a relic requires an action within 5 ft",
            "If last creature dies before all relics collected, remaining relics shatter",
        ],
        compatible_templates=None,
    ),

    # -- TACTICAL (continued) -------------------------------------------------
    ArenaObjectiveDef(
        id="ritual_disruption",
        name="Ritual Disruption",
        category="tactical",
        description=(
            "The Armillary reveals dark rituals being performed at glowing "
            "circles etched into the arena floor. Shadowy figures chant in "
            "unison, their voices rising with each passing heartbeat. "
            "Interrupt every ritual before they reach completion—or face "
            "whatever horrors they intend to unleash."
        ),
        dm_instructions=(
            "Place N ritual circles around the arena (N = 2 + floor_number "
            "// 2). Each ritual completes after 3 rounds if not disrupted. "
            "A character within 5 ft of a circle can use an action to disrupt "
            "it, permanently deactivating that circle. If any ritual "
            "completes, it immediately summons a CR-appropriate creature."
        ),
        win_conditions=["All rituals disrupted before completion"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.2, "bonus_shard": 1},
        min_floor=2,
        weight=0.9,
        special_rules=[
            "Ritual circle count: 2 + floor_number // 2",
            "Each ritual completes after 3 undisrupted rounds",
            "Disrupting requires an action within 5 ft",
            "Completed ritual summons a CR-appropriate creature",
        ],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="escort",
        name="Escort",
        category="tactical",
        description=(
            "A wounded spirit of the Armillary flickers into view—translucent, "
            "fragile, and desperate. Its voice is barely a whisper: \"I must "
            "reach the far gate, or the path forward dies with me.\" Hostile "
            "creatures turn their attention toward the spirit with predatory "
            "intent. Protect it, or lose the way onward."
        ),
        dm_instructions=(
            "Place an NPC spirit at one edge of the arena (AC 10, HP = 15 + "
            "5 * floor_number, speed 20 ft). The NPC moves toward a marked "
            "exit point on the opposite side each round. Enemies prioritise "
            "attacking the NPC when they can reach it. The party wins when "
            "the NPC reaches the exit alive."
        ),
        win_conditions=["NPC reaches the exit alive"],
        fail_conditions=[
            "NPC reduced to 0 HP",
            "All party members reduced to 0 HP",
        ],
        bonus_rewards={"gold_multiplier": 1.25, "bonus_shard": 1},
        min_floor=2,
        weight=0.8,
        special_rules=[
            "NPC spirit: AC 10, HP scales with floor, speed 20 ft",
            "NPC moves toward exit each round",
            "Enemies prioritise attacking the NPC",
        ],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="relic_defense",
        name="Relic Defense",
        category="tactical",
        description=(
            "The Armillary's voice rings with alarm: \"They have stolen "
            "fragments of my memory—relics that bind my floors together. "
            "Stop the thieves before they escape through the exit portals, "
            "or the Drift will unravel around you.\""
        ),
        dm_instructions=(
            "Place 2-3 exit portals at the edges of the arena. N creatures "
            "(N = party_size) each carry a relic and move toward the nearest "
            "portal at their full speed each round. If a relic-carrier "
            "reaches a portal, that relic is lost. A creature drops its relic "
            "when reduced to 0 HP; a character can pick it up with a free "
            "action. The party wins if they recover at least half the relics."
        ),
        win_conditions=["At least half of relics recovered"],
        fail_conditions=[
            "More than half of relics escape through portals",
            "All party members reduced to 0 HP",
        ],
        bonus_rewards={"gold_multiplier": 1.2, "bonus_shard": 1},
        min_floor=3,
        weight=0.7,
        special_rules=[
            "2-3 exit portals at arena edges",
            "Relic-carriers flee toward nearest portal each round",
            "Dropped relics can be picked up with a free action",
            "Party must recover at least half the relics to win",
        ],
        compatible_templates=None,
    ),

    # -- COMBAT (continued) ---------------------------------------------------
    ArenaObjectiveDef(
        id="arena_champion",
        name="Arena Champion",
        category="combat",
        description=(
            "The Armillary's voice booms with theatrical grandeur: \"One among "
            "you must prove worthy in single combat! Step into the Crucible "
            "and face my champion—while the rest contend with lesser trials "
            "beyond the ring.\" A circle of blazing runes carves itself into "
            "the arena floor, and the largest creature stalks into its centre."
        ),
        dm_instructions=(
            "The highest CR creature starts in a central ring (15 ft radius). "
            "One party member enters the ring for a 1v1 duel. Other party "
            "members face remaining creatures outside the ring. If the chosen "
            "champion falls to 0 HP, another party member may step into the "
            "ring to continue the duel. Victory requires defeating the arena "
            "champion (highest CR creature)."
        ),
        win_conditions=["Arena champion (highest CR creature) defeated"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.35, "bonus_shard": 2},
        min_floor=3,
        weight=0.6,
        special_rules=[
            "Central duel ring: 15 ft radius",
            "One party member enters the ring for 1v1",
            "If champion falls, another party member may step in",
            "Remaining creatures fight outside the ring",
        ],
        compatible_templates=["boss", "elite_duel"],
    ),
    ArenaObjectiveDef(
        id="timed_assault",
        name="Timed Assault",
        category="combat",
        description=(
            "An hourglass of shimmering sand materialises above the arena, "
            "its grains already falling. The Armillary's voice carries cold "
            "urgency: \"Destroy them all before the sands run out—or the "
            "Drift will empower what remains beyond your ability to survive.\""
        ),
        dm_instructions=(
            "The party has N rounds (N = 4 + floor_number) to defeat all "
            "enemies. Track the round count openly for all players. If the "
            "time limit expires, all remaining enemies immediately gain +2 "
            "to attack rolls, +2 to damage rolls, and resistance to all "
            "damage types for the remainder of the encounter."
        ),
        win_conditions=["All enemies defeated within the time limit"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.2},
        min_floor=2,
        weight=0.9,
        special_rules=[
            "Time limit: 4 + floor_number rounds",
            "Track round count openly",
            "On expiry: remaining enemies gain +2 attack, +2 damage, resistance to all",
        ],
        compatible_templates=None,
    ),

    # -- EXPLORATION (continued) -----------------------------------------------
    ArenaObjectiveDef(
        id="capture",
        name="Capture",
        category="exploration",
        description=(
            "The Armillary's voice takes on a curious, almost hungry tone: "
            "\"One creature among them carries a spark I require. Bring it "
            "to me alive—kill it, and the spark is extinguished forever.\" "
            "A faint shimmer outlines one of the hostile creatures, marking "
            "it as the target."
        ),
        dm_instructions=(
            "Mark one creature as the capture target (highlighted with a "
            "visible shimmer). The target must be reduced to 0 HP using "
            "nonlethal damage only (melee attacks can be declared nonlethal). "
            "If the target is killed by lethal damage the objective fails "
            "immediately. All other hostile creatures can be killed normally. "
            "Victory requires the target to be captured (nonlethal KO) and "
            "all remaining hostiles defeated."
        ),
        win_conditions=[
            "Target captured via nonlethal KO AND all other hostiles defeated",
        ],
        fail_conditions=[
            "Capture target killed by lethal damage",
            "All party members reduced to 0 HP",
        ],
        bonus_rewards={"gold_multiplier": 1.3, "bonus_shard": 2},
        min_floor=3,
        weight=0.7,
        special_rules=[
            "One creature marked as capture target",
            "Target must be reduced to 0 HP with nonlethal (melee) damage",
            "Lethal kill of target causes immediate objective failure",
        ],
        compatible_templates=None,
    ),
    ArenaObjectiveDef(
        id="dimensional_anchor",
        name="Dimensional Anchor",
        category="exploration",
        description=(
            "A planar rift tears open at the centre of the arena, its edges "
            "crackling with violet energy. The Armillary speaks through "
            "gritted harmonics: \"The Drift bleeds through—activate the "
            "dimensional anchors before it swallows everything. The rift's "
            "spawn will not make it easy.\""
        ),
        dm_instructions=(
            "Place N anchor points around the arena (N = 3). Each anchor "
            "requires 2 consecutive actions by a character within 5 ft to "
            "activate. A rift at the centre of the arena spawns one "
            "CR 1/4 creature at initiative count 20 each round. When all "
            "anchors are activated the rift closes and any remaining "
            "creatures lose resistance to all damage types. Victory requires "
            "all anchors to be activated."
        ),
        win_conditions=["All dimensional anchors activated"],
        fail_conditions=["All party members reduced to 0 HP"],
        bonus_rewards={"gold_multiplier": 1.25, "bonus_shard": 2},
        min_floor=3,
        weight=0.6,
        special_rules=[
            "3 anchor points requiring 2 consecutive actions within 5 ft each",
            "Central rift spawns one CR 1/4 creature per round",
            "Closing the rift removes resistance from remaining creatures",
        ],
        compatible_templates=None,
    ),
]


# ---------------------------------------------------------------------------
# Index and helpers
# ---------------------------------------------------------------------------

_OBJECTIVE_INDEX: dict[str, ArenaObjectiveDef] = {
    obj.id: obj for obj in ARENA_OBJECTIVES
}


def get_objective(obj_id: str) -> ArenaObjectiveDef | None:
    """Return a single objective by its unique *id*, or ``None``."""
    return _OBJECTIVE_INDEX.get(obj_id)


def get_objectives_for_floor(floor_number: int) -> list[ArenaObjectiveDef]:
    """Return every objective whose *min_floor* is at or below *floor_number*."""
    return [obj for obj in ARENA_OBJECTIVES if obj.min_floor <= floor_number]


def select_objective(
    floor_number: int,
    arena_number: int,
    template: str,
    used_objectives: list[str] | None = None,
    is_boss: bool = False,
) -> ArenaObjectiveDef:
    """Pick an appropriate objective for the given arena context.

    Selection rules (evaluated in order):
    1. Floor 1, Arena 1 -> always **Extermination**.
    2. Floor 1, Arena 2+ -> 70 % Extermination, 30 % drawn from
       Survival / Activation (if eligible by template).
    3. Boss encounter (``is_boss=True``) -> force **Extermination** or
       **Destruction** (if floor >= 3).
    4. Floor 2+ -> weight-based random from all eligible objectives,
       preferring those not yet used on this floor.
    """
    used = set(used_objectives) if used_objectives else set()

    # --- Rule 1: introductory arena -----------------------------------------
    if floor_number == 1 and arena_number == 1:
        return _OBJECTIVE_INDEX["extermination"]

    # --- Rule 2: remaining floor-1 arenas -----------------------------------
    if floor_number == 1:
        if random.random() < 0.70:
            return _OBJECTIVE_INDEX["extermination"]
        # 30 % chance – pick from survival / activation if template-compatible
        candidates = [
            _OBJECTIVE_INDEX[oid]
            for oid in ("survival", "activation")
            if _OBJECTIVE_INDEX[oid].min_floor <= floor_number
            and _is_template_compatible(_OBJECTIVE_INDEX[oid], template)
        ]
        if candidates:
            return random.choice(candidates)
        return _OBJECTIVE_INDEX["extermination"]

    # --- Rule 3: boss encounters --------------------------------------------
    if is_boss:
        boss_ids = ["extermination"]
        if floor_number >= 3:
            boss_ids.append("destruction")
        boss_candidates = [
            _OBJECTIVE_INDEX[oid]
            for oid in boss_ids
            if _is_template_compatible(_OBJECTIVE_INDEX[oid], template)
        ]
        if boss_candidates:
            return random.choice(boss_candidates)
        # Fallback – extermination is always valid
        return _OBJECTIVE_INDEX["extermination"]

    # --- Rule 4: floor 2+ weighted selection --------------------------------
    eligible = [
        obj
        for obj in ARENA_OBJECTIVES
        if obj.min_floor <= floor_number
        and _is_template_compatible(obj, template)
    ]
    if not eligible:
        return _OBJECTIVE_INDEX["extermination"]

    # Prefer objectives not yet used on this floor
    unused = [obj for obj in eligible if obj.id not in used]
    pool = unused if unused else eligible

    weights = [obj.weight for obj in pool]
    return random.choices(pool, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_template_compatible(obj: ArenaObjectiveDef, template: str) -> bool:
    """Return ``True`` if the objective can appear with the given template."""
    if obj.compatible_templates is None:
        return True
    return template in obj.compatible_templates
