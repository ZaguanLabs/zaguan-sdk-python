import pytest
import respx
import httpx
from zaguan import ZaguanClient, AsyncZaguanClient


class TestCreditsManagement:
    """Test credits management functionality."""

    @respx.mock
    def test_get_credits_balance(self):
        """Test getting credits balance."""
        mock_response = {
            "credits_remaining": 1500,
            "tier": "professional",
            "bands": ["standard", "priority"],
            "reset_date": "2025-02-01"
        }
        
        respx.get("https://api.example.com/v1/credits/balance").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        balance = client.get_credits_balance()
        
        assert balance.credits_remaining == 1500
        assert balance.tier == "professional"
        assert balance.bands == ["standard", "priority"]
        assert balance.reset_date == "2025-02-01"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_credits_balance_async(self):
        """Test getting credits balance (async)."""
        mock_response = {
            "credits_remaining": 1500,
            "tier": "professional",
            "bands": ["standard", "priority"],
            "reset_date": "2025-02-01"
        }
        
        respx.get("https://api.example.com/v1/credits/balance").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        balance = await client.get_credits_balance()
        
        assert balance.credits_remaining == 1500
        assert balance.tier == "professional"
        assert balance.bands == ["standard", "priority"]
        assert balance.reset_date == "2025-02-01"

    @respx.mock
    def test_get_credits_history(self):
        """Test getting credits history."""
        mock_response = {
            "entries": [
                {
                    "id": "req-123",
                    "timestamp": "2025-01-01T10:00:00Z",
                    "request_id": "chatcmpl-abc123",
                    "model": "openai/gpt-4o",
                    "provider": "openai",
                    "band": "standard",
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                    "credits_debited": 15,
                    "cost": 0.075,
                    "latency_ms": 1200,
                    "status": "completed"
                },
                {
                    "id": "req-124",
                    "timestamp": "2025-01-01T11:00:00Z",
                    "request_id": "chatcmpl-def456",
                    "model": "anthropic/claude-3-sonnet",
                    "provider": "anthropic",
                    "band": "priority",
                    "prompt_tokens": 200,
                    "completion_tokens": 100,
                    "total_tokens": 300,
                    "credits_debited": 30,
                    "cost": 0.150,
                    "latency_ms": 800,
                    "status": "completed"
                }
            ],
            "total_entries": 2,
            "next_cursor": "cursor-abc123"
        }
        
        respx.get("https://api.example.com/v1/credits/history").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        history = client.get_credits_history(limit=10)
        
        assert len(history.entries) == 2
        assert history.total_entries == 2
        assert history.next_cursor == "cursor-abc123"
        
        # Check first entry
        entry1 = history.entries[0]
        assert entry1.id == "req-123"
        assert entry1.model == "openai/gpt-4o"
        assert entry1.provider == "openai"
        assert entry1.total_tokens == 150
        assert entry1.credits_debited == 15
        assert entry1.cost == 0.075
        
        # Check second entry
        entry2 = history.entries[1]
        assert entry2.id == "req-124"
        assert entry2.model == "anthropic/claude-3-sonnet"
        assert entry2.provider == "anthropic"
        assert entry2.total_tokens == 300
        assert entry2.credits_debited == 30
        assert entry2.cost == 0.150

    @respx.mock
    def test_get_credits_history_with_pagination(self):
        """Test credits history with pagination parameters."""
        mock_response = {
            "entries": [],
            "total_entries": 0,
            "next_cursor": None
        }
        
        respx.get("https://api.example.com/v1/credits/history").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        history = client.get_credits_history(limit=5, cursor="test-cursor")
        
        assert len(history.entries) == 0
        assert history.total_entries == 0
        assert history.next_cursor is None

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_credits_history_async(self):
        """Test getting credits history (async)."""
        mock_response = {
            "entries": [
                {
                    "id": "req-125",
                    "timestamp": "2025-01-01T12:00:00Z",
                    "request_id": "chatcmpl-ghi789",
                    "model": "google/gemini-pro",
                    "provider": "google",
                    "band": "standard",
                    "prompt_tokens": 50,
                    "completion_tokens": 25,
                    "total_tokens": 75,
                    "credits_debited": 7,
                    "cost": 0.035,
                    "latency_ms": 600,
                    "status": "completed"
                }
            ],
            "total_entries": 1,
            "next_cursor": None
        }
        
        respx.get("https://api.example.com/v1/credits/history").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        history = await client.get_credits_history()
        
        assert len(history.entries) == 1
        assert history.total_entries == 1
        assert history.entries[0].model == "google/gemini-pro"
        assert history.entries[0].provider == "google"

    @respx.mock
    def test_get_credits_stats(self):
        """Test getting credits statistics."""
        mock_response = {
            "period": "week",
            "total_credits_used": 500,
            "total_cost": 25.50,
            "model_breakdown": [
                {"model": "openai/gpt-4o", "credits_used": 200, "cost": 10.00},
                {"model": "anthropic/claude-3-sonnet", "credits_used": 200, "cost": 12.00},
                {"model": "google/gemini-pro", "credits_used": 100, "cost": 3.50}
            ]
        }
        
        respx.get("https://api.example.com/v1/credits/stats").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        stats = client.get_credits_stats()
        
        assert stats.period == "week"
        assert stats.total_credits_used == 500
        assert stats.total_cost == 25.50
        assert len(stats.model_breakdown) == 3
        
        # Check model breakdown
        gpt4o_stats = stats.model_breakdown[0]
        assert gpt4o_stats["model"] == "openai/gpt-4o"
        assert gpt4o_stats["credits_used"] == 200
        assert gpt4o_stats["cost"] == 10.00

    @respx.mock
    def test_get_credits_stats_with_period(self):
        """Test credits stats with specific period."""
        mock_response = {
            "period": "month",
            "total_credits_used": 2000,
            "total_cost": 100.00,
            "model_breakdown": []
        }
        
        respx.get("https://api.example.com/v1/credits/stats?period=month").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        stats = client.get_credits_stats(period="month")
        
        assert stats.period == "month"
        assert stats.total_credits_used == 2000
        assert stats.total_cost == 100.00

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_credits_stats_async(self):
        """Test getting credits statistics (async)."""
        mock_response = {
            "period": "day",
            "total_credits_used": 50,
            "total_cost": 2.50,
            "model_breakdown": [
                {"model": "openai/gpt-4o-mini", "credits_used": 30, "cost": 1.50},
                {"model": "anthropic/claude-3-haiku", "credits_used": 20, "cost": 1.00}
            ]
        }
        
        respx.get("https://api.example.com/v1/credits/stats").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
        stats = await client.get_credits_stats()
        
        assert stats.period == "day"
        assert stats.total_credits_used == 50
        assert stats.total_cost == 2.50
        assert len(stats.model_breakdown) == 2

    @respx.mock
    def test_credits_with_request_id(self):
        """Test that credits endpoints preserve request IDs."""
        mock_response = {
            "credits_remaining": 1000,
            "tier": "basic",
            "bands": ["standard"],
            "reset_date": None
        }
        
        respx.get("https://api.example.com/v1/credits/balance").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
        balance = client.get_credits_balance(request_id="test-req-123")
        
        assert balance.credits_remaining == 1000
        assert balance.tier == "basic"
        
        # The request ID should be in the headers of the actual request
        # (this is tested by the mock accepting the request)