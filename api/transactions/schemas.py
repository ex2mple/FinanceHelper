import datetime

from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from api.categories.schemas import CategoryBase
from api.users.schemas import UserBase
from api.utils.datetime_utils import make_timezone_aware


class TransactionBase(BaseModel):
    id: int
    user_id: int
    category_id: int
    title: str
    datetime: datetime.datetime
    amount: int
    user: UserBase
    category: CategoryBase

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)


class TransactionCreate(BaseModel):
    title: Annotated[str, Field(...)]
    category_id: Annotated[int, Field(...)]
    datetime: Annotated[datetime.datetime, Field(...)]
    amount: Annotated[int, Field(...)]

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)


class TransactionSelfUpdate(BaseModel):
    title: Annotated[str | None, Field(default=None)]
    user_id: Annotated[int | None, Field(default=None)]
    category_id: Annotated[int | None, Field(default=None)]
    datetime: Annotated[datetime.datetime | None, Field(default=None)]
    amount: Annotated[int | None, Field(default=None)]

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)
