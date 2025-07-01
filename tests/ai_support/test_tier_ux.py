"""
TradeMate Tier UX System Test Suite
Testing tier-specific UX rendering and WhatsApp formatting
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from app.ai_support.tier_ux import TierUXRenderer, WhatsAppUXFormatter, TierConfig
from app.ai_support.models import SupportResponse, SupportMessage, SupportTier, UserContext, MessageType


class TestTierUXRenderer:
    """Test suite for tier-specific UX rendering"""
    
    @pytest.fixture
    def ux_renderer(self):
        """Initialize UX renderer"""
        return TierUXRenderer()
    
    @pytest.fixture
    def sample_ai_response(self):
        """Create sample AI response"""
        return SupportResponse(
            message="Your trading order has been processed successfully.",
            confidence=0.92,
            escalate=False,
            category="order_management",
            suggested_actions=["check_portfolio", "view_order_history"],
            response_time=1.8
        )
    
    @pytest.fixture
    def lite_tier_user(self):
        """Create LITE tier user context"""
        return UserContext(
            user_id="lite_user_001",
            tier=SupportTier.LITE,
            name="Anjali Singh",
            portfolio_value=75000,
            recent_orders=[{"id": "LT001", "symbol": "SBI", "quantity": 10}],
            balance=25000,
            kyc_status="basic",
            preferred_language="hi",
            trading_history={"total_trades": 15, "success_rate": 88},
            risk_profile="conservative"
        )
    
    @pytest.fixture
    def pro_tier_user(self):
        """Create PRO tier user context"""
        return UserContext(
            user_id="pro_user_001",
            tier=SupportTier.PRO,
            name="Rohit Sharma",
            portfolio_value=2500000,
            recent_orders=[{"id": "PR001", "symbol": "TCS", "quantity": 100}],
            balance=500000,
            kyc_status="verified",
            preferred_language="en",
            trading_history={"total_trades": 250, "success_rate": 94},
            risk_profile="moderate"
        )
    
    @pytest.fixture
    def elite_tier_user(self):
        """Create ELITE tier user context"""
        return UserContext(
            user_id="elite_user_001",
            tier=SupportTier.ELITE,
            name="Priya Mehta",
            portfolio_value=15000000,
            recent_orders=[{"id": "EL001", "symbol": "RELIANCE", "quantity": 500}],
            balance=3000000,
            kyc_status="premium",
            preferred_language="en",
            trading_history={"total_trades": 800, "success_rate": 97},
            risk_profile="aggressive"
        )
    
    @pytest.fixture
    def black_tier_user(self):
        """Create BLACK tier user context"""
        return UserContext(
            user_id="black_user_001",
            tier=SupportTier.BLACK,
            name="Mukesh Ambani",
            portfolio_value=500000000000,
            recent_orders=[{"id": "BL001", "symbol": "RELIANCE", "quantity": 100000}],
            balance=50000000000,
            kyc_status="ultra_premium",
            preferred_language="en",
            trading_history={"total_trades": 2500, "success_rate": 99.8},
            risk_profile="ultra_aggressive"
        )
    
    @pytest.mark.asyncio
    async def test_ux_renderer_initialization(self, ux_renderer):
        """Test UX renderer initializes with all tier configurations"""
        assert len(ux_renderer.tier_configs) == 4  # LITE, PRO, ELITE, BLACK
        assert SupportTier.LITE in ux_renderer.tier_configs
        assert SupportTier.PRO in ux_renderer.tier_configs
        assert SupportTier.ELITE in ux_renderer.tier_configs
        assert SupportTier.BLACK in ux_renderer.tier_configs
    
    @pytest.mark.asyncio
    async def test_lite_tier_ux_rendering(self, ux_renderer, sample_ai_response, lite_tier_user):
        """Test LITE tier UX rendering - simple and clear"""
        support_message = SupportMessage(
            id="LT_MSG_001",
            user_id=lite_tier_user.user_id,
            phone="+919876543210",
            message="SBI order status check karna hai",
            message_type=MessageType.TEXT,
            language="hi",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.LITE,
            priority=2
        )
        
        rendered_response = await ux_renderer.render_tier_response(
            sample_ai_response, support_message, lite_tier_user
        )
        
        assert rendered_response["tier"] == "LITE"
        assert rendered_response["style"] == "simple_clear"
        # Should have basic emojis for LITE tier
        assert any(emoji in rendered_response["message"] for emoji in ["😊", "💳", "📈"])
        assert "Anjali" in rendered_response["greeting"]
        assert len(rendered_response["quick_actions"]) <= 3  # Limited actions for LITE
    
    @pytest.mark.asyncio
    async def test_pro_tier_ux_rendering(self, ux_renderer, sample_ai_response, pro_tier_user):
        """Test PRO tier UX rendering - professional and smart"""
        support_message = SupportMessage(
            id="PR_MSG_001",
            user_id=pro_tier_user.user_id,
            phone="+919876543211",
            message="TCS order execution analysis needed",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.PRO,
            priority=3
        )
        
        rendered_response = await ux_renderer.render_tier_response(
            sample_ai_response, support_message, pro_tier_user
        )
        
        assert rendered_response["tier"] == "PRO"
        assert rendered_response["style"] == "professional_smart"
        # Should have strategic emojis for PRO tier
        assert any(emoji in rendered_response["message"] for emoji in ["⚡", "📊", "🎤"])
        assert "Rohit" in rendered_response["greeting"]
        assert len(rendered_response["quick_actions"]) <= 5  # More actions for PRO
        assert "upgrade_hint" in rendered_response  # Should suggest ELITE upgrade
    
    @pytest.mark.asyncio
    async def test_elite_tier_ux_rendering(self, ux_renderer, sample_ai_response, elite_tier_user):
        """Test ELITE tier UX rendering - sophisticated and personal"""
        support_message = SupportMessage(
            id="EL_MSG_001",
            user_id=elite_tier_user.user_id,
            phone="+919876543212",
            message="Executive brief on RELIANCE position required",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.ELITE,
            priority=4
        )
        
        rendered_response = await ux_renderer.render_tier_response(
            sample_ai_response, support_message, elite_tier_user
        )
        
        assert rendered_response["tier"] == "ELITE"
        assert rendered_response["style"] == "sophisticated_personal"
        # Should have executive emojis for ELITE tier
        assert any(emoji in rendered_response["message"] for emoji in ["👑", "📹", "🎯"])
        assert "Ms. Priya" in rendered_response["greeting"]
        assert "executive" in rendered_response["message"].lower()
        assert len(rendered_response["quick_actions"]) <= 7  # Comprehensive actions
    
    @pytest.mark.asyncio
    async def test_black_tier_ux_rendering(self, ux_renderer, sample_ai_response, black_tier_user):
        """Test BLACK tier UX rendering - luxury concierge level"""
        support_message = SupportMessage(
            id="BL_MSG_001",
            user_id=black_tier_user.user_id,
            phone="+919876543213",
            message="Immediate assistance required for ₹385 crore RELIANCE transaction",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.BLACK,
            priority=5
        )
        
        rendered_response = await ux_renderer.render_tier_response(
            sample_ai_response, support_message, black_tier_user
        )
        
        assert rendered_response["tier"] == "BLACK"
        assert rendered_response["style"] == "luxury_concierge"
        # Should have exclusive emojis for BLACK tier
        assert any(emoji in rendered_response["message"] for emoji in ["◆", "🎩", "🏛️"])
        assert "Mr. Mukesh" in rendered_response["greeting"]
        assert any(word in rendered_response["message"].lower() for word in ["concierge", "exclusive", "priority"])
        assert "butler_connection" in rendered_response  # Should offer butler connection
        assert len(rendered_response["quick_actions"]) >= 8  # Comprehensive luxury actions
    
    @pytest.mark.asyncio
    async def test_tier_specific_greeting_generation(self, ux_renderer):
        """Test tier-specific greeting generation"""
        test_cases = [
            (SupportTier.LITE, "Rajesh", "नमस्ते Rajesh! 😊"),
            (SupportTier.PRO, "Priya", "Hello Priya ⚡"),
            (SupportTier.ELITE, "Gautam", "Good day, Mr. Gautam 👑"),
            (SupportTier.BLACK, "Mukesh", "Greetings, Mr. Mukesh ◆")
        ]
        
        for tier, name, expected_style in test_cases:
            greeting = await ux_renderer._generate_tier_greeting(tier, name, "en")
            assert name in greeting
            # Should match the expected tier style
            if tier == SupportTier.LITE:
                assert "😊" in greeting or "नमस्ते" in greeting
            elif tier == SupportTier.PRO:
                assert "⚡" in greeting or "Hello" in greeting
            elif tier == SupportTier.ELITE:
                assert "👑" in greeting or "Mr." in greeting
            elif tier == SupportTier.BLACK:
                assert "◆" in greeting or "Greetings" in greeting
    
    @pytest.mark.asyncio
    async def test_tier_upgrade_hints(self, ux_renderer, sample_ai_response, pro_tier_user):
        """Test upgrade hints for lower tiers"""
        support_message = SupportMessage(
            id="UP_MSG_001",
            user_id=pro_tier_user.user_id,
            phone="+919876543214",
            message="Need advanced portfolio analytics",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.PRO,
            priority=3
        )
        
        rendered_response = await ux_renderer.render_tier_response(
            sample_ai_response, support_message, pro_tier_user
        )
        
        assert "upgrade_hint" in rendered_response
        upgrade_hint = rendered_response["upgrade_hint"]
        assert "ELITE" in upgrade_hint
        assert "advanced" in upgrade_hint.lower() or "premium" in upgrade_hint.lower()
    
    @pytest.mark.asyncio
    async def test_quick_actions_tier_specific(self, ux_renderer, sample_ai_response):
        """Test tier-specific quick actions generation"""
        tiers_and_expected_actions = [
            (SupportTier.LITE, ["Check Balance", "Order Status", "Help"]),
            (SupportTier.PRO, ["Portfolio Analysis", "Trading Tools", "Market Insights", "Support"]),
            (SupportTier.ELITE, ["Executive Brief", "Portfolio Review", "Market Intelligence", "Personal Advisor"]),
            (SupportTier.BLACK, ["Butler Connection", "Concierge Service", "Executive Dashboard", "Priority Support"])
        ]
        
        for tier, expected_actions in tiers_and_expected_actions:
            actions = await ux_renderer._generate_quick_actions(tier, sample_ai_response.category)
            
            # Should have appropriate number of actions for tier
            if tier == SupportTier.LITE:
                assert len(actions) <= 3
            elif tier == SupportTier.PRO:
                assert len(actions) <= 5
            elif tier == SupportTier.ELITE:
                assert len(actions) <= 7
            elif tier == SupportTier.BLACK:
                assert len(actions) >= 8
            
            # Should contain tier-appropriate action types
            action_text = " ".join(actions).lower()
            if tier == SupportTier.BLACK:
                assert "butler" in action_text or "concierge" in action_text
            elif tier == SupportTier.ELITE:
                assert "executive" in action_text or "advisor" in action_text
    
    @pytest.mark.asyncio
    async def test_response_time_display_by_tier(self, ux_renderer):
        """Test response time display varies by tier"""
        response_times = {
            SupportTier.LITE: 25.5,
            SupportTier.PRO: 12.3,
            SupportTier.ELITE: 8.1,
            SupportTier.BLACK: 2.8
        }
        
        for tier, response_time in response_times.items():
            time_display = await ux_renderer._format_response_time(tier, response_time)
            
            if tier == SupportTier.BLACK:
                # BLACK tier shows sub-second precision
                assert "2.8s" in time_display or "instant" in time_display.lower()
            elif tier == SupportTier.ELITE:
                # ELITE shows second precision
                assert "8s" in time_display or "8.1s" in time_display
            else:
                # Lower tiers show rounded times
                assert str(int(response_time)) in time_display


class TestWhatsAppUXFormatter:
    """Test suite for WhatsApp UX formatting"""
    
    @pytest.fixture
    def whatsapp_formatter(self):
        """Initialize WhatsApp formatter"""
        return WhatsAppUXFormatter()
    
    @pytest.fixture
    def sample_tier_response(self):
        """Create sample tier response for formatting"""
        return {
            "tier": "PRO",
            "style": "professional_smart",
            "message": "Your TCS order has been executed successfully. Portfolio value updated.",
            "greeting": "Hello Rohit ⚡",
            "confidence_indicator": "High confidence response (92%)",
            "quick_actions": ["Portfolio Analysis", "Order History", "Market Insights", "Support"],
            "response_time": "12.3s",
            "upgrade_hint": "Upgrade to ELITE for executive briefings",
            "signature": "TradeMate PRO Support"
        }
    
    @pytest.mark.asyncio
    async def test_whatsapp_message_formatting(self, sample_tier_response):
        """Test WhatsApp message formatting"""
        formatted_message = await WhatsAppUXFormatter.format_for_whatsapp(sample_tier_response)
        
        # Should be a properly formatted WhatsApp message
        assert isinstance(formatted_message, str)
        assert "Hello Rohit ⚡" in formatted_message
        assert "TCS order" in formatted_message
        assert "TradeMate PRO Support" in formatted_message
        
        # Should contain quick actions as buttons
        assert "Portfolio Analysis" in formatted_message
        assert "Order History" in formatted_message
    
    @pytest.mark.asyncio
    async def test_black_tier_whatsapp_formatting(self):
        """Test BLACK tier WhatsApp formatting with luxury elements"""
        black_tier_response = {
            "tier": "BLACK",
            "style": "luxury_concierge",
            "message": "Your ₹385 crore RELIANCE transaction has been prioritized by our billionaire desk.",
            "greeting": "Greetings, Mr. Mukesh ◆",
            "confidence_indicator": "Concierge certainty (98%)",
            "quick_actions": ["Butler Connection", "Concierge Service", "Executive Dashboard", "Priority Support", "Emergency Line"],
            "response_time": "2.8s",
            "butler_connection": "Connect to dedicated butler Arjun Mehta",
            "signature": "TradeMate Black Concierge"
        }
        
        formatted_message = await WhatsAppUXFormatter.format_for_whatsapp(black_tier_response)
        
        assert "Mr. Mukesh ◆" in formatted_message
        assert "billionaire desk" in formatted_message
        assert "Butler Connection" in formatted_message
        assert "TradeMate Black Concierge" in formatted_message
        assert "◆" in formatted_message  # Should preserve luxury symbols
    
    @pytest.mark.asyncio
    async def test_interactive_buttons_generation(self, sample_tier_response):
        """Test interactive buttons generation for WhatsApp"""
        formatted_message = await WhatsAppUXFormatter.format_for_whatsapp(sample_tier_response)
        
        # Should format quick actions as interactive elements
        quick_actions = sample_tier_response["quick_actions"]
        for action in quick_actions:
            assert action in formatted_message
        
        # Should maintain proper WhatsApp formatting
        assert len(formatted_message) <= 4096  # WhatsApp message limit
        assert "\n" in formatted_message  # Should have line breaks for readability
    
    @pytest.mark.asyncio
    async def test_emoji_preservation_by_tier(self):
        """Test emoji preservation for different tiers"""
        tier_responses = [
            {"tier": "LITE", "message": "आपका order complete हो गया 😊💳", "greeting": "नमस्ते Anjali 😊"},
            {"tier": "PRO", "message": "Portfolio analysis ready ⚡📊", "greeting": "Hello Rohit ⚡"},
            {"tier": "ELITE", "message": "Executive brief prepared 👑📹", "greeting": "Good day, Ms. Priya 👑"},
            {"tier": "BLACK", "message": "Concierge assistance activated ◆🎩", "greeting": "Greetings, Mr. Mukesh ◆"}
        ]
        
        for tier_response in tier_responses:
            formatted_message = await WhatsAppUXFormatter.format_for_whatsapp(tier_response)
            
            # Should preserve tier-specific emojis
            if tier_response["tier"] == "LITE":
                assert "😊" in formatted_message
            elif tier_response["tier"] == "PRO":
                assert "⚡" in formatted_message
            elif tier_response["tier"] == "ELITE":
                assert "👑" in formatted_message
            elif tier_response["tier"] == "BLACK":
                assert "◆" in formatted_message
    
    @pytest.mark.asyncio
    async def test_message_length_optimization(self):
        """Test message length optimization for WhatsApp"""
        long_tier_response = {
            "tier": "ELITE",
            "message": "This is a very long message that contains extensive details about portfolio analysis, market conditions, trading recommendations, and executive briefings " * 10,
            "greeting": "Good day, Executive",
            "quick_actions": ["Action 1", "Action 2", "Action 3", "Action 4", "Action 5"],
            "signature": "TradeMate ELITE Support"
        }
        
        formatted_message = await WhatsAppUXFormatter.format_for_whatsapp(long_tier_response)
        
        # Should optimize length for WhatsApp
        assert len(formatted_message) <= 4096  # WhatsApp limit
        # Should preserve essential elements even when truncating
        assert "Good day, Executive" in formatted_message
        assert "TradeMate ELITE Support" in formatted_message
    
    @pytest.mark.asyncio
    async def test_multilingual_formatting_preservation(self):
        """Test multilingual text formatting preservation"""
        multilingual_response = {
            "tier": "PRO",
            "message": "आपका TCS order successfully execute हो गया है। Portfolio में ₹1,92,500 का profit दिख रहा है।",
            "greeting": "नमस्ते Rohit ⚡",
            "quick_actions": ["Portfolio देखें", "Order History", "Market Updates"],
            "signature": "TradeMate PRO Support"
        }
        
        formatted_message = await WhatsAppUXFormatter.format_for_whatsapp(multilingual_response)
        
        # Should preserve Hindi text
        assert "आपका" in formatted_message
        assert "नमस्ते" in formatted_message
        assert "Portfolio देखें" in formatted_message
        # Should preserve currency formatting
        assert "₹1,92,500" in formatted_message


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])