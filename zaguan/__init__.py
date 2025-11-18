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
    CreditsBalance, CreditsHistoryEntry, CreditsHistory, CreditsStats
)
from .errors import ZaguanError, APIError, InsufficientCreditsError, RateLimitError

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
]