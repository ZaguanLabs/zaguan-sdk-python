"""
HTTP utilities for the Zaguan SDK.
"""

import httpx
import json
import uuid
from typing import Optional, Dict, Any, Iterator
from .errors import APIError, InsufficientCreditsError, RateLimitError, BandAccessDeniedError


def handle_response(response: httpx.Response, model_class: Any = None):
    """Handle an HTTP response and convert it to the appropriate model or error."""
    if response.status_code >= 200 and response.status_code < 300:
        if model_class:
            return model_class(**response.json())
        return response.json()
    
    # Handle error responses
    error_data = None
    try:
        error_data = response.json()
    except json.JSONDecodeError:
        pass
    
    message = "Unknown error"
    request_id = response.headers.get("X-Request-Id")
    
    if error_data and "error" in error_data:
        error = error_data["error"]
        message = error.get("message", message)
        
        # Handle specific error types
        error_type = error.get("type")
        if error_type == "insufficient_credits":
            raise InsufficientCreditsError(
                message,
                error.get("credits_required", 0),
                error.get("credits_remaining", 0)
            )
        elif error_type == "rate_limit_exceeded":
            raise RateLimitError(
                message,
                error.get("retry_after")
            )
        elif error_type == "band_access_denied":
            raise BandAccessDeniedError(
                message,
                error.get("band"),
                error.get("required_tier"),
                error.get("current_tier")
            )
    
    raise APIError(response.status_code, message, request_id)


def prepare_headers(api_key: str, request_id: Optional[str] = None) -> Dict[str, str]:
    """Prepare headers for an API request."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    if request_id:
        headers["X-Request-Id"] = request_id
    else:
        headers["X-Request-Id"] = str(uuid.uuid4())
    
    return headers