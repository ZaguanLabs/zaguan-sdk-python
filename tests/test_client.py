import pytest
import respx
import httpx
from zaguan import ZaguanClient, AsyncZaguanClient, ChatRequest, Message


@pytest.fixture
def sample_chat_request():
    return ChatRequest(
        model="openai/gpt-4o-mini",
        messages=[
            Message(role="user", content="Hello, world!")
        ]
    )


@respx.mock
def test_chat_completion(sample_chat_request):
    # Mock the API response
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
    
    # Create client and make request
    client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
    response = client.chat(sample_chat_request)
    
    # Verify response
    assert response.id == "chatcmpl-123"
    assert response.choices[0].message.content == "Hello! How can I help you today?"
    assert response.usage.total_tokens == 30


@respx.mock
@pytest.mark.asyncio
async def test_async_chat_completion(sample_chat_request):
    # Mock the API response
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
    
    # Create client and make request
    client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
    response = await client.chat(sample_chat_request)
    
    # Verify response
    assert response.id == "chatcmpl-123"
    assert response.choices[0].message.content == "Hello! How can I help you today?"
    assert response.usage.total_tokens == 30