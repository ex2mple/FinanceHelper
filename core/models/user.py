from sqlalchemy import String, ForeignKey, Integer
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(255))
    gender: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer)
    salary: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String, unique=True)
    # role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1)