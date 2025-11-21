"""
Streaming utilities for the Zaguan SDK.
"""

from typing import List, Optional
from .models import ChatChunk, Message, Choice


class StreamAccumulator:
    """
    Helper class to accumulate streaming chunks into a final message.
    
    This is useful for reconstructing the complete response from streaming chunks.
    """
    
    def __init__(self):
        """Initialize the accumulator."""
        self.id: Optional[str] = None
        self.object: Optional[str] = None
        self.created: Optional[int] = None
        self.model: Optional[str] = None
        self.content_parts: List[str] = []
        self.role: Optional[str] = None
        self.finish_reason: Optional[str] = None
        self.tool_calls: List[dict] = []
        
    def add_chunk(self, chunk: ChatChunk) -> None:
        """
        Add a chunk to the accumulator.
        
        Args:
            chunk: The chunk to add
        """
        # Update metadata from first chunk
        if self.id is None:
            self.id = chunk.id
            self.object = chunk.object
            self.created = chunk.created
            self.model = chunk.model
        
        # Process choices
        for choice in chunk.choices:
            if choice.delta:
                # Accumulate role
                if choice.delta.role:
                    self.role = choice.delta.role
                
                # Accumulate content
                if choice.delta.content:
                    self.content_parts.append(choice.delta.content)
                
                # Accumulate tool calls
                if choice.delta.tool_calls:
                    self.tool_calls.extend(choice.delta.tool_calls)
            
            # Update finish reason
            if choice.finish_reason:
                self.finish_reason = choice.finish_reason
    
    def get_message(self) -> Message:
        """
        Get the accumulated message.
        
        Returns:
            The complete message reconstructed from all chunks
        """
        content = "".join(self.content_parts) if self.content_parts else None
        
        return Message(
            role=self.role,
            content=content,
            tool_calls=self.tool_calls if self.tool_calls else None
        )
    
    def get_content(self) -> str:
        """
        Get the accumulated content as a string.
        
        Returns:
            The complete content text
        """
        return "".join(self.content_parts)
    
    def reset(self) -> None:
        """Reset the accumulator to process a new stream."""
        self.id = None
        self.object = None
        self.created = None
        self.model = None
        self.content_parts = []
        self.role = None
        self.finish_reason = None
        self.tool_calls = []


def reconstruct_message_from_stream(chunks: List[ChatChunk]) -> Message:
    """
    Reconstruct a complete message from a list of streaming chunks.
    
    Args:
        chunks: List of chat chunks from a streaming response
        
    Returns:
        The reconstructed message
        
    Example:
        ```python
        chunks = []
        for chunk in client.chat_stream(request):
            chunks.append(chunk)
        
        message = reconstruct_message_from_stream(chunks)
        print(message.content)
        ```
    """
    accumulator = StreamAccumulator()
    for chunk in chunks:
        accumulator.add_chunk(chunk)
    return accumulator.get_message()
