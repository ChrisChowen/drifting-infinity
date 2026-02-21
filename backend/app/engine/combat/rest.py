"""Rest system for roguelike floor progression.

Rest model:
- Between arenas: Momentum recovery (partial, see momentum.py)
- Some inter-arena breaks: Short rest (spend hit dice, recover short-rest abilities)
- End of floor: Long rest (full restoration, level up)

Short rests are distributed evenly across the floor (2-3 per floor for
standard parties). This ensures both short-rest classes (Warlock, Monk,
Fighter) and long-rest classes (Wizard, Cleric) remain viable.
"""

from dataclasses import dataclass


@dataclass
class ShortRestResult:
    """What a short rest provides to the party."""
    hit_dice_spendable: bool  # Each character can spend hit dice to heal
    short_rest_abilities: bool  # Short-rest class features recharge
    warlock_slots: bool  # Warlock spell slots recover
    second_wind: bool  # Fighter Second Wind recharges
    ki_points: bool  # Monk Ki points recover


@dataclass
class LongRestResult:
    """What a long rest provides to the party."""
    full_hp: bool  # All HP restored
    all_spell_slots: bool  # All spell slots recovered
    all_abilities: bool  # All class features recharged
    hit_dice_recovery: float  # Fraction of total hit dice recovered (0.5 = half)
    exhaustion_reduction: int  # Levels of exhaustion removed
    can_level_up: bool  # Party can level up if they have enough XP


def compute_short_rest_recovery() -> ShortRestResult:
    """Compute what a short rest provides.

    Per D&D 5e rules: spend hit dice, recover short-rest abilities.
    """
    return ShortRestResult(
        hit_dice_spendable=True,
        short_rest_abilities=True,
        warlock_slots=True,
        second_wind=True,
        ki_points=True,
    )


def compute_long_rest_recovery() -> LongRestResult:
    """Compute what a long rest provides.

    Full restoration at end of floor. Party can also level up.
    """
    return LongRestResult(
        full_hp=True,
        all_spell_slots=True,
        all_abilities=True,
        hit_dice_recovery=0.5,  # Recover half of total hit dice
        exhaustion_reduction=1,  # Remove 1 level of exhaustion
        can_level_up=True,
    )


def rest_schedule_for_floor(
    total_arenas: int,
    short_rests_allowed: int = 2,
) -> list[str]:
    """Generate the recovery schedule for a floor.

    Returns a list of recovery types for the gaps BETWEEN arenas.
    Length = total_arenas - 1 (no recovery after the last arena;
    a long rest happens at floor end instead).

    Short rests are distributed evenly across the floor.
    All other gaps use momentum recovery.

    Args:
        total_arenas: Number of arenas in this floor
        short_rests_allowed: Number of short rests to place (from ScalingParams)

    Returns:
        List of "momentum" or "short_rest" strings, one per inter-arena gap.
    """
    if total_arenas <= 1:
        return []

    gaps = total_arenas - 1
    schedule = ["momentum"] * gaps

    # Place short rests evenly across the floor
    rests_to_place = min(short_rests_allowed, gaps)
    if rests_to_place > 0:
        # Spread evenly: for 2 rests in 4 gaps, place at positions 1 and 3
        step = gaps / (rests_to_place + 1)
        for i in range(rests_to_place):
            idx = int(round(step * (i + 1))) - 1
            idx = max(0, min(gaps - 1, idx))
            schedule[idx] = "short_rest"

    return schedule
