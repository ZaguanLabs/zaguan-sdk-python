# Zaguan SDK Complete Examples

This document provides comprehensive, production-ready code examples for all three official Zaguan SDKs.

## Quick Links

- [Go Examples](#go-examples)
- [Python Examples](#python-examples)
- [TypeScript Examples](#typescript-examples)
- [Common Patterns](#common-patterns)

---

## Go Examples

### Basic Chat

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/zaguanai/zaguansdk-go"
)

func main() {
    client := zaguansdk.NewClient(zaguansdk.Config{
        BaseURL: "https://api.zaguan.example.com",
        APIKey:  "your-api-key",
        Timeout: 30 * time.Second,
    })

    ctx := context.Background()

    resp, err := client.Chat(ctx, zaguansdk.ChatRequest{
        Model: "openai/gpt-4o-mini",
        Messages: []zaguansdk.Message{
            {
                Role:    zaguansdk.RoleUser,
                Content: zaguansdk.NewStringContent("Hello!"),
            },
        },
    }, nil)

    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(resp.Choices[0].Message.Content)
}
```

### Streaming

```go
stream, err := client.ChatStream(ctx, zaguansdk.ChatRequest{
    Model: "openai/gpt-4o-mini",
    Messages: []zaguansdk.Message{
        {Role: zaguansdk.RoleUser, Content: zaguansdk.NewStringContent("Tell me a story")},
    },
}, nil)

if err != nil {
    log.Fatal(err)
}

for chunk := range stream.Ch {
    if len(chunk.Choices) > 0 {
        fmt.Print(chunk.Choices[0].Delta.Content)
    }
}
```

### Vision

```go
resp, err := client.Chat(ctx, zaguansdk.ChatRequest{
    Model: "openai/gpt-4o",
    Messages: []zaguansdk.Message{
        {
            Role: zaguansdk.RoleUser,
            Content: zaguansdk.NewArrayContent([]zaguansdk.ContentPart{
                {Type: "text", Text: "What's in this image?"},
                {Type: "image_url", ImageURL: &zaguansdk.ImageURL{
                    URL: "https://example.com/image.jpg", Detail: "high"}},
            }),
        },
    },
}, nil)
```

### Function Calling

```go
tools := []zaguansdk.Tool{
    {
        Type: "function",
        Function: zaguansdk.Function{
            Name: "get_weather",
            Description: "Get weather for a location",
            Parameters: map[string]interface{}{
                "type": "object",
                "properties": map[string]interface{}{
                    "location": map[string]interface{}{"type": "string"},
                },
                "required": []string{"location"},
            },
        },
    },
}

resp, err := client.Chat(ctx, zaguansdk.ChatRequest{
    Model: "openai/gpt-4o-mini",
    Messages: []zaguansdk.Message{
        {Role: zaguansdk.RoleUser, Content: zaguansdk.NewStringContent("Weather in Paris?")},
    },
    Tools: tools,
    ToolChoice: "auto",
}, nil)
```

### Provider-Specific (Gemini Reasoning)

```go
resp, err := client.Chat(ctx, zaguansdk.ChatRequest{
    Model: "google/gemini-2.5-pro",
    Messages: []zaguansdk.Message{
        {Role: zaguansdk.RoleUser, Content: zaguansdk.NewStringContent("Complex problem...")},
    },
    ProviderOptions: map[string]interface{}{
        "reasoning_effort": "high",
        "thinking_budget": 10000,
    },
}, nil)

if resp.Usage.CompletionTokensDetails != nil {
    fmt.Printf("Reasoning tokens: %d\n", resp.Usage.CompletionTokensDetails.ReasoningTokens)
}
```

### Credits

```go
balance, err := client.GetCreditsBalance(ctx, nil)
fmt.Printf("Credits: %d, Tier: %s\n", balance.CreditsRemaining, balance.Tier)

history, err := client.GetCreditsHistory(ctx, &zaguansdk.CreditsHistoryOptions{Limit: 10})
for _, entry := range history.Entries {
    fmt.Printf("%s: %s - %d credits\n", entry.Timestamp, entry.Model, entry.CreditsDebited)
}
```

---

## Python Examples

### Basic Chat

```python
from zaguan import ZaguanClient

client = ZaguanClient(
    base_url="https://api.zaguan.example.com",
    api_key="your-api-key"
)

response = client.chat(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### Async Client

```python
import asyncio
from zaguan import AsyncZaguanClient

async def main():
    client = AsyncZaguanClient(base_url="...", api_key="...")
    response = await client.chat(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

### Streaming

```python
for chunk in client.chat_stream(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story"}]
):
    if chunk.choices:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Vision

```python
response = client.chat(
    model="openai/gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    }]
)
```

### Function Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    }
}]

response = client.chat(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Weather in Paris?"}],
    tools=tools
)
```

### Provider-Specific (Anthropic Thinking)

```python
response = client.chat(
    model="anthropic/claude-3-5-sonnet",
    messages=[{"role": "user", "content": "Complex problem..."}],
    provider_specific_params={
        "thinking": {"type": "enabled", "budget_tokens": 5000}
    }
)
```

### Error Handling

```python
from zaguan.errors import InsufficientCreditsError, APIError

try:
    response = client.chat(...)
except InsufficientCreditsError as e:
    print(f"Need {e.credits_required}, have {e.credits_remaining}")
except APIError as e:
    print(f"Error {e.status_code}: {e.message}")
```

---

## TypeScript Examples

### Basic Chat

```typescript
import { ZaguanClient } from '@zaguan/sdk';

const client = new ZaguanClient({
  baseUrl: 'https://api.zaguan.example.com',
  apiKey: 'your-api-key',
});

const response = await client.chat({
  model: 'openai/gpt-4o-mini',
  messages: [{ role: 'user', content: 'Hello!' }],
});

console.log(response.choices[0].message.content);
```

### Streaming

```typescript
for await (const chunk of client.chatStream({
  model: 'openai/gpt-4o-mini',
  messages: [{ role: 'user', content: 'Tell me a story' }],
})) {
  if (chunk.choices[0]?.delta?.content) {
    process.stdout.write(chunk.choices[0].delta.content);
  }
}
```

### Vision

```typescript
const response = await client.chat({
  model: 'openai/gpt-4o',
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: "What's in this image?" },
        {
          type: 'image_url',
          image_url: { url: 'https://example.com/image.jpg' },
        },
      ],
    },
  ],
});
```

### Provider-Specific (Perplexity Search)

```typescript
const response = await client.chat({
  model: 'perplexity/sonar-reasoning',
  messages: [{ role: 'user', content: 'Latest AI news?' }],
  provider_specific_params: {
    search_domain_filter: ['arxiv.org'],
    return_citations: true,
  },
});
```

### Error Handling

```typescript
import { InsufficientCreditsError, APIError } from '@zaguan/sdk';

