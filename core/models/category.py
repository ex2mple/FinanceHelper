from sqlalchemy import ForeignKey, String
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Category(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    color: Mapped[str] = mapped_column(String)
