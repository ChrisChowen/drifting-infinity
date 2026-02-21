"""Run start/end state management.

Handles resetting characters between runs, PPC decay, and computing the
snapshot of meta-bonuses that a run starts with.
"""

from app.engine.meta.lives import compute_starting_lives
from app.engine.meta.talents import get_active_effects


def decay_ppc_between_runs(current_ppc: float) -> float:
    """Decay PPC 30% toward 1.0 between runs.

    This prevents a great run from making the next one too easy, and a
    terrible run from making the next one impossible.

    Examples:
        1.3 → 1.21
        0.7 → 0.79
        1.0 → 1.0 (no change)
    """
    return round(1.0 + (current_ppc - 1.0) * 0.7, 3)


def compute_run_start_state(
    unlocked_talents: list[str],
) -> dict:
    """Compute the snapshot of meta-bonuses applied at run start.

    This snapshot is stored on the Run model so that mid-run talent
    purchases don't retroactively affect the current run.
    """
    effects = get_active_effects(unlocked_talents)
    starting_lives = compute_starting_lives(unlocked_talents)

    return {
        "starting_lives": starting_lives,
        "effects": effects,
        "talents_snapshot": list(unlocked_talents),
    }


def reset_character_for_new_run(character_data: dict) -> dict:
    """Reset a character's run-specific state for a new run.

    Preserves: name, class, subclass, gacha equipment, lifetime death_count, scars.
    Resets: level, HP, XP, is_dead, run_deaths.

    Args:
        character_data: Dict representation of character state.

    Returns:
        Updated character dict with run-specific fields reset.
    """
    return {
        **character_data,
        "level": 1,
        "xp_total": 0,
        "is_dead": False,
        "run_deaths": 0,
        # HP will be set by class defaults at level 1 during run initialization
    }
