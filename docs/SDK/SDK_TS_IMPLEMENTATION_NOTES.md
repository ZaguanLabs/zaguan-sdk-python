# TypeScript SDK Implementation Notes

These notes specialize the generic SDK design for **TypeScript**. They describe an `@zaguan/sdk` (or similar) package that works in Node.js (and optionally in browsers) and talks to Zaguan CoreX.

Goals:

- Familiar to users of OpenAI’s official JS/TS client.
- Strong typings for requests and responses.
- First-class streaming via `AsyncIterable`.
- Easy integration in both backend services and frontend apps.

## Package Structure

Suggested layout:

```text
src/
  client.ts          // ZaguanClient class
  types.ts           // Shared types (ChatRequest, ChatResponse, Usage, etc.)
  errors.ts          // Error classes
  http.ts            // Internal HTTP helpers (fetch wrappers)

index.ts             // Re-exports public API
```

Build as ESM with type declarations, targeting Node 18+ (and modern browsers if desired).

## Configuration & Client

### Config Interface

```ts
export interface ZaguanConfig {
  baseUrl: string; // e.g. "https://api.zaguan.example.com"
  apiKey: string; // Bearer token
  timeoutMs?: number; // Optional per-request timeout
  fetch?: typeof fetch; // Optional custom fetch implementation
}
```

### Client Class

```ts
export class ZaguanClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly timeoutMs?: number;
  private readonly fetchImpl: typeof fetch;

  constructor(cfg: ZaguanConfig) {
    this.baseUrl = cfg.baseUrl.replace(/\/$/, '');
    this.apiKey = cfg.apiKey;
    this.timeoutMs = cfg.timeoutMs;
    this.fetchImpl = cfg.fetch ?? fetch;
  }

  // Core methods
  // chat, chatStream, listModels, getCapabilities, credits, etc.
}
```

### Per-Request Options

```ts
export interface RequestOptions {
  requestId?: string;
  timeoutMs?: number;
  headers?: Record<string, string>;
}
```

All client methods should accept `options?: RequestOptions`.

## Core Types (Chat)

### Message

```ts
export type Role = 'system' | 'user' | 'assistant' | 'tool';

export interface Message {
  role: Role;
  content: string | Array<{ type: string; [key: string]: any }>; // multimodal-friendly
  name?: string;
}
```

### ChatRequest

```ts
export interface ChatRequest {
  model: string;
  messages: Message[];

  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  stream?: boolean;
  tools?: any[]; // You can refine to a Tool type
  tool_choice?: string | Record<string, any>;
  response_format?: Record<string, any>;

  // Zaguan extensions
  provider_specific_params?: Record<string, any>;
}
```

### Usage

```ts
export interface TokenDetails {
  reasoning_tokens?: number;
  cached_tokens?: number;
  audio_tokens?: number;
  accepted_prediction_tokens?: number;
  rejected_prediction_tokens?: number;
}

export interface Usage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;

  prompt_tokens_details?: TokenDetails;
  completion_tokens_details?: TokenDetails;
}
```

### ChatResponse

```ts
export interface Choice {
  index: number;
  message?: Message;
  finish_reason?: string;
  // tool_calls, logprobs, etc. can be added as needed
}

export interface ChatResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Choice[];
  usage: Usage;
}
```

For streaming, define a `ChatChunk` / `ChoiceDelta` that mirrors OpenAI’s streaming chunks.

## Non-Streaming Chat Method

```ts
import { v4 as uuidv4 } from "uuid"; // or a light UUID function

export class ZaguanClient {
  ...

  async chat(request: ChatRequest, options: RequestOptions = {}): Promise<ChatResponse> {
    const requestId = options.requestId ?? uuidv4();
    const ctrl = new AbortController();
    const timeout = options.timeoutMs ?? this.timeoutMs;
    if (timeout) {
      setTimeout(() => ctrl.abort(), timeout).unref?.();
    }

    const res = await this.fetchImpl(`${this.baseUrl}/v1/chat/completions`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
        "X-Request-Id": requestId,
        ...(options.headers ?? {}),
      },
      body: JSON.stringify(request),
      signal: ctrl.signal,
    });

    return this.handleJsonResponse<ChatResponse>(res);
  }
}
```

