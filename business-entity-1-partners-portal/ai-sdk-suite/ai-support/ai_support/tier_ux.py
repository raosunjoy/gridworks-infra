"""
Tier-Specific UX Renderer
Transform universal AI responses into tier-differentiated experiences
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import SupportMessage, SupportResponse, SupportTier, UserContext


class TierUXRenderer:
    """Render tier-specific UX experiences from universal AI responses"""
    
    def __init__(self):
        self.tier_personalities = self._load_tier_personalities()
        self.visual_styles = self._load_visual_styles()
        self.interaction_patterns = self._load_interaction_patterns()
        
    def _load_tier_personalities(self) -> Dict[SupportTier, Dict[str, Any]]:
        """Load tier-specific personality configurations"""
        
        return {
            SupportTier.LITE: {
                "tone": "friendly_helpful",
                "emoji_usage": "basic",  # 😊💳📈
                "greeting": "Hi!",
                "signature": "GridWorks Team",
                "max_emojis": 2,
                "response_style": "simple_clear"
            },
            
            SupportTier.PRO: {
                "tone": "professional_smart", 
                "emoji_usage": "strategic",  # ⚡📊🎤
                "greeting": "⚡ PRO Support",
                "signature": "Your PRO Support Team",
                "max_emojis": 3,
                "response_style": "detailed_actionable"
            },
            
            SupportTier.ELITE: {
                "tone": "expert_advisor",
                "emoji_usage": "sophisticated",  # 👑📹🎯
                "greeting": "Good {time_of_day}, {name}",
                "signature": "- {name}, Your Elite Advisor",
                "max_emojis": 2,
                "response_style": "analytical_personal"
            },
            
            SupportTier.BLACK: {
                "tone": "concierge_butler",
                "emoji_usage": "exclusive",  # ◆🎩🏛️
                "greeting": "At your service, Mr./Ms. {surname}",
                "signature": "- {name}, Your Market Butler",
                "max_emojis": 1,
                "response_style": "white_glove_luxury"
            }
        }
    
    def _load_visual_styles(self) -> Dict[SupportTier, Dict[str, Any]]:
        """Load tier-specific visual styling"""
        
        return {
            SupportTier.LITE: {
                "badge": "",
                "color_scheme": "blue",
                "header_style": "simple",
                "message_format": "plain_text",
                "emoji_set": ["😊", "💳", "📈", "🤝", "👍", "📱"]
            },
            
            SupportTier.PRO: {
                "badge": "⚡ PRO",
                "color_scheme": "blue_gold",
                "header_style": "branded",
                "message_format": "enhanced_formatting",
                "emoji_set": ["⚡", "📊", "🎤", "🚀", "💡", "📈"]
            },
            
            SupportTier.ELITE: {
                "badge": "👑 ELITE",
                "color_scheme": "platinum_gold",
                "header_style": "executive",
                "message_format": "executive_brief",
                "emoji_set": ["👑", "📹", "🎯", "📊", "💎", "🏆"]
            },
            
            SupportTier.BLACK: {
                "badge": "◆ BLACK",
                "color_scheme": "black_gold",
                "header_style": "luxury_concierge",
                "message_format": "concierge_communication",
                "emoji_set": ["◆", "🎩", "🏛️", "💼", "🔒", "⚡"]
            }
        }
    
    def _load_interaction_patterns(self) -> Dict[SupportTier, Dict[str, Any]]:
        """Load tier-specific interaction patterns"""
        
        return {
            SupportTier.LITE: {
                "response_time_message": "Getting your answer...",
                "quick_actions": ["Help", "Retry", "Contact"],
                "upgrade_hints": True,
                "follow_up_style": "simple_check_in"
            },
            
            SupportTier.PRO: {
                "response_time_message": "⚡ PRO analysis in progress...",
                "quick_actions": ["🚀 Smart Fix", "🎤 Voice Help", "📊 Analysis", "⚡ Priority"],
                "upgrade_hints": True,
                "follow_up_style": "professional_follow_up"
            },
            
            SupportTier.ELITE: {
                "response_time_message": "👑 Expert analysis in preparation...",
                "quick_actions": ["🎯 Execute", "📹 Consult", "📊 Deep Analysis", "🏆 Expert"],
                "upgrade_hints": True,
                "follow_up_style": "advisor_check_in"
            },
            
            SupportTier.BLACK: {
                "response_time_message": "◆ Butler crafting your solution...",
                "quick_actions": ["◆ Execute", "📞 Butler Call", "🏛️ Concierge", "⚡ Auto-Fix"],
                "upgrade_hints": False,
                "follow_up_style": "white_glove_service"
            }
        }
    
    async def render_tier_response(
        self,
        base_response: SupportResponse,
        message: SupportMessage,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Transform universal response into tier-specific experience"""
        
        tier = message.user_tier
        personality = self.tier_personalities[tier]
        visual_style = self.visual_styles[tier]
        interactions = self.interaction_patterns[tier]
        
        # Generate tier-specific greeting
        greeting = await self._generate_greeting(tier, user_context)
        
        # Enhance message with tier personality
        enhanced_message = await self._enhance_message(
            base_response.message, 
            tier, 
            personality, 
            visual_style
        )
        
        # Generate tier-specific actions
        tier_actions = await self._generate_tier_actions(
            base_response.actions,
            tier,
            interactions
        )
        
        # Add tier features and upgrades
        tier_features = await self._generate_tier_features(tier, base_response)
        upgrade_hints = await self._generate_upgrade_hints(tier, interactions)
        
        # Create final response
        return {
            "greeting": greeting,
            "message": enhanced_message,
            "actions": tier_actions,
            "tier_features": tier_features,
            "upgrade_hints": upgrade_hints,
            "visual_style": visual_style,
            "signature": await self._generate_signature(tier, personality, user_context),
            "response_metadata": {
                "tier": tier.value,
                "response_time": base_response.response_time,
                "confidence": base_response.confidence,
                "escalate": base_response.escalate
            }
        }
    
    async def _generate_greeting(self, tier: SupportTier, user_context: UserContext) -> str:
        """Generate tier-appropriate greeting"""
        
        personality = self.tier_personalities[tier]
        current_hour = datetime.now().hour
        
        if tier == SupportTier.LITE:
            return personality["greeting"]
            
        elif tier == SupportTier.PRO:
            return personality["greeting"]
            
        elif tier == SupportTier.ELITE:
            time_of_day = self._get_time_of_day(current_hour)
            return personality["greeting"].format(
                time_of_day=time_of_day,
                name=user_context.name.split()[0]  # First name
            )
            
        elif tier == SupportTier.BLACK:
            surname = user_context.name.split()[-1] if user_context.name else "Valued Client"
            return personality["greeting"].format(surname=surname)
    
    def _get_time_of_day(self, hour: int) -> str:
        """Get appropriate time of day greeting"""
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    async def _enhance_message(
        self,
        base_message: str,
        tier: SupportTier,
        personality: Dict[str, Any],
        visual_style: Dict[str, Any]
    ) -> str:
        """Enhance message with tier-specific styling and personality"""
        
        if tier == SupportTier.LITE:
            return await self._render_lite_message(base_message, visual_style)
            
        elif tier == SupportTier.PRO:
            return await self._render_pro_message(base_message, visual_style)
            
        elif tier == SupportTier.ELITE:
            return await self._render_elite_message(base_message, visual_style)
            
        elif tier == SupportTier.BLACK:
            return await self._render_black_message(base_message, visual_style)
    
    async def _render_lite_message(self, message: str, style: Dict[str, Any]) -> str:
        """Render LITE tier message: Simple and clear"""
        
        # Add 1-2 relevant emojis
        if "order" in message.lower():
            message = message.replace("order", "order 📋")
        if "money" in message.lower():
            message = message.replace("money", "money 💳")
            
        return message
    
    async def _render_pro_message(self, message: str, style: Dict[str, Any]) -> str:
        """Render PRO tier message: Professional with strategic emojis"""
        
        # Add PRO formatting
        enhanced = f"⚡ **PRO ANALYSIS**\n\n{message}"
        
        # Add strategic emojis
        enhanced = enhanced.replace("analysis", "analysis 📊")
        enhanced = enhanced.replace("solution", "solution 🚀")
        
        return enhanced
    
    async def _render_elite_message(self, message: str, style: Dict[str, Any]) -> str:
        """Render ELITE tier message: Executive brief style"""
        
        # Add ELITE header
        enhanced = f"👑 **ELITE ADVISORY**\n\n"
        
        # Structure as executive brief
        sections = message.split('. ')
        if len(sections) > 1:
            enhanced += f"🎯 **Executive Summary**: {sections[0]}\n\n"
            enhanced += f"📊 **Detailed Analysis**: {'. '.join(sections[1:])}"
        else:
            enhanced += message
            
        return enhanced
    
    async def _render_black_message(self, message: str, style: Dict[str, Any]) -> str:
        """Render BLACK tier message: Luxury concierge style"""
        
        # Add BLACK concierge header
        enhanced = f"◆ **BLACK CONCIERGE**\n\n"
        
        # Add butler language patterns
        if "issue" in message.lower():
            enhanced += "🎩 **Immediate Resolution**\n\n"
        
        enhanced += message
        
        # Add anticipatory service
        enhanced += "\n\n💼 **Anticipatory Service**: I've also prepared market insights for your review."
        
        return enhanced
    
    async def _generate_tier_actions(
        self,
        base_actions: List[Dict[str, Any]],
        tier: SupportTier,
        interactions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate tier-specific action buttons"""
        
        tier_actions = []
        
        # Add tier-specific quick actions
        quick_actions = interactions["quick_actions"]
        
        for action in quick_actions:
            tier_actions.append({
                "text": action,
                "action": action.lower().replace(" ", "_").replace("🚀", "").replace("⚡", "").strip(),
                "tier": tier.value
            })
        
        # Enhance base actions with tier styling
        for action in base_actions:
            enhanced_action = action.copy()
            enhanced_action["tier_styled"] = True
            tier_actions.append(enhanced_action)
        
        return tier_actions
    
    async def _generate_tier_features(
        self,
        tier: SupportTier,
        response: SupportResponse
    ) -> List[str]:
        """Generate tier-specific feature highlights"""
        
        features = {
            SupportTier.LITE: [
                "24/7 AI Support",
                "11 Language Support",
                "WhatsApp Native"
            ],
            
            SupportTier.PRO: [
                "⚡ Priority Support",
                "🎤 Voice Support Available", 
                "📊 Smart Analytics",
                "🚀 <15 Second Responses"
            ],
            
            SupportTier.ELITE: [
                "👑 Expert Advisor Access",
                "📹 Video Consultation Available",
                "🎯 Personalized Analysis",
                "📊 Portfolio Impact Assessment"
            ],
            
            SupportTier.BLACK: [
                "◆ Dedicated Market Butler",
                "⚡ Instant Resolution Service",
                "🏛️ White-Glove Treatment",
                "💼 Proactive Market Intelligence"
            ]
        }
        
        return features.get(tier, [])
    
    async def _generate_upgrade_hints(
        self,
        tier: SupportTier,
        interactions: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate subtle upgrade hints for lower tiers"""
        
        if not interactions["upgrade_hints"]:
            return None
            
        upgrade_messages = {
            SupportTier.LITE: {
                "message": "⚡ PRO users get voice support for complex issues like this",
                "cta": "Upgrade to PRO for ₹99/month",
                "target_tier": "PRO"
            },
            
            SupportTier.PRO: {
                "message": "👑 ELITE users get personal advisor consultation for portfolio optimization",
                "cta": "Experience ELITE advisory",
                "target_tier": "ELITE"
            },
            
            SupportTier.ELITE: {
                "message": "◆ BLACK members get proactive market butler service during volatile periods",
                "cta": "Exclusive BLACK invitation",
                "target_tier": "BLACK"
            }
        }
        
        return upgrade_messages.get(tier)
    
    async def _generate_signature(
        self,
        tier: SupportTier,
        personality: Dict[str, Any],
        user_context: UserContext
    ) -> str:
        """Generate tier-appropriate signature"""
        
        signature_template = personality["signature"]
        
        if tier in [SupportTier.ELITE, SupportTier.BLACK]:
            # Personalized signatures for premium tiers
            agent_names = {
                SupportTier.ELITE: "Priya Sharma",
                SupportTier.BLACK: "Arjun Mehta"
            }
            
            return signature_template.format(name=agent_names[tier])
        
        return signature_template


class WhatsAppUXFormatter:
    """Format tier-specific responses for WhatsApp delivery"""
    
    @staticmethod
    async def format_for_whatsapp(tier_response: Dict[str, Any]) -> str:
        """Convert tier response to WhatsApp-optimized format"""
        
        tier = tier_response["response_metadata"]["tier"]
        
        if tier == "LITE":
            return WhatsAppUXFormatter._format_lite_whatsapp(tier_response)
        elif tier == "PRO":
            return WhatsAppUXFormatter._format_pro_whatsapp(tier_response)
        elif tier == "ELITE":
            return WhatsAppUXFormatter._format_elite_whatsapp(tier_response)
        elif tier == "BLACK":
            return WhatsAppUXFormatter._format_black_whatsapp(tier_response)
    
    @staticmethod
    def _format_lite_whatsapp(response: Dict[str, Any]) -> str:
        """Format LITE response for WhatsApp"""
        
        formatted = f"{response['message']}\n\n"
        
        # Add simple action buttons
        actions = response['actions'][:2]  # Limit to 2 actions for simplicity
        for action in actions:
            formatted += f"• {action['text']}\n"
        
        if response.get('upgrade_hints'):
            formatted += f"\n💡 {response['upgrade_hints']['message']}"
        
        formatted += f"\n\n{response['signature']}"
        
        return formatted.strip()
    
    @staticmethod
    def _format_pro_whatsapp(response: Dict[str, Any]) -> str:
        """Format PRO response for WhatsApp"""
        
        formatted = f"{response['greeting']}\n\n"
        formatted += f"{response['message']}\n\n"
        
        # Add PRO action buttons
        formatted += "🚀 **Quick Actions**:\n"
        for action in response['actions'][:4]:
            formatted += f"• {action['text']}\n"
        
        # Add tier features
        formatted += f"\n⚡ **PRO Features Active**:\n"
        for feature in response['tier_features'][:2]:
            formatted += f"• {feature}\n"
        
        formatted += f"\n{response['signature']}"
        
        return formatted.strip()
    
    @staticmethod
    def _format_elite_whatsapp(response: Dict[str, Any]) -> str:
        """Format ELITE response for WhatsApp"""
        
        formatted = f"{response['greeting']}\n\n"
        formatted += f"{response['message']}\n\n"
        
        # Add executive actions
        formatted += "🎯 **Strategic Options**:\n"
        for action in response['actions']:
            formatted += f"• {action['text']}\n"
        
        # Add ELITE features
        formatted += f"\n👑 **ELITE Services**:\n"
        for feature in response['tier_features']:
            formatted += f"• {feature}\n"
        
        formatted += f"\n{response['signature']}"
        
        return formatted.strip()
    
    @staticmethod
    def _format_black_whatsapp(response: Dict[str, Any]) -> str:
        """Format BLACK response for WhatsApp"""
        
        formatted = f"{response['greeting']}\n\n"
        formatted += f"{response['message']}\n\n"
        
        # Add concierge actions
        formatted += "◆ **Concierge Services**:\n"
        for action in response['actions']:
            formatted += f"• {action['text']}\n"
        
        # Add anticipatory service note
        if "anticipatory" in response['message'].lower():
            formatted += f"\n💼 **Butler Notes**: Continuous monitoring active\n"
        
        formatted += f"\n{response['signature']}"
        
        return formatted.strip()