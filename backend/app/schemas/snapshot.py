from pydantic import BaseModel, Field


class CharacterSnapshotInput(BaseModel):
    character_id: str
    name: str
    hp_percentage: float = Field(ge=0.0, le=1.0)
    is_on_final_stand: bool = False
    is_dead: bool = False
    resources_depleted: float = Field(ge=0.0, le=1.0, default=0.0)


class HealthSnapshotCreate(BaseModel):
    dm_assessment: str  # "healthy", "strained", "critical", "dire"
    dm_combat_perception: str | None = None  # "too_easy", "just_right", "too_hard", "near_tpk"
    any_on_final_stand: bool = False
    character_snapshots: list[CharacterSnapshotInput]


class HealthSnapshotResponse(BaseModel):
    id: str
    floor_id: str
    after_arena_number: int
    dm_assessment: str
    dm_combat_perception: str | None = None
    any_on_final_stand: bool
    character_snapshots: list
    average_hp_percentage: float
    lowest_hp_percentage: float
    any_dead: bool
    estimated_resource_depletion: float
    cumulative_stress: float
