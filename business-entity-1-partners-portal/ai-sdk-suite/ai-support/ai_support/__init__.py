"""
GridWorks AI Support Engine
Universal AI support with tier-specific UX differentiation
"""

from .universal_engine import UniversalAISupport
from .tier_ux import TierUXRenderer  
from .whatsapp_handler import WhatsAppSupportHandler
from .escalation_system import EscalationSystem
from .zk_proof_engine import ZKSupportProof

__all__ = [
    'UniversalAISupport',
    'TierUXRenderer', 
    'WhatsAppSupportHandler',
    'EscalationSystem',
    'ZKSupportProof'
]

__version__ = '1.0.0'