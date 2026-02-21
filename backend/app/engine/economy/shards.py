"""Astral Shard economy per GDD 7.2."""

SHARDS_BASE_PER_FLOOR = 3
SHARDS_FLOOR_SCALING_DIVISOR = 4  # +1 shard per 4 floors
SHARDS_RUN_COMPLETE_BONUS = 10
SHARDS_ACHIEVEMENT_BONUS = 5
SHARDS_PER_PULL = 5

# Achievement bonuses
SHARDS_FIRST_BOSS_KILL = 5
SHARDS_NO_DEATH_FLOOR = 3
SHARDS_FULL_CLEAR = 5


def compute_floor_clear_shards(floor_number: int = 1) -> int:
    """Shards for clearing a floor. Scales with depth."""
    return SHARDS_BASE_PER_FLOOR + floor_number // SHARDS_FLOOR_SCALING_DIVISOR


def compute_run_complete_shards() -> int:
    return SHARDS_RUN_COMPLETE_BONUS


def compute_achievement_shards(
    first_boss_kill: bool = False,
    no_deaths_this_floor: bool = False,
    full_clear: bool = False,
) -> int:
    """Compute bonus shards from achievements."""
    total = 0
    if first_boss_kill:
        total += SHARDS_FIRST_BOSS_KILL
    if no_deaths_this_floor:
        total += SHARDS_NO_DEATH_FLOOR
    if full_clear:
        total += SHARDS_FULL_CLEAR
    return total


def compute_total_run_shards(
    floors_cleared: int,
    run_completed: bool,
    floor_numbers: list[int] | None = None,
) -> int:
    """Compute total shards for a run."""
    total = 0
    if floor_numbers:
        for fn in floor_numbers:
            total += compute_floor_clear_shards(fn)
    else:
        for fn in range(1, floors_cleared + 1):
            total += compute_floor_clear_shards(fn)
    if run_completed:
        total += SHARDS_RUN_COMPLETE_BONUS
    return total
