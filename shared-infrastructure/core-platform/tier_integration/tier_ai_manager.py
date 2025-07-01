"""
Tier-AI Integration Manager
Manages AI SDK services across Lite/Pro/Elite/Black tiers with intelligent upselling
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import logging

from app.sdk_manager import GridWorksSDK, ClientConfiguration, ServiceType, IntegrationType
from app.ai_support import SupportTier
from app.ai_intelligence import UserTier as IntelligenceTier

logger = logging.getLogger(__name__)


class UserTier(Enum):
    LITE = "lite"
    PRO = "pro"
    ELITE = "elite"
    BLACK = "black"


class AIServiceQuota:
    """AI service usage quotas by tier"""
    
    TIER_QUOTAS = {
        UserTier.LITE: {
            "support_queries_daily": 5,
            "morning_pulse_access": True,
            "morning_pulse_format": "text_only",
            "trade_ideas": 0,
            "custom_alerts": 0,
            "group_access": "observer",
            "expert_verification": False,
            "whatsapp_delivery": False
        },
        UserTier.PRO: {
            "support_queries_daily": 50,
            "morning_pulse_access": True,
            "morning_pulse_format": "voice_plus_text",
            "trade_ideas": 3,
            "custom_alerts": 10,
            "group_access": "participant", 
            "expert_verification": "can_apply",
            "whatsapp_delivery": True,
            "max_expert_groups": 3
        },
        UserTier.ELITE: {
            "support_queries_daily": "unlimited",
            "morning_pulse_access": True,
            "morning_pulse_format": "personalized_video",
            "trade_ideas": 5,
            "custom_alerts": "unlimited",
            "group_access": "creator",
            "expert_verification": "fast_track",
            "whatsapp_delivery": True,
            "max_expert_groups": "unlimited",
            "revenue_sharing": True,
            "video_support": True
        },
        UserTier.BLACK: {
            "support_queries_daily": "unlimited",
            "morning_pulse_access": True,
            "morning_pulse_format": "institutional_report",
            "trade_ideas": 10,
            "custom_alerts": "unlimited",
            "group_access": "platform_admin",
            "expert_verification": "instant",
            "whatsapp_delivery": True,
            "max_expert_groups": "unlimited", 
            "revenue_sharing": True,
            "video_support": True,
            "dedicated_support": True,
            "institutional_intelligence": True,
            "white_label_access": True
        }
    }


class TierAIManager:
    """Manages AI services integration across user tiers"""
    
    def __init__(self):
        self.tier_sdks = {}  # Cache SDK instances by tier
        self.usage_tracker = {}  # Track daily usage by user
        self.upsell_triggers = UpsellTriggerManager()
    
    async def get_user_ai_config(self, user_tier: UserTier) -> Dict[str, Any]:
        """Get AI configuration for user tier"""
        
        base_quota = AIServiceQuota.TIER_QUOTAS[user_tier]
        
        # Map to SDK configuration
        services = [ServiceType.SUPPORT]  # All tiers get support
        
        if user_tier in [UserTier.PRO, UserTier.ELITE, UserTier.BLACK]:
            services.append(ServiceType.INTELLIGENCE)
        
        if user_tier in [UserTier.ELITE, UserTier.BLACK]:
            services.append(ServiceType.MODERATOR)
        
        return {
            "services": services,
            "quotas": base_quota,
            "rate_limits": self._get_rate_limits(user_tier),
            "features": self._get_tier_features(user_tier)
        }
    
    async def create_user_sdk(self, user_id: str, user_tier: UserTier) -> GridWorksSDK:
        """Create tier-appropriate SDK for user"""
        
        ai_config = await self.get_user_ai_config(user_tier)
        
        client_config = ClientConfiguration(
            client_id=f"user_{user_id}",
            client_name=f"GridWorks {user_tier.value.title()} User",
            api_key=f"user_key_{user_id}",
            services=ai_config["services"],
            integration_type=IntegrationType.REST_API,
            custom_settings=ai_config["features"],
            rate_limits=ai_config["rate_limits"]
        )
        
        sdk = GridWorksSDK(client_config)
        await sdk.initialize_services()
        
        return sdk
    
    async def handle_ai_support_request(
        self, 
        user_id: str, 
        user_tier: UserTier,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle AI support request with tier-specific features"""
        
        # Check quota
        quota_check = await self._check_support_quota(user_id, user_tier)
        if not quota_check["allowed"]:
            return {
                "success": False,
                "error": "quota_exceeded",
                "upsell": await self.upsell_triggers.get_support_upsell(user_tier),
                "quota_reset": quota_check["reset_time"]
            }
        
        # Get SDK
        sdk = await self.create_user_sdk(user_id, user_tier)
        
        # Map tier to support tier
        support_tier_map = {
            UserTier.LITE: SupportTier.LITE,
            UserTier.PRO: SupportTier.PRO, 
            UserTier.ELITE: SupportTier.ELITE,
            UserTier.BLACK: SupportTier.BLACK
        }
        
        # Process request
        response = await sdk.process_request(
            service="support",
            action="query",
            data={
                "user_id": user_id,
                "message": query,
                "user_tier": support_tier_map[user_tier].value,
                "deliver_via_whatsapp": AIServiceQuota.TIER_QUOTAS[user_tier]["whatsapp_delivery"]
            },
            user_context=context
        )
        
        # Track usage
        await self._track_usage(user_id, "support_query")
        
        # Check for upsell triggers
        upsell = await self.upsell_triggers.check_support_upsell(user_id, user_tier)
        if upsell:
            response.data["upsell_offer"] = upsell
        
        return response.data
    
    async def handle_morning_pulse_request(
        self,
        user_id: str,
        user_tier: UserTier
    ) -> Dict[str, Any]:
        """Handle morning pulse request with tier-specific format"""
        
        quota = AIServiceQuota.TIER_QUOTAS[user_tier]
        
        if not quota["morning_pulse_access"]:
            return {
                "success": False,
                "error": "tier_restriction",
                "upsell": await self.upsell_triggers.get_intelligence_upsell(user_tier)
            }
        
        # Get SDK for Pro+ tiers
        if user_tier == UserTier.LITE:
            return await self._get_lite_morning_pulse_teaser(user_id)
        
        sdk = await self.create_user_sdk(user_id, user_tier)
        
        # Map tier to intelligence tier
        intelligence_tier_map = {
            UserTier.PRO: IntelligenceTier.PRO,
            UserTier.ELITE: IntelligenceTier.PRO,  # Elite uses Pro intelligence with enhanced delivery
            UserTier.BLACK: IntelligenceTier.BLACK
        }
        
        response = await sdk.process_request(
            service="intelligence",
            action="morning_pulse",
            data={
                "user_id": user_id,
                "user_tier": intelligence_tier_map[user_tier].value,
                "delivery_channels": self._get_delivery_channels(user_tier),
                "format": quota["morning_pulse_format"]
            }
        )
        
        # Enhance response based on tier
        if user_tier == UserTier.ELITE:
            response.data["personalized_insights"] = await self._add_elite_personalization(user_id, response.data)
        elif user_tier == UserTier.BLACK:
            response.data["institutional_intelligence"] = await self._add_black_institutional_data(response.data)
        
        # Track usage and check upsells
        await self._track_usage(user_id, "morning_pulse")
        upsell = await self.upsell_triggers.check_intelligence_upsell(user_id, user_tier)
        if upsell:
            response.data["upsell_offer"] = upsell
        
        return response.data
    
    async def handle_expert_group_request(
        self,
        user_id: str,
        user_tier: UserTier,
        action: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle expert group interactions based on tier"""
        
        quota = AIServiceQuota.TIER_QUOTAS[user_tier]
        
        # Check tier permissions
        if quota["group_access"] == "observer" and action in ["create_group", "moderate_message"]:
            return {
                "success": False,
                "error": "tier_restriction",
                "message": "Upgrade to Pro to participate in expert groups",
                "upsell": await self.upsell_triggers.get_moderator_upsell(user_tier)
            }
        
        if quota["group_access"] == "participant" and action == "create_group":
            return {
                "success": False,
                "error": "tier_restriction", 
                "message": "Upgrade to Elite to create expert groups and earn revenue",
                "upsell": await self.upsell_triggers.get_moderator_upsell(user_tier)
            }
        
        # Get SDK for Elite+ tiers
        if user_tier in [UserTier.ELITE, UserTier.BLACK]:
            sdk = await self.create_user_sdk(user_id, user_tier)
            
            response = await sdk.process_request(
                service="moderator",
                action=action,
                data=data
            )
            
            # Add tier-specific enhancements
            if user_tier == UserTier.BLACK and action == "create_group":
                response.data["white_label_options"] = await self._get_white_label_options(user_id)
            
            return response.data
        
        # For Pro tier - limited group participation
        if user_tier == UserTier.PRO and action == "view_group":
            return await self._get_pro_group_access(user_id, data)
        
        # Lite tier - read-only access
        return await self._get_lite_group_access(user_id, data)
    
    def _get_rate_limits(self, user_tier: UserTier) -> Dict[str, int]:
        """Get API rate limits by tier"""
        
        rate_limits = {
            UserTier.LITE: {
                "support": 10,      # 10/hour
                "intelligence": 2,  # 2/hour
                "moderator": 0      # No access
            },
            UserTier.PRO: {
                "support": 100,     # 100/hour
                "intelligence": 20, # 20/hour  
                "moderator": 10     # 10/hour
            },
            UserTier.ELITE: {
                "support": 500,     # 500/hour
                "intelligence": 100,# 100/hour
                "moderator": 50     # 50/hour
            },
            UserTier.BLACK: {
                "support": "unlimited",
                "intelligence": "unlimited", 
                "moderator": "unlimited"
            }
        }
        
        return rate_limits[user_tier]
    
    def _get_tier_features(self, user_tier: UserTier) -> Dict[str, Any]:
        """Get tier-specific feature configuration"""
        
        features = {
            UserTier.LITE: {
                "ai_personality": "helpful_basic",
                "response_length": "short",
                "technical_depth": "basic",
                "language_sophistication": "simple"
            },
            UserTier.PRO: {
                "ai_personality": "professional_trader",
                "response_length": "medium",
                "technical_depth": "intermediate",
                "language_sophistication": "professional",
                "voice_synthesis": True
            },
            UserTier.ELITE: {
                "ai_personality": "expert_advisor",
                "response_length": "detailed",
                "technical_depth": "advanced", 
                "language_sophistication": "sophisticated",
                "voice_synthesis": True,
                "video_generation": True,
                "personalization": "high"
            },
            UserTier.BLACK: {
                "ai_personality": "institutional_butler",
                "response_length": "comprehensive",
                "technical_depth": "institutional",
                "language_sophistication": "institutional",
                "voice_synthesis": True,
                "video_generation": True,
                "personalization": "maximum",
                "dedicated_model": True
            }
        }
        
        return features[user_tier]
    
    async def _check_support_quota(self, user_id: str, user_tier: UserTier) -> Dict[str, Any]:
        """Check if user has available support quota"""
        
        quota = AIServiceQuota.TIER_QUOTAS[user_tier]["support_queries_daily"]
        
        if quota == "unlimited":
            return {"allowed": True}
        
        # Check daily usage
        today = datetime.now().strftime("%Y-%m-%d")
        usage_key = f"{user_id}_{today}_support"
        
        current_usage = self.usage_tracker.get(usage_key, 0)
        
        if current_usage >= quota:
            # Calculate reset time (next day)
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            return {
                "allowed": False,
                "current_usage": current_usage,
                "quota": quota,
                "reset_time": tomorrow.isoformat()
            }
        
        return {"allowed": True, "remaining": quota - current_usage}
    
    async def _track_usage(self, user_id: str, service: str):
        """Track daily service usage"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        usage_key = f"{user_id}_{today}_{service}"
        
        self.usage_tracker[usage_key] = self.usage_tracker.get(usage_key, 0) + 1
    
    def _get_delivery_channels(self, user_tier: UserTier) -> List[str]:
        """Get delivery channels based on tier"""
        
        channels = {
            UserTier.LITE: ["app"],
            UserTier.PRO: ["app", "whatsapp", "email"],
            UserTier.ELITE: ["app", "whatsapp", "email", "sms"],
            UserTier.BLACK: ["app", "whatsapp", "email", "sms", "dedicated_app"]
        }
        
        return channels[user_tier]
    
    async def _get_lite_morning_pulse_teaser(self, user_id: str) -> Dict[str, Any]:
        """Get teaser version of morning pulse for Lite tier"""
        
        return {
            "success": True,
            "format": "teaser",
            "content": {
                "summary": "NASDAQ down 1.2%, Oil up 3% - Mixed signals for Indian markets",
                "teaser_insights": [
                    "IT stocks may face pressure from NASDAQ decline",
                    "Energy stocks could benefit from oil rally"
                ],
                "locked_content": {
                    "trade_ideas": 3,
                    "voice_analysis": "30-second detailed analysis",
                    "risk_alerts": 2
                }
            },
            "upsell": {
                "message": "Unlock 3 specific trade ideas + voice analysis",
                "cta": "Upgrade to Pro for ₹999/month",
                "offer": "First week free",
                "value_demo": "Yesterday's Pro trade ideas averaged +2.3% returns"
            }
        }
    
    async def _add_elite_personalization(self, user_id: str, pulse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add Elite-tier personalization to morning pulse"""
        
        # In production, this would analyze user's portfolio and trading history
        return {
            "portfolio_impact_analysis": "Based on your holdings, RELIANCE position may benefit from oil rally",
            "personalized_risk_alerts": ["Your TCS position vulnerable to IT sector weakness"],
            "custom_opportunity_scan": "New breakout detected in HDFC - matches your swing trading style"
        }
    
    async def _add_black_institutional_data(self, pulse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add Black-tier institutional intelligence"""
        
        return {
            "institutional_flows": {
                "fii_activity": "Net selling ₹2,400Cr in cash segment",
                "dii_activity": "Net buying ₹1,800Cr - focused on banking",
                "hedge_fund_positions": "Long bias in IT, Short in realty"
            },
            "insider_trading_alerts": ["Promoter buying detected in 3 mid-cap stocks"],
            "block_deal_intelligence": ["LIC sold 2% stake in XYZ Corp at ₹850/share"],
            "regulatory_updates": ["SEBI circular on F&O position limits effective next week"]
        }


class UpsellTriggerManager:
    """Manages intelligent upsell triggers based on AI usage patterns"""
    
    def __init__(self):
        self.trigger_history = {}  # Track when triggers were shown
    
    async def check_support_upsell(self, user_id: str, user_tier: UserTier) -> Optional[Dict[str, Any]]:
        """Check if support usage should trigger upsell"""
        
        if user_tier == UserTier.BLACK:
            return None  # No upsell for top tier
        
        # Get usage data (simplified - would query database)
        usage_data = await self._get_user_usage_data(user_id)
        
        triggers = {
            UserTier.LITE: {
                "condition": usage_data.get("support_queries_today", 0) >= 5,
                "message": "You've reached your daily AI support limit",
                "offer": "Upgrade to Pro for unlimited queries + voice responses",
                "value": "Pro users get answers in 15 seconds vs 30 seconds"
            },
            UserTier.PRO: {
                "condition": usage_data.get("advanced_queries", 0) > 10,
                "message": "You're asking sophisticated trading questions",
                "offer": "Upgrade to Elite for personal AI trading butler",
                "value": "Elite AI provides portfolio-specific advice"
            },
            UserTier.ELITE: {
                "condition": usage_data.get("institutional_queries", 0) > 5,
                "message": "You need institutional-grade support",
                "offer": "Upgrade to Black for dedicated relationship manager",
                "value": "Black tier gets 1-second response time + human backup"
            }
        }
        
        trigger = triggers.get(user_tier)
        if trigger and trigger["condition"]:
            return await self._create_upsell_offer(user_tier, "support", trigger)
        
        return None
    
    async def check_intelligence_upsell(self, user_id: str, user_tier: UserTier) -> Optional[Dict[str, Any]]:
        """Check if intelligence usage should trigger upsell"""
        
        usage_data = await self._get_user_usage_data(user_id)
        
        triggers = {
            UserTier.LITE: {
                "condition": usage_data.get("pulse_opens", 0) > 7,  # Opens pulse 7+ times
                "message": "You're actively using morning intelligence",
                "offer": "Upgrade to Pro for voice notes + specific trade ideas",
                "value": "Pro trade ideas averaged +15% returns last month"
            },
            UserTier.PRO: {
                "condition": usage_data.get("trade_idea_clicks", 0) > 20,
                "message": "You're executing our trade ideas consistently",
                "offer": "Upgrade to Elite for personalized portfolio optimization",
                "value": "Elite users get 5 daily ideas vs 3, plus video analysis"
            },
            UserTier.ELITE: {
                "condition": usage_data.get("portfolio_value", 0) > 5000000,  # ₹50L+ portfolio
                "message": "Your portfolio qualifies for institutional intelligence",
                "offer": "Upgrade to Black for institutional research access",
                "value": "Access to FII flows, block deals, insider intelligence"
            }
        }
        
        trigger = triggers.get(user_tier)
        if trigger and trigger["condition"]:
            return await self._create_upsell_offer(user_tier, "intelligence", trigger)
        
        return None
    
    async def check_moderator_upsell(self, user_id: str, user_tier: UserTier) -> Optional[Dict[str, Any]]:
        """Check if group activity should trigger upsell"""
        
        usage_data = await self._get_user_usage_data(user_id)
        
        triggers = {
            UserTier.LITE: {
                "condition": usage_data.get("group_observation_time", 0) > 30,  # 30+ minutes observing
                "message": "You're actively following expert groups",
                "offer": "Upgrade to Pro to participate in discussions",
                "value": "Pro users can ask questions and get expert responses"
            },
            UserTier.PRO: {
                "condition": usage_data.get("group_subscriptions", 0) >= 2,  # Paying for 2+ groups
                "message": "You're investing in expert knowledge",
                "offer": "Upgrade to Elite to create your own expert group",
                "value": "Elite experts earn average ₹25,000/month"
            },
            UserTier.ELITE: {
                "condition": usage_data.get("expert_revenue", 0) > 15000,  # Earning ₹15K+/month
                "message": "You're successfully monetizing your expertise",
                "offer": "Upgrade to Black for unlimited earning potential",
                "value": "Black experts can create institutional groups with higher fees"
            }
        }
        
        trigger = triggers.get(user_tier)
        if trigger and trigger["condition"]:
            return await self._create_upsell_offer(user_tier, "moderator", trigger)
        
        return None
    
    async def get_support_upsell(self, user_tier: UserTier) -> Dict[str, Any]:
        """Get generic support upsell for quota exceeded"""
        
        upsells = {
            UserTier.LITE: {
                "title": "Upgrade to Pro for Unlimited AI Support",
                "features": [
                    "Unlimited daily queries (vs 5 current limit)",
                    "15-second response time (vs 30 seconds)",
                    "Voice responses via WhatsApp",
                    "Advanced portfolio analysis"
                ],
                "price": "₹999/month",
                "cta": "Upgrade Now",
                "trial": "7 days free trial"
            }
        }
        
        return upsells.get(user_tier, {})
    
    async def get_intelligence_upsell(self, user_tier: UserTier) -> Dict[str, Any]:
        """Get intelligence service upsell"""
        
        upsells = {
            UserTier.LITE: {
                "title": "Unlock Full Morning Intelligence",
                "features": [
                    "30-second voice analysis every morning",
                    "3 specific trade ideas with entry/exit points",
                    "WhatsApp delivery at 7:30 AM",
                    "Backtesting links for each idea"
                ],
                "price": "₹999/month",
                "cta": "Get Voice Intelligence",
                "demo": "Listen to sample voice note"
            }
        }
        
        return upsells.get(user_tier, {})
    
    async def get_moderator_upsell(self, user_tier: UserTier) -> Dict[str, Any]:
        """Get moderator/group upsell"""
        
        upsells = {
            UserTier.LITE: {
                "title": "Join Expert Group Discussions",
                "features": [
                    "Participate in expert group chats",
                    "Ask questions to verified experts",
                    "Access to 3 premium groups",
                    "Real-time call notifications"
                ],
                "price": "₹999/month",
                "cta": "Join Groups"
            },
            UserTier.PRO: {
                "title": "Create Your Expert Group & Earn",
                "features": [
                    "Create unlimited expert groups",
                    "Earn up to ₹50,000/month",
                    "AI-powered group moderation",
                    "Performance tracking dashboard"
                ],
                "price": "₹4,999/month",
                "cta": "Become Expert",
                "earning_potential": "Top experts earn ₹25K+/month"
            }
        }
        
        return upsells.get(user_tier, {})
    
    async def _create_upsell_offer(
        self, 
        current_tier: UserTier, 
        service: str, 
        trigger: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create personalized upsell offer"""
        
        # Check if we've shown this trigger recently
        trigger_key = f"{current_tier.value}_{service}_upsell"
        last_shown = self.trigger_history.get(trigger_key)
        
        if last_shown and (datetime.now() - last_shown).days < 3:
            return None  # Don't spam upsells
        
        # Record trigger
        self.trigger_history[trigger_key] = datetime.now()
        
        return {
            "trigger_type": "ai_usage_based",
            "current_tier": current_tier.value,
            "service": service,
            "message": trigger["message"],
            "offer": trigger["offer"],
            "value_proposition": trigger["value"],
            "urgency": "Limited time: First month 50% off",
            "social_proof": await self._get_social_proof(current_tier),
            "cta": f"Upgrade to {self._get_next_tier(current_tier).value.title()}"
        }
    
    def _get_next_tier(self, current_tier: UserTier) -> UserTier:
        """Get next tier for upsell"""
        
        tier_progression = {
            UserTier.LITE: UserTier.PRO,
            UserTier.PRO: UserTier.ELITE,
            UserTier.ELITE: UserTier.BLACK
        }
        
        return tier_progression.get(current_tier, current_tier)
    
    async def _get_social_proof(self, current_tier: UserTier) -> str:
        """Get social proof for upsell"""
        
        proofs = {
            UserTier.LITE: "Join 100,000+ Pro users who never miss a trade opportunity",
            UserTier.PRO: "Elite users create 3x more profitable strategies",
            UserTier.ELITE: "Black users access institutional-grade intelligence"
        }
        
        return proofs.get(current_tier, "Upgrade for better trading results")
    
    async def _get_user_usage_data(self, user_id: str) -> Dict[str, Any]:
        """Get user usage data for trigger evaluation"""
        
        # In production, this would query the database
        # For now, return mock data
        return {
            "support_queries_today": 3,
            "pulse_opens": 5,
            "trade_idea_clicks": 12,
            "group_observation_time": 45,
            "group_subscriptions": 1,
            "expert_revenue": 8000,
            "portfolio_value": 2500000,
            "advanced_queries": 15,
            "institutional_queries": 3
        }