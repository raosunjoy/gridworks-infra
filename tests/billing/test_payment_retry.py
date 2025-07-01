"""
Comprehensive test suite for Payment Retry System
100% test coverage for intelligent payment failure handling
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import json

from app.billing.payment_retry import (
    PaymentRetrySystem,
    PaymentFailure,
    GracePeriod,
    FailureType,
    RetryStrategy,
    FailureStatus
)
from app.ai_support.models import SupportTier
from app.black.models import BlackTier


class TestPaymentRetrySystem:
    """Test PaymentRetrySystem functionality"""
    
    @pytest.fixture
    def retry_system(self):
        """Create PaymentRetrySystem instance for testing"""
        return PaymentRetrySystem()
    
    @pytest.fixture
    def sample_failure(self):
        """Create sample payment failure for testing"""
        return PaymentFailure(
            failure_id="FAIL_TEST123",
            user_id="test_user_001",
            tier=SupportTier.PRO,
            transaction_id="TXN_TEST123",
            amount=9900,  # ₹99
            failure_type=FailureType.INSUFFICIENT_FUNDS,
            failure_reason="Insufficient balance",
            status=FailureStatus.PENDING,
            max_retries=5
        )
    
    @pytest.mark.asyncio
    async def test_handle_payment_failure_success(self, retry_system):
        """Test successful payment failure handling"""
        
        with patch.object(retry_system, '_store_payment_failure') as mock_store, \
             patch.object(retry_system, '_schedule_retry') as mock_schedule:
            
            mock_store.return_value = None
            mock_schedule.return_value = {
                "success": True,
                "failure_id": "FAIL_TEST123",
                "status": "retry_scheduled"
            }
            
            result = await retry_system.handle_payment_failure(
                user_id="test_user_001",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST123",
                amount=9900,
                failure_type=FailureType.INSUFFICIENT_FUNDS,
                failure_reason="Insufficient balance"
            )
            
            assert result["success"] is True
            assert result["status"] == "retry_scheduled"
            assert "failure_id" in result
            mock_store.assert_called_once()
            mock_schedule.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_no_retry_failure(self, retry_system):
        """Test handling of failures that don't support retry"""
        
        with patch.object(retry_system, '_store_payment_failure') as mock_store, \
             patch.object(retry_system, '_handle_no_retry_failure') as mock_no_retry:
            
            mock_store.return_value = None
            mock_no_retry.return_value = {
                "success": False,
                "status": "user_action_required",
                "action_required": "update_payment_method"
            }
            
            result = await retry_system.handle_payment_failure(
                user_id="test_user_001",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST123",
                amount=9900,
                failure_type=FailureType.CONSENT_REVOKED,
                failure_reason="User revoked consent"
            )
            
            assert result["success"] is False
            assert result["status"] == "user_action_required"
            assert result["action_required"] == "update_payment_method"
    
    @pytest.mark.asyncio
    async def test_calculate_next_retry_exponential_backoff(self, retry_system, sample_failure):
        """Test exponential backoff retry timing"""
        
        # Test first retry (1 minute)
        sample_failure.retry_count = 0
        next_retry = await retry_system._calculate_next_retry(
            sample_failure, RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        expected_time = datetime.now() + timedelta(minutes=1)
        time_diff = abs((next_retry - expected_time).total_seconds())
        assert time_diff < 5  # Within 5 seconds tolerance
        
        # Test second retry (2 minutes)
        sample_failure.retry_count = 1
        next_retry = await retry_system._calculate_next_retry(
            sample_failure, RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        expected_time = datetime.now() + timedelta(minutes=2)
        time_diff = abs((next_retry - expected_time).total_seconds())
        assert time_diff < 5
    
    @pytest.mark.asyncio
    async def test_calculate_next_retry_linear_backoff(self, retry_system, sample_failure):
        """Test linear backoff retry timing"""
        
        # Test first retry (5 minutes)
        sample_failure.retry_count = 0
        next_retry = await retry_system._calculate_next_retry(
            sample_failure, RetryStrategy.LINEAR_BACKOFF
        )
        
        expected_time = datetime.now() + timedelta(minutes=5)
        time_diff = abs((next_retry - expected_time).total_seconds())
        assert time_diff < 5
        
        # Test second retry (10 minutes)
        sample_failure.retry_count = 1
        next_retry = await retry_system._calculate_next_retry(
            sample_failure, RetryStrategy.LINEAR_BACKOFF
        )
        
        expected_time = datetime.now() + timedelta(minutes=10)
        time_diff = abs((next_retry - expected_time).total_seconds())
        assert time_diff < 5
    
    @pytest.mark.asyncio
    async def test_calculate_next_retry_scheduled(self, retry_system, sample_failure):
        """Test scheduled retry timing for insufficient funds"""
        
        sample_failure.failure_type = FailureType.INSUFFICIENT_FUNDS
        next_retry = await retry_system._calculate_next_retry(
            sample_failure, RetryStrategy.SCHEDULED_RETRY
        )
        
        # Should be scheduled for next day at 9 AM
        expected_time = (datetime.now() + timedelta(days=1)).replace(
            hour=9, minute=0, second=0, microsecond=0
        )
        time_diff = abs((next_retry - expected_time).total_seconds())
        assert time_diff < 5
    
    @pytest.mark.asyncio
    async def test_execute_retry_attempt_success(self, retry_system):
        """Test successful retry attempt execution"""
        
        with patch.object(retry_system, '_get_payment_failure') as mock_get, \
             patch.object(retry_system, '_update_payment_failure') as mock_update, \
             patch.object(retry_system, '_attempt_payment_retry') as mock_attempt, \
             patch.object(retry_system, '_send_failure_notification') as mock_notify:
            
            # Mock failure that can be retried
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.INSUFFICIENT_FUNDS,
                failure_reason="Insufficient balance",
                status=FailureStatus.RETRYING,
                retry_count=1,
                max_retries=5
            )
            
            mock_get.return_value = mock_failure
            mock_update.return_value = None
            mock_attempt.return_value = {
                "success": True,
                "transaction_id": "TXN_RETRY_SUCCESS"
            }
            mock_notify.return_value = None
            
            result = await retry_system.execute_retry_attempt("FAIL_TEST123")
            
            assert result["success"] is True
            assert result["status"] == "resolved"
            assert result["transaction_id"] == "TXN_RETRY_SUCCESS"
            assert result["retry_count"] == 2  # Incremented
    
    @pytest.mark.asyncio
    async def test_execute_retry_attempt_max_retries_exceeded(self, retry_system):
        """Test retry attempt when max retries exceeded"""
        
        with patch.object(retry_system, '_get_payment_failure') as mock_get, \
             patch.object(retry_system, '_handle_max_retries_exceeded') as mock_max:
            
            # Mock failure that has reached max retries
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.INSUFFICIENT_FUNDS,
                failure_reason="Insufficient balance",
                status=FailureStatus.RETRYING,
                retry_count=5,  # At max retries
                max_retries=5
            )
            
            mock_get.return_value = mock_failure
            mock_max.return_value = {
                "success": False,
                "status": "grace_period_started"
            }
            
            result = await retry_system.execute_retry_attempt("FAIL_TEST123")
            
            assert result["success"] is False
            assert result["status"] == "grace_period_started"
            mock_max.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_max_retries_exceeded_subscription(self, retry_system):
        """Test max retries exceeded for subscription payment"""
        
        with patch.object(retry_system, '_update_payment_failure') as mock_update, \
             patch.object(retry_system, '_is_subscription_payment') as mock_is_sub, \
             patch.object(retry_system, '_start_grace_period') as mock_grace, \
             patch.object(retry_system, '_send_failure_notification') as mock_notify:
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.INSUFFICIENT_FUNDS,
                failure_reason="Insufficient balance",
                status=FailureStatus.RETRYING,
                retry_count=5,
                max_retries=5
            )
            
            mock_update.return_value = None
            mock_is_sub.return_value = True
            mock_grace.return_value = GracePeriod(
                grace_id="GRACE_TEST",
                user_id="test_user",
                tier=SupportTier.PRO,
                failure_id="FAIL_TEST123",
                started_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7)
            )
            mock_notify.return_value = None
            
            result = await retry_system._handle_max_retries_exceeded(mock_failure)
            
            assert result["success"] is False
            assert result["status"] == "grace_period_started"
            assert "grace_period_expires" in result
            assert result["grace_days"] == 7  # PRO tier grace period
    
    @pytest.mark.asyncio
    async def test_handle_max_retries_exceeded_non_subscription(self, retry_system):
        """Test max retries exceeded for non-subscription payment"""
        
        with patch.object(retry_system, '_update_payment_failure') as mock_update, \
             patch.object(retry_system, '_is_subscription_payment') as mock_is_sub, \
             patch.object(retry_system, '_send_failure_notification') as mock_notify:
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=500,  # ₹5 trading fee
                failure_type=FailureType.CARD_DECLINED,
                failure_reason="Card declined",
                status=FailureStatus.RETRYING,
                retry_count=3,
                max_retries=3
            )
            
            mock_update.return_value = None
            mock_is_sub.return_value = False
            mock_notify.return_value = None
            
            result = await retry_system._handle_max_retries_exceeded(mock_failure)
            
            assert result["success"] is False
            assert result["status"] == "action_required"
            assert result["action_required"] == "update_payment_method_immediately"
    
    @pytest.mark.asyncio
    async def test_start_grace_period(self, retry_system):
        """Test grace period initiation"""
        
        with patch.object(retry_system, '_store_grace_period') as mock_store, \
             patch.object(retry_system, '_schedule_grace_period_warnings') as mock_schedule:
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.ELITE,  # 14 days grace
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.INSUFFICIENT_FUNDS,
                failure_reason="Insufficient balance",
                status=FailureStatus.FAILED_PERMANENTLY
            )
            
            mock_store.return_value = None
            mock_schedule.return_value = None
            
            grace_period = await retry_system._start_grace_period(mock_failure)
            
            assert grace_period.user_id == "test_user"
            assert grace_period.tier == SupportTier.ELITE
            assert grace_period.failure_id == "FAIL_TEST123"
            
            # Check grace period duration (14 days for ELITE)
            duration = grace_period.expires_at - grace_period.started_at
            assert abs(duration.days - 14) <= 1  # Allow 1 day tolerance
    
    @pytest.mark.asyncio
    async def test_handle_no_retry_failure_consent_revoked(self, retry_system):
        """Test handling of consent revoked failure"""
        
        with patch.object(retry_system, '_update_payment_failure') as mock_update, \
             patch.object(retry_system, '_send_failure_notification') as mock_notify:
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.CONSENT_REVOKED,
                failure_reason="User revoked consent",
                status=FailureStatus.PENDING
            )
            
            mock_update.return_value = None
            mock_notify.return_value = None
            
            result = await retry_system._handle_no_retry_failure(mock_failure)
            
            assert result["success"] is False
            assert result["status"] == "user_action_required"
            assert result["failure_type"] == "consent_revoked"
            assert result["action_required"] == "reauthorize_payments"
    
    @pytest.mark.asyncio
    async def test_handle_no_retry_failure_expired_payment(self, retry_system):
        """Test handling of expired payment method failure"""
        
        with patch.object(retry_system, '_update_payment_failure') as mock_update, \
             patch.object(retry_system, '_send_failure_notification') as mock_notify:
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.EXPIRED_PAYMENT_METHOD,
                failure_reason="Card expired",
                status=FailureStatus.PENDING
            )
            
            mock_update.return_value = None
            mock_notify.return_value = None
            
            result = await retry_system._handle_no_retry_failure(mock_failure)
            
            assert result["success"] is False
            assert result["status"] == "user_action_required"
            assert result["failure_type"] == "expired_payment_method"
            assert result["action_required"] == "update_payment_method"
    
    @pytest.mark.asyncio
    async def test_send_standard_failure_notification(self, retry_system):
        """Test standard tier failure notification"""
        
        with patch.object(retry_system, '_get_user_details') as mock_user, \
             patch.object(retry_system.whatsapp_client, 'send_message') as mock_send:
            
            mock_user.return_value = {"phone": "+919876543210"}
            mock_send.return_value = None
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=SupportTier.PRO,
                transaction_id="TXN_TEST",
                amount=9900,
                failure_type=FailureType.INSUFFICIENT_FUNDS,
                failure_reason="Insufficient balance",
                status=FailureStatus.RETRYING,
                next_retry_at=datetime.now() + timedelta(minutes=5)
            )
            
            await retry_system._send_standard_failure_notification(
                mock_failure, "retry_scheduled", "+919876543210"
            )
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[0][0] == "+919876543210"  # Phone number
            assert "₹99.00" in call_args[0][1]  # Amount in message
            assert "retrying automatically" in call_args[0][1].lower()
    
    @pytest.mark.asyncio
    async def test_send_black_tier_failure_notification(self, retry_system):
        """Test Black tier failure notification"""
        
        with patch.object(retry_system.whatsapp_client, 'send_message') as mock_send:
            
            mock_send.return_value = None
            
            mock_failure = PaymentFailure(
                failure_id="FAIL_TEST123",
                user_id="test_user",
                tier=BlackTier.OBSIDIAN,
                transaction_id="TXN_TEST",
                amount=500000,  # ₹5,000
                failure_type=FailureType.NETWORK_ERROR,
                failure_reason="Network timeout",
                status=FailureStatus.RETRYING
            )
            
            await retry_system._send_black_tier_failure_notification(
                mock_failure, "retry_scheduled", "+919876543210"
            )
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[0][0] == "+919876543210"
            assert "TradeMate OBSIDIAN" in call_args[0][1]
            assert "₹5,000.00" in call_args[0][1]
            assert "concierge" in call_args[0][1].lower()
    
    def test_grace_period_configuration(self, retry_system):
        """Test grace period configuration for different tiers"""
        
        # Test tier-specific grace periods
        assert retry_system.grace_periods[SupportTier.LITE] == 3
        assert retry_system.grace_periods[SupportTier.PRO] == 7
        assert retry_system.grace_periods[SupportTier.ELITE] == 14
        assert retry_system.grace_periods[BlackTier.ONYX] == 30
        assert retry_system.grace_periods[BlackTier.OBSIDIAN] == 45
        assert retry_system.grace_periods[BlackTier.VOID] == 60
    
    def test_retry_strategy_configuration(self, retry_system):
        """Test retry strategy configuration for different failure types"""
        
        # Test strategy mapping
        assert retry_system.retry_strategies[FailureType.INSUFFICIENT_FUNDS] == RetryStrategy.SCHEDULED_RETRY
        assert retry_system.retry_strategies[FailureType.CARD_DECLINED] == RetryStrategy.EXPONENTIAL_BACKOFF
        assert retry_system.retry_strategies[FailureType.NETWORK_ERROR] == RetryStrategy.EXPONENTIAL_BACKOFF
        assert retry_system.retry_strategies[FailureType.CONSENT_REVOKED] == RetryStrategy.NO_RETRY
        assert retry_system.retry_strategies[FailureType.EXPIRED_PAYMENT_METHOD] == RetryStrategy.NO_RETRY
        assert retry_system.retry_strategies[FailureType.FRAUD_DETECTION] == RetryStrategy.NO_RETRY
    
    def test_max_retries_configuration(self, retry_system):
        """Test max retries configuration for different failure types"""
        
        # Test max retries mapping
        assert retry_system.max_retries[FailureType.INSUFFICIENT_FUNDS] == 5
        assert retry_system.max_retries[FailureType.CARD_DECLINED] == 3
        assert retry_system.max_retries[FailureType.NETWORK_ERROR] == 3
        assert retry_system.max_retries[FailureType.CONSENT_REVOKED] == 0
        assert retry_system.max_retries[FailureType.EXPIRED_PAYMENT_METHOD] == 0
        assert retry_system.max_retries[FailureType.FRAUD_DETECTION] == 0
    
    def test_is_subscription_payment(self, retry_system):
        """Test subscription payment detection"""
        
        # Subscription payment
        subscription_failure = PaymentFailure(
            failure_id="FAIL_TEST",
            user_id="test_user",
            tier=SupportTier.PRO,
            transaction_id="TXN_TEST",
            amount=9900,
            failure_type=FailureType.INSUFFICIENT_FUNDS,
            failure_reason="Test",
            status=FailureStatus.PENDING,
            metadata={"payment_type": "subscription"}
        )
        
        assert retry_system._is_subscription_payment(subscription_failure) is True
        
        # Non-subscription payment
        trading_failure = PaymentFailure(
            failure_id="FAIL_TEST",
            user_id="test_user",
            tier=SupportTier.PRO,
            transaction_id="TXN_TEST",
            amount=500,
            failure_type=FailureType.CARD_DECLINED,
            failure_reason="Test",
            status=FailureStatus.PENDING,
            metadata={"payment_type": "trading_fee"}
        )
        
        assert retry_system._is_subscription_payment(trading_failure) is False


