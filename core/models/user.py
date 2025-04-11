from sqlalchemy import String, ForeignKey
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str] = mapped_column(String(50), default="")
    # role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1)