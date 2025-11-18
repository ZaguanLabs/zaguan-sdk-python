import pytest
import respx
import httpx
from zaguan_sdk import ZaguanClient, AsyncZaguanClient
from zaguan_sdk.errors import ZaguanError, APIError, InsufficientCreditsError, RateLimitError


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""

    @respx.mock
    def test_api_error_400(self):
        """Test API error with 400 status code."""
        error_response = {
            "error": {
                "message": "Invalid request parameters",
                "type": "invalid_request_error",
                "code": "invalid_parameters"
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(400, json=error_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(APIError) as exc_info:
            client.chat(request)
        
        assert exc_info.value.status_code == 400
        assert "Invalid request parameters" in str(exc_info.value)

    @respx.mock
    def test_insufficient_credits_error(self):
        """Test insufficient credits error."""
        error_response = {
            "error": {
                "message": "Insufficient credits for this request",
                "type": "insufficient_credits",
                "credits_required": 100,
                "credits_remaining": 50
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(402, json=error_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(InsufficientCreditsError) as exc_info:
            client.chat(request)
        
        assert exc_info.value.credits_required == 100
        assert exc_info.value.credits_remaining == 50
        assert "Insufficient credits" in str(exc_info.value)

    @respx.mock
    def test_rate_limit_error(self):
        """Test rate limit error."""
        error_response = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_exceeded",
                "retry_after": 60
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(429, json=error_response, headers={"Retry-After": "60"})
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(RateLimitError) as exc_info:
            client.chat(request)
        
        assert exc_info.value.retry_after == 60
        assert "Rate limit exceeded" in str(exc_info.value)

    @respx.mock
    def test_server_error_500(self):
        """Test server error 500."""
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(500, json={"error": {"message": "Internal server error"}})
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(APIError) as exc_info:
            client.chat(request)
        
        assert exc_info.value.status_code == 500

    @respx.mock
    def test_authentication_error_401(self):
        """Test authentication error 401."""
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(401, json={"error": {"message": "Unauthorized"}})
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="invalid-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(APIError) as exc_info:
            client.chat(request)
        
        assert exc_info.value.status_code == 401

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_api_error_400(self):
        """Test async API error with 400 status code."""
        error_response = {
            "error": {
                "message": "Invalid request parameters",
                "type": "invalid_request_error"
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(400, json=error_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(APIError) as exc_info:
            await client.chat(request)
        
        assert exc_info.value.status_code == 400

    @respx.mock
    @pytest.mark.asyncio
    async def test_async_insufficient_credits_error(self):
        """Test async insufficient credits error."""
        error_response = {
            "error": {
                "message": "Insufficient credits for this request",
                "type": "insufficient_credits",
                "credits_required": 100,
                "credits_remaining": 50
            }
        }
        
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(402, json=error_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(InsufficientCreditsError) as exc_info:
            await client.chat(request)
        
        assert exc_info.value.credits_required == 100
        assert exc_info.value.credits_remaining == 50

    def test_error_inheritance(self):
        """Test error class inheritance."""
        # Test that all custom errors inherit from ZaguanError
        assert issubclass(APIError, ZaguanError)
        assert issubclass(InsufficientCreditsError, ZaguanError)
        assert issubclass(RateLimitError, ZaguanError)

    @respx.mock
    def test_request_id_in_error(self):
        """Test that request ID is included in error responses."""
        error_response = {
            "error": {
                "message": "Bad request",
                "type": "invalid_request_error"
            }
        }
        
        mock = respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(
                400, 
                json=error_response,
                headers={"X-Request-Id": "test-request-id-123"}
            )
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(APIError) as exc_info:
            client.chat(request)
        
        assert exc_info.value.request_id == "test-request-id-123"

    @respx.mock
    def test_malformed_json_error(self):
        """Test handling of malformed JSON in error response."""
        respx.post("https://api.example.com/v1/chat/completions").mock(
            return_value=httpx.Response(500, text="Internal server error")
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        
        from zaguan_sdk import ChatRequest, Message
        request = ChatRequest(
            model="openai/gpt-4o",
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(APIError) as exc_info:
            client.chat(request)
        
        # Should still raise APIError with generic message
        assert isinstance(exc_info.value, APIError)
        assert exc_info.value.status_code == 500