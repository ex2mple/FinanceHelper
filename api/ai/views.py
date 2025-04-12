"""
API endpoints for AI interactions.
"""
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, Query

from pydantic import BaseModel, Field

from core.ai.mistral import MistralAgent
from core.config import settings

router = APIRouter(tags=["AI"])


class AgentType(str, Enum):
    """Типы доступных агентов Mistral."""
    LARGE = "large"
    SMALL = "small"


class MessageRequest(BaseModel):
    """Request schema for messages."""
    content: str = Field(..., description="Текстовый запрос пользователя")


class MessageResponse(BaseModel):
    """Response schema for messages."""
    response: str = Field(..., description="Ответ от нейросети")
    agent_type: AgentType = Field(..., description="Тип использованного агента")


async def get_mistral_agent(agent_type: AgentType = Query(AgentType.LARGE, description="Тип агента (large или small)")) -> MistralAgent:
    """Dependency for getting a Mistral AI agent based on agent type."""
    try:
        agent_id = settings.mistral_large_agent_id if agent_type == AgentType.LARGE else settings.mistral_small_agent_id
        
        return MistralAgent(
            api_key=settings.mistral_api_key,
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка инициализации Mistral AI: {str(e)}")


@router.post("/ask", response_model=MessageResponse)
async def ask_agent(
    request: MessageRequest,
    agent_type: AgentType = Query(AgentType.LARGE, description="Тип агента (large или small)"),
    agent: MistralAgent = Depends(get_mistral_agent)
) -> MessageResponse:
    """
    Отправить запрос к нейросети и получить ответ.
    
    - **content**: Текстовый запрос пользователя
    - **agent_type**: Тип агента (large или small)
    """
    try:
        response = await agent.generate_agent_response(
            prompt=request.content
        )
        return MessageResponse(response=response, agent_type=agent_type)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )


@router.post("/ask/large", response_model=MessageResponse)
async def ask_large_agent(
    request: MessageRequest
) -> MessageResponse:
    """
    Отправить запрос к large агенту Mistral.
    
    - **content**: Текстовый запрос пользователя
    """
    try:
        agent = MistralAgent(
            api_key=settings.mistral_api_key,
            agent_id=settings.mistral_large_agent_id
        )
        
        response = await agent.generate_agent_response(
            prompt=request.content
        )
        return MessageResponse(response=response, agent_type=AgentType.LARGE)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )


@router.post("/ask/small", response_model=MessageResponse)
async def ask_small_agent(
    request: MessageRequest
) -> MessageResponse:
    """
    Отправить запрос к small агенту Mistral.
    
    - **content**: Текстовый запрос пользователя
    """
    try:
        agent = MistralAgent(
            api_key=settings.mistral_api_key,
            agent_id=settings.mistral_small_agent_id
        )
        
        response = await agent.generate_agent_response(
            prompt=request.content
        )
        return MessageResponse(response=response, agent_type=AgentType.SMALL)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )