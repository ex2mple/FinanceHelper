"""
API endpoints for AI interactions.
"""
from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel, Field

from core.ai.mistral import MistralAgent
from core.config import settings

router = APIRouter(tags=["AI"])


class MessageRequest(BaseModel):
    """Request schema for messages."""
    content: str = Field(..., description="Текстовый запрос пользователя")


class MessageResponse(BaseModel):
    """Response schema for messages."""
    response: str = Field(..., description="Ответ от нейросети")


async def get_mistral_agent() -> MistralAgent:
    """Dependency for getting a Mistral AI agent."""
    try:
        return MistralAgent(
            api_key=settings.mistral_api_key,
            agent_id=settings.mistral_default_agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка инициализации Mistral AI: {str(e)}")


@router.post("/ask", response_model=MessageResponse)
async def ask_agent(
    request: MessageRequest,
    agent: MistralAgent = Depends(get_mistral_agent)
) -> MessageResponse:
    """
    Отправить запрос к нейросети и получить ответ.
    
    - **content**: Текстовый запрос пользователя
    """
    try:
        response = await agent.generate_agent_response(
            prompt=request.content
        )
        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )