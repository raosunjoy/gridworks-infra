"""
GridWorks Infra - Configuration Management
Environment-based configuration with validation
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, validator, PostgresDsn, RedisDsn
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """
    
    # Application
    APP_NAME: str = "GridWorks Infrastructure"
    APP_VERSION: str = "1.0.0"
    API_VERSION: str = "v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_READ_URL: Optional[PostgresDsn] = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: RedisDsn
    REDIS_POOL_SIZE: int = 20
    REDIS_DECODE_RESPONSES: bool = True
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ENCRYPTION_KEY: str
    BCRYPT_ROUNDS: int = 12
    
    # API Keys
    API_KEY_PREFIX: str = "gw_"
    API_KEY_LENGTH: int = 32
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 100  # per minute
    RATE_LIMIT_BURST: int = 20
    
    # CORS
    CORS_ENABLED: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_CREDENTIALS: bool = True
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # Trading Services
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    UPSTOX_API_KEY: Optional[str] = None
    UPSTOX_API_SECRET: Optional[str] = None
    
    # WhatsApp Business
    WHATSAPP_API_KEY: Optional[str] = None
    WHATSAPP_PHONE_NUMBER: Optional[str] = None
    WHATSAPP_WEBHOOK_TOKEN: Optional[str] = None
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@gridworks.ai"
    SMTP_FROM_NAME: str = "GridWorks Infrastructure"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Features
    FEATURE_AI_SUITE: bool = True
    FEATURE_ANONYMOUS_SERVICES: bool = True
    FEATURE_TRADING_AS_SERVICE: bool = True
    FEATURE_BANKING_AS_SERVICE: bool = True
    
    # Enterprise Features
    MULTI_TENANT_MODE: bool = True
    AUDIT_LOGGING_ENABLED: bool = True
    ENCRYPTION_AT_REST: bool = True
    
    # Billing
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    
    # Service URLs
    PARTNERS_PORTAL_URL: str = "http://localhost:3001"
    API_GATEWAY_URL: str = "http://localhost:8000"
    ADMIN_PANEL_URL: str = "http://localhost:3002"
    
    # Webhook Configuration
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_COUNT: int = 3
    WEBHOOK_RETRY_DELAY: int = 60
    
    # Cache Configuration
    CACHE_TTL_DEFAULT: int = 3600  # 1 hour
    CACHE_TTL_SHORT: int = 300     # 5 minutes
    CACHE_TTL_LONG: int = 86400    # 24 hours
    
    # Pagination
    PAGINATION_DEFAULT_LIMIT: int = 20
    PAGINATION_MAX_LIMIT: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("REDIS_URL", pre=True)
    def validate_redis_url(cls, v):
        if not v:
            raise ValueError("REDIS_URL is required")
        return v
    
    @validator("JWT_SECRET_KEY", pre=True)
    def validate_jwt_secret(cls, v):
        if not v:
            raise ValueError("JWT_SECRET_KEY is required")
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v
    
    @validator("ENCRYPTION_KEY", pre=True)
    def validate_encryption_key(cls, v):
        if not v:
            raise ValueError("ENCRYPTION_KEY is required")
        if len(v) < 32:
            raise ValueError("ENCRYPTION_KEY must be at least 32 characters")
        return v
    
    def get_tier_config(self, tier: str) -> Dict[str, Any]:
        """Get configuration for specific client tier"""
        tier_configs = {
            "growth": {
                "api_rate_limit": 10000,
                "max_api_keys": 10,
                "max_users": 50,
                "support_sla": "24 hours",
                "data_retention_days": 90
            },
            "enterprise": {
                "api_rate_limit": 50000,
                "max_api_keys": 50,
                "max_users": 200,
                "support_sla": "4 hours",
                "data_retention_days": 365
            },
            "quantum": {
                "api_rate_limit": 200000,
                "max_api_keys": 200,
                "max_users": 1000,
                "support_sla": "1 hour",
                "data_retention_days": 730
            },
            "custom": {
                "api_rate_limit": 500000,
                "max_api_keys": 500,
                "max_users": 5000,
                "support_sla": "15 minutes",
                "data_retention_days": 1095
            }
        }
        return tier_configs.get(tier, tier_configs["growth"])
    
    def get_service_endpoints(self, service_type: str) -> List[str]:
        """Get API endpoints for a service type"""
        endpoints = {
            "ai_suite": [
                "/api/v1/ai/support",
                "/api/v1/ai/intelligence",
                "/api/v1/ai/moderator"
            ],
            "anonymous_services": [
                "/api/v1/anonymous/portfolio",
                "/api/v1/anonymous/communication",
                "/api/v1/anonymous/verification"
            ],
            "trading_as_service": [
                "/api/v1/trading/orders",
                "/api/v1/trading/positions",
                "/api/v1/trading/market-data"
            ],
            "banking_as_service": [
                "/api/v1/banking/accounts",
                "/api/v1/banking/payments",
                "/api/v1/banking/compliance"
            ]
        }
        return endpoints.get(service_type, [])


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()


# Environment-specific configurations
if settings.ENVIRONMENT == "development":
    settings.DEBUG = True
    settings.RELOAD = True
    settings.DATABASE_ECHO = True
    settings.LOG_LEVEL = "DEBUG"
elif settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.RELOAD = False
    settings.DATABASE_ECHO = False
    settings.LOG_LEVEL = "INFO"


# Feature flags
FEATURES = {
    "ai_suite": settings.FEATURE_AI_SUITE,
    "anonymous_services": settings.FEATURE_ANONYMOUS_SERVICES,
    "trading_as_service": settings.FEATURE_TRADING_AS_SERVICE,
    "banking_as_service": settings.FEATURE_BANKING_AS_SERVICE,
    "multi_tenant": settings.MULTI_TENANT_MODE,
    "audit_logging": settings.AUDIT_LOGGING_ENABLED,
    "encryption": settings.ENCRYPTION_AT_REST
}


# Service configuration
SERVICE_CONFIG = {
    "ai_suite": {
        "enabled": settings.FEATURE_AI_SUITE,
        "models": {
            "openai": settings.OPENAI_MODEL,
            "anthropic": settings.ANTHROPIC_MODEL
        },
        "rate_limits": {
            "support": 1000,
            "intelligence": 500,
            "moderator": 2000
        }
    },
    "anonymous_services": {
        "enabled": settings.FEATURE_ANONYMOUS_SERVICES,
        "privacy_levels": ["onyx", "obsidian", "void"],
        "butler_personalities": ["sterling", "prism", "nexus"],
        "zk_proof_enabled": True
    },
    "trading_as_service": {
        "enabled": settings.FEATURE_TRADING_AS_SERVICE,
        "supported_exchanges": ["NSE", "BSE", "MCX"],
        "supported_brokers": ["zerodha", "upstox"],
        "order_types": ["market", "limit", "stoploss", "cover", "amo"]
    },
    "banking_as_service": {
        "enabled": settings.FEATURE_BANKING_AS_SERVICE,
        "supported_currencies": ["INR", "USD", "EUR", "GBP"],
        "payment_methods": ["imps", "neft", "rtgs", "upi", "swift"],
        "compliance_checks": ["kyc", "aml", "sanctions"]
    }
}