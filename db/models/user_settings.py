from sqlalchemy import Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base, Snipe


class UserSettings(Base):
    __tablename__ = "user_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snipe: Mapped[Snipe] = relationship(backref="snipe")

    color: Mapped[str] = mapped_column(String(6))
    family_friendly: Mapped[bool] = mapped_column(Boolean)
    sniped: Mapped[bool] = mapped_column(Boolean)
    block_dms: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, msg={self.msg!r})"
