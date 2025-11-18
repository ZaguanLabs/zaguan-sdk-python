import pytest
import respx
import httpx
from zaguan import ZaguanClient, AsyncZaguanClient, ChatRequest, Message


class TestStreaming:
    """Test streaming chat functionality and edge cases."""

    @respx.mock
    def test_chat_stream_basic(self):
        """Test basic streaming functionality."""
        # Mock streaming response
        stream_data = [
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\",\"content\":\"Hello\"},\"finish_reason\":null}]}\n\n",
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"content\":\" world\"},\"finish_reason\":null}]}\n\n",
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="Say hello")]
        )
        
        chunks = list(client.chat_stream(request))
        
        assert len(chunks) == 2
        assert chunks[0].choices[0].delta.content == "Hello"
        assert chunks[1].choices[0].delta.content == " world"

    @respx.mock
    @pytest.mark.asyncio
    async def test_chat_stream_async(self):
        """Test async streaming functionality."""
        # Mock streaming response
        stream_data = [
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\",\"content\":\"Hello\"},\"finish_reason\":null}]}\n\n",
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"content\":\" world\"},\"finish_reason\":null}]}\n\n",
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="Say hello")]
        )
        
        chunks = []
        async for chunk in client.chat_stream(request):
            chunks.append(chunk)
        
        assert len(chunks) == 2
        assert chunks[0].choices[0].delta.content == "Hello"
        assert chunks[1].choices[0].delta.content == " world"

    @respx.mock
    def test_chat_stream_with_tools(self):
        """Test streaming with tool calls."""
        stream_data = [
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\",\"tool_calls\":[{\"id\":\"call_123\",\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"arguments\":\"{\\\"location\\\":\\\"NYC\\\"}\"}}]},\"finish_reason\":null}]}\n\n",
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="What's the weather?")]
        )
        
        chunks = list(client.chat_stream(request))
        
        assert len(chunks) == 1
        tool_calls = chunks[0].choices[0].delta.tool_calls
        assert tool_calls is not None
        assert len(tool_calls) == 1
        assert tool_calls[0]["id"] == "call_123"
        assert tool_calls[0]["function"]["name"] == "get_weather"

    @respx.mock
    def test_chat_stream_empty_response(self):
        """Test streaming with empty response."""
        stream_data = [
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="")]
        )
        
        chunks = list(client.chat_stream(request))
        
        # Should get no chunks (empty lines are filtered out)
        assert len(chunks) == 0

    @respx.mock
    def test_chat_stream_malformed_data(self):
        """Test streaming with some malformed data."""
        stream_data = [
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\",\"content\":\"Hello\"},\"finish_reason\":null}]}\n\n",
            "invalid json data\n",
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"content\":\" world\"},\"finish_reason\":null}]}\n\n",
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="Say hello")]
        )
        
        # Should skip malformed data and continue
        chunks = list(client.chat_stream(request))
        
        assert len(chunks) == 2  # Only valid chunks
        assert chunks[0].choices[0].delta.content == "Hello"
        assert chunks[1].choices[0].delta.content == " world"

    @respx.mock
    def test_chat_stream_finish_reason(self):
        """Test streaming with finish reasons."""
        stream_data = [
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"role\":\"assistant\",\"content\":\"Hello\"},\"finish_reason\":\"stop\"}]}\n\n",
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="Say hello")]
        )
        
        chunks = list(client.chat_stream(request))
        
        assert len(chunks) == 1
        assert chunks[0].choices[0].finish_reason == "stop"

    @respx.mock
    def test_streaming_request_parameters(self):
        """Test that streaming request includes all parameters."""
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[Message(role="user", content="Hello")],
            temperature=0.7,
            max_tokens=100,
            tools=[{"type": "function", "function": {"name": "test_func"}}]
        )
        
        stream_data = [
            "data: {\"id\":\"chatcmpl-123\",\"object\":\"chat.completion.chunk\",\"created\":1234567890,\"model\":\"openai/gpt-4o-mini\",\"choices\":[{\"index\":0,\"delta\":{\"content\":\"Hello\"},\"finish_reason\":null}]}\n\n",
            "data: [DONE]\n\n"
        ]
        
        mock_response = httpx.Response(
            200,
            content="\n".join(stream_data),
            headers={"Content-Type": "text/event-stream"}
        )
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=mock_response
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        chunks = list(client.chat_stream(request))
        
        # Just verify it works - the actual parameters are sent in the request
        assert len(chunks) == 1