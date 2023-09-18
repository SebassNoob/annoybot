from sqlalchemy import Integer, Boolean, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Snipe(Base):
    __tablename__ = "snipe"
    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_settings.id"), primary_key=True
    )

    msg: Mapped[str] = mapped_column(String)
    date: Mapped[DateTime] = mapped_column(DateTime)
    nsfw: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"Snipe(id={self.id!r}, msg={self.msg!r}, date={self.date!r}, nsfw={self.nsfw!r})"
