"""
GridWorks Configuration Management
Handles all application settings and environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # App Configuration
    APP_NAME: str = "GridWorks"
    DEBUG: bool = Field(default=False, env="DEBUG")
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    # WhatsApp Business API
    WHATSAPP_ACCESS_TOKEN: str = Field(..., env="WHATSAPP_ACCESS_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID: str = Field(..., env="WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = Field(..., env="WHATSAPP_WEBHOOK_VERIFY_TOKEN")
    WHATSAPP_APP_SECRET: str = Field(..., env="WHATSAPP_APP_SECRET")
    
    # AI/ML Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Trading APIs
    ZERODHA_API_KEY: Optional[str] = Field(default=None, env="ZERODHA_API_KEY")
    ZERODHA_API_SECRET: Optional[str] = Field(default=None, env="ZERODHA_API_SECRET")
    UPSTOX_API_KEY: Optional[str] = Field(default=None, env="UPSTOX_API_KEY")
    UPSTOX_API_SECRET: Optional[str] = Field(default=None, env="UPSTOX_API_SECRET")
    
    # Regulatory APIs
    SEBI_AA_CLIENT_ID: Optional[str] = Field(default=None, env="SEBI_AA_CLIENT_ID")
    SEBI_AA_CLIENT_SECRET: Optional[str] = Field(default=None, env="SEBI_AA_CLIENT_SECRET")
    CKYC_API_KEY: Optional[str] = Field(default=None, env="CKYC_API_KEY")
    
    # Setu API Integration (Financial Services)
    SETU_CLIENT_ID: Optional[str] = Field(default=None, env="SETU_CLIENT_ID")
    SETU_CLIENT_SECRET: Optional[str] = Field(default=None, env="SETU_CLIENT_SECRET")
    SETU_BASE_URL: str = Field(default="https://prod.setu.co", env="SETU_BASE_URL")
    SETU_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="SETU_WEBHOOK_SECRET")
    
    # Stripe Payment Gateway
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # Razorpay Payment Gateway
    RAZORPAY_KEY_ID: Optional[str] = Field(default=None, env="RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET: Optional[str] = Field(default=None, env="RAZORPAY_KEY_SECRET")
    
    # Enterprise Security
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")
    HSM_KEY_ID: Optional[str] = Field(default=None, env="HSM_KEY_ID")
    AUDIT_ENCRYPTION_KEY: str = Field(..., env="AUDIT_ENCRYPTION_KEY")
    
    # External APIs
    NSE_API_URL: str = Field(default="https://www.nseindia.com/api", env="NSE_API_URL")
    MARKET_DATA_API_KEY: Optional[str] = Field(default=None, env="MARKET_DATA_API_KEY")
    NEWS_API_KEY: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    
    # Background Tasks
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Feature Flags
    ENABLE_SOCIAL_TRADING: bool = Field(default=False, env="ENABLE_SOCIAL_TRADING")
    ENABLE_OPTIONS_TRADING: bool = Field(default=False, env="ENABLE_OPTIONS_TRADING")
    ENABLE_CRYPTO_TRADING: bool = Field(default=False, env="ENABLE_CRYPTO_TRADING")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()