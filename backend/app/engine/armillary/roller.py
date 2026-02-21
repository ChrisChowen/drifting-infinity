"""Armillary effect roller - weighted random selection."""

import random
from dataclasses import dataclass

from app.data.armillary_effects_data import (
    ARMILLARY_EFFECTS,
    ArmillaryEffectDef,
    get_effects_by_category,
)


@dataclass
class ArmillaryRollResult:
    effect: ArmillaryEffectDef
    was_rerolled: bool = False


# Base category weights (out of 100)
DEFAULT_CATEGORY_WEIGHTS: dict[str, int] = {
    "hostile": 40,
    "beneficial": 20,
    "environmental": 25,
    "wild": 15,
}


def roll_armillary_effect(
    round_number: int,
    category_weights: dict[str, int] | None = None,
    recent_effect_keys: list[str] | None = None,
) -> ArmillaryRollResult:
    """Roll a random Armillary effect.

    Args:
        round_number: Current combat round (for min_round filtering)
        category_weights: Custom category weights (overrides defaults)
        recent_effect_keys: Recently used effect keys (reduces repeat chance)

    Returns:
        ArmillaryRollResult with the selected effect
    """
    weights = category_weights or DEFAULT_CATEGORY_WEIGHTS
    recent = set(recent_effect_keys or [])

    # Step 1: Pick category by weight
    categories = list(weights.keys())
    category_values = [weights[c] for c in categories]
    category = random.choices(categories, weights=category_values, k=1)[0]

    # Step 2: Get valid effects for this category and round
    effects = get_effects_by_category(category)
    valid = [e for e in effects if e.min_round <= round_number]

    if not valid:
        # Fallback: try any category
        valid = [e for e in ARMILLARY_EFFECTS if e.min_round <= round_number]

    if not valid:
        # Ultimate fallback
        valid = [e for e in ARMILLARY_EFFECTS if e.severity == 1]

    # Step 3: Weight by severity and reduce recently used
    effect_weights = []
    for e in valid:
        w = 10.0
        # Higher severity = slightly less common
        if e.severity == 2:
            w = 7.0
        elif e.severity == 3:
            w = 4.0
        # Reduce weight for recently used effects
        if e.key in recent:
            w *= 0.3
        effect_weights.append(w)

    selected = random.choices(valid, weights=effect_weights, k=1)[0]
    return ArmillaryRollResult(effect=selected)


def reroll_armillary_effect(
    current_effect_key: str,
    round_number: int,
    category_weights: dict[str, int] | None = None,
) -> ArmillaryRollResult:
    """Reroll an Armillary effect (costs 1 Favour).

    Excludes the current effect from the pool.
    """
    result = roll_armillary_effect(
        round_number=round_number,
        category_weights=category_weights,
        recent_effect_keys=[current_effect_key],
    )
    result.was_rerolled = True
    return result
