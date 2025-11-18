# Python SDK Implementation Notes

These notes specialize the generic SDK design for **Python**. They describe a `zaguan` (or similar) package that provides a high-level client over Zaguan CoreX.

Goals:

- Comfortable for users of `openai` / `anthropic` Python clients.
- Support both **sync** and (optionally) **async** usage.
- Provide first-class streaming, usage, and credits support.

## Package Layout

Suggested structure:

```text
zaguan/
  __init__.py
  client.py         # Public Client classes (sync, async)
  models.py         # Pydantic or dataclass models for requests/responses
  errors.py         # Error types
  _http.py          # Internal HTTP helpers (requests/httpx/aiohttp)
```

You can choose `requests` for sync and `httpx` or `aiohttp` for async. `httpx` is a good default because it supports both modes in a unified way.

## Configuration & Clients

### Configuration

A simple config object or constructor arguments:

```python
class Config(BaseModel):
    base_url: str
    api_key: str
    timeout: Optional[float] = None  # seconds
```

### Sync Client

```python
class ZaguanClient:
    def __init__(self, base_url: str, api_key: str, timeout: Optional[float] = None, http_client: Optional["SyncClient"] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = http_client or httpx.Client(timeout=timeout)

    # Close method or context manager support recommended
```

### Async Client (Optional but Recommended)

```python
class AsyncZaguanClient:
    def __init__(self, base_url: str, api_key: str, timeout: Optional[float] = None, http_client: Optional["AsyncClient"] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = http_client or httpx.AsyncClient(timeout=timeout)
```

Both clients should share the same request/response models.

## Core Models (Pydantic or Dataclasses)

Using Pydantic (v1 or v2) is a good choice for type safety and validation, but plain `dataclasses` plus `json` also works.

### ChatRequest

```python
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]

    temperature: Optional[float] = None
    max_tokens: Optional[int] = Field(None, alias="max_tokens")
    top_p: Optional[float] = None
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None

    # Zaguan extensions
    provider_specific_params: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
```

### Usage

```python
class TokenDetails(BaseModel):
    reasoning_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    accepted_prediction_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    prompt_tokens_details: Optional[TokenDetails] = None
    completion_tokens_details: Optional[TokenDetails] = None
```

### ChatResponse

```python
class Choice(BaseModel):
    index: int
    message: Optional[Message] = None
    finish_reason: Optional[str] = None
    # Add tool calls / logprobs as needed


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
```

For streaming, define a `ChatChunk` / `ChoiceDelta` model similar to OpenAI’s streaming chunks.

## Sync Methods

### Non-Streaming Chat

```python
import uuid

class ZaguanClient:
    ...

    def chat(self, request: ChatRequest, request_id: Optional[str] = None) -> ChatResponse:
        rid = request_id or str(uuid.uuid4())
        url = f"{self.base_url}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Request-Id": rid,
        }

        resp = self._client.post(url, headers=headers, json=request.dict(by_alias=True, exclude_none=True))
        return self._handle_response(resp, model=ChatResponse)
```

### Streaming Chat

Using `httpx` with `stream()` or raw `requests` streaming:

```python
from typing import Iterator

    def chat_stream(self, request: ChatRequest, request_id: Optional[str] = None) -> Iterator["ChatChunk"]:
        rid = request_id or str(uuid.uuid4())
        url = f"{self.base_url}/v1/chat/completions"
        req_body = request.copy()
        req_body.stream = True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Request-Id": rid,
        }

        with self._client.stream("POST", url, headers=headers, json=req_body.dict(by_alias=True, exclude_none=True)) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or line.startswith(b"data: [DONE]"):
                    continue
                # Parse SSE-style line: e.g. b"data: { ... }"
                if line.startswith(b"data:"):
                    payload = line[len(b"data:"):].strip()
                    data = json.loads(payload)
                    yield ChatChunk.parse_obj(data)
```

Async version would use `async with client.stream(...)` and `async for line in resp.aiter_lines()`.

## Models & Capabilities

```python
class ModelInfo(BaseModel):
    id: str
    object: str
    owned_by: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ModelCapabilities(BaseModel):
    model_id: str
    supports_vision: bool
    supports_tools: bool
    supports_reasoning: bool
    max_context_tokens: Optional[int] = None
    provider_specific: Optional[Dict[str, Any]] = None
```

Client methods:

```python
    def list_models(self) -> List[ModelInfo]:
        resp = self._client.get(f"{self.base_url}/v1/models", headers=self._headers())
        return [ModelInfo.parse_obj(m) for m in resp.json().get("data", [])]

    def get_capabilities(self) -> List[ModelCapabilities]:
        resp = self._client.get(f"{self.base_url}/v1/capabilities", headers=self._headers())
        return [ModelCapabilities.parse_obj(c) for c in resp.json()]
```

## Credits (Optional)

If exposing credits endpoints:

```python
class CreditsBalance(BaseModel):
    credits_remaining: int
    tier: str
    bands: List[str]
    reset_date: Optional[str] = None


    def get_credits_balance(self) -> CreditsBalance:
        resp = self._client.get(f"{self.base_url}/v1/credits/balance", headers=self._headers())
        return CreditsBalance.parse_obj(resp.json())
```

Similar patterns can be used for history and stats.

## Errors

Define an SDK error hierarchy:

```python
class ZaguanError(Exception):
    pass


class APIError(ZaguanError):
    def __init__(self, status_code: int, message: str, request_id: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
```

In `_handle_response`, parse JSON error bodies and raise `APIError` on non-2xx.

## Testing Notes

- Use `pytest` for unit tests and integration tests.
- Mock HTTP with `respx` or similar when using `httpx`.
- For integration tests, point the client at a local or staging CoreX instance and:
  - Test non-streaming and streaming chat.
  - Test multiple providers.
  - Validate `Usage` data, including reasoning tokens where applicable.

These notes should give you a solid, idiomatic Python SDK design aligned with the generic SDK documentation.
