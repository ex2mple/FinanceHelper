from sqlalchemy import String, ForeignKey, Integer, BigInteger
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer)
    salary: Mapped[int] = mapped_column(BigInteger)
    email: Mapped[str] = mapped_column(String(100), unique=True)

    advices: Mapped["Advice"] = relationship(
        back_populates="user", uselist=True, cascade="all, delete-orphan"
    )
    categories: Mapped["Category"] = relationship(
        back_populates="user", uselist=True, cascade="all, delete-orphan"
    )
    transactions: Mapped["Transaction"] = relationship(
        back_populates="user", uselist=True, cascade="all, delete-orphan"
    )
