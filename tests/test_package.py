"""
Test to verify the package structure and imports.
"""

def test_package_structure():
    # Test imports
    from zaguan_sdk import (
        ZaguanClient, AsyncZaguanClient,
        Message, TokenDetails, Usage, ChatRequest, Choice,
        ChatResponse, ChatChunk, ModelInfo, ModelCapabilities,
        CreditsBalance, CreditsHistoryEntry, CreditsHistory, CreditsStats
    )
    
    from zaguan_sdk import (
        ZaguanError, APIError, InsufficientCreditsError, RateLimitError
    )
    
    # Verify classes exist
    assert ZaguanClient is not None
    assert AsyncZaguanClient is not None
    assert Message is not None
    assert ChatRequest is not None
    assert ChatResponse is not None
    
    print("All imports successful")


if __name__ == "__main__":
    test_package_structure()