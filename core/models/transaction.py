from sqlalchemy import ForeignKey, DateTime, Integer
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Transaction(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categorys.id"))
    datetime: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    amount: Mapped[int] = mapped_column(Integer)
