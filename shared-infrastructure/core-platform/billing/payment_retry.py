"""
GridWorks Payment Failure Handling & Retry System
Intelligent retry mechanisms with graceful degradation and recovery workflows
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid

from app.ai_support.models import SupportTier
from app.black.models import BlackTier
from app.billing.unified_billing_system import UnifiedBillingSystem
from app.billing.subscription_manager import SubscriptionManager
from app.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of payment failures"""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_DECLINED = "card_declined"
    NETWORK_ERROR = "network_error"
    BANK_ERROR = "bank_error"
    CONSENT_REVOKED = "consent_revoked"
    EXPIRED_PAYMENT_METHOD = "expired_payment_method"
    FRAUD_DETECTION = "fraud_detection"
    TECHNICAL_ERROR = "technical_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE_RETRY = "immediate_retry"
    SCHEDULED_RETRY = "scheduled_retry"
    NO_RETRY = "no_retry"


class FailureStatus(Enum):
    """Status of payment failure handling"""
    PENDING = "pending"
    RETRYING = "retrying"
    RESOLVED = "resolved"
    FAILED_PERMANENTLY = "failed_permanently"
    USER_ACTION_REQUIRED = "user_action_required"
    GRACE_PERIOD = "grace_period"


@dataclass
class PaymentFailure:
    """Payment failure details"""
    failure_id: str
    user_id: str
    tier: Union[SupportTier, BlackTier]
    transaction_id: str
    amount: int
    failure_type: FailureType
    failure_reason: str
    status: FailureStatus
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    original_failed_at: datetime = field(default_factory=datetime.now)
    last_retry_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GracePeriod:
    """Grace period for failed payments"""
    grace_id: str
    user_id: str
    tier: Union[SupportTier, BlackTier]
    failure_id: str
    started_at: datetime
    expires_at: datetime
    warning_sent: bool = False
    final_warning_sent: bool = False
    service_suspended: bool = False


