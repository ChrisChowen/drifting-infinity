from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Spell(Base):
    __tablename__ = "spells"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 = cantrip, 1-9
    school: Mapped[str] = mapped_column(String(30), nullable=False)  # evocation, abjuration, etc.
    casting_time: Mapped[str] = mapped_column(String(100), default="")
    spell_range: Mapped[str] = mapped_column(String(100), default="")
    components: Mapped[str] = mapped_column(String(200), default="")  # "V, S, M (a pinch of dust)"
    duration: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(50), default="srd-5.2")
