import datetime
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, HTTPException, Body, Depends, Path

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.views import user_dependency
from api.transactions.crud import get_filtered_transactions_grouped
from core.config import settings
from core.models import db_helper

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


@router.get("/advice", response_model=MessageResponse)
async def ask_agent_advice(
    current_user: user_dependency,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> MessageResponse:
    res = await get_filtered_transactions_grouped(session=session, user_id=current_user.id,
                                                  start_date=start_date, end_date=end_date)
    print(res)
    return MessageResponse(response='ok')


@router.get("/advice/user/{user_id}", response_model=MessageResponse)
async def ask_agent_advice(
    user_id: Annotated[int, Path()],
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> MessageResponse:
    res = await get_filtered_transactions_grouped(session=session, user_id=user_id,
                                                  start_date=start_date, end_date=end_date)
    # TODO: Здесь нужно отдать результат в эндпоинт с моделями и получить от них ответ
    aiohttp.ClientSession()
    return MessageResponse(response='ok')
