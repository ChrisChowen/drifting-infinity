"""XP budget computation for roguelike encounter building.

IMPORTANT: The XP budget (adjusted XP with encounter multiplier) is used
for encounter building only. XP *awards* to players use raw XP (total creature
XP without the encounter multiplier) divided by party size. See leveling.py.

The budget is driven by:
1. Floor-level difficulty (from intensity_curve.py's FLOOR_DIFFICULTY)
2. Party level and size (from 2024 DMG XP thresholds)
3. Tier inflation (deeper tiers get proportionally harder)
4. Intensity multiplier (from the intensity curve's pacing)

Roguelike design: budgets are higher than standard 5e. The "moderate"
threshold is our floor, and "high" is normal operating range.
"""

from app.data.xp_thresholds import XP_THRESHOLDS

# Tier-based budget inflation for deeper floors
TIER_INFLATION: dict[int, float] = {
    1: 1.0,
    2: 1.10,
    3: 1.15,
    4: 1.20,
}

# Minimum XP budget per tier to prevent trivially weak encounters.
# Even a "warmup" fight should be meaningful.
MIN_BUDGET_PER_TIER: dict[int, int] = {
    1: 200,   # At least a CR 1 creature worth of budget
    2: 1500,
    3: 4000,
    4: 8000,
}


def compute_xp_budget(
    party_level: int,
    party_size: int,
    difficulty: str,
    floor_number: int = 1,
    arena_number: int = 1,
    tier: int = 1,
    xp_budget_multiplier: float = 1.0,
    early_game_scaling_factor: float = 1.0,
) -> int:
    """Compute the XP budget for an encounter.

    difficulty: "moderate" or "high" (roguelike has no "low").
    xp_budget_multiplier: Campaign balance setting (default 1.0).
    early_game_scaling_factor: Multiplier for floors 1-5 (default 1.0).
    """
    thresholds = XP_THRESHOLDS.get(party_level, XP_THRESHOLDS[1])

    # In a roguelike, "moderate" is the minimum. Map accordingly:
    # "moderate" → use the DMG "moderate" threshold
    # "high" → use the DMG "high" threshold
    per_player = thresholds.get(difficulty, thresholds["moderate"])
    base_budget = per_player * party_size

    # Apply tier inflation
    inflation = TIER_INFLATION.get(tier, 1.0)
    base_budget = int(base_budget * inflation)

    # Apply campaign XP budget multiplier
    base_budget = int(base_budget * xp_budget_multiplier)

    # Apply early-game scaling on floors 1-5
    if floor_number <= 5 and early_game_scaling_factor != 1.0:
        base_budget = int(base_budget * early_game_scaling_factor)

    # Enforce minimum budget
    minimum = MIN_BUDGET_PER_TIER.get(tier, 200)
    base_budget = max(base_budget, minimum)

    return base_budget


def get_cr_range_for_budget(
    budget: int, party_level: int, party_size: int
) -> tuple[float, float]:
    """Get reasonable CR range for a given XP budget.

    Returns (cr_min, cr_max) — creatures outside this range are filtered out.
    """
    from app.data.xp_thresholds import CR_TO_XP

    # CR min: no worthless creatures. Minimum CR 0.125 (Kobold-level).
    # For higher levels, scale up the floor.
    if party_level <= 2:
        cr_min = 0.125
    elif party_level <= 4:
        cr_min = 0.25
    elif party_level <= 6:
        cr_min = 0.5
    elif party_level <= 10:
        cr_min = 1.0
    else:
        cr_min = max(1.0, (party_level - 4) / 4)

    # CR max: don't exceed party_level + 3 (boss), or party_level + 1 (normal)
    cr_max = party_level + 3

    # Also cap by XP: no single creature should exceed the full budget
    for cr in sorted(CR_TO_XP.keys(), reverse=True):
        if CR_TO_XP[cr] <= budget:
            cr_max = min(cr_max, cr + 1)
            break

    return (cr_min, cr_max)
