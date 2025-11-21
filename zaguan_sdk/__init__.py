"""
Zaguan SDK for Python
=====================

An official Python SDK for Zaguan CoreX - an enterprise-grade AI gateway
that provides unified access to 15+ AI providers and 500+ models through
a single, OpenAI-compatible API.
"""

__version__ = "0.2.0"
__author__ = "Zaguan AI"
__email__ = "support@zaguanai.com"

from .client import ZaguanClient
from .async_client import AsyncZaguanClient
from .models import (
    Message, TokenDetails, Usage, ChatRequest, Choice,
    ChatResponse, ChatChunk, ModelInfo, ModelCapabilities,
    CreditsBalance, CreditsHistoryEntry, CreditsHistory, CreditsStats,
    EmbeddingRequest, Embedding, EmbeddingResponse,
    AudioTranscriptionRequest, AudioTranslationRequest, AudioTranscriptionResponse, AudioSpeechRequest,
    ImageGenerationRequest, ImageEditRequest, ImageVariationRequest, ImageData, ImageResponse,
    ModerationRequest, ModerationCategories, ModerationCategoryScores, ModerationResult, ModerationResponse,
    AnthropicThinkingConfig, AnthropicContentBlock, AnthropicMessage, AnthropicUsage,
    AnthropicMessagesRequest, AnthropicMessagesResponse, AnthropicMessagesDelta, AnthropicMessagesStreamEvent,
    AnthropicCountTokensRequest, AnthropicCountTokensResponse,
    AnthropicMessagesBatchItem, AnthropicMessagesBatchRequest, AnthropicMessagesBatchResponse
)
from .errors import ZaguanError, APIError, InsufficientCreditsError, RateLimitError, BandAccessDeniedError
from .streaming import StreamAccumulator, reconstruct_message_from_stream
from .retry import RetryConfig, with_retry, async_with_retry
from .observability import (
    RequestEvent, ResponseEvent, ErrorEvent,
    ObservabilityHook, LoggingHook, MetricsCollector, CompositeHook
)

# Version info
__all__ = [
    "ZaguanClient",
    "AsyncZaguanClient",
    "Message",
    "TokenDetails",
    "Usage",
    "ChatRequest",
    "Choice",
    "ChatResponse",
    "ChatChunk",
    "ModelInfo",
    "ModelCapabilities",
    "CreditsBalance",
    "CreditsHistoryEntry",
    "CreditsHistory",
    "CreditsStats",
    "ZaguanError",
    "APIError",
    "InsufficientCreditsError",
    "RateLimitError",
    "BandAccessDeniedError",
    # Embeddings
    "EmbeddingRequest",
    "Embedding",
    "EmbeddingResponse",
    # Audio
    "AudioTranscriptionRequest",
    "AudioTranslationRequest",
    "AudioTranscriptionResponse",
    "AudioSpeechRequest",
    # Images
    "ImageGenerationRequest",
    "ImageEditRequest",
    "ImageVariationRequest",
    "ImageData",
    "ImageResponse",
    # Moderations
    "ModerationRequest",
    "ModerationCategories",
    "ModerationCategoryScores",
    "ModerationResult",
    "ModerationResponse",
    # Anthropic Messages API
    "AnthropicThinkingConfig",
    "AnthropicContentBlock",
    "AnthropicMessage",
    "AnthropicUsage",
    "AnthropicMessagesRequest",
    "AnthropicMessagesResponse",
    "AnthropicMessagesDelta",
    "AnthropicMessagesStreamEvent",
    "AnthropicCountTokensRequest",
    "AnthropicCountTokensResponse",
    "AnthropicMessagesBatchItem",
    "AnthropicMessagesBatchRequest",
    "AnthropicMessagesBatchResponse",
    # Streaming utilities
    "StreamAccumulator",
    "reconstruct_message_from_stream",
    # Retry utilities
    "RetryConfig",
    "with_retry",
    "async_with_retry",
    # Observability
    "RequestEvent",
    "ResponseEvent",
    "ErrorEvent",
    "ObservabilityHook",
    "LoggingHook",
    "MetricsCollector",
    "CompositeHook",
]