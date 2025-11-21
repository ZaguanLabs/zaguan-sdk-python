# Provider-Specific Examples

This guide shows how to use provider-specific features with the Zaguan Python SDK.

## Table of Contents

- [Google Gemini](#google-gemini)
- [Anthropic Claude](#anthropic-claude)
- [DeepSeek](#deepseek)
- [Perplexity](#perplexity)
- [Alibaba Qwen](#alibaba-qwen)
- [xAI Grok](#xai-grok)
- [OpenAI](#openai)

## Google Gemini

### Reasoning Control

Google Gemini supports advanced reasoning with configurable effort levels:

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Use Gemini with high reasoning effort
request = ChatRequest(
    model="google/gemini-2.5-pro",
    messages=[
        Message(role="user", content="Solve this complex math problem: ...")
    ],
    provider_specific_params={
        "reasoning_effort": "high",  # Options: "none", "low", "medium", "high"
        "thinking_budget": 10000,    # Max thinking tokens
        "include_thinking": True      # Include thinking in response
    }
)

response = client.chat(request)
print(response.choices[0].message.content)

# Check reasoning token usage
if response.usage.completion_tokens_details:
    reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
    print(f"Reasoning tokens used: {reasoning_tokens}")
```

## Anthropic Claude

### Extended Thinking (Native Messages API)

For Anthropic-specific features like extended thinking, use the native Messages API:

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

# Use extended thinking
request = AnthropicMessagesRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[
        AnthropicMessage(
            role="user",
            content="Explain quantum entanglement in detail"
        )
    ],
    max_tokens=2048,
    thinking=AnthropicThinkingConfig(
        type="enabled",
        budget_tokens=5000  # 1000-10000 tokens for internal reasoning
    )
)

response = client.messages(request)

# Process response with thinking blocks
for block in response.content:
    if block.type == "thinking":
        print(f"🧠 Thinking: {block.thinking}")
        if block.signature:
            print(f"   Signature: {block.signature}")
    elif block.type == "text":
        print(f"💬 Response: {block.text}")
```

### Streaming with Extended Thinking

```python
request = AnthropicMessagesRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[AnthropicMessage(role="user", content="Tell me a story")],
    max_tokens=1024,
    thinking=AnthropicThinkingConfig(type="enabled", budget_tokens=3000)
)

for event in client.messages_stream(request):
    if event.type == "content_block_delta":
        if event.delta and event.delta.text:
            print(event.delta.text, end="", flush=True)
        elif event.delta and event.delta.thinking:
            print(f"\n[Thinking: {event.delta.thinking}]", end="", flush=True)
```

### Token Counting

```python
from zaguan_sdk import AnthropicCountTokensRequest, AnthropicMessage

request = AnthropicCountTokensRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[
        AnthropicMessage(role="user", content="Hello, world!")
    ]
)

response = client.count_tokens(request)
print(f"Input tokens: {response.input_tokens}")
```

### Batch Processing

```python
from zaguan_sdk import AnthropicMessagesBatchItem, AnthropicMessagesRequest, AnthropicMessage

# Create batch items
items = [
    AnthropicMessagesBatchItem(
        custom_id=f"request-{i}",
        params=AnthropicMessagesRequest(
            model="anthropic/claude-3-5-sonnet",
            messages=[AnthropicMessage(role="user", content=f"Question {i}")],
            max_tokens=100
        )
    )
    for i in range(10)
]

# Submit batch
batch = client.create_messages_batch(items)
print(f"Batch ID: {batch.id}")

# Check status
status = client.get_messages_batch(batch.id)
print(f"Status: {status.processing_status}")

# Get results when ready
if status.processing_status == "ended":
    for line in client.get_messages_batch_results(batch.id):
        result = json.loads(line)
        print(f"Result for {result['custom_id']}: {result['result']}")
```

## DeepSeek

### Controlling Thinking Output

DeepSeek models include reasoning in `<think>` tags. You can disable this:

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Disable thinking output
request = ChatRequest(
    model="deepseek/deepseek-reasoner",
    messages=[
        Message(role="user", content="What is the capital of France?")
    ],
    thinking=False  # Suppresses <think> tags in response
)

response = client.chat(request)
print(response.choices[0].message.content)
```

## Perplexity

### Real-Time Web Search

Perplexity models can search the web and provide citations:

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Use Perplexity with search options
request = ChatRequest(
    model="perplexity/sonar-reasoning",
    messages=[
        Message(role="user", content="What are the latest developments in AI?")
    ],
    provider_specific_params={
        "search_domain_filter": ["arxiv.org", "openai.com"],  # Limit search domains
        "return_citations": True,
        "return_related_questions": True,
        "search_recency_filter": "month"  # "hour", "day", "week", "month", "year"
    }
)

response = client.chat(request)
print(response.choices[0].message.content)

# Note: Perplexity embeds reasoning in <think> tags within content
# You'll need to parse the content to extract thinking
```

## Alibaba Qwen

### Thinking Control

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Enable thinking for Qwen models
request = ChatRequest(
    model="alibaba/qwen-2.5-72b",
    messages=[
        Message(role="user", content="Solve this logic puzzle: ...")
    ],
    provider_specific_params={
        "enable_thinking": True,
        "thinking_budget": 8000
    }
)

response = client.chat(request)
print(response.choices[0].message.content)

# Check reasoning tokens
if response.usage.completion_tokens_details:
    print(f"Reasoning tokens: {response.usage.completion_tokens_details.reasoning_tokens}")
```

## xAI Grok

### Structured Responses API

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Use Grok with structured output
request = ChatRequest(
    model="xai/grok-2",
    messages=[
        Message(role="user", content="Extract key information from this text: ...")
    ],
    provider_specific_params={
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "extraction",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "key_points": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "summary", "key_points"]
                }
            }
        }
    }
)

response = client.chat(request)
print(response.choices[0].message.content)
```

## OpenAI

### Reasoning Models (o1, o3)

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Use OpenAI o1 with reasoning effort
request = ChatRequest(
    model="openai/o1",
    messages=[
        Message(role="user", content="Solve this complex problem: ...")
    ],
    reasoning_effort="high"  # "minimal", "low", "medium", "high"
)

response = client.chat(request)
print(response.choices[0].message.content)

# Check reasoning tokens
if response.usage.completion_tokens_details:
    reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
    print(f"Reasoning tokens: {reasoning_tokens}")
```

### Audio Output (GPT-4o Audio)

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Generate audio response
request = ChatRequest(
    model="openai/gpt-4o-audio",
    messages=[
        Message(role="user", content="Tell me a short story")
    ],
    modalities=["text", "audio"],
    audio={
        "voice": "alloy",  # "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        "format": "mp3"    # "wav", "mp3", "opus", "aac", "flac", "pcm"
    }
)

response = client.chat(request)
print(response.choices[0].message.content)

# Audio data will be in the response
```

## Advanced Features

### Streaming with Accumulation

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message, StreamAccumulator

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

request = ChatRequest(
    model="openai/gpt-4o",
    messages=[Message(role="user", content="Tell me a story")]
)

# Use StreamAccumulator to reconstruct the full message
accumulator = StreamAccumulator()

for chunk in client.chat_stream(request):
    accumulator.add_chunk(chunk)
    # Print each chunk as it arrives
    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\n--- Full Message ---")
message = accumulator.get_message()
print(message.content)
```

### Retry Logic

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message, RetryConfig, with_retry

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Configure retry behavior
retry_config = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_status_codes=(429, 500, 502, 503, 504)
)

@with_retry(retry_config)
def make_request():
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")]
    )
    return client.chat(request)

response = make_request()
print(response.choices[0].message.content)
```

### Observability

```python
from zaguan_sdk import ZaguanClient, LoggingHook, MetricsCollector, CompositeHook

# Create observability hooks
logging_hook = LoggingHook(verbose=True)
metrics = MetricsCollector()
hook = CompositeHook([logging_hook, metrics])

# Note: Hook integration would be added to client in future version
# For now, you can manually track metrics

# After some requests...
summary = metrics.get_summary()
print(f"Total requests: {summary['total_requests']}")
print(f"Success rate: {summary['success_rate']:.2%}")
print(f"Average latency: {summary['average_latency_ms']:.2f}ms")
print(f"Total tokens: {summary['total_tokens']}")
print(f"Total cost: ${summary['total_cost']:.6f}")
```

## Multi-Provider Comparison

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

prompt = "Explain quantum computing in simple terms"

# Try the same prompt with different providers
models = [
    "openai/gpt-4o",
    "anthropic/claude-3-5-sonnet",
    "google/gemini-2.0-flash",
    "deepseek/deepseek-v3",
    "perplexity/sonar-reasoning"
]

for model in models:
    print(f"\n{'='*60}")
    print(f"Model: {model}")
    print('='*60)
    
    request = ChatRequest(
        model=model,
        messages=[Message(role="user", content=prompt)],
        max_tokens=200
    )
    
    response = client.chat(request)
    print(response.choices[0].message.content)
    print(f"\nTokens: {response.usage.total_tokens}")
```

## Best Practices

1. **Use provider-specific params for advanced features**: The `provider_specific_params` field allows you to access unique capabilities of each provider.

2. **Handle reasoning tokens appropriately**: Different providers report reasoning tokens differently. Always check `completion_tokens_details.reasoning_tokens`.

3. **Use the native Anthropic API for Anthropic-specific features**: The `/v1/messages` endpoint provides better support for extended thinking and other Anthropic features.

4. **Enable retry logic for production**: Use `RetryConfig` to handle transient failures gracefully.

5. **Monitor with observability hooks**: Use `MetricsCollector` and `LoggingHook` to track usage and performance.

6. **Stream for better UX**: Use streaming for long responses to provide immediate feedback to users.

7. **Test with multiple providers**: Zaguan makes it easy to switch providers by just changing the model name, so test which works best for your use case.
