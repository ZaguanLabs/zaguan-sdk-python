# Go SDK Implementation Notes

These notes specialize the generic SDK design for **Go**. They are a blueprint for a `zaguansdk` (or similar) Go module that talks to Zaguan CoreX.

The goal is to make it easy for Go services to call Zaguan with:

- Idiomatic `context.Context` usage.
- Strong typing for requests and responses.
- Proper streaming support.
- Clear error handling.

## Package Layout

Suggested minimal layout:

```text
zaguansdk/
  client.go        // Client, configuration, core methods
  chat.go          // Chat request/response types + helpers
  models.go        // Model & capability types
  credits.go       // Credits-related client methods & types (optional)
  errors.go        // Error types
```

You can refine this layout as the SDK grows.

## Configuration & Client

### Config Struct

Define a configuration struct to hold core settings:

```go
type Config struct {
    BaseURL    string        // e.g. "https://api.zaguan.example.com"
    APIKey     string        // Bearer token
    HTTPClient *http.Client  // Optional; use http.DefaultClient if nil
    Timeout    time.Duration // Optional per-request timeout
}
```

### Client Struct

```go
type Client struct {
    baseURL    string
    apiKey     string
    httpClient *http.Client
    timeout    time.Duration
}

func NewClient(cfg Config) *Client {
    hc := cfg.HTTPClient
    if hc == nil {
        hc = http.DefaultClient
    }
    return &Client{
        baseURL:    strings.TrimRight(cfg.BaseURL, "/"),
        apiKey:     cfg.APIKey,
        httpClient: hc,
        timeout:    cfg.Timeout,
    }
}
```

### Per-Request Options

Consider a `RequestOptions` struct for overrides:

```go
type RequestOptions struct {
    RequestID string        // Optional; auto-generated if empty
    Timeout   time.Duration // Optional; overrides client timeout
    Headers   http.Header   // Optional extra headers
}
```

All client methods should accept `ctx context.Context` and an optional `*RequestOptions`.

## Core Types (Chat)

### ChatRequest

Mirror OpenAI’s schema, plus Zaguan extensions:

```go
type ChatRequest struct {
    Model       string            `json:"model"`
    Messages    []Message         `json:"messages"`
    Temperature *float32          `json:"temperature,omitempty"`
    MaxTokens   *int              `json:"max_tokens,omitempty"`
    TopP        *float32          `json:"top_p,omitempty"`
    Stream      bool              `json:"stream,omitempty"`
    Tools       []Tool            `json:"tools,omitempty"`
    ToolChoice  any               `json:"tool_choice,omitempty"`
    ResponseFmt any               `json:"response_format,omitempty"`

    // Zaguan extensions
    ProviderOptions map[string]any `json:"provider_specific_params,omitempty"`
    // VirtualModelID, metadata, etc. can be added if used by your deployment
}
```

### Message

```go
type Role string

const (
    RoleSystem    Role = "system"
    RoleUser      Role = "user"
    RoleAssistant Role = "assistant"
    RoleTool      Role = "tool"
)

type Message struct {
    Role    Role         `json:"role"`
    Content any          `json:"content"` // string or []ContentPart
    Name    string       `json:"name,omitempty"`
    // Tool call fields as needed
}
```

You can refine `Content` into concrete types (`string` vs `[]ContentPart`) using custom marshalers if desired.

### ChatResponse & Usage

```go
type ChatResponse struct {
    ID      string    `json:"id"`
    Object  string    `json:"object"`
    Created int64     `json:"created"`
    Model   string    `json:"model"`
    Choices []Choice  `json:"choices"`
    Usage   Usage     `json:"usage"`
}

type Choice struct {
    Index        int      `json:"index"`
    Message      Message  `json:"message,omitempty"`
    FinishReason string   `json:"finish_reason,omitempty"`
    // Tool calls, logprobs, etc., as needed
}

type Usage struct {
    PromptTokens     int            `json:"prompt_tokens"`
    CompletionTokens int            `json:"completion_tokens"`
    TotalTokens      int            `json:"total_tokens"`

    PromptTokensDetails     *TokenDetails `json:"prompt_tokens_details,omitempty"`
    CompletionTokensDetails *TokenDetails `json:"completion_tokens_details,omitempty"`
}

type TokenDetails struct {
    ReasoningTokens          int `json:"reasoning_tokens,omitempty"`
    CachedTokens             int `json:"cached_tokens,omitempty"`
    AudioTokens              int `json:"audio_tokens,omitempty"`
    AcceptedPredictionTokens int `json:"accepted_prediction_tokens,omitempty"`
    RejectedPredictionTokens int `json:"rejected_prediction_tokens,omitempty"`
}
```

