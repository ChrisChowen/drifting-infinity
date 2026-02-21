"""2014 DMG encounter multipliers for action economy adjustment."""

# Creature count ranges and their multipliers
ENCOUNTER_MULTIPLIERS: list[tuple[int, int, float]] = [
    (1, 1, 1.0),
    (2, 2, 1.5),
    (3, 6, 2.0),
    (7, 10, 2.5),
    (11, 14, 3.0),
    (15, 100, 4.0),
]

# Party size shifts: positive = shift multiplier up (harder), negative = down (easier)
PARTY_SIZE_MULTIPLIER_SHIFT: dict[str, int] = {
    "solo": 1,
    "small": 1,
    "standard": 0,
    "large": -1,
}


def get_encounter_multiplier(creature_count: int, party_size_category: str = "standard") -> float:
    """Get the encounter multiplier for a given creature count, adjusted for party size."""
    shift = PARTY_SIZE_MULTIPLIER_SHIFT.get(party_size_category, 0)

    # Find the base multiplier index
    base_index = 0
    for i, (low, high, _) in enumerate(ENCOUNTER_MULTIPLIERS):
        if low <= creature_count <= high:
            base_index = i
            break
    else:
        base_index = len(ENCOUNTER_MULTIPLIERS) - 1

    # Apply party size shift
    adjusted_index = max(0, min(len(ENCOUNTER_MULTIPLIERS) - 1, base_index + shift))
    return ENCOUNTER_MULTIPLIERS[adjusted_index][2]
