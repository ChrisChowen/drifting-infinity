"""Gacha collection milestones per GDD 7.4."""

from dataclasses import dataclass


@dataclass
class MilestoneReward:
    pulls_required: int
    reward_type: str
    reward_amount: int
    description: str


MILESTONES: list[MilestoneReward] = [
    MilestoneReward(10, "shards", 5, "10 pulls: Bonus 5 Astral Shards"),
    MilestoneReward(25, "gold", 500, "25 pulls: Bonus 500 Gold"),
    MilestoneReward(50, "shards", 15, "50 pulls: Bonus 15 Astral Shards"),
    MilestoneReward(100, "legendary_pity", 1, "100 pulls: Guaranteed Legendary on next pull"),
]


def check_milestones(total_pulls: int, already_claimed: set[int]) -> list[MilestoneReward]:
    """Check which milestones have been reached but not yet claimed."""
    return [
        m for m in MILESTONES
        if total_pulls >= m.pulls_required and m.pulls_required not in already_claimed
    ]
