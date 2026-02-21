from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Monster(Base):
    __tablename__ = "monsters"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="srd-5.2")

    # Core stats
    cr: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    xp: Mapped[int] = mapped_column(Integer, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_dice: Mapped[str | None] = mapped_column(String(20))
    ac: Mapped[int] = mapped_column(Integer, nullable=False)

    # Type/size
    size: Mapped[str | None] = mapped_column(String(20))
    creature_type: Mapped[str | None] = mapped_column(String(50))
    alignment: Mapped[str | None] = mapped_column(String(50))

    # Classified role
    tactical_role: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default="brute")
    secondary_role: Mapped[str | None] = mapped_column(String(20))

    # Intelligence tier (for behaviour profiles)
    intelligence_tier: Mapped[str] = mapped_column(String(20), default="instinctual")

    # Full MechanicalSignature as JSON
    mechanical_signature: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # BehaviourProfile as JSON
    behaviour_profile: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Weakness Exploit profile (denormalized for fast query)
    vulnerabilities: Mapped[list] = mapped_column(JSON, default=list)
    weak_saves: Mapped[list] = mapped_column(JSON, default=list)

    # Environment tags for map matching
    environments: Mapped[list] = mapped_column(JSON, default=list)

    # The complete statblock JSON from Open5e
    statblock: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Tagging metadata
    tagging_source: Mapped[str] = mapped_column(String(20), default="automated")
    tagging_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    last_tagged_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
