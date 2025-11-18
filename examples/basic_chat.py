"""
Example usage of the Zaguan SDK.
"""

from zaguan_sdk import ZaguanClient, ChatRequest, Message


def basic_chat_example():
    """Basic chat completion example."""
    # Initialize client
    client = ZaguanClient(
        base_url="https://api.your-zaguan-host.com",
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
    response = client.chat(request)
    
    # Print response
    print(response.choices[0].message.content)


if __name__ == "__main__":
    basic_chat_example()