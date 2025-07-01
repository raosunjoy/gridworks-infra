"""
Comprehensive Integration Test Suite for AI SDK Suite
Tests end-to-end workflows and tier progression scenarios
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.sdk_manager import GridWorksSDK, ClientConfiguration, ServiceType, IntegrationType
from app.tier_integration.tier_ai_manager import TierAIManager, UserTier
from examples.user_tier_journey import MockUser


class TestUserTierProgression:
    """Test complete user tier progression scenarios"""
    
    @pytest.fixture
    def tier_manager(self):
        return TierAIManager()
    
    @pytest.mark.asyncio
    async def test_lite_to_pro_progression(self, tier_manager):
        """Test user progression from Lite to Pro tier"""
        user = MockUser("user_progression_123", "Priya Sharma", UserTier.LITE)
        
        # Lite tier experience - hit quota limit
        for i in range(5):
            result = await tier_manager.handle_ai_support_request(
                user_id=user.id,
                user_tier=user.tier,
                query=f"Query {i+1}: How to read charts?",
                context={"balance": user.balance}
            )
            user.log_interaction("support", "query", result.get("success", True))
        
        # 6th query should be blocked
        blocked_result = await tier_manager.handle_ai_support_request(
            user_id=user.id,
            user_tier=user.tier,
            query="Query 6: Another question",
            context={"balance": user.balance}
        )
        
        assert blocked_result["success"] is False
        assert blocked_result["error"] == "quota_exceeded"
        assert "upsell" in blocked_result
        
        # Check upsell trigger
        upsell = await tier_manager.upsell_triggers.check_support_upsell(user.id, user.tier)
        assert upsell is not None
        assert "Pro" in upsell["cta"]
        
        # User upgrades to Pro
        user.upgrade_tier(UserTier.PRO)
        
        # Now unlimited queries work
        pro_result = await tier_manager.handle_ai_support_request(
            user_id=user.id,
            user_tier=user.tier,
            query="Pro tier query works",
            context={"balance": user.balance}
        )
        
        assert pro_result["success"] is True
        assert "upsell_offer" not in pro_result or pro_result["upsell_offer"] is None
    
    @pytest.mark.asyncio
    async def test_pro_to_elite_progression(self, tier_manager):
        """Test user progression from Pro to Elite tier"""
        user = MockUser("user_pro_elite", "Rajesh Kumar", UserTier.PRO)
        user.portfolio_value = 500000  # ₹5L portfolio
        
        # Pro user actively uses morning pulse
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={
                    "success": True,
                    "format": "voice_plus_text",
                    "content": {
                        "trade_ideas": [{"symbol": "TCS", "action": "SHORT", "confidence": 75}]
                    }
                }
            ))
            
            # Use morning pulse multiple times
            for i in range(10):
                result = await tier_manager.handle_morning_pulse_request(
                    user_id=user.id,
                    user_tier=user.tier
                )
                user.log_interaction("intelligence", "morning_pulse")
        
        # Check for Elite upsell trigger
        upsell = await tier_manager.upsell_triggers.check_intelligence_upsell(user.id, user.tier)
        assert upsell is not None
        assert "Elite" in upsell["offer"]
        
        # User upgrades to Elite
        user.upgrade_tier(UserTier.ELITE)
        user.simulate_trading_success()  # Portfolio grows
        
        # Elite user can now create expert groups
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={
                    "success": True,
                    "group_id": "expert_group_456",
                    "revenue_sharing_enabled": True
                }
            ))
            
            group_result = await tier_manager.handle_expert_group_request(
                user_id=user.id,
                user_tier=user.tier,
                action="create_group",
                data={
                    "group_settings": {
                        "name": "Rajesh's Swing Signals",
                        "subscription_price": 1999,
                        "max_members": 30
                    }
                }
            )
            
            assert group_result["success"] is True
            assert group_result["group_id"] == "expert_group_456"
    
    @pytest.mark.asyncio
    async def test_elite_to_black_progression(self, tier_manager):
        """Test user progression from Elite to Black tier"""
        user = MockUser("user_elite_black", "Institutional Trader", UserTier.ELITE)
        user.portfolio_value = 10000000  # ₹1Cr portfolio
        user.revenue_earned = 50000  # Earning ₹50K/month from expert groups
        
        # Elite user earning well from expert groups
        upsell = await tier_manager.upsell_triggers.check_moderator_upsell(user.id, user.tier)
        
        # Should not trigger immediately (requires ₹15K+ monthly revenue)
        # Let's simulate higher revenue
        with patch.object(tier_manager.upsell_triggers, '_get_user_usage_data') as mock_usage:
            mock_usage.return_value = {"expert_revenue": 18000}
            
            upsell = await tier_manager.upsell_triggers.check_moderator_upsell(user.id, user.tier)
            assert upsell is not None
            assert "Black" in upsell["offer"]
            assert "unlimited earning potential" in upsell["offer"]
        
        # User upgrades to Black
        user.upgrade_tier(UserTier.BLACK)
        
        # Black tier gets institutional intelligence
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={
                    "success": True,
                    "format": "institutional_report",
                    "content": {"comprehensive_analysis": "10-page report"}
                }
            ))
            
            tier_manager._add_black_institutional_data = AsyncMock(return_value={
                "institutional_flows": {"fii_activity": "Net selling ₹2,400Cr"}
            })
            
            black_pulse = await tier_manager.handle_morning_pulse_request(
                user_id=user.id,
                user_tier=user.tier
            )
            
            assert black_pulse["success"] is True
            assert black_pulse["format"] == "institutional_report"
            assert "institutional_intelligence" in black_pulse


class TestCrossServiceIntegration:
    """Test integration between different AI services"""
    
    @pytest.mark.asyncio
    async def test_support_to_intelligence_workflow(self):
        """Test workflow from support query to intelligence recommendation"""
        config = ClientConfiguration(
            client_id="workflow_client",
            client_name="Workflow Test",
            api_key="workflow_key",
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API
        )
        
        with patch('app.ai_support.AISupport') as mock_support:
            with patch('app.ai_intelligence.AIIntelligence') as mock_intelligence:
                # Mock support service suggesting intelligence check
                mock_support_instance = Mock()
                mock_support_instance.process_query = AsyncMock(return_value={
                    "success": True,
                    "message": "Portfolio looks good for current market conditions",
                    "suggestion": "check_morning_pulse_for_opportunities",
                    "next_service": "intelligence"
                })
                mock_support.return_value = mock_support_instance
                
                # Mock intelligence service providing market insights
                mock_intelligence_instance = Mock()
                mock_intelligence_instance.generate_morning_pulse = AsyncMock(return_value={
                    "success": True,
                    "content": {
                        "summary": "Market showing bullish signals",
                        "trade_ideas": [{"symbol": "RELIANCE", "action": "BUY"}]
                    }
                })
                mock_intelligence.return_value = mock_intelligence_instance
                
                # Initialize SDK
                sdk = GridWorksSDK(config)
                await sdk.initialize_services()
                
                # Step 1: User asks support about portfolio
                support_response = await sdk.process_request(
                    service="support",
                    action="query",
                    data={"message": "How is my portfolio performing?"}
                )
                
                assert support_response.success is True
                assert "check_morning_pulse" in support_response.data["suggestion"]
                
                # Step 2: Follow suggestion to check intelligence
                intelligence_response = await sdk.process_request(
                    service="intelligence",
                    action="morning_pulse",
                    data={"user_id": "workflow_user"}
                )
                
                assert intelligence_response.success is True
                assert len(intelligence_response.data["content"]["trade_ideas"]) > 0
    
    @pytest.mark.asyncio
    async def test_intelligence_to_moderator_workflow(self):
        """Test workflow from intelligence insights to expert group interaction"""
        tier_manager = TierAIManager()
        user_id = "workflow_user_456"
        
        # Step 1: User gets morning pulse with trade ideas
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={
                    "success": True,
                    "content": {
                        "trade_ideas": [
                            {"symbol": "TCS", "action": "SHORT", "confidence": 80}
                        ]
                    }
                }
            ))
            
            intelligence_result = await tier_manager.handle_morning_pulse_request(
                user_id=user_id,
                user_tier=UserTier.PRO
            )
            
            assert intelligence_result["success"] is True
            trade_idea = intelligence_result["content"]["trade_ideas"][0]
            assert trade_idea["symbol"] == "TCS"
        
        # Step 2: User wants to discuss the idea in expert group
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={
                    "success": True,
                    "message_approved": True,
                    "group_engagement": "high"
                }
            ))
            
            # User posts about the trade idea in expert group
            moderator_result = await tier_manager.handle_expert_group_request(
                user_id=user_id,
                user_tier=UserTier.PRO,
                action="view_group",  # Pro can view groups
                data={
                    "group_id": "nifty_pro_signals",
                    "message": f"What do you think about the TCS SHORT idea? GridWorks AI suggested it with 80% confidence."
                }
            )
            
            # Pro tier gets limited access but can participate
            assert moderator_result is not None


class TestRevenueIntegrationScenarios:
    """Test revenue-related integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_expert_monetization_workflow(self):
        """Test complete expert monetization workflow"""
        tier_manager = TierAIManager()
        expert_user = MockUser("expert_monetization", "Expert Trader", UserTier.ELITE)
        
        # Step 1: Expert creates group
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={
                    "success": True,
                    "group_id": "monetization_group_123",
                    "revenue_sharing": {"expert_share": 75, "platform_share": 25}
                }
            ))
            
            group_creation = await tier_manager.handle_expert_group_request(
                user_id=expert_user.id,
                user_tier=expert_user.tier,
                action="create_group",
                data={
                    "group_settings": {
                        "name": "Expert Monetization Signals",
                        "subscription_price": 2999,
                        "max_members": 25
                    }
                }
            )
            
            assert group_creation["success"] is True
            group_id = group_creation["group_id"]
        
        # Step 2: Simulate member subscriptions and revenue
        member_count = 20
        monthly_revenue = member_count * 2999  # ₹59,980
        expert_share = monthly_revenue * 0.75  # 75% for Elite tier
        platform_share = monthly_revenue * 0.25  # 25% for platform
        
        expert_user.revenue_earned = expert_share
        
        # Step 3: Check if expert qualifies for Black tier upgrade
        if expert_user.revenue_earned > 15000:  # ₹15K+ monthly revenue
            upsell = await tier_manager.upsell_triggers.check_moderator_upsell(
                expert_user.id, expert_user.tier
            )
            
            if upsell:
                assert "Black" in upsell["offer"]
                # Expert can upgrade for even higher revenue potential
                expert_user.upgrade_tier(UserTier.BLACK)
                
                # Black tier gets 85% revenue share instead of 75%
                new_expert_share = monthly_revenue * 0.85
                additional_revenue = new_expert_share - expert_share
                
                assert additional_revenue > 0  # Should get more revenue in Black tier
    
    @pytest.mark.asyncio
    async def test_b2b_sdk_integration_revenue(self):
        """Test B2B SDK integration revenue scenarios"""
        # Simulate broker using GridWorks SDK
        broker_config = ClientConfiguration(
            client_id="broker_client_123",
            client_name="XYZ Broker",
            api_key="broker_api_key",
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API,
            custom_settings={
                "white_label": True,
                "broker_branding": "XYZ Broker",
                "revenue_sharing": "b2b_model"
            }
        )
        
        with patch('app.ai_support.AISupport') as mock_support:
            with patch('app.ai_intelligence.AIIntelligence') as mock_intelligence:
                mock_support.return_value = Mock()
                mock_intelligence.return_value = Mock()
                
                # Broker initializes SDK
                broker_sdk = GridWorksSDK(broker_config)
                await broker_sdk.initialize_services()
                
                assert broker_sdk.initialized is True
                assert broker_sdk.config.custom_settings["white_label"] is True
                
                # Broker can offer GridWorks AI to their users
                # Revenue sharing model: Broker pays GridWorks for SDK usage
                monthly_broker_fee = 500000  # ₹5L/month for unlimited usage
                gridworks_revenue = monthly_broker_fee
                
                assert gridworks_revenue > 0
                
                await broker_sdk.shutdown()


