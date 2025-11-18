# Zaguan SDK Core Types & Concepts

This document defines the **logical types and concepts** that every Zaguan SDK should expose. Names and exact shapes may vary per language, but the semantics must be consistent.

## Overview

Zaguan CoreX provides an OpenAI-compatible API surface with extensions for multi-provider features. SDKs should:

1. **Preserve OpenAI compatibility** - All standard OpenAI types work as expected
2. **Expose provider extensions** - Via `provider_specific_params` or `extra_body`
3. **Handle reasoning tokens** - Support detailed token breakdowns
4. **Support multimodal** - Text, images, audio content
5. **Enable credits tracking** - When credits system is enabled

## Client

Each SDK should provide a primary `Client` type responsible for:

- Holding configuration (base URL, API key, timeouts, etc.).
- Exposing high-level methods for interacting with Zaguan CoreX.

Conceptual interface:

- `chat(request) -> ChatResponse`
- `chatStream(request) -> stream<ChatChunk>`
- `listModels() -> Model[]`
- `getCapabilities() -> Capability[] | map`
- `getCreditsBalance() -> CreditsBalance` (if credits enabled)
- `getCreditsHistory(options?) -> CreditsHistory` (if credits enabled)
- `getCreditsStats(options?) -> CreditsStats` (if credits enabled)

## Chat Request

The chat request is modeled after OpenAI's `ChatCompletionRequest`, with Zaguan-specific extensions.

### Standard OpenAI Fields

- `model: string` **[REQUIRED]**
  - Provider-prefixed format: `"provider/model-name"`
  - Examples: `"openai/gpt-4o-mini"`, `"anthropic/claude-3-opus"`, `"google/gemini-2.0-flash"`
  - Also supports unprefixed names for backward compatibility
- `messages: Message[]` **[REQUIRED]**
  - Array of conversation messages
- `temperature?: number` (0.0 - 2.0)
  - Controls randomness in responses
- `max_tokens?: number`
  - Maximum tokens to generate
  - Note: Some providers use `maxTokens` (camelCase)
- `top_p?: number` (0.0 - 1.0)
  - Nucleus sampling parameter
- `stream?: boolean`
  - Enable streaming responses (SSE format)
- `stop?: string[]`
  - Stop sequences
- `presence_penalty?: number` (-2.0 - 2.0)
- `frequency_penalty?: number` (-2.0 - 2.0)
- `logit_bias?: Record<string, number>`
- `user?: string`
  - End-user identifier for abuse monitoring

### Function/Tool Calling

- `tools?: Tool[]`
  - Array of available tools/functions
- `tool_choice?: string | object`
  - `"none"`, `"auto"`, `"required"`, or specific tool
- `parallel_tool_calls?: boolean`
  - Allow parallel tool execution

### Structured Output

- `response_format?: object`
  - `{ type: "text" }` - Default text output
  - `{ type: "json_object" }` - JSON mode
  - `{ type: "json_schema", json_schema: {...} }` - Strict schema validation

### Audio Output (GPT-4o Audio)

- `modalities?: string[]`
  - `["text", "audio"]` for audio output
- `audio?: object`
  - `{ voice: "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer" }`
  - `{ format: "wav" | "mp3" | "opus" | "aac" | "flac" | "pcm" }`

### Reasoning Models (o1, o3, etc.)

- `reasoning_effort?: string`
  - `"minimal"`, `"low"`, `"medium"`, `"high"`
  - For OpenAI o1/o3 and similar reasoning models

### Zaguan-Specific Extensions

- `provider_specific_params?: Record<string, any>`
  - **Primary extension mechanism** for provider features
  - Passed through to the provider without modification
  - See "Provider-Specific Parameters" section below
- `extra_body?: Record<string, any>`
  - Alternative name for `provider_specific_params` (OpenAI SDK compatibility)
- `thinking?: boolean`
  - **DeepSeek-specific**: Enable/disable reasoning output
  - When `false`, suppresses `<think>` tags in response
- `virtual_model_id?: string`
  - If your deployment uses virtual/alias models