class TestPaymentFailureModel:
    """Test PaymentFailure data model"""
    
    def test_payment_failure_creation(self):
        """Test PaymentFailure creation with all fields"""
        
        failure = PaymentFailure(
            failure_id="FAIL_TEST123",
            user_id="test_user_001",
            tier=SupportTier.PRO,
            transaction_id="TXN_TEST123",
            amount=9900,
            failure_type=FailureType.INSUFFICIENT_FUNDS,
            failure_reason="Insufficient balance",
            status=FailureStatus.PENDING,
            retry_count=0,
            max_retries=5,
            metadata={"custom": "value"}
        )
        
        assert failure.failure_id == "FAIL_TEST123"
        assert failure.user_id == "test_user_001"
        assert failure.tier == SupportTier.PRO
        assert failure.amount == 9900
        assert failure.failure_type == FailureType.INSUFFICIENT_FUNDS
        assert failure.status == FailureStatus.PENDING
        assert failure.retry_count == 0
        assert failure.max_retries == 5
        assert failure.metadata["custom"] == "value"
    
    def test_payment_failure_defaults(self):
        """Test PaymentFailure default values"""
        
        failure = PaymentFailure(
            failure_id="FAIL_TEST",
            user_id="test_user",
            tier=SupportTier.LITE,
            transaction_id="TXN_TEST",
            amount=1000,
            failure_type=FailureType.CARD_DECLINED,
            failure_reason="Test failure",
            status=FailureStatus.PENDING
        )
        
        assert failure.retry_count == 0
        assert failure.max_retries == 3
        assert failure.next_retry_at is None
        assert failure.last_retry_at is None
        assert failure.resolved_at is None
        assert isinstance(failure.original_failed_at, datetime)
        assert failure.metadata == {}


