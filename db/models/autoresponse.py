from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Autoresponse(Base):
    __tablename__ = "autoresponse"
    server_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("server_settings.id"), primary_key=True
    )

    msg: Mapped[str] = mapped_column(String, primary_key=True)
    response: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Autoresponse(id={self.server_id!r}, msg={self.msg!r}, response={self.response!r})"
