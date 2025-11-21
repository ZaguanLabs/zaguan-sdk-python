"""
Core data models for the Zaguan SDK.
"""

from typing import List, Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    A message in a chat conversation.
    
    Note: role is optional to support streaming deltas where role may not be present
    in every chunk. For non-streaming messages, role should always be provided.
    """
    role: Optional[Literal["system", "user", "assistant", "tool", "function", "developer"]] = None
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Dict[str, Any]] = None

    model_config = {
        "extra": "allow"  # Forward compatibility: ignore unknown fields
    }


class TokenDetails(BaseModel):
    """Detailed token usage information."""
    reasoning_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    accepted_prediction_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None

    model_config = {
        "extra": "allow"
    }


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[TokenDetails] = None
    completion_tokens_details: Optional[TokenDetails] = None

    model_config = {
        "extra": "allow"
    }


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
    extra_body: Optional[Dict[str, Any]] = None  # Alias for provider_specific_params

    # Advanced OpenAI-compatible parameters
    n: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, float]] = None
    stop: Optional[Union[str, List[str]]] = None
    seed: Optional[int] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    
    # Audio output (GPT-4o Audio)
    modalities: Optional[List[str]] = None
    audio: Optional[Dict[str, Any]] = None
    
    # Reasoning models (o1, o3, etc.)
    reasoning_effort: Optional[Literal["minimal", "low", "medium", "high"]] = None
    
    # DeepSeek-specific
    thinking: Optional[bool] = None
    
    # Zaguan extensions
    virtual_model_id: Optional[str] = None
    store: Optional[bool] = None
    verbosity: Optional[Literal["low", "medium", "high"]] = None
    parallel_tool_calls: Optional[bool] = None

    def copy(self) -> "ChatRequest":
        """Create a copy of this ChatRequest."""
        return ChatRequest(**self.model_dump())
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """
        Override model_dump to merge extra_body with provider_specific_params.
        This ensures compatibility with OpenAI SDK patterns.
        """
        data = super().model_dump(**kwargs)
        
        # Merge extra_body into provider_specific_params if both exist
        if data.get("extra_body") and data.get("provider_specific_params"):
            merged = {**data["provider_specific_params"], **data["extra_body"]}
            data["provider_specific_params"] = merged
            del data["extra_body"]
        elif data.get("extra_body"):
            # If only extra_body exists, rename it to provider_specific_params
            data["provider_specific_params"] = data["extra_body"]
            del data["extra_body"]
        
        return data

    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # Forward compatibility
    }


class Choice(BaseModel):
    """A choice in a chat response."""
    index: int
    message: Optional[Message] = None
    delta: Optional[Message] = None
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    model_config = {
        "extra": "allow"
    }


class ChatResponse(BaseModel):
    """Response from a chat completion."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    metadata: Optional[Dict[str, Any]] = None  # Extensibility field

    model_config = {
        "extra": "allow"
    }


