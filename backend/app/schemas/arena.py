from typing import Literal

from pydantic import BaseModel

CreatureStatus = Literal["alive", "bloodied", "defeated"]


class ArenaResponse(BaseModel):
    id: str
    floor_id: str
    arena_number: int
    encounter_template: str | None
    difficulty_target: float | None
    xp_budget: int | None
    adjusted_xp: int | None
    actual_difficulty: str | None
    gold_earned_per_player: int
    tactical_brief: str | None
    map_id: str | None
    environment: str | None = None
    is_active: bool
    is_complete: bool
    momentum_bonus_earned: bool
    objective: str | None = None
    objective_progress: dict | None = None
    is_social: bool = False
    social_encounter_id: str | None = None
    social_encounter_result: dict | None = None
    secret_event_id: str | None = None
    dm_notes: str | None = None
    custom_read_aloud: str | None = None
    narrative_content: dict | None = None


class ArenaCompleteResponse(BaseModel):
    message: str
    gold_per_player: int
    xp_award: int
    leveled_characters: list[dict]


class ArenaCreatureStatusResponse(BaseModel):
    id: str
    arena_id: str
    monster_id: str
    instance_label: str
    status: CreatureStatus
    is_reinforcement: bool


class CreatureStatusUpdate(BaseModel):
    status: CreatureStatus