- `metadata?: Record<string, any>`
  - Application metadata (user ID, trace ID, etc.)
  - Not interpreted by CoreX, passed through for logging
- `store?: boolean`
  - Enable conversation storage (if supported)
- `verbosity?: string`
  - `"low"`, `"medium"`, `"high"` for some models

## Message

Messages follow the OpenAI chat format closely for maximum compatibility.

### Message Structure

- `role: string` **[REQUIRED]**
  - `"system"` - System instructions
  - `"user"` - User messages
  - `"assistant"` - Assistant responses
  - `"tool"` - Tool/function call results
  - `"function"` - Legacy function call results
  - `"developer"` - Developer messages (some providers)
- `content: string | Array<ContentPart>` **[REQUIRED for most roles]**
  - Simple string for text-only messages
  - Array of content parts for multimodal messages
- `name?: string`
  - Name of the user/assistant/function
- `tool_calls?: ToolCall[]`
  - Tool calls made by assistant (assistant role only)
- `tool_call_id?: string`
  - ID of the tool call being responded to (tool role only)
- `function_call?: object`
  - Legacy function call format

### Content Parts (Multimodal)

#### Text Content

```json
{
  "type": "text",
  "text": "Describe this image"
}
```

#### Image Content (URL)

```json
{
  "type": "image_url",
  "image_url": {
    "url": "https://example.com/image.jpg",
    "detail": "high" | "low" | "auto"
  }
}
```

#### Image Content (Base64)

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
}
```

#### Audio Input (GPT-4o Audio)

```json
{
  "type": "input_audio",
  "input_audio": {
    "data": "base64_encoded_audio",
    "format": "wav" | "mp3"
  }
}
```

### Example Messages

#### Simple Text

```json
{
  "role": "user",
  "content": "Hello, how are you?"
}
```

#### Multimodal (Vision)

```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "What's in this image?"
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/photo.jpg"
      }
    }
  ]
}
```

#### Tool Call Response

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "{\"result\": \"success\"}"
}
```

## Tools / Function Calling

Tools mirror OpenAI’s `tools` / `functions` mechanism.

Conceptual type:

- `Tool`:
  - `type: "function"`
  - `function: { name: string; description?: string; parameters: JSONSchema }`

SDK responsibilities:

- Allow users to define tools with minimal friction.
- Preserve JSON Schema for `parameters`.
- Support tool call results via messages with `role: "tool"` (or equivalent), as per OpenAI format.

## Chat Response

Chat responses should follow OpenAI’s shape, with Zaguan-aware usage information.

Common fields:

- `id: string`
- `model: string`
- `created: number`
- `choices: Choice[]`
- `usage: Usage`

Where `Choice` has fields like:

- `index: number`
- `message?: Message` (for non-streaming)
- `delta?: Message` (for streaming)
- `finishReason?: string`
- `toolCalls?: ToolCall[]` (if using tools)

### Streaming Responses

For `chatStream`, the SDK should surface a sequence/stream of `ChatChunk`/`ChoiceDelta` objects that correspond to OpenAI’s streaming chunks.

SDKs may optionally provide helpers to:

- Reconstruct the final message from all `delta` chunks.
- Track intermediate usage if CoreX exposes such data.

## Usage (Including Reasoning Tokens)

Usage is a critical part of the SDK, especially for billing and analytics.

### Base Usage Fields

- `prompt_tokens: number` **[REQUIRED]**
  - Tokens in the input/prompt
- `completion_tokens: number` **[REQUIRED]**
  - Tokens in the generated output
- `total_tokens: number` **[REQUIRED]**
  - Sum of prompt and completion tokens

### Detailed Token Breakdown

#### Prompt Token Details

- `prompt_tokens_details?: object`
  - `cached_tokens?: number` - Tokens served from cache (Anthropic, OpenAI)
  - `audio_tokens?: number` - Audio input tokens (GPT-4o Audio)

#### Completion Token Details

