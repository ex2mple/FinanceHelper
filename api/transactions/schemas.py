import datetime

from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from api.utils.datetime_utils import make_timezone_aware


class TransactionBase(BaseModel):
    id: int
    user_id: int
    category_id: int
    datetime: datetime.datetime
    amount: int

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)


class TransactionCreate(BaseModel):
    user_id: Annotated[int, Field(...)]
    category_id: Annotated[int, Field(...)]
    datetime: Annotated[datetime.datetime, Field(...)]
    amount: Annotated[int, Field(..., ge=0)]

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)


class TransactionSelfUpdate(BaseModel):
    category_id: Annotated[int | None, Field(...)]
    datetime: Annotated[datetime.datetime | None, Field(...)]
    amount: Annotated[int | None, Field(..., ge=0)]

    @field_validator('datetime')
    @classmethod
    def validate_datetime(cls, dt: datetime.datetime) -> datetime.datetime:
        return make_timezone_aware(dt)
