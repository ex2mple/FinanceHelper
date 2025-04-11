from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime


class AdviceBase(BaseModel):
    id: int
    user_id: int
    advice: str
    datetime_create: datetime


class AdviceCreate(BaseModel):
    user_id: Annotated[int, Field(...)]
    advice: Annotated[str, Field(...)]
    datetime_create: Annotated[datetime, Field(...)]


class AdviceSelfUpdate(BaseModel):
    user_id: Annotated[int | None, Field(...)]
    advice: Annotated[str | None, Field(...)]
    datetime_create: Annotated[datetime | None, Field(...)]
