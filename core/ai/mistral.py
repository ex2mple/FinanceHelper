"""
Mistral AI client implementation for asynchronous interaction with Mistral AI agents.
"""
import asyncio
from typing import List, Dict, Optional, Union

from mistralai.client import MistralClient
from pydantic import BaseModel, Field

from core.config import settings


class MistralMessageSchema(BaseModel):
    """Schema for Mistral AI message."""
    role: str
    content: str


class MistralResponseSchema(BaseModel):
    """Schema for Mistral AI response."""
    response: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)


class MistralAgent:
    """
    Asynchronous class for working with Mistral AI agents.
    
    This class provides an interface for interacting with Mistral AI
    models and agents asynchronously.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """
        Initialize the Mistral AI agent.
        
        Args:
            api_key: Mistral AI API key. If not provided, will use from settings.
            agent_id: Default Mistral AI agent ID. If not provided, will use from settings.
        """
        self.api_key = api_key or settings.mistral_api_key
        self.agent_id = agent_id or settings.mistral_default_agent_id
        self.client = MistralClient(api_key=self.api_key)
    
    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a blocking function in an executor to make it asynchronous."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    async def agent_completion(
        self, 
        agent_id: str,
        messages: List[Dict[str, str]]
    ) -> MistralResponseSchema:
        """
        Generate a completion using a specific Mistral AI agent.
        
        Args:
            agent_id: The ID of the Mistral AI agent to use.
            messages: List of messages in the conversation.
            
        Returns:
            A MistralResponseSchema with the response and metadata.
        """
        # Run the agent completion in an executor to make it asynchronous
        try:
            response = await self._run_in_executor(
                self.client.chat_with_agent,
                agent_id=agent_id,
                messages=messages
            )
            
            # Extract relevant information from the response
            result = MistralResponseSchema(
                response=response.choices[0].message.content,
                model=agent_id,
                usage={}
            )
            
            return result
        except AttributeError:
            # В случае изменения API, пробуем альтернативный метод
            try:
                response = await self._run_in_executor(
                    self.client.agents.chat,
                    agent_id=agent_id,
                    messages=messages
                )
                
                result = MistralResponseSchema(
                    response=response.choices[0].message.content,
                    model=agent_id,
                    usage={}
                )
                
                return result
            except AttributeError:
                # Пробуем еще один вариант API
                try:
                    response = await self._run_in_executor(
                        self.client.agents.complete,
                        agent_id=agent_id,
                        messages=messages
                    )
                    
                    result = MistralResponseSchema(
                        response=response.choices[0].message.content,
                        model=agent_id,
                        usage={}
                    )
                    
                    return result
                except Exception as e:
                    raise Exception(f"Ошибка при вызове Mistral API: {str(e)}")
    
    async def generate_agent_response(
        self,
        prompt: str,
        agent_id: Optional[str] = None
    ) -> str:
        """
        Generate a response using a specific Mistral AI agent.
        
        Args:
            prompt: The user prompt to respond to.
            agent_id: The ID of the Mistral AI agent to use. If not provided, will use default.
            
        Returns:
            The generated response text.
        """
        # Use the default agent_id if none provided
        agent_id = agent_id or self.agent_id
        
        # Format messages for the agent
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Generate the response using the specified agent
        response = await self.agent_completion(
            agent_id=agent_id,
            messages=messages
        )
        
        return response.response