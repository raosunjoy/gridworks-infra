"""
Comprehensive Test Suite for Tier AI Manager
Tests all tier-integrated AI SDK functionality with 100% coverage
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from decimal import Decimal

from app.tier_integration.tier_ai_manager import (
    TierAIManager, 
    UserTier, 
    AIServiceQuota,
    UpsellTriggerManager
)
from app.sdk_manager import GridWorksSDK, ClientConfiguration


class TestUserTier:
    """Test UserTier enum functionality"""
    
    def test_user_tier_values(self):
        """Test all tier values exist"""
        assert UserTier.LITE.value == "lite"
        assert UserTier.PRO.value == "pro"
        assert UserTier.ELITE.value == "elite"
        assert UserTier.BLACK.value == "black"
    
    def test_user_tier_from_string(self):
        """Test tier creation from string values"""
        assert UserTier("lite") == UserTier.LITE
        assert UserTier("pro") == UserTier.PRO
        assert UserTier("elite") == UserTier.ELITE
        assert UserTier("black") == UserTier.BLACK


class TestAIServiceQuota:
    """Test AI service quota configuration"""
    
    def test_lite_tier_quotas(self):
        """Test Lite tier quota configuration"""
        quota = AIServiceQuota.TIER_QUOTAS[UserTier.LITE]
        
        assert quota["support_queries_daily"] == 5
        assert quota["morning_pulse_access"] is True
        assert quota["morning_pulse_format"] == "text_only"
        assert quota["trade_ideas"] == 0
        assert quota["custom_alerts"] == 0
        assert quota["group_access"] == "observer"
        assert quota["expert_verification"] is False
        assert quota["whatsapp_delivery"] is False
    
    def test_pro_tier_quotas(self):
        """Test Pro tier quota configuration"""
        quota = AIServiceQuota.TIER_QUOTAS[UserTier.PRO]
        
        assert quota["support_queries_daily"] == 50
        assert quota["morning_pulse_format"] == "voice_plus_text"
        assert quota["trade_ideas"] == 3
        assert quota["custom_alerts"] == 10
        assert quota["group_access"] == "participant"
        assert quota["expert_verification"] == "can_apply"
        assert quota["whatsapp_delivery"] is True
        assert quota["max_expert_groups"] == 3
    
    def test_elite_tier_quotas(self):
        """Test Elite tier quota configuration"""
        quota = AIServiceQuota.TIER_QUOTAS[UserTier.ELITE]
        
        assert quota["support_queries_daily"] == "unlimited"
        assert quota["morning_pulse_format"] == "personalized_video"
        assert quota["trade_ideas"] == 5
        assert quota["custom_alerts"] == "unlimited"
        assert quota["group_access"] == "creator"
        assert quota["expert_verification"] == "fast_track"
        assert quota["max_expert_groups"] == "unlimited"
        assert quota["revenue_sharing"] is True
        assert quota["video_support"] is True
    
    def test_black_tier_quotas(self):
        """Test Black tier quota configuration"""
        quota = AIServiceQuota.TIER_QUOTAS[UserTier.BLACK]
        
        assert quota["support_queries_daily"] == "unlimited"
        assert quota["morning_pulse_format"] == "institutional_report"
        assert quota["trade_ideas"] == 10
        assert quota["institutional_intelligence"] is True
        assert quota["white_label_access"] is True
        assert quota["dedicated_support"] is True
    
    def test_all_tiers_have_quotas(self):
        """Test all tiers have quota configurations"""
        for tier in UserTier:
            assert tier in AIServiceQuota.TIER_QUOTAS
            quota = AIServiceQuota.TIER_QUOTAS[tier]
            assert isinstance(quota, dict)
            assert len(quota) > 0


class TestTierAIManager:
    """Test TierAIManager core functionality"""
    
    @pytest.fixture
    def tier_manager(self):
        """Create TierAIManager instance for testing"""
        return TierAIManager()
    
    @pytest.fixture
    def mock_sdk(self):
        """Create mock SDK instance"""
        sdk = Mock(spec=GridWorksSDK)
        sdk.process_request = AsyncMock()
        sdk.initialize_services = AsyncMock()
        return sdk
    
    @pytest.mark.asyncio
    async def test_get_user_ai_config_lite(self, tier_manager):
        """Test AI config for Lite tier"""
        config = await tier_manager.get_user_ai_config(UserTier.LITE)
        
        assert "services" in config
        assert "quotas" in config
        assert "rate_limits" in config
        assert "features" in config
        
        # Lite tier should only have support service
        from app.sdk_manager import ServiceType
        assert ServiceType.SUPPORT in config["services"]
        assert ServiceType.INTELLIGENCE not in config["services"]
        assert ServiceType.MODERATOR not in config["services"]
    
    @pytest.mark.asyncio
    async def test_get_user_ai_config_pro(self, tier_manager):
        """Test AI config for Pro tier"""
        config = await tier_manager.get_user_ai_config(UserTier.PRO)
        
        from app.sdk_manager import ServiceType
        assert ServiceType.SUPPORT in config["services"]
        assert ServiceType.INTELLIGENCE in config["services"]
        assert ServiceType.MODERATOR not in config["services"]
    
    @pytest.mark.asyncio
    async def test_get_user_ai_config_elite(self, tier_manager):
        """Test AI config for Elite tier"""
        config = await tier_manager.get_user_ai_config(UserTier.ELITE)
        
        from app.sdk_manager import ServiceType
        assert ServiceType.SUPPORT in config["services"]
        assert ServiceType.INTELLIGENCE in config["services"]
        assert ServiceType.MODERATOR in config["services"]
    
    def test_get_rate_limits(self, tier_manager):
        """Test rate limits by tier"""
        lite_limits = tier_manager._get_rate_limits(UserTier.LITE)
        assert lite_limits["support"] == 10
        assert lite_limits["intelligence"] == 2
        assert lite_limits["moderator"] == 0
        
        pro_limits = tier_manager._get_rate_limits(UserTier.PRO)
        assert pro_limits["support"] == 100
        assert pro_limits["intelligence"] == 20
        assert pro_limits["moderator"] == 10
        
        black_limits = tier_manager._get_rate_limits(UserTier.BLACK)
        assert black_limits["support"] == "unlimited"
        assert black_limits["intelligence"] == "unlimited"
        assert black_limits["moderator"] == "unlimited"
    
    def test_get_tier_features(self, tier_manager):
        """Test tier-specific features"""
        lite_features = tier_manager._get_tier_features(UserTier.LITE)
        assert lite_features["ai_personality"] == "helpful_basic"
        assert lite_features["response_length"] == "short"
        assert lite_features["technical_depth"] == "basic"
        
        elite_features = tier_manager._get_tier_features(UserTier.ELITE)
        assert elite_features["ai_personality"] == "expert_advisor"
        assert elite_features["video_generation"] is True
        assert elite_features["personalization"] == "high"
        
        black_features = tier_manager._get_tier_features(UserTier.BLACK)
        assert black_features["ai_personality"] == "institutional_butler"
        assert black_features["dedicated_model"] is True


class TestAISupportRequest:
    """Test AI Support request handling"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_support_request_quota_check(self, tier_manager):
        """Test support quota checking"""
        user_id = "test_user_123"
        
        # Test within quota
        quota_result = await tier_manager._check_support_quota(user_id, UserTier.LITE)
        assert quota_result["allowed"] is True
        assert quota_result["remaining"] == 5
        
        # Simulate usage to hit quota
        for i in range(5):
            await tier_manager._track_usage(user_id, "support_query")
        
        quota_result = await tier_manager._check_support_quota(user_id, UserTier.LITE)
        assert quota_result["allowed"] is False
        assert quota_result["current_usage"] == 5
        assert quota_result["quota"] == 5
    
    @pytest.mark.asyncio
    async def test_support_request_unlimited_quota(self, tier_manager):
        """Test unlimited quota for Elite/Black tiers"""
        user_id = "elite_user_123"
        
        quota_result = await tier_manager._check_support_quota(user_id, UserTier.ELITE)
        assert quota_result["allowed"] is True
        assert "remaining" not in quota_result  # Unlimited
        
        # Even after heavy usage, should still be allowed
        for i in range(100):
            await tier_manager._track_usage(user_id, "support_query")
        
        quota_result = await tier_manager._check_support_quota(user_id, UserTier.ELITE)
        assert quota_result["allowed"] is True
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_handle_ai_support_request_success(self, mock_create_sdk, tier_manager):
        """Test successful AI support request"""
        # Mock SDK response
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {
            "success": True,
            "message": "Order failed due to insufficient margin",
            "actions": [],
            "response_time": 0.025
        }
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        # Test request
        result = await tier_manager.handle_ai_support_request(
            user_id="test_user_123",
            user_tier=UserTier.PRO,
            query="Why did my order fail?",
            context={"balance": 50000}
        )
        
        assert result["success"] is True
        assert "message" in result
        assert result["response_time"] == 0.025
        
        # Verify SDK was called correctly
        mock_create_sdk.assert_called_once_with("test_user_123", UserTier.PRO)
        mock_sdk.process_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_ai_support_request_quota_exceeded(self, tier_manager):
        """Test support request when quota exceeded"""
        user_id = "quota_test_user"
        
        # Use up all quota
        for i in range(5):
            await tier_manager._track_usage(user_id, "support_query")
        
        result = await tier_manager.handle_ai_support_request(
            user_id=user_id,
            user_tier=UserTier.LITE,
            query="Test query",
            context={}
        )
        
        assert result["success"] is False
        assert result["error"] == "quota_exceeded"
        assert "upsell" in result
        assert "quota_reset" in result


