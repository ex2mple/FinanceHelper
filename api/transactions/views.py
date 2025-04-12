import csv
import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File
from pydantic import Field
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .schemas import TransactionCreate, TransactionBase, TransactionSelfUpdate, TransactionCSVUpload
from .crud import create_transaction, get_user_transactions, get_transaction, update_transaction, delete_transaction, \
    get_filtered_transactions, get_filtered_transactions_grouped
from core.models import db_helper, User, Category
from typing import Optional, Annotated

from ..auth.views import user_dependency
from ..categories.crud import create_category
from ..categories.schemas import CategoryCreate
from ..utils.datetime_utils import make_timezone_aware

from io import StringIO

from ..utils.system import generate_beautiful_color

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
    category_exists = (await session.execute(stmt)).scalar_one_or_none()
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
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stmt = (select(Category)
            .options(selectinload(Category.user))
            .options(selectinload(Category.transactions))
            .where(Category.id == transaction_in.category_id))
    category_exists = (await session.execute(stmt)).scalar_one_or_none()
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
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
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
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
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
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
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


@router.get("/group", response_model=list[tuple[str, int]])
async def get_filtered_transactions_grouped_api(
    current_user: user_dependency,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[tuple[str, int]]:
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
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
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


@router.get("/group/{user_id}", response_model=list[tuple[str, int]])
async def get_filtered_transactions_grouped_api_custom_user_id(
    user_id: Annotated[int, Path()],
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[tuple[str, int]]:
    """
    Получение списка транзакций с фильтрацией и группировкой по id.
    """
    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
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


@router.post("/upload", status_code=status.HTTP_201_CREATED,
             response_model=TransactionCSVUpload)
async def upload_transaction_in_csv(
    current_user: user_dependency,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> TransactionCSVUpload:
    """Загрузка новых транзакций из CSV-файла для авторизованного пользователя"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть в формате CSV"
            )

        # Типы операций, которые считаются расходами (сумма будет отрицательной)
        expense_transaction_types = {'ATR', 'ATT', 'FEE', 'GCS', 'PUC', 'RCI', 'RCU', 'RET', 'TOT', 'TRM', 'TRS', 'UCH'}
        transaction_type_descriptions = {
            'ADO': 'Пополнение с карты другого банка',
            'ATR': 'Списание для операции округления',
            'ATT': 'Пополнение брокерского счёта',
            'CHB': 'Вознаграждение за операции покупок',
            'DIN': 'Проценты на остаток по счету',
            'FEE': 'Комиссия',
            'PAY': 'Пополнение',
            'PUC': 'Покупка',
            'RCI': 'Оплата задолженности по кредиту',
            'RCU': 'Списание с расчетного счета для оплаты кредита',
            'RET': 'Перевод',
            'TOT': 'Перевод на карту другого банка',
            'TRM': 'Перевод по реквизитам карты через МПС',
            'TRS': 'Перевод по реквизитам карты',
            'UCH': 'Оплата услуг'
        }

        # Чтение содержимого файла
        contents = await file.read()
        contents = contents.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(contents))

        created_transactions = []
        errors = []
        category_cache = {}  # Кэш для категорий

        for row_num, row in enumerate(csv_reader, start=1):
            try:
                # Получаем данные из строки CSV
                transaction_type = row.get('transaction_type_cd', '')
                category_name = row.get('loyalty_cashback_category_nm', '')
                date_str = row.get('real_transaction_dttm', '')
                amount_str = row.get('transaction_amt_rur', '0')

                # Проверяем обязательные поля
                if not transaction_type or not date_str or not amount_str:
                    print(f'<{transaction_type}>, <{category_name}>, <{date_str}>, <{amount_str}>')
                    errors.append(f"Строка {row_num}: отсутствуют обязательные поля")
                    continue

                # Преобразование категории
                if not category_name or category_name == '0':
                    category_name = 'Другое'

                # Преобразование даты в формате DD.MM.YYYY HH:MI в datetime
                try:
                    datetime_obj = datetime.datetime.strptime(date_str, '%d.%m.%Y %H:%M')
                    datetime_obj = make_timezone_aware(datetime_obj)
                except ValueError:
                    errors.append(f"Строка {row_num}: неверный формат даты '{date_str}'")
                    continue

                # Преобразование суммы
                try:
                    amount = int(float(amount_str.replace(',', '.')))
                    # Если тип транзакции подразумевает расход, делаем сумму отрицательной
                    if transaction_type in expense_transaction_types:
                        amount = -abs(amount)
                except ValueError:
                    errors.append(f"Строка {row_num}: неверный формат суммы '{amount_str}'")
                    continue

                # Находим или создаем категорию
                if category_name in category_cache:
                    category_id = category_cache[category_name]
                else:
                    # Ищем категорию по имени (используя LIKE для нечеткого поиска)
                    stmt = (select(Category)
                            .filter(Category.name.ilike(f"%{category_name}%"),
                                    or_(Category.user_id == current_user.id, Category.user_id == -1)))
                    category = (await session.execute(stmt)).scalar_one_or_none()

                    if not category:
                        # Создаем новую категорию
                        category_in = CategoryCreate(name=category_name,
                                                     color=generate_beautiful_color())
                        category = await create_category(
                            session=session,
                            category_in=category_in,
                            user_id=current_user.id
                        )

                    category_id = category.id
                    category_cache[category_name] = category_id

                # Создаем объект TransactionCreate
                transaction_data = {
                    "title": transaction_type_descriptions.get(transaction_type, 'Неизвестная операция'),
                    "amount": amount,
                    "category_id": category_id,
                    "datetime": datetime_obj
                }

                transaction_in = TransactionCreate(**transaction_data)

                # Создаем транзакцию
                transaction = await create_transaction(
                    session=session,
                    transaction_in=transaction_in,
                    user_id=current_user.id
                )
                created_transactions.append(transaction)

            except Exception as e:
                errors.append(f"Строка {row_num}: {str(e)}")

        return TransactionCSVUpload(created_transactions_count=len(created_transactions), errors=errors,
                                    transactions=created_transactions)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки файла: {str(e)}"
        )
