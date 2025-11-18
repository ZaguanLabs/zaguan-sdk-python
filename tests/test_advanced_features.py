import pytest
import respx
import httpx
from zaguan_sdk import ZaguanClient, AsyncZaguanClient, ChatRequest, Message


class TestAdvancedFeatures:
    """Test advanced features and edge cases."""

    @respx.mock
    def test_health_check_sync(self):
        """Test health check endpoint (sync)."""
        mock_response = {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",
            "version": "1.0.0"
        }
        
        respx.get("https://api.example.com/health").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        result = client.health_check()
        
        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"

    @respx.mock
    @pytest.mark.asyncio
    async def test_health_check_async(self):
        """Test health check endpoint (async)."""
        mock_response = {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",
            "version": "1.0.0"
        }
        
        respx.get("https://api.example.com/health").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        result = await client.health_check()
        
        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"

    def test_chat_request_advanced_params(self):
        """Test ChatRequest with advanced OpenAI parameters."""
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")],
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
            n=2,
            presence_penalty=0.1,
            frequency_penalty=0.2,
            logit_bias={"123": 0.5},
            stop=["END"],
            seed=42,
            user="test-user",
            metadata={"key": "value"}
        )
        
        # Test that all parameters are properly set
        assert request.model == "openai/gpt-4o"
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.top_p == 0.9
        assert request.n == 2
        assert request.presence_penalty == 0.1
        assert request.frequency_penalty == 0.2
        assert request.logit_bias == {"123": 0.5}
        assert request.stop == ["END"]
        assert request.seed == 42
        assert request.user == "test-user"
        assert request.metadata == {"key": "value"}

    def test_chat_request_copy_method(self):
        """Test ChatRequest copy method."""
        original = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")],
            temperature=0.7
        )
        
        copied = original.copy()
        
        # Test that it's a different object but with same values
        assert copied is not original
        assert copied.model == original.model
        assert copied.temperature == original.temperature
        assert len(copied.messages) == len(original.messages)
        
        # Test that modifications don't affect the original
        copied.temperature = 0.5
        assert original.temperature == 0.7

    @respx.mock
    def test_helper_methods(self):
        """Test convenience helper methods."""
        mock_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "openai/gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        # Test chat_simple
        response = client.chat_simple("Hello")
        assert response.choices[0].message.content == "Hello! How can I help you today?"
        
        # Test chat_with_system
        response = client.chat_with_system("You are a helpful assistant.", "How are you?")
        assert response.choices[0].message.content == "Hello! How can I help you today?"

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_helper_methods(self):
        """Test async convenience helper methods."""
        mock_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "openai/gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        # Test chat_simple
        response = await client.chat_simple("Hello")
        assert response.choices[0].message.content == "Hello! How can I help you today?"
        
        # Test chat_with_system
        response = await client.chat_with_system("You are a helpful assistant.", "How are you?")
        assert response.choices[0].message.content == "Hello! How can I help you today?"

    def test_chat_request_stop_list(self):
        """Test ChatRequest with list of stop sequences."""
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")],
            stop=["END", "STOP", "DONE"]
        )
        
        assert request.stop == ["END", "STOP", "DONE"]

    def test_message_multimodal_content(self):
        """Test Message with multimodal content."""
        # String content
        msg1 = Message(role="user", content="Hello")
        assert msg1.content == "Hello"
        
        # Array content (multimodal)
        multimodal_content = [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
        msg2 = Message(role="user", content=multimodal_content)
        assert msg2.content == multimodal_content

    def test_message_with_tool_calls(self):
        """Test Message with tool calls."""
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "New York"}'
                }
            }
        ]
        
        msg = Message(
            role="assistant",
            content="I'll check the weather for you.",
            tool_calls=tool_calls
        )
        
        assert msg.tool_calls == tool_calls
        assert msg.content == "I'll check the weather for you."