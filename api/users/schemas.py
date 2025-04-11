# import datetime

from pydantic import BaseModel, Field
from typing import Annotated


# class Role(BaseModel):
#     id: int
#     name: str


class UserBase(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: Annotated[str, Field(..., min_length=5, max_length=30)]
    password: Annotated[str, Field(..., min_length=7, max_length=255)]


class UserSelfUpdate(BaseModel):
    username: Annotated[str | None, Field(min_length=5, max_length=30)]
    bio: Annotated[str | None, Field(max_length=50)]
    password: Annotated[str | None, Field(min_length=7, max_length=255)]