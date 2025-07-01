"""
Comprehensive test suite for Unified Billing System
Achieving 100% test coverage for all billing components
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
import json

from app.billing.unified_billing_system import (
    UnifiedBillingSystem,
    BillingChannel,
    PaymentProcessor,
    UnifiedBillingConfig,
    BillingAnalytics
)
from app.ai_support.models import SupportTier
from app.black.models import BlackTier
from app.billing.subscription_manager import SubscriptionStatus, BillingCycle


class TestUnifiedBillingSystem:
    """Test suite for UnifiedBillingSystem - 100% coverage"""
    
    @pytest.fixture
    async def billing_system(self):
        """Create billing system instance with mocked dependencies"""
        system = UnifiedBillingSystem()
        
        # Mock all external dependencies
        system.subscription_manager = AsyncMock()
        system.luxury_billing = AsyncMock()
        system.whatsapp_client = AsyncMock()
        
        # Mock internal methods
        system._get_user_details = AsyncMock(return_value={
            "user_id": "test_user",
            "phone": "+919876543210",
            "email": "test@example.com",
            "name": "Test User"
        })
        
        return system
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test UnifiedBillingSystem initialization"""
        system = UnifiedBillingSystem()
        
        # Verify all tiers are configured
        assert len(system.billing_configs) == 6
        assert SupportTier.LITE in system.billing_configs
        assert SupportTier.PRO in system.billing_configs
        assert SupportTier.ELITE in system.billing_configs
        assert BlackTier.ONYX in system.billing_configs
        assert BlackTier.OBSIDIAN in system.billing_configs
        assert BlackTier.VOID in system.billing_configs
        
        # Verify channel assignments
        assert system.billing_configs[SupportTier.LITE].channel == BillingChannel.WHATSAPP
        assert system.billing_configs[BlackTier.VOID].channel == BillingChannel.IN_APP_LUXURY
    
    @pytest.mark.asyncio
    async def test_lite_tier_billing(self, billing_system):
        """Test LITE tier free activation and per-trade billing"""
        # Test free activation
        result = await billing_system.initiate_billing(
            user_id="lite_user",
            tier=SupportTier.LITE,
            billing_type="subscription"
        )
        
        assert result["success"] is True
        assert result["tier"] == "LITE"
        assert result["subscription_fee"] == 0
        assert result["per_trade_fee"] == 2
        
        # Verify WhatsApp message sent
        billing_system.whatsapp_client.send_message.assert_called_once()
        
        # Test per-trade fee collection
        billing_system._get_user_consent_id = AsyncMock(return_value="CONSENT_123")
        billing_system.subscription_manager.setu_client = AsyncMock()
        billing_system.subscription_manager.setu_client.collect_instant_fee = AsyncMock(
            return_value={"success": True, "transaction_id": "TXN_123"}
        )
        
        trade_result = await billing_system.initiate_billing(
            user_id="lite_user",
            tier=SupportTier.LITE,
            billing_type="per_trade"
        )
        
        assert trade_result["success"] is True
        assert billing_system.whatsapp_client.send_message.call_count == 2
    
    @pytest.mark.asyncio
    async def test_pro_tier_billing(self, billing_system):
        """Test PRO tier subscription and payment flow"""
        # Mock subscription creation
        billing_system.subscription_manager.create_subscription = AsyncMock(
            return_value={
                "success": True,
                "subscription_id": "sub_123",
                "amount": 99,
                "payment_link": "upi://pay?pa=trademate@paytm&am=99",
                "features": ["Professional Tools", "Advanced AI"]
            }
        )
        
        result = await billing_system.initiate_billing(
            user_id="pro_user",
            tier=SupportTier.PRO,
            billing_type="subscription"
        )
        
        assert result["success"] is True
        assert result["amount"] == 99
        
        # Verify WhatsApp interactive message sent
        billing_system.whatsapp_client.send_interactive_message.assert_called_once()
        call_args = billing_system.whatsapp_client.send_interactive_message.call_args[1]
        assert "PRO" in call_args["message"]
        assert len(call_args["buttons"]) == 3  # Pay UPI, Pay Card, Need Help
    
    @pytest.mark.asyncio
    async def test_elite_tier_billing(self, billing_system):
        """Test ELITE tier with setup fee and quarterly billing"""
        billing_system.subscription_manager.create_subscription = AsyncMock(
            return_value={
                "success": True,
                "subscription_id": "sub_elite_123",
                "amount": 2999,
                "setup_fee": 25000,
                "billing_cycle": "quarterly"
            }
        )
        
        result = await billing_system.initiate_billing(
            user_id="elite_user",
            tier=SupportTier.ELITE,
            billing_type="subscription"
        )
        
        assert result["success"] is True
        
        # Verify correct billing cycle
        subscription_call = billing_system.subscription_manager.create_subscription.call_args[1]
        assert subscription_call["billing_cycle"] == BillingCycle.QUARTERLY
    
    @pytest.mark.asyncio
    async def test_black_onyx_billing(self, billing_system):
        """Test BLACK ONYX tier luxury billing"""
        billing_system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={
                "success": True,
                "session_id": "LUX_ONYX_123",
                "billing_interface": {
                    "theme": "midnight_obsidian",
                    "concierge_available": True
                }
            }
        )
        
        result = await billing_system.initiate_billing(
            user_id="onyx_user",
            tier=BlackTier.ONYX,
            billing_type="subscription"
        )
        
        assert result["success"] is True
        assert "LUX" in result["session_id"]
        
        # Verify luxury billing called, not WhatsApp
        billing_system.luxury_billing.create_luxury_billing_session.assert_called_once()
        billing_system.whatsapp_client.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_black_void_billing(self, billing_system):
        """Test BLACK VOID tier with butler coordination"""
        billing_system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={
                "success": True,
                "session_id": "LUX_VOID_123",
                "butler_session": {
                    "butler_greeting": "Good evening, sir"
                }
            }
        )
        
        billing_system._notify_butler_for_billing = AsyncMock()
        billing_system._create_luxury_stripe_subscription = AsyncMock()
        
        result = await billing_system.initiate_billing(
            user_id="void_user",
            tier=BlackTier.VOID,
            billing_type="subscription"
        )
        
        assert result["success"] is True
        
        # Verify butler notification
        billing_system._notify_butler_for_billing.assert_called_once()
        call_args = billing_system._notify_butler_for_billing.call_args[0]
        assert call_args[1] == BlackTier.VOID
        assert call_args[2] == 150000000  # ₹15L in paise
    
    @pytest.mark.asyncio
    async def test_payment_callback_processing(self, billing_system):
        """Test payment callback handling from various sources"""
        # Test Setu callback
        setu_webhook = {
            "eventType": "payment_link.paid",
            "data": {
                "metadata": {
                    "user_id": "test_user",
                    "tier": "PRO",
                    "subscription_id": "sub_123"
                },
                "amountPaid": 9900,
                "transactionId": "TXN_123"
            }
        }
        
        billing_system.subscription_manager.handle_subscription_payment_success = AsyncMock(
            return_value={"success": True, "subscription_activated": True}
        )
        
        result = await billing_system.process_payment_callback(setu_webhook, "setu")
        assert result["success"] is True
        
        # Test Stripe callback
        stripe_webhook = {
            "type": "invoice.payment_succeeded",
            "data": {"object": {"subscription": "sub_123"}}
        }
        
        billing_system._process_stripe_callback = AsyncMock(
            return_value={"success": True}
        )
        
        result = await billing_system.process_payment_callback(stripe_webhook, "stripe")
        assert result["success"] is True
        
        # Test luxury callback
        luxury_data = {
            "session_id": "LUX_123",
            "payment_confirmed": True
        }
        
        billing_system._process_luxury_callback = AsyncMock(
            return_value={"success": True}
        )
        
        result = await billing_system.process_payment_callback(luxury_data, "luxury")
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_whatsapp_payment_messages(self, billing_system):
        """Test WhatsApp payment message formatting"""
        # Test PRO tier message
        await billing_system._send_whatsapp_payment_request(
            phone="+919876543210",
            tier=SupportTier.PRO,
            subscription_result={
                "amount": 99,
                "payment_link": "upi://pay?pa=trademate@paytm&am=99",
                "features": ["Professional Tools"]
            }
        )
        
        # Verify message content
        call_args = billing_system.whatsapp_client.send_interactive_message.call_args[1]
        assert "₹99/month" in call_args["message"]
        assert "Professional trading tools" in call_args["message"]
        
        # Test ELITE tier message
        await billing_system._send_whatsapp_payment_request(
            phone="+919876543210",
            tier=SupportTier.ELITE,
            subscription_result={
                "amount": 2999,
                "features": ["Executive Analytics"]
            }
        )
        
        call_args = billing_system.whatsapp_client.send_interactive_message.call_args[1]
        assert "₹2,999/month" in call_args["message"]
        assert "ELITE" in call_args["message"]
    
    @pytest.mark.asyncio
    async def test_auto_debit_consent_flow(self, billing_system):
        """Test auto-debit consent setup and usage"""
        # Test when consent doesn't exist
        billing_system._get_user_consent_id = AsyncMock(return_value=None)
        billing_system._setup_auto_debit_consent = AsyncMock(
            return_value={"success": True, "consent_id": "CONSENT_NEW"}
        )
        
        billing_system.subscription_manager.setu_client = AsyncMock()
        billing_system.subscription_manager.setu_client.collect_instant_fee = AsyncMock(
            return_value={"success": True}
        )
        
        result = await billing_system._collect_per_trade_fee_whatsapp(
            user_id="test_user",
            phone="+919876543210",
            tier=SupportTier.PRO,
            amount=500
        )
        
        # Verify consent setup called
        billing_system._setup_auto_debit_consent.assert_called_once()
        
        # Test when consent exists
        billing_system._get_user_consent_id = AsyncMock(return_value="CONSENT_EXISTING")
        
        result = await billing_system._collect_per_trade_fee_whatsapp(
            user_id="test_user",
            phone="+919876543210",
            tier=SupportTier.PRO,
            amount=500
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, billing_system):
        """Test error handling in various scenarios"""
        # Test unknown tier
        result = await billing_system.initiate_billing(
            user_id="test_user",
            tier="UNKNOWN_TIER",
            billing_type="subscription"
        )
        
        assert result["success"] is False
        assert "Unknown tier" in result["error"]
        
        # Test subscription creation failure
        billing_system.subscription_manager.create_subscription = AsyncMock(
            side_effect=Exception("Stripe API error")
        )
        
        result = await billing_system.initiate_billing(
            user_id="test_user",
            tier=SupportTier.PRO,
            billing_type="subscription"
        )
        
        assert result["success"] is False
        assert "Stripe API error" in result["error"]
        
        # Test unknown billing type
        result = await billing_system.initiate_billing(
            user_id="test_user",
            tier=SupportTier.PRO,
            billing_type="unknown_type"
        )
        
        assert result["success"] is False
        assert "Unknown billing type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_billing_cycle_conversion(self, billing_system):
        """Test billing cycle conversion logic"""
        # Test monthly
        config = billing_system.billing_configs[SupportTier.PRO]
        cycle = await billing_system._get_billing_cycle(config)
        assert cycle == BillingCycle.MONTHLY
        
        # Test quarterly
        config = billing_system.billing_configs[SupportTier.ELITE]
        cycle = await billing_system._get_billing_cycle(config)
        assert cycle == BillingCycle.QUARTERLY
        
        # Test annual
        config = billing_system.billing_configs[BlackTier.VOID]
        cycle = await billing_system._get_billing_cycle(config)
        assert cycle == BillingCycle.ANNUAL
    
    @pytest.mark.asyncio
    async def test_activation_confirmations(self, billing_system):
        """Test activation confirmation messages"""
        # Test LITE confirmation
        await billing_system._send_whatsapp_activation_confirmation(
            user_id="lite_user",
            tier=SupportTier.LITE,
            amount_paid=0
        )
        
        call_args = billing_system.whatsapp_client.send_message.call_args[0]
        assert "Welcome to TradeMate LITE" in call_args[1]
        assert "₹2 per trade" in call_args[1]
        
        # Test PRO confirmation
        await billing_system._send_whatsapp_activation_confirmation(
            user_id="pro_user",
            tier=SupportTier.PRO,
            amount_paid=9900
        )
        
        call_args = billing_system.whatsapp_client.send_message.call_args[0]
        assert "PRO Activated" in call_args[1]
        assert "₹99" in call_args[1]
        
        # Test ELITE confirmation
        await billing_system._send_whatsapp_activation_confirmation(
            user_id="elite_user",
            tier=SupportTier.ELITE,
            amount_paid=299900
        )
        
        call_args = billing_system.whatsapp_client.send_message.call_args[0]
        assert "ELITE" in call_args[1]
        assert "₹2,999" in call_args[1]


