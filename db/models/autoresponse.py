from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Autoresponse(Base):
    __tablename__ = "autoresponse"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("server_settings.id"))

    msg: Mapped[str] = mapped_column(String)
    response: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Autoresponse(id={self.id!r}, msg={self.msg!r}, response={self.response!r})"
