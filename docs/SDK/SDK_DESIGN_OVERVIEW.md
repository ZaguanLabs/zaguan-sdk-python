# Zaguan SDK Design Overview

## Purpose

This document defines what a **Zaguan SDK** is and the baseline expectations for any official or community SDK (Go, TypeScript/JavaScript, Python, etc.).

A Zaguan SDK should:

- Make it **easy** to call Zaguan CoreX without dealing with raw HTTP.
- Expose **all important features** of CoreX, not just basic chat.
- Provide a **stable, ergonomic API** over:
  - OpenAI-compatible chat and related endpoints.
  - Zaguan-specific enhancements (routing, credits, reasoning tokens, etc.).
- Be **safe and production-ready** (timeouts, retries, streaming, request IDs).

This guide is language-agnostic: each SDK should map these ideas into its own idioms.

## What is Zaguan CoreX?

**Zaguan CoreX** is an enterprise-grade AI gateway that provides **unified access to 15+ AI providers and 500+ models** through a single, OpenAI-compatible API. It eliminates vendor lock-in, optimizes costs, and unlocks advanced capabilities that individual providers don't offer.

### Key Value Propositions

1. **Multi-Provider Abstraction**: Access OpenAI, Anthropic, Google, Alibaba, DeepSeek, Groq, Perplexity, xAI, Mistral, Cohere, and more through one API
2. **Cost Optimization**: 40-60% cost reduction through smart routing and provider arbitrage
3. **Advanced Features**: Reasoning control, multimodal AI, real-time data, long context windows
4. **Enterprise Performance**: 2-3x faster responses, 5,000+ concurrent connections
5. **Zero Vendor Lock-in**: Switch providers by changing model name only

## Target Users

SDKs are primarily for:

- **Application developers** who want a single API for many providers.
- **Platform/infrastructure teams** integrating credits, tiers, and bands.
- **Tooling authors** (CLI, agents, IDE extensions) who need:
  - Correct OpenAI compatibility.
  - Access to Zaguan-specific features.
- **Enterprise teams** requiring multi-provider AI infrastructure
- **SaaS platforms** building AI-powered products
- **Research teams** experimenting with multiple models

## High-Level Architecture

From the SDK’s perspective, the flow is:

```text
User Code
  ↓
Zaguan SDK
  ↓
HTTP (OpenAI-compatible API surface)
  ↓
Zaguan CoreX (translation layer, orchestration, providers)
```

Internally, CoreX:

- Normalizes requests into internal `core.*` types.
- Routes to providers (OpenAI, Anthropic, Google, Perplexity, xAI, etc.).
- Tracks usage, credits, reasoning tokens, and other metrics.

The SDK only talks to **Zaguan CoreX**, never directly to individual providers.

## Design Principles

- **Compatibility first**
  - Should feel familiar to users of OpenAI SDKs.
  - Migration from existing OpenAI client code should be straightforward.
  - Drop-in replacement for OpenAI SDK in most cases.

- **Zaguan-native features second**
  - Provide explicit, well-documented ways to access:
    - Routing features (virtual models, bands, provider preference).
    - Provider-specific parameters (e.g. Gemini reasoning effort, Anthropic extended thinking).
    - Reasoning and thinking controls.
    - Credits & usage tracking.
    - Multi-provider capabilities.

- **Minimal magic**
  - Defaults are safe and sensible.
  - Advanced features are opt-in but discoverable.
  - No hidden behavior or implicit conversions.

- **Language idiomatic**
  - Go: `context.Context`, error returns, interfaces.
  - TypeScript/JS: Promises, async iterators, typed objects.
  - Python: async/await, iterators, exceptions.

- **Production-ready**
  - Comprehensive error handling.
  - Request ID tracking for debugging.
  - Retry logic with exponential backoff.
  - Timeout configuration.
  - Streaming support with cancellation.

## Core Capabilities Every SDK MUST Expose

At a minimum, any official Zaguan SDK must expose:

### 1. Configuration

- Base URL (e.g. `https://your-zaguan-host`).
- API key (Bearer token authentication).
- Optional: timeout, retries, logging hooks, custom headers.
- Connection pooling and keep-alive settings.
- Custom HTTP client injection for advanced scenarios.

### 2. Chat Completions (OpenAI-style)

- Non-streaming chat (single response).
- Streaming chat (incremental chunks, cancellation support).
- Support for all OpenAI parameters: temperature, max_tokens, top_p, etc.
- Tool/function calling support.
- JSON mode and structured output.
- Multimodal content (text, images, audio).

These map to the primary `POST /v1/chat/completions` endpoint.

### 3. Models & Capabilities

- `GET /v1/models` — list models, including provider-prefixed names like `openai/gpt-4o-mini`, `anthropic/claude-3-opus`, `google/gemini-2.0-flash`.
- `GET /v1/capabilities` — detailed capability information (vision, reasoning, tools, max context, etc.), if enabled.
- Model filtering and search capabilities.

### 4. Credits & Usage (if credits enabled on the server)

- `GET /v1/credits/balance` — current balance, tier, bands, reset date.
- `GET /v1/credits/history` — historical usage with pagination.
- `GET /v1/credits/stats` — aggregated statistics by period, band, provider.

These allow applications to show remaining credits, usage history, and statistics.

### 5. Zaguan Extensions

