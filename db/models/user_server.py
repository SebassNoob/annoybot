from sqlalchemy import Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user_settings import UserSettings
from .server_settings import ServerSettings


class UserServer(Base):
    __tablename__ = "user_server"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("server_settings.id"))
    server: Mapped[ServerSettings] = relationship(backref="server_settings")

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_settings.id"))
    user: Mapped[UserSettings] = relationship(backref="user_settings")

    blacklist: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"UserServer(id={self.id!r}, server_ids={self.server_id!r}, user_ids={self.user_id!r}, blacklist={self.blacklist!r})"