class ChatChunk(BaseModel):
    """A chunk in a streaming chat response."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]

    model_config = {
        "extra": "allow"
    }


class ModelInfo(BaseModel):
    """Information about a model."""
    id: str
    object: str
    owned_by: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = {
        "extra": "allow"
    }


class ModelCapabilities(BaseModel):
    """Capabilities of a model."""
    model_id: str
    supports_vision: bool
    supports_tools: bool
    supports_reasoning: bool
    max_context_tokens: Optional[int] = None
    provider_specific: Optional[Dict[str, Any]] = None

    model_config = {
        "extra": "allow"
    }


class CreditsBalance(BaseModel):
    """Credits balance information."""
    credits_remaining: int
    tier: str
    bands: List[str]
    reset_date: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = {
        "extra": "allow"
    }


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


# ============================================================================
# Embeddings Models
# ============================================================================

class EmbeddingRequest(BaseModel):
    """Request for creating embeddings."""
    model: str
    input: Union[str, List[str]]
    encoding_format: Optional[Literal["float", "base64"]] = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None


class Embedding(BaseModel):
    """A single embedding vector."""
    object: str
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    """Response from embeddings endpoint."""
    object: str
    data: List[Embedding]
    model: str
    usage: Usage


# ============================================================================
# Audio Models
# ============================================================================

class AudioTranscriptionRequest(BaseModel):
    """Request for audio transcription."""
    file: bytes  # Audio file content
    model: str
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = "json"
    temperature: Optional[float] = None
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = None


class AudioTranslationRequest(BaseModel):
    """Request for audio translation."""
    file: bytes  # Audio file content
    model: str
    prompt: Optional[str] = None
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = "json"
    temperature: Optional[float] = None


class AudioTranscriptionResponse(BaseModel):
    """Response from audio transcription."""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None
    segments: Optional[List[Dict[str, Any]]] = None


class AudioSpeechRequest(BaseModel):
    """Request for text-to-speech."""
    model: str
    input: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: Optional[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]] = "mp3"
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0)


# ============================================================================
# Images Models
# ============================================================================

class ImageGenerationRequest(BaseModel):
    """Request for image generation."""
    model: Optional[str] = "dall-e-3"
    prompt: str
    n: Optional[int] = Field(default=1, ge=1, le=10)
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]] = "1024x1024"
    quality: Optional[Literal["standard", "hd"]] = "standard"
    response_format: Optional[Literal["url", "b64_json"]] = "url"
    style: Optional[Literal["vivid", "natural"]] = "vivid"
    user: Optional[str] = None


class ImageEditRequest(BaseModel):
    """Request for image editing."""
    image: bytes  # Image file content
    prompt: str
    mask: Optional[bytes] = None  # Mask file content
    model: Optional[str] = "dall-e-2"
    n: Optional[int] = Field(default=1, ge=1, le=10)
    size: Optional[Literal["256x256", "512x512", "1024x1024"]] = "1024x1024"
    response_format: Optional[Literal["url", "b64_json"]] = "url"
    user: Optional[str] = None


class ImageVariationRequest(BaseModel):
    """Request for image variations."""
    image: bytes  # Image file content
    model: Optional[str] = "dall-e-2"
    n: Optional[int] = Field(default=1, ge=1, le=10)
    size: Optional[Literal["256x256", "512x512", "1024x1024"]] = "1024x1024"
    response_format: Optional[Literal["url", "b64_json"]] = "url"
    user: Optional[str] = None


class ImageData(BaseModel):
    """A single generated/edited image."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None


class ImageResponse(BaseModel):
    """Response from image endpoints."""
    created: int
    data: List[ImageData]


# ============================================================================
# Moderations Models
# ============================================================================

class ModerationRequest(BaseModel):
    """Request for content moderation."""
    input: Union[str, List[str]]
    model: Optional[str] = "text-moderation-latest"


class ModerationCategories(BaseModel):
    """Moderation categories."""
    hate: bool
    hate_threatening: bool = Field(alias="hate/threatening")
    harassment: bool
    harassment_threatening: bool = Field(alias="harassment/threatening")
    self_harm: bool = Field(alias="self-harm")
    self_harm_intent: bool = Field(alias="self-harm/intent")
    self_harm_instructions: bool = Field(alias="self-harm/instructions")
    sexual: bool
    sexual_minors: bool = Field(alias="sexual/minors")
    violence: bool
    violence_graphic: bool = Field(alias="violence/graphic")

    model_config = {
        "populate_by_name": True
    }


class ModerationCategoryScores(BaseModel):
    """Moderation category scores."""
    hate: float
    hate_threatening: float = Field(alias="hate/threatening")
    harassment: float
    harassment_threatening: float = Field(alias="harassment/threatening")
    self_harm: float = Field(alias="self-harm")
    self_harm_intent: float = Field(alias="self-harm/intent")
    self_harm_instructions: float = Field(alias="self-harm/instructions")
    sexual: float
    sexual_minors: float = Field(alias="sexual/minors")
    violence: float
    violence_graphic: float = Field(alias="violence/graphic")

    model_config = {
        "populate_by_name": True
    }


class ModerationResult(BaseModel):
    """A single moderation result."""
    flagged: bool
    categories: ModerationCategories
    category_scores: ModerationCategoryScores


class ModerationResponse(BaseModel):
    """Response from moderation endpoint."""
    id: str
    model: str
    results: List[ModerationResult]


# ============================================================================
# Anthropic Messages API (Native)
# ============================================================================