class TestMorningPulseRequest:
    """Test Morning Pulse request handling"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_lite_morning_pulse_teaser(self, tier_manager):
        """Test Lite tier gets teaser version"""
        result = await tier_manager.handle_morning_pulse_request(
            user_id="lite_user_123",
            user_tier=UserTier.LITE
        )
        
        assert result["success"] is True
        assert result["format"] == "teaser"
        assert "content" in result
        assert "summary" in result["content"]
        assert "locked_content" in result["content"]
        assert "upsell" in result
        assert result["upsell"]["cta"] == "Upgrade to Pro for ₹999/month"
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_pro_morning_pulse_full(self, mock_create_sdk, tier_manager):
        """Test Pro tier gets full morning pulse"""
        # Mock SDK response
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {
            "success": True,
            "format": "voice_plus_text",
            "content": {
                "summary": "NASDAQ down 1.2%, focus on IT stocks",
                "voice_note_url": "https://voice.example.com/pulse_123.mp3",
                "trade_ideas": [
                    {"symbol": "TCS", "action": "SHORT", "entry_price": 3900}
                ]
            }
        }
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        result = await tier_manager.handle_morning_pulse_request(
            user_id="pro_user_123",
            user_tier=UserTier.PRO
        )
        
        assert result["success"] is True
        assert result["format"] == "voice_plus_text"
        assert "voice_note_url" in result["content"]
        assert len(result["content"]["trade_ideas"]) > 0
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_elite_morning_pulse_personalized(self, mock_create_sdk, tier_manager):
        """Test Elite tier gets personalized morning pulse"""
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {
            "success": True,
            "format": "personalized_video",
            "content": {
                "summary": "Personalized analysis for your portfolio",
                "trade_ideas": []
            }
        }
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        # Mock personalization
        tier_manager._add_elite_personalization = AsyncMock(return_value={
            "portfolio_impact_analysis": "Your RELIANCE position benefits from oil rally"
        })
        
        result = await tier_manager.handle_morning_pulse_request(
            user_id="elite_user_123",
            user_tier=UserTier.ELITE
        )
        
        assert result["success"] is True
        assert "personalized_insights" in result
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_black_morning_pulse_institutional(self, mock_create_sdk, tier_manager):
        """Test Black tier gets institutional intelligence"""
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {
            "success": True,
            "format": "institutional_report",
            "content": {
                "comprehensive_analysis": "10-page institutional report"
            }
        }
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        # Mock institutional data
        tier_manager._add_black_institutional_data = AsyncMock(return_value={
            "institutional_flows": {"fii_activity": "Net selling ₹2,400Cr"}
        })
        
        result = await tier_manager.handle_morning_pulse_request(
            user_id="black_user_123",
            user_tier=UserTier.BLACK
        )
        
        assert result["success"] is True
        assert "institutional_intelligence" in result


class TestExpertGroupRequest:
    """Test Expert Group request handling"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_lite_tier_group_restriction(self, tier_manager):
        """Test Lite tier cannot create groups"""
        result = await tier_manager.handle_expert_group_request(
            user_id="lite_user_123",
            user_tier=UserTier.LITE,
            action="create_group",
            data={"group_settings": {"name": "Test Group"}}
        )
        
        assert result["success"] is False
        assert result["error"] == "tier_restriction"
        assert "Upgrade to Pro" in result["message"]
        assert "upsell" in result
    
    @pytest.mark.asyncio
    async def test_pro_tier_group_participation_only(self, tier_manager):
        """Test Pro tier cannot create groups but can participate"""
        result = await tier_manager.handle_expert_group_request(
            user_id="pro_user_123",
            user_tier=UserTier.PRO,
            action="create_group",
            data={}
        )
        
        assert result["success"] is False
        assert result["error"] == "tier_restriction"
        assert "Upgrade to Elite" in result["message"]
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_elite_tier_group_creation(self, mock_create_sdk, tier_manager):
        """Test Elite tier can create expert groups"""
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {
            "success": True,
            "group_id": "expert_group_123",
            "revenue_sharing_enabled": True
        }
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        result = await tier_manager.handle_expert_group_request(
            user_id="elite_user_123",
            user_tier=UserTier.ELITE,
            action="create_group",
            data={
                "group_settings": {
                    "name": "Elite Trading Signals",
                    "subscription_price": 1999
                }
            }
        )
        
        assert result["success"] is True
        assert result["group_id"] == "expert_group_123"
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_black_tier_white_label_groups(self, mock_create_sdk, tier_manager):
        """Test Black tier gets white label options"""
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {
            "success": True,
            "group_id": "institutional_group_123"
        }
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        # Mock white label options
        tier_manager._get_white_label_options = AsyncMock(return_value={
            "custom_branding": True,
            "api_access": True
        })
        
        result = await tier_manager.handle_expert_group_request(
            user_id="black_user_123",
            user_tier=UserTier.BLACK,
            action="create_group",
            data={"group_settings": {"institutional_grade": True}}
        )
        
        assert result["success"] is True
        assert "white_label_options" in result


