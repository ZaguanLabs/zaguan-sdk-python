# Zaguan SDK Provider-Specific Features

This document provides a comprehensive reference for provider-specific features and parameters available through Zaguan CoreX.

## Overview

Zaguan CoreX supports 15+ AI providers with unique capabilities. While the API is OpenAI-compatible, each provider offers specialized features accessible via the `provider_specific_params` field.

## Provider Feature Matrix

| Provider          | Reasoning  | Vision | Audio  | Function Calling | Streaming | Special Features                      |
| ----------------- | ---------- | ------ | ------ | ---------------- | --------- | ------------------------------------- |
| **OpenAI**        | ✅ (o1/o3) | ✅     | ✅     | ✅               | ✅        | Flex processing, DALL-E, Whisper      |
| **Google Gemini** | ✅         | ✅     | ✅     | ✅               | ✅        | 2M context, reasoning effort control  |
| **Anthropic**     | ✅         | ✅     | ❌     | ✅               | ✅        | Extended thinking, citations, caching |
| **Alibaba Qwen**  | ✅         | ✅     | ❌     | ✅               | ✅        | Thinking control, multilingual        |
| **DeepSeek**      | ✅         | ❌     | ❌     | ✅               | ✅        | Cost-effective reasoning              |
| **Groq**          | ❌         | ❌     | ❌     | ✅               | ✅        | Ultra-fast inference (500+ tok/s)     |
| **Perplexity**    | ✅         | ❌     | ❌     | ✅               | ✅        | Web search, citations                 |
| **xAI**           | ❌         | ✅     | ❌     | ✅               | ✅        | Real-time data, responses API         |
| **Mistral**       | ❌         | ❌     | ❌     | ✅               | ✅        | Open models                           |
| **Cohere**        | ❌         | ❌     | ❌     | ✅               | ✅        | Rerank, classify, embeddings          |
| **Fireworks**     | ✅         | ✅     | ❌     | ✅               | ✅        | 100+ models                           |
| **Together AI**   | ✅         | ✅     | ❌     | ✅               | ✅        | Open model hosting                    |
| **OpenRouter**    | Varies     | Varies | Varies | Varies           | ✅        | 200+ models aggregation               |
| **Ollama**        | Varies     | Varies | ❌     | Varies           | ✅        | Local hosting                         |

---

## OpenAI

### Models

- **GPT-4o**: Multimodal flagship (text, vision, audio)
- **GPT-4o-mini**: Cost-effective multimodal
- **o1, o3**: Advanced reasoning models
- **o1-mini**: Faster reasoning
- **GPT-4 Turbo**: High-performance text
- **GPT-3.5 Turbo**: Cost-effective text

### Reasoning Control (o1/o3 models)

```json
{
  "model": "openai/o1",
  "messages": [...],
  "reasoning_effort": "high"
}
```

**Options**: `"minimal"`, `"low"`, `"medium"`, `"high"`

### Flex Processing (Cost Optimization)

```json
{
  "model": "openai/gpt-4o-mini",
  "messages": [...],
  "provider_specific_params": {
    "flex": true,
    "flex_priority": "low"
  }
}
```

**Benefits**: Up to 50% cost reduction for non-urgent requests

### Audio Output (GPT-4o Audio)

```json
{
  "model": "openai/gpt-4o-audio-preview",
  "messages": [...],
  "modalities": ["text", "audio"],
  "audio": {
    "voice": "alloy",
    "format": "mp3"
  }
}
```

**Voices**: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
**Formats**: `wav`, `mp3`, `opus`, `aac`, `flac`, `pcm`

### Vision

```json
{
  "model": "openai/gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "What's in this image?" },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/image.jpg",
            "detail": "high"
          }
        }
      ]
    }
  ]
}
```

**Detail levels**: `low`, `high`, `auto`

---

## Google Gemini

### Models