- `completion_tokens_details?: object`
  - `reasoning_tokens?: number` - **Reasoning/thinking tokens**
    - Populated by: OpenAI o1/o3, Google Gemini (with reasoning), DeepSeek
    - **NOT populated by**: Perplexity (uses `<think>` tags in content)
  - `audio_tokens?: number` - Audio output tokens (GPT-4o Audio)
  - `accepted_prediction_tokens?: number` - Accepted predicted tokens (prompt caching)
  - `rejected_prediction_tokens?: number` - Rejected predicted tokens

### Provider-Specific Usage Behavior

#### OpenAI (o1, o3, o1-mini)

- ✅ Populates `reasoning_tokens`
- ✅ Reasoning tokens counted separately
- ✅ Included in `completion_tokens`

#### Google Gemini (with reasoning_effort)

- ✅ Populates `reasoning_tokens` when `reasoning_effort` is set
- ✅ Separate thinking token count
- ✅ Thinking content available in response

#### Anthropic Claude (Extended Thinking)

- ✅ Populates `reasoning_tokens` when extended thinking is enabled
- ✅ Thinking blocks separate from main content
- ✅ Can control thinking budget

#### DeepSeek (R1, Reasoner)

- ✅ Populates `reasoning_tokens`
- ⚠️ Reasoning in `<think>` tags (also in content)
- ✅ Can disable with `thinking: false`

#### Perplexity (Sonar Reasoning)

- ❌ Does NOT populate `reasoning_tokens`
- ⚠️ Reasoning embedded in `<think>` tags in content
- ℹ️ Must parse content to extract reasoning

#### Alibaba Qwen (QwQ)

- ✅ Populates `reasoning_tokens`
- ✅ Thinking control via provider params
- ✅ Separate thinking content

### Example Usage Objects

#### Basic Usage

```json
{
  "prompt_tokens": 50,
  "completion_tokens": 100,
  "total_tokens": 150
}
```

#### With Reasoning Tokens

```json
{
  "prompt_tokens": 50,
  "completion_tokens": 150,
  "total_tokens": 200,
  "completion_tokens_details": {
    "reasoning_tokens": 50
  }
}
```

#### With Caching

```json
{
  "prompt_tokens": 1000,
  "completion_tokens": 100,
  "total_tokens": 1100,
  "prompt_tokens_details": {
    "cached_tokens": 900
  }
}
```

#### With Audio

```json
{
  "prompt_tokens": 50,
  "completion_tokens": 100,
  "total_tokens": 150,
  "prompt_tokens_details": {
    "audio_tokens": 20
  },
  "completion_tokens_details": {
    "audio_tokens": 30
  }
}
```

### SDK Implementation Notes

- Expose all fields as **optional** in type system
- Document provider-specific behavior clearly
- For Perplexity, provide helper to extract `<think>` content
- Consider adding `hasReasoningTokens()` helper method
- Log warnings when reasoning tokens expected but not present

## Models & Capabilities

### Model

A `Model` represents an entry from `GET /v1/models`.

Suggested fields:

- `id: string` (includes provider prefix, e.g. `"openai/gpt-4o-mini"`).
- `ownedBy?: string` (provider or owner).
- `description?: string`.
- `metadata?: Record<string, any>`.

SDKs may simply mirror the server’s JSON response into a typed model structure.

### Capabilities

`GET /v1/capabilities` returns detailed capability information per model.

Suggested conceptual shape:

- `modelId: string`
- `supportsVision: boolean`
- `supportsTools: boolean`
- `supportsReasoning: boolean`
- `maxContextTokens?: number`
- `supportsAudioIn?: boolean`
- `supportsAudioOut?: boolean`
- `providerSpecific?: Record<string, any>`

SDK authors can refine this based on the actual API schema, but should aim to:

- Make capability queries easy.
- Avoid losing important provider-specific flags.

## Provider-Specific Parameters

The `provider_specific_params` (or `extra_body`) field is the **primary extension mechanism** for accessing provider-specific features.

### Google Gemini

```json
{
  "provider_specific_params": {
    "reasoning_effort": "none" | "low" | "medium" | "high",
    "thinking_budget": 10000,
    "include_thinking": true
  }
}
```