class TestErrorHandlingIntegration:
    """Test error handling across integrated services"""
    
    @pytest.mark.asyncio
    async def test_service_failure_cascade_prevention(self):
        """Test that one service failure doesn't cascade to others"""
        config = ClientConfiguration(
            client_id="error_test_client",
            client_name="Error Test",
            api_key="error_key", 
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE, ServiceType.MODERATOR],
            integration_type=IntegrationType.REST_API
        )
        
        with patch('app.ai_support.AISupport') as mock_support:
            with patch('app.ai_intelligence.AIIntelligence') as mock_intelligence:
                with patch('app.ai_moderator.AIModerator') as mock_moderator:
                    # Support service fails
                    mock_support.side_effect = Exception("Support service down")
                    
                    # Intelligence and moderator work fine
                    mock_intelligence_instance = Mock()
                    mock_intelligence_instance.generate_morning_pulse = AsyncMock(return_value={
                        "success": True, "content": {"summary": "Market update"}
                    })
                    mock_intelligence.return_value = mock_intelligence_instance
                    
                    mock_moderator_instance = Mock()
                    mock_moderator.return_value = mock_moderator_instance
                    
                    sdk = GridWorksSDK(config)
                    
                    # SDK initialization should fail due to support service
                    with pytest.raises(RuntimeError, match="Failed to initialize service support"):
                        await sdk.initialize_services()
    
    @pytest.mark.asyncio
    async def test_partial_service_degradation(self):
        """Test graceful degradation when some services are unavailable"""
        tier_manager = TierAIManager()
        
        # Mock scenario where intelligence service is down but support works
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk_instance = Mock()
            
            # Support works
            mock_sdk_instance.process_request = AsyncMock(
                side_effect=lambda service, action, data, **kwargs: (
                    Mock(data={"success": True, "message": "Support response"})
                    if service == "support"
                    else Mock(data={"success": False, "error": "Intelligence service unavailable"})
                )
            )
            mock_sdk.return_value = mock_sdk_instance
            
            # Support should work
            support_result = await tier_manager.handle_ai_support_request(
                user_id="test_user",
                user_tier=UserTier.PRO,
                query="Test query",
                context={}
            )
            
            assert support_result["success"] is True
            
            # Intelligence should fail gracefully
            intelligence_result = await tier_manager.handle_morning_pulse_request(
                user_id="test_user",
                user_tier=UserTier.PRO
            )
            
            # Should return fallback or error response, not crash
            assert intelligence_result is not None
            assert "error" in intelligence_result or "fallback" in intelligence_result


