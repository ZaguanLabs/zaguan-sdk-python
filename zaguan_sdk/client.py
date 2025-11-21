"""
Synchronous client for the Zaguan SDK.
"""

import httpx
import json
import uuid
from typing import Optional, Iterator, List, Union, Dict, Any
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


class ZaguanClient:
    """
    Synchronous client for interacting with Zaguan CoreX.

    This client provides a high-level interface to all Zaguan CoreX functionality
    including chat completions, model management, and credits tracking.

    Example:
        ```python
        from zaguan_sdk import ZaguanClient, ChatRequest, Message

        client = ZaguanClient(
            base_url="https://api.zaguanai.com",
            api_key="your-api-key"
        )

        # Simple chat
        response = client.chat_simple("Hello, world!")
        print(response.choices[0].message.content)

        # Advanced request
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")],
            temperature=0.7
        )
        response = client.chat(request)
        ```
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.Client] = None
    ):
        """
        Initialize the Zaguan client.

        Args:
            base_url: The base URL for the Zaguan CoreX API
            api_key: The API key for authentication
            timeout: Request timeout in seconds. Defaults to 30 seconds.
            http_client: Optional pre-configured HTTP client. If not provided,
                        a new httpx.Client will be created.

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
        self._client = http_client or httpx.Client(timeout=self.timeout)
    
    def _prepare_headers(self, request_id: Optional[str] = None) -> Dict[str, str]:
        """Prepare headers for an API request."""
        return prepare_headers(self.api_key, request_id)
    
    def chat(
        self, 
        request: ChatRequest, 
        request_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Perform a chat completion request.

        This is the main method for generating responses from AI models.
        Supports all OpenAI-compatible parameters plus Zaguan-specific features.

        Args:
            request: The chat completion request containing model, messages, and parameters
            request_id: Optional unique identifier for request tracking and debugging.
                       If not provided, one will be automatically generated.

        Returns:
            ChatResponse: Contains the generated response, usage statistics, and metadata

        Raises:
            APIError: For HTTP errors (400, 401, 429, 500, etc.)
            InsufficientCreditsError: When account has insufficient credits
            RateLimitError: When rate limits are exceeded

        Example:
            ```python
            from zaguan_sdk import ChatRequest, Message

            request = ChatRequest(
                model="openai/gpt-4o",
                messages=[
                    Message(role="system", content="You are a helpful assistant."),
                    Message(role="user", content="What is 2+2?")
                ],
                temperature=0.7,
                max_tokens=150
            )

            response = client.chat(request)
            print(response.choices[0].message.content)
            print(f"Used {response.usage.total_tokens} tokens")
            ```
        """
        url = f"{self.base_url}/v1/chat/completions"
        headers = self._prepare_headers(request_id)
        
        # Convert request to dict, handling aliases and excluding None values
        request_dict = request.model_dump(by_alias=True, exclude_none=True)
        
        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, ChatResponse)
    
    def chat_stream(
        self, 
        request: ChatRequest, 
        request_id: Optional[str] = None
    ) -> Iterator[ChatChunk]:
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
            with self._client.stream("POST", url, headers=headers, json=request_dict) as response:
                response.raise_for_status()
                for line in response.iter_lines():
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
    
    def list_models(self, request_id: Optional[str] = None) -> List[ModelInfo]:
        """
        List available models.
        
        Args:
            request_id: Optional request ID for tracking
            
        Returns:
            List of model information
        """
        url = f"{self.base_url}/v1/models"
        headers = self._prepare_headers(request_id)
        
        response = self._client.get(url, headers=headers)
        data = handle_response(response)
        return [ModelInfo(**model) for model in data.get("data", [])]
    
    def get_capabilities(self, request_id: Optional[str] = None) -> List[ModelCapabilities]:
        """
        Get model capabilities.
        
        Args:
            request_id: Optional request ID for tracking
            
        Returns:
            List of model capabilities
        """
        url = f"{self.base_url}/v1/capabilities"
        headers = self._prepare_headers(request_id)
        
        response = self._client.get(url, headers=headers)
        data = handle_response(response)
        return [ModelCapabilities(**cap) for cap in data]
    
    def get_credits_balance(self, request_id: Optional[str] = None) -> CreditsBalance:
        """
        Get credits balance.
        
        Args:
            request_id: Optional request ID for tracking
            
        Returns:
            Credits balance information
        """
        url = f"{self.base_url}/v1/credits/balance"
        headers = self._prepare_headers(request_id)
        
        response = self._client.get(url, headers=headers)
        return handle_response(response, CreditsBalance)
    
    def get_credits_history(
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
            
        response = self._client.get(url, headers=headers, params=params)
        return handle_response(response, CreditsHistory)
    
    def get_credits_stats(
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
            
        response = self._client.get(url, headers=headers, params=params)
        return handle_response(response, CreditsStats)

    def health_check(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a health check on the API.

        Args:
            request_id: Optional request ID for tracking

        Returns:
            Health status information
        """
        url = f"{self.base_url}/health"
        headers = self._prepare_headers(request_id)

        response = self._client.get(url, headers=headers)
        return handle_response(response)
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Helper methods for convenience
    def chat_simple(self, message: str, model: str = "openai/gpt-4o-mini") -> ChatResponse:
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
        return self.chat(request)

    def chat_with_system(self, system_prompt: str, user_message: str, model: str = "openai/gpt-4o-mini") -> ChatResponse:
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
        return self.chat(request)

    # ========================================================================
    # Embeddings
    # ========================================================================

    def create_embeddings(
        self,
        request: EmbeddingRequest,
        request_id: Optional[str] = None
    ) -> EmbeddingResponse:
        """
        Create embeddings for the given input.

        Args:
            request: The embedding request
            request_id: Optional request ID for tracking

        Returns:
            Embedding response with vectors

        Example:
            ```python
            request = EmbeddingRequest(
                model="openai/text-embedding-3-small",
                input="Hello, world!"
            )
            response = client.create_embeddings(request)
            print(response.data[0].embedding)
            ```
        """
        url = f"{self.base_url}/v1/embeddings"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, EmbeddingResponse)

    # ========================================================================
    # Audio
    # ========================================================================

    def create_transcription(
        self,
        file_path: str,
        model: str = "whisper-1",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> AudioTranscriptionResponse:
        """
        Transcribe audio to text.

        Args:
            file_path: Path to the audio file
            model: Model to use (default: whisper-1)
            language: Language of the audio (ISO-639-1 format)
            prompt: Optional text to guide the model's style
            response_format: Format of the response (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature
            request_id: Optional request ID for tracking

        Returns:
            Transcription response

        Example:
            ```python
            response = client.create_transcription(
                file_path="audio.mp3",
                model="whisper-1",
                language="en"
            )
            print(response.text)
            ```
        """
        url = f"{self.base_url}/v1/audio/transcriptions"
        headers = self._prepare_headers(request_id)
        # Remove Content-Type for multipart
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

            response = self._client.post(url, headers=headers, files=files, data=data)

        if response_format == "json" or response_format == "verbose_json":
            return handle_response(response, AudioTranscriptionResponse)
        else:
            # Return text directly for other formats
            return AudioTranscriptionResponse(text=response.text)

    def create_translation(
        self,
        file_path: str,
        model: str = "whisper-1",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> AudioTranscriptionResponse:
        """
        Translate audio to English text.

        Args:
            file_path: Path to the audio file
            model: Model to use (default: whisper-1)
            prompt: Optional text to guide the model's style
            response_format: Format of the response
            temperature: Sampling temperature
            request_id: Optional request ID for tracking

        Returns:
            Translation response
        """
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

            response = self._client.post(url, headers=headers, files=files, data=data)

        if response_format == "json" or response_format == "verbose_json":
            return handle_response(response, AudioTranscriptionResponse)
        else:
            return AudioTranscriptionResponse(text=response.text)

    def create_speech(
        self,
        request: AudioSpeechRequest,
        output_path: str,
        request_id: Optional[str] = None
    ) -> None:
        """
        Generate speech from text.

        Args:
            request: The speech request
            output_path: Path to save the audio file
            request_id: Optional request ID for tracking

        Example:
            ```python
            request = AudioSpeechRequest(
                model="tts-1",
                input="Hello, world!",
                voice="alloy"
            )
            client.create_speech(request, "output.mp3")
            ```
        """
        url = f"{self.base_url}/v1/audio/speech"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

    # ========================================================================
    # Images
    # ========================================================================

    def create_image(
        self,
        request: ImageGenerationRequest,
        request_id: Optional[str] = None
    ) -> ImageResponse:
        """
        Generate images from a text prompt.

        Args:
            request: The image generation request
            request_id: Optional request ID for tracking

        Returns:
            Image response with URLs or base64 data

        Example:
            ```python
            request = ImageGenerationRequest(
                prompt="A cute cat",
                model="dall-e-3",
                size="1024x1024",
                quality="hd"
            )
            response = client.create_image(request)
            print(response.data[0].url)
            ```
        """
        url = f"{self.base_url}/v1/images/generations"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, ImageResponse)

    def edit_image(
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
        """
        Edit an image based on a prompt.

        Args:
            image_path: Path to the image file (PNG, <4MB, square)
            prompt: Description of the desired edit
            mask_path: Optional path to mask image (transparent areas will be edited)
            model: Model to use
            n: Number of images to generate
            size: Size of the generated images
            response_format: Format of the response (url or b64_json)
            request_id: Optional request ID for tracking

        Returns:
            Image response
        """
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

        response = self._client.post(
            url,
            headers=headers,
            files={k: (k, v) for k, v in files.items()},
            data=data
        )
        return handle_response(response, ImageResponse)

    def create_image_variation(
        self,
        image_path: str,
        model: str = "dall-e-2",
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url",
        request_id: Optional[str] = None
    ) -> ImageResponse:
        """
        Create variations of an image.

        Args:
            image_path: Path to the image file (PNG, <4MB, square)
            model: Model to use
            n: Number of variations to generate
            size: Size of the generated images
            response_format: Format of the response (url or b64_json)
            request_id: Optional request ID for tracking

        Returns:
            Image response
        """
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

            response = self._client.post(url, headers=headers, files=files, data=data)

        return handle_response(response, ImageResponse)

    # ========================================================================
    # Moderations
    # ========================================================================

    def create_moderation(
        self,
        request: ModerationRequest,
        request_id: Optional[str] = None
    ) -> ModerationResponse:
        """
        Check if content violates OpenAI's usage policies.

        Args:
            request: The moderation request
            request_id: Optional request ID for tracking

        Returns:
            Moderation response with flagged categories

        Example:
            ```python
            request = ModerationRequest(
                input="I want to hurt someone"
            )
            response = client.create_moderation(request)
            if response.results[0].flagged:
                print("Content flagged!")
                print(response.results[0].categories)
            ```
        """
        url = f"{self.base_url}/v1/moderations"
        headers = self._prepare_headers(request_id)

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, ModerationResponse)

    # ========================================================================
    # Anthropic Messages API (Native)
    # ========================================================================

    def messages(
        self,
        request: AnthropicMessagesRequest,
        request_id: Optional[str] = None
    ) -> AnthropicMessagesResponse:
        """
        Send a request to Anthropic's native Messages API.

        This is the recommended way to access Anthropic-specific features like
        extended thinking. Use this instead of the OpenAI-compatible chat API
        when you need Anthropic's native response format.

        Args:
            request: The Anthropic messages request
            request_id: Optional request ID for tracking

        Returns:
            Anthropic messages response with content blocks

        Example:
            ```python
            from zaguan_sdk import AnthropicMessagesRequest, AnthropicMessage, AnthropicThinkingConfig

            request = AnthropicMessagesRequest(
                model="anthropic/claude-3-5-sonnet",
                messages=[
                    AnthropicMessage(role="user", content="Explain quantum computing")
                ],
                max_tokens=1024,
                thinking=AnthropicThinkingConfig(type="enabled", budget_tokens=5000)
            )
            response = client.messages(request)
            for block in response.content:
                if block.type == "thinking":
                    print(f"Thinking: {block.thinking}")
                elif block.type == "text":
                    print(f"Response: {block.text}")
            ```
        """
        url = f"{self.base_url}/v1/messages"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, AnthropicMessagesResponse)

    def messages_stream(
        self,
        request: AnthropicMessagesRequest,
        request_id: Optional[str] = None
    ) -> Iterator[AnthropicMessagesStreamEvent]:
        """
        Stream responses from Anthropic's Messages API.

        Args:
            request: The Anthropic messages request
            request_id: Optional request ID for tracking

        Yields:
            Streaming events from Anthropic

        Example:
            ```python
            request = AnthropicMessagesRequest(
                model="anthropic/claude-3-5-sonnet",
                messages=[AnthropicMessage(role="user", content="Tell me a story")],
                max_tokens=1024,
                stream=True
            )
            for event in client.messages_stream(request):
                if event.type == "content_block_delta":
                    if event.delta.text:
                        print(event.delta.text, end="", flush=True)
            ```
        """
        url = f"{self.base_url}/v1/messages"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        # Ensure streaming is enabled
        stream_request = request.model_copy()
        stream_request.stream = True

        request_dict = stream_request.model_dump(by_alias=True, exclude_none=True)

        try:
            with self._client.stream("POST", url, headers=headers, json=request_dict) as response:
                response.raise_for_status()
                for line in response.iter_lines():
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

    def count_tokens(
        self,
        request: AnthropicCountTokensRequest,
        request_id: Optional[str] = None
    ) -> AnthropicCountTokensResponse:
        """
        Count tokens for an Anthropic Messages request.

        This endpoint allows you to count tokens before sending a request,
        useful for cost estimation and staying within token limits.

        Args:
            request: The token counting request
            request_id: Optional request ID for tracking

        Returns:
            Token count response

        Example:
            ```python
            from zaguan_sdk import AnthropicCountTokensRequest, AnthropicMessage

            request = AnthropicCountTokensRequest(
                model="anthropic/claude-3-5-sonnet",
                messages=[
                    AnthropicMessage(role="user", content="Hello, world!")
                ]
            )
            response = client.count_tokens(request)
            print(f"Input tokens: {response.input_tokens}")
            ```
        """
        url = f"{self.base_url}/v1/messages/count_tokens"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        request_dict = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, AnthropicCountTokensResponse)

    def create_messages_batch(
        self,
        requests: List[AnthropicMessagesBatchItem],
        request_id: Optional[str] = None
    ) -> AnthropicMessagesBatchResponse:
        """
        Create a batch of message requests for asynchronous processing.

        Args:
            requests: List of batch items with custom IDs and parameters
            request_id: Optional request ID for tracking

        Returns:
            Batch response with status and ID

        Example:
            ```python
            from zaguan_sdk import AnthropicMessagesBatchItem, AnthropicMessagesRequest, AnthropicMessage

            items = [
                AnthropicMessagesBatchItem(
                    custom_id="request-1",
                    params=AnthropicMessagesRequest(
                        model="anthropic/claude-3-5-sonnet",
                        messages=[AnthropicMessage(role="user", content="Hello")],
                        max_tokens=100
                    )
                )
            ]
            batch = client.create_messages_batch(items)
            print(f"Batch ID: {batch.id}")
            ```
        """
        url = f"{self.base_url}/v1/messages/batches"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        batch_request = AnthropicMessagesBatchRequest(requests=requests)
        request_dict = batch_request.model_dump(by_alias=True, exclude_none=True)

        response = self._client.post(url, headers=headers, json=request_dict)
        return handle_response(response, AnthropicMessagesBatchResponse)

    def get_messages_batch(
        self,
        batch_id: str,
        request_id: Optional[str] = None
    ) -> AnthropicMessagesBatchResponse:
        """
        Get the status of a message batch.

        Args:
            batch_id: The batch ID to query
            request_id: Optional request ID for tracking

        Returns:
            Batch status response
        """
        url = f"{self.base_url}/v1/messages/batches/{batch_id}"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        response = self._client.get(url, headers=headers)
        return handle_response(response, AnthropicMessagesBatchResponse)

    def list_messages_batches(
        self,
        request_id: Optional[str] = None
    ) -> List[AnthropicMessagesBatchResponse]:
        """
        List all message batches.

        Args:
            request_id: Optional request ID for tracking

        Returns:
            List of batch responses
        """
        url = f"{self.base_url}/v1/messages/batches"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        response = self._client.get(url, headers=headers)
        data = handle_response(response)
        return [AnthropicMessagesBatchResponse(**batch) for batch in data.get("data", [])]

    def cancel_messages_batch(
        self,
        batch_id: str,
        request_id: Optional[str] = None
    ) -> AnthropicMessagesBatchResponse:
        """
        Cancel a message batch.

        Args:
            batch_id: The batch ID to cancel
            request_id: Optional request ID for tracking

        Returns:
            Updated batch status
        """
        url = f"{self.base_url}/v1/messages/batches/{batch_id}/cancel"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        response = self._client.post(url, headers=headers)
        return handle_response(response, AnthropicMessagesBatchResponse)

    def get_messages_batch_results(
        self,
        batch_id: str,
        request_id: Optional[str] = None
    ) -> Iterator[str]:
        """
        Get batch results as JSONL stream.

        Args:
            batch_id: The batch ID to get results for
            request_id: Optional request ID for tracking

        Yields:
            JSONL lines with results

        Example:
            ```python
            for line in client.get_messages_batch_results("batch_123"):
                result = json.loads(line)
                print(f"Custom ID: {result['custom_id']}")
                print(f"Result: {result['result']}")
            ```
        """
        url = f"{self.base_url}/v1/messages/batches/{batch_id}/results"
        headers = self._prepare_headers(request_id)
        headers["anthropic-version"] = "2023-06-01"

        try:
            with self._client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    line = line.strip()
                    if line:
                        yield line
        except httpx.HTTPStatusError as e:
            handle_response(e.response)