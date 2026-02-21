from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Character(Base):
    __tablename__ = "characters"
    __table_args__ = (
        Index("ix_characters_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    # Core identity
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    character_class: Mapped[str] = mapped_column(String(50), nullable=False)
    subclass: Mapped[str | None] = mapped_column(String(50))
    level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Combat stats
    ac: Mapped[int] = mapped_column(Integer, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, default=30)

    # Saves: {"str": 2, "dex": 5, ...}
    saves: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Damage types available: ["fire", "radiant", "slashing"]
    damage_types: Mapped[list] = mapped_column(JSON, default=list)

    # Capabilities checklist
    capabilities: Mapped[dict] = mapped_column(JSON, default=dict)

    # XP tracking
    xp_total: Mapped[int] = mapped_column(Integer, default=0)
    xp_to_next_level: Mapped[int] = mapped_column(Integer, default=300)

    # Gacha equipment slots
    variant_id: Mapped[str | None] = mapped_column(String(26))
    identity_id: Mapped[str | None] = mapped_column(String(26))
    weapon_id: Mapped[str | None] = mapped_column(String(26))

    # Death & respawn tracking (Phase 8)
    is_dead: Mapped[bool] = mapped_column(Boolean, default=False)
    death_count: Mapped[int] = mapped_column(Integer, default=0)
    replaced_by_id: Mapped[str | None] = mapped_column(String(26))
    is_replacement: Mapped[bool] = mapped_column(Boolean, default=False)
    original_character_id: Mapped[str | None] = mapped_column(String(26))

    # Meta-progression (Phase 9)
    run_deaths: Mapped[int] = mapped_column(Integer, default=0)
    scars: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="characters")
    enhancements: Mapped[list["CharacterEnhancement"]] = relationship(
        "CharacterEnhancement", cascade="all, delete-orphan"
    )


class CharacterEnhancement(Base):
    __tablename__ = "character_enhancements"
    __table_args__ = (
        Index("ix_char_enhancements_character_id", "character_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False)
    enhancement_id: Mapped[str] = mapped_column(String(26), nullable=False)
    slot_index: Mapped[int] = mapped_column(Integer, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


from app.models.campaign import Campaign  # noqa: E402, F401