### Anthropic Claude

```json
{
  "provider_specific_params": {
    "thinking": {
      "type": "enabled",
      "budget_tokens": 5000
    },
    "system": [
      {
        "type": "text",
        "text": "System prompt",
        "cache_control": { "type": "ephemeral" }
      }
    ]
  }
}
```

### Perplexity

```json
{
  "provider_specific_params": {
    "search_domain_filter": ["example.com"],
    "return_images": false,
    "return_related_questions": true,
    "search_recency_filter": "month"
  }
}
```

### Alibaba Qwen

```json
{
  "provider_specific_params": {
    "enable_thinking": true,
    "thinking_budget": 8000
  }
}
```

### xAI Grok

```json
{
  "provider_specific_params": {
    "response_format": {
      "type": "json_schema",
      "json_schema": {...}
    }
  }
}
```

### OpenAI (Flex Processing)

```json
{
  "provider_specific_params": {
    "flex": true,
    "flex_priority": "low"
  }
}
```

## Credits & Accounting

When credits system is enabled, responses may include credit information.

### PromptShield Metadata

```json
{
  "promptshield": {
    "credits_used": 5,
    "credits_remaining": 495,
    "credits_total": 500,
    "credits_percent": 99,
    "reset_date": "2025-01-01T00:00:00Z",
    "warning": "Low credits: 10% remaining"
  }
}
```

### Credits Balance Response

```json
{
  "credits_remaining": 495,
  "tier": "pro",
  "bands": ["A", "B", "C"],
  "reset_date": "2025-01-01T00:00:00Z",
  "stripe_price_id": "price_123"
}
```

### Credits History Entry

```json
{
  "id": "hist_123",
  "timestamp": "2024-11-18T10:30:00Z",
  "request_id": "req_abc",
  "model": "openai/gpt-4o-mini",
  "provider": "openai",
  "band": "A",
  "prompt_tokens": 50,
  "completion_tokens": 100,
  "total_tokens": 150,
  "credits_debited": 5,
  "cost": 0.0015,
  "latency_ms": 1250,
  "status": "success"
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "message": "Insufficient credits",
    "type": "insufficient_credits",
    "code": "insufficient_credits",
    "param": null
  }
}
```

### Insufficient Credits Error

```json
{
  "error": {
    "message": "Insufficient credits: 5 required, 3 remaining",
    "type": "insufficient_credits",
    "code": "insufficient_credits",
    "credits_required": 5,
    "credits_remaining": 3,
    "reset_date": "2025-01-01T00:00:00Z"
  }
}
```

### Band Access Denied Error

```json
{
  "error": {
    "message": "Access denied to band D (requires platinum tier)",
    "type": "band_access_denied",
    "code": "band_access_denied",
    "band": "D",
    "required_tier": "platinum",
    "current_tier": "pro"
  }
}
```

### Rate Limit Error

```json
{
  "error": {
    "message": "Rate limit exceeded",
    "type": "rate_limit_exceeded",
    "code": "rate_limit_exceeded",
    "retry_after": 60
  }
}
```

## Metadata & Extensibility

To allow future extension without breaking changes:

- Most top-level types should have a **generic/opaque metadata field**, e.g. `metadata: Record<string, any>`.
- SDKs should ignore unknown fields from the server instead of failing.
- Use optional fields for new capabilities.
- Maintain backward compatibility in type definitions.

This ensures that CoreX can evolve and add new fields without requiring immediate SDK updates.

## Type Safety Recommendations

### Strongly Typed Languages (Go, TypeScript)

- Use union types for `content` (string | ContentPart[])
- Use enums for known string values (role, finish_reason)
- Make optional fields truly optional (pointers in Go, `?` in TS)
- Provide type guards for discriminated unions

### Dynamically Typed Languages (Python)

- Use type hints (Python 3.7+)
- Provide Pydantic models or dataclasses
- Document expected types in docstrings
- Validate at runtime when possible

### All Languages

- Provide helper methods for common patterns
- Include examples in documentation
- Test with real API responses
- Handle missing/null fields gracefully
