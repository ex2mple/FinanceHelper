from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import Category, Advice
from sqlalchemy import select, or_
from .schemas import AdviceSelfUpdate, AdviceCreate


async def create_advice(session: AsyncSession, advice_in: AdviceCreate) -> Advice:
    advice = Advice(**advice_in.model_dump())
    session.add(advice)
    await session.commit()
    await session.refresh(advice, ["user"])
    return advice


async def get_user_advices(session: AsyncSession, user_id: int) -> list[Advice]:
    stmt = (
        select(Advice)
        .options(selectinload(Advice.user))
        .filter(Advice.user_id == user_id)
        .order_by(Advice.datetime.desc())
    )
    advices_all = (await session.execute(stmt)).scalars().all()
    return advices_all


async def get_advice(session: AsyncSession, advice_id: int) -> Advice:
    stmt = (select(Advice)
            .options(selectinload(Advice.user))
            .where(Advice.id == advice_id))
    advice = (await session.execute(stmt)).scalar_one_or_none()
    return advice


async def update_advice(session: AsyncSession, advice: Advice,
                             advice_in: AdviceSelfUpdate) -> Advice:
    if advice_in.user_id is not None:
        advice.user_id = advice_in.user_id
    if advice_in.name is not None:
        advice.name = advice_in.name
    await session.commit()
    await session.refresh(advice, ["user"])
    return advice


async def delete_advice(session: AsyncSession, advice: Advice) -> None:
    await session.delete(advice)
    await session.commit()
