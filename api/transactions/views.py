from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TransactionCreate, TransactionBase, TransactionSelfUpdate
from .crud import create_transaction, get_user_transactions, get_transaction, update_transaction, delete_transaction
from core.models import db_helper, User, Category


router = APIRouter(tags=["Transactions"],
                   prefix='/api/transactions')


@router.post("/create", response_model=TransactionBase, status_code=status.HTTP_201_CREATED)
async def create_new_transaction(
        transaction_in: TransactionCreate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Создание новой транзакции.
    """
    stmt = select(User).where(User.id == transaction_in.user_id)
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stmt = select(Category).where(Category.id == transaction_in.id)
    category_exists = (await session.scalars(stmt)).first()
    if category_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    transaction = await create_transaction(session=session, transaction_in=transaction_in)
    return transaction


@router.get("/{user_id}", response_model=list[TransactionBase])
async def get_transactions_by_user(
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[TransactionBase]:
    """
    Получение списка транзакций пользователя.
    """
    stmt = select(User).where(User.id == user_id)
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    transactions = await get_user_transactions(session=session, user_id=user_id, limit=limit, offset=offset)
    return transactions


@router.get("/{transaction_id}", response_model=TransactionBase)
async def get_transaction_by_id(
        transaction_id: int,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Получение транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


@router.put("/{transaction_id}", response_model=TransactionBase)
async def update_transaction_by_id(
        transaction_id: int,
        transaction_in: TransactionSelfUpdate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Обновление транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    updated_transaction = await update_transaction(session=session, transaction=transaction, transaction_in=transaction_in)
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_by_id(
        transaction_id: int,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    """
    Удаление транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    await delete_transaction(session=session, transaction=transaction)