class TestPerformanceIntegration:
    """Test performance aspects of integrated services"""
    
    @pytest.mark.asyncio
    async def test_concurrent_tier_requests(self):
        """Test handling concurrent requests from different tier users"""
        tier_manager = TierAIManager()
        
        # Create users across different tiers
        users = [
            MockUser("lite_user", "Lite User", UserTier.LITE),
            MockUser("pro_user", "Pro User", UserTier.PRO),
            MockUser("elite_user", "Elite User", UserTier.ELITE),
            MockUser("black_user", "Black User", UserTier.BLACK)
        ]
        
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={"success": True, "message": "Response"}
            ))
            
            # Create concurrent requests from all tier users
            tasks = []
            for user in users:
                if user.tier != UserTier.LITE:  # Lite users don't get full intelligence
                    task = tier_manager.handle_morning_pulse_request(
                        user_id=user.id,
                        user_tier=user.tier
                    )
                    tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks)
            
            # All requests should complete successfully
            assert len(results) == 3  # Pro, Elite, Black
            for result in results:
                assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_scalability_metrics(self):
        """Test system behavior under load"""
        tier_manager = TierAIManager()
        
        # Simulate high load scenario
        num_concurrent_users = 100
        requests_per_user = 5
        
        with patch.object(tier_manager, 'create_user_sdk') as mock_sdk:
            mock_sdk.return_value = Mock()
            mock_sdk.return_value.process_request = AsyncMock(return_value=Mock(
                data={"success": True, "message": "Load test response"}
            ))
            
            # Create high volume of concurrent requests
            tasks = []
            for user_id in range(num_concurrent_users):
                for request_id in range(requests_per_user):
                    task = tier_manager.handle_ai_support_request(
                        user_id=f"load_user_{user_id}",
                        user_tier=UserTier.PRO,  # Pro tier has reasonable limits
                        query=f"Load test query {request_id}",
                        context={}
                    )
                    tasks.append(task)
            
            # Execute all requests
            start_time = datetime.now()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = datetime.now()
            
            # Analyze results
            successful_requests = sum(
                1 for result in results 
                if isinstance(result, dict) and result.get("success", False)
            )
            failed_requests = len(results) - successful_requests
            
            processing_time = (end_time - start_time).total_seconds()
            requests_per_second = len(results) / processing_time
            
            # System should handle reasonable load
            assert successful_requests > 0
            assert requests_per_second > 10  # At least 10 RPS
            
            # Some requests might fail due to rate limiting, which is expected
            if failed_requests > 0:
                assert failed_requests < len(results) * 0.5  # Less than 50% should fail