## Chat Methods

### Non-Streaming Chat

```go
func (c *Client) Chat(ctx context.Context, req ChatRequest, opts *RequestOptions) (*ChatResponse, error) {
    // 1. Apply timeout via context if cfg.Timeout/opts.Timeout are set
    // 2. Marshal req -> JSON
    // 3. Build HTTP request to POST /v1/chat/completions
    // 4. Add Authorization and X-Request-Id headers
    // 5. Send request and decode JSON into ChatResponse
}
```

Key points:

- Use `context.WithTimeout` if `opts.Timeout` or `c.timeout` is non-zero.
- Generate a UUID for `X-Request-Id` if `opts.RequestID` is empty.
- Wrap errors with enough context (URL, status code) while preserving original messages.

### Streaming Chat

Idiomatic Go options:

1. Return a **receive-only channel** of `ChatResponseChunk`:

   ```go
   type ChatStream struct {
       Ch   <-chan ChatResponseChunk
       Err  chan error   // or error once closed
       Done <-chan struct{}
   }

   func (c *Client) ChatStream(ctx context.Context, req ChatRequest, opts *RequestOptions) (*ChatStream, error) {
       // Similar to Chat, but with stream: true and SSE/chunk handling
   }
   ```

2. Or provide a **callback-based API**:

   ```go
   func (c *Client) ChatStream(ctx context.Context, req ChatRequest, opts *RequestOptions, onChunk func(ChatResponseChunk) error) error
   ```

Either way, implementation should:

- Set `req.Stream = true`.
- Read the HTTP response body line-by-line / event-by-event.
- Unmarshal each JSON chunk into a `ChatResponseChunk` type that mirrors OpenAI’s streaming delta.
- Stop on context cancellation, EOF, or error.

## Models & Capabilities

### Models

```go
type Model struct {
    ID          string         `json:"id"`
    Object      string         `json:"object"`
    OwnedBy     string         `json:"owned_by,omitempty"`
    Description string         `json:"description,omitempty"`
    Metadata    map[string]any `json:"metadata,omitempty"`
}

func (c *Client) ListModels(ctx context.Context, opts *RequestOptions) ([]Model, error) {
    // GET /v1/models
}
```

### Capabilities

```go
type ModelCapabilities struct {
    ModelID           string         `json:"model_id"`
    SupportsVision    bool           `json:"supports_vision"`
    SupportsTools     bool           `json:"supports_tools"`
    SupportsReasoning bool           `json:"supports_reasoning"`
    MaxContextTokens  int            `json:"max_context_tokens,omitempty"`
    ProviderSpecific  map[string]any `json:"provider_specific,omitempty"`
}

func (c *Client) GetCapabilities(ctx context.Context, opts *RequestOptions) ([]ModelCapabilities, error) {
    // GET /v1/capabilities
}
```

## Credits (Optional in v1)

If you want to support credits endpoints:

```go
type CreditsBalance struct {
    CreditsRemaining int      `json:"credits_remaining"`
    Tier             string   `json:"tier"`
    Bands            []string `json:"bands"`
    ResetDate        *string  `json:"reset_date,omitempty"`
}

func (c *Client) GetCreditsBalance(ctx context.Context, opts *RequestOptions) (*CreditsBalance, error) {
    // GET /v1/credits/balance
}
```

Similar types and methods can be added for history and stats.

## Errors

Define a structured error type:

```go
type APIError struct {
    StatusCode int
    Message    string
    RequestID  string
    // Optional: Type, Code, etc.
}

func (e *APIError) Error() string {
    if e.RequestID != "" {
        return fmt.Sprintf("zaguan API error (%d) [%s]: %s", e.StatusCode, e.RequestID, e.Message)
    }
    return fmt.Sprintf("zaguan API error (%d): %s", e.StatusCode, e.Message)
}
```

On non-2xx responses, decode the body into a temporary struct, extract message and request ID header, and return `*APIError`.

## Testing Notes

- Use `httptest.Server` to simulate Zaguan CoreX responses where possible.
- For integration tests, run a local CoreX instance and:
  - Test non-streaming and streaming chat.
  - Test multiple providers/configured models.
  - Test reasoning tokens exposure in `Usage` where supported.

These notes should give you a concrete, idiomatic Go starting point that aligns with the generic SDK design docs.
