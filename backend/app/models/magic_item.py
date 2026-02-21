from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MagicItem(Base):
    __tablename__ = "magic_items"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)  # common, uncommon, rare, very_rare, legendary
    type: Mapped[str] = mapped_column(String(100), nullable=False)   # Armor, Weapon, Wondrous item, Ring, etc.
    requires_attunement: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(50), default="srd-5.2")

    # Roguelike integration
    category: Mapped[str] = mapped_column(String(30), default="equipment")  # equipment, consumable, wondrous
    floor_min: Mapped[int] = mapped_column(Integer, default=1)
    gold_value: Mapped[int] = mapped_column(Integer, default=100)
