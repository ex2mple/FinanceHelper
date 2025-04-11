# import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Literal


# class Role(BaseModel):
#     id: int
#     name: str


class UserBase(BaseModel):
    id: int
    username: str
    email: str


class UserCreate(BaseModel):
    username: Annotated[str, Field(..., min_length=5, max_length=30)]
    password: Annotated[str, Field(..., min_length=7, max_length=255)]
    gender: Annotated[Literal["Male", "Female"], Field(...)]
    age: Annotated[int, Field(..., ge=0, le=99)]
    salary: Annotated[int, Field(..., ge=0)]
    email: Annotated[EmailStr, Field(...)]


class UserSelfUpdate(BaseModel):
        username: Annotated[str | None, Field(min_length=5, max_length=30)]
        password: Annotated[str | None, Field(min_length=7, max_length=255)]
        gender: Annotated[Literal["Male", "Female"] | None, Field(...)]
        age: Annotated[int | None, Field(ge=0, le=99)]
        salary: Annotated[int | None, Field(ge=0)]
        email: Annotated[EmailStr | None, Field(...)]