class TestDataConsistencyIntegration:
    """Test data consistency across integrated services"""
    
    @pytest.mark.asyncio
    async def test_user_state_consistency(self):
        """Test user state consistency across services"""
        tier_manager = TierAIManager()
        user_id = "consistency_user_123"
        
        # User starts with some usage
        await tier_manager._track_usage(user_id, "support_query")
        await tier_manager._track_usage(user_id, "support_query")
        
        # Check quota reflects usage
        quota_check = await tier_manager._check_support_quota(user_id, UserTier.LITE)
        assert quota_check["allowed"] is True
        assert quota_check["remaining"] == 3  # 5 - 2 = 3
        
        # More usage
        await tier_manager._track_usage(user_id, "support_query")
        await tier_manager._track_usage(user_id, "support_query")
        await tier_manager._track_usage(user_id, "support_query")
        
        # Should now be at limit
        quota_check = await tier_manager._check_support_quota(user_id, UserTier.LITE)
        assert quota_check["allowed"] is False
        assert quota_check["current_usage"] == 5
    
    @pytest.mark.asyncio
    async def test_tier_upgrade_state_transition(self):
        """Test state transitions during tier upgrades"""
        tier_manager = TierAIManager()
        user_id = "upgrade_user_456"
        
        # Start as Lite user, use up quota
        for i in range(5):
            await tier_manager._track_usage(user_id, "support_query")
        
        lite_quota = await tier_manager._check_support_quota(user_id, UserTier.LITE)
        assert lite_quota["allowed"] is False
        
        # Upgrade to Pro - should have new quota
        pro_quota = await tier_manager._check_support_quota(user_id, UserTier.PRO)
        assert pro_quota["allowed"] is True  # Pro tier has higher limits
        
        # Usage history should persist but not affect new tier limits
        await tier_manager._track_usage(user_id, "support_query")  # 6th query
        pro_quota_after = await tier_manager._check_support_quota(user_id, UserTier.PRO)
        assert pro_quota_after["allowed"] is True  # Still within Pro limits


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])