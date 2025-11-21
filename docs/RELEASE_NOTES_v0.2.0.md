# Release Notes - Zaguan Python SDK v0.2.0

**Release Date:** November 21, 2024

## 🎉 Overview

Version 0.2.0 is a **major feature release** that implements all "should" requirements from the SDK documentation, making this a production-ready, feature-complete SDK with enterprise-grade capabilities.

## 🚀 What's New

### Anthropic Messages API (Native)

Full support for Anthropic's native Messages API with extended thinking:

- **Native API Endpoint** - `/v1/messages` with Anthropic's format
- **Extended Thinking (Beta)** - Configure thinking budgets (1,000-10,000 tokens)
- **Token Counting** - Estimate costs before sending requests
- **Batches API** - Complete batch processing support

```python
from zaguan_sdk import AnthropicMessagesRequest, AnthropicMessage, AnthropicThinkingConfig

response = client.messages(AnthropicMessagesRequest(
    model="anthropic/claude-3-5-sonnet",
    messages=[AnthropicMessage(role="user", content="Explain quantum computing")],
    max_tokens=2048,
    thinking=AnthropicThinkingConfig(type="enabled", budget_tokens=5000)
))
```

### Streaming Utilities

Easily reconstruct complete messages from streaming chunks:

```python
from zaguan_sdk import StreamAccumulator

accumulator = StreamAccumulator()
for chunk in client.chat_stream(request):
    accumulator.add_chunk(chunk)

message = accumulator.get_message()
```

### Retry Logic with Exponential Backoff

Production-ready retry handling:

```python
from zaguan_sdk import RetryConfig, with_retry

@with_retry(RetryConfig(max_retries=5, exponential_base=2.0, jitter=True))
def make_request():
    return client.chat(request)
```

### Observability & Monitoring

Track metrics and logs for production monitoring:

```python
from zaguan_sdk import MetricsCollector, LoggingHook

metrics = MetricsCollector()
# After requests...
summary = metrics.get_summary()
print(f"Success rate: {summary['success_rate']:.2%}")
print(f"Average latency: {summary['average_latency_ms']:.2f}ms")
```

### Forward Compatibility

All models now support unknown fields from future API versions:

- Models use `extra="allow"` configuration
- Metadata fields added to core types
- Future API changes won't break existing code

## 📦 New Features

### New Modules
- `zaguan_sdk/streaming.py` - Streaming utilities
- `zaguan_sdk/retry.py` - Retry logic with exponential backoff
- `zaguan_sdk/observability.py` - Logging and metrics infrastructure

### New Models (12 Anthropic-specific types)
- `AnthropicThinkingConfig`
- `AnthropicContentBlock`
- `AnthropicMessage`
- `AnthropicUsage`
- `AnthropicMessagesRequest`
- `AnthropicMessagesResponse`
- `AnthropicMessagesDelta`
- `AnthropicMessagesStreamEvent`
- `AnthropicCountTokensRequest`
- `AnthropicCountTokensResponse`
- `AnthropicMessagesBatchItem`
- `AnthropicMessagesBatchRequest`
- `AnthropicMessagesBatchResponse`

### New Client Methods
- `messages()` - Anthropic Messages API
- `messages_stream()` - Streaming Anthropic messages
- `count_tokens()` - Token counting
- `create_messages_batch()` - Create batch
- `get_messages_batch()` - Get batch status
- `list_messages_batches()` - List batches
- `cancel_messages_batch()` - Cancel batch
- `get_messages_batch_results()` - Get results

### New Utilities
- `StreamAccumulator` - Accumulate streaming chunks
- `reconstruct_message_from_stream()` - Helper function
- `RetryConfig` - Retry configuration
- `with_retry()` - Sync retry decorator
- `async_with_retry()` - Async retry function
- `LoggingHook` - Logging implementation
- `MetricsCollector` - Metrics tracking
- `CompositeHook` - Combine hooks

## 📚 Documentation

### New Comprehensive Guides
- **`docs/PROVIDER_EXAMPLES.md`** - Provider-specific usage examples
  - Google Gemini reasoning control
  - Anthropic extended thinking
  - DeepSeek thinking control
  - Perplexity search
  - Alibaba Qwen
  - xAI Grok
  - OpenAI reasoning models

- **`docs/ADVANCED_FEATURES.md`** - Advanced features guide
  - Anthropic Messages API
  - Streaming utilities
  - Retry logic
  - Observability
  - Forward compatibility
  - Error handling

- **`IMPLEMENTATION_SUMMARY.md`** - Complete implementation details

## 🎯 SDK Specification Compliance

This release achieves **100% compliance** with all "should" requirements:

- ✅ Anthropic Messages API with extended thinking
- ✅ Streaming utilities for message reconstruction
- ✅ Retry logic with exponential backoff
- ✅ Observability hooks for logging and metrics
- ✅ Forward compatibility with unknown fields
- ✅ Metadata fields for extensibility
- ✅ Comprehensive provider-specific examples

## 🔄 Migration from v0.1.0

**No migration required!** All changes are additive and backward compatible.

Existing code continues to work unchanged:

```python
# v0.1.0 code works perfectly in v0.2.0
response = client.chat(ChatRequest(
    model="openai/gpt-4o-mini",
    messages=[Message(role="user", content="Hello")]
))
```

New features can be adopted incrementally as needed.

## 🔒 Security & Stability

- **No breaking changes**
- **Backward compatible** with v0.1.0
- **All new features are opt-in**
- **No known vulnerabilities**

## 📊 Package Information

- **Version:** 0.2.0
- **Python Support:** 3.8, 3.9, 3.10, 3.11, 3.12+
- **Dependencies:** httpx>=0.23.0, pydantic>=2.0.0
- **License:** Apache-2.0

## 🙏 Acknowledgments

This release implements all documented "should" requirements from the SDK specification, making the Zaguan Python SDK a best-in-class SDK with enterprise-grade features.

## 📦 Installation

```bash
pip install --upgrade zaguan-sdk
```

Or install from source:

```bash
git clone https://github.com/ZaguanLabs/zaguan-sdk-python.git
cd zaguan-sdk-python
pip install .
```

## 🔗 Links

- **Documentation:** https://zaguanai.com/docs
- **Repository:** https://github.com/ZaguanLabs/zaguan-sdk-python
- **PyPI:** https://pypi.org/project/zaguan-sdk/
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Provider Examples:** [docs/PROVIDER_EXAMPLES.md](docs/PROVIDER_EXAMPLES.md)
- **Advanced Features:** [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)

## 💬 Support

- **Email:** support@zaguanai.com
- **Issues:** https://github.com/ZaguanLabs/zaguan-sdk-python/issues
- **Homepage:** https://zaguanai.com

---

**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)
