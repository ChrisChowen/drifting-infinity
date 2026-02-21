"""Gold economy calculations per GDD 6.2."""


# Level multiplier for gold payouts
LEVEL_MULTIPLIERS: dict[int, int] = {}
for lvl in range(1, 5):
    LEVEL_MULTIPLIERS[lvl] = 1
for lvl in range(5, 11):
    LEVEL_MULTIPLIERS[lvl] = 2
for lvl in range(11, 17):
    LEVEL_MULTIPLIERS[lvl] = 4
for lvl in range(17, 21):
    LEVEL_MULTIPLIERS[lvl] = 8

# Milestone bonuses per floor cleared (scaled through all 20 floors)
MILESTONE_BONUSES: dict[int, int] = {
    1: 50,
    2: 100,
    3: 200,
    4: 400,
    5: 500,
    6: 650,
    7: 800,
    8: 1000,
    9: 1200,
    10: 1500,
    11: 1800,
    12: 2200,
    13: 2600,
    14: 3000,
    15: 3500,
    16: 4000,
    17: 4500,
    18: 5000,
    19: 6000,
    20: 8000,
}

FULL_RUN_COMPLETION_BONUS = 150
PARTICIPATION_FLOOR_PER_ARENA = 50

# Per-arena completion bonus: 30 * party_level (~20% increase for better economy)
ARENA_COMPLETION_BONUS_PER_LEVEL = 30

# Treasure hoard multiplier for high-difficulty arenas
TREASURE_HOARD_MULTIPLIER = 1.5


def compute_arena_gold(
    arena_number: int,
    party_level: int,
    difficulty: str = "moderate",
    gold_multiplier: float = 1.0,
) -> int:
    """Compute base gold payout for an arena.

    Arena N yields 5N gp base, plus a flat 25 * party_level bonus.
    High-difficulty arenas get a 1.5x treasure hoard multiplier.
    gold_multiplier: Campaign balance setting (default 1.0).
    """
    base = 5 * arena_number
    multiplier = LEVEL_MULTIPLIERS.get(party_level, 1)
    arena_gold = base * multiplier

    # Flat arena completion bonus
    arena_gold += ARENA_COMPLETION_BONUS_PER_LEVEL * party_level

    # Treasure hoard for high-difficulty encounters
    if difficulty == "high":
        arena_gold = int(arena_gold * TREASURE_HOARD_MULTIPLIER)

    # Apply campaign gold multiplier
    arena_gold = int(arena_gold * gold_multiplier)

    return arena_gold


def compute_participation_gold(arenas_cleared: int, party_level: int) -> int:
    """Compute participation floor gold (guaranteed minimum)."""
    multiplier = LEVEL_MULTIPLIERS.get(party_level, 1)
    return arenas_cleared * PARTICIPATION_FLOOR_PER_ARENA * multiplier


def compute_milestone_gold(floor_number: int, party_level: int) -> int:
    """Compute milestone bonus for clearing a floor."""
    base = MILESTONE_BONUSES.get(floor_number, 0)
    multiplier = LEVEL_MULTIPLIERS.get(party_level, 1)
    return base * multiplier


def compute_run_completion_gold(party_level: int) -> int:
    """Compute bonus for completing a full run."""
    multiplier = LEVEL_MULTIPLIERS.get(party_level, 1)
    return FULL_RUN_COMPLETION_BONUS * multiplier


def compute_total_run_gold(
    arenas_cleared_per_floor: list[int],
    floors_completed: list[int],
    party_level: int,
    run_completed: bool,
) -> int:
    """Compute total gold for a run."""
    total = 0

    # Base gold from arenas
    arena_gold = 0
    for floor_idx, count in enumerate(arenas_cleared_per_floor):
        for arena_num in range(1, count + 1):
            arena_gold += compute_arena_gold(arena_num, party_level)

    # Participation floor (guaranteed minimum)
    total_arenas = sum(arenas_cleared_per_floor)
    participation = compute_participation_gold(total_arenas, party_level)

    # Use the higher of base or participation
    total += max(arena_gold, participation)

    # Milestone bonuses
    for floor_num in floors_completed:
        total += compute_milestone_gold(floor_num, party_level)

    # Run completion bonus
    if run_completed:
        total += compute_run_completion_gold(party_level)

    return total
