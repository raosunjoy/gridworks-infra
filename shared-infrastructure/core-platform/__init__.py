"""
GridWorks AI Platform
Multi-AI SDK Suite for trading intelligence and automation
"""

# Core SDK Manager
from .sdk_manager import (
    GridWorksSDK,
    WhatsAppSDK,
    BrokerSDK, 
    TradingGroupSDK,
    create_whatsapp_sdk,
    create_broker_sdk,
    create_trading_group_sdk,
    create_enterprise_sdk
)

# AI Services
from .ai_support import UniversalAISupport
from .ai_intelligence import AIIntelligenceService
from .ai_moderator import AIModerator, ExpertVerificationEngine

__version__ = "1.0.0"
__author__ = "GridWorks AI Team"

__all__ = [
    # Core SDK
    'GridWorksSDK',
    'WhatsAppSDK',
    'BrokerSDK',
    'TradingGroupSDK',
    
    # Factory Functions
    'create_whatsapp_sdk',
    'create_broker_sdk', 
    'create_trading_group_sdk',
    'create_enterprise_sdk',
    
    # AI Services
    'UniversalAISupport',
    'AIIntelligenceService',
    'AIModerator',
    'ExpertVerificationEngine'
]