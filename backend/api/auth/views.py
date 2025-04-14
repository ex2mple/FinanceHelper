from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, APIRouter, Response, Cookie, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from core.models import db_helper, User
from sqlalchemy.ext.asyncio import AsyncSession
from api.users.crud import get_user_by_username, get_user_by_email
from .schemas import Token, TokenData
from api.users.schemas import UserBase
from .security import verify_password

# from core.config import RoleId
router = APIRouter(tags=["Auth"])

SECRET_KEY = "ce641aabf56e3d7ef3d7f8a9e16fb52ad5d3b2f2233d3977dbc1dbee024e264c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 21  # 21 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
session_dependency = Annotated[
    AsyncSession, Depends(db_helper.session_dependency)
]  # Связь с БД | получение сессии


async def get_current_user(
        session: session_dependency, token: Annotated[str | None, Cookie()] = None
) -> User:
    if token is None:
        token: str = Depends(oauth2_scheme)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_email(session, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


user_dependency = Annotated[
    UserBase, Depends(get_current_user)
]  # Зависимость от текущего пользователя


async def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(session, email: str, password: str) -> User | bool:
    user: User = await get_user_by_email(session, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
        response: Response,
        request: Request,
        session: session_dependency,
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    user: User = await authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    remember = (await request.form()).get("remember") == 'true'
    access_token = await create_access_token(
        data={"sub": user.email},
        expires_delta=ACCESS_TOKEN_EXPIRE_DAYS if remember else None,
    )
    expires = (
        (datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)) if remember else None
    )

    response.set_cookie(key="token", value=access_token, httponly=True, expires=expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserBase)
def get_me(current_user: user_dependency):
    return current_user


# @router.get("/is_admin")
# def is_user_admin(current_user: user_dependency):
#     return current_user.role_id in [RoleId.ADMIN.value, RoleId.OWNER.value]


@router.get("/logout")
def logout_me(response: Response):
    response.delete_cookie(key="token")
    return {"message": "You have been logged out."}
