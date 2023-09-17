from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from models.base import Base


class Hello(Base):
    __tablename__ = "hello"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    msg: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, msg={self.msg!r})"
