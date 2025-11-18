"""
Async example usage of the Zaguan SDK.
"""

import asyncio
from zaguan_sdk import AsyncZaguanClient, ChatRequest, Message


async def async_chat_example():
    """Async chat completion example."""
    # Initialize client
    client = AsyncZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Create chat request
    request = ChatRequest(
        model="openai/gpt-4o-mini",
        messages=[
            Message(role="user", content="Hello! How are you?")
        ]
    )
    
    # Make request
    response = await client.chat(request)
    
    # Print response
    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(async_chat_example())