try {
  const response = await client.chat({...});
} catch (error) {
  if (error instanceof InsufficientCreditsError) {
    console.error(`Need ${error.creditsRequired}, have ${error.creditsRemaining}`);
  } else if (error instanceof APIError) {
    console.error(`Error ${error.statusCode}: ${error.message}`);
  }
}
```

---

## Common Patterns

### Retry with Exponential Backoff

```python
import time

def chat_with_retry(client, request, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat(**request)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait = e.retry_after or (2 ** attempt)
            time.sleep(wait)
```

### Conversation Management

```typescript
class ConversationManager {
  private messages: Message[] = [];

  async chat(userMessage: string): Promise<string> {
    this.messages.push({ role: 'user', content: userMessage });

    const response = await this.client.chat({
      model: 'openai/gpt-4o-mini',
      messages: this.messages,
    });

    this.messages.push(response.choices[0].message);
    return response.choices[0].message.content as string;
  }
}
```

### Multi-Provider Fallback

```python
async def chat_with_fallback(message, providers):
    for model in providers:
        try:
            return await client.chat(model=model, messages=[{"role": "user", "content": message}])
        except Exception:
            continue
    raise Exception("All providers failed")

result = await chat_with_fallback("Hello", [
    "openai/gpt-4o-mini",
    "google/gemini-2.0-flash",
    "anthropic/claude-3-5-sonnet"
])
```

---

For more examples and detailed documentation, see:

- `SDK_GO_IMPLEMENTATION_NOTES.md`
- `SDK_PYTHON_IMPLEMENTATION_NOTES.md`
- `SDK_TS_IMPLEMENTATION_NOTES.md`
- `SDK_PROVIDER_FEATURES.md`
