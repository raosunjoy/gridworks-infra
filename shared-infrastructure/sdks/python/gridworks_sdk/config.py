"""
Configuration classes for GridWorks SDK
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class RetryConfig(BaseModel):
    """Retry configuration for failed requests"""
    attempts: int = Field(default=3, ge=1, le=10)
    delay: float = Field(default=1.0, ge=0.1, le=60.0)
    backoff: float = Field(default=2.0, ge=1.0, le=10.0)


class WebSocketConfig(BaseModel):
    """WebSocket configuration"""
    auto_reconnect: bool = Field(default=True)
    reconnect_interval: float = Field(default=5.0, ge=1.0, le=300.0)
    max_reconnect_attempts: int = Field(default=5, ge=1, le=100)
    ping_interval: float = Field(default=30.0, ge=10.0, le=300.0)
    ping_timeout: float = Field(default=10.0, ge=1.0, le=60.0)


class GridWorksConfig(BaseModel):
    """Main configuration for GridWorks SDK"""
    
    # Authentication
    api_key: str = Field(..., description="GridWorks API key")
    token: Optional[str] = Field(default=None, description="Optional JWT token")
    client_id: str = Field(..., description="Client identifier")
    
    # Environment settings
    environment: Environment = Field(default=Environment.PRODUCTION)
    base_url: Optional[str] = Field(default=None, description="Custom base URL")
    
    # Request settings
    timeout: float = Field(default=30.0, ge=1.0, le=300.0)
    max_retries: int = Field(default=3, ge=0, le=10)
    
    # Debugging
    debug: bool = Field(default=False)
    
    # Custom headers
    headers: Dict[str, str] = Field(default_factory=dict)
    
    # Retry configuration
    retry: RetryConfig = Field(default_factory=RetryConfig)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key format"""
        if not v.startswith('gw_'):
            raise ValueError('API key must start with "gw_"')
        if len(v) < 40:
            raise ValueError('API key is too short')
        return v
    
    @validator('base_url', pre=True)
    def set_base_url(cls, v, values):
        """Set default base URL based on environment"""
        if v is not None:
            return v
            
        env = values.get('environment', Environment.PRODUCTION)
        base_urls = {
            Environment.DEVELOPMENT: "https://api-dev.gridworks.com",
            Environment.STAGING: "https://api-staging.gridworks.com", 
            Environment.PRODUCTION: "https://api.gridworks.com"
        }
        return base_urls[env]
    
    class Config:
        use_enum_values = True


class SDKOptions(BaseModel):
    """Additional SDK options"""
    
    # Concurrency
    max_concurrent_requests: int = Field(default=10, ge=1, le=100)
    
    # Logging
    enable_logging: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # User agent
    user_agent: Optional[str] = Field(default=None)
    
    # WebSocket configuration
    websocket: WebSocketConfig = Field(default_factory=WebSocketConfig)
    
    # Request/response middleware
    enable_request_logging: bool = Field(default=False)
    enable_response_logging: bool = Field(default=False)
    
    # Caching
    enable_response_caching: bool = Field(default=False)
    cache_ttl: int = Field(default=300, ge=60, le=3600)  # seconds
    
    # Rate limiting
    enable_client_rate_limiting: bool = Field(default=True)
    requests_per_minute: int = Field(default=1000, ge=1, le=10000)
    
    @validator('user_agent', pre=True)
    def set_user_agent(cls, v):
        """Set default user agent"""
        if v is not None:
            return v
        return "GridWorks-Python-SDK/1.0.0"


def create_config_for_environment(
    environment: Environment,
    api_key: str,
    client_id: str,
    **kwargs
) -> GridWorksConfig:
    """Create configuration for specific environment"""
    return GridWorksConfig(
        environment=environment,
        api_key=api_key,
        client_id=client_id,
        debug=environment == Environment.DEVELOPMENT,
        timeout=60.0 if environment == Environment.DEVELOPMENT else 30.0,
        **kwargs
    )