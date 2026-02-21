from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RunInventory(Base):
    __tablename__ = "run_inventory"
    __table_args__ = (
        Index("ix_run_inventory_run_id", "run_id"),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    item_rarity: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # "reward", "shop", "gacha"
    is_consumed: Mapped[bool] = mapped_column(Boolean, default=False)
