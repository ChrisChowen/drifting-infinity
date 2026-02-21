from typing import Literal

from pydantic import BaseModel, Field

BalancePreset = Literal["relaxed", "standard", "challenging", "brutal"]


class CampaignSettings(BaseModel):
    # Balance preset (sets recommended defaults for all other balance fields)
    balance_preset: BalancePreset = "standard"

    # Core balance knobs
    leveling_speed: float = Field(default=1.0, ge=0.25, le=4.0)
    difficulty_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)
    gold_multiplier: float = Field(default=1.0, ge=0.25, le=4.0)
    shard_multiplier: float = Field(default=1.0, ge=0.25, le=4.0)
    xp_budget_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)

    # Early-game tuning
    early_game_scaling_factor: float = Field(
        default=0.85, ge=0.5, le=1.5,
        description="Multiplier for floors 1-5 XP budgets. <1.0 = easier early game.",
    )
    first_run_bonus_lives: int = Field(
        default=1, ge=0, le=3,
        description="Extra lives on a campaign's first run (when PPC has no history).",
    )

    # Armillary tuning
    armillary_aggression: float = Field(
        default=1.0, ge=0.5, le=2.0,
        description="Multiplier for Armillary hostile weight. <1.0 = fewer hostile events.",
    )

    # Other settings
    shop_frequency: float = Field(default=0.30, ge=0.0, le=1.0)
    max_level: int = Field(default=20, ge=1, le=20)
    environment_preference: str | None = None


# Preset defaults for quick configuration
BALANCE_PRESETS: dict[str, dict] = {
    "relaxed": {
        "leveling_speed": 1.2,
        "difficulty_multiplier": 0.8,
        "gold_multiplier": 1.3,
        "xp_budget_multiplier": 0.85,
        "early_game_scaling_factor": 0.75,
        "first_run_bonus_lives": 2,
        "armillary_aggression": 0.7,
    },
    "standard": {
        "leveling_speed": 1.0,
        "difficulty_multiplier": 1.0,
        "gold_multiplier": 1.0,
        "xp_budget_multiplier": 1.0,
        "early_game_scaling_factor": 0.85,
        "first_run_bonus_lives": 1,
        "armillary_aggression": 1.0,
    },
    "challenging": {
        "leveling_speed": 0.9,
        "difficulty_multiplier": 1.15,
        "gold_multiplier": 0.9,
        "xp_budget_multiplier": 1.1,
        "early_game_scaling_factor": 0.95,
        "first_run_bonus_lives": 0,
        "armillary_aggression": 1.2,
    },
    "brutal": {
        "leveling_speed": 0.8,
        "difficulty_multiplier": 1.3,
        "gold_multiplier": 0.75,
        "xp_budget_multiplier": 1.25,
        "early_game_scaling_factor": 1.0,
        "first_run_bonus_lives": 0,
        "armillary_aggression": 1.5,
    },
}


class CampaignCreate(BaseModel):
    name: str


class CampaignUpdate(BaseModel):
    name: str | None = None
    settings: dict | None = None


class CampaignResponse(BaseModel):
    id: str
    name: str
    party_power_coefficient: float
    total_runs: int
    gold_balance: int
    astral_shard_balance: int
    settings: dict
