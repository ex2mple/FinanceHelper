import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Transaction
from sqlalchemy import select
from .schemas import TransactionCreate, TransactionSelfUpdate
from sqlalchemy import func

from ..categories.crud import get_category


async def create_transaction(session: AsyncSession, transaction_in: TransactionCreate) -> Transaction:
    transaction = Transaction(**transaction_in.model_dump())
    session.add(transaction)
    await session.commit()
    return transaction


async def get_user_transactions(session: AsyncSession, user_id: int,
                                limit: int | None, offset: int | None) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.datetime)
    )
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    transactions_all = (await session.scalars(stmt)).all()
    return transactions_all


async def get_transaction(session: AsyncSession, transaction_id: int) -> Transaction:
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    transaction = (await session.scalars(stmt)).first()
    return transaction


async def update_transaction(session: AsyncSession, transaction: Transaction,
                             transaction_in: TransactionSelfUpdate) -> Transaction:
    if transaction_in.category_id is not None:
        transaction.category_id = transaction_in.category_id
    if transaction_in.datetime is not None:
        transaction.datetime = transaction_in.datetime
    if transaction_in.amount is not None:
        transaction.amount = transaction_in.amount
    await session.refresh(transaction)
    return transaction


async def delete_transaction(session: AsyncSession, transaction: Transaction) -> None:
    await session.delete(transaction)
    await session.commit()


async def get_filtered_transactions(
    session: AsyncSession,
    user_id: int | None = None,
    order_by: str = "asc",
    limit: int | None = None,
    offset: int | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
) -> list[Transaction]:
    stmt = select(Transaction)

    # Фильтрация по user_id
    if user_id is not None:
        stmt = stmt.where(Transaction.user_id == user_id)

    # Сортировка
    if order_by == "desc":
        stmt = stmt.order_by(Transaction.datetime.desc())
    else:
        stmt = stmt.order_by(Transaction.datetime.asc())

    # Фильтрация по дате
    if start_date is not None:
        stmt = stmt.where(Transaction.datetime >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.datetime <= end_date)

    # Применение offset и limit
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return result.all()


async def get_filtered_transactions_grouped(
    session: AsyncSession,
    user_id: int | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
) -> list[tuple[str, float | int]]:
    stmt = select(Transaction.category_id, func.sum(Transaction.amount).label("total_amount"))

    # Фильтрация по user_id
    if user_id is not None:
        stmt = stmt.where(Transaction.user_id == user_id)

    # Фильтрация по дате
    if start_date is not None:
        stmt = stmt.where(Transaction.datetime >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.datetime <= end_date)

    # Группировка по category_id
    stmt = stmt.group_by(Transaction.category_id)
    result = (await session.execute(stmt)).all()
    res = []
    for cat in result:
        cat_name = await get_category(session=session, category_id=cat[0])
        res.append((cat_name.name, cat[1]))
    return res
