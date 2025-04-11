from typing import Annotated
from fastapi import Depends, Path, HTTPException, status
from core.models import db_helper, User
from . import crud
from sqlalchemy.ext.asyncio import AsyncSession


async def user_by_id(
        user_id: Annotated[int, Path],
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> User:
    user: User = await crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


async def user_by_username(
        username: Annotated[str, Path],
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> User:
    user: User = await crud.get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user