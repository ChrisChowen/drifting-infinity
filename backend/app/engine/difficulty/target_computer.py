"""Difficulty target computation — between-floor calibration.

This module adjusts the base intensity from the floor curve based on
the party's state from the PREVIOUS floor's performance. It is NOT
reactive to individual arena outcomes — that would prevent pre-generating
all encounters for a floor.

The DM submits a health snapshot after each floor. That snapshot feeds
into the next floor's difficulty computation. Within a floor, all arenas
share the same base difficulty (with intra-floor pacing variation from
intensity_curve.py).
"""

from dataclasses import dataclass


@dataclass
class DifficultyTarget:
    base_intensity: float
    adjusted_intensity: float
    difficulty: str
    xp_multiplier: float  # Applied to the base XP budget
    notes: list[str]


def compute_difficulty_target(
    base_intensity: float,
    previous_floor_avg_hp: float = 1.0,
    previous_floor_deaths: int = 0,
    previous_floor_tpk: bool = False,
    resource_depletion: float = 0.0,
    party_power_coefficient: float = 1.0,
    dm_assessment: str = "healthy",
) -> DifficultyTarget:
    """Compute the floor's difficulty target based on previous floor results.

    This is called once per floor to set the difficulty for all arenas.
    Individual arenas get pacing variation from the intensity curve, but
    the base difficulty level is consistent across the floor.

    Args:
        base_intensity: From intensity_curve.py (floor-level base).
        previous_floor_avg_hp: Party's average HP% at end of previous floor.
        previous_floor_deaths: Number of deaths on previous floor.
        previous_floor_tpk: Whether previous floor ended in TPK.
        resource_depletion: Estimated spell slot / ability depletion (0-1).
        party_power_coefficient: Historical PPC from previous floors.
        dm_assessment: DM's subjective assessment of previous floor:
            "healthy", "strained", "critical", "dire"
    """
    adjusted = base_intensity
    notes = []

    # Previous floor HP-based adjustment (gentler than per-arena)
    if previous_floor_tpk:
        adjusted *= 0.70
        notes.append("Previous floor TPK — significant reduction (-30%)")
    elif previous_floor_avg_hp < 0.25:
        adjusted *= 0.80
        notes.append("Party ended previous floor critically hurt (-20%)")
    elif previous_floor_avg_hp < 0.45:
        adjusted *= 0.90
        notes.append("Party ended previous floor low on HP (-10%)")
    elif previous_floor_avg_hp > 0.85:
        adjusted *= 1.05
        notes.append("Party ended previous floor healthy (+5%)")

    # Death toll from previous floor
    if previous_floor_deaths >= 2:
        adjusted *= 0.85
        notes.append(f"Multiple deaths last floor ({previous_floor_deaths}) (-15%)")
    elif previous_floor_deaths == 1:
        adjusted *= 0.93
        notes.append("One death last floor (-7%)")

    # Resource depletion
    if resource_depletion > 0.7:
        adjusted *= 0.92
        notes.append("High resource depletion entering floor (-8%)")

    # PPC historical adjustment (wider dead zone to avoid over-correction)
    # PPC is the primary between-floor calibration signal.
    if party_power_coefficient > 1.25:
        adjusted *= 1.10
        notes.append(
            f"Strong party history (PPC={party_power_coefficient:.2f}) (+10%)"
        )
    elif party_power_coefficient < 0.7:
        adjusted *= 0.70
        notes.append(
            f"Party in crisis (PPC={party_power_coefficient:.2f}) (-30%)"
        )
    elif party_power_coefficient < 0.85:
        adjusted *= 0.85
        notes.append(
            f"Struggling party (PPC={party_power_coefficient:.2f}) (-15%)"
        )

    # DM assessment — strongest signal, applied last
    assessment_mods = {
        "healthy": 1.0,
        "strained": 0.90,
        "critical": 0.78,
        "dire": 0.65,
    }
    dm_mod = assessment_mods.get(dm_assessment, 1.0)
    if dm_mod != 1.0:
        adjusted *= dm_mod
        notes.append(f"DM assessment: {dm_assessment} (x{dm_mod})")

    # Clamp — floor is higher than before (no trivial encounters)
    adjusted = max(0.35, min(1.0, adjusted))

    # Map to difficulty and XP multiplier
    # Roguelike: no "low" difficulty. Moderate is the floor.
    if adjusted < 0.65:
        difficulty = "moderate"
        xp_multiplier = 0.90
    else:
        difficulty = "high"
        xp_multiplier = 1.0 + (adjusted - 0.65) * 0.30  # 1.0 → 1.105

    # Cap multiplier
    xp_multiplier = min(1.15, xp_multiplier)

    return DifficultyTarget(
        base_intensity=base_intensity,
        adjusted_intensity=round(adjusted, 3),
        difficulty=difficulty,
        xp_multiplier=round(xp_multiplier, 3),
        notes=notes,
    )
