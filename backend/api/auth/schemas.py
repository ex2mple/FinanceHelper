from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Annotated[EmailStr | None, Field(default=None)]
