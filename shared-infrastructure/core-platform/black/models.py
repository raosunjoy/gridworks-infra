"""
GridWorks Black Data Models
Exclusive data structures for premium trading platform
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid


class BlackTier(Enum):
    """GridWorks Black sub-tiers"""
    ONYX = "ONYX"        # ₹50L-2Cr portfolio
    OBSIDIAN = "OBSIDIAN" # ₹2Cr-5Cr portfolio  
    VOID = "VOID"         # ₹5Cr+ portfolio


class AccessLevel(Enum):
    """Access levels within Black tier"""
    STANDARD = "standard"      # Basic Black features
    PREMIUM = "premium"        # Enhanced features
    CONCIERGE = "concierge"    # Full white-glove service
    EXCLUSIVE = "exclusive"    # Void-only features


class InvestmentClass(Enum):
    """Types of exclusive investment opportunities"""
    PRE_IPO = "pre_ipo"
    PRIVATE_EQUITY = "private_equity"
    HEDGE_FUNDS = "hedge_funds"
    STRUCTURED_PRODUCTS = "structured_products"
    ALTERNATIVE_INVESTMENTS = "alternative_investments"


class DevicePlatform(Enum):
    """Supported premium device platforms"""
    IOS_NATIVE = "ios_native"
    ANDROID_NATIVE = "android_native"
    WEB_FALLBACK = "web_fallback"


class SecurityFeature(Enum):
    """Premium security features"""
    HARDWARE_BOUND = "hardware_bound"
    BIOMETRIC_AUTH = "biometric_auth"
    DEVICE_FINGERPRINT = "device_fingerprint"
    SECURE_ENCLAVE = "secure_enclave"
    FACE_ID = "face_id"
    FINGERPRINT = "fingerprint"
    HARDWARE_KEY = "hardware_key"


@dataclass
class BlackUser:
    """GridWorks Black user profile"""
    user_id: str
    tier: BlackTier
    access_level: AccessLevel
    portfolio_value: float
    net_worth: float
    risk_appetite: str  # conservative, moderate, aggressive, ultra_aggressive
    investment_preferences: List[InvestmentClass]
    
    # Exclusivity metrics
    invitation_code: str
    invited_by: Optional[str]
    joining_date: datetime
    tier_progression_date: datetime
    
    # Butler assignment
    dedicated_butler: Optional[str]
    butler_contact_preference: str  # chat, call, video, in_person
    
    # Verification
    kyc_level: str  # enhanced, premium, ultra_premium
    aml_score: float
    risk_score: float
    compliance_status: str
    
    # Preferences
    trading_hours_preference: str
    notification_preferences: Dict[str, bool]
    privacy_settings: Dict[str, Any]
    
    # Status
    is_active: bool
    last_activity: datetime
    session_count: int
    total_trades: int
    total_volume: float


@dataclass
class MarketButlerProfile:
    """Dedicated market butler for Black users"""
    butler_id: str
    name: str
    specializations: List[str]  # equities, derivatives, alternatives, wealth_management
    languages: List[str]
    experience_years: int
    certification_level: str  # CFA, FRM, CAIA, etc.
    
    # Performance metrics
    client_satisfaction: float
    average_response_time: float  # seconds
    success_rate: float
    portfolio_performance: float  # alpha generated
    
    # Availability
    working_hours: Dict[str, Any]
    time_zone: str
    current_load: int
    max_clients: int
    
    # Communication
    preferred_channels: List[str]
    contact_info: Dict[str, str]
    availability_status: str  # available, busy, offline


@dataclass
class ExclusiveOpportunity:
    """Exclusive investment opportunity for Black users"""
    opportunity_id: str
    title: str
    description: str
    investment_class: InvestmentClass
    
    # Financial details
    minimum_investment: float
    maximum_investment: float
    expected_return: float
    risk_level: str
    investment_horizon: str  # months/years
    
    # Exclusivity
    total_slots: int
    available_slots: int
    tier_requirements: List[BlackTier]
    access_level_required: AccessLevel
    
    # Timeline
    launch_date: datetime
    closing_date: datetime
    investment_start: datetime
    expected_exit: datetime
    
    # Documentation
    pitch_deck_url: str
    due_diligence_report: str
    legal_documents: List[str]
    
    # Performance
    track_record: Dict[str, Any]
    similar_investments: List[str]
    success_probability: float


@dataclass
class ConciergeRequest:
    """White-glove concierge service request"""
    request_id: str
    user_id: str
    butler_id: str
    
    # Request details
    service_type: str  # trading, research, portfolio_review, market_access, lifestyle
    priority: str      # standard, urgent, critical
    description: str
    specific_requirements: Dict[str, Any]
    
    # Timeline
    requested_at: datetime
    required_by: Optional[datetime]
    estimated_completion: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Status tracking
    status: str  # pending, in_progress, completed, cancelled
    progress_updates: List[Dict[str, Any]]
    
    # Resources
    assigned_specialists: List[str]
    external_partners: List[str]
    estimated_cost: Optional[float]
    
    # Outcome
    satisfaction_rating: Optional[float]
    outcome_summary: Optional[str]
    follow_up_required: bool


@dataclass
class BlackSession:
    """User session for Black app"""
    session_id: str
    user_id: str
    device_id: str
    
    # Session details
    start_time: datetime
    last_activity: datetime
    session_duration: float
    
    # Security
    authentication_method: str  # biometric, hardware_key, multi_factor
    device_fingerprint: str
    location: Dict[str, Any]
    risk_score: float
    
    # Activity tracking
    screens_visited: List[str]
    actions_performed: List[Dict[str, Any]]
    trades_executed: int
    volume_traded: float
    
    # Butler interaction
    butler_conversations: List[str]
    support_interactions: int
    concierge_requests: int
    
    # Performance
    response_times: List[float]
    error_count: int
    satisfaction_score: Optional[float]


@dataclass
class BlackAnalytics:
    """Analytics data for Black platform"""
    user_id: str
    analytics_date: datetime
    
    # Trading metrics
    portfolio_performance: Dict[str, float]
    risk_metrics: Dict[str, float]
    trade_analytics: Dict[str, Any]
    benchmark_comparison: Dict[str, float]
    
    # Engagement metrics
    app_usage: Dict[str, float]
    feature_usage: Dict[str, int]
    butler_interaction_frequency: float
    concierge_utilization: float
    
    # Satisfaction metrics
    nps_score: Optional[float]
    support_satisfaction: Optional[float]
    platform_satisfaction: Optional[float]
    retention_probability: float
    
    # Personalization data
    preferences_learned: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    predictive_insights: Dict[str, Any]
    
    # Revenue metrics
    fees_paid: float
    services_purchased: float
    referrals_generated: int
    lifetime_value: float


@dataclass
class VoidExclusives:
    """Ultra-exclusive features for Void tier users"""
    user_id: str
    
    # Ultra-premium access
    private_market_access: bool
    hedge_fund_seeding: bool
    family_office_services: bool
    
    # Exclusive events
    ceo_roundtables: List[str]
    private_dinners: List[str]
    international_conferences: List[str]
    
    # Custom services
    dedicated_research_team: bool
    custom_derivatives: bool
    bespoke_strategies: List[str]
    
    # Lifestyle concierge
    luxury_travel: bool
    art_investments: bool
    real_estate_deals: bool
    
    # Network access
    billionaire_network: bool
    startup_deal_flow: bool
    government_relations: bool