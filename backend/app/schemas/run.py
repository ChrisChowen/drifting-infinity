from datetime import datetime

from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    starting_level: int | None = Field(default=None, ge=1, le=20)
    floor_count: int | None = Field(default=None, ge=1, le=20)
    seed: int | None = None

    def compute_floor_count(self, party_level: int) -> int:
        """Return floor_count, or auto-compute from party level.

        GDD target: ~20 adventuring days from Lv 1-20.
        If the party starts at a higher level the remaining floors scale down.
        """
        if self.floor_count is not None:
            return self.floor_count
        remaining_levels = max(1, 20 - party_level)
        return max(4, remaining_levels)


class RunResponse(BaseModel):
    id: str
    campaign_id: str
    started_at: datetime
    ended_at: datetime | None
    starting_level: int
    floor_count: int
    floors_completed: int
    total_gold_earned: int
    total_shards_earned: int
    seed: int = 0
    outcome: str | None
    difficulty_curve: list
    armillary_favour: int
    affix_history: list = []
    lives_remaining: int = 3
    total_deaths: int = 0
    death_log: list = []
