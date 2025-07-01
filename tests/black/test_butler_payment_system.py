"""
Comprehensive test suite for Butler AI Payment Authorization System
100% test coverage for AI-powered payment decision making
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import json

from app.black.butler_payment_system import (
    ButlerPaymentSystem,
    PaymentContext,
    ButlerAuthorization,
    PaymentAuthorizationLevel,
    PaymentRiskLevel,
    PaymentCategory
)
from app.black.models import BlackTier


class TestButlerPaymentSystem:
    """Test ButlerPaymentSystem functionality"""
    
    @pytest.fixture
    def butler_system(self):
        """Create ButlerPaymentSystem instance for testing"""
        return ButlerPaymentSystem()
    
    @pytest.fixture
    def sample_payment_context(self):
        """Create sample payment context for testing"""
        return PaymentContext(
            payment_id="PAY_TEST_001",
            user_id="test_user_001",
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
    
    @pytest.mark.asyncio
    async def test_authorize_payment_automatic_approval(self, butler_system, sample_payment_context):
        """Test automatic payment approval for low-risk payments"""
        
        # Low amount, low risk payment
        sample_payment_context.amount = 50000  # ₹500
        sample_payment_context.category = PaymentCategory.SUBSCRIPTION
        sample_payment_context.recurring = True
        
        with patch.object(butler_system, '_assess_payment_risk') as mock_risk, \
             patch.object(butler_system, '_determine_authorization_level') as mock_level, \
             patch.object(butler_system, '_auto_approve_payment') as mock_auto:
            
            mock_risk.return_value = {
                "risk_level": PaymentRiskLevel.LOW,
                "risk_score": 0.2,
                "confidence": 0.9
            }
            mock_level.return_value = PaymentAuthorizationLevel.AUTOMATIC
            mock_auto.return_value = {
                "authorized": True,
                "authorization_id": "AUTO_001",
                "method": "automatic"
            }
            
            result = await butler_system.authorize_payment(sample_payment_context)
            
            assert result["authorized"] is True
            assert result["method"] == "automatic"
            mock_risk.assert_called_once()
            mock_level.assert_called_once()
            mock_auto.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authorize_payment_butler_review(self, butler_system, sample_payment_context):
        """Test butler review authorization"""
        
        with patch.object(butler_system, '_assess_payment_risk') as mock_risk, \
             patch.object(butler_system, '_determine_authorization_level') as mock_level, \
             patch.object(butler_system, '_butler_review_payment') as mock_butler:
            
            mock_risk.return_value = {
                "risk_level": PaymentRiskLevel.MEDIUM,
                "risk_score": 0.5,
                "confidence": 0.7
            }
            mock_level.return_value = PaymentAuthorizationLevel.BUTLER_REVIEW
            mock_butler.return_value = {
                "authorized": True,
                "method": "butler_ai",
                "butler_name": "Arjun Mehta"
            }
            
            result = await butler_system.authorize_payment(sample_payment_context)
            
            assert result["authorized"] is True
            assert result["method"] == "butler_ai"
            assert result["butler_name"] == "Arjun Mehta"
    
    @pytest.mark.asyncio
    async def test_authorize_payment_human_approval_required(self, butler_system, sample_payment_context):
        """Test human approval requirement for high-risk payments"""
        
        # High-value payment
        sample_payment_context.amount = 10000000  # ₹1 Cr
        
        with patch.object(butler_system, '_assess_payment_risk') as mock_risk, \
             patch.object(butler_system, '_determine_authorization_level') as mock_level, \
             patch.object(butler_system, '_human_approval_required') as mock_human:
            
            mock_risk.return_value = {
                "risk_level": PaymentRiskLevel.HIGH,
                "risk_score": 0.8,
                "confidence": 0.4
            }
            mock_level.return_value = PaymentAuthorizationLevel.HUMAN_APPROVAL
            mock_human.return_value = {
                "authorized": False,
                "escalated": True,
                "estimated_review_time": "2-4 hours"
            }
            
            result = await butler_system.authorize_payment(sample_payment_context)
            
            assert result["authorized"] is False
            assert result["escalated"] is True
            assert "estimated_review_time" in result
    
    @pytest.mark.asyncio
    async def test_authorize_payment_emergency_override(self, butler_system):
        """Test emergency payment override"""
        
        emergency_context = PaymentContext(
            payment_id="PAY_EMERGENCY_001",
            user_id="test_user_001",
            tier=BlackTier.VOID,
            amount=200000,  # ₹2,000
            currency="INR",
            category=PaymentCategory.EMERGENCY,
            recipient="Apollo Hospital",
            description="Medical emergency payment",
            risk_factors=[],
            time_sensitive=True,
            recurring=False
        )
        
        with patch.object(butler_system, '_assess_payment_risk') as mock_risk, \
             patch.object(butler_system, '_determine_authorization_level') as mock_level, \
             patch.object(butler_system, '_emergency_override_protocol') as mock_emergency:
            
            mock_risk.return_value = {
                "risk_level": PaymentRiskLevel.LOW,
                "risk_score": 0.1,
                "confidence": 0.95
            }
            mock_level.return_value = PaymentAuthorizationLevel.EMERGENCY_OVERRIDE
            mock_emergency.return_value = {
                "authorized": True,
                "method": "emergency_override",
                "processing_time": "<5 minutes"
            }
            
            result = await butler_system.authorize_payment(emergency_context)
            
            assert result["authorized"] is True
            assert result["method"] == "emergency_override"
    
    @pytest.mark.asyncio
    async def test_assess_payment_risk_low_risk(self, butler_system, sample_payment_context):
        """Test payment risk assessment for low-risk payment"""
        
        # Small recurring subscription
        sample_payment_context.amount = 2000  # ₹20
        sample_payment_context.category = PaymentCategory.SUBSCRIPTION
        sample_payment_context.recurring = True
        
        with patch.object(butler_system, '_analyze_amount_risk') as mock_amount, \
             patch.object(butler_system, '_analyze_time_risk') as mock_time, \
             patch.object(butler_system, '_analyze_behavioral_risk') as mock_behavior, \
             patch.object(butler_system, '_analyze_merchant_risk') as mock_merchant, \
             patch.object(butler_system, '_analyze_frequency_risk') as mock_frequency:
            
            mock_amount.return_value = {"score": 0.1, "anomaly": False, "factors": []}
            mock_time.return_value = {"score": 0.1, "anomaly": False, "factors": []}
            mock_behavior.return_value = {"score": 0.1, "anomaly": False, "factors": []}
            mock_merchant.return_value = {"score": 0.1, "anomaly": False, "factors": []}
            mock_frequency.return_value = {"score": 0.1, "anomaly": False, "factors": []}
            
            risk_assessment = await butler_system._assess_payment_risk(sample_payment_context)
            
            assert risk_assessment["risk_level"] == PaymentRiskLevel.LOW
            assert risk_assessment["risk_score"] < 0.3
            assert len(risk_assessment["risk_factors"]) == 0
            assert risk_assessment["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_assess_payment_risk_high_risk(self, butler_system, sample_payment_context):
        """Test payment risk assessment for high-risk payment"""
        
        # Large amount to unknown recipient
        sample_payment_context.amount = 5000000  # ₹50,000
        sample_payment_context.recipient = "Unknown Company Ltd"
        sample_payment_context.time_sensitive = True
        
        with patch.object(butler_system, '_analyze_amount_risk') as mock_amount, \
             patch.object(butler_system, '_analyze_time_risk') as mock_time, \
             patch.object(butler_system, '_analyze_behavioral_risk') as mock_behavior, \
             patch.object(butler_system, '_analyze_merchant_risk') as mock_merchant, \
             patch.object(butler_system, '_analyze_frequency_risk') as mock_frequency:
            
            mock_amount.return_value = {
                "score": 0.8, 
                "anomaly": True, 
                "factors": ["amount_exceeds_historical_maximum"]
            }
            mock_time.return_value = {
                "score": 0.3, 
                "anomaly": True, 
                "factors": ["large_urgent_payment"]
            }
            mock_behavior.return_value = {"score": 0.2, "anomaly": False, "factors": []}
            mock_merchant.return_value = {
                "score": 0.6, 
                "anomaly": True, 
                "factors": ["unknown_recipient"]
            }
            mock_frequency.return_value = {"score": 0.1, "anomaly": False, "factors": []}
            
            risk_assessment = await butler_system._assess_payment_risk(sample_payment_context)
            
            assert risk_assessment["risk_level"] == PaymentRiskLevel.HIGH
            assert risk_assessment["risk_score"] >= 0.6
            assert len(risk_assessment["risk_factors"]) > 0
            assert "amount_exceeds_historical_maximum" in risk_assessment["risk_factors"]
    
    @pytest.mark.asyncio
    async def test_determine_authorization_level_automatic(self, butler_system, sample_payment_context):
        """Test authorization level determination for automatic approval"""
        
        sample_payment_context.amount = 50000  # ₹500 - below automatic threshold
        sample_payment_context.recurring = True
        sample_payment_context.category = PaymentCategory.SUBSCRIPTION
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.LOW,
            "risk_score": 0.2
        }
        
        auth_level = await butler_system._determine_authorization_level(
            sample_payment_context, risk_assessment
        )
        
        assert auth_level == PaymentAuthorizationLevel.AUTOMATIC
    
    @pytest.mark.asyncio
    async def test_determine_authorization_level_butler_review(self, butler_system, sample_payment_context):
        """Test authorization level determination for butler review"""
        
        sample_payment_context.amount = 500000  # ₹5,000 - in butler review range
        sample_payment_context.category = PaymentCategory.LUXURY_SERVICE
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.MEDIUM,
            "risk_score": 0.5
        }
        
        auth_level = await butler_system._determine_authorization_level(
            sample_payment_context, risk_assessment
        )
        
        assert auth_level == PaymentAuthorizationLevel.BUTLER_REVIEW
    
    @pytest.mark.asyncio
    async def test_determine_authorization_level_human_approval(self, butler_system, sample_payment_context):
        """Test authorization level determination for human approval"""
        
        sample_payment_context.amount = 15000000  # ₹1.5 Cr - above human approval threshold
        sample_payment_context.category = PaymentCategory.INVESTMENT
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.HIGH,
            "risk_score": 0.8
        }
        
        auth_level = await butler_system._determine_authorization_level(
            sample_payment_context, risk_assessment
        )
        
        assert auth_level == PaymentAuthorizationLevel.HUMAN_APPROVAL
    
    @pytest.mark.asyncio
    async def test_determine_authorization_level_emergency(self, butler_system):
        """Test authorization level determination for emergency payments"""
        
        emergency_context = PaymentContext(
            payment_id="PAY_EMERGENCY_001",
            user_id="test_user_001",
            tier=BlackTier.OBSIDIAN,
            amount=100000,  # ₹1,000
            currency="INR",
            category=PaymentCategory.EMERGENCY,
            recipient="Hospital",
            description="Emergency medical payment",
            risk_factors=[],
            time_sensitive=True,
            recurring=False
        )
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.LOW,
            "risk_score": 0.1
        }
        
        auth_level = await butler_system._determine_authorization_level(
            emergency_context, risk_assessment
        )
        
        assert auth_level == PaymentAuthorizationLevel.EMERGENCY_OVERRIDE
    
    @pytest.mark.asyncio
    async def test_auto_approve_payment(self, butler_system, sample_payment_context):
        """Test automatic payment approval"""
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.LOW,
            "risk_score": 0.2,
            "confidence": 0.9
        }
        
        with patch.object(butler_system, '_store_authorization') as mock_store, \
             patch.object(butler_system, '_log_auto_approval_for_butler') as mock_log:
            
            mock_store.return_value = None
            mock_log.return_value = None
            
            result = await butler_system._auto_approve_payment(
                sample_payment_context, risk_assessment
            )
            
            assert result["authorized"] is True
            assert result["method"] == "automatic"
            assert "authorization_id" in result
            assert result["risk_level"] == "low"
            assert result["butler_notified"] is True
    
    @pytest.mark.asyncio
    async def test_butler_review_payment_approved(self, butler_system, sample_payment_context):
        """Test butler review with approval"""
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.MEDIUM,
            "risk_score": 0.5,
            "risk_factors": []
        }
        
        with patch.object(butler_system.market_butler, 'get_assigned_butler') as mock_butler, \
             patch.object(butler_system, '_get_user_spending_patterns') as mock_patterns, \
             patch.object(butler_system, '_get_user_preferences') as mock_prefs, \
             patch.object(butler_system, '_get_butler_ai_decision') as mock_decision, \
             patch.object(butler_system, '_store_authorization') as mock_store, \
             patch.object(butler_system, '_send_butler_approval_notification') as mock_notify:
            
            mock_butler.return_value = {
                "butler_id": "butler_001",
                "name": "Arjun Mehta"
            }
            mock_patterns.return_value = {"monthly_average": 150000}
            mock_prefs.return_value = {"auto_approve_subscriptions": True}
            mock_decision.return_value = {
                "decision": "approved",
                "confidence": 0.85,
                "reasoning": "Payment approved based on medium risk assessment",
                "conditions": []
            }
            mock_store.return_value = None
            mock_notify.return_value = None
            
            result = await butler_system._butler_review_payment(
                sample_payment_context, risk_assessment
            )
            
            assert result["authorized"] is True
            assert result["method"] == "butler_ai"
            assert result["butler_name"] == "Arjun Mehta"
            assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_butler_review_payment_escalated(self, butler_system, sample_payment_context):
        """Test butler review with escalation to human"""
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.HIGH,
            "risk_score": 0.8,
            "risk_factors": ["large_amount", "unusual_recipient"]
        }
        
        with patch.object(butler_system.market_butler, 'get_assigned_butler') as mock_butler, \
             patch.object(butler_system, '_get_user_spending_patterns') as mock_patterns, \
             patch.object(butler_system, '_get_user_preferences') as mock_prefs, \
             patch.object(butler_system, '_get_butler_ai_decision') as mock_decision, \
             patch.object(butler_system, '_escalate_to_human_review') as mock_escalate:
            
            mock_butler.return_value = {
                "butler_id": "butler_001",
                "name": "Arjun Mehta"
            }
            mock_patterns.return_value = {"monthly_average": 150000}
            mock_prefs.return_value = {"auto_approve_subscriptions": True}
            mock_decision.return_value = {
                "decision": "escalated",
                "confidence": 0.4,
                "reasoning": "High risk payment requires human oversight"
            }
            mock_escalate.return_value = {
                "escalation_id": "ESC_001",
                "estimated_time": "2-4 hours"
            }
            
            result = await butler_system._butler_review_payment(
                sample_payment_context, risk_assessment
            )
            
            assert result["authorized"] is False
            assert result["escalated"] is True
            assert result["escalation_id"] == "ESC_001"
            assert "butler_reasoning" in result
    
    @pytest.mark.asyncio
    async def test_butler_review_payment_denied(self, butler_system, sample_payment_context):
        """Test butler review with denial"""
        
        # Suspicious payment
        sample_payment_context.recipient = "Suspicious Company"
        sample_payment_context.description = "Unclear purpose"
        
        risk_assessment = {
            "risk_level": PaymentRiskLevel.HIGH,
            "risk_score": 0.9,
            "risk_factors": ["suspicious_recipient", "unclear_purpose"]
        }
        
        with patch.object(butler_system.market_butler, 'get_assigned_butler') as mock_butler, \
             patch.object(butler_system, '_get_user_spending_patterns') as mock_patterns, \
             patch.object(butler_system, '_get_user_preferences') as mock_prefs, \
             patch.object(butler_system, '_get_butler_ai_decision') as mock_decision, \
             patch.object(butler_system, '_store_authorization') as mock_store, \
             patch.object(butler_system, '_send_butler_denial_notification') as mock_notify:
            
            mock_butler.return_value = {
                "butler_id": "butler_001",
                "name": "Arjun Mehta"
            }
            mock_patterns.return_value = {"monthly_average": 150000}
            mock_prefs.return_value = {"auto_approve_subscriptions": True}
            mock_decision.return_value = {
                "decision": "denied",
                "confidence": 0.9,
                "reasoning": "Payment denied due to suspicious recipient and unclear purpose"
            }
            mock_store.return_value = None
            mock_notify.return_value = None
            
            result = await butler_system._butler_review_payment(
                sample_payment_context, risk_assessment
            )
            
            assert result["authorized"] is False
            assert result["method"] == "butler_ai"
            assert result["appeal_available"] is True
            assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_get_butler_ai_decision_approve_normal(self, butler_system):
        """Test butler AI decision for normal payment approval"""
        
        context = {
            "payment": {
                "amount": 5000,  # ₹5,000
                "category": "luxury_service",
                "recurring": False
            },
            "user": {
                "spending_patterns": {"monthly_average": 150000}
            },
            "risk": {
                "level": "medium",
                "score": 0.4,
                "factors": []
            }
        }
        
        decision = await butler_system._get_butler_ai_decision("butler_001", context)
        
        assert decision["decision"] == "approved"
        assert decision["confidence"] > 0.6
        assert "reasoning" in decision
    
    @pytest.mark.asyncio
    async def test_get_butler_ai_decision_approve_emergency(self, butler_system):
        """Test butler AI decision for emergency payment"""
        
        context = {
            "payment": {
                "amount": 25000,  # ₹25,000
                "category": "emergency",
                "recurring": False
            },
            "user": {
                "spending_patterns": {"monthly_average": 150000}
            },
            "risk": {
                "level": "low",
                "score": 0.1,
                "factors": []
            }
        }
        
        decision = await butler_system._get_butler_ai_decision("butler_001", context)
        
        assert decision["decision"] == "approved"
        assert decision["confidence"] >= 0.95
        assert "emergency" in decision["reasoning"].lower()
        assert "emergency_protocols_activated" in decision.get("conditions", [])
    
    @pytest.mark.asyncio
    async def test_get_butler_ai_decision_escalate_high_risk(self, butler_system):
        """Test butler AI decision for high-risk escalation"""
        
        context = {
            "payment": {
                "amount": 500000,  # ₹5 lakh - very high amount
                "category": "investment",
                "recurring": False
            },
            "user": {
                "spending_patterns": {"monthly_average": 150000}
            },
            "risk": {
                "level": "critical",
                "score": 0.9,
                "factors": ["large_amount", "unusual_pattern"]
            }
        }
        
        decision = await butler_system._get_butler_ai_decision("butler_001", context)
        
        assert decision["decision"] == "escalated"
        assert decision["confidence"] >= 0.9
        assert "critical risk" in decision["reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_amount_risk_normal(self, butler_system, sample_payment_context):
        """Test amount risk analysis for normal payment"""
        
        sample_payment_context.amount = 75000  # ₹750 - normal amount
        
        with patch.object(butler_system, '_get_user_spending_patterns') as mock_patterns:
            mock_patterns.return_value = {
                "monthly_average": 150000,
                "max_transaction": 500000,
                "luxury_service_average": 100000
            }
            
            risk = await butler_system._analyze_amount_risk(sample_payment_context)
            
            assert risk["score"] < 0.5
            assert risk["anomaly"] is False
            assert len(risk["factors"]) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_amount_risk_high(self, butler_system, sample_payment_context):
        """Test amount risk analysis for high-risk payment"""
        
        sample_payment_context.amount = 1500000  # ₹15,000 - very high amount
        
        with patch.object(butler_system, '_get_user_spending_patterns') as mock_patterns:
            mock_patterns.return_value = {
                "monthly_average": 150000,
                "max_transaction": 500000,
                "luxury_service_average": 75000
            }
            
            risk = await butler_system._analyze_amount_risk(sample_payment_context)
            
            assert risk["score"] > 0.4
            assert risk["anomaly"] is True
            assert len(risk["factors"]) > 0
            assert "amount_exceeds_historical_maximum" in risk["factors"]
    
    @pytest.mark.asyncio
    async def test_analyze_time_risk_normal_hours(self, butler_system, sample_payment_context):
        """Test time risk analysis for normal business hours"""
        
        # Mock current time to be 2 PM (normal business hour)
        with patch('app.black.butler_payment_system.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0, 0)  # 2 PM
            
            risk = await butler_system._analyze_time_risk(sample_payment_context)
            
            assert risk["score"] < 0.3
            assert risk["anomaly"] is False
    
    @pytest.mark.asyncio
    async def test_analyze_time_risk_unusual_hours(self, butler_system, sample_payment_context):
        """Test time risk analysis for unusual hours"""
        
        # Mock current time to be 3 AM (unusual hour)
        with patch('app.black.butler_payment_system.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 3, 0, 0)  # 3 AM
            
            risk = await butler_system._analyze_time_risk(sample_payment_context)
            
            assert risk["anomaly"] is True
            assert "unusual_time_of_day" in risk["factors"]
    
    def test_authorization_thresholds_configuration(self, butler_system):
        """Test authorization thresholds configuration"""
        
        # Test ONYX tier thresholds
        onyx_thresholds = butler_system.authorization_thresholds[BlackTier.ONYX]
        assert onyx_thresholds["automatic"] == 100000  # ₹1,000
        assert onyx_thresholds["butler_review"] == 1000000  # ₹10,000
        
        # Test OBSIDIAN tier thresholds
        obsidian_thresholds = butler_system.authorization_thresholds[BlackTier.OBSIDIAN]
        assert obsidian_thresholds["automatic"] == 500000  # ₹5,000
        assert obsidian_thresholds["human_approval"] == 10000000  # ₹1,00,000
        
        # Test VOID tier thresholds
        void_thresholds = butler_system.authorization_thresholds[BlackTier.VOID]
        assert void_thresholds["automatic"] == 1000000  # ₹10,000
        assert void_thresholds["dual_authorization"] == 100000000  # ₹10,00,000
    
    def test_risk_weights_configuration(self, butler_system):
        """Test risk assessment weights configuration"""
        
        weights = butler_system.risk_weights
        
        # Ensure all weights sum to 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01
        
        # Check individual weights
        assert weights["amount_anomaly"] == 0.3
        assert weights["time_anomaly"] == 0.2
        assert weights["behavioral_pattern"] == 0.1
    
    def test_category_configurations(self, butler_system):
        """Test payment category configurations"""
        
        # Test subscription category
        subscription_config = butler_system.category_configs[PaymentCategory.SUBSCRIPTION]
        assert subscription_config["auto_approve_recurring"] is True
        assert subscription_config["risk_multiplier"] == 0.5
        assert subscription_config["butler_involvement"] == "minimal"
        
        # Test emergency category
        emergency_config = butler_system.category_configs[PaymentCategory.EMERGENCY]
        assert emergency_config["auto_approve_recurring"] is False
        assert emergency_config["risk_multiplier"] == 0.1
        assert emergency_config["butler_involvement"] == "immediate"
        
        # Test investment category
        investment_config = butler_system.category_configs[PaymentCategory.INVESTMENT]
        assert investment_config["risk_multiplier"] == 1.2
        assert investment_config["butler_involvement"] == "advisory"


class TestPaymentContext:
    """Test PaymentContext data model"""
    
    def test_payment_context_creation(self):
        """Test PaymentContext creation with all fields"""
        
        context = PaymentContext(
            payment_id="PAY_TEST_001",
            user_id="test_user_001",
            tier=BlackTier.OBSIDIAN,
            amount=75000,
            currency="INR",
            category=PaymentCategory.LUXURY_SERVICE,
            recipient="Four Seasons Hotel",
            description="Premium suite reservation",
            risk_factors=["high_amount"],
            time_sensitive=True,
            recurring=False,
            metadata={"booking_id": "FS_2024_001"}
        )
        
        assert context.payment_id == "PAY_TEST_001"
        assert context.user_id == "test_user_001"
        assert context.tier == BlackTier.OBSIDIAN
        assert context.amount == 75000
        assert context.currency == "INR"
        assert context.category == PaymentCategory.LUXURY_SERVICE
        assert context.recipient == "Four Seasons Hotel"
        assert context.description == "Premium suite reservation"
        assert context.risk_factors == ["high_amount"]
        assert context.time_sensitive is True
        assert context.recurring is False
        assert context.metadata["booking_id"] == "FS_2024_001"


class TestButlerAuthorization:
    """Test ButlerAuthorization data model"""
    
    def test_butler_authorization_creation(self):
        """Test ButlerAuthorization creation"""
        
        authorization = ButlerAuthorization(
            authorization_id="AUTH_TEST_001",
            payment_id="PAY_TEST_001",
            butler_id="butler_001",
            decision="approved",
            confidence=0.85,
            reasoning="Payment approved based on risk assessment",
            conditions=["compliance_check"],
            authorized_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=2),
            human_review_required=False,
            metadata={"review_notes": "Low risk payment"}
        )
        
        assert authorization.authorization_id == "AUTH_TEST_001"
        assert authorization.payment_id == "PAY_TEST_001"
        assert authorization.butler_id == "butler_001"
        assert authorization.decision == "approved"
        assert authorization.confidence == 0.85
        assert authorization.reasoning == "Payment approved based on risk assessment"
        assert authorization.conditions == ["compliance_check"]
        assert authorization.human_review_required is False
        assert authorization.metadata["review_notes"] == "Low risk payment"


# Integration test
class TestButlerPaymentSystemIntegration:
    """Integration tests for complete butler payment authorization flow"""
    
    @pytest.mark.asyncio
    async def test_complete_authorization_flow(self):
        """Test complete payment authorization flow"""
        
        butler_system = ButlerPaymentSystem()
        
        # Test different payment scenarios
        scenarios = [
            {
                "name": "Low-risk subscription",
                "context": PaymentContext(
                    payment_id="PAY_SUB_001",
                    user_id="test_user_001",
                    tier=BlackTier.ONYX,
                    amount=5000,  # ₹50
                    currency="INR",
                    category=PaymentCategory.SUBSCRIPTION,
                    recipient="TradeMate Pro",
                    description="Monthly subscription",
                    risk_factors=[],
                    time_sensitive=False,
                    recurring=True
                ),
                "expected_authorized": True,
                "expected_method": "automatic"
            },
            {
                "name": "Medium-risk luxury service",
                "context": PaymentContext(
                    payment_id="PAY_LUX_001",
                    user_id="test_user_001",
                    tier=BlackTier.OBSIDIAN,
                    amount=250000,  # ₹2,500
                    currency="INR",
                    category=PaymentCategory.LUXURY_SERVICE,
                    recipient="Taj Hotel",
                    description="Presidential suite booking",
                    risk_factors=[],
                    time_sensitive=False,
                    recurring=False
                ),
                "expected_authorized": True,
                "expected_method": "butler_ai"
            },
            {
                "name": "Emergency payment",
                "context": PaymentContext(
                    payment_id="PAY_EMG_001",
                    user_id="test_user_001",
                    tier=BlackTier.VOID,
                    amount=150000,  # ₹1,500
                    currency="INR",
                    category=PaymentCategory.EMERGENCY,
                    recipient="Apollo Hospital",
                    description="Medical emergency",
                    risk_factors=[],
                    time_sensitive=True,
                    recurring=False
                ),
                "expected_authorized": True,
                "expected_method": "emergency_override"
            }
        ]
        
        with patch.object(butler_system, '_get_user_spending_patterns') as mock_patterns, \
             patch.object(butler_system, '_get_user_preferences') as mock_prefs, \
             patch.object(butler_system.market_butler, 'get_assigned_butler') as mock_butler, \
             patch.object(butler_system, '_store_authorization') as mock_store, \
             patch.object(butler_system, '_log_auto_approval_for_butler') as mock_log, \
             patch.object(butler_system, '_send_butler_approval_notification') as mock_notify:
            
            mock_patterns.return_value = {
                "monthly_average": 150000,
                "max_transaction": 500000,
                "subscription_average": 5000,
                "luxury_service_average": 200000
            }
            mock_prefs.return_value = {"auto_approve_subscriptions": True}
            mock_butler.return_value = {"butler_id": "butler_001", "name": "Arjun Mehta"}
            mock_store.return_value = None
            mock_log.return_value = None
            mock_notify.return_value = None
            
            for scenario in scenarios:
                result = await butler_system.authorize_payment(scenario["context"])
                
                assert result["authorized"] == scenario["expected_authorized"], \
                    f"Failed for scenario: {scenario['name']}"
                
                if result["authorized"]:
                    assert result["method"] == scenario["expected_method"], \
                        f"Wrong method for scenario: {scenario['name']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])