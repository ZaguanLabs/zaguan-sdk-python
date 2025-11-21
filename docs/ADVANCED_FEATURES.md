# Advanced Features Guide

This guide covers advanced features of the Zaguan Python SDK that make it production-ready and feature-complete.

## Table of Contents

- [Anthropic Messages API](#anthropic-messages-api)
- [Streaming Utilities](#streaming-utilities)
- [Retry Logic](#retry-logic)
- [Observability](#observability)
- [Forward Compatibility](#forward-compatibility)
- [Error Handling](#error-handling)

## Anthropic Messages API

The SDK provides full support for Anthropic's native Messages API, including extended thinking (Beta).

### Basic Usage

```python
from zaguan_sdk import (
    ZaguanClient,
    AnthropicMessagesRequest,
    AnthropicMessage,
    AnthropicThinkingConfig
)

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Simple message
request = AnthropicMessagesRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[
        AnthropicMessage(role="user", content="Hello!")
    ],
    max_tokens=1024
)

response = client.messages(request)
print(response.content[0].text)
```

### Extended Thinking

```python
# Enable extended thinking for complex reasoning
request = AnthropicMessagesRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[
        AnthropicMessage(
            role="user",
            content="Solve this complex problem step by step: ..."
        )
    ],
    max_tokens=2048,
    thinking=AnthropicThinkingConfig(
        type="enabled",
        budget_tokens=5000  # 1000-10000 tokens
    )
)

response = client.messages(request)

# Process thinking and text blocks
for block in response.content:
    if block.type == "thinking":
        print(f"Internal reasoning: {block.thinking}")
        print(f"Signature: {block.signature}")
    elif block.type == "text":
        print(f"Final answer: {block.text}")
```

### Streaming

```python
request = AnthropicMessagesRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[AnthropicMessage(role="user", content="Tell me a story")],
    max_tokens=1024
)

for event in client.messages_stream(request):
    if event.type == "content_block_delta":
        if event.delta and event.delta.text:
            print(event.delta.text, end="", flush=True)
    elif event.type == "message_stop":
        print("\n[Stream complete]")
```

### Token Counting

```python
from zaguan_sdk import AnthropicCountTokensRequest

request = AnthropicCountTokensRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[
        AnthropicMessage(role="user", content="Your message here")
    ]
)

response = client.count_tokens(request)
print(f"This request will use {response.input_tokens} input tokens")
```

### Batch Processing

```python
from zaguan_sdk import AnthropicMessagesBatchItem
import json

# Create batch
items = [
    AnthropicMessagesBatchItem(
        custom_id=f"req-{i}",
        params=AnthropicMessagesRequest(
            model="anthropic/claude-3-5-sonnet",
            messages=[AnthropicMessage(role="user", content=f"Question {i}")],
            max_tokens=100
        )
    )
    for i in range(100)
]

batch = client.create_messages_batch(items)
print(f"Batch created: {batch.id}")

# Poll for completion
import time
while True:
    status = client.get_messages_batch(batch.id)
    print(f"Status: {status.processing_status}")
    
    if status.processing_status == "ended":
        break
    
    time.sleep(5)

# Get results
for line in client.get_messages_batch_results(batch.id):
    result = json.loads(line)
    print(f"{result['custom_id']}: {result['result']}")
```

## Streaming Utilities

The SDK provides utilities to work with streaming responses.

### StreamAccumulator

```python
from zaguan_sdk import StreamAccumulator, ChatRequest, Message

request = ChatRequest(
    model="openai/gpt-4o",
    messages=[Message(role="user", content="Write a poem")]
)

accumulator = StreamAccumulator()

for chunk in client.chat_stream(request):
    accumulator.add_chunk(chunk)
    # Print as we go
    if chunk.choices and chunk.choices[0].delta:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\n--- Full Message ---")
message = accumulator.get_message()
print(f"Role: {message.role}")
print(f"Content: {message.content}")
print(f"Finish reason: {accumulator.finish_reason}")
```

### Reconstruct from Chunks

```python
from zaguan_sdk import reconstruct_message_from_stream

# Collect all chunks
chunks = []
for chunk in client.chat_stream(request):
    chunks.append(chunk)

# Reconstruct the full message
message = reconstruct_message_from_stream(chunks)
print(message.content)
```

## Retry Logic

The SDK includes configurable retry logic with exponential backoff.

### Basic Retry

```python
from zaguan_sdk import RetryConfig, with_retry

# Configure retry behavior
retry_config = RetryConfig(
    max_retries=5,              # Maximum retry attempts
    initial_delay=1.0,          # Initial delay in seconds
    max_delay=60.0,             # Maximum delay between retries
    exponential_base=2.0,       # Exponential backoff multiplier
    jitter=True,                # Add random jitter to avoid thundering herd
    retry_on_status_codes=(429, 500, 502, 503, 504)  # Status codes to retry
)

@with_retry(retry_config)
def make_request():
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")]
    )
    return client.chat(request)

# This will automatically retry on transient failures
response = make_request()
```

### Async Retry

```python
from zaguan_sdk import AsyncZaguanClient, async_with_retry, RetryConfig

async_client = AsyncZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

async def make_async_request():
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")]
    )
    return await async_client.chat(request)

# Use async retry
retry_config = RetryConfig(max_retries=3)
response = await async_with_retry(make_async_request, retry_config)
```

### Custom Retry Logic

```python
import time
from zaguan_sdk import RetryConfig

config = RetryConfig(
    max_retries=10,
    initial_delay=0.5,
    max_delay=30.0,
    exponential_base=1.5,
    jitter=True
)

# Calculate delay for each attempt
for attempt in range(config.max_retries):
    delay = config.calculate_delay(attempt)
    print(f"Attempt {attempt + 1}: delay = {delay:.2f}s")
```

## Observability

The SDK provides hooks for logging and metrics collection.

### Logging Hook

```python
from zaguan_sdk import LoggingHook

# Create a logging hook
hook = LoggingHook(verbose=True)

# Manually log events (automatic integration coming in future version)
from zaguan_sdk import RequestEvent, ResponseEvent
import time

# Log request
request_event = RequestEvent(
    request_id="req-123",
    method="POST",
    url="https://api.zaguanai.com/v1/chat/completions",
    model="openai/gpt-4o"
)
hook.on_request_start(request_event)

# ... make request ...

# Log response
response_event = ResponseEvent(
    request_id="req-123",
    status_code=200,
    latency_ms=1250.5,
    model="openai/gpt-4o",
    prompt_tokens=50,
    completion_tokens=100,
    total_tokens=150,
    reasoning_tokens=0,
    cost=0.0015
)
hook.on_request_end(response_event)
```

### Metrics Collector

```python
from zaguan_sdk import MetricsCollector

# Create metrics collector
metrics = MetricsCollector()

# Track requests (manual tracking for now)
# ... after making requests ...

# Get summary
summary = metrics.get_summary()
print(f"Total requests: {summary['total_requests']}")
print(f"Successful: {summary['successful_requests']}")
print(f"Failed: {summary['failed_requests']}")
print(f"Success rate: {summary['success_rate']:.2%}")
print(f"Average latency: {summary['average_latency_ms']:.2f}ms")
print(f"Total tokens: {summary['total_tokens']}")
print(f"Total cost: ${summary['total_cost']:.6f}")
print(f"\nRequests by model:")
for model, count in summary['requests_by_model'].items():
    print(f"  {model}: {count}")
```

### Composite Hook

```python
from zaguan_sdk import CompositeHook, LoggingHook, MetricsCollector

# Combine multiple hooks
logging = LoggingHook(verbose=True)
metrics = MetricsCollector()

composite = CompositeHook([logging, metrics])

# Use composite hook for all events
# ... events will be sent to both hooks ...
```

## Forward Compatibility

The SDK is designed to be forward-compatible with future API changes.

### Extra Fields

All models use `extra="allow"` configuration, which means:

```python
# Unknown fields from the API are preserved, not rejected
response = client.chat(request)

# If the API adds new fields in the future, they won't break your code
# You can access them via the model's __dict__ if needed
```

### Metadata Fields

Core types include metadata fields for extensibility:

```python
# ChatResponse has a metadata field
response = client.chat(request)
if response.metadata:
    print(f"Additional metadata: {response.metadata}")

# CreditsBalance has a metadata field
balance = client.get_credits_balance()
if balance.metadata:
    print(f"Additional balance info: {balance.metadata}")
```

## Error Handling

The SDK provides structured error types for better error handling.

### Error Types

```python
from zaguan_sdk import (
    ZaguanError,
    APIError,
    InsufficientCreditsError,
    RateLimitError,
    BandAccessDeniedError
)

try:
    response = client.chat(request)
except InsufficientCreditsError as e:
    print(f"Out of credits: {e.message}")
    print(f"Credits required: {e.credits_required}")
    print(f"Credits remaining: {e.credits_remaining}")
    print(f"Reset date: {e.reset_date}")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
    print(f"Retry after: {e.retry_after} seconds")
    time.sleep(e.retry_after)
    # Retry the request
except BandAccessDeniedError as e:
    print(f"Band access denied: {e.message}")
    print(f"Required tier: {e.required_tier}")
    print(f"Current tier: {e.current_tier}")
except APIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Request ID: {e.request_id}")
except ZaguanError as e:
    print(f"SDK error: {e}")
```

### Request ID Tracking

```python
import uuid

# Provide your own request ID for tracking
request_id = str(uuid.uuid4())

try:
    response = client.chat(request, request_id=request_id)
except APIError as e:
    print(f"Request {request_id} failed: {e.message}")
    # Use request_id to look up logs on the server
```

## Best Practices

1. **Use retry logic in production**: Configure `RetryConfig` to handle transient failures.

2. **Monitor with observability hooks**: Track metrics and logs to understand usage patterns.

3. **Handle errors gracefully**: Use specific error types to provide better user feedback.

4. **Stream for long responses**: Use streaming to provide immediate feedback to users.

5. **Use request IDs**: Provide request IDs for better debugging and idempotency.

6. **Leverage provider-specific features**: Use `provider_specific_params` to access unique capabilities.

7. **Test forward compatibility**: The SDK is designed to handle new API fields gracefully.

8. **Use Anthropic native API when needed**: For Anthropic-specific features like extended thinking, use the `/v1/messages` endpoint.

9. **Accumulate streaming responses**: Use `StreamAccumulator` to reconstruct full messages from streams.

10. **Monitor token usage**: Always check `usage` fields to track costs and optimize prompts.
