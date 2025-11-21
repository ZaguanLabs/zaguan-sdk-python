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
    Message,
    EmbeddingRequest, EmbeddingResponse,
    AudioTranscriptionRequest, AudioTranslationRequest, AudioTranscriptionResponse, AudioSpeechRequest,
    ImageGenerationRequest, ImageEditRequest, ImageVariationRequest, ImageResponse,
    ModerationRequest, ModerationResponse,
    AnthropicMessagesRequest, AnthropicMessagesResponse, AnthropicMessagesStreamEvent,
    AnthropicCountTokensRequest, AnthropicCountTokensResponse,
    AnthropicMessagesBatchRequest, AnthropicMessagesBatchResponse, AnthropicMessagesBatchItem
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
            timeout: Request timeout in seconds. Defaults to 30 seconds.
            http_client: Optional pre-configured HTTP client
            
        Raises:
            ValueError: If base_url or api_key are empty/None
        """
        if not base_url or not base_url.strip():
            raise ValueError("base_url cannot be empty")
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")
        
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout if timeout is not None else 30.0
        self._client = http_client or httpx.AsyncClient(timeout=self.timeout)
    
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
        
        try:
            async with self._client.stream("POST", url, headers=headers, json=request_dict) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or line == "data: [DONE]":
                        continue
                    # Parse SSE-style line
                    if line.startswith("data:"):
                        payload = line[len("data:"):].strip()
                        if not payload:
                            continue
                        try:
                            data = json.loads(payload)
                            yield ChatChunk(**data)
                        except json.JSONDecodeError as e:
                            # Skip malformed lines but could log warning
                            continue
                        except Exception as e:
                            # Handle Pydantic validation errors
                            raise ZaguanError(f"Failed to parse chunk: {e}")
        except httpx.HTTPStatusError as e:
            # Re-raise as our custom error type
            handle_response(e.response)
    
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

    # ========================================================================
    # Embeddings
    # ========================================================================

    async def create_embeddings(
        self,
        request: EmbeddingRequest,
        request_id: Optional[str] = None
    ) -> EmbeddingResponse:
        """Create embeddings for the given input."""
        url = f"{self.base_url}/v1/embeddings"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, EmbeddingResponse)

    # ========================================================================
    # Audio
    # ========================================================================

    async def create_transcription(
        self,
        file_path: str,
        model: str = "whisper-1",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> AudioTranscriptionResponse:
        """Transcribe audio to text."""
        url = f"{self.base_url}/v1/audio/transcriptions"
        headers = self._prepare_headers(request_id)
        del headers["Content-Type"]

        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "model": model,
                "response_format": response_format
            }
            if language:
                data["language"] = language
            if prompt:
                data["prompt"] = prompt
            if temperature is not None:
                data["temperature"] = temperature

            response = await self._client.post(url, headers=headers, files=files, data=data)

        if response_format == "json" or response_format == "verbose_json":
            return handle_response(response, AudioTranscriptionResponse)
        else:
            return AudioTranscriptionResponse(text=response.text)

    async def create_translation(
        self,
        file_path: str,
        model: str = "whisper-1",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> AudioTranscriptionResponse:
        """Translate audio to English text."""
        url = f"{self.base_url}/v1/audio/translations"
        headers = self._prepare_headers(request_id)
        del headers["Content-Type"]

        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "model": model,
                "response_format": response_format
            }
            if prompt:
                data["prompt"] = prompt
            if temperature is not None:
                data["temperature"] = temperature

            response = await self._client.post(url, headers=headers, files=files, data=data)

        if response_format == "json" or response_format == "verbose_json":
            return handle_response(response, AudioTranscriptionResponse)
        else:
            return AudioTranscriptionResponse(text=response.text)

    async def create_speech(
        self,
        request: AudioSpeechRequest,
        output_path: str,
        request_id: Optional[str] = None
    ) -> None:
        """Generate speech from text."""
        url = f"{self.base_url}/v1/audio/speech"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

    # ========================================================================
    # Images
    # ========================================================================

    async def create_image(
        self,
        request: ImageGenerationRequest,
        request_id: Optional[str] = None
    ) -> ImageResponse:
        """Generate images from a text prompt."""
        url = f"{self.base_url}/v1/images/generations"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, ImageResponse)

    async def edit_image(
        self,
        image_path: str,
        prompt: str,
        mask_path: Optional[str] = None,
        model: str = "dall-e-2",
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url",
        request_id: Optional[str] = None
    ) -> ImageResponse:
        """Edit an image based on a prompt."""
        url = f"{self.base_url}/v1/images/edits"
        headers = self._prepare_headers(request_id)
        del headers["Content-Type"]

        files = {}
        with open(image_path, "rb") as f:
            files["image"] = f.read()

        if mask_path:
            with open(mask_path, "rb") as f:
                files["mask"] = f.read()

        data = {
            "prompt": prompt,
            "model": model,
            "n": n,
            "size": size,
            "response_format": response_format
        }

        response = await self._client.post(
            url,
            headers=headers,
            files={k: (k, v) for k, v in files.items()},
            data=data
        )
        return handle_response(response, ImageResponse)

    async def create_image_variation(
        self,
        image_path: str,
        model: str = "dall-e-2",
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url",
        request_id: Optional[str] = None
    ) -> ImageResponse:
        """Create variations of an image."""
        url = f"{self.base_url}/v1/images/variations"
        headers = self._prepare_headers(request_id)
        del headers["Content-Type"]

        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {
                "model": model,
                "n": n,
                "size": size,
                "response_format": response_format
            }

            response = await self._client.post(url, headers=headers, files=files, data=data)

        return handle_response(response, ImageResponse)

    # ========================================================================
    # Moderations
    # ========================================================================

    async def create_moderation(
        self,
        request: ModerationRequest,
        request_id: Optional[str] = None
    ) -> ModerationResponse:
        """Check if content violates OpenAI's usage policies."""
        url = f"{self.base_url}/v1/moderations"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, ModerationResponse)

    # ========================================================================
    # Anthropic Messages API (Native)
    # ========================================================================

    async def messages(
        self,
        request: AnthropicMessagesRequest,
        request_id: Optional[str] = None
    ) -> AnthropicMessagesResponse:
        """Send a request to Anthropic's native Messages API."""
        url = f"{self.base_url}/v1/messages"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, AnthropicMessagesResponse)

    async def messages_stream(
        self,
        request: AnthropicMessagesRequest,
        request_id: Optional[str] = None
    ) -> AsyncIterator[AnthropicMessagesStreamEvent]:
        """Stream responses from Anthropic's Messages API."""
        url = f"{self.base_url}/v1/messages"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        # Ensure streaming is enabled
        stream_request = request.model_copy()
        stream_request.stream = True

        request_dict = stream_request.model_dump(by_alias=True, exclude_none=True)

        try:
            async with self._client.stream("POST", url, headers=headers, json=request_dict) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    # Parse SSE-style events
                    if line.startswith("event:"):
                        event_type = line[len("event:"):].strip()
                        continue
                    if line.startswith("data:"):
                        payload = line[len("data:"):].strip()
                        if not payload:
                            continue
                        try:
                            data = json.loads(payload)
                            yield AnthropicMessagesStreamEvent(**data)
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            raise ZaguanError(f"Failed to parse Anthropic stream event: {e}")
        except httpx.HTTPStatusError as e:
            handle_response(e.response)

    async def count_tokens(
        self,
        request: AnthropicCountTokensRequest,
        request_id: Optional[str] = None
    ) -> AnthropicCountTokensResponse:
        """Count tokens for an Anthropic Messages request."""
        url = f"{self.base_url}/v1/messages/count_tokens"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, AnthropicCountTokensResponse)

    async def create_messages_batch(
        self,
        requests: List[AnthropicMessagesBatchItem],
        request_id: Optional[str] = None
    ) -> AnthropicMessagesBatchResponse:
        """Create a batch of message requests for asynchronous processing."""
        url = f"{self.base_url}/v1/messages/batches"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        batch_request = AnthropicMessagesBatchRequest(requests=requests)
        request_dict = batch_request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, AnthropicMessagesBatchResponse)

    async def get_messages_batch(
        self,
        batch_id: str,
        request_id: Optional[str] = None
    ) -> AnthropicMessagesBatchResponse:
        """Get the status of a message batch."""
        url = f"{self.base_url}/v1/messages/batches/{batch_id}"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        response = await self._client.get(url, headers=headers)
        return handle_response(response, AnthropicMessagesBatchResponse)

    async def list_messages_batches(
        self,
        request_id: Optional[str] = None
    ) -> List[AnthropicMessagesBatchResponse]:
        """List all message batches."""
        url = f"{self.base_url}/v1/messages/batches"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        response = await self._client.get(url, headers=headers)
        data = handle_response(response)
        return [AnthropicMessagesBatchResponse(**batch) for batch in data.get("data", [])]

    async def cancel_messages_batch(
        self,
        batch_id: str,
        request_id: Optional[str] = None
    ) -> AnthropicMessagesBatchResponse:
        """Cancel a message batch."""
        url = f"{self.base_url}/v1/messages/batches/{batch_id}/cancel"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        response = await self._client.post(url, headers=headers)
        return handle_response(response, AnthropicMessagesBatchResponse)

    async def get_messages_batch_results(
        self,
        batch_id: str,
        request_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Get batch results as JSONL stream."""
        url = f"{self.base_url}/v1/messages/batches/{batch_id}/results"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        try:
            async with self._client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if line:
                        yield line
        except httpx.HTTPStatusError as e:
            handle_response(e.response)