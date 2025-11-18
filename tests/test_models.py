"""Tests for model classes and data structures."""
import pytest
from zaguan_sdk import ChatRequest, Message


def test_message_role_optional():
    """Test that Message role is optional (for streaming deltas)."""
    # This should work with role
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    
    # This should also work without role (for streaming deltas)
    msg_delta = Message(content="Hello")
    assert msg_delta.role is None
    assert msg_delta.content == "Hello"


def test_message_supports_all_roles():
    """Test that Message supports all documented roles."""
    roles = ["system", "user", "assistant", "tool", "function", "developer"]
    for role in roles:
        msg = Message(role=role, content="test")
        assert msg.role == role


def test_chat_request_extra_body_merge():
    """Test that extra_body is merged with provider_specific_params."""
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")],
        provider_specific_params={"param1": "value1"},
        extra_body={"param2": "value2"}
    )
    
    dumped = request.model_dump(exclude_none=True)
    
    # extra_body should be merged into provider_specific_params
    assert "extra_body" not in dumped
    assert dumped["provider_specific_params"] == {
        "param1": "value1",
        "param2": "value2"
    }


def test_chat_request_extra_body_only():
    """Test that extra_body alone becomes provider_specific_params."""
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")],
        extra_body={"param1": "value1"}
    )
    
    dumped = request.model_dump(exclude_none=True)
    
    # extra_body should become provider_specific_params
    assert "extra_body" not in dumped
    assert dumped["provider_specific_params"] == {"param1": "value1"}


def test_chat_request_thinking_parameter():
    """Test that thinking parameter is supported (DeepSeek)."""
    request = ChatRequest(
        model="deepseek/deepseek-reasoner",
        messages=[Message(role="user", content="Hello")],
        thinking=False
    )
    
    dumped = request.model_dump(exclude_none=True)
    assert dumped["thinking"] is False


def test_chat_request_reasoning_effort():
    """Test that reasoning_effort parameter is supported (o1, o3)."""
    request = ChatRequest(
        model="openai/o1",
        messages=[Message(role="user", content="Hello")],
        reasoning_effort="high"
    )
    
    dumped = request.model_dump(exclude_none=True)
    assert dumped["reasoning_effort"] == "high"


def test_chat_request_modalities():
    """Test that modalities parameter is supported (GPT-4o Audio)."""
    request = ChatRequest(
        model="openai/gpt-4o-audio",
        messages=[Message(role="user", content="Hello")],
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "mp3"}
    )
    
    dumped = request.model_dump(exclude_none=True)
    assert dumped["modalities"] == ["text", "audio"]
    assert dumped["audio"] == {"voice": "alloy", "format": "mp3"}


def test_chat_request_virtual_model_id():
    """Test that virtual_model_id is supported."""
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")],
        virtual_model_id="my-app-prod"
    )
    
    dumped = request.model_dump(exclude_none=True)
    assert dumped["virtual_model_id"] == "my-app-prod"


def test_chat_request_parallel_tool_calls():
    """Test that parallel_tool_calls is supported."""
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[Message(role="user", content="Hello")],
        parallel_tool_calls=True
    )
    
    dumped = request.model_dump(exclude_none=True)
    assert dumped["parallel_tool_calls"] is True


def test_message_function_call():
    """Test that Message supports function_call for legacy compatibility."""
    msg = Message(
        role="assistant",
        content=None,
        function_call={"name": "get_weather", "arguments": '{"location": "NYC"}'}
    )
    
    assert msg.function_call is not None
    assert msg.function_call["name"] == "get_weather"
