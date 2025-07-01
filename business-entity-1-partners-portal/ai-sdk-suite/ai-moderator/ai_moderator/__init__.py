"""
GridWorks AI Moderator Service
Community-as-a-Service for trading groups with expert verification and intelligent moderation
"""

from .moderator_engine import AIModerator, GroupManager
from .expert_verification import ExpertVerificationEngine, ExpertProfileManager
from .community_analytics import CommunityAnalytics
from .reputation_system import ReputationEngine

__all__ = [
    'AIModerator',
    'GroupManager',
    'ExpertVerificationEngine',
    'ExpertProfileManager',
    'CommunityAnalytics',
    'ReputationEngine'
]

__version__ = '1.0.0'