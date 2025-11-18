# Zaguan SDK Feature Checklist

This document is a **practical checklist** for SDK authors. Completing these items means an SDK has broad, production-ready coverage of Zaguan CoreX features.

Use this as a development and review tool.

## 1. Configuration

- [ ] **Base URL** is configurable (e.g. `http://localhost:8080`, `https://api.example.com`).
- [ ] **API key** configuration is supported (via constructor, env vars, or config object).
- [ ] Per-request overrides for **timeout** and, optionally, **headers** are supported.
- [ ] The SDK automatically adds `Authorization: Bearer <API_KEY>` to requests.
- [ ] The SDK generates a unique `X-Request-Id` per request if the user does not provide one.
- [ ] Users can override `X-Request-Id` per request.

## 2. Chat (Non-Streaming)

- [ ] `client.chat(request)` (or equivalent) is implemented.
- [ ] Request type supports:
  - [ ] `model`
  - [ ] `messages` (system/user/assistant, multimodal where supported)
  - [ ] `temperature`, `max_tokens`, `top_p`
  - [ ] `tools` and `tool_choice`
  - [ ] `response_format` (for JSON mode)
- [ ] Response type includes:
  - [ ] `id`, `model`, `created`
  - [ ] `choices` with `message` and `finish_reason`
  - [ ] `usage` with `prompt_tokens`, `completion_tokens`, `total_tokens`
  - [ ] Optional nested usage details (reasoning tokens, cached tokens, etc.).

## 3. Chat (Streaming)

- [ ] `client.chatStream(request)` (or equivalent) is implemented.
- [ ] Streaming interface is idiomatic for the language (e.g., channel, async iterator, async generator).
- [ ] Supports cancellation (context/AbortController/etc.).
- [ ] Emits chunks that correctly reflect OpenAI-style streaming deltas:
  - [ ] `delta` message fragments.
  - [ ] `finish_reason` when the stream ends.
- [ ] Optionally, helper(s) exist to reconstruct the final message from chunks.

## 4. Models & Capabilities

- [ ] `client.listModels()` returns parsed model structures.
- [ ] Provider-prefixed IDs (e.g. `openai/gpt-4o-mini`) are preserved.
- [ ] `client.getCapabilities()` (or similar) returns per-model capabilities when the endpoint is available.
- [ ] Capability types expose key fields (vision support, tools support, reasoning support, max context, etc.).

## 5. Provider-Specific Parameters / extra_body

- [ ] SDK exposes a way to pass **provider-specific parameters** without breaking type safety.
  - Example: a `providerOptions` / `extraBody` / `extensions` field.
- [ ] Documentation shows how to use this for common providers, such as:
  - [ ] Google Gemini reasoning controls (e.g. `reasoning_effort`).
  - [ ] Alibaba Qwen thinking controls.
  - [ ] Perplexity search and other options.
- [ ] The SDK does not strip or alter these fields before sending them to Zaguan.

## 6. Reasoning Tokens & Usage Details

- [ ] The `Usage` type includes fields for:
  - [ ] `promptTokens`
  - [ ] `completionTokens`
  - [ ] `totalTokens`
  - [ ] Optional `promptTokensDetails` fields.
  - [ ] Optional `completionTokensDetails` fields, including `reasoningTokens`.
- [ ] The SDK’s docs explain that not all providers populate reasoning tokens.
- [ ] Known provider behaviors are documented (for example: Perplexity’s reasoning tokens are in `<think>` content, not usage details).

## 7. Credits (If Enabled on Server)

- [ ] `client.getCreditsBalance()` is implemented.
- [ ] `client.getCreditsHistory(options?)` is implemented.
- [ ] `client.getCreditsStats(options?)` is implemented.
- [ ] Credits types include tier and band information where provided.
- [ ] Documentation explains how credits relate to model usage and bands.

## 8. Error Handling

- [ ] SDK defines a structured error type / exception including:
  - [ ] HTTP status code.
  - [ ] Error message.
  - [ ] Request ID (from response, if present).
  - [ ] Optionally, error type/code from server.
- [ ] Client code can distinguish between:
  - [ ] Client errors (4xx).
  - [ ] Server errors (5xx).
  - [ ] Network/transport errors.
- [ ] Optional retry logic is configurable and safe (no blind retries of non-idempotent operations).

## 9. Logging & Observability

- [ ] SDK exposes hooks or configuration for logging (request/response metadata, not full bodies by default).
- [ ] SDK allows capturing:
  - [ ] Request ID.
  - [ ] Model.
  - [ ] Latency.
  - [ ] HTTP status.
- [ ] These hooks are safe to use in high-volume production environments (no excessive allocations or blocking).

## 10. Forward Compatibility & Extensibility

- [ ] SDK is robust to unknown fields in responses (ignores them without failing).
- [ ] Most major types include a `metadata` or `extra` field for future expansion.
- [ ] The public API is versioned; breaking changes require a major version bump.

## 11. Documentation & Examples

- [ ] README or dedicated docs page for the SDK.
- [ ] Code examples for:
  - [ ] Basic chat.
  - [ ] Streaming chat.
  - [ ] Tools / function calling.
  - [ ] Multimodal (if applicable).
  - [ ] Provider-specific parameters.
  - [ ] Credits usage (if enabled).
- [ ] Clear explanation of how the SDK maps to Zaguan CoreX behavior and what deviations from raw OpenAI APIs exist.

When all of the above are checked, the SDK can be considered **feature-complete for v1**.
