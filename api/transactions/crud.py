import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import Transaction, Category
from sqlalchemy import select
from .schemas import TransactionCreate, TransactionSelfUpdate
from sqlalchemy import func

from ..categories.crud import get_category
from ..utils.datetime_utils import make_timezone_aware


async def create_transaction(session: AsyncSession, transaction_in: TransactionCreate,
                             user_id: int) -> Transaction:
    transaction = Transaction(user_id=user_id,
                              **transaction_in.model_dump())
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction, ["category", "user"])
    return transaction


async def get_user_transactions(session: AsyncSession, user_id: int,
                                limit: int | None, offset: int | None) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.category).selectinload(Category.user))
        .options(selectinload(Transaction.user))
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.datetime)
    )
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    transactions_all = (await session.execute(stmt)).scalars().all()
    return transactions_all


async def get_transaction(session: AsyncSession, transaction_id: int) -> Transaction:
    stmt = (select(Transaction)
            .options(selectinload(Transaction.category),
                     selectinload(Transaction.user))
            .where(Transaction.id == transaction_id))
    transaction = (await session.execute(stmt)).scalar_one_or_none()
    return transaction


async def update_transaction(session: AsyncSession, transaction: Transaction,
                             transaction_in: TransactionSelfUpdate) -> Transaction:
    if transaction_in.user_id is not None:
        transaction.user_id = transaction_in.user_id
    if transaction_in.category_id is not None:
        transaction.category_id = transaction_in.category_id
    if transaction_in.title is not None:
        transaction.title = transaction_in.title
    if transaction_in.datetime is not None:
        transaction.datetime = transaction_in.datetime
    if transaction_in.amount is not None:
        transaction.amount = transaction_in.amount
    await session.commit()
    await session.refresh(transaction, ["category", "user"])
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
    stmt = (select(Transaction)
            .options(selectinload(Transaction.category).selectinload(Category.user))
            .options(selectinload(Transaction.user)))

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
        start_date = make_timezone_aware(start_date)
        stmt = stmt.where(Transaction.datetime >= start_date)
    if end_date is not None:
        end_date = make_timezone_aware(end_date)
        stmt = stmt.where(Transaction.datetime <= end_date)

    # Применение offset и limit
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_filtered_transactions_grouped(
    session: AsyncSession,
    user_id: int | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
) -> list[tuple[str, int]]:
    stmt = (select(Category.name, func.sum(Transaction.amount).label("total_amount"))
            .join(Category))

    # Фильтрация по user_id
    if user_id is not None:
        stmt = stmt.where(Transaction.user_id == user_id)

    # Фильтрация по дате
    if start_date is not None:
        start_date = make_timezone_aware(start_date)
        stmt = stmt.where(Transaction.datetime >= start_date)
    if end_date is not None:
        end_date = make_timezone_aware(end_date)
        stmt = stmt.where(Transaction.datetime <= end_date)

    # Группировка по category_id
    stmt = stmt.group_by(Category.name)
    result = (await session.execute(stmt)).all()
    return result
