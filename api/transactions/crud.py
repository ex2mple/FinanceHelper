from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Transaction
from sqlalchemy import select
from .schemas import TransactionCreate, TransactionSelfUpdate


async def create_transaction(session: AsyncSession, transaction_in: TransactionCreate) -> Transaction:
    transaction = Transaction(**transaction_in.model_dump())
    session.add(transaction)
    await session.commit()
    return transaction


async def get_user_transactions(session: AsyncSession, user_id: int,
                                limit: int, offset: int) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.datetime)
        .offset(offset)
        .limit(limit)
    )
    transactions_all = (await session.scalars(stmt)).all()
    res = []
    for i in transactions_all:
        res.append(i)
    return res


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
