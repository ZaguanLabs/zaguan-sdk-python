# Zaguan SDK v0.1.0 - Initial Release

🎉 **First official release of the Zaguan Python SDK!**

The Zaguan SDK provides a complete, OpenAI-compatible Python client for Zaguan CoreX - an enterprise-grade AI gateway with unified access to 15+ AI providers and 500+ models.

## 🚀 Features

### Core Functionality
- ✅ **Chat Completions** - Streaming and non-streaming support
- ✅ **Models & Capabilities** - List available models and their features
- ✅ **Credits Management** - Balance, history, and statistics tracking
- ✅ **Health Checks** - Monitor API availability

### Extended Endpoints (100% Coverage)
- ✅ **Embeddings** - Create vector embeddings for semantic search and RAG
- ✅ **Audio Transcription** - Convert speech to text with Whisper
- ✅ **Audio Translation** - Translate audio to English
- ✅ **Text-to-Speech** - Generate speech with 6 different voices
- ✅ **Image Generation** - Create images with DALL-E 2 and DALL-E 3
- ✅ **Image Editing** - Edit images with prompts and masks
- ✅ **Image Variations** - Generate variations of existing images
- ✅ **Content Moderation** - Check content for policy violations

### Developer Experience
- ✅ **Sync & Async** - Both `ZaguanClient` and `AsyncZaguanClient`
- ✅ **Type Safety** - Full type hints with Pydantic models
- ✅ **Error Handling** - Comprehensive exception types
- ✅ **Streaming Support** - Real-time response streaming
- ✅ **Request ID Tracking** - Built-in request tracing
- ✅ **OpenAI Compatible** - Drop-in replacement for OpenAI SDK

## 📦 Installation

```bash
pip install zaguan-sdk
```

## 🔧 Quick Start

```python
from zaguan_sdk import ZaguanClient, ChatRequest, Message

# Initialize client
client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="your-api-key"
)

# Create chat completion
request = ChatRequest(
    model="openai/gpt-4o-mini",
    messages=[Message(role="user", content="Hello!")]
)

response = client.chat(request)
print(response.choices[0].message.content)
```

## 📚 Documentation

- **Homepage**: https://zaguanai.com
- **Documentation**: https://zaguanai.com/docs
- **Repository**: https://github.com/ZaguanLabs/zaguan-sdk-python
- **PyPI**: https://pypi.org/project/zaguan-sdk/

## 🧪 Testing

- **56 passing tests** with 100% core functionality coverage
- Supports Python 3.8, 3.9, 3.10, 3.11, 3.12

## 📊 Statistics

- **15 endpoints** fully implemented
- **20+ Pydantic models** for type safety
- **~1,600 lines** of production code
- **100% endpoint coverage** per SDK specification

## 🎯 Use Cases

- **Semantic Search & RAG** - Embeddings for document similarity
- **Audio Processing** - Transcription, translation, text-to-speech
- **Image Generation** - DALL-E for marketing, design, A/B testing
- **Content Safety** - Automated moderation for user-generated content
- **Multi-Provider AI** - Access 15+ providers through one API

## 🔄 Migration from OpenAI SDK

The Zaguan SDK is a complete drop-in replacement:

```python
# Before (OpenAI SDK)
from openai import OpenAI
client = OpenAI(api_key="...")

# After (Zaguan SDK)
from zaguan_sdk import ZaguanClient
client = ZaguanClient(
    base_url="https://api.zaguanai.com",
    api_key="..."
)

# All methods work identically!
```

## 🙏 Acknowledgments

Built with:
- `httpx` - Modern HTTP client
- `pydantic` - Data validation and type safety
- `pytest` - Comprehensive testing

## 📧 Support

- **Email**: support@zaguanai.com
- **Issues**: https://github.com/ZaguanLabs/zaguan-sdk-python/issues

---

**Full Changelog**: Initial release with complete endpoint coverage
