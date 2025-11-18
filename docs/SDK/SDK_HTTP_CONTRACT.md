# Zaguan SDK HTTP & Auth Contract

This document defines the **wire-level contract** that all Zaguan SDKs must honor when talking to Zaguan CoreX.

## Base URL & Endpoints

### Base URL

SDKs must allow configuring a base URL, for example:

- `http://localhost:8080` for local development.
- `https://api.your-zaguan-host.com` for production.

### Core Endpoints

Every SDK MUST support these endpoints:

- `POST /v1/chat/completions`
  - Primary chat endpoint.
  - OpenAI-compatible request and response shape.
- `GET /v1/models`
  - Lists available models with provider-prefixed IDs (e.g. `openai/gpt-4o-mini`).
- `GET /v1/capabilities`
  - Returns detailed capability information per model (vision, tools, reasoning, etc.), when enabled.

SDKs SHOULD support, or be designed to easily add, additional endpoints exposed by CoreX (audio, images, batches, assistants) as documented elsewhere.

### Credits Endpoints (Optional but Recommended)

If the server has credits enabled, SDKs SHOULD expose typed accessors for:

- `GET /v1/credits/balance`
- `GET /v1/credits/history`
- `GET /v1/credits/stats`

These are particularly important for SaaS dashboards and admin tools.

### Health Endpoint

- `GET /health`

SDKs do not need to expose this as part of the public API, but can use it internally for diagnostics or health checks.

## Authentication

### API Key

Zaguan CoreX uses standard Bearer token authentication:

```http
Authorization: Bearer <API_KEY>
```

SDKs must:

- Require an API key at client configuration time, or accept it via environment variables/config.
- Attach the header to **every** authenticated request.

### Multiple Keys

SDKs may support multiple clients (one per key) or facilities like:

- Multi-tenant scenarios.
- Per-user or per-team API keys.

This is an SDK design decision, but it must remain compatible with the underlying Bearer-token model.

## Request IDs (`X-Request-Id`)

The credits and accounting system in CoreX relies on stable request IDs.

SDKs should:

- Automatically generate a **unique request ID** (e.g. UUID) for each request when the user does not provide one.
- Allow the user to **explicitly provide** a request ID per request.
- Send it as:

```http
X-Request-Id: <value>
```

This enables:

- Idempotency and safe retries at the server side.
- Accurate credits accounting.
- Easier debugging and log correlation.

## Streaming Protocol

For streaming chat (`stream: true` in the request body to `/v1/chat/completions`):

- CoreX follows the OpenAI streaming semantics (Server-Sent Events / chunked responses).
- SDKs must:
  - Support establishing a streaming request.
  - Emit chunks incrementally as they arrive.
  - Provide a way to **cancel** an in-progress stream.

Idiomatic streaming interfaces by language:

- Go: channel of `ChatCompletionChunk`, or callback-based API.
- TypeScript/JS: `AsyncIterable<ChatCompletionChunk>` or event emitter.
- Python: async generator (`async for chunk in client.chat_stream(...):`).

SDKs should:

- Preserve the structure of `delta` and `finish_reason` fields from OpenAI.
- Optionally offer helpers to reconstruct the final message from chunks.

## Error Handling

SDKs must:

- Treat HTTP status codes appropriately:
  - `2xx`: success.
  - `4xx`: client errors (invalid input, auth, etc.).
  - `5xx`: server errors.
- Parse error responses into a structured error type, including at minimum:
  - `statusCode` (HTTP code).
  - `message` (error message from server, if present).
  - `requestId` (from response headers, if present).
  - Optionally, `type` or provider-specific error codes if CoreX exposes them.

### Retries

SDKs should **not** automatically retry non-idempotent operations by default.

They may provide optional, configurable retry policies for:

- Network errors (connection reset, timeout).
- Certain `5xx` responses, if safe.

Retries must:

- Respect backoff (e.g. exponential).
- Respect context cancellation / abort signals.

## Headers & Content Types

SDKs must:

- Send JSON requests with:

```http
Content-Type: application/json
```

- Accept JSON responses.
- Handle gzip or other compression transparently if the HTTP library supports it.

## Timeouts

SDKs should:

- Provide sensible default timeouts (e.g. 30–60 seconds for chat).
- Allow per-request timeout override.
- Allow a global client-level timeout configuration.

Timeouts should be implemented in a way that is idiomatic for the language (e.g., `context.Context` in Go, `AbortController` in JS, etc.).

## Forward Compatibility

SDKs should be robust to:

- **Extra fields** in responses (ignore unknown fields rather than failing).
- **Optional fields** becoming present over time (e.g. new usage details).

This ensures that CoreX can evolve without immediately breaking clients.
