from sqlalchemy import ForeignKey, Text, DateTime
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Advice(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    advice: Mapped[str] = mapped_column(Text)
    datetime_create: Mapped[DateTime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(
        back_populates="advices", uselist=False
    )
