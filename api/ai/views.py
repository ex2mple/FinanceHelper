import datetime
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, HTTPException, Body, Depends, Path, status

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.auth.views import user_dependency
from api.transactions.crud import get_filtered_transactions_grouped
from api.utils.system import default_categories, convert_category_to_numeric, CATEGORY_NAMES, categories
from core.config import settings
from core.models import db_helper, User

import aiohttp

router = APIRouter(tags=["AI"])


from mistralai import Mistral


class MessageRequest(BaseModel):
    request: str = Field(..., min_length=5, max_length=500)


class MessageResponse(BaseModel):
    response: str = Field(...)


@router.post("/ask", response_model=MessageResponse)
async def ask_agent(
    model: Annotated[Literal["small", "large"], Field(...)],
    request: Annotated[MessageRequest, Body()]
) -> MessageResponse:
    try:
        agent_id = settings.mistral_large_agent_id
        if model == "small":
            agent_id = settings.mistral_small_agent_id

        client = Mistral(api_key=settings.mistral_api_key)
        chat_response = await client.agents.complete_async(
            agent_id=agent_id,
            messages=[
                {
                    "role": "user",
                    "content": request.request,
                },
            ],
        )
        response = chat_response.choices[0].message.content

        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )


@router.post("/advice", response_model=MessageResponse)
async def ask_agent_advice(
    current_user: user_dependency,
    request: Annotated[MessageRequest, Body()],
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> MessageResponse:
    today = datetime.datetime.now()
    last_month = today - datetime.timedelta(days=30)
    res = await get_filtered_transactions_grouped(session=session, user_id=current_user.id,
                                                  start_date=last_month, end_date=today)

    reversed_CATEGORY_NAMES = {v: k for k, v in CATEGORY_NAMES.items()}
    reversed_categories = {v: k for k, v in categories.items()}
    params = {}
    for category in res:
        title, color, summ = category
        title_int = convert_category_to_numeric(title)
        title = 'expense_' + CATEGORY_NAMES[title_int]
        if title not in params:
            params[title] = summ
        else:
            params[title] += summ
    params['age'] = current_user.age
    params['gender'] = current_user.gender[0]
    params['income'] = current_user.salary

    text = (f"\n\nМой возраст: {params['age']} лет\n"
            f"Мой пол: {params['gender']}\n"
            f"Моя зарплата: {params['income']}\n"
            f"Вот информация о моих реальных и предсказанных тратах по категориям:\n")
    http_session = aiohttp.ClientSession()
    try:
        async with http_session.get('127.0.0.1:8080/overspending', params=params) as resp:
            data = await resp.json()
            overspending_categories = data['overspending_categories']
            for cat in overspending_categories:
                cat_int = reversed_CATEGORY_NAMES[cat]
                cat_my = reversed_categories[cat_int]
                text += (f'Категория "{cat_my}": '
                         f'Реальные траты: {overspending_categories[cat][0]}, '
                         f'Ождиаемые траты: {overspending_categories[cat][1]}\n')
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )
    finally:
        await http_session.close()

    try:
        agent_id = settings.mistral_large_agent_id

        client = Mistral(api_key=settings.mistral_api_key)
        print(f'Запрос: {request.request + text}')
        chat_response = await client.agents.complete_async(
            agent_id=agent_id,
            messages=[
                {
                    "role": "user",
                    "content": request.request + text,
                },
            ],
        )
        response = chat_response.choices[0].message.content

        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )


@router.post("/advice/user/{user_id}", response_model=MessageResponse)
async def ask_agent_advice(
    user_id: Annotated[int, Path()],
    request: Annotated[MessageRequest, Body()],
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> MessageResponse:
    stmt = (select(User)
            .options(selectinload(User.transactions))
            .options(selectinload(User.categories))
            .options(selectinload(User.advices))
            .where(User.id == user_id))
    user_exists = (await session.execute(stmt)).scalar_one_or_none()
    if user_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    today = datetime.datetime.now()
    last_month = today - datetime.timedelta(days=30)
    res = await get_filtered_transactions_grouped(session=session, user_id=user_id,
                                                  start_date=last_month, end_date=today)

    reversed_CATEGORY_NAMES = {v: k for k, v in CATEGORY_NAMES.items()}
    reversed_categories = {v: k for k, v in categories.items()}
    params = {}
    for category in res:
        title, color, summ = category
        title_int = convert_category_to_numeric(title)
        title = 'expense_' + CATEGORY_NAMES[title_int]
        if title not in params:
            params[title] = summ
        else:
            params[title] += summ
    params['age'] = user_exists.age
    params['gender'] = user_exists.gender[0]
    params['income'] = user_exists.salary

    text = (f"\n\nМой возраст: {params['age']} лет\n"
            f"Мой пол: {params['gender']}\n"
            f"Моя зарплата: {params['income']}\n"
            f"Вот информация о моих реальных и предсказанных тратах по категориям:\n")
    http_session = aiohttp.ClientSession()
    try:
        async with http_session.get('127.0.0.1:8080/overspending', params=params) as resp:
            data = await resp.json()
            overspending_categories = data['overspending_categories']
            for cat in overspending_categories:
                cat_int = reversed_CATEGORY_NAMES[cat]
                cat_my = reversed_categories[cat_int]
                text += (f'Категория "{cat_my}": '
                         f'Реальные траты: {overspending_categories[cat][0]}, '
                         f'Ождиаемые траты: {overspending_categories[cat][1]}\n')
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )
    finally:
        await http_session.close()

    try:
        agent_id = settings.mistral_large_agent_id

        client = Mistral(api_key=settings.mistral_api_key)
        print(f'Запрос: {request.request + text}')
        chat_response = await client.agents.complete_async(
            agent_id=agent_id,
            messages=[
                {
                    "role": "user",
                    "content": request.request + text,
                },
            ],
        )
        response = chat_response.choices[0].message.content

        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )
