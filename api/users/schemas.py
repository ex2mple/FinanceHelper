# import datetime

from pydantic import BaseModel, Field
from typing import Annotated, Literal


# class Role(BaseModel):
#     id: int
#     name: str


class UserBase(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: Annotated[str, Field(..., min_length=5, max_length=30)]
    password: Annotated[str, Field(..., min_length=7, max_length=255)]
    gender: Annotated[Literal["Male", "Female"], Field(...)]
    age: Annotated[int, Field(..., ge=0, le=99)]
    salary: Annotated[int, Field(..., ge=0)]


class UserSelfUpdate(UserCreate):
    pass
