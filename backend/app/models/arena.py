from sqlalchemy import JSON, Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Arena(Base):
    __tablename__ = "arenas"
    __table_args__ = (
        Index("ix_arenas_floor_id", "floor_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    floor_id: Mapped[str] = mapped_column(ForeignKey("floors.id"), nullable=False)

    arena_number: Mapped[int] = mapped_column(Integer, nullable=False)
    encounter_template: Mapped[str | None] = mapped_column(String(50))
    difficulty_target: Mapped[float | None] = mapped_column(Float)
    xp_budget: Mapped[int | None] = mapped_column(Integer)
    adjusted_xp: Mapped[int | None] = mapped_column(Integer)
    actual_difficulty: Mapped[str | None] = mapped_column(String(20))
    gold_earned_per_player: Mapped[int] = mapped_column(Integer, default=0)
    tactical_brief: Mapped[str | None] = mapped_column(Text)
    map_id: Mapped[str | None] = mapped_column(String(50))
    environment: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    momentum_bonus_earned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Objective tracking (Phase 7A)
    objective: Mapped[str | None] = mapped_column(String(50))
    objective_progress: Mapped[dict | None] = mapped_column(JSON)

    # Social encounter tracking
    is_social: Mapped[bool] = mapped_column(Boolean, default=False)
    social_encounter_id: Mapped[str | None] = mapped_column(String(50))
    social_encounter_result: Mapped[dict | None] = mapped_column(JSON)

    # Secret event tracking
    secret_event_id: Mapped[str | None] = mapped_column(String(50))

    # DM override fields (Dynamic Sourcebook)
    dm_notes: Mapped[str | None] = mapped_column(Text)
    custom_read_aloud: Mapped[str | None] = mapped_column(Text)
    narrative_content: Mapped[dict | None] = mapped_column(JSON)

    # Relationships
    floor: Mapped["Floor"] = relationship("Floor", back_populates="arenas")
    creatures: Mapped[list["ArenaCreatureStatus"]] = relationship(
        "ArenaCreatureStatus", cascade="all, delete-orphan"
    )
    armillary_effects: Mapped[list["ArmillaryEffect"]] = relationship(
        "ArmillaryEffect", cascade="all, delete-orphan"
    )


class ArenaCreatureStatus(Base):
    """Simplified creature tracking — status only, no HP or conditions.

    The DM tracks HP, conditions, and initiative in their own VTT.
    We only track alive/bloodied/defeated for difficulty analysis.
    """

    __tablename__ = "arena_creatures"
    __table_args__ = (
        Index("ix_arena_creatures_arena_id", "arena_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    arena_id: Mapped[str] = mapped_column(ForeignKey("arenas.id"), nullable=False)
    monster_id: Mapped[str] = mapped_column(String(26), nullable=False)

    instance_label: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="alive")  # alive / bloodied / defeated
    is_reinforcement: Mapped[bool] = mapped_column(Boolean, default=False)


class ArmillaryEffect(Base):
    __tablename__ = "armillary_effects"
    __table_args__ = (
        Index("ix_armillary_effects_arena_id", "arena_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    arena_id: Mapped[str] = mapped_column(ForeignKey("arenas.id"), nullable=False)

    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    effect_key: Mapped[str] = mapped_column(String(50), nullable=False)
    effect_description: Mapped[str] = mapped_column(Text, nullable=False)
    xp_cost: Mapped[int] = mapped_column(Integer, default=0)
    was_overridden: Mapped[bool] = mapped_column(Boolean, default=False)
    was_rerolled: Mapped[bool] = mapped_column(Boolean, default=False)


from app.models.floor import Floor  # noqa: E402, F401
