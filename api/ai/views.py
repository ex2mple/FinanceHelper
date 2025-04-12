from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Body

from pydantic import BaseModel, Field
from core.config import settings

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
