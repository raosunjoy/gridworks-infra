"""
Integration tests for complete billing flows
Testing end-to-end scenarios across all tiers
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json

from app.billing.unified_billing_system import UnifiedBillingSystem
from app.billing.subscription_manager import SubscriptionManager
from app.black.luxury_billing import BlackTierLuxuryBilling, LuxuryPaymentMethod
from app.ai_support.models import SupportTier
from app.black.models import BlackTier


class TestBillingIntegrationFlows:
    """Integration tests for complete billing flows"""
    
    @pytest.fixture
    async def integrated_system(self):
        """Create fully integrated billing system"""
        system = UnifiedBillingSystem()
        
        # Mock external APIs but keep internal logic
        with patch('stripe.Customer.create') as mock_stripe_customer:
            mock_stripe_customer.return_value = {"id": "cus_test123"}
            
            with patch('stripe.Subscription.create') as mock_stripe_sub:
                mock_stripe_sub.return_value = {
                    "id": "sub_test123",
                    "status": "active"
                }
                
                # Mock Setu API
                system.subscription_manager.setu_client = AsyncMock()
                system.subscription_manager.setu_client.create_payment_link = AsyncMock(
                    return_value={
                        "payment_url": "upi://pay?pa=test",
                        "payment_id": "PAY_123"
                    }
                )
                
                # Mock WhatsApp client
                system.whatsapp_client = AsyncMock()
                
                yield system
    
    @pytest.mark.asyncio
    async def test_lite_user_journey(self, integrated_system):
        """Test complete LITE user journey from signup to trading"""
        # Step 1: User signs up for LITE (free tier)
        signup_result = await integrated_system.initiate_billing(
            user_id="lite_journey_001",
            tier=SupportTier.LITE,
            billing_type="subscription"
        )
        
        assert signup_result["success"] is True
        assert signup_result["subscription_fee"] == 0
        assert signup_result["per_trade_fee"] == 2
        
        # Verify welcome message sent
        integrated_system.whatsapp_client.send_message.assert_called()
        welcome_msg = integrated_system.whatsapp_client.send_message.call_args[0][1]
        assert "Welcome to TradeMate LITE" in welcome_msg
        
        # Step 2: User makes first trade
        integrated_system._get_user_consent_id = AsyncMock(return_value=None)
        integrated_system._setup_auto_debit_consent = AsyncMock(
            return_value={"success": True, "consent_id": "CONSENT_LITE_001"}
        )
        
        integrated_system.subscription_manager.setu_client.collect_instant_fee = AsyncMock(
            return_value={
                "success": True,
                "transaction_id": "TXN_LITE_001",
                "amount": 200
            }
        )
        
        trade_result = await integrated_system.initiate_billing(
            user_id="lite_journey_001",
            tier=SupportTier.LITE,
            billing_type="per_trade",
            amount_override=200  # ₹2 fee
        )
        
        assert trade_result["success"] is True
        
        # Verify auto-debit consent setup
        integrated_system._setup_auto_debit_consent.assert_called_once()
        
        # Verify fee collection
        integrated_system.subscription_manager.setu_client.collect_instant_fee.assert_called_once()
        
        # Verify trade confirmation sent
        assert integrated_system.whatsapp_client.send_message.call_count >= 2
        trade_msg = integrated_system.whatsapp_client.send_message.call_args[0][1]
        assert "₹2" in trade_msg
    
    @pytest.mark.asyncio
    async def test_pro_upgrade_journey(self, integrated_system):
        """Test LITE to PRO upgrade journey"""
        # Step 1: LITE user requests PRO upgrade
        integrated_system.subscription_manager.create_subscription = AsyncMock(
            return_value={
                "success": True,
                "subscription_id": "sub_pro_001",
                "amount": 99,
                "payment_link": "upi://pay?pa=trademate@paytm&am=99",
                "features": ["Professional Tools", "Voice Trading"]
            }
        )
        
        upgrade_result = await integrated_system.initiate_billing(
            user_id="upgrade_journey_001",
            tier=SupportTier.PRO,
            billing_type="subscription"
        )
        
        assert upgrade_result["success"] is True
        assert upgrade_result["amount"] == 99
        
        # Verify interactive upgrade message
        integrated_system.whatsapp_client.send_interactive_message.assert_called()
        interactive_msg = integrated_system.whatsapp_client.send_interactive_message.call_args[1]
        assert "₹99/month" in interactive_msg["message"]
        assert len(interactive_msg["buttons"]) == 3
        
        # Step 2: Simulate payment success callback
        webhook_data = {
            "eventType": "payment_link.paid",
            "data": {
                "metadata": {
                    "user_id": "upgrade_journey_001",
                    "tier": "PRO",
                    "subscription_id": "sub_pro_001"
                },
                "amountPaid": 9900,
                "transactionId": "TXN_PRO_001"
            }
        }
        
        integrated_system.subscription_manager.handle_subscription_payment_success = AsyncMock(
            return_value={"success": True, "subscription_activated": True}
        )
        
        callback_result = await integrated_system.process_payment_callback(
            webhook_data, "setu"
        )
        
        assert callback_result["success"] is True
        
        # Verify activation confirmation sent
        assert integrated_system.whatsapp_client.send_message.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_elite_onboarding_journey(self, integrated_system):
        """Test ELITE tier onboarding with setup fee"""
        # ELITE requires setup fee + subscription
        integrated_system.subscription_manager.create_subscription = AsyncMock(
            return_value={
                "success": True,
                "subscription_id": "sub_elite_001",
                "amount": 2999,
                "setup_fee": 25000,
                "payment_link": "upi://pay?pa=trademate@paytm&am=27999",
                "billing_cycle": "quarterly"
            }
        )
        
        elite_result = await integrated_system.initiate_billing(
            user_id="elite_journey_001",
            tier=SupportTier.ELITE,
            billing_type="subscription"
        )
        
        assert elite_result["success"] is True
        
        # Verify premium messaging
        interactive_msg = integrated_system.whatsapp_client.send_interactive_message.call_args[1]
        assert "ELITE" in interactive_msg["message"]
        assert "₹2,999/month" in interactive_msg["message"]
    
    @pytest.mark.asyncio
    async def test_black_onyx_journey(self, integrated_system):
        """Test BLACK ONYX tier luxury journey"""
        # BLACK tiers use luxury billing, not WhatsApp
        integrated_system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={
                "success": True,
                "session_id": "LUX_ONYX_001",
                "billing_interface": {
                    "title": "◼ ONYX MEMBERSHIP BILLING",
                    "billing_amount": 84000,
                    "theme_colors": {"primary": "#1a1a1a"},
                    "payment_methods": [
                        {"id": "private_banking", "name": "Private Banking"}
                    ]
                },
                "concierge_available": True
            }
        )
        
        onyx_result = await integrated_system.initiate_billing(
            user_id="onyx_journey_001",
            tier=BlackTier.ONYX,
            billing_type="subscription"
        )
        
        assert onyx_result["success"] is True
        assert "LUX" in onyx_result["session_id"]
        
        # Verify NO WhatsApp messages sent for Black tier
        integrated_system.whatsapp_client.send_message.assert_not_called()
        integrated_system.whatsapp_client.send_interactive_message.assert_not_called()
        
        # Verify luxury billing used
        integrated_system.luxury_billing.create_luxury_billing_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_black_void_ultimate_journey(self, integrated_system):
        """Test BLACK VOID tier with butler coordination"""
        integrated_system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={
                "success": True,
                "session_id": "LUX_VOID_001",
                "billing_interface": {
                    "title": "🕳️ VOID ULTIMATE BILLING",
                    "billing_amount": 1500000,
                    "butler_session": {
                        "butler_session_id": "BUTLER_VOID_001",
                        "butler_greeting": "Good evening, sir. Shall I proceed?"
                    }
                }
            }
        )
        
        integrated_system._notify_butler_for_billing = AsyncMock()
        integrated_system._create_luxury_stripe_subscription = AsyncMock()
        
        void_result = await integrated_system.initiate_billing(
            user_id="void_journey_001",
            tier=BlackTier.VOID,
            billing_type="subscription"
        )
        
        assert void_result["success"] is True
        assert "butler_session" in void_result["billing_interface"]
        
        # Verify butler notification
        integrated_system._notify_butler_for_billing.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_payment_failure_recovery(self, integrated_system):
        """Test payment failure and recovery flow"""
        # Simulate payment failure
        integrated_system.subscription_manager.create_subscription = AsyncMock(
            return_value={
                "success": True,
                "subscription_id": "sub_fail_001",
                "payment_link": "upi://pay?pa=trademate@paytm&am=99"
            }
        )
        
        # Create subscription
        await integrated_system.initiate_billing(
            user_id="failure_test_001",
            tier=SupportTier.PRO,
            billing_type="subscription"
        )
        
        # Simulate payment failure webhook
        failure_webhook = {
            "eventType": "payment_link.expired",
            "data": {
                "referenceId": "PAY_FAIL_001",
                "metadata": {"user_id": "failure_test_001"}
            }
        }
        
        failure_result = await integrated_system.process_payment_callback(
            failure_webhook, "setu"
        )
        
        assert failure_result["success"] is True
        assert failure_result["event_processed"] == "payment_link.expired"
    
    @pytest.mark.asyncio
    async def test_multi_tier_concurrent_billing(self, integrated_system):
        """Test concurrent billing across multiple tiers"""
        # Mock all dependencies
        integrated_system._get_user_details = AsyncMock(
            return_value={"user_id": "test", "phone": "+919876543210"}
        )
        
        integrated_system.subscription_manager.create_subscription = AsyncMock(
            return_value={"success": True, "subscription_id": "sub_123"}
        )
        
        integrated_system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={"success": True, "session_id": "LUX_123"}
        )
        
        # Create billing requests for all tiers
        tasks = [
            integrated_system.initiate_billing("lite_001", SupportTier.LITE, "subscription"),
            integrated_system.initiate_billing("pro_001", SupportTier.PRO, "subscription"),
            integrated_system.initiate_billing("elite_001", SupportTier.ELITE, "subscription"),
            integrated_system.initiate_billing("onyx_001", BlackTier.ONYX, "subscription"),
            integrated_system.initiate_billing("obsidian_001", BlackTier.OBSIDIAN, "subscription"),
            integrated_system.initiate_billing("void_001", BlackTier.VOID, "subscription")
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for result in results:
            assert result["success"] is True
        
        # Verify correct channels used
        whatsapp_calls = integrated_system.whatsapp_client.send_message.call_count
        whatsapp_calls += integrated_system.whatsapp_client.send_interactive_message.call_count
        luxury_calls = integrated_system.luxury_billing.create_luxury_billing_session.call_count
        
        assert whatsapp_calls >= 3  # LITE, PRO, ELITE
        assert luxury_calls == 3  # ONYX, OBSIDIAN, VOID


class TestBillingAnalyticsIntegration:
    """Test billing analytics with real data flow"""
    
    @pytest.mark.asyncio
    async def test_analytics_after_transactions(self):
        """Test analytics calculations after various transactions"""
        from app.billing.unified_billing_system import BillingAnalytics
        
        system = UnifiedBillingSystem()
        analytics = BillingAnalytics(system)
        
        # Get initial metrics
        metrics = await analytics.get_billing_metrics()
        
        # Verify structure
        assert metrics["revenue_by_tier"]["LITE"]["users"] == 44920
        assert metrics["revenue_by_tier"]["BLACK"]["users"] == 50
        assert metrics["key_metrics"]["total_revenue"] == 138275400
        
        # Verify channel split
        whatsapp_revenue = metrics["billing_channels"]["whatsapp"]["revenue"]
        luxury_revenue = metrics["billing_channels"]["luxury_app"]["revenue"]
        total_revenue = metrics["key_metrics"]["total_revenue"]
        
        assert whatsapp_revenue + luxury_revenue == total_revenue
        
        # Verify payment method distribution
        total_volume = sum(
            m["volume"] for m in metrics["payment_methods"].values()
        )
        assert abs(total_volume - 100.0) < 0.1  # Should sum to ~100%


class TestEndToEndScenarios:
    """Test complete end-to-end billing scenarios"""
    
    @pytest.mark.asyncio
    async def test_new_user_to_black_tier_journey(self):
        """Test journey from new user to BLACK tier"""
        system = UnifiedBillingSystem()
        
        # Mock all external dependencies
        system._get_user_details = AsyncMock(
            return_value={"user_id": "journey_001", "phone": "+919876543210"}
        )
        system.whatsapp_client = AsyncMock()
        system.subscription_manager = AsyncMock()
        system.luxury_billing = AsyncMock()
        
        # Step 1: Start as LITE user
        system.subscription_manager.create_subscription = AsyncMock(
            return_value={"success": True, "tier": "LITE"}
        )
        
        lite_result = await system.initiate_billing(
            "journey_001", SupportTier.LITE, "subscription"
        )
        assert lite_result["success"] is True
        
        # Step 2: Upgrade to PRO after 3 months
        system.subscription_manager.create_subscription = AsyncMock(
            return_value={"success": True, "tier": "PRO", "amount": 99}
        )
        
        pro_result = await system.initiate_billing(
            "journey_001", SupportTier.PRO, "subscription"
        )
        assert pro_result["success"] is True
        
        # Step 3: Upgrade to ELITE after 6 months
        system.subscription_manager.create_subscription = AsyncMock(
            return_value={"success": True, "tier": "ELITE", "amount": 2999}
        )
        
        elite_result = await system.initiate_billing(
            "journey_001", SupportTier.ELITE, "subscription"
        )
        assert elite_result["success"] is True
        
        # Step 4: Finally qualify for BLACK ONYX
        system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={
                "success": True,
                "session_id": "LUX_JOURNEY_001",
                "tier": "ONYX"
            }
        )
        
        black_result = await system.initiate_billing(
            "journey_001", BlackTier.ONYX, "subscription"
        )
        assert black_result["success"] is True
        
        # Verify transition from WhatsApp to Luxury billing
        assert system.whatsapp_client.send_message.call_count >= 3  # LITE, PRO, ELITE
        assert system.luxury_billing.create_luxury_billing_session.call_count == 1  # BLACK


# Test configuration
pytest_plugins = ["pytest_asyncio"]


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "--cov=app.billing",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])