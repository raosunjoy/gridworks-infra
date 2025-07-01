"""
GridWorks Infra - B2B Database Models
Enterprise client management, subscriptions, and service tracking
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, Text,
    ForeignKey, Table, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func

Base = declarative_base()


# Enums
class ClientTier(str, Enum):
    """Enterprise client subscription tiers"""
    GROWTH = "growth"           # ₹25L-5Cr annually
    ENTERPRISE = "enterprise"   # ₹5Cr-25Cr annually
    QUANTUM = "quantum"        # ₹25Cr-100Cr annually
    CUSTOM = "custom"          # Custom pricing


class ServiceType(str, Enum):
    """B2B Infrastructure service types"""
    AI_SUITE = "ai_suite"
    ANONYMOUS_SERVICES = "anonymous_services"
    TRADING_AS_SERVICE = "trading_as_service"
    BANKING_AS_SERVICE = "banking_as_service"
    CUSTOM_INTEGRATION = "custom_integration"


class BillingCycle(str, Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"


# Association tables
client_services = Table(
    'client_services',
    Base.metadata,
    Column('client_id', UUID(as_uuid=True), ForeignKey('enterprise_clients.id')),
    Column('service_id', UUID(as_uuid=True), ForeignKey('b2b_services.id')),
    Column('enabled_at', DateTime, default=func.now()),
    Column('configuration', JSONB, default={}),
    UniqueConstraint('client_id', 'service_id')
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id')),
    UniqueConstraint('user_id', 'role_id')
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id')),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id')),
    UniqueConstraint('role_id', 'permission_id')
)


class EnterpriseClient(Base):
    """Enterprise client account model"""
    __tablename__ = 'enterprise_clients'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    company_name = Column(String(255), nullable=False, unique=True)
    legal_entity_name = Column(String(255), nullable=False)
    registration_number = Column(String(100))
    tax_id = Column(String(100))
    
    # Contact information
    primary_contact_name = Column(String(255), nullable=False)
    primary_contact_email = Column(String(255), nullable=False)
    primary_contact_phone = Column(String(50))
    billing_email = Column(String(255))
    technical_email = Column(String(255))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Subscription details
    tier = Column(String(50), default=ClientTier.GROWTH.value)
    custom_contract = Column(JSONB, default={})
    onboarding_date = Column(DateTime, default=func.now())
    renewal_date = Column(DateTime)
    
    # Configuration
    api_rate_limit = Column(Integer, default=10000)  # Per minute
    max_api_keys = Column(Integer, default=10)
    max_users = Column(Integer, default=50)
    allowed_ips = Column(ARRAY(String), default=[])
    webhook_urls = Column(JSONB, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    suspension_reason = Column(Text)
    
    # Metadata
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="client")
    api_keys = relationship("APIKey", back_populates="client")
    services = relationship("B2BService", secondary=client_services, back_populates="clients")
    subscriptions = relationship("ClientSubscription", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    usage_records = relationship("UsageRecord", back_populates="client")
    audit_logs = relationship("AuditLog", back_populates="client")
    
    __table_args__ = (
        Index('idx_client_tier', 'tier'),
        Index('idx_client_active', 'is_active'),
        CheckConstraint('api_rate_limit > 0', name='check_positive_rate_limit'),
    )


class User(Base):
    """Enterprise client user model"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'), nullable=False)
    
    # Authentication
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255))
    
    # Profile
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(50))
    department = Column(String(100))
    title = Column(String(100))
    
    # Security
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(45))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Metadata
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("EnterpriseClient", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("UserSession", back_populates="user")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_client', 'client_id'),
    )


class Role(Base):
    """Role-based access control"""
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'))
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)  # System roles vs custom roles
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    __table_args__ = (
        UniqueConstraint('client_id', 'name'),
    )


class Permission(Base):
    """Granular permissions"""
    __tablename__ = 'permissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    resource = Column(String(100), nullable=False)  # e.g., "ai_suite", "trading"
    action = Column(String(100), nullable=False)    # e.g., "read", "write", "execute"
    scope = Column(String(100))                     # e.g., "own", "team", "all"
    
    name = Column(String(255), nullable=False, unique=True)  # e.g., "ai_suite.read.all"
    description = Column(Text)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    __table_args__ = (
        UniqueConstraint('resource', 'action', 'scope'),
        Index('idx_permission_resource', 'resource'),
    )


