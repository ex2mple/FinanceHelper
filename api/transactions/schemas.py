import datetime

from pydantic import BaseModel, Field
from typing import Annotated


class TransactionBase(BaseModel):
    id: int
    user_id: int
    category_id: int
    datetime: datetime.datetime
    amount: int


class TransactionCreate(BaseModel):
    user_id: Annotated[int, Field(...)]
    category_id: Annotated[int, Field(...)]
    datetime: Annotated[datetime.datetime, Field(...)]
    amount: Annotated[int, Field(..., ge=0)]


class TransactionSelfUpdate(BaseModel):
    category_id: Annotated[int | None, Field(...)]
    datetime: Annotated[datetime.datetime | None, Field(...)]
    amount: Annotated[int | None, Field(..., ge=0)]
