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
    datetime: datetime.datetime
    amount: int
    user: UserBase
    category: CategoryBase

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)


class TransactionCreate(BaseModel):
    category_id: Annotated[int, Field(...)]
    datetime: Annotated[datetime.datetime, Field(...)]
    amount: Annotated[int, Field(..., ge=0)]

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)


class TransactionSelfUpdate(BaseModel):
    user_id: Annotated[int | None, Field(default=None)]
    category_id: Annotated[int | None, Field(default=None)]
    datetime: Annotated[datetime.datetime | None, Field(default=None)]
    amount: Annotated[int | None, Field(default=None,  ge=0)]

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)
