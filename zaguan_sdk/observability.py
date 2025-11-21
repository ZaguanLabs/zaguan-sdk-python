"""
Observability hooks for logging and metrics in the Zaguan SDK.
"""

from typing import Optional, Dict, Any, Callable, Protocol
from datetime import datetime
import time


class RequestEvent:
    """Event data for a request."""
    
    def __init__(
        self,
        request_id: str,
        method: str,
        url: str,
        model: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.request_id = request_id
        self.method = method
        self.url = url
        self.model = model
        self.timestamp = timestamp or datetime.utcnow()
        self.start_time = time.time()


class ResponseEvent:
    """Event data for a response."""
    
    def __init__(
        self,
        request_id: str,
        status_code: int,
        latency_ms: float,
        model: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        reasoning_tokens: Optional[int] = None,
        cost: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ):
        self.request_id = request_id
        self.status_code = status_code
        self.latency_ms = latency_ms
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.reasoning_tokens = reasoning_tokens
        self.cost = cost
        self.timestamp = timestamp or datetime.utcnow()


class ErrorEvent:
    """Event data for an error."""
    
    def __init__(
        self,
        request_id: str,
        error_type: str,
        error_message: str,
        status_code: Optional[int] = None,
        retry_attempt: Optional[int] = None,
        timestamp: Optional[datetime] = None
    ):
        self.request_id = request_id
        self.error_type = error_type
        self.error_message = error_message
        self.status_code = status_code
        self.retry_attempt = retry_attempt
        self.timestamp = timestamp or datetime.utcnow()


class ObservabilityHook(Protocol):
    """Protocol for observability hooks."""
    
    def on_request_start(self, event: RequestEvent) -> None:
        """Called when a request starts."""
        ...
    
    def on_request_end(self, event: ResponseEvent) -> None:
        """Called when a request completes successfully."""
        ...
    
    def on_request_error(self, event: ErrorEvent) -> None:
        """Called when a request fails."""
        ...


class LoggingHook:
    """
    Simple logging hook that prints events to stdout.
    
    Example:
        ```python
        from zaguan_sdk import ZaguanClient
        from zaguan_sdk.observability import LoggingHook
        
        client = ZaguanClient(
            base_url="https://api.example.com",
            api_key="your-key"
        )
        
        # Add logging hook
        hook = LoggingHook(verbose=True)
        # Note: Hook integration would be added to client
        ```
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the logging hook.
        
        Args:
            verbose: Whether to log detailed information
        """
        self.verbose = verbose
    
    def on_request_start(self, event: RequestEvent) -> None:
        """Log request start."""
        if self.verbose:
            print(f"[{event.timestamp.isoformat()}] Request {event.request_id}: {event.method} {event.url}")
            if event.model:
                print(f"  Model: {event.model}")
    
    def on_request_end(self, event: ResponseEvent) -> None:
        """Log request completion."""
        print(f"[{event.timestamp.isoformat()}] Request {event.request_id}: "
              f"Status {event.status_code}, Latency {event.latency_ms:.2f}ms")
        
        if self.verbose:
            if event.model:
                print(f"  Model: {event.model}")
            if event.total_tokens:
                print(f"  Tokens: {event.prompt_tokens} prompt + {event.completion_tokens} completion = {event.total_tokens} total")
            if event.reasoning_tokens:
                print(f"  Reasoning tokens: {event.reasoning_tokens}")
            if event.cost:
                print(f"  Cost: ${event.cost:.6f}")
    
    def on_request_error(self, event: ErrorEvent) -> None:
        """Log request error."""
        print(f"[{event.timestamp.isoformat()}] Request {event.request_id}: "
              f"ERROR {event.error_type}")
        
        if self.verbose:
            print(f"  Message: {event.error_message}")
            if event.status_code:
                print(f"  Status code: {event.status_code}")
            if event.retry_attempt is not None:
                print(f"  Retry attempt: {event.retry_attempt}")


class MetricsCollector:
    """
    Collects metrics about SDK usage.
    
    This can be used to track request counts, latencies, token usage, etc.
    
    Example:
        ```python
        from zaguan_sdk.observability import MetricsCollector
        
        collector = MetricsCollector()
        
        # After some requests...
        print(f"Total requests: {collector.total_requests}")
        print(f"Average latency: {collector.average_latency_ms:.2f}ms")
        print(f"Total tokens: {collector.total_tokens}")
        ```
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency_ms = 0.0
        self.total_tokens = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_reasoning_tokens = 0
        self.total_cost = 0.0
        self.requests_by_model: Dict[str, int] = {}
        self.errors_by_type: Dict[str, int] = {}
    
    def on_request_start(self, event: RequestEvent) -> None:
        """Record request start."""
        self.total_requests += 1
    
    def on_request_end(self, event: ResponseEvent) -> None:
        """Record request completion."""
        self.successful_requests += 1
        self.total_latency_ms += event.latency_ms
        
        if event.model:
            self.requests_by_model[event.model] = self.requests_by_model.get(event.model, 0) + 1
        
        if event.total_tokens:
            self.total_tokens += event.total_tokens
        if event.prompt_tokens:
            self.total_prompt_tokens += event.prompt_tokens
        if event.completion_tokens:
            self.total_completion_tokens += event.completion_tokens
        if event.reasoning_tokens:
            self.total_reasoning_tokens += event.reasoning_tokens
        if event.cost:
            self.total_cost += event.cost
    
    def on_request_error(self, event: ErrorEvent) -> None:
        """Record request error."""
        self.failed_requests += 1
        self.errors_by_type[event.error_type] = self.errors_by_type.get(event.error_type, 0) + 1
    
    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected metrics.
        
        Returns:
            Dictionary with metric summaries
        """
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.success_rate,
            "average_latency_ms": self.average_latency_ms,
            "total_tokens": self.total_tokens,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_reasoning_tokens": self.total_reasoning_tokens,
            "total_cost": self.total_cost,
            "requests_by_model": self.requests_by_model,
            "errors_by_type": self.errors_by_type
        }


class CompositeHook:
    """
    Combines multiple observability hooks.
    
    Example:
        ```python
        from zaguan_sdk.observability import CompositeHook, LoggingHook, MetricsCollector
        
        hook = CompositeHook([
            LoggingHook(verbose=True),
            MetricsCollector()
        ])
        ```
    """
    
    def __init__(self, hooks: list):
        """
        Initialize with a list of hooks.
        
        Args:
            hooks: List of observability hooks
        """
        self.hooks = hooks
    
    def on_request_start(self, event: RequestEvent) -> None:
        """Call on_request_start on all hooks."""
        for hook in self.hooks:
            hook.on_request_start(event)
    
    def on_request_end(self, event: ResponseEvent) -> None:
        """Call on_request_end on all hooks."""
        for hook in self.hooks:
            hook.on_request_end(event)
    
    def on_request_error(self, event: ErrorEvent) -> None:
        """Call on_request_error on all hooks."""
        for hook in self.hooks:
            hook.on_request_error(event)