class TestGracePeriodModel:
    """Test GracePeriod data model"""
    
    def test_grace_period_creation(self):
        """Test GracePeriod creation with all fields"""
        
        started_at = datetime.now()
        expires_at = started_at + timedelta(days=7)
        
        grace_period = GracePeriod(
            grace_id="GRACE_TEST123",
            user_id="test_user_001",
            tier=SupportTier.PRO,
            failure_id="FAIL_TEST123",
            started_at=started_at,
            expires_at=expires_at,
            warning_sent=False,
            final_warning_sent=False,
            service_suspended=False
        )
        
        assert grace_period.grace_id == "GRACE_TEST123"
        assert grace_period.user_id == "test_user_001"
        assert grace_period.tier == SupportTier.PRO
        assert grace_period.failure_id == "FAIL_TEST123"
        assert grace_period.started_at == started_at
        assert grace_period.expires_at == expires_at
        assert grace_period.warning_sent is False
        assert grace_period.final_warning_sent is False
        assert grace_period.service_suspended is False
    
    def test_grace_period_defaults(self):
        """Test GracePeriod default values"""
        
        grace_period = GracePeriod(
            grace_id="GRACE_TEST",
            user_id="test_user",
            tier=SupportTier.LITE,
            failure_id="FAIL_TEST",
            started_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=3)
        )
        
        assert grace_period.warning_sent is False
        assert grace_period.final_warning_sent is False
        assert grace_period.service_suspended is False


