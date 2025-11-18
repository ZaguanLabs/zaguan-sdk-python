"""
Core data models for the Zaguan SDK.
"""

from typing import List, Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a chat conversation."""
    role: Optional[Literal["system", "user", "assistant", "tool", "function"]] = None
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class TokenDetails(BaseModel):
    """Detailed token usage information."""
    reasoning_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    accepted_prediction_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[TokenDetails] = None
    completion_tokens_details: Optional[TokenDetails] = None


class ChatRequest(BaseModel):
    """Request for a chat completion."""
    model: str
    messages: List[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = Field(None, alias="max_tokens")
    top_p: Optional[float] = None
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    provider_specific_params: Optional[Dict[str, Any]] = None

    # Advanced OpenAI-compatible parameters
    n: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, float]] = None
    stop: Optional[Union[str, List[str]]] = None
    seed: Optional[int] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

    def copy(self) -> "ChatRequest":
        """Create a copy of this ChatRequest."""
        return ChatRequest(**self.model_dump())

    model_config = {
        "populate_by_name": True
    }


class Choice(BaseModel):
    """A choice in a chat response."""
    index: int
    message: Optional[Message] = None
    delta: Optional[Message] = None
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    """Response from a chat completion."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


class ChatChunk(BaseModel):
    """A chunk in a streaming chat response."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]


class ModelInfo(BaseModel):
    """Information about a model."""
    id: str
    object: str
    owned_by: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ModelCapabilities(BaseModel):
    """Capabilities of a model."""
    model_id: str
    supports_vision: bool
    supports_tools: bool
    supports_reasoning: bool
    max_context_tokens: Optional[int] = None
    provider_specific: Optional[Dict[str, Any]] = None


class CreditsBalance(BaseModel):
    """Credits balance information."""
    credits_remaining: int
    tier: str
    bands: List[str]
    reset_date: Optional[str] = None


class CreditsHistoryEntry(BaseModel):
    """An entry in the credits history."""
    id: str
    timestamp: str
    request_id: str
    model: str
    provider: str
    band: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    credits_debited: int
    cost: float
    latency_ms: int
    status: str


class CreditsHistory(BaseModel):
    """Credits history."""
    entries: List[CreditsHistoryEntry]
    total_entries: int
    next_cursor: Optional[str] = None


class CreditsStats(BaseModel):
    """Credits statistics."""
    period: str
    total_credits_used: int
    total_cost: float
    model_breakdown: List[Dict[str, Any]]