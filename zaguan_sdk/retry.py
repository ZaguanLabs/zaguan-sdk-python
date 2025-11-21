"""
Retry logic with exponential backoff for the Zaguan SDK.
"""

import time
import random
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps
import httpx

T = TypeVar('T')


class RetryConfig:
    """
    Configuration for retry behavior.
    
    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        jitter: Whether to add random jitter to delays (default: True)
        retry_on_status_codes: HTTP status codes to retry on (default: 429, 500, 502, 503, 504)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504)
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on_status_codes = retry_on_status_codes
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate the delay for a given retry attempt.
        
        Args:
            attempt: The retry attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        # Add jitter to avoid thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if a request should be retried.
        
        Args:
            exception: The exception that occurred
            attempt: The current attempt number (0-indexed)
            
        Returns:
            True if the request should be retried
        """
        if attempt >= self.max_retries:
            return False
        
        # Retry on network errors
        if isinstance(exception, (httpx.NetworkError, httpx.TimeoutException)):
            return True
        
        # Retry on specific HTTP status codes
        if isinstance(exception, httpx.HTTPStatusError):
            return exception.response.status_code in self.retry_on_status_codes
        
        return False


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator to add retry logic to a function.
    
    Args:
        config: Retry configuration. If None, uses default configuration.
        
    Example:
        ```python
        @with_retry(RetryConfig(max_retries=5))
        def make_request():
            response = client.get("https://api.example.com")
            response.raise_for_status()
            return response
        ```
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            attempt = 0
            last_exception = None
            
            while attempt <= config.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if not config.should_retry(e, attempt):
                        raise
                    
                    delay = config.calculate_delay(attempt)
                    time.sleep(delay)
                    attempt += 1
            
            # If we exhausted all retries, raise the last exception
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


async def async_with_retry(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    *args,
    **kwargs
) -> T:
    """
    Async function to retry an async operation.
    
    Args:
        func: The async function to retry
        config: Retry configuration
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        The result of the function call
        
    Example:
        ```python
        async def make_request():
            response = await client.get("https://api.example.com")
            response.raise_for_status()
            return response
        
        result = await async_with_retry(make_request, RetryConfig(max_retries=5))
        ```
    """
    if config is None:
        config = RetryConfig()
    
    attempt = 0
    last_exception = None
    
    while attempt <= config.max_retries:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if not config.should_retry(e, attempt):
                raise
            
            delay = config.calculate_delay(attempt)
            
            # Use asyncio.sleep for async
            import asyncio
            await asyncio.sleep(delay)
            attempt += 1
    
    # If we exhausted all retries, raise the last exception
    if last_exception:
        raise last_exception
