"""
GridWorks Tier Management System
Intelligent tier upgrade/downgrade logic with automatic triggers
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json

from app.ai_support.models import SupportTier
from app.black.models import BlackTier
from app.billing.unified_billing_system import UnifiedBillingSystem
from app.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)


class TierChangeReason(Enum):
    """Reasons for tier changes"""
    PORTFOLIO_GROWTH = "portfolio_growth"
    TRADING_ACTIVITY = "trading_activity"
    FEATURE_USAGE = "feature_usage"
    PAYMENT_FAILURE = "payment_failure"
    USER_REQUEST = "user_request"
    AUTOMATIC_OPTIMIZATION = "automatic_optimization"
    DOWNGRADE_REQUEST = "downgrade_request"
    INACTIVITY = "inactivity"


class TierChangeStatus(Enum):
    """Status of tier change requests"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TierMetrics:
    """User metrics for tier evaluation"""
    user_id: str
    current_tier: Union[SupportTier, BlackTier]
    portfolio_value: float
    monthly_trades: int
    monthly_volume: float
    feature_usage_score: float
    payment_reliability: float
    engagement_score: float
    tenure_months: int
    referrals_made: int
    last_activity: datetime
    
    
@dataclass
class TierChangeRequest:
    """Tier change request details"""
    request_id: str
    user_id: str
    current_tier: Union[SupportTier, BlackTier]
    target_tier: Union[SupportTier, BlackTier]
    reason: TierChangeReason
    status: TierChangeStatus
    metrics: TierMetrics
    financial_impact: Dict[str, float]
    approval_required: bool
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TierManagementSystem:
    """
    Intelligent tier management with automatic triggers
    
    Features:
    - Automatic tier upgrade detection
    - Smart downgrade prevention
    - Prorated billing adjustments
    - Seamless tier transitions
    - User communication
    """
    
    def __init__(self):
        self.billing_system = UnifiedBillingSystem()
        self.whatsapp_client = WhatsAppClient()
        
        # Tier qualification criteria
        self.tier_criteria = {
            SupportTier.LITE: {
                "portfolio_min": 0,
                "portfolio_max": 50000,  # ₹50K
                "monthly_trades_min": 0,
                "features": ["basic_trading", "ai_support", "voice_commands"]
            },
            SupportTier.PRO: {
                "portfolio_min": 50000,  # ₹50K
                "portfolio_max": 2000000,  # ₹20L
                "monthly_trades_min": 5,
                "features": ["professional_tools", "advanced_ai", "priority_support", "voice_trading"]
            },
            SupportTier.ELITE: {
                "portfolio_min": 2000000,  # ₹20L
                "portfolio_max": 5000000,  # ₹50L
                "monthly_trades_min": 10,
                "features": ["executive_analytics", "dedicated_support", "portfolio_management"]
            },
            BlackTier.ONYX: {
                "portfolio_min": 5000000,  # ₹50L
                "portfolio_max": 20000000,  # ₹2Cr
                "monthly_trades_min": 15,
                "features": ["elite_market_access", "concierge_lite", "professional_services"]
            },
            BlackTier.OBSIDIAN: {
                "portfolio_min": 20000000,  # ₹2Cr
                "portfolio_max": 50000000,  # ₹5Cr
                "monthly_trades_min": 20,
                "features": ["institutional_tools", "premium_concierge", "family_office"]
            },
            BlackTier.VOID: {
                "portfolio_min": 50000000,  # ₹5Cr
                "portfolio_max": float('inf'),
                "monthly_trades_min": 25,
                "features": ["unlimited_access", "personal_butler", "emergency_response"]
            }
        }
        
        # Upgrade triggers (automatic qualification)
        self.upgrade_triggers = {
            "portfolio_milestone": {
                "weight": 0.4,
                "thresholds": {
                    SupportTier.LITE: 50000,  # ₹50K for PRO
                    SupportTier.PRO: 2000000,  # ₹20L for ELITE  
                    SupportTier.ELITE: 5000000,  # ₹50L for ONYX
                    BlackTier.ONYX: 20000000,  # ₹2Cr for OBSIDIAN
                    BlackTier.OBSIDIAN: 50000000  # ₹5Cr for VOID
                }
            },
            "trading_activity": {
                "weight": 0.3,
                "thresholds": {
                    SupportTier.LITE: 10,  # 10 trades/month for PRO
                    SupportTier.PRO: 25,  # 25 trades/month for ELITE
                    SupportTier.ELITE: 50,  # 50 trades/month for ONYX
                    BlackTier.ONYX: 100,  # 100 trades/month for OBSIDIAN
                    BlackTier.OBSIDIAN: 200  # 200 trades/month for VOID
                }
            },
            "feature_usage": {
                "weight": 0.2,
                "score_threshold": 0.8  # 80% feature utilization
            },
            "engagement": {
                "weight": 0.1,
                "score_threshold": 0.7  # 70% engagement score
            }
        }
        
        logger.info("Tier Management System initialized")
    
    async def evaluate_tier_eligibility(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Evaluate user's tier eligibility and recommend changes"""
        
        try:
            # Get user metrics
            metrics = await self._get_user_metrics(user_id)
            
            # Calculate tier score for each tier
            tier_scores = await self._calculate_tier_scores(metrics)
            
            # Find optimal tier
            recommended_tier = await self._determine_optimal_tier(metrics, tier_scores)
            
            # Check if upgrade/downgrade is needed
            if recommended_tier != metrics.current_tier:
                change_analysis = await self._analyze_tier_change(
                    metrics, recommended_tier
                )
                
                return {
                    "user_id": user_id,
                    "current_tier": self._tier_to_string(metrics.current_tier),
                    "recommended_tier": self._tier_to_string(recommended_tier),
                    "change_needed": True,
                    "change_type": "upgrade" if self._is_upgrade(metrics.current_tier, recommended_tier) else "downgrade",
                    "tier_scores": {self._tier_to_string(k): v for k, v in tier_scores.items()},
                    "change_analysis": change_analysis,
                    "auto_approved": change_analysis["auto_approved"]
                }
            else:
                return {
                    "user_id": user_id,
                    "current_tier": self._tier_to_string(metrics.current_tier),
                    "recommended_tier": self._tier_to_string(metrics.current_tier),
                    "change_needed": False,
                    "tier_scores": {self._tier_to_string(k): v for k, v in tier_scores.items()}
                }
                
        except Exception as e:
            logger.error(f"Tier evaluation failed for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def initiate_tier_change(
        self,
        user_id: str,
        target_tier: Union[SupportTier, BlackTier],
        reason: TierChangeReason = TierChangeReason.USER_REQUEST
    ) -> Dict[str, Any]:
        """Initiate tier change process"""
        
        try:
            # Get current user metrics
            metrics = await self._get_user_metrics(user_id)
            
            # Validate tier change
            validation = await self._validate_tier_change(metrics, target_tier)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "requirements": validation.get("requirements")
                }
            
            # Calculate financial impact
            financial_impact = await self._calculate_financial_impact(
                metrics.current_tier, target_tier
            )
            
            # Create tier change request
            change_request = TierChangeRequest(
                request_id=f"TIER_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                current_tier=metrics.current_tier,
                target_tier=target_tier,
                reason=reason,
                status=TierChangeStatus.PENDING,
                metrics=metrics,
                financial_impact=financial_impact,
                approval_required=self._requires_approval(metrics.current_tier, target_tier),
                created_at=datetime.now()
            )
            
            # Process or queue for approval
            if change_request.approval_required:
                await self._queue_for_approval(change_request)
                return {
                    "success": True,
                    "request_id": change_request.request_id,
                    "status": "pending_approval",
                    "financial_impact": financial_impact,
                    "estimated_processing": "24-48 hours"
                }
            else:
                # Auto-approve and process
                return await self._process_tier_change(change_request)
                
        except Exception as e:
            logger.error(f"Tier change initiation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_tier_change(
        self,
        change_request: TierChangeRequest
    ) -> Dict[str, Any]:
        """Process approved tier change"""
        
        try:
            logger.info(f"Processing tier change: {change_request.request_id}")
            
            # Update request status
            change_request.status = TierChangeStatus.PROCESSING
            
            # Handle billing changes
            billing_result = await self._handle_tier_billing_change(change_request)
            
            if not billing_result["success"]:
                change_request.status = TierChangeStatus.FAILED
                return billing_result
            
            # Update user tier
            await self._update_user_tier(
                change_request.user_id, 
                change_request.target_tier
            )
            
            # Send user notification
            await self._send_tier_change_notification(change_request)
            
            # Log tier change
            await self._log_tier_change(change_request)
            
            # Update request status
            change_request.status = TierChangeStatus.COMPLETED
            change_request.processed_at = datetime.now()
            
            return {
                "success": True,
                "request_id": change_request.request_id,
                "new_tier": self._tier_to_string(change_request.target_tier),
                "financial_adjustment": billing_result.get("adjustment"),
                "effective_date": datetime.now().isoformat(),
                "next_billing_date": billing_result.get("next_billing_date")
            }
            
        except Exception as e:
            logger.error(f"Tier change processing failed: {e}")
            change_request.status = TierChangeStatus.FAILED
            return {"success": False, "error": str(e)}
    
    async def _handle_tier_billing_change(
        self,
        change_request: TierChangeRequest
    ) -> Dict[str, Any]:
        """Handle billing adjustments for tier changes"""
        
        try:
            current_tier = change_request.current_tier
            target_tier = change_request.target_tier
            financial_impact = change_request.financial_impact
            
            # Handle different tier change scenarios
            if self._is_upgrade(current_tier, target_tier):
                return await self._handle_tier_upgrade_billing(
                    change_request.user_id, current_tier, target_tier, financial_impact
                )
            else:
                return await self._handle_tier_downgrade_billing(
                    change_request.user_id, current_tier, target_tier, financial_impact
                )
                
        except Exception as e:
            logger.error(f"Billing change handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_tier_upgrade_billing(
        self,
        user_id: str,
        current_tier: Union[SupportTier, BlackTier],
        target_tier: Union[SupportTier, BlackTier],
        financial_impact: Dict[str, float]
    ) -> Dict[str, Any]:
        """Handle billing for tier upgrades"""
        
        try:
            # Calculate proration for current billing period
            proration = await self._calculate_upgrade_proration(
                user_id, current_tier, target_tier
            )
            
            # Create new subscription for target tier
            subscription_result = await self.billing_system.initiate_billing(
                user_id=user_id,
                tier=target_tier,
                billing_type="subscription",
                amount_override=proration["upgrade_amount"]
            )
            
            if subscription_result["success"]:
                # Cancel current subscription if needed
                if self._is_subscription_tier(current_tier):
                    await self._cancel_current_subscription(user_id)
                
                return {
                    "success": True,
                    "adjustment": proration["adjustment_amount"],
                    "new_subscription_id": subscription_result.get("subscription_id"),
                    "next_billing_date": proration["next_billing_date"]
                }
            else:
                return subscription_result
                
        except Exception as e:
            logger.error(f"Upgrade billing handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_tier_downgrade_billing(
        self,
        user_id: str,
        current_tier: Union[SupportTier, BlackTier],
        target_tier: Union[SupportTier, BlackTier],
        financial_impact: Dict[str, float]
    ) -> Dict[str, Any]:
        """Handle billing for tier downgrades"""
        
        try:
            # Calculate refund for remaining period
            refund = await self._calculate_downgrade_refund(
                user_id, current_tier, target_tier
            )
            
            # Process refund if applicable
            if refund["amount"] > 0:
                refund_result = await self._process_tier_downgrade_refund(
                    user_id, refund["amount"]
                )
            else:
                refund_result = {"success": True, "refund_amount": 0}
            
            # Create new subscription for target tier (if needed)
            if self._is_subscription_tier(target_tier):
                subscription_result = await self.billing_system.initiate_billing(
                    user_id=user_id,
                    tier=target_tier,
                    billing_type="subscription"
                )
                
                if not subscription_result["success"]:
                    return subscription_result
            else:
                subscription_result = {"success": True}
            
            return {
                "success": True,
                "refund_amount": refund["amount"],
                "new_subscription_id": subscription_result.get("subscription_id"),
                "effective_date": refund["effective_date"]
            }
            
        except Exception as e:
            logger.error(f"Downgrade billing handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_tier_scores(
        self,
        metrics: TierMetrics
    ) -> Dict[Union[SupportTier, BlackTier], float]:
        """Calculate suitability scores for each tier"""
        
        scores = {}
        
        for tier, criteria in self.tier_criteria.items():
            score = 0.0
            
            # Portfolio value score
            if metrics.portfolio_value >= criteria["portfolio_min"]:
                if metrics.portfolio_value <= criteria.get("portfolio_max", float('inf')):
                    score += 0.4  # Perfect fit
                else:
                    score += 0.4 * (criteria.get("portfolio_max", metrics.portfolio_value) / metrics.portfolio_value)
            else:
                score += 0.4 * (metrics.portfolio_value / criteria["portfolio_min"])
            
            # Trading activity score
            monthly_trades_min = criteria.get("monthly_trades_min", 0)
            if metrics.monthly_trades >= monthly_trades_min:
                score += 0.3
            else:
                score += 0.3 * (metrics.monthly_trades / monthly_trades_min) if monthly_trades_min > 0 else 0
            
            # Feature usage score
            score += 0.2 * metrics.feature_usage_score
            
            # Engagement score
            score += 0.1 * metrics.engagement_score
            
            scores[tier] = min(1.0, score)  # Cap at 1.0
        
        return scores
    
    async def _determine_optimal_tier(
        self,
        metrics: TierMetrics,
        tier_scores: Dict[Union[SupportTier, BlackTier], float]
    ) -> Union[SupportTier, BlackTier]:
        """Determine optimal tier based on scores and criteria"""
        
        # Find tier with highest score that user qualifies for
        qualified_tiers = []
        
        for tier, score in tier_scores.items():
            criteria = self.tier_criteria[tier]
            
            # Check minimum requirements
            if (metrics.portfolio_value >= criteria["portfolio_min"] and
                metrics.monthly_trades >= criteria.get("monthly_trades_min", 0) and
                score >= 0.7):  # Minimum 70% score
                qualified_tiers.append((tier, score))
        
        if qualified_tiers:
            # Sort by score and return highest
            qualified_tiers.sort(key=lambda x: x[1], reverse=True)
            return qualified_tiers[0][0]
        else:
            # Default to LITE if no qualifications met
            return SupportTier.LITE
    
    async def _send_tier_change_notification(
        self,
        change_request: TierChangeRequest
    ):
        """Send tier change notification to user"""
        
        user_id = change_request.user_id
        target_tier = change_request.target_tier
        
        # Get user phone for WhatsApp notification
        user_details = await self._get_user_details(user_id)
        phone = user_details.get("phone")
        
        if not phone:
            logger.warning(f"No phone found for user {user_id}")
            return
        
        # Create tier-specific notification
        if isinstance(target_tier, BlackTier):
            # Black tier upgrade - special notification
            message = f"""🎉 *Congratulations! Welcome to GridWorks {target_tier.value}*

You've been upgraded to our ultra-premium {target_tier.value} tier!

✨ *Your new exclusive benefits:*
{self._get_tier_benefits_text(target_tier)}

🎩 *Your dedicated concierge will contact you within 24 hours*

*Welcome to the elite trading experience!*"""
        else:
            # Standard tier notification
            message = f"""🚀 *Tier Upgrade Complete!*

Welcome to GridWorks {target_tier.value}!

✅ *Your new features:*
{self._get_tier_benefits_text(target_tier)}

💳 *Billing updated automatically*
Next charge: {change_request.financial_impact.get('next_billing_date', 'Next cycle')}

*Start exploring your new features now!*"""
        
        await self.whatsapp_client.send_message(phone, message)
        logger.info(f"Tier change notification sent to {phone}")
    
    def _get_tier_benefits_text(self, tier: Union[SupportTier, BlackTier]) -> str:
        """Get formatted benefits text for tier"""
        
        benefits = {
            SupportTier.PRO: [
                "⚡ Professional trading tools",
                "🤖 Advanced AI support",
                "🎤 Voice trading commands",
                "📊 Priority support (<15s)"
            ],
            SupportTier.ELITE: [
                "👑 Executive analytics suite",
                "📹 Dedicated support specialist",
                "📊 Portfolio optimization AI",
                "🎯 Institutional market access"
            ],
            BlackTier.ONYX: [
                "🖤 Elite market access",
                "💼 Professional services",
                "📊 Advanced analytics",
                "🎯 Concierge support"
            ],
            BlackTier.OBSIDIAN: [
                "⚫ Institutional-grade tools",
                "🤖 Premium AI assistance",
                "🏛️ Family office coordination",
                "24/7 executive support"
            ],
            BlackTier.VOID: [
                "🕳️ Unlimited platform access",
                "👑 Personal market strategist",
                "🌍 Global investment opportunities",
                "🎩 Dedicated butler service"
            ]
        }
        
        tier_benefits = benefits.get(tier, ["Enhanced trading experience"])
        return "\n".join(tier_benefits)
    
    def _tier_to_string(self, tier: Union[SupportTier, BlackTier]) -> str:
        """Convert tier enum to string"""
        return tier.value if tier else "UNKNOWN"
    
    def _is_upgrade(
        self,
        current_tier: Union[SupportTier, BlackTier],
        target_tier: Union[SupportTier, BlackTier]
    ) -> bool:
        """Check if target tier is an upgrade"""
        
        tier_hierarchy = [
            SupportTier.LITE,
            SupportTier.PRO,
            SupportTier.ELITE,
            BlackTier.ONYX,
            BlackTier.OBSIDIAN,
            BlackTier.VOID
        ]
        
        try:
            current_index = tier_hierarchy.index(current_tier)
            target_index = tier_hierarchy.index(target_tier)
            return target_index > current_index
        except ValueError:
            return False
    
    async def _get_user_metrics(self, user_id: str) -> TierMetrics:
        """Get user metrics for tier evaluation"""
        
        # Mock implementation - replace with actual data fetching
        return TierMetrics(
            user_id=user_id,
            current_tier=SupportTier.LITE,
            portfolio_value=75000.0,  # ₹75K - qualifies for PRO
            monthly_trades=12,
            monthly_volume=250000.0,
            feature_usage_score=0.85,
            payment_reliability=0.95,
            engagement_score=0.80,
            tenure_months=6,
            referrals_made=2,
            last_activity=datetime.now() - timedelta(hours=2)
        )
    
    async def _get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get user contact details"""
        
        # Mock implementation
        return {
            "user_id": user_id,
            "phone": "+919876543210",
            "email": "user@example.com"
        }
    
    def _is_subscription_tier(self, tier: Union[SupportTier, BlackTier]) -> bool:
        """Check if tier requires subscription"""
        return tier != SupportTier.LITE
    
    async def _validate_tier_change(
        self,
        metrics: TierMetrics,
        target_tier: Union[SupportTier, BlackTier]
    ) -> Dict[str, Any]:
        """Validate if tier change is allowed"""
        
        criteria = self.tier_criteria.get(target_tier)
        if not criteria:
            return {"valid": False, "error": "Invalid target tier"}
        
        # Check minimum requirements
        if metrics.portfolio_value < criteria["portfolio_min"]:
            return {
                "valid": False,
                "error": f"Portfolio value ₹{metrics.portfolio_value:,.0f} below minimum ₹{criteria['portfolio_min']:,.0f}",
                "requirements": {"portfolio_min": criteria["portfolio_min"]}
            }
        
        monthly_trades_min = criteria.get("monthly_trades_min", 0)
        if metrics.monthly_trades < monthly_trades_min:
            return {
                "valid": False,
                "error": f"Monthly trades {metrics.monthly_trades} below minimum {monthly_trades_min}",
                "requirements": {"monthly_trades_min": monthly_trades_min}
            }
        
        return {"valid": True}
    
    async def _calculate_financial_impact(
        self,
        current_tier: Union[SupportTier, BlackTier],
        target_tier: Union[SupportTier, BlackTier]
    ) -> Dict[str, float]:
        """Calculate financial impact of tier change"""
        
        # Mock calculation - replace with actual pricing logic
        return {
            "current_monthly_fee": 0 if current_tier == SupportTier.LITE else 99,
            "new_monthly_fee": 0 if target_tier == SupportTier.LITE else 99,
            "setup_fee": 0,
            "proration_credit": 0,
            "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    def _requires_approval(
        self,
        current_tier: Union[SupportTier, BlackTier],
        target_tier: Union[SupportTier, BlackTier]
    ) -> bool:
        """Check if tier change requires manual approval"""
        
        # Black tier upgrades require approval
        if isinstance(target_tier, BlackTier):
            return True
        
        # Downgrades require approval
        if not self._is_upgrade(current_tier, target_tier):
            return True
        
        return False
    
    async def _queue_for_approval(self, change_request: TierChangeRequest):
        """Queue tier change for manual approval"""
        
        # Mock implementation - replace with actual approval workflow
        logger.info(f"Queued tier change for approval: {change_request.request_id}")
    
    async def _update_user_tier(
        self,
        user_id: str,
        new_tier: Union[SupportTier, BlackTier]
    ):
        """Update user's tier in database"""
        
        # Mock implementation - replace with actual database update
        logger.info(f"Updated user {user_id} tier to {new_tier.value}")
    
    async def _log_tier_change(self, change_request: TierChangeRequest):
        """Log tier change for audit purposes"""
        
        # Mock implementation - replace with actual audit logging
        logger.info(f"Tier change logged: {change_request.request_id}")


# Demo usage
async def demo_tier_management():
    """Demonstrate tier management system"""
    
    print("🎯 GridWorks Tier Management System Demo")
    print("=" * 60)
    
    tier_manager = TierManagementSystem()
    
    # Test tier evaluation
    evaluation = await tier_manager.evaluate_tier_eligibility("demo_user_001")
    
    print("📊 Tier Evaluation:")
    print(f"Current Tier: {evaluation.get('current_tier')}")
    print(f"Recommended Tier: {evaluation.get('recommended_tier')}")
    print(f"Change Needed: {evaluation.get('change_needed')}")
    
    if evaluation.get("change_needed"):
        # Test tier change initiation
        change_result = await tier_manager.initiate_tier_change(
            user_id="demo_user_001",
            target_tier=SupportTier.PRO,
            reason=TierChangeReason.PORTFOLIO_GROWTH
        )
        
        print(f"\n🔄 Tier Change Result:")
        print(f"Success: {change_result.get('success')}")
        print(f"Request ID: {change_result.get('request_id')}")
        print(f"Status: {change_result.get('status')}")


if __name__ == "__main__":
    asyncio.run(demo_tier_management())