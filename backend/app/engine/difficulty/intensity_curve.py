"""Intensity curve for roguelike floor pacing — attrition-aware model.

Each floor has 3-5 arenas. The party enters fresh (long rest between floors)
and is ground down by successive combats, with partial recovery between
arenas (momentum or short rest). The pacing curve accounts for this:

- The XP budget for each arena is adjusted DOWN based on the expected
  resource state of the party at that point in the floor.
- The *perceived* difficulty still escalates because attrition compounds:
  a 0.95x budget fight against a 70%-strength party is harder than a
  1.0x budget fight against a 100%-strength party.
- The climax is still the hardest *feeling* fight, but its raw XP budget
  doesn't pile on top of the resource drain.

The rest schedule (momentum vs short rest between arenas) is deterministic
and known at floor-generation time, so no runtime party state is needed.
All arenas for a floor can still be pre-generated.

Floor-to-floor recalibration uses PPC and DM assessment (unchanged).
"""

from dataclasses import dataclass
from enum import Enum


class IntensityPhase(str, Enum):
    WARMUP = "warmup"
    ESCALATION = "escalation"
    CLIMAX = "climax"


@dataclass
class IntensityState:
    phase: IntensityPhase
    intensity: float  # 0.0 to 1.0
    difficulty: str  # "moderate" or "high"


# Floor escalation: each floor is harder than the last.
# This is the primary difficulty driver across a 20-floor run.
# Designed so floor 1-2 are beatable on first run, floor 3-4 starts
# wiping unprepared parties, and later floors require meta-progression.
FLOOR_DIFFICULTY: dict[int, float] = {
    1: 0.48,   # Moderate — accessible opening, learn the systems
    2: 0.55,   # Moderate — pressure starts building
    3: 0.62,   # Moderate-high — first real challenge
    4: 0.70,   # High — first-run parties start struggling here
    5: 0.76,   # High — requires solid tactics or meta-buffs
    6: 0.85,
    7: 0.88,
    8: 0.90,
    9: 0.92,
    10: 0.94,  # Tier 2 peak — serious challenge
    11: 0.88,  # Slight reset for Tier 3 (new abilities)
    12: 0.91,
    13: 0.93,
    14: 0.95,
    15: 0.96,
    16: 0.97,  # Tier 3 peak
    17: 0.90,  # Slight reset for Tier 4
    18: 0.93,
    19: 0.96,
    20: 1.00,  # Final floor — maximum difficulty
}

# --- Attrition model constants ---
# Each arena drains this fraction of the party's remaining resources.
# This is a simple geometric decay: after N arenas with no recovery,
# expected_strength = (1 - ATTRITION_PER_ARENA)^N.
# 0.12 means each fight costs ~12% of remaining strength — after 4 fights
# with only momentum recovery, the party is at roughly 55-60% strength.
ATTRITION_PER_ARENA: float = 0.12

# How much each recovery type restores (as a fraction of max strength).
# Momentum: a hit die + a spell slot ≈ small bump.
# Short rest: hit dice + short-rest features ≈ meaningful recovery.
RECOVERY_MOMENTUM: float = 0.05
RECOVERY_SHORT_REST: float = 0.20

# The pacing curve defines the *desired perceived difficulty* at each
# arena position. This is what the player FEELS, combining raw encounter
# budget with their depleted state. The raw budget is then derived by
# dividing perceived intensity by expected party strength.
#
# Opener:  0.95 — strong opening fight, party is fresh so budget is close
# Middle:  1.00 — steady pressure, budget drops as attrition rises
# Climax:  1.10 — the peak experience, but raw budget is tempered by the
#                  fact that the party is at their weakest
PERCEIVED_OPENER: float = 0.95
PERCEIVED_CLIMAX: float = 1.10

# Cap on raw budget multiplier — even with attrition factored in, never
# give a single arena more than this multiplier of the floor's base budget.
# This prevents degenerate cases where very low expected strength would
# cause the raw budget to spike unreasonably.
MAX_RAW_MULTIPLIER: float = 1.05


def _compute_expected_strength(
    arena_number: int,
    total_arenas: int,
    rest_schedule: list[str] | None = None,
) -> float:
    """Estimate the party's resource strength entering a given arena.

    Returns a value from 0.0 to 1.0 where 1.0 = fully rested.
    The model is deterministic: it uses the known rest schedule to
    compute expected drain and recovery across the floor.

    Args:
        arena_number: 1-indexed arena within the floor.
        total_arenas: Total arenas on this floor.
        rest_schedule: List of "momentum" or "short_rest" for each
            inter-arena gap (length = total_arenas - 1). If None,
            a default schedule is synthesized (2 short rests, evenly
            distributed).
    """
    if arena_number <= 1:
        return 1.0

    # Build a default rest schedule if none provided
    if rest_schedule is None:
        rest_schedule = _default_rest_schedule(total_arenas)

    strength = 1.0
    for arena_idx in range(1, arena_number):
        # Arena combat drains resources
        strength *= (1.0 - ATTRITION_PER_ARENA)

        # Recovery happens in the gap AFTER this arena (before the next)
        gap_idx = arena_idx - 1  # gap 0 is between arena 1 and arena 2
        if gap_idx < len(rest_schedule):
            recovery_type = rest_schedule[gap_idx]
            if recovery_type == "short_rest":
                strength = min(1.0, strength + RECOVERY_SHORT_REST)
            else:
                strength = min(1.0, strength + RECOVERY_MOMENTUM)

    return round(strength, 4)