class APIKey(Base):
    """API key management"""
    __tablename__ = 'api_keys'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'), nullable=False)
    
    key_hash = Column(String(64), nullable=False, unique=True)  # SHA256 hash
    key_prefix = Column(String(10), nullable=False)  # For identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Permissions and limits
    permissions = Column(ARRAY(String), default=[])
    rate_limit = Column(Integer, default=1000)  # Per minute
    allowed_ips = Column(ARRAY(String), default=[])
    
    # Lifecycle
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    request_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Relationships
    client = relationship("EnterpriseClient", back_populates="api_keys")
    
    __table_args__ = (
        Index('idx_apikey_prefix', 'key_prefix'),
        Index('idx_apikey_client', 'client_id'),
    )


class B2BService(Base):
    """B2B infrastructure services catalog"""
    __tablename__ = 'b2b_services'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    service_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Features and configuration
    features = Column(JSONB, default={})
    default_config = Column(JSONB, default={})
    api_endpoints = Column(ARRAY(String), default=[])
    
    # Pricing (per tier)
    pricing = Column(JSONB, default={})
    usage_based_pricing = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    launch_date = Column(DateTime)
    
    # Metadata
    documentation_url = Column(String(500))
    sdk_versions = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    clients = relationship("EnterpriseClient", secondary=client_services, back_populates="services")
    
    __table_args__ = (
        Index('idx_service_type', 'service_type'),
    )


class ClientSubscription(Base):
    """Client subscription management"""
    __tablename__ = 'client_subscriptions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'), nullable=False)
    
    # Subscription details
    tier = Column(String(50), nullable=False)
    billing_cycle = Column(String(50), default=BillingCycle.ANNUAL.value)
    
    # Pricing
    base_amount = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    
    # Duration
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    trial_end_date = Column(DateTime)
    
    # Status
    status = Column(String(50), default="active")  # active, trial, suspended, cancelled
    auto_renew = Column(Boolean, default=True)
    
    # Service limits
    service_limits = Column(JSONB, default={})
    
    # Metadata
    contract_url = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("EnterpriseClient", back_populates="subscriptions")
    
    __table_args__ = (
        Index('idx_subscription_status', 'status'),
        Index('idx_subscription_dates', 'start_date', 'end_date'),
    )


class UsageRecord(Base):
    """Service usage tracking"""
    __tablename__ = 'usage_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'), nullable=False)
    
    # Service identification
    service_type = Column(String(50), nullable=False)
    service_name = Column(String(255), nullable=False)
    endpoint = Column(String(500))
    
    # Usage metrics
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    request_count = Column(Integer, default=0)
    response_time_ms = Column(Float)
    data_processed_bytes = Column(Integer)
    
    # Cost tracking
    billable_units = Column(Float, default=0.0)
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Additional metrics
    metrics = Column(JSONB, default={})
    
    # Relationships
    client = relationship("EnterpriseClient", back_populates="usage_records")
    
    __table_args__ = (
        Index('idx_usage_timestamp', 'timestamp'),
        Index('idx_usage_client_service', 'client_id', 'service_type'),
    )


class Invoice(Base):
    """Billing and invoicing"""
    __tablename__ = 'invoices'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'), nullable=False)
    
    invoice_number = Column(String(50), nullable=False, unique=True)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    # Billing period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    
    # Line items
    line_items = Column(JSONB, default=[])
    
    # Status
    status = Column(String(50), default="pending")  # pending, paid, overdue, cancelled
    payment_date = Column(DateTime)
    payment_method = Column(String(50))
    payment_reference = Column(String(255))
    
    # Documents
    invoice_url = Column(String(500))
    
    # Metadata
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("EnterpriseClient", back_populates="invoices")
    
    __table_args__ = (
        Index('idx_invoice_status', 'status'),
        Index('idx_invoice_dates', 'invoice_date', 'due_date'),
    )


class AuditLog(Base):
    """Comprehensive audit logging"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('enterprise_clients.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Event details
    event_type = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    action = Column(String(100))
    
    # Request context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    api_key_id = Column(UUID(as_uuid=True))
    
    # Event data
    request_data = Column(JSONB, default={})
    response_data = Column(JSONB, default={})
    metadata = Column(JSONB, default={})
    
    # Status
    status = Column(String(50))  # success, failure, error
    error_message = Column(Text)
    
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    client = relationship("EnterpriseClient", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_client_event', 'client_id', 'event_type'),
        Index('idx_audit_user', 'user_id'),
    )


class UserSession(Base):
    """Active user sessions"""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    session_token = Column(String(255), nullable=False, unique=True)
    refresh_token = Column(String(255), unique=True)
    
    # Session details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_info = Column(JSONB, default={})
    
    # Lifecycle
    created_at = Column(DateTime, default=func.now())
    last_active_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index('idx_session_token', 'session_token'),
        Index('idx_session_user', 'user_id'),
        Index('idx_session_expires', 'expires_at'),
    )