`handleJsonResponse` should parse JSON, check `res.ok`, and throw a structured error on failure.

## Streaming Chat Method

Use `AsyncIterable` to expose streaming in an idiomatic way:

```ts
export interface ChatChunk {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    delta?: Message;
    finish_reason?: string;
  }>;
}

export class ZaguanClient {
  ...

  async *chatStream(request: ChatRequest, options: RequestOptions = {}): AsyncIterable<ChatChunk> {
    const requestId = options.requestId ?? uuidv4();
    const ctrl = new AbortController();
    const timeout = options.timeoutMs ?? this.timeoutMs;
    if (timeout) {
      setTimeout(() => ctrl.abort(), timeout).unref?.();
    }

    const body = { ...request, stream: true };

    const res = await this.fetchImpl(`${this.baseUrl}/v1/chat/completions`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
        "X-Request-Id": requestId,
        ...(options.headers ?? {}),
      },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    });

    if (!res.ok || !res.body) {
      await this.handleJsonError(res);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let newlineIndex: number;
      while ((newlineIndex = buffer.indexOf("\n")) >= 0) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);

        if (!line || !line.startsWith("data:")) continue;
        const dataStr = line.slice("data:".length).trim();
        if (dataStr === "[DONE]") return;

        const json = JSON.parse(dataStr);
        yield json as ChatChunk;
      }
    }
  }
}
```

This assumes SSE-like streaming lines (`data: { ... }`). Adjust if your server uses a slightly different format.

## Models & Capabilities

```ts
export interface ModelInfo {
  id: string;
  object: string;
  owned_by?: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface ModelCapabilities {
  model_id: string;
  supports_vision: boolean;
  supports_tools: boolean;
  supports_reasoning: boolean;
  max_context_tokens?: number;
  provider_specific?: Record<string, any>;
}

export class ZaguanClient {
  ...

  async listModels(options: RequestOptions = {}): Promise<ModelInfo[]> {
    const res = await this.fetchImpl(`${this.baseUrl}/v1/models`, {
      headers: this.headers(options),
    });
    const json = await this.handleJsonResponse<{ data: ModelInfo[] }>(res);
    return json.data;
  }

  async getCapabilities(options: RequestOptions = {}): Promise<ModelCapabilities[]> {
    const res = await this.fetchImpl(`${this.baseUrl}/v1/capabilities`, {
      headers: this.headers(options),
    });
    return this.handleJsonResponse<ModelCapabilities[]>(res);
  }

  private headers(options: RequestOptions): Record<string, string> {
    const requestId = options.requestId ?? uuidv4();
    return {
      "Authorization": `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
      "X-Request-Id": requestId,
      ...(options.headers ?? {}),
    };
  }
}
```

## Credits (Optional)

If exposing credits:

```ts
export interface CreditsBalance {
  credits_remaining: number;
  tier: string;
  bands: string[];
  reset_date?: string;
}

export class ZaguanClient {
  ...

  async getCreditsBalance(options: RequestOptions = {}): Promise<CreditsBalance> {
    const res = await this.fetchImpl(`${this.baseUrl}/v1/credits/balance`, {
      headers: this.headers(options),
    });
    return this.handleJsonResponse<CreditsBalance>(res);
  }
}
```

## Errors

Define structured error types:

```ts
export class ZaguanError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ZaguanError';
  }
}

export class APIError extends ZaguanError {
  readonly statusCode: number;
  readonly requestId?: string;

  constructor(statusCode: number, message: string, requestId?: string) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.requestId = requestId;
  }
}
```

`handleJsonResponse` should:

- Parse JSON.
- If `res.ok`: return parsed body.
- Else: extract an error message (if available) and request ID, then throw `APIError`.

## Testing Notes

- Use `vitest`, `jest`, or `mocha` + `chai` for tests.
- Mock `fetch` using `whatwg-fetch`, `msw`, or test doubles.
- For integration tests, point at a local CoreX instance and verify:
  - Non-streaming and streaming chat.
  - Usage (including reasoning tokens) where supported.
  - Error handling and request ID propagation.

These notes give you a concrete TS design aligned with the generic SDK docs and idiomatic for modern Node/JS environments.
