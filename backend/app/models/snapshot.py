from sqlalchemy import JSON, Boolean, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HealthSnapshot(Base):
    __tablename__ = "health_snapshots"
    __table_args__ = (
        Index("ix_health_snapshots_floor_id", "floor_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    floor_id: Mapped[str] = mapped_column(ForeignKey("floors.id"), nullable=False)
    after_arena_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Quick mode (always present)
    dm_assessment: Mapped[str] = mapped_column(String(20), nullable=False)
    dm_combat_perception: Mapped[str | None] = mapped_column(String(20), nullable=True)
    any_on_final_stand: Mapped[bool] = mapped_column(Boolean, default=False)

    # Per-character data
    character_snapshots: Mapped[list] = mapped_column(JSON, nullable=False)

    # Computed fields
    average_hp_percentage: Mapped[float] = mapped_column(Float, default=1.0)
    lowest_hp_percentage: Mapped[float] = mapped_column(Float, default=1.0)
    any_dead: Mapped[bool] = mapped_column(Boolean, default=False)
    deaths_count: Mapped[int] = mapped_column(Integer, default=0)
    was_tpk: Mapped[bool] = mapped_column(Boolean, default=False)
    estimated_resource_depletion: Mapped[float] = mapped_column(Float, default=0.0)
    cumulative_stress: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationship
    floor: Mapped["Floor"] = relationship("Floor", back_populates="snapshots")


from app.models.floor import Floor  # noqa: E402, F401
