"""
Common models used across all services
"""

from typing import Any, Optional, List, Dict, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str
    request_id: str


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(APIResponse[List[T]]):
    """Paginated API response"""
    pagination: PaginationInfo


class RequestMetrics(BaseModel):
    """Request performance metrics"""
    request_id: str
    endpoint: str
    method: str
    duration: float  # seconds
    status_code: int
    timestamp: str
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[str] = None


class ServiceTier(str, Enum):
    """Service tier levels"""
    STARTER = "starter"
    PROFESSIONAL = "professional" 
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ServiceTierInfo(BaseModel):
    """Service tier information"""
    name: ServiceTier
    limits: Dict[str, Any]
    features: List[str]


class ClientInfo(BaseModel):
    """Client information"""
    id: str
    name: str
    email: str
    tier: ServiceTierInfo
    status: str  # active, suspended, trial
    subscription: Dict[str, Any]


class AuthenticationInfo(BaseModel):
    """Authentication information"""
    type: str  # api_key, jwt, oauth
    token: str
    expires_at: Optional[str] = None
    scopes: Optional[List[str]] = None
    client_id: str


class HealthStatus(BaseModel):
    """Service health status"""
    service: str
    status: bool
    latency: Optional[float] = None
    last_check: str
    details: Optional[Dict[str, Any]] = None


class ErrorDetails(BaseModel):
    """Detailed error information"""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None


class RateLimitInfo(BaseModel):
    """Rate limiting information"""
    limit: int
    remaining: int
    reset_time: str
    window: int  # seconds


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    data: Any
    timestamp: str
    channel: Optional[str] = None
    request_id: Optional[str] = None


class FileUpload(BaseModel):
    """File upload information"""
    filename: str
    content_type: str
    size: int
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Attachment(BaseModel):
    """File attachment"""
    type: str
    url: str
    name: str
    size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class Address(BaseModel):
    """Address information"""
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    additional_info: Optional[str] = None


class Contact(BaseModel):
    """Contact information"""
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[Address] = None


class Money(BaseModel):
    """Money amount with currency"""
    amount: float
    currency: str = Field(default="INR")
    
    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


class TimeRange(BaseModel):
    """Time range specification"""
    start_time: datetime
    end_time: datetime
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds"""
        return (self.end_time - self.start_time).total_seconds()


class FilterOptions(BaseModel):
    """Common filter options"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = Field(default=50, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")


class BulkOperationResult(BaseModel, Generic[T]):
    """Result of bulk operation"""
    total: int
    successful: int
    failed: int
    successful_items: List[T]
    failed_items: List[Dict[str, Any]]
    summary: Dict[str, Any]


class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe options"""
    HOUR = "1h"
    DAY = "1d" 
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"
    YEAR = "365d"


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    error_rate: float
    throughput: float  # requests per second


class ComplianceStatus(str, Enum):
    """Compliance status options"""
    PASSED = "passed"
    PENDING = "pending"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DocumentType(str, Enum):
    """Document types for KYC/compliance"""
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    ADDRESS_PROOF = "address_proof"
    BANK_STATEMENT = "bank_statement"
    INCOME_PROOF = "income_proof"
    BUSINESS_REGISTRATION = "business_registration"
    OTHER = "other"