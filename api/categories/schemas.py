from pydantic import BaseModel, Field
from typing import Annotated


class CategoryBase(BaseModel):
    id: int
    user_id: int
    name: str
    color: str


class CategoryCreate(BaseModel):
    user_id: Annotated[int, Field(...)]
    name: Annotated[str, Field(...)]
    color: Annotated[str, Field(...)]


class CategorySelfUpdate(BaseModel):
    user_id: Annotated[int | None, Field(default=None)]
    name: Annotated[str | None, Field(default=None)]
    color: Annotated[str | None, Field(default=None)]
