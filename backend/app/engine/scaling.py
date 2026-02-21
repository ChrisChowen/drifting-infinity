"""Party size scaling rules per GDD Part 8."""

from dataclasses import dataclass
from enum import Enum


class PartySizeCategory(str, Enum):
    SOLO = "solo"
    SMALL = "small"
    STANDARD = "standard"
    LARGE = "large"


@dataclass
class ScalingParams:
    category: PartySizeCategory
    encounter_multiplier_shift: int  # -1, 0, +1
    armillary_hostile_weight: int
    armillary_beneficial_weight: int
    max_arenas_per_floor: int
    max_floors: int
    momentum_recovery_count: int  # Base recovery options per arena
    momentum_bonus_count: int  # Recovery options with Momentum Bonus
    short_rests_per_floor: int  # Number of short rests distributed across the floor
    cr_minimum_offset: int  # Additional CR minimum offset
    xp_budget_adjustment: float  # Multiplier on XP budget


def classify_party_size(party_size: int) -> PartySizeCategory:
    if party_size <= 1:
        return PartySizeCategory.SOLO
    elif party_size <= 3:
        return PartySizeCategory.SMALL
    elif party_size <= 5:
        return PartySizeCategory.STANDARD
    else:
        return PartySizeCategory.LARGE


def get_scaling_params(party_size: int) -> ScalingParams:
    category = classify_party_size(party_size)

    match category:
        case PartySizeCategory.SOLO:
            return ScalingParams(
                category=category,
                encounter_multiplier_shift=1,
                armillary_hostile_weight=30,
                armillary_beneficial_weight=30,
                max_arenas_per_floor=3,
                max_floors=3,
                momentum_recovery_count=1,
                momentum_bonus_count=2,
                short_rests_per_floor=1,
                cr_minimum_offset=0,
                xp_budget_adjustment=0.8,  # 20% reduction for NPC companion
            )
        case PartySizeCategory.SMALL:
            return ScalingParams(
                category=category,
                encounter_multiplier_shift=1,
                armillary_hostile_weight=35,
                armillary_beneficial_weight=25,
                max_arenas_per_floor=4,
                max_floors=4,
                momentum_recovery_count=2,
                momentum_bonus_count=3,
                short_rests_per_floor=2,
                cr_minimum_offset=0,
                xp_budget_adjustment=1.0,
            )
        case PartySizeCategory.STANDARD:
            return ScalingParams(
                category=category,
                encounter_multiplier_shift=0,
                armillary_hostile_weight=40,
                armillary_beneficial_weight=20,
                max_arenas_per_floor=5,
                max_floors=4,
                momentum_recovery_count=2,
                momentum_bonus_count=3,
                short_rests_per_floor=2,
                cr_minimum_offset=0,
                xp_budget_adjustment=1.0,
            )
        case PartySizeCategory.LARGE:
            return ScalingParams(
                category=category,
                encounter_multiplier_shift=-1,
                armillary_hostile_weight=45,
                armillary_beneficial_weight=18,
                max_arenas_per_floor=5,
                max_floors=4,
                momentum_recovery_count=2,
                momentum_bonus_count=3,
                short_rests_per_floor=2,
                cr_minimum_offset=1,
                xp_budget_adjustment=1.0,
            )


def get_tier(party_level: int) -> int:
    """Get the tier of play (1-4) from party level."""
    if party_level <= 4:
        return 1
    elif party_level <= 10:
        return 2
    elif party_level <= 16:
        return 3
    else:
        return 4