- **Gemini 2.0 Flash**: Fast, multimodal, 2M context
- **Gemini 2.5 Pro**: Advanced reasoning, 2M context
- **Gemini 1.5 Pro**: Production-ready, 2M context
- **Gemini 1.5 Flash**: Cost-effective, 1M context

### Reasoning Effort Control

```json
{
  "model": "google/gemini-2.5-pro",
  "messages": [...],
  "provider_specific_params": {
    "reasoning_effort": "high",
    "thinking_budget": 10000,
    "include_thinking": true
  }
}
```

**Reasoning Effort Options**:

- `"none"`: No reasoning (fastest, cheapest)
- `"low"`: Minimal reasoning (1K-2K tokens)
- `"medium"`: Moderate reasoning (3K-5K tokens)
- `"high"`: Deep reasoning (8K-10K tokens)

**Parameters**:

- `thinking_budget`: Maximum thinking tokens (default: 10000)
- `include_thinking`: Include thinking content in response (default: true)

### Vision

```json
{
  "model": "google/gemini-2.0-flash",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "Analyze this image" },
        {
          "type": "image_url",
          "image_url": { "url": "https://example.com/image.jpg" }
        }
      ]
    }
  ]
}
```

### Long Context (2M tokens)

```json
{
  "model": "google/gemini-2.0-flash",
  "messages": [...],
  "max_tokens": 8192
}
```

**Context windows**: Up to 2,097,152 tokens

---

## Anthropic Claude

### Models

- **Claude 3.5 Sonnet**: Best overall, extended thinking
- **Claude 3 Opus**: Most capable, 200K context
- **Claude 3 Sonnet**: Balanced performance
- **Claude 3 Haiku**: Fast and affordable

### Extended Thinking API

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

**Thinking Types**:

- `"enabled"`: Enable extended thinking with budget
- `"disabled"`: Disable extended thinking

**Budget**: 1-10,000 tokens (default: 5000)

### Prompt Caching

```json
{
  "model": "anthropic/claude-3-5-sonnet",
  "messages": [...],
  "provider_specific_params": {
    "system": [
      {
        "type": "text",
        "text": "Long system prompt...",
        "cache_control": {"type": "ephemeral"}
      }
    ]
  }
}
```

**Benefits**: 90% cost reduction for cached content

### Citations

```json
{
  "model": "anthropic/claude-3-5-sonnet",
  "messages": [...],
  "provider_specific_params": {
    "citations": {
      "type": "char",
      "enabled": true
    }
  }
}
```

**Citation Types**:

- `"char"`: Character-level citations
- `"page"`: Page-level citations (PDFs)
- `"content_block"`: Content block citations

### Vision

```json
{
  "model": "anthropic/claude-3-5-sonnet",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "Describe this image" },
        {
          "type": "image",
          "source": {
            "type": "url",
            "url": "https://example.com/image.jpg"
          }
        }
      ]
    }
  ]
}
```

---

## Alibaba Qwen

### Models

- **Qwen 2.5**: General purpose, multilingual
- **QwQ**: Advanced reasoning model
- **Qwen-VL**: Vision-language model

### Thinking Control

```json
{
  "model": "alibaba/qwq-32b-preview",
  "messages": [...],
  "provider_specific_params": {
    "enable_thinking": true,
    "thinking_budget": 8000
  }
}
```

**Parameters**:

- `enable_thinking`: Enable/disable reasoning (default: true)
- `thinking_budget`: Maximum thinking tokens (1-10000)

### Multilingual Support

Qwen models excel at Chinese, Japanese, Korean, and other Asian languages.

```json
{
  "model": "alibaba/qwen-2.5-72b-instruct",
  "messages": [{ "role": "user", "content": "用中文回答：什么是人工智能？" }]
}
```

---

## DeepSeek

### Models

- **DeepSeek V3**: Latest general model
- **DeepSeek R1**: Advanced reasoning
- **DeepSeek Reasoner**: Cost-effective reasoning

### Thinking Control

