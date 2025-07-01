"""
Custom exceptions for GridWorks SDK
"""

from typing import Any, Optional


class GridWorksError(Exception):
    """Base exception for all GridWorks SDK errors"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self) -> str:
        return self.message
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class APIError(GridWorksError):
    """API request failed"""
    
    def __init__(self, 
                 message: str, 
                 status_code: int = 500,
                 code: str = "API_ERROR",
                 details: Optional[Any] = None):
        super().__init__(message, details)
        self.status_code = status_code
        self.code = code
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update({
            "status_code": self.status_code,
            "code": self.code
        })
        return result


class AuthenticationError(APIError):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, 401, "AUTHENTICATION_ERROR", details)


class ValidationError(APIError):
    """Request validation failed"""
    
    def __init__(self, 
                 message: str, 
                 field: Optional[str] = None, 
                 details: Optional[Any] = None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)
        self.field = field
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.field:
            result["field"] = self.field
        return result


class RateLimitError(APIError):
    """Rate limit exceeded"""
    
    def __init__(self, 
                 message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None,
                 details: Optional[Any] = None):
        super().__init__(message, 429, "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.retry_after:
            result["retry_after"] = self.retry_after
        return result


class ServiceUnavailableError(APIError):
    """Service temporarily unavailable"""
    
    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Any] = None):
        super().__init__(message, 503, "SERVICE_UNAVAILABLE", details)


class NetworkError(GridWorksError):
    """Network connection error"""
    
    def __init__(self, message: str = "Network error occurred", details: Optional[Any] = None):
        super().__init__(message, details)


class TimeoutError(GridWorksError):
    """Request timeout"""
    
    def __init__(self, message: str = "Request timeout", details: Optional[Any] = None):
        super().__init__(message, details)


class ConfigurationError(GridWorksError):
    """SDK configuration error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, details)


class WebSocketError(GridWorksError):
    """WebSocket connection error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, details)


def create_error_from_response(response_data: dict, status_code: int) -> APIError:
    """
    Create appropriate error from API response
    
    Args:
        response_data: Response data from API
        status_code: HTTP status code
        
    Returns:
        Appropriate exception instance
    """
    message = response_data.get("message", "An error occurred")
    code = response_data.get("code", "UNKNOWN_ERROR")
    details = response_data.get("details")
    
    if status_code == 400:
        return ValidationError(message, response_data.get("field"), details)
    elif status_code == 401:
        return AuthenticationError(message, details)
    elif status_code == 429:
        return RateLimitError(message, response_data.get("retry_after"), details)
    elif status_code == 503:
        return ServiceUnavailableError(message, details)
    else:
        return APIError(message, status_code, code, details)