- Provider-specific parameters via `provider_specific_params` or `extra_body`:
  - **Google Gemini**: `reasoning_effort` (none/low/medium/high), thinking budget.
  - **Anthropic**: Extended thinking API, prompt caching, citations.
  - **Alibaba Qwen**: Thinking controls, enable/disable reasoning.
  - **Perplexity**: Search options, citation modes.
  - **xAI**: Responses API for structured outputs.
  - **DeepSeek**: Thinking parameter control.
- Virtual models / routing hints, if your deployment uses them.
- Reasoning token exposure where supported by providers and CoreX.
- Band-based access control and tier management.

### 6. Observability Hooks

- Request ID handling (`X-Request-Id`).
  - Auto-generation if not provided.
  - Idempotency support.
- Optional user-provided hooks for logging and metrics, including:
  - Request start/end.
  - Request ID, model, latency, status.
  - Token usage and cost tracking.
  - Error details and retry attempts.

### 7. Advanced Features (Recommended)

- **Audio**: Transcription, translation, speech synthesis.
- **Images**: Generation, edits, variations.
- **Embeddings**: Text embeddings for semantic search.
- **Batches**: Batch processing for cost optimization.
- **Assistants**: Stateful conversation management.
- **Fine-tuning**: Model customization (where supported).
- **Moderations**: Content filtering and safety.

## Relationship to Existing OpenAI SDKs

Zaguan CoreX exposes an **OpenAI-compatible API** so existing OpenAI SDKs can be pointed at it with minimal changes. A Zaguan SDK goes further by:

- Providing first-class access to **Zaguan-specific features**.
- Handling CoreX’s **credits and accounting** endpoints.
- Offering a **stable, documented contract** for multi-provider usage.

For many users, the Zaguan SDK should be the **preferred integration path**, with “use the OpenAI SDK and point it at Zaguan” as a quick-start compatibility mode.

## Supported Providers

Zaguan CoreX supports 15+ AI providers with 500+ models:

| Provider          | Key Models                           | Capabilities                                                |
| ----------------- | ------------------------------------ | ----------------------------------------------------------- |
| **OpenAI**        | GPT-4o, GPT-4o-mini, o1, o3          | Vision, audio, reasoning, function calling, DALL-E, Whisper |
| **Google Gemini** | Gemini 2.0 Flash, Gemini 2.5 Pro     | 2M context, advanced reasoning, multimodal                  |
| **Anthropic**     | Claude 3.5 Sonnet, Claude 3 Opus     | Extended thinking, citations, prompt caching, vision        |
| **Alibaba Qwen**  | Qwen 2.5, QwQ                        | Advanced reasoning, thinking control, multilingual          |
| **DeepSeek**      | DeepSeek V3, DeepSeek R1             | Cost-effective reasoning, strong performance                |
| **Groq**          | Llama 3, Mixtral                     | Ultra-fast inference (500+ tokens/sec)                      |
| **Perplexity**    | Sonar, Sonar Reasoning               | Real-time web search, citations                             |
| **xAI**           | Grok 2, Grok 2 Vision                | Real-time data, structured responses API                    |
| **Mistral**       | Mistral Large, Mixtral               | Open models, multilingual                                   |
| **Cohere**        | Command R+, Embed                    | RAG optimization, rerank, classify                          |
| **Fireworks**     | 100+ models                          | DeepSeek, Llama, Qwen, vision models                        |
| **Together AI**   | Various                              | Open model hosting                                          |
| **OpenRouter**    | 200+ models                          | Multi-provider aggregation                                  |
| **Ollama**        | Local models                         | Privacy-sensitive, offline                                  |
| **+ More**        | Novita, Inception, Vercel, Synthetic | Specialized capabilities                                    |

## Provider-Specific Features

### Google Gemini Reasoning Control

```json
{
  "model": "google/gemini-2.5-pro",
  "messages": [...],
  "provider_specific_params": {
    "reasoning_effort": "high",
    "thinking_budget": 10000
  }
}
```

### Anthropic Extended Thinking

```json
{
  "model": "anthropic/claude-3-5-sonnet",
  "messages": [...],
  "provider_specific_params": {
    "thinking": {
      "type": "enabled",
      "budget_tokens": 5000
    }
  }
}
```

### Perplexity Search

```json
{
  "model": "perplexity/sonar-reasoning",
  "messages": [...],
  "provider_specific_params": {
    "search_domain_filter": ["example.com"],
    "return_citations": true
  }
}
```

### DeepSeek Thinking Control

```json
{
  "model": "deepseek/deepseek-reasoner",
  "messages": [...],
  "thinking": false
}
```

## Future: Zaguan-Native API Layer

Beyond OpenAI compatibility, SDKs may expose a higher-level, Zaguan-native API in the future:

- `chatVirtual("my-app-prod", request)` where CoreX selects the underlying model.
- Routing hints like `preferredProvider`, fallback providers, or bands.
- Explicit reasoning controls that abstract over provider differences.
- Automatic failover and retry across providers.
- Cost optimization with automatic model selection.

The documents in `docs/SDK` are written so that this layer can be added cleanly on top of the core HTTP contract and type system.

## Performance Characteristics

Zaguan CoreX is optimized for production workloads:

- **270% faster JSON processing** through custom optimizations
- **139x better streaming** with advanced buffer pooling
- **60% memory reduction** under heavy load
- **5,000+ concurrent connections** supported
- **10,000+ requests/second** throughput
- **Sub-50% CPU usage** at scale

## Security & Authentication

- **Bearer token authentication** via `Authorization` header
- **Database-backed API keys** with Argon2 hashing
- **Rate limiting** per IP and per key
- **Request validation** and size limits
- **Audit logging** for compliance
- **Test and live key separation**