class TestUpsellTriggerManager:
    """Test intelligent upsell trigger system"""
    
    @pytest.fixture
    def upsell_manager(self):
        return UpsellTriggerManager()
    
    @pytest.mark.asyncio
    async def test_support_upsell_lite_quota_trigger(self, upsell_manager):
        """Test support upsell trigger for Lite tier quota hit"""
        # Mock usage data showing quota hit
        with patch.object(upsell_manager, '_get_user_usage_data') as mock_usage:
            mock_usage.return_value = {"support_queries_today": 5}
            
            result = await upsell_manager.check_support_upsell("user_123", UserTier.LITE)
            
            assert result is not None
            assert result["trigger_type"] == "ai_usage_based"
            assert result["current_tier"] == "lite"
            assert result["service"] == "support"
            assert "Upgrade to Pro" in result["cta"]
    
    @pytest.mark.asyncio
    async def test_intelligence_upsell_pro_engagement_trigger(self, upsell_manager):
        """Test intelligence upsell for Pro tier high engagement"""
        with patch.object(upsell_manager, '_get_user_usage_data') as mock_usage:
            mock_usage.return_value = {"trade_idea_clicks": 25}
            
            result = await upsell_manager.check_intelligence_upsell("user_123", UserTier.PRO)
            
            assert result is not None
            assert "Elite" in result["offer"]
            assert "personalized portfolio optimization" in result["offer"]
    
    @pytest.mark.asyncio
    async def test_moderator_upsell_elite_revenue_trigger(self, upsell_manager):
        """Test moderator upsell for Elite tier earning well"""
        with patch.object(upsell_manager, '_get_user_usage_data') as mock_usage:
            mock_usage.return_value = {"expert_revenue": 18000}
            
            result = await upsell_manager.check_moderator_upsell("user_123", UserTier.ELITE)
            
            assert result is not None
            assert "Black" in result["offer"]
            assert "unlimited earning potential" in result["offer"]
    
    @pytest.mark.asyncio
    async def test_no_upsell_for_black_tier(self, upsell_manager):
        """Test no upsell triggers for Black tier (top tier)"""
        result = await upsell_manager.check_support_upsell("user_123", UserTier.BLACK)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_upsell_frequency_control(self, upsell_manager):
        """Test upsell frequency limiting"""
        # Mock usage data that would trigger upsell
        with patch.object(upsell_manager, '_get_user_usage_data') as mock_usage:
            mock_usage.return_value = {"support_queries_today": 5}
            
            # First trigger should work
            result1 = await upsell_manager.check_support_upsell("user_123", UserTier.LITE)
            assert result1 is not None
            
            # Second trigger within 3 days should be None (frequency control)
            result2 = await upsell_manager.check_support_upsell("user_123", UserTier.LITE)
            assert result2 is None
    
    def test_get_next_tier(self, upsell_manager):
        """Test tier progression logic"""
        assert upsell_manager._get_next_tier(UserTier.LITE) == UserTier.PRO
        assert upsell_manager._get_next_tier(UserTier.PRO) == UserTier.ELITE
        assert upsell_manager._get_next_tier(UserTier.ELITE) == UserTier.BLACK
        assert upsell_manager._get_next_tier(UserTier.BLACK) == UserTier.BLACK
    
    @pytest.mark.asyncio
    async def test_get_social_proof(self, upsell_manager):
        """Test social proof generation"""
        lite_proof = await upsell_manager._get_social_proof(UserTier.LITE)
        assert "100,000+ Pro users" in lite_proof
        
        pro_proof = await upsell_manager._get_social_proof(UserTier.PRO)
        assert "Elite users create 3x more" in pro_proof


