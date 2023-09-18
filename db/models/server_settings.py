from sqlalchemy import Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .autoresponse import Autoresponse
from typing import List


class ServerSettings(Base):
    __tablename__ = "server_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    autoresponse_on: Mapped[bool] = mapped_column(Boolean)
    autoresponses: Mapped[List[Autoresponse]] = relationship(backref="autoresponse")

    def __repr__(self) -> str:
        return (
            f"ServerSettings(id={self.id!r}, autoresponse_on={self.autoresponse_on!r})"
        )
