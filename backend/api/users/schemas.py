from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Literal


class UserBase(BaseModel):
    id: int
    username: Annotated[str, Field(..., min_length=5, max_length=50)]
    email: Annotated[EmailStr, Field(..., max_length=100)]
    gender: Annotated[Literal["Male", "Female"], Field(...)]
    age: Annotated[int, Field(..., ge=0, le=99)]
    salary: Annotated[int, Field(..., ge=0)]


class UserCreate(BaseModel):
    username: Annotated[str, Field(..., min_length=5, max_length=50)]
    password: Annotated[str, Field(..., min_length=8, max_length=50)]
    gender: Annotated[Literal["Male", "Female"], Field(...)]
    age: Annotated[int, Field(..., ge=0, le=99)]
    salary: Annotated[int, Field(..., ge=0)]
    email: Annotated[EmailStr, Field(..., max_length=100)]


class UserSelfUpdate(BaseModel):
    username: Annotated[str | None, Field(default=None, min_length=5, max_length=50)]
    password: Annotated[str | None, Field(default=None, min_length=8, max_length=50)]
    gender: Annotated[Literal["Male", "Female"] | None, Field(default=None)]
    age: Annotated[int | None, Field(default=None, ge=0, le=99)]
    salary: Annotated[int | None, Field(default=None, ge=0)]
    email: Annotated[EmailStr | None, Field(default=None, max_length=100)]
