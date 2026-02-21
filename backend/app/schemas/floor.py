from pydantic import BaseModel, Field


class FloorCreate(BaseModel):
    arena_count: int = Field(ge=2, le=6, default=4)


class FloorResponse(BaseModel):
    id: str
    run_id: str
    floor_number: int
    arena_count: int
    arenas_completed: int
    cr_minimum_offset: int
    is_complete: bool
    templates_used: list
    objectives_used: list = []
    active_affixes: list = []