def _default_rest_schedule(total_arenas: int) -> list[str]:
    """Synthesize a default rest schedule (matches rest.py defaults).

    Places 2 short rests evenly across the inter-arena gaps.
    """
    if total_arenas <= 1:
        return []
    gaps = total_arenas - 1
    schedule = ["momentum"] * gaps
    rests_to_place = min(2, gaps)
    if rests_to_place > 0:
        step = gaps / (rests_to_place + 1)
        for i in range(rests_to_place):
            idx = int(round(step * (i + 1))) - 1
            idx = max(0, min(gaps - 1, idx))
            schedule[idx] = "short_rest"
    return schedule


def _get_arena_pacing(
    arena_number: int,
    total_arenas: int,
    rest_schedule: list[str] | None = None,
) -> tuple[IntensityPhase, float]:
    """Get the pacing phase and attrition-aware multiplier for an arena.

    The multiplier accounts for expected party resource state so that
    the *perceived* difficulty follows the desired curve while the raw
    XP budget compensates for attrition.

    Returns (phase, multiplier) where multiplier adjusts the floor's
    base difficulty for this arena's position in the floor.
    """
    if total_arenas <= 1:
        return IntensityPhase.CLIMAX, 1.0

    # Determine phase
    if arena_number == 1:
        phase = IntensityPhase.WARMUP
    elif arena_number == total_arenas:
        phase = IntensityPhase.CLIMAX
    else:
        phase = IntensityPhase.ESCALATION

    # Desired perceived intensity (what the player should FEEL)
    # Linear interpolation from opener to climax across arena positions
    position = (arena_number - 1) / (total_arenas - 1)
    perceived = PERCEIVED_OPENER + position * (PERCEIVED_CLIMAX - PERCEIVED_OPENER)

    # Expected party strength entering this arena
    strength = _compute_expected_strength(arena_number, total_arenas, rest_schedule)

    # Raw budget multiplier = perceived / strength
    # When the party is at 70% strength, a perceived 1.0 fight only
    # needs a 0.70x raw budget — attrition does the rest.
    # But we cap the raw multiplier to avoid extreme spikes.
    if strength > 0.0:
        raw_mult = perceived * strength
    else:
        raw_mult = perceived * 0.5

    raw_mult = min(MAX_RAW_MULTIPLIER, raw_mult)

    return phase, round(raw_mult, 4)


def compute_intensity_curve(
    arena_number: int,
    total_arenas: int,
    floor_number: int,
    party_power_coefficient: float = 1.0,
    rest_schedule: list[str] | None = None,
) -> IntensityState:
    """Compute the intensity state for an arena.

    The floor_number determines the base difficulty (via FLOOR_DIFFICULTY).
    The arena_number provides attrition-aware intra-floor pacing.
    The PPC adjusts the floor difficulty based on historical performance.
    The rest_schedule enables accurate attrition modeling.

    Args:
        arena_number: 1-indexed arena within the floor.
        total_arenas: Total arenas on this floor.
        floor_number: Floor number in the run (1-20+).
        party_power_coefficient: Historical PPC (default 1.0).
        rest_schedule: List of "momentum" or "short_rest" for each
            inter-arena gap. If None, a default schedule is used.

    Returns IntensityState with phase, intensity (0.0-1.0), and difficulty.
    """
    # Base floor difficulty (interpolate for floors beyond the table)
    if floor_number in FLOOR_DIFFICULTY:
        base = FLOOR_DIFFICULTY[floor_number]
    elif floor_number > 20:
        base = 1.0
    else:
        # Interpolate between known values
        lower = max(k for k in FLOOR_DIFFICULTY if k <= floor_number)
        upper = min(k for k in FLOOR_DIFFICULTY if k >= floor_number)
        if lower == upper:
            base = FLOOR_DIFFICULTY[lower]
        else:
            t = (floor_number - lower) / (upper - lower)
            base = (
                FLOOR_DIFFICULTY[lower]
                + t * (FLOOR_DIFFICULTY[upper] - FLOOR_DIFFICULTY[lower])
            )

    # PPC adjustment: strong parties (>1.0) get harder floors,
    # weak parties (<1.0) get slightly easier ones.
    # The effect is moderate — PPC 1.3 adds ~6%, PPC 0.7 subtracts ~6%.
    ppc_adjustment = (party_power_coefficient - 1.0) * 0.20
    base = max(0.40, min(1.0, base + ppc_adjustment))

    # Attrition-aware intra-floor pacing
    phase, pacing_mult = _get_arena_pacing(
        arena_number, total_arenas, rest_schedule,
    )
    intensity = max(0.40, min(1.0, base * pacing_mult))

    # Map to difficulty tier — no "low" in a roguelike
    if intensity < 0.70:
        difficulty = "moderate"
    else:
        difficulty = "high"

    return IntensityState(
        phase=phase,
        intensity=round(intensity, 3),
        difficulty=difficulty,
    )
