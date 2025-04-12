from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Category
from sqlalchemy import select, or_
from .schemas import CategoryCreate, CategorySelfUpdate


async def create_category(session: AsyncSession, category_in: CategoryCreate) -> Category:
    category = Category(**category_in.model_dump())
    session.add(category)
    await session.commit()
    return category


async def get_user_categories(session: AsyncSession, user_id: int) -> list[Category]:
    stmt = (
        select(Category)
        .filter(or_(Category.user_id == user_id, Category.user_id == -1))
        .order_by(Category.name)
    )
    categories_all = (await session.scalars(stmt)).all()
    return categories_all


async def get_category(session: AsyncSession, category_id: int) -> Category:
    stmt = select(Category).where(Category.id == category_id)
    category = (await session.scalars(stmt)).first()
    return category


async def update_category(session: AsyncSession, category: Category,
                          category_in: CategorySelfUpdate) -> Category:
    if category_in.user_id is not None:
        category.user_id = category_in.user_id
    if category_in.name is not None:
        category.name = category_in.name
    if category_in.color is not None:
        category.color = category_in.color
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category: Category) -> None:
    await session.delete(category)
    await session.commit()
