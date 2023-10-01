from sqlalchemy import Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base, Snipe
from typing import Optional


class UserSettings(Base):
    __tablename__ = "user_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snipe: Mapped[Optional[Snipe]] = relationship(backref="snipe")

    color: Mapped[str] = mapped_column(String(6))
    family_friendly: Mapped[bool] = mapped_column(Boolean)
    sniped: Mapped[bool] = mapped_column(Boolean)
    block_dms: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, color={self.color!r}, family_friendly={self.family_friendly!r}, sniped={self.sniped!r}, block_dms={self.block_dms!r})"
