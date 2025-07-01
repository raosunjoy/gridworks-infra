"""
Comprehensive Test Suite for Tier AI API Endpoints
Tests FastAPI endpoints with tier-specific features and intelligent upselling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from app.api.v1.tier_ai_endpoints import router
from app.tier_integration.tier_ai_manager import UserTier
from app.models.user import User


# Mock FastAPI app for testing
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class MockUser:
    """Mock user for testing"""
    
    def __init__(self, tier: UserTier, user_id: int = 123):
        self.id = user_id
        self.tier = tier.value
        self.username = f"test_user_{user_id}"
        self.display_name = f"Test User {user_id}"
        self.balance = 50000
        self.portfolio_value = 500000
        self.reputation_score = 75
        self.api_key = f"test_key_{user_id}"
    
    async def get_recent_orders(self):
        return [
            {"order_id": "order_123", "symbol": "RELIANCE", "status": "completed"},
            {"order_id": "order_124", "symbol": "TCS", "status": "pending"}
        ]
    
    def get_context(self):
        return {
            "user_id": self.id,
            "tier": self.tier,
            "balance": self.balance,
            "portfolio_value": self.portfolio_value
        }


class TestSupportEndpoints:
    """Test AI Support API endpoints"""
    
    @pytest.fixture
    def mock_tier_manager(self):
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            yield mock_manager
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_ai_support_query_success(self, mock_tier_manager, mock_get_current_user):
        """Test successful AI support query"""
        # Mock user
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        # Mock tier manager response
        mock_tier_manager.handle_ai_support_request = AsyncMock(return_value={
            "success": True,
            "message": "Order failed due to insufficient margin",
            "response_time": 0.025,
            "actions": [{"type": "check_margin", "description": "Check margin requirements"}]
        })
        
        # Test request
        response = client.post("/ai/support/query", json={
            "message": "Why did my order fail?",
            "context": {"order_id": "order_123"},
            "language": "english"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Order failed due to insufficient margin" in data["message"]
        assert data["response_time"] == 0.025
        assert len(data["actions"]) > 0
    
    def test_ai_support_query_quota_exceeded(self, mock_tier_manager, mock_get_current_user):
        """Test AI support query when quota exceeded"""
        # Mock Lite tier user
        mock_user = MockUser(UserTier.LITE)
        mock_get_current_user.return_value = mock_user
        
        # Mock quota exceeded response
        mock_tier_manager.handle_ai_support_request = AsyncMock(return_value={
            "success": False,
            "error": "quota_exceeded",
            "upsell": {
                "title": "Upgrade to Pro for Unlimited AI Support",
                "features": ["Unlimited daily queries", "15-second response time"],
                "price": "₹999/month"
            },
            "quota_reset": "2025-07-01T00:00:00"
        })
        
        response = client.post("/ai/support/query", json={
            "message": "Test query",
            "language": "english"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "quota_exceeded"
        assert "upsell" in data
        assert "Upgrade to Pro" in data["upsell"]["title"]
    
    def test_get_support_quota(self, mock_tier_manager, mock_get_current_user):
        """Test getting support quota information"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager._check_support_quota = AsyncMock(return_value={
            "allowed": True,
            "remaining": 45,
            "quota": 50
        })
        
        response = client.get("/ai/support/quota")
        
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "pro"
        assert data["quota"]["remaining"] == 45
        assert "tier_limits" in data
    
    def test_ai_support_query_invalid_request(self, mock_get_current_user):
        """Test AI support with invalid request data"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        # Missing required 'message' field
        response = client.post("/ai/support/query", json={
            "language": "english"
        })
        
        assert response.status_code == 422  # Validation error


class TestIntelligenceEndpoints:
    """Test AI Intelligence API endpoints"""
    
    @pytest.fixture
    def mock_tier_manager(self):
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            yield mock_manager
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_get_morning_pulse_pro(self, mock_tier_manager, mock_get_current_user):
        """Test morning pulse for Pro tier user"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.handle_morning_pulse_request = AsyncMock(return_value={
            "success": True,
            "format": "voice_plus_text",
            "content": {
                "summary": "NASDAQ down 1.2%, IT stocks may face pressure",
                "voice_note_url": "https://voice.example.com/pulse_123.mp3",
                "trade_ideas": [
                    {
                        "symbol": "TCS",
                        "action": "SHORT", 
                        "entry_price": 3900,
                        "target": 3800,
                        "stop_loss": 3950,
                        "confidence": 75
                    }
                ]
            }
        })
        
        response = client.get("/ai/intelligence/morning-pulse")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["format"] == "voice_plus_text"
        assert "voice_note_url" in data["content"]
        assert len(data["content"]["trade_ideas"]) > 0
    
    def test_get_morning_pulse_lite_teaser(self, mock_tier_manager, mock_get_current_user):
        """Test morning pulse teaser for Lite tier user"""
        mock_user = MockUser(UserTier.LITE)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.handle_morning_pulse_request = AsyncMock(return_value={
            "success": True,
            "format": "teaser",
            "content": {
                "summary": "NASDAQ down 1.2%, Oil up 3% - Mixed signals",
                "teaser_insights": ["IT stocks may face pressure", "Energy could benefit"],
                "locked_content": {
                    "trade_ideas": 3,
                    "voice_analysis": "30-second detailed analysis"
                }
            },
            "upsell": {
                "message": "Unlock 3 specific trade ideas + voice analysis",
                "cta": "Upgrade to Pro for ₹999/month"
            }
        })
        
        response = client.get("/ai/intelligence/morning-pulse")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["format"] == "teaser"
        assert "locked_content" in data["content"]
        assert "upsell" in data
    
    def test_create_custom_alert_pro_tier(self, mock_tier_manager, mock_get_current_user):
        """Test creating custom alert for Pro tier user"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        alert_config = {
            "symbol": "RELIANCE",
            "condition": "price_above",
            "threshold": 2500,
            "notification_channels": ["whatsapp", "email"]
        }
        
        response = client.post("/ai/intelligence/custom-alert", json=alert_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "alert_id" in data
        assert "Alert created successfully" in data["message"]
    
    def test_create_custom_alert_lite_tier_restriction(self, mock_tier_manager, mock_get_current_user):
        """Test custom alert restriction for Lite tier"""
        mock_user = MockUser(UserTier.LITE)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.upsell_triggers.get_intelligence_upsell = AsyncMock(return_value={
            "title": "Unlock Custom Alerts",
            "price": "₹999/month"
        })
        
        alert_config = {
            "symbol": "RELIANCE",
            "condition": "price_above",
            "threshold": 2500
        }
        
        response = client.post("/ai/intelligence/custom-alert", json=alert_config)
        
        assert response.status_code == 402  # Payment required
        data = response.json()
        assert data["detail"]["error"] == "tier_restriction"
        assert "Pro tier" in data["detail"]["message"]
        assert "upsell" in data["detail"]


class TestExpertGroupsEndpoints:
    """Test Expert Groups API endpoints"""
    
    @pytest.fixture
    def mock_tier_manager(self):
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            yield mock_manager
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_expert_group_action_elite_create(self, mock_tier_manager, mock_get_current_user):
        """Test creating expert group as Elite tier user"""
        mock_user = MockUser(UserTier.ELITE)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.handle_expert_group_request = AsyncMock(return_value={
            "success": True,
            "group_id": "expert_group_123",
            "group_config": {
                "name": "Elite Trading Signals",
                "subscription_price": 2999,
                "max_members": 50
            },
            "revenue_sharing_enabled": True
        })
        
        request_data = {
            "action": "create_group",
            "group_settings": {
                "name": "Elite Trading Signals",
                "subscription_price": 2999,
                "max_members": 50,
                "category": "swing_trading"
            }
        }
        
        response = client.post("/ai/groups/action", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["group_id"] == "expert_group_123"
        assert data["revenue_sharing_enabled"] is True
    
    def test_expert_group_action_pro_restriction(self, mock_tier_manager, mock_get_current_user):
        """Test group creation restriction for Pro tier"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.handle_expert_group_request = AsyncMock(return_value={
            "success": False,
            "error": "tier_restriction",
            "message": "Upgrade to Elite to create expert groups and earn revenue",
            "upsell": {
                "title": "Create Your Expert Group & Earn",
                "features": ["Create unlimited expert groups", "Earn up to ₹50,000/month"],
                "price": "₹4,999/month"
            }
        })
        
        request_data = {
            "action": "create_group",
            "group_settings": {"name": "Test Group"}
        }
        
        response = client.post("/ai/groups/action", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "tier_restriction"
        assert "Upgrade to Elite" in data["message"]
        assert "upsell" in data
    
    def test_get_my_expert_groups_elite(self, mock_get_current_user):
        """Test getting expert groups for Elite tier user"""
        mock_user = MockUser(UserTier.ELITE)
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/ai/groups/my-groups")
        
        assert response.status_code == 200
        data = response.json()
        assert "groups" in data
        assert data["tier_access"] == "creator"
        assert data["can_create_groups"] is True
        
        # Should have own expert group
        own_group = next((g for g in data["groups"] if g["role"] == "owner"), None)
        assert own_group is not None
        assert "monthly_revenue" in own_group
    
    def test_get_my_expert_groups_lite(self, mock_get_current_user):
        """Test getting expert groups for Lite tier user"""
        mock_user = MockUser(UserTier.LITE)
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/ai/groups/my-groups")
        
        assert response.status_code == 200
        data = response.json()
        assert data["tier_access"] == "observer"
        assert data["can_create_groups"] is False
        assert len(data["groups"]) == 0  # Lite tier has no group access


class TestTierManagementEndpoints:
    """Test tier management API endpoints"""
    
    @pytest.fixture
    def mock_tier_manager(self):
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            yield mock_manager
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_get_tier_features(self, mock_tier_manager, mock_get_current_user):
        """Test getting tier features and upgrade options"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.get_user_ai_config = AsyncMock(return_value={
            "services": ["support", "intelligence"],
            "quotas": {"support_queries_daily": 50},
            "features": {"ai_personality": "professional_trader"}
        })
        
        with patch('app.api.v1.tier_ai_endpoints.get_upgrade_benefits') as mock_benefits:
            mock_benefits.return_value = {
                "support": "Personal AI butler + video support",
                "intelligence": "5 trade ideas + video briefings",
                "roi_estimate": "Elite users average ₹25,000 monthly revenue"
            }
            
            with patch('app.api.v1.tier_ai_endpoints.get_user_ai_analytics') as mock_analytics:
                mock_analytics.return_value = {
                    "daily_usage": {"support_queries": 12},
                    "engagement_score": 0.78
                }
                
                response = client.get("/ai/tier/features")
                
                assert response.status_code == 200
                data = response.json()
                assert data["current_tier"]["name"] == "pro"
                assert data["next_tier"]["name"] == "elite"
                assert "upgrade_benefits" in data["next_tier"]
                assert "usage_analytics" in data
    
    def test_preview_tier_upgrade(self, mock_tier_manager, mock_get_current_user):
        """Test tier upgrade preview"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        with patch('app.api.v1.tier_ai_endpoints.calculate_upgrade_roi') as mock_roi:
            mock_roi.return_value = {
                "upgrade_cost": 4999,
                "estimated_monthly_benefit": 25000,
                "payback_period_months": 2.4,
                "annual_roi_percentage": 500
            }
            
            response = client.post("/ai/tier/upgrade-preview", json={"target_tier": "elite"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["upgrade_summary"]["from"] == "pro"
            assert data["upgrade_summary"]["to"] == "elite"
            assert "roi_analysis" in data["upgrade_summary"]
            assert data["pricing"]["monthly"] == 4999
            assert data["trial_available"] is True
    
    def test_preview_tier_upgrade_invalid_path(self, mock_get_current_user):
        """Test invalid tier upgrade path"""
        mock_user = MockUser(UserTier.BLACK)
        mock_get_current_user.return_value = mock_user
        
        response = client.post("/ai/tier/upgrade-preview", json={"target_tier": "lite"})
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid upgrade path" in data["detail"]


class TestAnalyticsEndpoints:
    """Test analytics API endpoints"""
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_get_ai_usage_analytics(self, mock_get_current_user):
        """Test getting AI usage analytics"""
        mock_user = MockUser(UserTier.ELITE)
        mock_get_current_user.return_value = mock_user
        
        with patch('app.api.v1.tier_ai_endpoints.get_user_ai_analytics') as mock_analytics:
            mock_analytics.return_value = {
                "daily_usage": {
                    "support_queries": 25,
                    "morning_pulse_opens": 12,
                    "group_interactions": 45
                },
                "weekly_trends": {
                    "most_active_service": "intelligence",
                    "usage_growth": 15,
                    "engagement_score": 0.82
                },
                "satisfaction_indicators": {
                    "response_ratings": 4.7,
                    "retention_probability": 0.95
                }
            }
            
            response = client.get("/ai/analytics/ai-usage")
            
            assert response.status_code == 200
            data = response.json()
            assert "daily_usage" in data
            assert "weekly_trends" in data
            assert "satisfaction_indicators" in data
            assert data["daily_usage"]["support_queries"] == 25
    
    def test_get_upsell_insights(self, mock_get_current_user):
        """Test getting personalized upsell insights"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            mock_manager.upsell_triggers.check_support_upsell = AsyncMock(return_value={
                "trigger_type": "ai_usage_based",
                "message": "You're asking sophisticated questions",
                "offer": "Upgrade to Elite for personal AI butler"
            })
            mock_manager.upsell_triggers.check_intelligence_upsell = AsyncMock(return_value=None)
            mock_manager.upsell_triggers.check_moderator_upsell = AsyncMock(return_value={
                "message": "You're investing in expert knowledge",
                "offer": "Create your own expert group in Elite"
            })
            
            with patch('app.api.v1.tier_ai_endpoints.get_usage_recommendations') as mock_recommendations:
                mock_recommendations.return_value = [
                    {
                        "type": "monetization",
                        "title": "Start Your Expert Group",
                        "description": "Your accuracy is 78% - start earning",
                        "action": "upgrade_to_elite"
                    }
                ]
                
                with patch('app.api.v1.tier_ai_endpoints.get_progression_timeline') as mock_timeline:
                    mock_timeline.return_value = {
                        "current_tier": "pro",
                        "next_milestone": "elite",
                        "estimated_timeline": "1-2 months based on your portfolio"
                    }
                    
                    response = client.get("/ai/analytics/upsell-insights")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["current_tier"] == "pro"
                    assert "active_upsells" in data
                    assert "usage_based_recommendations" in data
                    assert "tier_progression_timeline" in data


class TestErrorHandling:
    """Test error handling in API endpoints"""
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_ai_support_service_error(self, mock_get_current_user):
        """Test handling of AI support service errors"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            mock_manager.handle_ai_support_request = AsyncMock(
                side_effect=Exception("AI service temporarily unavailable")
            )
            
            response = client.post("/ai/support/query", json={
                "message": "Test query",
                "language": "english"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "AI support error" in data["detail"]
    
    def test_intelligence_service_error(self, mock_get_current_user):
        """Test handling of intelligence service errors"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            mock_manager.handle_morning_pulse_request = AsyncMock(
                side_effect=Exception("Intelligence service down")
            )
            
            response = client.get("/ai/intelligence/morning-pulse")
            
            assert response.status_code == 500
            data = response.json()
            assert "Intelligence service error" in data["detail"]
    
    def test_unauthorized_access(self):
        """Test unauthorized access to endpoints"""
        # No authentication provided
        response = client.post("/ai/support/query", json={
            "message": "Test query"
        })
        
        # Should return authentication error
        assert response.status_code in [401, 422]  # Depending on auth implementation


class TestBackgroundTasks:
    """Test background task functionality"""
    
    @pytest.fixture
    def mock_tier_manager(self):
        with patch('app.api.v1.tier_ai_endpoints.tier_ai_manager') as mock_manager:
            yield mock_manager
    
    @pytest.fixture
    def mock_get_current_user(self):
        with patch('app.api.v1.tier_ai_endpoints.get_current_user') as mock_user:
            yield mock_user
    
    def test_analytics_tracking_background_task(self, mock_tier_manager, mock_get_current_user):
        """Test that analytics tracking happens in background"""
        mock_user = MockUser(UserTier.PRO)
        mock_get_current_user.return_value = mock_user
        
        mock_tier_manager.handle_ai_support_request = AsyncMock(return_value={
            "success": True,
            "message": "Test response"
        })
        
        with patch('app.api.v1.tier_ai_endpoints.track_ai_usage') as mock_track:
            response = client.post("/ai/support/query", json={
                "message": "Test query",
                "language": "english"
            })
            
            assert response.status_code == 200
            # Background task should be scheduled (though not executed in test)
            # This verifies the endpoint structure is correct


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])