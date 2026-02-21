"""Essence award computation.

Essence is the meta-progression currency earned from every run — both
successes and failures.  More progress = more essence, incentivising
players to push further even when a run is doomed.
"""


def compute_run_essence(
    floors_completed: int = 0,
    boss_kills: int = 0,
    achievements_earned: int = 0,
    run_won: bool = False,
) -> int:
    """Compute total essence earned from a single run.

    Formula:
    - 10 essence per floor completed
    - 25 essence per boss kill
    - 15 essence per achievement earned during the run
    - 100 bonus essence for a successful (won) run
    """
    total = floors_completed * 10
    total += boss_kills * 25
    total += achievements_earned * 15
    if run_won:
        total += 100
    return total


def compute_achievement_essence(achievement_id: str) -> int:
    """Return the bonus essence reward for a specific achievement.

    Most achievements also contribute to the per-run achievement count,
    but some grant extra one-time essence on first unlock.
    """
    # One-time bonus for first unlock of milestone achievements
    _MILESTONE_BONUSES: dict[str, int] = {
        "first_blood": 10,
        "the_long_descent": 25,
        "armillarys_equal": 50,
        "deathless_run": 75,
        "completionist": 30,
        "secret_finder": 40,
    }
    return _MILESTONE_BONUSES.get(achievement_id, 0)
