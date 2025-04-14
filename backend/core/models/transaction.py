from sqlalchemy import ForeignKey, DateTime, BigInteger, String
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Transaction(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categorys.id"))
    datetime: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    amount: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(100))

    user: Mapped["User"] = relationship(
        back_populates="transactions", uselist=False
    )
    category: Mapped["Category"] = relationship(
        back_populates="transactions", uselist=False
    )