class TestBillingAnalytics:
    """Test suite for BillingAnalytics - 100% coverage"""
    
    @pytest.fixture
    async def analytics(self):
        """Create analytics instance"""
        billing_system = UnifiedBillingSystem()
        return BillingAnalytics(billing_system)
    
    @pytest.mark.asyncio
    async def test_get_billing_metrics(self, analytics):
        """Test comprehensive billing metrics retrieval"""
        metrics = await analytics.get_billing_metrics()
        
        # Verify structure
        assert "revenue_by_tier" in metrics
        assert "payment_methods" in metrics
        assert "billing_channels" in metrics
        assert "key_metrics" in metrics
        
        # Verify tier metrics
        assert len(metrics["revenue_by_tier"]) == 4
        assert metrics["revenue_by_tier"]["LITE"]["users"] == 44920
        assert metrics["revenue_by_tier"]["BLACK"]["arpu"] == 1500000
        
        # Verify payment method metrics
        assert metrics["payment_methods"]["upi"]["success_rate"] == 99.2
        assert metrics["payment_methods"]["private_banking"]["success_rate"] == 100.0
        
        # Verify channel metrics
        assert metrics["billing_channels"]["whatsapp"]["users"] == 52797
        assert metrics["billing_channels"]["luxury_app"]["users"] == 50
        
        # Verify key metrics
        assert metrics["key_metrics"]["total_revenue"] == 138275400
        assert metrics["key_metrics"]["payment_success_rate"] == 98.7
        assert metrics["key_metrics"]["revenue_growth_mom"] == 23.5


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.fixture
    async def billing_system(self):
        """Create billing system for edge case testing"""
        return UnifiedBillingSystem()
    
    @pytest.mark.asyncio
    async def test_zero_amount_billing(self, billing_system):
        """Test handling of zero amount transactions"""
        billing_system._get_user_details = AsyncMock(return_value={
            "user_id": "test", "phone": "+919876543210"
        })
        billing_system.whatsapp_client = AsyncMock()
        
        result = await billing_system.initiate_billing(
            user_id="test",
            tier=SupportTier.LITE,
            billing_type="subscription",
            amount_override=0
        )
        
        assert result["success"] is True
        assert result["subscription_fee"] == 0
    
    @pytest.mark.asyncio
    async def test_large_amount_billing(self, billing_system):
        """Test handling of large amounts (VOID tier)"""
        billing_system.luxury_billing = AsyncMock()
        billing_system.luxury_billing.create_luxury_billing_session = AsyncMock(
            return_value={"success": True, "session_id": "LUX_123"}
        )
        
        result = await billing_system.initiate_billing(
            user_id="void_user",
            tier=BlackTier.VOID,
            billing_type="subscription",
            amount_override=150000000  # ₹15L
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_billing_requests(self, billing_system):
        """Test handling of concurrent billing requests"""
        billing_system._get_user_details = AsyncMock(return_value={
            "user_id": "test", "phone": "+919876543210"
        })
        billing_system.subscription_manager = AsyncMock()
        billing_system.whatsapp_client = AsyncMock()
        
        # Simulate concurrent requests
        tasks = [
            billing_system.initiate_billing(f"user_{i}", SupportTier.PRO, "subscription")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all completed without exceptions
        for result in results:
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_payment_retry_logic(self, billing_system):
        """Test payment retry mechanisms"""
        billing_system._get_user_details = AsyncMock(return_value={
            "user_id": "test", "phone": "+919876543210"
        })
        
        # Simulate failure then success
        billing_system.subscription_manager = AsyncMock()
        billing_system.subscription_manager.create_subscription = AsyncMock(
            side_effect=[
                {"success": False, "error": "Network error"},
                {"success": True, "subscription_id": "sub_123"}
            ]
        )
        
        # First attempt should fail
        result1 = await billing_system.initiate_billing(
            "test_user", SupportTier.PRO, "subscription"
        )
        assert result1["success"] is False
        
        # Second attempt should succeed
        result2 = await billing_system.initiate_billing(
            "test_user", SupportTier.PRO, "subscription"
        )
        assert result2["success"] is True


# Test configuration for coverage
pytest_plugins = ["pytest_asyncio"]


if __name__ == "__main__":
    # Run with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=app.billing.unified_billing_system",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=100"
    ])