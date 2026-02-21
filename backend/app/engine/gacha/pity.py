"""Pity counter management for gacha system."""


def update_pity_counters(
    current_state: dict,
    pulled_rarity: str,
) -> dict:
    """Update pity counters after a pull.

    Args:
        current_state: dict with pulls_since_rare, pulls_since_very_rare, pulls_since_legendary
        pulled_rarity: The rarity that was pulled

    Returns:
        Updated counter dict
    """
    state = dict(current_state)

    # Increment all counters
    state["pulls_since_rare"] = state.get("pulls_since_rare", 0) + 1
    state["pulls_since_very_rare"] = state.get("pulls_since_very_rare", 0) + 1
    state["pulls_since_legendary"] = state.get("pulls_since_legendary", 0) + 1
    state["total_pulls"] = state.get("total_pulls", 0) + 1

    # Reset counters for pulled rarity and above
    rarity_order = ["common", "uncommon", "rare", "very_rare", "legendary"]
    pulled_idx = rarity_order.index(pulled_rarity) if pulled_rarity in rarity_order else 0

    if pulled_idx >= 2:  # rare or higher
        state["pulls_since_rare"] = 0
    if pulled_idx >= 3:  # very_rare or higher
        state["pulls_since_very_rare"] = 0
    if pulled_idx >= 4:  # legendary
        state["pulls_since_legendary"] = 0

    return state