class AnthropicThinkingConfig(BaseModel):
    """Configuration for Anthropic's extended thinking feature (Beta)."""
    type: Literal["enabled", "disabled"]
    budget_tokens: Optional[int] = Field(None, ge=1000, le=10000)


class AnthropicContentBlock(BaseModel):
    """A content block in an Anthropic message."""
    type: str  # "text", "thinking", "tool_use", "tool_result", "image"
    text: Optional[str] = None
    thinking: Optional[str] = None
    signature: Optional[str] = None  # Verification signature for thinking blocks
    id: Optional[str] = None  # For tool_use blocks
    name: Optional[str] = None  # For tool_use blocks
    input: Optional[Dict[str, Any]] = None  # For tool_use blocks
    tool_use_id: Optional[str] = None  # For tool_result blocks
    content: Optional[Union[str, List[Dict[str, Any]]]] = None  # For tool_result blocks
    source: Optional[Dict[str, Any]] = None  # For image blocks

    model_config = {
        "extra": "allow"  # Forward compatibility
    }


class AnthropicMessage(BaseModel):
    """A message in Anthropic's native format."""
    role: Literal["user", "assistant"]
    content: Union[str, List[AnthropicContentBlock]]

    model_config = {
        "extra": "allow"
    }


class AnthropicUsage(BaseModel):
    """Token usage information in Anthropic format."""
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None

    model_config = {
        "extra": "allow"
    }


class AnthropicMessagesRequest(BaseModel):
    """Request for Anthropic's native Messages API."""
    model: str
    messages: List[AnthropicMessage]
    max_tokens: int  # Required by Anthropic
    system: Optional[Union[str, List[Dict[str, Any]]]] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=0)
    stop_sequences: Optional[List[str]] = None
    stream: Optional[bool] = False
    thinking: Optional[AnthropicThinkingConfig] = None
    metadata: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None

    model_config = {
        "extra": "allow"
    }


class AnthropicMessagesResponse(BaseModel):
    """Response from Anthropic's Messages API."""
    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    content: List[AnthropicContentBlock]
    model: str
    stop_reason: Optional[str] = None  # "end_turn", "max_tokens", "stop_sequence", "tool_use"
    stop_sequence: Optional[str] = None
    usage: AnthropicUsage

    model_config = {
        "extra": "allow"
    }


class AnthropicMessagesDelta(BaseModel):
    """Delta for streaming Anthropic messages."""
    type: str
    text: Optional[str] = None
    thinking: Optional[str] = None
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None

    model_config = {
        "extra": "allow"
    }


class AnthropicMessagesStreamEvent(BaseModel):
    """A streaming event from Anthropic's Messages API."""
    type: str  # "message_start", "content_block_start", "content_block_delta", "content_block_stop", "message_delta", "message_stop"
    message: Optional[AnthropicMessagesResponse] = None
    index: Optional[int] = None
    content_block: Optional[AnthropicContentBlock] = None
    delta: Optional[AnthropicMessagesDelta] = None
    usage: Optional[AnthropicUsage] = None

    model_config = {
        "extra": "allow"
    }


class AnthropicCountTokensRequest(BaseModel):
    """Request for counting tokens in an Anthropic message."""
    model: str
    messages: List[AnthropicMessage]
    system: Optional[Union[str, List[Dict[str, Any]]]] = None
    tools: Optional[List[Dict[str, Any]]] = None


class AnthropicCountTokensResponse(BaseModel):
    """Response from Anthropic token counting."""
    input_tokens: int


class AnthropicMessagesBatchItem(BaseModel):
    """A single item in an Anthropic batch request."""
    custom_id: str
    params: AnthropicMessagesRequest


class AnthropicMessagesBatchRequest(BaseModel):
    """Request to create an Anthropic message batch."""
    requests: List[AnthropicMessagesBatchItem]


class AnthropicMessagesBatchResponse(BaseModel):
    """Response from Anthropic batch operations."""
    id: str
    type: Literal["message_batch"]
    processing_status: str  # "in_progress", "canceling", "ended"
    request_counts: Dict[str, int]  # {"processing": 0, "succeeded": 10, "errored": 0, "canceled": 0, "expired": 0}
    ended_at: Optional[str] = None
    created_at: str
    expires_at: str
    cancel_initiated_at: Optional[str] = None
    results_url: Optional[str] = None

    model_config = {
        "extra": "allow"
    }