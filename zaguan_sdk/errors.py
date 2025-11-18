"""
Error types for the Zaguan SDK.
"""

from typing import Optional


class ZaguanError(Exception):
    """Base exception for all Zaguan SDK errors."""
    pass


class APIError(ZaguanError):
    """Exception for API errors."""
    def __init__(self, status_code: int, message: str, request_id: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id


class InsufficientCreditsError(ZaguanError):
    """Exception for insufficient credits."""
    def __init__(self, message: str, credits_required: int, credits_remaining: int):
        super().__init__(message)
        self.credits_required = credits_required
        self.credits_remaining = credits_remaining


class RateLimitError(ZaguanError):
    """Exception for rate limiting."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after