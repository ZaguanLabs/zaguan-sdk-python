# zaguan-sdk-python
Official Zaguán SDK for Python

## Overview

The official Python SDK for Zaguán CoreX - an enterprise-grade AI gateway that provides unified access to 15+ AI providers and 500+ models through a single, OpenAI-compatible API.

## Installation

```bash
pip install zaguan
```

## Quick Start

### Synchronous Usage

```python
from zaguan import ZaguanClient, ChatRequest, Message

# Initialize client
client = ZaguanClient(
    base_url="https://api.your-zaguan-host.com",
    api_key="your-api-key"
)

# Create chat request
request = ChatRequest(
    model="openai/gpt-4o-mini",
    messages=[
        Message(role="user", content="Hello! How are you?")
    ]
)

# Make request
response = client.chat(request)

# Print response
print(response.choices[0].message.content)
```

### Asynchronous Usage

```python
import asyncio
from zaguan import AsyncZaguanClient, ChatRequest, Message

async def main():
    # Initialize client
    client = AsyncZaguanClient(
        base_url="https://api.your-zaguan-host.com",
        api_key="your-api-key"
    )

    # Create chat request
    request = ChatRequest(
        model="openai/gpt-4o-mini",
        messages=[
            Message(role="user", content="Hello! How are you?")
        ]
    )

    # Make request
    response = await client.chat(request)

    # Print response
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Features

- **Synchronous and Asynchronous Clients**: Support for both sync and async usage patterns
- **OpenAI Compatibility**: Drop-in replacement for OpenAI SDK with additional features
- **Multi-Provider Support**: Access to 15+ AI providers through a single API
- **Streaming Support**: Real-time response streaming with cancellation support
- **Error Handling**: Comprehensive error handling with specific exception types
- **Type Safety**: Full type hints and Pydantic models for all API objects
- **Credits Management**: Access to credits balance, history, and statistics

## Documentation

For detailed documentation, see the files in the [docs/SDK](docs/SDK) directory:

- [SDK Design Overview](docs/SDK/SDK_DESIGN_OVERVIEW.md)
- [Python Implementation Notes](docs/SDK/SDK_PYTHON_IMPLEMENTATION_NOTES.md)
- [Complete Examples](docs/SDK/SDK_EXAMPLES.md)
- [Core Types](docs/SDK/SDK_CORE_TYPES.md)
- [HTTP Contract](docs/SDK/SDK_HTTP_CONTRACT.md)
- [Testing and Versioning](docs/SDK/SDK_TESTING_AND_VERSIONING.md)

## Development

### Installation

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
python -m pytest tests/ -v
```

## License

MIT License