```json
{
  "model": "deepseek/deepseek-reasoner",
  "messages": [...],
  "thinking": false
}
```

**Note**: When `thinking: false`, suppresses `<think>` tags in response.

### Cost-Effective Reasoning

DeepSeek models provide strong reasoning at significantly lower cost than competitors.

**Pricing**: ~10x cheaper than GPT-4 for similar reasoning quality

---

## Groq

### Models

- **Llama 3.1 405B**: Largest open model
- **Llama 3.1 70B**: Balanced performance
- **Llama 3.1 8B**: Fast and efficient
- **Mixtral 8x7B**: Mixture of experts

### Ultra-Fast Inference

```json
{
  "model": "groq/llama-3.1-70b-versatile",
  "messages": [...],
  "stream": true
}
```

**Performance**: 500+ tokens/second streaming

### Use Cases

- Real-time chat applications
- Low-latency requirements
- High-throughput workloads

---

## Perplexity

### Models

- **Sonar**: General web search
- **Sonar Reasoning**: Search with reasoning
- **Sonar Pro**: Enhanced search capabilities

### Web Search

```json
{
  "model": "perplexity/sonar-reasoning",
  "messages": [...],
  "provider_specific_params": {
    "search_domain_filter": ["wikipedia.org", "arxiv.org"],
    "return_citations": true,
    "return_images": false,
    "return_related_questions": true,
    "search_recency_filter": "month"
  }
}
```

**Parameters**:

- `search_domain_filter`: Limit search to specific domains
- `return_citations`: Include source citations
- `return_images`: Include image results
- `return_related_questions`: Suggest follow-up questions
- `search_recency_filter`: `day`, `week`, `month`, `year`

### Citations

Perplexity automatically includes citations in responses:

```json
{
  "choices": [
    {
      "message": {
        "content": "According to recent studies[1], AI...",
        "citations": [
          {
            "url": "https://example.com/study",
            "title": "AI Study 2024"
          }
        ]
      }
    }
  ]
}
```

---

## xAI Grok

### Models

- **Grok 2**: Latest general model
- **Grok 2 Vision**: Multimodal capabilities
- **Grok Beta**: Experimental features

### Responses API (Structured Outputs)

```json
{
  "model": "xai/grok-2",
  "messages": [...],
  "provider_specific_params": {
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "name": "user_info",
        "schema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
          },
          "required": ["name", "age"]
        }
      }
    }
  }
}
```

### Real-Time Data

Grok has access to real-time Twitter/X data and current events.

---

## Cohere

### Models

- **Command R+**: Most capable
- **Command R**: Balanced performance
- **Command**: Cost-effective
- **Embed**: Embeddings

### Rerank API (RAG Optimization)

```json
POST /v1/rerank
{
  "model": "rerank-english-v3.0",
  "query": "What is machine learning?",
  "documents": [
    "Machine learning is...",
    "Deep learning is...",
    "AI is..."
  ],
  "top_n": 3
}
```

**Response**:

```json
{
  "results": [
    {
      "index": 0,
      "relevance_score": 0.98,
      "document": "Machine learning is..."
    }
  ]
}
```

### Classify API

```json
POST /v1/classify
{
  "model": "embed-english-v3.0",
  "inputs": ["This is spam", "This is not spam"],
  "examples": [
    {"text": "Buy now!", "label": "spam"},
    {"text": "Hello friend", "label": "not_spam"}
  ]
}
```

### Embeddings

```json
POST /v1/embeddings
{
  "model": "embed-english-v3.0",
  "texts": ["Text to embed"],
  "input_type": "search_document"
}
```

**Input Types**: `search_document`, `search_query`, `classification`, `clustering`

---

## Fireworks

### Models

- **100+ models** including DeepSeek, Llama, Qwen, Mixtral
- Vision models
- Function calling models

### Model Format

```json
{
  "model": "fireworks/accounts/fireworks/models/llama-v3p1-70b-instruct"
}
```

### Features

