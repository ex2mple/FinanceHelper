from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User
from sqlalchemy import select
from .schemas import UserBase, UserCreate, UserSelfUpdate
from ..auth.security import get_password_hash


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    user = User(**user_in.model_dump())
    session.add(user)
    await session.commit()
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User:
    stmt = (
        select(User)
        .where(User.username == username)
        # .options( Вот здесь можно подключать relationship
        #     joinedload(User.stats),
        #     selectinload(User.awards),
        #     selectinload(User.items),
        #     # joinedload(User.gp),
        #     joinedload(User.role),
        # )
    )
    user = (await session.scalars(stmt)).first()
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    stmt = select(User).where(User.id == user_id)
    user = (await session.scalars(stmt)).first()
    return user

async def get_user_by_email(session: AsyncSession, email: str | EmailStr) -> User:
    stmt = select(User).where(User.email == email)
    user = (await session.scalars(stmt)).first()
    return user


async def get_user(session: AsyncSession, user_id: int) -> User:
    stmt = (
        select(User)
        .where(User.id == user_id)
    )
    user = (await session.scalars(stmt)).first()
    return user


async def self_update_user(
        session: AsyncSession, user: User, data: UserSelfUpdate
) -> None:
    if data.gender:
        user.gender = data.gender
    if data.age:
        user.age = data.age
    if data.salary:
        user.salary = data.salary
    if data.password:
        user.password = get_password_hash(data.password)
    await session.commit()


async def delete_user(session: AsyncSession, user: UserBase) -> None:
    await session.delete(user)
    await session.commit()
