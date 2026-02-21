from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        Index("ix_runs_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)

    starting_level: Mapped[int] = mapped_column(Integer, nullable=False)
    floor_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Random seed for encounter variety
    seed: Mapped[int] = mapped_column(Integer, default=0)

    # Outcome tracking
    floors_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_gold_earned: Mapped[int] = mapped_column(Integer, default=0)
    total_shards_earned: Mapped[int] = mapped_column(Integer, default=0)
    outcome: Mapped[str | None] = mapped_column(String(20))

    # Difficulty curve data
    difficulty_curve: Mapped[list] = mapped_column(JSON, default=list)

    # Armillary's Favour
    armillary_favour: Mapped[int] = mapped_column(Integer, default=0)

    # Affix history across floors (Phase 7B)
    affix_history: Mapped[list] = mapped_column(JSON, default=list)

    # Death & respawn tracking (Phase 8)
    lives_remaining: Mapped[int] = mapped_column(Integer, default=3)
    total_deaths: Mapped[int] = mapped_column(Integer, default=0)
    death_log: Mapped[list] = mapped_column(JSON, default=list)

    # Meta-progression (Phase 9)
    essence_earned: Mapped[int] = mapped_column(Integer, default=0)
    meta_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    lore_beats_triggered: Mapped[list] = mapped_column(JSON, default=list)
    secret_events: Mapped[list] = mapped_column(JSON, default=list)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="runs")
    floors: Mapped[list["Floor"]] = relationship(
        "Floor", back_populates="run", cascade="all, delete-orphan"
    )


from app.models.campaign import Campaign  # noqa: E402, F401
from app.models.floor import Floor  # noqa: E402, F401
