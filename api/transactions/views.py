import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .schemas import TransactionCreate, TransactionBase, TransactionSelfUpdate
from .crud import create_transaction, get_user_transactions, get_transaction, update_transaction, delete_transaction, \
    get_filtered_transactions, get_filtered_transactions_grouped
from core.models import db_helper, User, Category
from typing import Optional, Annotated

from ..auth.views import user_dependency
from ..utils.datetime_utils import make_timezone_aware

router = APIRouter(tags=["Transactions"])


@router.post("/create", response_model=TransactionBase, status_code=status.HTTP_201_CREATED)
async def create_new_transaction(
        transaction_in: TransactionCreate,
        current_user: user_dependency,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Создание новой транзакции.
    """
    stmt = (select(Category)
            .options(selectinload(Category.user))
            .options(selectinload(Category.transactions))
            .where(Category.id == transaction_in.category_id))
    category_exists = (await session.scalars(stmt)).first()
    if category_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    transaction = await create_transaction(session=session, transaction_in=transaction_in, user_id=current_user.id)
    return transaction


@router.post("/create/{user_id}", response_model=TransactionBase, status_code=status.HTTP_201_CREATED)
async def create_new_transaction_custom_user_id(
        user_id: Annotated[int, Path()],
        transaction_in: TransactionCreate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Создание новой транзакции.
    """
    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stmt = (select(Category)
            .options(selectinload(Category.user))
            .options(selectinload(Category.transactions))
            .where(Category.id == transaction_in.category_id))
    category_exists = (await session.scalars(stmt)).first()
    if category_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    transaction = await create_transaction(session=session, transaction_in=transaction_in, user_id=user_id)
    return transaction


@router.get("/my", response_model=list[TransactionBase])
async def get_transactions_by_user(
        current_user: user_dependency,
        limit: Optional[int] = Query(default=None, ge=0),
        offset: Optional[int] = Query(default=None, ge=0),
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[TransactionBase]:
    """
    Получение списка транзакций пользователя.
    """
    transactions = await get_user_transactions(session=session, user_id=current_user.id, limit=limit, offset=offset)
    return transactions


@router.get("/user/{user_id}", response_model=list[TransactionBase])
async def get_transactions_by_custom_user_id(
        user_id: Annotated[int, Path()],
        limit: Optional[int] = Query(default=None, ge=0),
        offset: Optional[int] = Query(default=None, ge=0),
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[TransactionBase]:
    """
    Получение списка транзакций пользователя.
    """
    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    transactions = await get_user_transactions(session=session, user_id=user_id, limit=limit, offset=offset)
    return transactions


@router.get("/{transaction_id}", response_model=TransactionBase)
async def get_transaction_by_id(
        transaction_id: Annotated[int, Path()],
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Получение транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


@router.patch("/{transaction_id}", response_model=TransactionBase)
async def update_transaction_by_id(
        current_user: user_dependency,
        transaction_id: Annotated[int, Path()],
        transaction_in: TransactionSelfUpdate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Обновление транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't update this transaction")

    updated_transaction = await update_transaction(session=session, transaction=transaction, transaction_in=transaction_in)
    return updated_transaction


@router.patch("/{transaction_id}/user/{user_id}", response_model=TransactionBase)
async def update_transaction_by_id_custom_user_id(
        transaction_id: Annotated[int, Path()],
        user_id: Annotated[int, Path()],
        transaction_in: TransactionSelfUpdate,
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionBase:
    """
    Обновление транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if transaction.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't update this transaction")

    updated_transaction = await update_transaction(session=session, transaction=transaction, transaction_in=transaction_in)
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_by_id(
        current_user: user_dependency,
        transaction_id: Annotated[int, Path()],
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    """
    Удаление транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete this transaction")

    await delete_transaction(session=session, transaction=transaction)


@router.delete("/{transaction_id}/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_by_id_custom_user_id(
    transaction_id: Annotated[int, Path()],
    user_id: Annotated[int, Path()],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    """
    Удаление транзакции по ID.
    """
    transaction = await get_transaction(session=session, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if transaction.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete this transaction")

    await delete_transaction(session=session, transaction=transaction)


@router.get("/filter", response_model=list[TransactionBase])
async def get_filtered_transactions_api(
    current_user: user_dependency,
    order_by: str = Query(default="asc", regex="^(asc|desc)$"),
    limit: Optional[int] = Query(default=None, ge=0),
    offset: Optional[int] = Query(default=None, ge=0),
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[TransactionBase]:
    """
        Получение списка транзакций с фильтрацией и сортировкой.
    """
    if start_date and end_date:
        start_date = make_timezone_aware(start_date)
        end_date = make_timezone_aware(end_date)
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be less than or equal to end_date",
            )

    transactions = await get_filtered_transactions(
        session=session,
        user_id=current_user.id,
        order_by=order_by,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
    )
    return transactions


@router.get("/group", response_model=list[tuple[str, float | int]])
async def get_filtered_transactions_grouped_api(
    current_user: user_dependency,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[tuple[str, float | int]]:
    """
    Получение списка транзакций с фильтрацией и группировкой по id.
    """
    if start_date and end_date:
        start_date = make_timezone_aware(start_date)
        end_date = make_timezone_aware(end_date)
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be less than or equal to end_date",
            )

    transactions = await get_filtered_transactions_grouped(
        session=session,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
    return transactions


@router.get("/filter/{user_id}", response_model=list[TransactionBase])
async def get_filtered_transactions_api_custom_user_id(
    user_id: Annotated[int, Path()],
    order_by: str = Query(default="asc", regex="^(asc|desc)$"),
    limit: Optional[int] = Query(default=None, ge=0),
    offset: Optional[int] = Query(default=None, ge=0),
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[TransactionBase]:
    """
        Получение списка транзакций с фильтрацией и сортировкой.
    """
    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if start_date and end_date:
        start_date = make_timezone_aware(start_date)
        end_date = make_timezone_aware(end_date)
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be less than or equal to end_date",
            )

    transactions = await get_filtered_transactions(
        session=session,
        user_id=user_id,
        order_by=order_by,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
    )
    return transactions


@router.get("/group/{user_id}", response_model=list[tuple[str, float | int]])
async def get_filtered_transactions_grouped_api_custom_user_id(
    user_id: Annotated[int, Path()],
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[tuple[str, float | int]]:
    """
    Получение списка транзакций с фильтрацией и группировкой по id.
    """
    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.scalars(stmt)).first()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if start_date and end_date:
        start_date = make_timezone_aware(start_date)
        end_date = make_timezone_aware(end_date)
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be less than or equal to end_date",
            )

    transactions = await get_filtered_transactions_grouped(
        session=session,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return transactions


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_avatar(
        current_user: user_dependency,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Загрузка новых транзакций для авторизованного юзера"""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )

        image_id = image_storage.upload_image(file)

        current_user.avatar_id = image_id
        await db.commit()

        return {"avatar_id": image_id}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )
