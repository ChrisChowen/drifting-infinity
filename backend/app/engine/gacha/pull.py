"""Gacha pull mechanics per GDD 7.0."""

import random
from dataclasses import dataclass


@dataclass
class PullResult:
    rarity: str  # "common", "uncommon", "rare", "very_rare", "legendary"
    was_pity: bool


# Base rarity rates
BASE_RATES: dict[str, float] = {
    "common": 0.50,
    "uncommon": 0.30,
    "rare": 0.13,
    "very_rare": 0.05,
    "legendary": 0.02,
}


def determine_rarity(
    pulls_since_rare: int = 0,
    pulls_since_very_rare: int = 0,
    pulls_since_legendary: int = 0,
    floor_number: int = 1,
) -> PullResult:
    """Determine the rarity of a gacha pull with pity system.

    Pity guarantees:
    - Rare guaranteed at 5 pulls
    - Very Rare guaranteed at 15 pulls
    - Legendary guaranteed at 40 pulls
    - Soft pity at 30 pulls (legendary rate doubles)

    Floor-based bonus: deeper floors slightly increase rare+ rates,
    rewarding persistence and making later pulls more exciting.
    """
    # Check hard pity first
    if pulls_since_legendary >= 40:
        return PullResult(rarity="legendary", was_pity=True)
    if pulls_since_very_rare >= 15:
        return PullResult(rarity="very_rare", was_pity=True)
    if pulls_since_rare >= 5:
        return PullResult(rarity="rare", was_pity=True)

    # Adjust rates with soft pity
    rates = dict(BASE_RATES)
    if pulls_since_legendary >= 30:
        # Soft pity: double legendary rate
        rates["legendary"] *= 2.0
        rates["common"] -= rates["legendary"] - BASE_RATES["legendary"]

    # Floor-based rate bonus: +0.5% to rare+ per floor (capped at +10%)
    floor_bonus = min(0.10, floor_number * 0.005)
    if floor_bonus > 0:
        rates["rare"] += floor_bonus * 0.5
        rates["very_rare"] += floor_bonus * 0.3
        rates["legendary"] += floor_bonus * 0.2
        rates["common"] = max(0.10, rates["common"] - floor_bonus)

    # Normalize rates
    total = sum(rates.values())
    normalized = {k: v / total for k, v in rates.items()}

    # Roll
    roll = random.random()
    cumulative = 0.0
    for rarity, rate in normalized.items():
        cumulative += rate
        if roll < cumulative:
            return PullResult(rarity=rarity, was_pity=False)

    return PullResult(rarity="common", was_pity=False)
