from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GoldLedger(Base):
    __tablename__ = "gold_ledger"
    __table_args__ = (
        Index("ix_gold_ledger_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    run_id: Mapped[str | None] = mapped_column(String(26))
    arena_id: Mapped[str | None] = mapped_column(String(26))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class AstralShardLedger(Base):
    __tablename__ = "astral_shard_ledger"
    __table_args__ = (
        Index("ix_astral_shard_ledger_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    run_id: Mapped[str | None] = mapped_column(String(26))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
