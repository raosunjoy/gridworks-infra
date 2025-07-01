"""
GridWorks AI Support Data Models
Universal data structures for support system
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid


class SupportTier(Enum):
    """User tier enumeration"""
    LITE = "LITE"
    PRO = "PRO"
    ELITE = "ELITE"
    BLACK = "BLACK"


class MessageType(Enum):
    """Message type enumeration"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    DOCUMENT = "document"


class QueryCategory(Enum):
    """Universal query categories"""
    ORDER_MANAGEMENT = "order_management"
    PORTFOLIO_QUERIES = "portfolio_queries"
    PAYMENT_ISSUES = "payment_issues"
    KYC_COMPLIANCE = "kyc_compliance"
    TECHNICAL_SUPPORT = "technical_support"
    MARKET_QUERIES = "market_queries"
    COMPLAINT = "complaint"
    GENERAL_INQUIRY = "general_inquiry"


class UrgencyLevel(Enum):
    """Query urgency levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class SupportMessage:
    """Universal support message structure"""
    id: str
    user_id: str
    phone: str
    message: str
    message_type: MessageType
    language: str
    timestamp: datetime
    user_tier: SupportTier
    priority: int
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class UniversalQuery:
    """Universal query classification result"""
    category: QueryCategory
    intent: str
    urgency: UrgencyLevel
    complexity: int  # 1-5 scale
    language: str
    entities: Dict[str, Any]
    confidence: float
    keywords: List[str]


@dataclass
class TierConfig:
    """Configuration for tier-specific support experience"""
    tier: SupportTier
    max_ai_response_time: float  # seconds
    human_escalation_threshold: float  # confidence threshold
    max_human_wait_time: int  # minutes
    features: List[str]
    agent_tier: str
    personality_tone: str
    max_response_length: int
    visual_style: Dict[str, Any]


@dataclass
class SupportResponse:
    """Universal support response structure"""
    message: str
    actions: List[Dict[str, Any]]
    tier_features: List[str]
    escalate: bool
    confidence: float
    response_time: float
    zk_proof: Optional[Dict[str, Any]] = None
    visual_enhancements: Optional[Dict[str, Any]] = None
    follow_up: Optional[str] = None


@dataclass
class UserContext:
    """User context for personalized support"""
    user_id: str
    tier: SupportTier
    name: str
    portfolio_value: float
    recent_orders: List[Dict[str, Any]]
    balance: float
    kyc_status: str
    preferred_language: str
    trading_history: Dict[str, Any]
    risk_profile: str
    
    
@dataclass
class AgentInfo:
    """Human agent information"""
    agent_id: str
    name: str
    tier_access: List[SupportTier]
    languages: List[str]
    specializations: List[str]
    current_load: int
    max_concurrent: int
    status: str  # available, busy, offline
    rating: float


@dataclass
class EscalationTicket:
    """Human escalation ticket"""
    ticket_id: str
    user: SupportMessage
    ai_context: Dict[str, Any]
    assigned_agent: Optional[AgentInfo]
    priority: int
    created_at: datetime
    estimated_resolution: datetime
    status: str  # queued, assigned, in_progress, resolved