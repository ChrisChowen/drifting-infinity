"""Tier-specific parameters for difficulty scaling."""

from dataclasses import dataclass


@dataclass
class TierParams:
    tier: int
    level_range: tuple[int, int]
    cr_floor: float  # Minimum CR for encounters
    cr_ceiling: float  # Maximum CR for "normal" encounters
    boss_cr_max: float  # Maximum CR for boss encounters
    budget_inflation: float  # XP budget multiplier
    recommended_floor_count: int
    recommended_arenas_per_floor: int


TIER_PARAMS: dict[int, TierParams] = {
    1: TierParams(
        tier=1,
        level_range=(1, 4),
        cr_floor=0.125,  # No CR 0 trash — minimum Kobold-level threat
        cr_ceiling=5,
        boss_cr_max=7,
        budget_inflation=1.0,
        recommended_floor_count=4,
        recommended_arenas_per_floor=4,
    ),
    2: TierParams(
        tier=2,
        level_range=(5, 10),
        cr_floor=1,
        cr_ceiling=11,
        boss_cr_max=14,
        budget_inflation=1.05,
        recommended_floor_count=4,
        recommended_arenas_per_floor=4,
    ),
    3: TierParams(
        tier=3,
        level_range=(11, 16),
        cr_floor=4,
        cr_ceiling=18,
        boss_cr_max=21,
        budget_inflation=1.1,
        recommended_floor_count=4,
        recommended_arenas_per_floor=5,
    ),
    4: TierParams(
        tier=4,
        level_range=(17, 20),
        cr_floor=8,
        cr_ceiling=24,
        boss_cr_max=30,
        budget_inflation=1.15,
        recommended_floor_count=4,
        recommended_arenas_per_floor=5,
    ),
}


def get_tier_params(tier: int) -> TierParams:
    return TIER_PARAMS.get(tier, TIER_PARAMS[1])
