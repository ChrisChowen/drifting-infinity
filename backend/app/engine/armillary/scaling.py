"""Armillary floor-based scaling per GDD 5.5.

Deeper floors increase hostile effect weight and unlock higher severity effects.
"""

from dataclasses import dataclass


@dataclass
class ArmillaryScaling:
    hostile_weight_bonus: int
    max_severity: int
    wild_weight_bonus: int
    favour_earned_on_clear: int


def get_armillary_scaling(floor_number: int) -> ArmillaryScaling:
    """Get Armillary scaling parameters for a floor.

    Floor 1: Base weights, max severity 2, earn 1 Favour on clear
    Floor 2: +5 hostile, max severity 2, earn 1 Favour
    Floor 3: +10 hostile, max severity 3, earn 2 Favour
    Floor 4: +15 hostile, +5 wild, max severity 3, earn 2 Favour
    """
    return ArmillaryScaling(
        hostile_weight_bonus=min(15, (floor_number - 1) * 5),
        max_severity=3 if floor_number >= 3 else 2,
        wild_weight_bonus=5 if floor_number >= 4 else 0,
        favour_earned_on_clear=2 if floor_number >= 3 else 1,
    )


def apply_scaling_to_weights(
    base_weights: dict[str, int],
    scaling: ArmillaryScaling,
) -> dict[str, int]:
    """Apply floor scaling to category weights."""
    weights = dict(base_weights)
    weights["hostile"] = weights.get("hostile", 40) + scaling.hostile_weight_bonus
    weights["wild"] = weights.get("wild", 15) + scaling.wild_weight_bonus
    return weights
