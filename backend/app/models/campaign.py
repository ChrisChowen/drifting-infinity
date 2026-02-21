from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Director state
    party_power_coefficient: Mapped[float] = mapped_column(Float, default=1.0)
    total_runs: Mapped[int] = mapped_column(Integer, default=0)

    # Currencies
    gold_balance: Mapped[int] = mapped_column(Integer, default=0)
    astral_shard_balance: Mapped[int] = mapped_column(Integer, default=0)

    # Configuration
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    characters: Mapped[list["Character"]] = relationship(
        "Character", back_populates="campaign", cascade="all, delete-orphan"
    )
    runs: Mapped[list["Run"]] = relationship(
        "Run", back_populates="campaign", cascade="all, delete-orphan"
    )
    meta: Mapped["CampaignMeta | None"] = relationship(
        "CampaignMeta", back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )


# Avoid circular import - import at module level for type checking only
from app.models.campaign_meta import CampaignMeta  # noqa: E402, F401
from app.models.character import Character  # noqa: E402, F401
from app.models.run import Run  # noqa: E402, F401