class PaymentRetrySystem:
    """
    Intelligent payment failure handling and retry system
    
    Features:
    - Smart retry strategies based on failure type
    - Grace period management for subscription failures
    - User communication and recovery assistance
    - Tier-specific handling policies
    - Escalation workflows for persistent failures
    """
    
    def __init__(self):
        self.billing_system = UnifiedBillingSystem()
        self.subscription_manager = SubscriptionManager()
        self.whatsapp_client = WhatsAppClient()
        
        # Tier-specific grace periods (in days)
        self.grace_periods = {
            SupportTier.LITE: 3,  # 3 days grace
            SupportTier.PRO: 7,   # 7 days grace
            SupportTier.ELITE: 14, # 14 days grace
            BlackTier.ONYX: 30,    # 30 days grace
            BlackTier.OBSIDIAN: 45, # 45 days grace
            BlackTier.VOID: 60     # 60 days grace
        }
        
        # Failure type to retry strategy mapping
        self.retry_strategies = {
            FailureType.INSUFFICIENT_FUNDS: RetryStrategy.SCHEDULED_RETRY,
            FailureType.CARD_DECLINED: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.NETWORK_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.BANK_ERROR: RetryStrategy.LINEAR_BACKOFF,
            FailureType.CONSENT_REVOKED: RetryStrategy.NO_RETRY,
            FailureType.EXPIRED_PAYMENT_METHOD: RetryStrategy.NO_RETRY,
            FailureType.FRAUD_DETECTION: RetryStrategy.NO_RETRY,
            FailureType.TECHNICAL_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.RATE_LIMIT_EXCEEDED: RetryStrategy.LINEAR_BACKOFF
        }
        
        # Max retry attempts by failure type
        self.max_retries = {
            FailureType.INSUFFICIENT_FUNDS: 5,
            FailureType.CARD_DECLINED: 3,
            FailureType.NETWORK_ERROR: 3,
            FailureType.BANK_ERROR: 3,
            FailureType.CONSENT_REVOKED: 0,
            FailureType.EXPIRED_PAYMENT_METHOD: 0,
            FailureType.FRAUD_DETECTION: 0,
            FailureType.TECHNICAL_ERROR: 3,
            FailureType.RATE_LIMIT_EXCEEDED: 5
        }
        
        logger.info("Payment Retry System initialized")
    
    async def handle_payment_failure(
        self,
        user_id: str,
        tier: Union[SupportTier, BlackTier],
        transaction_id: str,
        amount: int,
        failure_type: FailureType,
        failure_reason: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle payment failure with intelligent retry logic"""
        
        try:
            logger.info(f"Handling payment failure for user {user_id}: {failure_type.value}")
            
            # Create failure record
            failure = PaymentFailure(
                failure_id=f"FAIL_{uuid.uuid4().hex[:12].upper()}",
                user_id=user_id,
                tier=tier,
                transaction_id=transaction_id,
                amount=amount,
                failure_type=failure_type,
                failure_reason=failure_reason,
                status=FailureStatus.PENDING,
                max_retries=self.max_retries.get(failure_type, 3),
                metadata=metadata or {}
            )
            
            # Store failure record
            await self._store_payment_failure(failure)
            
            # Determine retry strategy
            strategy = self.retry_strategies.get(failure_type, RetryStrategy.EXPONENTIAL_BACKOFF)
            
            if strategy == RetryStrategy.NO_RETRY:
                # No retry - requires user action
                return await self._handle_no_retry_failure(failure)
            else:
                # Schedule retry attempt
                return await self._schedule_retry(failure, strategy)
                
        except Exception as e:
            logger.error(f"Payment failure handling error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _schedule_retry(
        self,
        failure: PaymentFailure,
        strategy: RetryStrategy
    ) -> Dict[str, Any]:
        """Schedule payment retry based on strategy"""
        
        try:
            # Calculate next retry time
            next_retry = await self._calculate_next_retry(failure, strategy)
            
            failure.next_retry_at = next_retry
            failure.status = FailureStatus.RETRYING
            
            # Update failure record
            await self._update_payment_failure(failure)
            
            # Send user notification
            await self._send_failure_notification(failure, "retry_scheduled")
            
            # Schedule actual retry
            await self._queue_retry_attempt(failure)
            
            return {
                "success": True,
                "failure_id": failure.failure_id,
                "status": "retry_scheduled",
                "next_retry_at": next_retry.isoformat(),
                "retry_strategy": strategy.value,
                "max_retries_remaining": failure.max_retries - failure.retry_count
            }
            
        except Exception as e:
            logger.error(f"Retry scheduling error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_next_retry(
        self,
        failure: PaymentFailure,
        strategy: RetryStrategy
    ) -> datetime:
        """Calculate next retry time based on strategy"""
        
        now = datetime.now()
        retry_count = failure.retry_count
        
        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            # 1min, 2min, 4min, 8min, 16min
            delay_minutes = 2 ** retry_count
            return now + timedelta(minutes=delay_minutes)
            
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            # 5min, 10min, 15min, 20min, 25min
            delay_minutes = 5 * (retry_count + 1)
            return now + timedelta(minutes=delay_minutes)
            
        elif strategy == RetryStrategy.IMMEDIATE_RETRY:
            # Immediate retry with small delay
            return now + timedelta(seconds=30)
            
        elif strategy == RetryStrategy.SCHEDULED_RETRY:
            # For insufficient funds - retry next business day
            if failure.failure_type == FailureType.INSUFFICIENT_FUNDS:
                # Schedule for next morning (9 AM)
                next_day = now + timedelta(days=1)
                return next_day.replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                # Default to 1 hour
                return now + timedelta(hours=1)
        
        else:
            # Default fallback
            return now + timedelta(hours=1)
    
    async def execute_retry_attempt(
        self,
        failure_id: str
    ) -> Dict[str, Any]:
        """Execute scheduled retry attempt"""
        
        try:
            # Get failure details
            failure = await self._get_payment_failure(failure_id)
            
            if not failure:
                return {"success": False, "error": "Failure record not found"}
            
            # Check if retry limit exceeded
            if failure.retry_count >= failure.max_retries:
                return await self._handle_max_retries_exceeded(failure)
            
            # Update retry count
            failure.retry_count += 1
            failure.last_retry_at = datetime.now()
            failure.status = FailureStatus.RETRYING
            
            await self._update_payment_failure(failure)
            
            # Attempt payment retry
            retry_result = await self._attempt_payment_retry(failure)
            
            if retry_result["success"]:
                # Payment successful
                failure.status = FailureStatus.RESOLVED
                failure.resolved_at = datetime.now()
                await self._update_payment_failure(failure)
                
                # Send success notification
                await self._send_failure_notification(failure, "resolved")
                
                return {
                    "success": True,
                    "status": "resolved",
                    "transaction_id": retry_result["transaction_id"],
                    "retry_count": failure.retry_count
                }
            else:
                # Retry failed - schedule next attempt or give up
                if failure.retry_count < failure.max_retries:
                    # Schedule next retry
                    strategy = self.retry_strategies.get(
                        failure.failure_type, 
                        RetryStrategy.EXPONENTIAL_BACKOFF
                    )
                    return await self._schedule_retry(failure, strategy)
                else:
                    # Max retries exceeded
                    return await self._handle_max_retries_exceeded(failure)
                    
        except Exception as e:
            logger.error(f"Retry execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _attempt_payment_retry(
        self,
        failure: PaymentFailure
    ) -> Dict[str, Any]:
        """Attempt to retry the failed payment"""
        
        try:
            # Use original payment details for retry
            retry_result = await self.billing_system.initiate_billing(
                user_id=failure.user_id,
                tier=failure.tier,
                billing_type="retry",
                amount_override=failure.amount,
                metadata={
                    "original_transaction_id": failure.transaction_id,
                    "failure_id": failure.failure_id,
                    "retry_count": failure.retry_count,
                    **failure.metadata
                }
            )
            
            return retry_result
            
        except Exception as e:
            logger.error(f"Payment retry attempt error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_max_retries_exceeded(
        self,
        failure: PaymentFailure
    ) -> Dict[str, Any]:
        """Handle case where max retries exceeded"""
        
        try:
            failure.status = FailureStatus.FAILED_PERMANENTLY
            await self._update_payment_failure(failure)
            
            # Start grace period for subscription payments
            if self._is_subscription_payment(failure):
                grace_period = await self._start_grace_period(failure)
                
                # Send grace period notification
                await self._send_failure_notification(failure, "grace_period_started")
                
                return {
                    "success": False,
                    "status": "grace_period_started",
                    "grace_period_expires": grace_period.expires_at.isoformat(),
                    "grace_days": self.grace_periods.get(failure.tier, 3),
                    "action_required": "update_payment_method"
                }
            else:
                # Non-subscription payment - require immediate action
                failure.status = FailureStatus.USER_ACTION_REQUIRED
                await self._update_payment_failure(failure)
                
                # Send action required notification
                await self._send_failure_notification(failure, "action_required")
                
                return {
                    "success": False,
                    "status": "action_required",
                    "action_required": "update_payment_method_immediately"
                }
                
        except Exception as e:
            logger.error(f"Max retries handling error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_grace_period(
        self,
        failure: PaymentFailure
    ) -> GracePeriod:
        """Start grace period for failed subscription payment"""
        
        grace_days = self.grace_periods.get(failure.tier, 3)
        
        grace_period = GracePeriod(
            grace_id=f"GRACE_{uuid.uuid4().hex[:12].upper()}",
            user_id=failure.user_id,
            tier=failure.tier,
            failure_id=failure.failure_id,
            started_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=grace_days)
        )
        
        # Store grace period
        await self._store_grace_period(grace_period)
        
        # Schedule grace period warnings
        await self._schedule_grace_period_warnings(grace_period)
        
        return grace_period
    
    async def _handle_no_retry_failure(
        self,
        failure: PaymentFailure
    ) -> Dict[str, Any]:
        """Handle failures that require immediate user action"""
        
        try:
            failure.status = FailureStatus.USER_ACTION_REQUIRED
            await self._update_payment_failure(failure)
            
            # Send immediate action notification
            await self._send_failure_notification(failure, "immediate_action")
            
            # Determine required action based on failure type
            if failure.failure_type == FailureType.CONSENT_REVOKED:
                action = "reauthorize_payments"
            elif failure.failure_type == FailureType.EXPIRED_PAYMENT_METHOD:
                action = "update_payment_method"
            elif failure.failure_type == FailureType.FRAUD_DETECTION:
                action = "contact_support"
            else:
                action = "update_payment_method"
            
            return {
                "success": False,
                "status": "user_action_required",
                "failure_type": failure.failure_type.value,
                "action_required": action,
                "failure_id": failure.failure_id
            }
            
        except Exception as e:
            logger.error(f"No-retry failure handling error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_failure_notification(
        self,
        failure: PaymentFailure,
        notification_type: str
    ):
        """Send user notification about payment failure"""
        
        try:
            # Get user details
            user_details = await self._get_user_details(failure.user_id)
            phone = user_details.get("phone")
            
            if not phone:
                logger.warning(f"No phone found for user {failure.user_id}")
                return
            
            # Create tier-specific message
            if isinstance(failure.tier, BlackTier):
                # Black tier - concierge-style notification
                await self._send_black_tier_failure_notification(
                    failure, notification_type, phone
                )
            else:
                # Standard tier - WhatsApp notification
                await self._send_standard_failure_notification(
                    failure, notification_type, phone
                )
                
        except Exception as e:
            logger.error(f"Failure notification error: {e}")
    
    async def _send_standard_failure_notification(
        self,
        failure: PaymentFailure,
        notification_type: str,
        phone: str
    ):
        """Send standard tier failure notification"""
        
        amount_str = f"₹{failure.amount / 100:.2f}"
        
        if notification_type == "retry_scheduled":
            message = f"""⚠️ *Payment Issue - We're Handling It!*

Your {amount_str} payment couldn't process right now.

🔄 *Don't worry - we're retrying automatically*
Next attempt: {failure.next_retry_at.strftime('%d %b, %I:%M %p') if failure.next_retry_at else 'Soon'}

Reason: {failure.failure_reason}

*No action needed - we'll notify you once resolved!*"""

        elif notification_type == "resolved":
            message = f"""✅ *Payment Successful!*

Your {amount_str} payment has been processed successfully.

*Your GridWorks services continue uninterrupted!*"""

        elif notification_type == "grace_period_started":
            grace_days = self.grace_periods.get(failure.tier, 3)
            message = f"""🚨 *Payment Failed - Action Needed*

Your {amount_str} payment couldn't be processed after multiple attempts.

⏰ *Grace Period: {grace_days} days*
Your services continue until {(datetime.now() + timedelta(days=grace_days)).strftime('%d %b %Y')}

👆 *Please update your payment method*
Reply with "payment" to fix this issue

*Don't worry - your account is safe!*"""

        elif notification_type == "immediate_action":
            message = f"""🚨 *Payment Issue - Immediate Action Required*

Your {amount_str} payment failed: {failure.failure_reason}

👆 *Action Required: Update payment method*
Reply with "payment" to resolve immediately

*Your services may be affected until resolved*"""

        else:
            message = f"""⚠️ *Payment Notification*

Your {amount_str} payment requires attention.
Please check your GridWorks account for details."""

        await self.whatsapp_client.send_message(phone, message)
        logger.info(f"Standard failure notification sent to {phone}")
    
    async def _send_black_tier_failure_notification(
        self,
        failure: PaymentFailure,
        notification_type: str,
        phone: str
    ):
        """Send Black tier concierge-style failure notification"""
        
        # Black tier would typically use in-app notifications
        # This is a fallback WhatsApp notification
        amount_str = f"₹{failure.amount / 100:,.2f}"
        
        if notification_type == "retry_scheduled":
            message = f"""🎩 *GridWorks {failure.tier.value} - Payment Notice*

Dear Valued Client,

Your {amount_str} payment encountered a temporary processing delay.

✨ *Our concierge team is handling this personally*
- Automatic retry scheduled
- Your services remain uninterrupted
- Personal attention guaranteed

*No action required from your end.*

*Your dedicated GridWorks butler*"""

        elif notification_type == "grace_period_started":
            grace_days = self.grace_periods.get(failure.tier, 30)
            message = f"""🎩 *GridWorks {failure.tier.value} - Concierge Service*

Dear Valued Client,

Your {amount_str} payment requires attention.

👑 *Extended Grace Period: {grace_days} days*
- All services continue uninterrupted
- Personal concierge assistance available
- Discreet resolution process

*Your dedicated concierge will contact you within 4 hours*

*White-glove service guaranteed*"""

        else:
            message = f"""🎩 *GridWorks {failure.tier.value} - Personal Notice*

Your {amount_str} payment requires personal attention.
Your dedicated concierge will contact you shortly.

*Exclusive service continues*"""

        await self.whatsapp_client.send_message(phone, message)
        logger.info(f"Black tier failure notification sent to {phone}")
    
    def _is_subscription_payment(self, failure: PaymentFailure) -> bool:
        """Check if failed payment is for subscription"""
        return failure.metadata.get("payment_type") == "subscription"
    
    async def _queue_retry_attempt(self, failure: PaymentFailure):
        """Queue retry attempt for execution at scheduled time"""
        
        # This would integrate with a job queue system (e.g., Celery, RQ)
        # For now, mock implementation
        logger.info(f"Queued retry for {failure.failure_id} at {failure.next_retry_at}")
    
    async def _schedule_grace_period_warnings(self, grace_period: GracePeriod):
        """Schedule warning notifications during grace period"""
        
        # Warning at 50% of grace period
        warning_time = grace_period.started_at + timedelta(
            seconds=(grace_period.expires_at - grace_period.started_at).total_seconds() * 0.5
        )
        
        # Final warning at 80% of grace period
        final_warning_time = grace_period.started_at + timedelta(
            seconds=(grace_period.expires_at - grace_period.started_at).total_seconds() * 0.8
        )
        
        logger.info(f"Scheduled grace period warnings for {grace_period.grace_id}")
    
    async def _store_payment_failure(self, failure: PaymentFailure):
        """Store payment failure record in database"""
        
        # Mock implementation - replace with actual database storage
        logger.info(f"Stored payment failure: {failure.failure_id}")
    
    async def _update_payment_failure(self, failure: PaymentFailure):
        """Update payment failure record in database"""
        
        # Mock implementation - replace with actual database update
        logger.info(f"Updated payment failure: {failure.failure_id}, status: {failure.status.value}")
    
    async def _get_payment_failure(self, failure_id: str) -> Optional[PaymentFailure]:
        """Get payment failure record from database"""
        
        # Mock implementation - replace with actual database query
        return PaymentFailure(
            failure_id=failure_id,
            user_id="mock_user",
            tier=SupportTier.PRO,
            transaction_id="TXN_MOCK",
            amount=9900,  # ₹99
            failure_type=FailureType.INSUFFICIENT_FUNDS,
            failure_reason="Insufficient balance",
            status=FailureStatus.RETRYING,
            retry_count=1,
            max_retries=5
        )
    
    async def _store_grace_period(self, grace_period: GracePeriod):
        """Store grace period record in database"""
        
        # Mock implementation - replace with actual database storage
        logger.info(f"Stored grace period: {grace_period.grace_id}")
    
    async def _get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get user contact details"""
        
        # Mock implementation
        return {
            "user_id": user_id,
            "phone": "+919876543210",
            "email": "user@example.com"
        }


# Demo usage
async def demo_payment_retry_system():
    """Demonstrate payment retry system"""
    
    print("💳 GridWorks Payment Retry System Demo")
    print("=" * 60)
    
    retry_system = PaymentRetrySystem()
    
    # Test payment failure handling
    failure_result = await retry_system.handle_payment_failure(
        user_id="demo_user_001",
        tier=SupportTier.PRO,
        transaction_id="TXN_DEMO_001",
        amount=9900,  # ₹99
        failure_type=FailureType.INSUFFICIENT_FUNDS,
        failure_reason="Insufficient balance in account",
        metadata={"payment_type": "subscription"}
    )
    
    print("🚨 Payment Failure Handled:")
    print(f"Status: {failure_result.get('status')}")
    print(f"Failure ID: {failure_result.get('failure_id')}")
    print(f"Next Retry: {failure_result.get('next_retry_at')}")
    
    # Test retry execution
    if failure_result.get("success"):
        retry_result = await retry_system.execute_retry_attempt(
            failure_result["failure_id"]
        )
        
        print(f"\n🔄 Retry Execution:")
        print(f"Success: {retry_result.get('success')}")
        print(f"Status: {retry_result.get('status')}")
        print(f"Retry Count: {retry_result.get('retry_count')}")


if __name__ == "__main__":
    asyncio.run(demo_payment_retry_system())