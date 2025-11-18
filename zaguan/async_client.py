"""
Asynchronous client for the Zaguan SDK.
"""

import httpx
import json
import uuid
from typing import Optional, AsyncIterator, List, Union, Dict, Any
from .models import (
    ChatRequest, ChatResponse, ChatChunk,
    ModelInfo, ModelCapabilities,
    CreditsBalance, CreditsHistory, CreditsStats,
    Message
)
from ._http import handle_response, prepare_headers
from .errors import ZaguanError


class AsyncZaguanClient:
    """Asynchronous client for interacting with Zaguan CoreX."""
    
    def __init__(
        self, 
        base_url: str, 
        api_key: str, 
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None
    ):
        """
        Initialize the client.
        
        Args:
            base_url: The base URL for the Zaguan CoreX API
            api_key: The API key for authentication
            timeout: Request timeout in seconds
            http_client: Optional pre-configured HTTP client
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = http_client or httpx.AsyncClient(timeout=timeout)
    
    def _prepare_headers(self, request_id: Optional[str] = None) -> Dict[str, str]:
        """Prepare headers for an API request."""
        return prepare_headers(self.api_key, request_id)
    
    async def chat(
        self, 
        request: ChatRequest, 
        request_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Perform a chat completion request.
        
        Args:
            request: The chat request
            request_id: Optional request ID for tracking
            
        Returns:
            The chat response
        """
        url = f"{self.base_url}/v1/chat/completions"
        headers = self._prepare_headers(request_id)
        
        # Convert request to dict, handling aliases and excluding None values
        request_dict = request.model_dump(by_alias=True, exclude_none=True)
        
        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, ChatResponse)
    
    async def chat_stream(
        self, 
        request: ChatRequest, 
        request_id: Optional[str] = None
    ) -> AsyncIterator[ChatChunk]:
        """
        Perform a streaming chat completion request.
        
        Args:
            request: The chat request
            request_id: Optional request ID for tracking
            
        Yields:
            Chat chunks as they arrive
        """
        url = f"{self.base_url}/v1/chat/completions"
        headers = self._prepare_headers(request_id)
        
        # Create a copy of the request with streaming enabled
        stream_request = request.copy()
        stream_request.stream = True
        
        # Convert request to dict, handling aliases and excluding None values
        request_dict = stream_request.model_dump(by_alias=True, exclude_none=True)
        
        async with self._client.stream("POST", url, headers=headers, json=request_dict) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or line.startswith("data: [DONE]"):
                    continue
                # Parse SSE-style line
                if line.startswith("data:"):
                    payload = line[len("data:"):].strip()
                    try:
                        data = json.loads(payload)
                        yield ChatChunk(**data)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
    
    async def list_models(self, request_id: Optional[str] = None) -> List[ModelInfo]:
        """
        List available models.
        
        Args:
            request_id: Optional request ID for tracking
            
        Returns:
            List of model information
        """
        url = f"{self.base_url}/v1/models"
        headers = self._prepare_headers(request_id)
        
        response = await self._client.get(url, headers=headers)
        data = handle_response(response)
        return [ModelInfo(**model) for model in data.get("data", [])]
    
    async def get_capabilities(self, request_id: Optional[str] = None) -> List[ModelCapabilities]:
        """
        Get model capabilities.
        
        Args:
            request_id: Optional request ID for tracking
            
        Returns:
            List of model capabilities
        """
        url = f"{self.base_url}/v1/capabilities"
        headers = self._prepare_headers(request_id)
        
        response = await self._client.get(url, headers=headers)
        data = handle_response(response)
        return [ModelCapabilities(**cap) for cap in data]
    
    async def get_credits_balance(self, request_id: Optional[str] = None) -> CreditsBalance:
        """
        Get credits balance.
        
        Args:
            request_id: Optional request ID for tracking
            
        Returns:
            Credits balance information
        """
        url = f"{self.base_url}/v1/credits/balance"
        headers = self._prepare_headers(request_id)
        
        response = await self._client.get(url, headers=headers)
        return handle_response(response, CreditsBalance)
    
    async def get_credits_history(
        self, 
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> CreditsHistory:
        """
        Get credits history.
        
        Args:
            limit: Maximum number of entries to return
            cursor: Cursor for pagination
            request_id: Optional request ID for tracking
            
        Returns:
            Credits history
        """
        url = f"{self.base_url}/v1/credits/history"
        headers = self._prepare_headers(request_id)
        
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
            
        response = await self._client.get(url, headers=headers, params=params)
        return handle_response(response, CreditsHistory)
    
    async def get_credits_stats(
        self, 
        period: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> CreditsStats:
        """
        Get credits statistics.
        
        Args:
            period: Time period for statistics (e.g., "day", "week", "month")
            request_id: Optional request ID for tracking
            
        Returns:
            Credits statistics
        """
        url = f"{self.base_url}/v1/credits/stats"
        headers = self._prepare_headers(request_id)
        
        params = {}
        if period is not None:
            params["period"] = period
            
        response = await self._client.get(url, headers=headers, params=params)
        return handle_response(response, CreditsStats)

    async def health_check(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a health check on the API.

        Args:
            request_id: Optional request ID for tracking

        Returns:
            Health status information
        """
        url = f"{self.base_url}/health"
        headers = self._prepare_headers(request_id)

        response = await self._client.get(url, headers=headers)
        return handle_response(response)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # Helper methods for convenience
    async def chat_simple(self, message: str, model: str = "openai/gpt-4o-mini") -> ChatResponse:
        """
        Simple chat completion with a single message.

        Args:
            message: The message to send
            model: The model to use (default: openai/gpt-4o-mini)

        Returns:
            Chat response
        """
        request = ChatRequest(
            model=model,
            messages=[Message(role="user", content=message)]
        )
        return await self.chat(request)

    async def chat_with_system(self, system_prompt: str, user_message: str, model: str = "openai/gpt-4o-mini") -> ChatResponse:
        """
        Chat completion with system prompt and user message.

        Args:
            system_prompt: System prompt to set context
            user_message: The user message
            model: The model to use

        Returns:
            Chat response
        """
        request = ChatRequest(
            model=model,
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_message)
            ]
        )
        return await self.chat(request)