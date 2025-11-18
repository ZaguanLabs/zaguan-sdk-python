"""
Advanced features example for the Zaguan SDK.

This example demonstrates:
- Provider-specific parameters
- Reasoning models (o1, o3)
- DeepSeek thinking control
- Audio modalities (GPT-4o Audio)
- Virtual model IDs
- Error handling
"""

from zaguan_sdk import (
    ZaguanClient, ChatRequest, Message,
    InsufficientCreditsError, RateLimitError, BandAccessDeniedError
)


def gemini_reasoning_example():
    """Example using Google Gemini with reasoning control."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="google/gemini-2.5-pro",
        messages=[
            Message(role="user", content="Solve this complex math problem: ...")
        ],
        provider_specific_params={
            "reasoning_effort": "high",
            "thinking_budget": 10000
        }
    )
    
    response = client.chat(request)
    print(f"Response: {response.choices[0].message.content}")
    
    # Check for reasoning tokens
    if response.usage.completion_tokens_details:
        reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
        if reasoning_tokens:
            print(f"Reasoning tokens used: {reasoning_tokens}")


def openai_reasoning_model_example():
    """Example using OpenAI o1/o3 reasoning models."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="openai/o1",
        messages=[
            Message(role="user", content="Explain quantum computing")
        ],
        reasoning_effort="high"  # Direct parameter for reasoning models
    )
    
    response = client.chat(request)
    print(f"Response: {response.choices[0].message.content}")
    print(f"Total tokens: {response.usage.total_tokens}")


def deepseek_thinking_control_example():
    """Example using DeepSeek with thinking control."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Disable thinking output
    request = ChatRequest(
        model="deepseek/deepseek-reasoner",
        messages=[
            Message(role="user", content="What is the capital of France?")
        ],
        thinking=False  # Suppress <think> tags
    )
    
    response = client.chat(request)
    print(f"Response (no thinking): {response.choices[0].message.content}")


def anthropic_extended_thinking_example():
    """Example using Anthropic Claude with extended thinking."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="anthropic/claude-3-5-sonnet",
        messages=[
            Message(role="user", content="Analyze this complex problem...")
        ],
        provider_specific_params={
            "thinking": {
                "type": "enabled",
                "budget_tokens": 5000
            }
        }
    )
    
    response = client.chat(request)
    print(f"Response: {response.choices[0].message.content}")


def perplexity_search_example():
    """Example using Perplexity with search parameters."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="perplexity/sonar-reasoning",
        messages=[
            Message(role="user", content="What are the latest AI developments?")
        ],
        provider_specific_params={
            "search_domain_filter": ["arxiv.org", "openai.com"],
            "return_citations": True,
            "search_recency_filter": "month"
        }
    )
    
    response = client.chat(request)
    print(f"Response with citations: {response.choices[0].message.content}")


def gpt4o_audio_example():
    """Example using GPT-4o with audio modalities."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="openai/gpt-4o-audio",
        messages=[
            Message(role="user", content="Tell me a story")
        ],
        modalities=["text", "audio"],
        audio={
            "voice": "alloy",
            "format": "mp3"
        }
    )
    
    response = client.chat(request)
    print(f"Response: {response.choices[0].message.content}")
    # Audio data would be in response if available


def extra_body_compatibility_example():
    """Example using extra_body for OpenAI SDK compatibility."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Using extra_body (OpenAI SDK style)
    request = ChatRequest(
        model="google/gemini-2.0-flash",
        messages=[
            Message(role="user", content="Hello")
        ],
        extra_body={
            "reasoning_effort": "medium"
        }
    )
    
    response = client.chat(request)
    print(f"Response: {response.choices[0].message.content}")


def virtual_model_example():
    """Example using virtual model IDs."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[
            Message(role="user", content="Hello")
        ],
        virtual_model_id="my-app-prod"  # Custom routing
    )
    
    response = client.chat(request)
    print(f"Response: {response.choices[0].message.content}")


def error_handling_example():
    """Example demonstrating comprehensive error handling."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    request = ChatRequest(
        model="openai/gpt-4o",
        messages=[
            Message(role="user", content="Hello")
        ]
    )
    
    try:
        response = client.chat(request)
        print(f"Response: {response.choices[0].message.content}")
    except InsufficientCreditsError as e:
        print(f"Insufficient credits: {e}")
        print(f"Required: {e.credits_required}, Remaining: {e.credits_remaining}")
    except RateLimitError as e:
        print(f"Rate limited: {e}")
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
    except BandAccessDeniedError as e:
        print(f"Band access denied: {e}")
        print(f"Band: {e.band}, Required tier: {e.required_tier}, Current: {e.current_tier}")
    except Exception as e:
        print(f"Error: {e}")


def context_manager_example():
    """Example using context manager for automatic cleanup."""
    with ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    ) as client:
        request = ChatRequest(
            model="openai/gpt-4o-mini",
            messages=[
                Message(role="user", content="Hello")
            ]
        )
        response = client.chat(request)
        print(f"Response: {response.choices[0].message.content}")
    # Client is automatically closed


if __name__ == "__main__":
    print("=== Gemini Reasoning Example ===")
    # gemini_reasoning_example()
    
    print("\n=== OpenAI Reasoning Model Example ===")
    # openai_reasoning_model_example()
    
    print("\n=== DeepSeek Thinking Control Example ===")
    # deepseek_thinking_control_example()
    
    print("\n=== Error Handling Example ===")
    # error_handling_example()
    
    print("\nExamples are commented out. Uncomment and add your API credentials to run.")
