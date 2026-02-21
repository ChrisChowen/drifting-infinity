"""Adjust Armillary category weights based on party state.

Per GDD 5.3: When the party is struggling, shift weights toward beneficial.
When the party is strong, shift toward hostile.
"""


def adjust_weights(
    base_weights: dict[str, int],
    average_hp_percentage: float = 1.0,
    any_dead: bool = False,
    cumulative_stress: float = 0.0,
    arena_number: int = 1,
    floor_number: int = 1,
    party_power_coefficient: float = 1.0,
) -> dict[str, int]:
    """Adjust category weights based on party state.

    Args:
        base_weights: Starting category weights
        average_hp_percentage: 0.0-1.0, party average HP
        any_dead: Whether any party member is dead
        cumulative_stress: 0.0-1.0, stress from health snapshots
        arena_number: Current arena in the floor
        floor_number: Current floor in the run
        party_power_coefficient: PPC from difficulty system (0.6-1.5)

    Returns:
        Adjusted weights dict
    """
    weights = dict(base_weights)

    # HP-based adjustment
    if average_hp_percentage < 0.3:
        # Party in critical shape: heavily favor beneficial
        weights["hostile"] = max(10, weights["hostile"] - 20)
        weights["beneficial"] = weights["beneficial"] + 15
    elif average_hp_percentage < 0.5:
        # Party strained: slightly favor beneficial
        weights["hostile"] = max(15, weights["hostile"] - 10)
        weights["beneficial"] = weights["beneficial"] + 8
    elif average_hp_percentage > 0.8:
        # Party doing well: increase hostile pressure
        weights["hostile"] = weights["hostile"] + 5
        weights["beneficial"] = max(10, weights["beneficial"] - 3)

    # Death penalty: if someone died, ease up
    if any_dead:
        weights["hostile"] = max(10, weights["hostile"] - 15)
        weights["beneficial"] = weights["beneficial"] + 10

    # Cumulative stress adjustment
    if cumulative_stress > 0.6:
        weights["hostile"] = max(10, weights["hostile"] - 10)
        weights["beneficial"] = weights["beneficial"] + 5

    # Floor scaling: deeper floors = more hostile (capped at +15)
    # Floors 1-3 get no bonus to keep the early game more accessible
    floor_bonus = min(15, max(0, floor_number - 3) * 2)
    weights["hostile"] = weights["hostile"] + floor_bonus

    # Arena scaling: later arenas = slightly more hostile
    arena_bonus = (arena_number - 1) * 2
    weights["hostile"] = weights["hostile"] + arena_bonus

    # PPC-based balancing: struggling parties get less hostile events
    if party_power_coefficient < 0.8:
        weights["hostile"] = max(10, weights["hostile"] - 10)
        weights["beneficial"] = weights["beneficial"] + 5
    elif party_power_coefficient > 1.2:
        weights["hostile"] = weights["hostile"] + 5

    # Normalize to ensure weights are positive
    for key in weights:
        weights[key] = max(5, weights[key])

    return weights
