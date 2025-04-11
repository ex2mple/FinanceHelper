from fastapi import APIRouter, Depends, HTTPException, status
from api.users import schemas, crud
from core.models import db_helper, User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from .dependencies import user_by_id, user_by_username
from ..auth.security import get_password_hash
from ..auth.views import user_dependency
import os.path
router = APIRouter(tags=["Users"])
AVATARS_DIR = os.path.abspath('media/users_images/')
DEFAULT_PHOTO = os.path.join(AVATARS_DIR, "default.png")


@router.post(
    "/", response_model=schemas.UserCreate, status_code=status.HTTP_201_CREATED
)
async def create_user(
        user: schemas.UserCreate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> schemas.UserBase:
    user.password = get_password_hash(user.password)
    await crud.create_user(session=session, user_in=user)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User created successfully",
    )


@router.patch("/update", status_code=status.HTTP_204_NO_CONTENT)
async def self_user_update(
        data: schemas.UserSelfUpdate,
        current_user: user_dependency,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    if data.username and current_user.balance < 5000:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Not enough money to change the nickname",
        )
    await crud.self_update_user(session=session, user=current_user, data=data)


@router.get("/{username}", response_model=schemas.UserBase)
async def get_user(
        user: User = Depends(user_by_username),
) -> schemas.UserBase:
    return user


# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user: schemas.UserBase = Depends(user_by_id),
#     session: AsyncSession = Depends(db_helper.session_dependency),
# ) -> None:
#     await crud.delete_user(session=session, user=user)