# Integration test
class TestPaymentRetryIntegration:
    """Integration tests for payment retry system"""
    
    @pytest.mark.asyncio
    async def test_complete_retry_flow(self):
        """Test complete payment retry flow"""
        
        retry_system = PaymentRetrySystem()
        
        with patch.object(retry_system, '_store_payment_failure'), \
             patch.object(retry_system, '_update_payment_failure'), \
             patch.object(retry_system, '_send_failure_notification'), \
             patch.object(retry_system, '_queue_retry_attempt'), \
             patch.object(retry_system.billing_system, 'initiate_billing') as mock_billing:
            
            # Mock successful retry
            mock_billing.return_value = {
                "success": True,
                "transaction_id": "TXN_RETRY_SUCCESS"
            }
            
            # Step 1: Handle initial failure
            failure_result = await retry_system.handle_payment_failure(
                user_id="test_user_001",
                tier=SupportTier.PRO,
                transaction_id="TXN_ORIGINAL",
                amount=9900,
                failure_type=FailureType.NETWORK_ERROR,
                failure_reason="Network timeout"
            )
            
            assert failure_result["success"] is True
            assert failure_result["status"] == "retry_scheduled"
            
            # Step 2: Execute retry (mock successful payment)
            with patch.object(retry_system, '_get_payment_failure') as mock_get:
                mock_get.return_value = PaymentFailure(
                    failure_id=failure_result["failure_id"],
                    user_id="test_user_001",
                    tier=SupportTier.PRO,
                    transaction_id="TXN_ORIGINAL",
                    amount=9900,
                    failure_type=FailureType.NETWORK_ERROR,
                    failure_reason="Network timeout",
                    status=FailureStatus.RETRYING,
                    retry_count=0,
                    max_retries=3
                )
                
                retry_result = await retry_system.execute_retry_attempt(
                    failure_result["failure_id"]
                )
                
                assert retry_result["success"] is True
                assert retry_result["status"] == "resolved"
                assert retry_result["transaction_id"] == "TXN_RETRY_SUCCESS"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])