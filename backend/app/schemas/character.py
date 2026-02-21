from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str
    character_class: str
    subclass: str | None = None
    level: int = Field(ge=1, le=20)
    ac: int = Field(ge=1, le=30)
    max_hp: int = Field(ge=1)
    speed: int = 30
    saves: dict[str, int] = {}
    damage_types: list[str] = []
    capabilities: dict[str, bool] = {}


class CharacterUpdate(BaseModel):
    name: str | None = None
    character_class: str | None = None
    subclass: str | None = None
    level: int | None = Field(default=None, ge=1, le=20)
    ac: int | None = Field(default=None, ge=1, le=30)
    max_hp: int | None = Field(default=None, ge=1)
    speed: int | None = None
    saves: dict[str, int] | None = None
    damage_types: list[str] | None = None
    capabilities: dict[str, bool] | None = None


class CharacterResponse(BaseModel):
    id: str
    campaign_id: str
    name: str
    character_class: str
    subclass: str | None
    level: int
    ac: int
    max_hp: int
    speed: int
    saves: dict[str, int]
    damage_types: list[str]
    capabilities: dict
    variant_id: str | None
    identity_id: str | None
    weapon_id: str | None
    xp_total: int = 0
    xp_to_next_level: int = 300
    is_dead: bool = False
    death_count: int = 0
    is_replacement: bool = False
    original_character_id: str | None = None
    replaced_by_id: str | None = None


class LevelUpData(BaseModel):
    new_max_hp: int = Field(ge=1)
    new_ac: int | None = None
    new_saves: dict | None = None
    new_capabilities: dict | None = None
