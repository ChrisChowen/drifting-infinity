from sqlalchemy import JSON, Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Floor(Base):
    __tablename__ = "floors"
    __table_args__ = (
        Index("ix_floors_run_id", "run_id"),
        Index("ix_floors_run_floor", "run_id", "floor_number"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), nullable=False)

    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    arena_count: Mapped[int] = mapped_column(Integer, nullable=False)
    arenas_completed: Mapped[int] = mapped_column(Integer, default=0)
    cr_minimum_offset: Mapped[int] = mapped_column(Integer, default=0)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Templates used this floor (avoid repetition)
    templates_used: Mapped[list] = mapped_column(JSON, default=list)

    # Objectives used this floor (avoid repetition) — Phase 7A
    objectives_used: Mapped[list] = mapped_column(JSON, default=list)

    # Active floor affixes (Mythic Plus style) — Phase 7B
    active_affixes: Mapped[list] = mapped_column(JSON, default=list)

    # Floor biome (constrains environments within this floor)
    floor_biome: Mapped[str | None] = mapped_column(String(30), default=None)

    # Floor theme (all arenas on this floor share this theme for narrative coherence)
    floor_theme: Mapped[str | None] = mapped_column(String(50), default=None)

    # Relationships
    run: Mapped["Run"] = relationship("Run", back_populates="floors")
    arenas: Mapped[list["Arena"]] = relationship(
        "Arena", back_populates="floor", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["HealthSnapshot"]] = relationship(
        "HealthSnapshot", back_populates="floor", cascade="all, delete-orphan"
    )


from app.models.arena import Arena  # noqa: E402, F401
from app.models.run import Run  # noqa: E402, F401
from app.models.snapshot import HealthSnapshot  # noqa: E402, F401
