from pydantic import BaseModel, Field
from typing import Annotated

from api.users.schemas import UserBase


class CategoryBase(BaseModel):
    id: int
    user_id: int
    name: Annotated[str, Field(..., min_length=3, max_length=50)]
    color: Annotated[str, Field(...)]
    user: UserBase


class CategoryCreate(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=50)]
    color: Annotated[str, Field(...)]


class CategorySelfUpdate(BaseModel):
    user_id: Annotated[int | None, Field(default=None)]
    name: Annotated[str | None, Field(default=None, min_length=3, max_length=50)]
    color: Annotated[str | None, Field(default=None)]
