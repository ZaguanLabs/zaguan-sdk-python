"""Tests for input validation and security."""
import pytest
from zaguan_sdk import ZaguanClient, AsyncZaguanClient, BandAccessDeniedError
from zaguan_sdk.errors import APIError


def test_client_requires_base_url():
    """Test that client raises ValueError for empty base_url."""
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        ZaguanClient(base_url="", api_key="test-key")
    
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        ZaguanClient(base_url="   ", api_key="test-key")


def test_client_requires_api_key():
    """Test that client raises ValueError for empty api_key."""
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        ZaguanClient(base_url="https://api.example.com", api_key="")
    
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        ZaguanClient(base_url="https://api.example.com", api_key="   ")


def test_async_client_requires_base_url():
    """Test that async client raises ValueError for empty base_url."""
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        AsyncZaguanClient(base_url="", api_key="test-key")


def test_async_client_requires_api_key():
    """Test that async client raises ValueError for empty api_key."""
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        AsyncZaguanClient(base_url="https://api.example.com", api_key="")


def test_client_default_timeout():
    """Test that client sets default timeout to 30 seconds."""
    client = ZaguanClient(base_url="https://api.example.com", api_key="test-key")
    assert client.timeout == 30.0


def test_client_custom_timeout():
    """Test that client respects custom timeout."""
    client = ZaguanClient(
        base_url="https://api.example.com", 
        api_key="test-key",
        timeout=60.0
    )
    assert client.timeout == 60.0


def test_async_client_default_timeout():
    """Test that async client sets default timeout to 30 seconds."""
    client = AsyncZaguanClient(base_url="https://api.example.com", api_key="test-key")
    assert client.timeout == 30.0


def test_band_access_denied_error_attributes():
    """Test that BandAccessDeniedError stores all attributes correctly."""
    error = BandAccessDeniedError(
        message="Access denied",
        band="D",
        required_tier="platinum",
        current_tier="pro"
    )
    assert str(error) == "Access denied"
    assert error.band == "D"
    assert error.required_tier == "platinum"
    assert error.current_tier == "pro"