- Fast inference
- Cost-effective
- Wide model selection

---

## Together AI

### Models

- Various open models
- Custom model hosting

### Features

- Open model access
- Competitive pricing
- Good for experimentation

---

## OpenRouter

### Models

- **200+ models** from multiple providers
- Automatic fallback
- Cost optimization

### Features

- Provider aggregation
- Automatic routing
- Unified billing

---

## Ollama (Local)

### Models

- Any model available in Ollama library
- Custom models
- Local hosting

### Configuration

```yaml
providers:
  ollama:
    enabled: true
    host: 'http://localhost:11434'
```

### Benefits

- Complete privacy
- No API costs
- Offline operation
- Custom models

---

## Provider Selection Guide

### For Reasoning Tasks

1. **OpenAI o1/o3** - Best overall reasoning
2. **Google Gemini 2.5 Pro** - Controllable reasoning effort
3. **Anthropic Claude 3.5 Sonnet** - Extended thinking
4. **DeepSeek R1** - Cost-effective reasoning
5. **Alibaba QwQ** - Multilingual reasoning

### For Vision Tasks

1. **OpenAI GPT-4o** - Best multimodal
2. **Google Gemini 2.0 Flash** - Fast vision + 2M context
3. **Anthropic Claude 3.5 Sonnet** - Document analysis
4. **xAI Grok 2 Vision** - Real-time image analysis

### For Speed

1. **Groq** - 500+ tokens/second
2. **Google Gemini 2.0 Flash** - Fast + capable
3. **OpenAI GPT-4o-mini** - Fast + affordable

### For Cost

1. **DeepSeek** - 10x cheaper than GPT-4
2. **Google Gemini Flash** - Low cost, high capability
3. **OpenAI GPT-4o-mini** - Affordable multimodal
4. **Groq** - Free tier available

### For RAG/Search

1. **Perplexity** - Built-in web search
2. **Cohere** - Rerank API
3. **OpenAI** - Embeddings + GPT-4

### For Long Context

1. **Google Gemini** - 2M tokens
2. **Anthropic Claude** - 200K tokens
3. **OpenAI GPT-4 Turbo** - 128K tokens

---

## Best Practices

### 1. Use Provider-Specific Features Wisely

- Only use provider params when needed
- Document provider dependencies
- Test fallback behavior

### 2. Handle Provider Differences

- Check for reasoning token support
- Parse content for embedded thinking
- Validate response formats

### 3. Cost Optimization

- Use reasoning effort controls
- Enable caching when available
- Choose appropriate models for tasks

### 4. Error Handling

- Handle provider-specific errors
- Implement retry logic
- Log provider responses

### 5. Testing

- Test with multiple providers
- Validate provider-specific features
- Monitor token usage

---

## Migration Between Providers

### From OpenAI to Gemini

```diff
{
- "model": "openai/gpt-4o",
+ "model": "google/gemini-2.0-flash",
  "messages": [...],
+ "provider_specific_params": {
+   "reasoning_effort": "medium"
+ }
}
```

### From Anthropic to OpenAI

```diff
{
- "model": "anthropic/claude-3-5-sonnet",
+ "model": "openai/gpt-4o",
  "messages": [...],
- "provider_specific_params": {
-   "thinking": {"type": "enabled", "budget_tokens": 5000}
- }
+ "reasoning_effort": "high"
}
```

### From DeepSeek to Gemini

```diff
{
- "model": "deepseek/deepseek-reasoner",
+ "model": "google/gemini-2.5-pro",
  "messages": [...],
- "thinking": true
+ "provider_specific_params": {
+   "reasoning_effort": "high"
+ }
}
```

---

## Conclusion

Zaguan CoreX provides unified access to diverse AI providers while preserving their unique capabilities. Use this guide to:

1. Choose the right provider for your use case
2. Access provider-specific features
3. Optimize costs and performance
4. Handle provider differences gracefully

For implementation details, see the language-specific SDK documentation.
