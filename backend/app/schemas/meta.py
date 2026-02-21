"""Meta-progression schemas (essence, talents, achievements, lore)."""

from pydantic import BaseModel


class MetaResponse(BaseModel):
    essence_balance: int
    essence_lifetime: int
    unlocked_talents: list[str]
    achievements: list[str]
    total_runs_completed: int
    total_runs_won: int
    highest_floor_reached: int
    total_floors_cleared: int
    total_deaths_all_runs: int
    secret_floors_discovered: list[str]
    lore_fragments_found: list[str]
    antagonist_encounters: int


class TalentResponse(BaseModel):
    id: str
    name: str
    branch: str
    tier: int
    cost: int
    effect_key: str
    description: str
    is_unlocked: bool
    can_afford: bool
    prerequisite_met: bool


class TalentTreeResponse(BaseModel):
    talents: list[TalentResponse]
    essence_balance: int


class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    essence_reward: int
    is_earned: bool


class LoreFragmentResponse(BaseModel):
    id: str
    title: str
    text: str
    category: str
    source: str
    is_discovered: bool


class LoreBeatResponse(BaseModel):
    id: str
    floor: int
    act: int
    trigger: str
    arbiter_text: str
    aethon_text: str | None
    dm_stage_direction: str
    lore_fragment_id: str | None


class RunEndMetaResponse(BaseModel):
    essence_earned: int
    new_achievements: list[AchievementResponse]
    lore_fragments_discovered: list[LoreFragmentResponse]
    total_essence: int
    talents_affordable: int
