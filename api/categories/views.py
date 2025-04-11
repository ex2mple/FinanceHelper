from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import CategoryCreate, CategoryBase, CategorySelfUpdate
from .crud import create_category, get_user_categories, get_category, update_category, delete_category
from core.models import db_helper, User, Category


router = APIRouter(tags=["Categories"])


@router.post("/create", response_model=CategoryBase, status_code=status.HTTP_201_CREATED)
async def create_new_category(
        category_in: CategoryCreate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> CategoryBase:
    """
    Создание новой категории.
    """
    stmt = select(User).where(User.id == category_in.user_id)
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    category = await create_category(session=session, category_in=category_in)
    return category


@router.get("/{user_id}", response_model=list[CategoryBase])
async def get_categories_by_user(
        user_id: int,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[CategoryBase]:
    """
    Получение списка категорий пользователя.
    """
    stmt = select(User).where(User.id == user_id)
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    categories = await get_user_categories(session=session, user_id=user_id)
    return categories


@router.get("/{category_id}", response_model=CategoryBase)
async def get_category_by_id(
        category_id: int,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> CategoryBase:
    """
    Получение категории по ID.
    """
    category = await get_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


@router.put("/{category_id}", response_model=CategoryBase)
async def update_category_by_id(
        category_id: int,
        category_in: CategorySelfUpdate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> CategoryBase:
    """
    Обновление категории по ID.
    """
    category = await get_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updated_category = await update_category(session=session, category=category, category_in=category_in)
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_by_id(
        category_id: int,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    """
    Удаление категории по ID.
    """
    category = await get_category(session=session, category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await delete_category(session=session, category=category)
