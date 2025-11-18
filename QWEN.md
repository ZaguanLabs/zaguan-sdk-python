# Zaguan SDK Python - Development Context

## Project Overview

This is the official Python SDK for **Zaguan CoreX**, an enterprise-grade AI gateway that provides unified access to 15+ AI providers and 500+ models through a single, OpenAI-compatible API. The SDK makes it easy to call Zaguan CoreX without dealing with raw HTTP while exposing all important features of CoreX.

### Key Features

1. **Multi-Provider Abstraction**: Access OpenAI, Anthropic, Google, Alibaba, DeepSeek, Groq, Perplexity, xAI, Mistral, Cohere, and more through one API
2. **Cost Optimization**: 40-60% cost reduction through smart routing and provider arbitrage
3. **Advanced Features**: Reasoning control, multimodal AI, real-time data, long context windows
4. **Enterprise Performance**: 2-3x faster responses, 5,000+ concurrent connections
5. **Zero Vendor Lock-in**: Switch providers by changing model name only

## Project Structure

This is a Python SDK project with the following structure:

```
zaguan-sdk-python/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── pytest.ini
├── .gitignore
├── docs/
│   ├── SDK/
│   │   ├── SDK_CORE_TYPES.md
│   │   ├── SDK_DESIGN_OVERVIEW.md
│   │   ├── SDK_EXAMPLES.md
│   │   ├── SDK_FEATURE_CHECKLIST.md
│   │   ├── SDK_GO_IMPLEMENTATION_NOTES.md
│   │   ├── SDK_HTTP_CONTRACT.md
│   │   ├── SDK_PROVIDER_FEATURES.md
│   │   ├── SDK_PYTHON_IMPLEMENTATION_NOTES.md
│   │   ├── SDK_TESTING_AND_VERSIONING.md
│   │   └── SDK_TS_IMPLEMENTATION_NOTES.md
│   └── missing.md
└── zaguan/ package
    ├── __init__.py
    ├── client.py         # Synchronous client
    ├── async_client.py   # Asynchronous client
    ├── models.py         # Pydantic models
    ├── errors.py         # Error hierarchy
    └── _http.py          # HTTP utilities
```

The Python SDK has been fully implemented and provides a complete interface to Zaguan CoreX.

## Implementation Status

The Python SDK has been fully implemented with the following components:

### ✅ Completed Components

1. **Client Classes**:
   - `ZaguanClient` for synchronous operations
   - `AsyncZaguanClient` for asynchronous operations

2. **Configuration**:
   - Base URL configuration
   - API key (Bearer token authentication)
   - Timeout configuration
   - Custom HTTP client injection

3. **Core Models**:
   - Pydantic models for all requests/responses
   - ChatRequest, ChatResponse, Message, Usage, etc.
   - Full support for OpenAI-compatible parameters
   - Tool calling support
   - Multimodal content support

4. **Error Handling**:
   - Complete exception hierarchy
   - API error parsing with status codes and messages
   - Specific error types for common scenarios

5. **Required Endpoints**:
   - `POST /v1/chat/completions` - Primary chat endpoint (OpenAI-compatible)
   - `GET /v1/models` - Lists available models
   - `GET /v1/capabilities` - Returns detailed capability information

6. **Recommended Endpoints**:
   - `GET /v1/credits/balance` - Current balance, tier, bands
   - `GET /v1/credits/history` - Historical usage with pagination
   - `GET /v1/credits/stats` - Aggregated statistics

7. **Additional Features**:
   - Streaming support for both sync and async clients
   - Request ID handling with auto-generation
   - Context manager support for proper resource cleanup
   - Full type safety with Pydantic v2
   - Comprehensive documentation and examples

### 📦 Packaging and Distribution

- Proper `pyproject.toml` configuration
- Requirements specification
- Wheel packaging support
- Ready for PyPI distribution

### 🧪 Testing

- Unit tests with mocking (respx)
- Tests for both sync and async clients
- Package import verification
- All tests passing

For details on what's missing or could be enhanced, see [docs/missing.md](docs/missing.md).


## Key Documentation References

1. **SDK_DESIGN_OVERVIEW.md** - Overall architecture and design principles
2. **SDK_PYTHON_IMPLEMENTATION_NOTES.md** - Python-specific implementation guidance
3. **SDK_CORE_TYPES.md** - Logical types and concepts
4. **SDK_HTTP_CONTRACT.md** - Wire-level API contract
5. **SDK_EXAMPLES.md** - Complete usage examples
6. **SDK_TESTING_AND_VERSIONING.md** - Testing strategy and versioning guidelines
7. **missing.md** - Details on what's missing or could be enhanced

## Target Users

The SDK is primarily for:

- Application developers wanting a single API for many providers
- Platform/infrastructure teams integrating credits, tiers, and bands
- Tooling authors needing OpenAI compatibility with Zaguan features
- Enterprise teams requiring multi-provider AI infrastructure
- SaaS platforms building AI-powered products
- Research teams experimenting with multiple models

## Relationship to OpenAI SDK

While Zaguan CoreX exposes an OpenAI-compatible API (allowing existing OpenAI SDKs to work), the Zaguan SDK provides:

- First-class access to Zaguan-specific features
- Handling of CoreX's credits and accounting endpoints
- A stable, documented contract for multi-provider usage
- Preferred integration path over raw OpenAI SDK usage

## Qwen Added Memories
- Zaguan contact email: support@zaguanai.com and website: https://zaguanai.com/
- Zaguan documentation URL: https://zaguanai.com/docs
