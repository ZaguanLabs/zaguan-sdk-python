<div align="center">

# 🚀 Zaguan Python SDK

**The official Python SDK for Zaguan CoreX**

[![PyPI version](https://badge.fury.io/py/zaguan-sdk.svg)](https://pypi.org/project/zaguan-sdk/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/badge/tests-56%20passing-brightgreen.svg)](https://github.com/ZaguanLabs/zaguan-sdk-python)

*One API. 15+ Providers. 500+ Models. Infinite Possibilities.*

[Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [Support](#support)

</div>

---

## 🌟 What is Zaguan?

**Zaguan CoreX** is an enterprise-grade AI gateway that provides unified access to multiple AI providers through a single, OpenAI-compatible API. Think of it as your universal adapter for AI services.

### Why Zaguan?

- 🔌 **One API for Everything** - Switch between OpenAI, Anthropic, Google, and 12+ other providers without changing code
- 💰 **Built-in Credits System** - Track usage, set limits, and manage costs across all providers
- 🎯 **OpenAI Compatible** - Drop-in replacement for OpenAI SDK with zero code changes
- 🚀 **Production Ready** - Enterprise-grade reliability, monitoring, and support
- 🔒 **Secure & Compliant** - SOC 2, GDPR, and HIPAA ready infrastructure

## Installation

```bash
pip install zaguan-sdk
```

## 🚀 Quick Start

### Basic Chat Completion

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

# Initialize the client
client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Simple chat completion
response = client.chat(ChatRequest(
    model="openai/gpt-4o-mini",
    messages=[Message(role="user", content="What is Python?")]
))

print(response.choices[0].message.content)
```

### Streaming Responses

```python
# Stream responses in real-time
for chunk in client.chat_stream(ChatRequest(
    model="openai/gpt-4o-mini",
    messages=[Message(role="user", content="Tell me a story")]
)):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Async Support

```python
import asyncio
from zaguan_sdk import AsyncZaguanClient

async def main():
    async with AsyncZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    ) as client:
        response = await client.chat(ChatRequest(
            model="anthropic/claude-3-5-sonnet",
            messages=[Message(role="user", content="Hello!")]
        ))
        print(response.choices[0].message.content)

asyncio.run(main())
```

### Multi-Provider Usage

```python
# Switch providers without changing code
models = [
    "openai/gpt-4o",
    "anthropic/claude-3-5-sonnet",
    "google/gemini-2.0-flash",
    "deepseek/deepseek-chat"
]

for model in models:
    response = client.chat(ChatRequest(
        model=model,
        messages=[Message(role="user", content="Hi!")]
    ))
    print(f"{model}: {response.choices[0].message.content}")
```

## ✨ Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **🔄 Sync & Async** | Both `ZaguanClient` and `AsyncZaguanClient` for any use case |
| **🔌 OpenAI Compatible** | Drop-in replacement - change 3 lines, keep everything else |
| **🌐 Multi-Provider** | Access OpenAI, Anthropic, Google, DeepSeek, and 12+ more |
| **📡 Streaming** | Real-time response streaming with cancellation support |
| **🛡️ Type Safe** | Full type hints and Pydantic validation for all models |
| **⚡ Production Ready** | Comprehensive error handling, retries, and timeouts |

### 📦 Complete API Coverage

<table>
<tr>
<td width="50%">

**💬 Chat & Completions**
- ✅ Chat completions
- ✅ Streaming responses
- ✅ Function calling
- ✅ Tool use
- ✅ Vision (multimodal)

**🧠 Embeddings & Search**
- ✅ Text embeddings
- ✅ Batch embeddings
- ✅ Semantic search ready

**🎨 Image Generation**
- ✅ DALL-E 2 & 3
- ✅ Image editing
- ✅ Image variations

</td>
<td width="50%">

**🎙️ Audio Processing**
- ✅ Speech-to-text (Whisper)
- ✅ Audio translation
- ✅ Text-to-speech (6 voices)

**🔍 Content Safety**
- ✅ Content moderation
- ✅ Policy compliance
- ✅ Safety scores

**💰 Credits & Usage**
- ✅ Balance tracking
- ✅ Usage history
- ✅ Cost analytics

</td>
</tr>
</table>

**🎯 100% coverage of major OpenAI-compatible endpoints**

## 📚 Examples

### Embeddings for Semantic Search

```python
from zaguan_sdk import EmbeddingRequest

# Create embeddings
response = client.create_embeddings(EmbeddingRequest(
    model="openai/text-embedding-3-small",
    input=["Python is great", "I love coding"]
))

for embedding in response.data:
    print(f"Embedding: {embedding.embedding[:5]}...")  # First 5 dimensions
```

### Audio Transcription

```python
# Transcribe audio file
transcription = client.create_transcription(
    file_path="meeting.mp3",
    model="whisper-1",
    language="en"
)
print(transcription.text)
```

### Image Generation

```python
from zaguan_sdk import ImageGenerationRequest

# Generate image with DALL-E
response = client.create_image(ImageGenerationRequest(
    prompt="A serene mountain landscape at sunset",
    model="dall-e-3",
    size="1024x1024",
    quality="hd"
))
print(response.data[0].url)
```

### Content Moderation

```python
from zaguan_sdk import ModerationRequest

# Check content safety
result = client.create_moderation(ModerationRequest(
    input="Your content here"
))

if result.results[0].flagged:
    print("Content flagged:", result.results[0].categories)
```

**📁 More examples in [`examples/`](examples/) directory**

## 🌐 Supported Providers

Access 15+ AI providers through one unified API:

| Provider | Models | Specialties |
|----------|--------|-------------|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | Chat, embeddings, images, audio |
| **Anthropic** | Claude 3.5 Sonnet, Opus | Long context, analysis |
| **Google** | Gemini 2.0, Gemini Pro | Multimodal, reasoning |
| **DeepSeek** | DeepSeek-V3, Reasoner | Coding, reasoning |
| **Alibaba** | Qwen 2.5 | Multilingual |
| **xAI** | Grok 2 | Real-time data |
| **Perplexity** | Sonar | Search-augmented |
| **Cohere** | Command R+ | Enterprise RAG |
| **Groq** | Llama 3, Mixtral | Ultra-fast inference |
| And more... | | |

**🔗 Full provider list:** [docs/SDK/SDK_PROVIDER_FEATURES.md](docs/SDK/SDK_PROVIDER_FEATURES.md)

## 📖 Documentation

### 📘 Getting Started
- **[Quick Start Guide](docs/SDK/SDK_PYTHON_IMPLEMENTATION_NOTES.md)** - Get up and running in 5 minutes
- **[Complete Examples](examples/)** - Real-world usage examples
- **[API Reference](docs/SDK/SDK_CORE_TYPES.md)** - Full type documentation

### 🏗️ Architecture
- **[SDK Design Overview](docs/SDK/SDK_DESIGN_OVERVIEW.md)** - Architecture and design principles
- **[HTTP Contract](docs/SDK/SDK_HTTP_CONTRACT.md)** - Wire-level API specification
- **[Provider Features](docs/SDK/SDK_PROVIDER_FEATURES.md)** - Provider-specific capabilities

### 🧪 Development
- **[Testing Guide](docs/SDK/SDK_TESTING_AND_VERSIONING.md)** - Testing strategy and best practices
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the SDK

## 🚀 Migration from OpenAI SDK

Switching from OpenAI SDK? It's just 3 lines:

```python
# Before (OpenAI SDK)
from openai import OpenAI
client = OpenAI(api_key="sk-...")

# After (Zaguan SDK)
from zaguan_sdk import ZaguanClient
client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-zaguan-key"
)

# Everything else stays exactly the same! 🎉
response = client.chat.completions.create(...)
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/ZaguanLabs/zaguan-sdk-python.git
cd zaguan-sdk-python

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=zaguan_sdk --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### Building and Publishing

```bash
# Build package
make build

# Run tests
make test

# Publish to PyPI (maintainers only)
make publish
```

## 🤝 Support

### Getting Help

- 📧 **Email**: [support@zaguanai.com](mailto:support@zaguanai.com)
- 🌐 **Website**: [https://zaguanai.com](https://zaguanai.com)
- 📚 **Documentation**: [https://zaguanai.com/docs](https://zaguanai.com/docs)
- 🐛 **Issues**: [GitHub Issues](https://github.com/ZaguanLabs/zaguan-sdk-python/issues)

### Community

- 💬 Join our [Discord community](https://discord.gg/zaguan) (coming soon)
- 🐦 Follow us on [Twitter](https://twitter.com/zaguanai) (coming soon)
- 📝 Read our [Blog](https://zaguanai.com/blog) (coming soon)

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ using:
- [httpx](https://www.python-httpx.org/) - Modern HTTP client
- [pydantic](https://docs.pydantic.dev/) - Data validation and type safety
- [pytest](https://pytest.org/) - Testing framework

---

<div align="center">

**[⬆ Back to Top](#-zaguan-python-sdk)**

Made with ❤️ by [Zaguan Labs](https://zaguanai.com)

</div>
