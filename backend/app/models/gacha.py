"""Gacha system models."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GachaPull(Base):
    __tablename__ = "gacha_pulls"
    __table_args__ = (
        Index("ix_gacha_pulls_campaign_banner", "campaign_id", "banner"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    banner: Mapped[str] = mapped_column(String(30), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)
    pull_number: Mapped[int] = mapped_column(Integer, nullable=False)
    result_type: Mapped[str] = mapped_column(String(20), nullable=False)
    result_id: Mapped[str] = mapped_column(String(26), nullable=False)
    result_name: Mapped[str] = mapped_column(String(100), nullable=False)
    was_pity: Mapped[bool] = mapped_column(Boolean, default=False)
    was_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class GachaBannerState(Base):
    __tablename__ = "gacha_banner_states"
    __table_args__ = (
        Index("ix_gacha_banner_states_campaign_banner", "campaign_id", "banner"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    banner: Mapped[str] = mapped_column(String(30), nullable=False)
    total_pulls: Mapped[int] = mapped_column(Integer, default=0)
    pulls_since_rare: Mapped[int] = mapped_column(Integer, default=0)
    pulls_since_very_rare: Mapped[int] = mapped_column(Integer, default=0)
    pulls_since_legendary: Mapped[int] = mapped_column(Integer, default=0)


class GachaVariant(Base):
    __tablename__ = "gacha_variants"
    __table_args__ = (
        Index("ix_gacha_variants_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)
    character_class: Mapped[str] = mapped_column(String(50), nullable=False)
    effect: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    equipped_to: Mapped[str | None] = mapped_column(String(26))


class GachaWeapon(Base):
    __tablename__ = "gacha_weapons"
    __table_args__ = (
        Index("ix_gacha_weapons_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)
    weapon_type: Mapped[str] = mapped_column(String(50), nullable=False)
    effect: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    equipped_to: Mapped[str | None] = mapped_column(String(26))


class GachaIdentity(Base):
    __tablename__ = "gacha_identities"
    __table_args__ = (
        Index("ix_gacha_identities_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)
    effect: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    equipped_to: Mapped[str | None] = mapped_column(String(26))
