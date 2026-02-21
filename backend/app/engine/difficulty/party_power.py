"""Party Power Coefficient — between-floor calibration.

PPC tracks historical performance to adjust future floor difficulty.
Updated BETWEEN FLOORS (not per-arena) based on:
- DM assessment of how the floor went
- Party HP state at end of floor
- Deaths during the floor
- Run-level outcome (TPK, completion, abandonment)

Within a floor, PPC is stable — this allows all arenas on a floor
to be pre-generated with consistent difficulty.

The PPC system has two modes:
- Calibration (floors 1-2): adjustments are doubled to quickly
  identify party power level for both optimised and new groups.
- Standard (floors 3+): normal adjustments for stable tracking.
"""


def compute_floor_ppc_adjustment(
    current_ppc: float,
    floor_cleared: bool,
    average_hp_at_floor_end: float = 0.5,
    deaths_on_floor: int = 0,
    dm_assessment: str = "healthy",
    is_calibration: bool = False,
) -> float:
    """Update PPC at the end of a floor based on how the floor went.

    This is the primary PPC update mechanism. Called once per floor.

    Args:
        current_ppc: Current PPC value.
        floor_cleared: Whether the party cleared all arenas on the floor.
        average_hp_at_floor_end: Party's average HP% at floor end.
        deaths_on_floor: Number of character deaths during the floor.
        dm_assessment: DM's assessment ("healthy"/"strained"/"critical"/"dire").
        is_calibration: True for floors 1-2 (double adjustments).

    Returns:
        New PPC value (clamped to 0.6-1.5).
    """
    adjustment = 0.0

    if floor_cleared:
        # Cleared the floor — adjust based on how cleanly
        if average_hp_at_floor_end > 0.7 and deaths_on_floor == 0:
            adjustment = 0.06  # Cruised through — party is strong
        elif average_hp_at_floor_end > 0.4 and deaths_on_floor == 0:
            adjustment = 0.03  # Moderate difficulty — as expected
        elif deaths_on_floor > 0:
            adjustment = -0.02  # Cleared but took casualties
        else:
            adjustment = 0.0  # Barely made it — neutral
    else:
        # Floor failure (TPK or abandoned)
        adjustment = -0.08

    # DM assessment override — strongest signal
    dm_adjustments = {
        "healthy": 0.0,
        "strained": -0.02,
        "critical": -0.05,
        "dire": -0.08,
    }
    adjustment += dm_adjustments.get(dm_assessment, 0.0)

    # Death penalty (stacks with assessment)
    if deaths_on_floor >= 2:
        adjustment -= 0.03

    # Calibration: double adjustments for fast convergence
    if is_calibration:
        adjustment *= 2.0

    new_ppc = current_ppc + adjustment
    return round(max(0.6, min(1.5, new_ppc)), 3)


def compute_run_end_ppc_adjustment(
    current_ppc: float,
    run_outcome: str,
    floors_completed: int,
    total_floors: int,
    average_hp_at_end: float = 0.5,
    deaths_this_run: int = 0,
) -> float:
    """Update PPC at the end of a run based on overall results.

    This is a secondary adjustment on top of per-floor updates.
    It provides a global correction based on the run's outcome.

    Args:
        run_outcome: "completed", "tpk", or "abandoned"
    """
    completion_ratio = floors_completed / max(total_floors, 1)

    if run_outcome == "completed":
        if average_hp_at_end > 0.7:
            adjustment = 0.05
        elif average_hp_at_end > 0.4:
            adjustment = 0.02
        else:
            adjustment = 0.0
    elif run_outcome == "tpk":
        # Scale by how far they got — TPK on floor 2 is worse signal
        # than TPK on floor 15
        adjustment = -0.06 * (1.0 - completion_ratio * 0.5)
    elif run_outcome == "abandoned":
        adjustment = -0.02 * (1.0 - completion_ratio)
    else:
        adjustment = 0.0

    # Additional death penalty
    adjustment -= deaths_this_run * 0.01

    new_ppc = current_ppc + adjustment
    return round(max(0.6, min(1.5, new_ppc)), 3)


def compute_run_local_adjustment(snapshots_this_run: list[dict]) -> float:
    """Compute a mid-run difficulty adjustment from snapshot history.

    This provides floor-level feedback within a run. Each snapshot
    represents the state after a completed floor (not per-arena).

    The adjustment is dampened and clamped to prevent wild swings.

    Args:
        snapshots_this_run: List of dicts with keys:
            - dm_combat_perception: "too_easy"|"just_right"|"too_hard"|"near_tpk"|None
            - average_hp_percentage: float 0-1
            - any_dead: bool

    Returns:
        Float adjustment to apply to XP budget multiplier.
    """
    if not snapshots_this_run:
        return 0.0

    total = 0.0

    for snap in snapshots_this_run:
        # DM perception signal
        perception = snap.get("dm_combat_perception")
        perception_adjustment = {
            "too_easy": 0.04,
            "just_right": 0.0,
            "too_hard": -0.03,
            "near_tpk": -0.06,
        }
        total += perception_adjustment.get(perception, 0.0)

        # HP signal
        avg_hp = snap.get("average_hp_percentage", 1.0)
        if avg_hp > 0.8:
            total += 0.02
        elif avg_hp < 0.3:
            total -= 0.03

        # Death signal
        if snap.get("any_dead", False):
            total -= 0.04

    # Dampen to prevent overreaction
    dampened = total * 0.6

    # Clamp to +-0.15
    return round(max(-0.15, min(0.15, dampened)), 3)
