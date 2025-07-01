"""
GridWorks Black - Butler AI Payment Authorization System
AI-powered payment assistance and authorization for ultra-premium users
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid

from app.black.models import BlackTier
from app.black.market_butler import MarketButler
from app.ai_support.models import SupportTier

logger = logging.getLogger(__name__)


class PaymentAuthorizationLevel(Enum):
    """Authorization levels for butler payment approval"""
    AUTOMATIC = "automatic"
    BUTLER_REVIEW = "butler_review"
    HUMAN_APPROVAL = "human_approval"
    DUAL_AUTHORIZATION = "dual_authorization"
    EMERGENCY_OVERRIDE = "emergency_override"


class PaymentRiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PaymentCategory(Enum):
    """Categories of payments for different handling"""
    SUBSCRIPTION = "subscription"
    TRADING_FEE = "trading_fee"
    LUXURY_SERVICE = "luxury_service"
    INVESTMENT = "investment"
    EMERGENCY = "emergency"
    LIFESTYLE = "lifestyle"


@dataclass
class PaymentContext:
    """Context information for payment authorization"""
    payment_id: str
    user_id: str
    tier: BlackTier
    amount: int
    currency: str
    category: PaymentCategory
    recipient: str
    description: str
    risk_factors: List[str]
    time_sensitive: bool
    recurring: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ButlerAuthorization:
    """Butler authorization decision"""
    authorization_id: str
    payment_id: str
    butler_id: str
    decision: str  # approved, denied, escalated
    confidence: float
    reasoning: str
    conditions: List[str]
    authorized_at: datetime
    expires_at: Optional[datetime]
    human_review_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ButlerPaymentSystem:
    """
    AI-powered Butler Payment Authorization System
    
    Features:
    - Intelligent payment risk assessment
    - Personalized authorization patterns
    - Real-time butler AI decision making
    - Human escalation workflows
    - Emergency payment protocols
    - Lifestyle spending insights
    """
    
    def __init__(self):
        self.market_butler = MarketButler()
        
        # Authorization thresholds by tier (in paise)
        self.authorization_thresholds = {
            BlackTier.ONYX: {
                "automatic": 100000,      # ₹1,000
                "butler_review": 1000000,  # ₹10,000
                "human_approval": 5000000, # ₹50,000
                "dual_authorization": float('inf')
            },
            BlackTier.OBSIDIAN: {
                "automatic": 500000,      # ₹5,000
                "butler_review": 2000000,  # ₹20,000
                "human_approval": 10000000, # ₹1,00,000
                "dual_authorization": 50000000  # ₹5,00,000
            },
            BlackTier.VOID: {
                "automatic": 1000000,     # ₹10,000
                "butler_review": 5000000,  # ₹50,000
                "human_approval": 20000000, # ₹2,00,000
                "dual_authorization": 100000000 # ₹10,00,000
            }
        }
        
        # Risk assessment weights
        self.risk_weights = {
            "amount_anomaly": 0.3,
            "time_anomaly": 0.2,
            "location_anomaly": 0.15,
            "frequency_anomaly": 0.15,
            "merchant_risk": 0.1,
            "behavioral_pattern": 0.1
        }
        
        # Payment category configurations
        self.category_configs = {
            PaymentCategory.SUBSCRIPTION: {
                "auto_approve_recurring": True,
                "risk_multiplier": 0.5,
                "butler_involvement": "minimal"
            },
            PaymentCategory.TRADING_FEE: {
                "auto_approve_recurring": True,
                "risk_multiplier": 0.3,
                "butler_involvement": "none"
            },
            PaymentCategory.LUXURY_SERVICE: {
                "auto_approve_recurring": False,
                "risk_multiplier": 1.0,
                "butler_involvement": "coordination"
            },
            PaymentCategory.INVESTMENT: {
                "auto_approve_recurring": False,
                "risk_multiplier": 1.2,
                "butler_involvement": "advisory"
            },
            PaymentCategory.EMERGENCY: {
                "auto_approve_recurring": False,
                "risk_multiplier": 0.1,
                "butler_involvement": "immediate"
            }
        }
        
        logger.info("Butler Payment System initialized")
    
    async def authorize_payment(
        self,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Main payment authorization flow"""
        
        try:
            logger.info(f"Authorizing payment {payment_context.payment_id} for {payment_context.tier.value} user")
            
            # Step 1: Risk assessment
            risk_assessment = await self._assess_payment_risk(payment_context)
            
            # Step 2: Determine authorization level required
            auth_level = await self._determine_authorization_level(
                payment_context, risk_assessment
            )
            
            # Step 3: Route to appropriate authorization flow
            if auth_level == PaymentAuthorizationLevel.AUTOMATIC:
                return await self._auto_approve_payment(payment_context, risk_assessment)
            
            elif auth_level == PaymentAuthorizationLevel.BUTLER_REVIEW:
                return await self._butler_review_payment(payment_context, risk_assessment)
            
            elif auth_level == PaymentAuthorizationLevel.HUMAN_APPROVAL:
                return await self._human_approval_required(payment_context, risk_assessment)
            
            elif auth_level == PaymentAuthorizationLevel.DUAL_AUTHORIZATION:
                return await self._dual_authorization_required(payment_context, risk_assessment)
            
            elif auth_level == PaymentAuthorizationLevel.EMERGENCY_OVERRIDE:
                return await self._emergency_override_protocol(payment_context, risk_assessment)
            
            else:
                return {"authorized": False, "error": "Unknown authorization level"}
                
        except Exception as e:
            logger.error(f"Payment authorization error: {e}")
            return {"authorized": False, "error": str(e)}
    
    async def _assess_payment_risk(
        self,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Comprehensive payment risk assessment"""
        
        try:
            risk_factors = []
            risk_score = 0.0
            
            # Amount analysis
            amount_risk = await self._analyze_amount_risk(payment_context)
            risk_score += amount_risk["score"] * self.risk_weights["amount_anomaly"]
            if amount_risk["anomaly"]:
                risk_factors.extend(amount_risk["factors"])
            
            # Time pattern analysis
            time_risk = await self._analyze_time_risk(payment_context)
            risk_score += time_risk["score"] * self.risk_weights["time_anomaly"]
            if time_risk["anomaly"]:
                risk_factors.extend(time_risk["factors"])
            
            # Behavioral pattern analysis
            behavioral_risk = await self._analyze_behavioral_risk(payment_context)
            risk_score += behavioral_risk["score"] * self.risk_weights["behavioral_pattern"]
            if behavioral_risk["anomaly"]:
                risk_factors.extend(behavioral_risk["factors"])
            
            # Merchant/recipient risk
            merchant_risk = await self._analyze_merchant_risk(payment_context)
            risk_score += merchant_risk["score"] * self.risk_weights["merchant_risk"]
            if merchant_risk["anomaly"]:
                risk_factors.extend(merchant_risk["factors"])
            
            # Frequency analysis
            frequency_risk = await self._analyze_frequency_risk(payment_context)
            risk_score += frequency_risk["score"] * self.risk_weights["frequency_anomaly"]
            if frequency_risk["anomaly"]:
                risk_factors.extend(frequency_risk["factors"])
            
            # Determine overall risk level
            if risk_score >= 0.8:
                risk_level = PaymentRiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = PaymentRiskLevel.HIGH
            elif risk_score >= 0.3:
                risk_level = PaymentRiskLevel.MEDIUM
            else:
                risk_level = PaymentRiskLevel.LOW
            
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "category_risk": self._get_category_risk_multiplier(payment_context.category),
                "confidence": min(1.0, 1.0 - (risk_score * 0.5)),
                "analysis": {
                    "amount_risk": amount_risk,
                    "time_risk": time_risk,
                    "behavioral_risk": behavioral_risk,
                    "merchant_risk": merchant_risk,
                    "frequency_risk": frequency_risk
                }
            }
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {
                "risk_level": PaymentRiskLevel.HIGH,
                "risk_score": 0.8,
                "risk_factors": ["assessment_error"],
                "error": str(e)
            }
    
    async def _determine_authorization_level(
        self,
        payment_context: PaymentContext,
        risk_assessment: Dict[str, Any]
    ) -> PaymentAuthorizationLevel:
        """Determine required authorization level"""
        
        try:
            amount = payment_context.amount
            tier = payment_context.tier
            risk_level = risk_assessment["risk_level"]
            category = payment_context.category
            
            thresholds = self.authorization_thresholds[tier]
            category_config = self.category_configs[category]
            
            # Emergency payments get special handling
            if category == PaymentCategory.EMERGENCY:
                if amount <= thresholds["butler_review"]:
                    return PaymentAuthorizationLevel.EMERGENCY_OVERRIDE
                else:
                    return PaymentAuthorizationLevel.HUMAN_APPROVAL
            
            # Apply category risk multiplier
            effective_amount = amount * category_config["risk_multiplier"]
            
            # Adjust thresholds based on risk level
            risk_multipliers = {
                PaymentRiskLevel.LOW: 1.5,      # Higher thresholds for low risk
                PaymentRiskLevel.MEDIUM: 1.0,   # Normal thresholds
                PaymentRiskLevel.HIGH: 0.5,     # Lower thresholds for high risk
                PaymentRiskLevel.CRITICAL: 0.2  # Much lower thresholds for critical risk
            }
            
            risk_multiplier = risk_multipliers[risk_level]
            adjusted_thresholds = {
                key: int(value * risk_multiplier) 
                for key, value in thresholds.items()
            }
            
            # Check recurring payment auto-approval
            if (payment_context.recurring and 
                category_config["auto_approve_recurring"] and
                risk_level in [PaymentRiskLevel.LOW, PaymentRiskLevel.MEDIUM]):
                return PaymentAuthorizationLevel.AUTOMATIC
            
            # Determine authorization level based on adjusted thresholds
            if effective_amount <= adjusted_thresholds["automatic"]:
                return PaymentAuthorizationLevel.AUTOMATIC
            elif effective_amount <= adjusted_thresholds["butler_review"]:
                return PaymentAuthorizationLevel.BUTLER_REVIEW
            elif effective_amount <= adjusted_thresholds["human_approval"]:
                return PaymentAuthorizationLevel.HUMAN_APPROVAL
            else:
                return PaymentAuthorizationLevel.DUAL_AUTHORIZATION
                
        except Exception as e:
            logger.error(f"Authorization level determination error: {e}")
            return PaymentAuthorizationLevel.HUMAN_APPROVAL
    
    async def _auto_approve_payment(
        self,
        payment_context: PaymentContext,
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Automatically approve low-risk payments"""
        
        try:
            # Create authorization record
            authorization = ButlerAuthorization(
                authorization_id=f"AUTO_{uuid.uuid4().hex[:12].upper()}",
                payment_id=payment_context.payment_id,
                butler_id="auto_system",
                decision="approved",
                confidence=risk_assessment["confidence"],
                reasoning="Low risk payment auto-approved by system",
                conditions=[],
                authorized_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
            # Store authorization
            await self._store_authorization(authorization)
            
            # Log for user's butler (informational)
            await self._log_auto_approval_for_butler(payment_context, authorization)
            
            return {
                "authorized": True,
                "authorization_id": authorization.authorization_id,
                "method": "automatic",
                "expires_at": authorization.expires_at.isoformat(),
                "risk_level": risk_assessment["risk_level"].value,
                "butler_notified": True
            }
            
        except Exception as e:
            logger.error(f"Auto-approval error: {e}")
            return {"authorized": False, "error": str(e)}
    
    async def _butler_review_payment(
        self,
        payment_context: PaymentContext,
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Butler AI reviews and decides on payment"""
        
        try:
            # Get assigned butler
            butler_info = await self.market_butler.get_assigned_butler(
                payment_context.user_id, payment_context.tier
            )
            
            # Prepare context for butler AI decision
            butler_context = {
                "payment": {
                    "amount": payment_context.amount / 100,  # Convert to rupees
                    "currency": payment_context.currency,
                    "category": payment_context.category.value,
                    "recipient": payment_context.recipient,
                    "description": payment_context.description,
                    "recurring": payment_context.recurring,
                    "time_sensitive": payment_context.time_sensitive
                },
                "user": {
                    "tier": payment_context.tier.value,
                    "user_id": payment_context.user_id,
                    "spending_patterns": await self._get_user_spending_patterns(payment_context.user_id),
                    "preferences": await self._get_user_preferences(payment_context.user_id)
                },
                "risk": {
                    "level": risk_assessment["risk_level"].value,
                    "score": risk_assessment["risk_score"],
                    "factors": risk_assessment["risk_factors"]
                }
            }
            
            # Butler AI decision making
            butler_decision = await self._get_butler_ai_decision(
                butler_info["butler_id"], butler_context
            )
            
            if butler_decision["decision"] == "approved":
                authorization = ButlerAuthorization(
                    authorization_id=f"BUTLER_{uuid.uuid4().hex[:12].upper()}",
                    payment_id=payment_context.payment_id,
                    butler_id=butler_info["butler_id"],
                    decision="approved",
                    confidence=butler_decision["confidence"],
                    reasoning=butler_decision["reasoning"],
                    conditions=butler_decision.get("conditions", []),
                    authorized_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=2)
                )
                
                await self._store_authorization(authorization)
                
                # Send butler notification to user
                await self._send_butler_approval_notification(
                    payment_context, authorization, butler_info
                )
                
                return {
                    "authorized": True,
                    "authorization_id": authorization.authorization_id,
                    "method": "butler_ai",
                    "butler_name": butler_info["name"],
                    "reasoning": authorization.reasoning,
                    "conditions": authorization.conditions,
                    "expires_at": authorization.expires_at.isoformat()
                }
                
            elif butler_decision["decision"] == "escalated":
                # Butler escalates to human review
                escalation = await self._escalate_to_human_review(
                    payment_context, risk_assessment, butler_decision
                )
                
                return {
                    "authorized": False,
                    "escalated": True,
                    "escalation_id": escalation["escalation_id"],
                    "estimated_review_time": escalation["estimated_time"],
                    "butler_reasoning": butler_decision["reasoning"]
                }
                
            else:  # denied
                authorization = ButlerAuthorization(
                    authorization_id=f"DENIED_{uuid.uuid4().hex[:12].upper()}",
                    payment_id=payment_context.payment_id,
                    butler_id=butler_info["butler_id"],
                    decision="denied",
                    confidence=butler_decision["confidence"],
                    reasoning=butler_decision["reasoning"],
                    conditions=[],
                    authorized_at=datetime.now(),
                    expires_at=None
                )
                
                await self._store_authorization(authorization)
                
                # Send butler denial notification
                await self._send_butler_denial_notification(
                    payment_context, authorization, butler_info
                )
                
                return {
                    "authorized": False,
                    "authorization_id": authorization.authorization_id,
                    "method": "butler_ai",
                    "butler_name": butler_info["name"],
                    "reasoning": authorization.reasoning,
                    "appeal_available": True
                }
                
        except Exception as e:
            logger.error(f"Butler review error: {e}")
            return {"authorized": False, "error": str(e)}
    
    async def _get_butler_ai_decision(
        self,
        butler_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get AI decision from butler system"""
        
        try:
            # Butler AI decision logic based on context
            payment_amount = context["payment"]["amount"]
            risk_level = context["risk"]["level"]
            category = context["payment"]["category"]
            user_patterns = context["user"]["spending_patterns"]
            
            # Decision factors
            confidence = 0.8
            
            # Amount analysis
            if payment_amount > user_patterns.get("monthly_average", 0) * 3:
                confidence -= 0.2
                if risk_level in ["high", "critical"]:
                    return {
                        "decision": "escalated",
                        "confidence": confidence,
                        "reasoning": f"Payment amount significantly exceeds typical spending pattern. Amount: ₹{payment_amount:,.2f}, Monthly average: ₹{user_patterns.get('monthly_average', 0):,.2f}"
                    }
            
            # Risk level analysis
            if risk_level == "critical":
                return {
                    "decision": "escalated",
                    "confidence": 0.9,
                    "reasoning": "Critical risk level detected - human review required for security"
                }
            elif risk_level == "high":
                confidence -= 0.3
                if category not in ["subscription", "trading_fee"]:
                    return {
                        "decision": "escalated",
                        "confidence": confidence,
                        "reasoning": "High risk payment outside of routine categories requires human oversight"
                    }
            
            # Category-specific logic
            if category == "emergency":
                return {
                    "decision": "approved",
                    "confidence": 0.95,
                    "reasoning": "Emergency payment approved - notifying human oversight team",
                    "conditions": ["emergency_protocols_activated"]
                }
            
            if category in ["subscription", "trading_fee"] and context["payment"]["recurring"]:
                return {
                    "decision": "approved",
                    "confidence": 0.9,
                    "reasoning": "Recurring payment for essential service approved"
                }
            
            # Default approval for low-medium risk
            if risk_level in ["low", "medium"] and confidence > 0.6:
                return {
                    "decision": "approved",
                    "confidence": confidence,
                    "reasoning": f"Payment approved based on {risk_level} risk assessment and spending pattern analysis"
                }
            
            # Default to escalation for unclear cases
            return {
                "decision": "escalated",
                "confidence": 0.5,
                "reasoning": "Payment requires human review due to insufficient confidence in automated decision"
            }
            
        except Exception as e:
            logger.error(f"Butler AI decision error: {e}")
            return {
                "decision": "escalated",
                "confidence": 0.0,
                "reasoning": f"Technical error in AI decision making: {str(e)}"
            }
    
    async def _analyze_amount_risk(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Analyze payment amount for anomalies"""
        
        try:
            user_patterns = await self._get_user_spending_patterns(payment_context.user_id)
            amount = payment_context.amount / 100  # Convert to rupees
            
            monthly_avg = user_patterns.get("monthly_average", 50000)  # Default ₹50K
            max_transaction = user_patterns.get("max_transaction", 100000)  # Default ₹1L
            category_avg = user_patterns.get(f"{payment_context.category.value}_average", monthly_avg * 0.1)
            
            anomaly_factors = []
            risk_score = 0.0
            
            # Check against user's maximum transaction
            if amount > max_transaction * 2:
                anomaly_factors.append("amount_exceeds_historical_maximum")
                risk_score += 0.4
            elif amount > max_transaction:
                anomaly_factors.append("amount_near_historical_maximum")
                risk_score += 0.2
            
            # Check against monthly average
            if amount > monthly_avg * 0.5:
                anomaly_factors.append("significant_portion_of_monthly_spending")
                risk_score += 0.2
            
            # Check against category average
            if amount > category_avg * 5:
                anomaly_factors.append("amount_significantly_above_category_average")
                risk_score += 0.3
            
            return {
                "score": min(1.0, risk_score),
                "anomaly": len(anomaly_factors) > 0,
                "factors": anomaly_factors,
                "analysis": {
                    "amount": amount,
                    "monthly_average": monthly_avg,
                    "category_average": category_avg,
                    "max_historical": max_transaction
                }
            }
            
        except Exception as e:
            return {"score": 0.5, "anomaly": True, "factors": ["analysis_error"], "error": str(e)}
    
    async def _analyze_time_risk(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Analyze payment timing for anomalies"""
        
        try:
            current_time = datetime.now()
            anomaly_factors = []
            risk_score = 0.0
            
            # Check for unusual hours
            if current_time.hour < 6 or current_time.hour > 23:
                anomaly_factors.append("unusual_time_of_day")
                risk_score += 0.3
            
            # Check for weekend/holiday patterns (simplified)
            if current_time.weekday() >= 5:  # Saturday/Sunday
                if payment_context.category not in [PaymentCategory.EMERGENCY, PaymentCategory.LIFESTYLE]:
                    anomaly_factors.append("business_payment_on_weekend")
                    risk_score += 0.1
            
            # Check time sensitivity vs amount
            if payment_context.time_sensitive and payment_context.amount > 1000000:  # >₹10K
                anomaly_factors.append("large_urgent_payment")
                risk_score += 0.2
            
            return {
                "score": min(1.0, risk_score),
                "anomaly": len(anomaly_factors) > 0,
                "factors": anomaly_factors,
                "analysis": {
                    "current_hour": current_time.hour,
                    "is_weekend": current_time.weekday() >= 5,
                    "is_time_sensitive": payment_context.time_sensitive
                }
            }
            
        except Exception as e:
            return {"score": 0.3, "anomaly": True, "factors": ["analysis_error"], "error": str(e)}
    
    async def _analyze_behavioral_risk(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Analyze behavioral patterns for anomalies"""
        
        # Mock implementation - would analyze user's historical behavior
        return {
            "score": 0.1,
            "anomaly": False,
            "factors": [],
            "analysis": {"behavior_consistent": True}
        }
    
    async def _analyze_merchant_risk(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Analyze merchant/recipient risk"""
        
        # Mock implementation - would check merchant reputation, blacklists, etc.
        return {
            "score": 0.1,
            "anomaly": False,
            "factors": [],
            "analysis": {"merchant_trusted": True}
        }
    
    async def _analyze_frequency_risk(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Analyze payment frequency for anomalies"""
        
        # Mock implementation - would analyze payment frequency patterns
        return {
            "score": 0.1,
            "anomaly": False,
            "factors": [],
            "analysis": {"frequency_normal": True}
        }
    
    def _get_category_risk_multiplier(self, category: PaymentCategory) -> float:
        """Get risk multiplier for payment category"""
        
        return self.category_configs[category]["risk_multiplier"]
    
    async def _get_user_spending_patterns(self, user_id: str) -> Dict[str, float]:
        """Get user's historical spending patterns"""
        
        # Mock implementation - would fetch from analytics database
        return {
            "monthly_average": 150000,  # ₹1.5L per month
            "max_transaction": 500000,  # ₹5L max transaction
            "subscription_average": 15000,  # ₹15K subscriptions
            "trading_fee_average": 5000,   # ₹5K trading fees
            "luxury_service_average": 75000,  # ₹75K luxury services
            "investment_average": 200000,  # ₹2L investments
        }
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's authorization preferences"""
        
        # Mock implementation
        return {
            "auto_approve_subscriptions": True,
            "auto_approve_trading_fees": True,
            "require_approval_above": 100000,  # ₹1L
            "emergency_contacts": ["+919876543210"],
            "preferred_authorization_method": "butler_ai"
        }
    
    async def _store_authorization(self, authorization: ButlerAuthorization):
        """Store authorization decision"""
        
        # Mock implementation
        logger.info(f"Stored authorization: {authorization.authorization_id}")
    
    async def _send_butler_approval_notification(
        self,
        payment_context: PaymentContext,
        authorization: ButlerAuthorization,
        butler_info: Dict[str, Any]
    ):
        """Send butler approval notification to user"""
        
        # Mock implementation - would send through appropriate channel
        logger.info(f"Butler {butler_info['name']} approved payment {payment_context.payment_id}")


# Demo usage
async def demo_butler_payment_system():
    """Demonstrate Butler AI payment authorization"""
    
    print("🤖 GridWorks Black - Butler AI Payment System Demo")
    print("=" * 60)
    
    butler_system = ButlerPaymentSystem()
    
    # Test payment authorization
    payment_context = PaymentContext(
        payment_id="PAY_DEMO_001",
        user_id="obsidian_user_001",
        tier=BlackTier.OBSIDIAN,
        amount=75000,  # ₹750
        currency="INR",
        category=PaymentCategory.LUXURY_SERVICE,
        recipient="Four Seasons Hotel",
        description="Premium suite reservation",
        risk_factors=[],
        time_sensitive=False,
        recurring=False,
        metadata={"booking_id": "FS_2024_001"}
    )
    
    authorization = await butler_system.authorize_payment(payment_context)
    
    print("🔐 Payment Authorization:")
    print(f"Authorized: {authorization.get('authorized')}")
    print(f"Method: {authorization.get('method')}")
    if authorization.get('butler_name'):
        print(f"Butler: {authorization.get('butler_name')}")
    print(f"Reasoning: {authorization.get('reasoning')}")
    
    # Test high-risk payment
    high_risk_payment = PaymentContext(
        payment_id="PAY_DEMO_002",
        user_id="void_user_001",
        tier=BlackTier.VOID,
        amount=10000000,  # ₹1 Cr
        currency="INR",
        category=PaymentCategory.INVESTMENT,
        recipient="Private Equity Fund",
        description="Investment opportunity",
        risk_factors=["large_amount", "new_recipient"],
        time_sensitive=True,
        recurring=False
    )
    
    high_risk_auth = await butler_system.authorize_payment(high_risk_payment)
    
    print(f"\n💰 High-Risk Payment Authorization:")
    print(f"Authorized: {high_risk_auth.get('authorized')}")
    print(f"Escalated: {high_risk_auth.get('escalated', False)}")
    print(f"Reasoning: {high_risk_auth.get('butler_reasoning', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(demo_butler_payment_system())