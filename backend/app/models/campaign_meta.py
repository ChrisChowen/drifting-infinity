"""Campaign meta-progression state.

Tracks persistent between-run progression: essence currency, unlocked talents,
achievements, lore discoveries, and lifetime statistics.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CampaignMeta(Base):
    __tablename__ = "campaign_meta"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False, unique=True)

    # Essence currency
    essence_balance: Mapped[int] = mapped_column(Integer, default=0)
    essence_lifetime: Mapped[int] = mapped_column(Integer, default=0)

    # Talent tree
    unlocked_talents: Mapped[list] = mapped_column(JSON, default=list)

    # Achievements
    achievements: Mapped[list] = mapped_column(JSON, default=list)

    # Lifetime statistics
    total_runs_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_runs_won: Mapped[int] = mapped_column(Integer, default=0)
    highest_floor_reached: Mapped[int] = mapped_column(Integer, default=0)
    total_floors_cleared: Mapped[int] = mapped_column(Integer, default=0)
    total_deaths_all_runs: Mapped[int] = mapped_column(Integer, default=0)

    # Discovery tracking
    secret_floors_discovered: Mapped[list] = mapped_column(JSON, default=list)
    lore_fragments_found: Mapped[list] = mapped_column(JSON, default=list)
    antagonist_encounters: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="meta")


from app.models.campaign import Campaign  # noqa: E402, F401
