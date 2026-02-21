"""Armillary budget tracker per GDD 5.4.

The Armillary has an XP budget equal to 20% of the encounter's XP budget.
Once the budget is spent, only severity-1 effects or beneficial effects can activate.
"""

from dataclasses import dataclass


@dataclass
class BudgetState:
    total_budget: int
    spent: int
    remaining: int
    is_exhausted: bool
    can_use_hostile: bool


def compute_armillary_budget(encounter_xp_budget: int) -> int:
    """Compute the Armillary's XP budget (20% of encounter XP)."""
    return int(encounter_xp_budget * 0.2)


def get_budget_state(
    total_budget: int,
    effects_used: list[dict],
) -> BudgetState:
    """Get current budget state from used effects.

    Args:
        total_budget: Total Armillary XP budget
        effects_used: List of dicts with 'xp_cost' and 'was_overridden'
    """
    spent = sum(
        e.get("xp_cost", 0)
        for e in effects_used
        if not e.get("was_overridden", False)
    )
    remaining = max(0, total_budget - spent)
    is_exhausted = remaining <= 0

    return BudgetState(
        total_budget=total_budget,
        spent=spent,
        remaining=remaining,
        is_exhausted=is_exhausted,
        can_use_hostile=not is_exhausted,
    )


def can_afford_effect(budget_state: BudgetState, xp_cost: int) -> bool:
    """Check if the Armillary can afford an effect."""
    if xp_cost <= 0:
        return True  # Beneficial effects are free
    return budget_state.remaining >= xp_cost


def downgrade_severity(
    current_severity: int,
    budget_remaining: int,
) -> int:
    """Downgrade effect severity if budget is low.

    If budget is running low, force lower severity effects.
    """
    if budget_remaining <= 0:
        return 1
    if budget_remaining < 30 and current_severity > 1:
        return current_severity - 1
    return current_severity
