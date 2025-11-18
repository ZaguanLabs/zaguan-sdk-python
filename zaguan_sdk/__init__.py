"""
Zaguan SDK for Python
=====================

An official Python SDK for Zaguan CoreX - an enterprise-grade AI gateway
that provides unified access to 15+ AI providers and 500+ models through
a single, OpenAI-compatible API.
"""

__version__ = "0.1.0"
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
    ModerationRequest, ModerationCategories, ModerationCategoryScores, ModerationResult, ModerationResponse
)
from .errors import ZaguanError, APIError, InsufficientCreditsError, RateLimitError, BandAccessDeniedError

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
]