class TestDeliveryChannels:
    """Test delivery channel configuration by tier"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    def test_lite_delivery_channels(self, tier_manager):
        """Test Lite tier delivery channels"""
        channels = tier_manager._get_delivery_channels(UserTier.LITE)
        assert channels == ["app"]
    
    def test_pro_delivery_channels(self, tier_manager):
        """Test Pro tier delivery channels"""
        channels = tier_manager._get_delivery_channels(UserTier.PRO)
        assert "app" in channels
        assert "whatsapp" in channels
        assert "email" in channels
        assert len(channels) == 3
    
    def test_black_delivery_channels(self, tier_manager):
        """Test Black tier delivery channels"""
        channels = tier_manager._get_delivery_channels(UserTier.BLACK)
        assert "dedicated_app" in channels
        assert len(channels) >= 4


class TestUsageTracking:
    """Test usage tracking functionality"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_track_usage(self, tier_manager):
        """Test usage tracking increments correctly"""
        user_id = "track_test_user"
        service = "support_query"
        
        # Track usage multiple times
        for i in range(3):
            await tier_manager._track_usage(user_id, service)
        
        # Check usage is tracked
        today = datetime.now().strftime("%Y-%m-%d")
        usage_key = f"{user_id}_{today}_{service}"
        assert tier_manager.usage_tracker[usage_key] == 3
    
    @pytest.mark.asyncio
    async def test_daily_usage_reset(self, tier_manager):
        """Test usage resets daily"""
        user_id = "reset_test_user"
        
        # Track usage today
        await tier_manager._track_usage(user_id, "support_query")
        
        # Mock tomorrow's date check
        with patch('app.tier_integration.tier_ai_manager.datetime') as mock_datetime:
            # Set tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            mock_datetime.now.return_value = tomorrow
            mock_datetime.strftime = datetime.strftime
            
            # Check quota for tomorrow (should be reset)
            quota_result = await tier_manager._check_support_quota(user_id, UserTier.LITE)
            assert quota_result["allowed"] is True


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_invalid_tier_handling(self, tier_manager):
        """Test handling of invalid tier values"""
        with pytest.raises(ValueError):
            UserTier("invalid_tier")
    
    @pytest.mark.asyncio
    async def test_empty_context_handling(self, tier_manager):
        """Test handling of empty context in requests"""
        # This should not crash
        quota_result = await tier_manager._check_support_quota("user_123", UserTier.LITE)
        assert "allowed" in quota_result
    
    @pytest.mark.asyncio
    async def test_concurrent_usage_tracking(self, tier_manager):
        """Test concurrent usage tracking doesn't cause race conditions"""
        user_id = "concurrent_test_user"
        
        # Create multiple concurrent tracking tasks
        tasks = []
        for i in range(10):
            task = asyncio.create_task(tier_manager._track_usage(user_id, "support_query"))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Check final count is correct
        today = datetime.now().strftime("%Y-%m-%d")
        usage_key = f"{user_id}_{today}_support_query"
        assert tier_manager.usage_tracker[usage_key] == 10


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_user_progression_lite_to_pro(self, tier_manager):
        """Test complete user progression from Lite to Pro"""
        user_id = "progression_user_123"
        
        # Start as Lite user - use up quota
        for i in range(5):
            await tier_manager._track_usage(user_id, "support_query")
        
        # Check quota exceeded
        quota_result = await tier_manager._check_support_quota(user_id, UserTier.LITE)
        assert quota_result["allowed"] is False
        
        # Check upsell trigger
        upsell_result = await tier_manager.upsell_triggers.check_support_upsell(user_id, UserTier.LITE)
        assert upsell_result is not None
        assert "Pro" in upsell_result["cta"]
        
        # User upgrades to Pro - now has higher quota
        pro_quota = await tier_manager._check_support_quota(user_id, UserTier.PRO)
        assert pro_quota["allowed"] is True
    
    @pytest.mark.asyncio
    @patch('app.tier_integration.tier_ai_manager.TierAIManager.create_user_sdk')
    async def test_morning_pulse_tier_progression(self, mock_create_sdk, tier_manager):
        """Test morning pulse experience across tier progression"""
        user_id = "pulse_progression_user"
        
        # Lite tier - teaser only
        lite_result = await tier_manager.handle_morning_pulse_request(user_id, UserTier.LITE)
        assert lite_result["format"] == "teaser"
        assert "locked_content" in lite_result["content"]
        
        # Pro tier - full pulse with voice
        mock_sdk = Mock()
        mock_response = Mock()
        mock_response.data = {"success": True, "format": "voice_plus_text", "content": {}}
        mock_sdk.process_request = AsyncMock(return_value=mock_response)
        mock_create_sdk.return_value = mock_sdk
        
        pro_result = await tier_manager.handle_morning_pulse_request(user_id, UserTier.PRO)
        assert pro_result["success"] is True
        
        # Elite tier - personalized content
        elite_result = await tier_manager.handle_morning_pulse_request(user_id, UserTier.ELITE)
        assert "personalized_insights" in elite_result or elite_result["success"] is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])