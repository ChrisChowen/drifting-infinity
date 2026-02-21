from datetime import datetime

from pydantic import BaseModel


class GoldLedgerEntry(BaseModel):
    id: str
    campaign_id: str
    amount: int
    reason: str
    run_id: str | None
    arena_id: str | None
    created_at: datetime


class ShardLedgerEntry(BaseModel):
    id: str
    campaign_id: str
    amount: int
    reason: str
    run_id: str | None
    created_at: datetime


class EconomyBalance(BaseModel):
    gold_balance: int
    astral_shard_balance: int


class GoldAward(BaseModel):
    amount: int
    reason: str
    run_id: str | None = None
    arena_id: str | None = None


class ShardAward(BaseModel):
    amount: int
    reason: str
    run_id: str | None = None
