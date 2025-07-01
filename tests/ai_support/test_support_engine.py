"""
TradeMate AI Support Engine Test Suite
Comprehensive testing for the brilliant AI support system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json

from app.ai_support.support_engine import TradeMateAISupportEngine
from app.ai_support.models import SupportMessage, SupportTier, UserContext, MessageType, SupportResponse
from app.ai_support.universal_engine import UniversalAISupport
from app.ai_support.tier_ux import TierUXRenderer
from app.ai_support.escalation_system import EscalationReason
from app.ai_support.performance_monitor import MetricType


class TestTradeMateAISupportEngine:
    """Test suite for the main AI Support Engine"""
    
    @pytest.fixture
    async def support_engine(self):
        """Initialize AI support engine for testing"""
        engine = TradeMateAISupportEngine()
        await engine.start()
        return engine
    
    @pytest.fixture
    def black_tier_user_context(self):
        """Create Black tier user context for testing"""
        return UserContext(
            user_id="test_black_user_001",
            tier=SupportTier.BLACK,
            name="Mukesh Ambani",
            portfolio_value=500000000000,  # ₹500 Cr
            recent_orders=[
                {"id": "TM_12345", "symbol": "RELIANCE", "quantity": 10000, "status": "executed"},
                {"id": "TM_12346", "symbol": "TCS", "quantity": 5000, "status": "pending"}
            ],
            balance=50000000000,  # ₹50 Cr
            kyc_status="ultra_premium_verified",
            preferred_language="en",
            trading_history={"total_trades": 2500, "success_rate": 99.8},
            risk_profile="ultra_aggressive"
        )
    
    @pytest.fixture
    def elite_tier_user_context(self):
        """Create Elite tier user context for testing"""
        return UserContext(
            user_id="test_elite_user_001",
            tier=SupportTier.ELITE,
            name="Gautam Adani",
            portfolio_value=15000000000,  # ₹150 Cr
            recent_orders=[
                {"id": "TM_12347", "symbol": "ADANIPORTS", "quantity": 1000, "status": "executed"}
            ],
            balance=2000000000,  # ₹20 Cr
            kyc_status="premium_verified",
            preferred_language="en",
            trading_history={"total_trades": 800, "success_rate": 99.2},
            risk_profile="aggressive"
        )
    
    @pytest.fixture
    def pro_tier_user_context(self):
        """Create Pro tier user context for testing"""
        return UserContext(
            user_id="test_pro_user_001",
            tier=SupportTier.PRO,
            name="Ravi Sharma",
            portfolio_value=5000000,  # ₹50 L
            recent_orders=[
                {"id": "TM_12348", "symbol": "HDFC", "quantity": 100, "status": "failed"}
            ],
            balance=1000000,  # ₹10 L
            kyc_status="verified",
            preferred_language="hi",
            trading_history={"total_trades": 150, "success_rate": 95},
            risk_profile="moderate"
        )
    
    @pytest.fixture
    def lite_tier_user_context(self):
        """Create Lite tier user context for testing"""
        return UserContext(
            user_id="test_lite_user_001",
            tier=SupportTier.LITE,
            name="Anjali Singh",
            portfolio_value=50000,  # ₹50K
            recent_orders=[
                {"id": "TM_12349", "symbol": "SBI", "quantity": 10, "status": "pending"}
            ],
            balance=25000,  # ₹25K
            kyc_status="basic_verified",
            preferred_language="hi",
            trading_history={"total_trades": 15, "success_rate": 87},
            risk_profile="conservative"
        )
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, support_engine):
        """Test AI support engine initializes correctly"""
        assert support_engine.is_running is True
        assert support_engine.ai_engine is not None
        assert support_engine.ux_renderer is not None
        assert support_engine.whatsapp_handler is not None
        assert support_engine.escalation_system is not None
        assert support_engine.zk_integration is not None
        assert support_engine.performance_monitor is not None
    
    @pytest.mark.asyncio
    async def test_black_tier_support_processing(self, support_engine, black_tier_user_context):
        """Test Black tier support message processing with ultra-premium treatment"""
        # Mock user context retrieval
        with patch.object(support_engine, '_get_user_context', return_value=black_tier_user_context):
            # Mock AI response
            ai_response = SupportResponse(
                message="Your ₹38.5 Cr RELIANCE order has been prioritized. Our billionaire desk is handling this personally.",
                confidence=0.98,
                escalate=False,
                category="trading_execution",
                suggested_actions=["contact_billionaire_desk", "priority_execution"],
                response_time=0.8
            )
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                result = await support_engine.process_support_message(
                    phone="+919876540001",
                    message_text="My 10,000 RELIANCE shares order worth ₹38.5 crores is stuck",
                    language="en"
                )
        
        assert result["success"] is True
        assert "billionaire" in result["message"].lower() or "priority" in result["message"].lower()
        assert result["performance"]["tier"] == "BLACK"
        assert result["performance"]["processing_time_ms"] < 5000  # <5s for Black tier
        assert result["zk_proof"]["proof_generated"] is True
        assert result["performance"]["escalated"] is False
    
    @pytest.mark.asyncio
    async def test_elite_tier_support_processing(self, support_engine, elite_tier_user_context):
        """Test Elite tier support with executive treatment"""
        with patch.object(support_engine, '_get_user_context', return_value=elite_tier_user_context):
            ai_response = SupportResponse(
                message="Your ADANIPORTS position has been analyzed. Executive summary attached.",
                confidence=0.95,
                escalate=False,
                category="portfolio_analysis",
                suggested_actions=["executive_brief", "portfolio_rebalance"],
                response_time=1.2
            )
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                result = await support_engine.process_support_message(
                    phone="+919876540002",
                    message_text="Need executive analysis of my ADANIPORTS position performance",
                    language="en"
                )
        
        assert result["success"] is True
        assert result["performance"]["tier"] == "ELITE"
        assert result["performance"]["processing_time_ms"] < 10000  # <10s for Elite tier
        assert "executive" in result["message"].lower() or "analysis" in result["message"].lower()
        assert result["zk_proof"]["proof_generated"] is True
    
    @pytest.mark.asyncio
    async def test_pro_tier_multilingual_support(self, support_engine, pro_tier_user_context):
        """Test Pro tier support with Hindi language processing"""
        with patch.object(support_engine, '_get_user_context', return_value=pro_tier_user_context):
            ai_response = SupportResponse(
                message="आपका HDFC ऑर्डर technical issue के कारण fail हुआ है। हम इसे तुरंत resolve कर रहे हैं।",
                confidence=0.92,
                escalate=False,
                category="order_failure",
                suggested_actions=["retry_order", "technical_support"],
                response_time=2.1
            )
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                result = await support_engine.process_support_message(
                    phone="+919876540003",
                    message_text="Mera HDFC order fail kyun hua? Paisa stuck hai",
                    language="hi"
                )
        
        assert result["success"] is True
        assert result["performance"]["tier"] == "PRO"
        assert result["performance"]["processing_time_ms"] < 15000  # <15s for Pro tier
        # Should contain Hindi text or be professionally formatted
        assert any(char in result["message"] for char in "आएईओउ") or "HDFC" in result["message"]
    
    @pytest.mark.asyncio
    async def test_lite_tier_basic_support(self, support_engine, lite_tier_user_context):
        """Test Lite tier support with basic treatment"""
        with patch.object(support_engine, '_get_user_context', return_value=lite_tier_user_context):
            ai_response = SupportResponse(
                message="आपका SBI order pending है। कुछ देर में process हो जाएगा। 😊",
                confidence=0.88,
                escalate=False,
                category="order_status",
                suggested_actions=["wait", "check_status_later"],
                response_time=3.5
            )
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                result = await support_engine.process_support_message(
                    phone="+919876540004",
                    message_text="SBI order kya hua? Status check karna hai",
                    language="hi"
                )
        
        assert result["success"] is True
        assert result["performance"]["tier"] == "LITE"
        assert result["performance"]["processing_time_ms"] < 30000  # <30s for Lite tier
        assert "SBI" in result["message"]
    
    @pytest.mark.asyncio
    async def test_escalation_trigger_low_confidence(self, support_engine, black_tier_user_context):
        """Test escalation when AI confidence is low"""
        with patch.object(support_engine, '_get_user_context', return_value=black_tier_user_context):
            # Low confidence AI response
            ai_response = SupportResponse(
                message="I'm not entirely sure about this complex derivatives query.",
                confidence=0.45,  # Low confidence triggers escalation
                escalate=True,
                category="complex_derivatives",
                suggested_actions=["human_escalation"],
                response_time=1.8
            )
            
            # Mock escalation system
            escalation_result = {
                "escalated": True,
                "estimated_response": "Expert will respond within 1 minute",
                "agent_assigned": "derivatives_specialist_001"
            }
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                with patch.object(support_engine.escalation_system, 'escalate_to_human', return_value=escalation_result):
                    result = await support_engine.process_support_message(
                        phone="+919876540001",
                        message_text="Complex derivatives arbitrage strategy for multi-leg options spread",
                        language="en"
                    )
        
        assert result["success"] is True
        assert result["performance"]["escalated"] is True
        assert "connecting" in result["message"].lower() or "support team" in result["message"].lower()
        assert result["performance"]["confidence"] == 0.45
    
    @pytest.mark.asyncio
    async def test_urgent_message_priority_boost(self, support_engine, elite_tier_user_context):
        """Test priority boost for urgent keywords"""
        # Test priority calculation
        urgent_message = "URGENT: Money stuck in failed transaction, need immediate help!"
        priority = await support_engine._calculate_priority(urgent_message, SupportTier.ELITE)
        
        normal_message = "Can you help me check my portfolio balance?"
        normal_priority = await support_engine._calculate_priority(normal_message, SupportTier.ELITE)
        
        assert priority > normal_priority
        assert priority == 5  # Max priority due to urgent keywords
    
    @pytest.mark.asyncio
    async def test_zk_proof_generation(self, support_engine, black_tier_user_context):
        """Test zero-knowledge proof generation for transparency"""
        with patch.object(support_engine, '_get_user_context', return_value=black_tier_user_context):
            ai_response = SupportResponse(
                message="Your support query has been resolved successfully.",
                confidence=0.96,
                escalate=False,
                category="general_support",
                suggested_actions=["mark_resolved"],
                response_time=1.1
            )
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                result = await support_engine.process_support_message(
                    phone="+919876540001",
                    message_text="Test support query for ZK proof generation",
                    language="en"
                )
        
        assert result["success"] is True
        assert "zk_proof" in result
        assert result["zk_proof"]["proof_generated"] is True
        assert "proof_id" in result["zk_proof"]
        assert "verification_url" in result["zk_proof"]
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, support_engine, pro_tier_user_context):
        """Test performance metrics collection"""
        with patch.object(support_engine, '_get_user_context', return_value=pro_tier_user_context):
            ai_response = SupportResponse(
                message="Performance monitoring test response",
                confidence=0.93,
                escalate=False,
                category="test",
                suggested_actions=["test_action"],
                response_time=2.3
            )
            
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                # Mock performance monitor
                with patch.object(support_engine.performance_monitor, 'record_metric') as mock_record:
                    result = await support_engine.process_support_message(
                        phone="+919876540003",
                        message_text="Test performance monitoring",
                        language="hi"
                    )
                    
                    # Verify performance metric was recorded
                    mock_record.assert_called_once()
                    call_args = mock_record.call_args
                    assert call_args[0][0] == MetricType.RESPONSE_TIME
                    assert call_args[0][1] == SupportTier.PRO
                    assert isinstance(call_args[0][2], float)  # processing time
    
    @pytest.mark.asyncio
    async def test_error_handling_user_not_found(self, support_engine):
        """Test error handling when user is not found"""
        with patch.object(support_engine, '_get_user_context', return_value=None):
            result = await support_engine.process_support_message(
                phone="+919999999999",
                message_text="Help me with my account",
                language="en"
            )
        
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "User not found"
        assert result["escalated"] is True
    
    @pytest.mark.asyncio
    async def test_performance_dashboard_retrieval(self, support_engine):
        """Test performance dashboard data retrieval"""
        # Mock dashboard data
        dashboard_data = {
            "sla_status": {
                "black": {"response_time": {"current": "2.1s", "status": "healthy"}},
                "elite": {"response_time": {"current": "8.3s", "status": "healthy"}},
                "pro": {"response_time": {"current": "12.7s", "status": "healthy"}},
                "lite": {"response_time": {"current": "28.1s", "status": "healthy"}}
            },
            "system_health": {"system_status": "operational"}
        }
        
        with patch.object(support_engine.performance_monitor, 'get_performance_dashboard', return_value=dashboard_data):
            dashboard = await support_engine.get_performance_dashboard()
        
        assert "sla_status" in dashboard
        assert "black" in dashboard["sla_status"]
        assert dashboard["system_health"]["system_status"] == "operational"
    
    @pytest.mark.asyncio
    async def test_zk_proof_verification(self, support_engine):
        """Test zero-knowledge proof verification"""
        proof_id = "TM_PROOF_12345"
        user_data = {"user_id": "test_user_001"}
        
        verification_result = {
            "valid": True,
            "proof_id": proof_id,
            "verification_timestamp": datetime.utcnow().isoformat(),
            "integrity_check": "passed"
        }
        
        with patch.object(support_engine.zk_integration, 'verify_support_claim', return_value=verification_result):
            result = await support_engine.verify_support_proof(proof_id, user_data)
        
        assert result["valid"] is True
        assert result["proof_id"] == proof_id
        assert "verification_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_tier_specific_response_times(self, support_engine):
        """Test tier-specific response time requirements"""
        test_cases = [
            (SupportTier.BLACK, 5000),   # <5s
            (SupportTier.ELITE, 10000),  # <10s
            (SupportTier.PRO, 15000),    # <15s
            (SupportTier.LITE, 30000)    # <30s
        ]
        
        for tier, max_time_ms in test_cases:
            # Create user context for tier
            user_context = UserContext(
                user_id=f"test_{tier.value}_user",
                tier=tier,
                name="Test User",
                portfolio_value=1000000,
                recent_orders=[],
                balance=100000,
                kyc_status="verified",
                preferred_language="en",
                trading_history={"total_trades": 100, "success_rate": 95},
                risk_profile="moderate"
            )
            
            with patch.object(support_engine, '_get_user_context', return_value=user_context):
                ai_response = SupportResponse(
                    message=f"Test response for {tier.value} tier",
                    confidence=0.95,
                    escalate=False,
                    category="test",
                    suggested_actions=["test"],
                    response_time=1.0
                )
                
                with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                    start_time = asyncio.get_event_loop().time()
                    
                    result = await support_engine.process_support_message(
                        phone=f"+91987654000{tier.value[0]}",
                        message_text=f"Test message for {tier.value} tier",
                        language="en"
                    )
                    
                    processing_time = result["performance"]["processing_time_ms"]
                    
                    # Verify response time meets tier SLA
                    assert processing_time < max_time_ms, f"{tier.value} tier exceeded SLA: {processing_time}ms > {max_time_ms}ms"
    
    @pytest.mark.asyncio
    async def test_multilingual_support_coverage(self, support_engine, pro_tier_user_context):
        """Test support for multiple Indian languages"""
        test_languages = [
            ("hi", "Hindi"),
            ("ta", "Tamil"),
            ("te", "Telugu"),
            ("bn", "Bengali"),
            ("gu", "Gujarati"),
            ("kn", "Kannada"),
            ("ml", "Malayalam"),
            ("mr", "Marathi"),
            ("pa", "Punjabi"),
            ("or", "Odia"),
            ("as", "Assamese")
        ]
        
        for lang_code, lang_name in test_languages:
            with patch.object(support_engine, '_get_user_context', return_value=pro_tier_user_context):
                ai_response = SupportResponse(
                    message=f"Response in {lang_name} language",
                    confidence=0.90,
                    escalate=False,
                    category="multilingual_test",
                    suggested_actions=["test"],
                    response_time=2.0
                )
                
                with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                    result = await support_engine.process_support_message(
                        phone="+919876540003",
                        message_text=f"Test message in {lang_name}",
                        language=lang_code
                    )
                
                assert result["success"] is True, f"Failed for language: {lang_name}"
                assert lang_name in result["message"] or "test" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_support_requests(self, support_engine):
        """Test handling multiple concurrent support requests"""
        # Create multiple user contexts
        user_contexts = [
            UserContext(
                user_id=f"concurrent_user_{i}",
                tier=SupportTier.PRO,
                name=f"User {i}",
                portfolio_value=1000000,
                recent_orders=[],
                balance=100000,
                kyc_status="verified",
                preferred_language="en",
                trading_history={"total_trades": 50, "success_rate": 95},
                risk_profile="moderate"
            ) for i in range(5)
        ]
        
        # Mock responses for concurrent requests
        async def mock_get_user_context(phone):
            user_index = int(phone[-1]) % 5
            return user_contexts[user_index]
        
        ai_response = SupportResponse(
            message="Concurrent request processed successfully",
            confidence=0.94,
            escalate=False,
            category="concurrent_test",
            suggested_actions=["test"],
            response_time=1.5
        )
        
        with patch.object(support_engine, '_get_user_context', side_effect=mock_get_user_context):
            with patch.object(support_engine.ai_engine, 'process_support_request', return_value=ai_response):
                # Launch 5 concurrent requests
                tasks = [
                    support_engine.process_support_message(
                        phone=f"+91987654000{i}",
                        message_text=f"Concurrent test message {i}",
                        language="en"
                    ) for i in range(5)
                ]
                
                results = await asyncio.gather(*tasks)
                
                # Verify all requests succeeded
                for i, result in enumerate(results):
                    assert result["success"] is True, f"Concurrent request {i} failed"
                    assert result["performance"]["tier"] == "PRO"


class TestAISupportSystemIntegration:
    """Integration tests for the complete AI support system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_support_flow(self):
        """Test complete end-to-end support flow"""
        # This would test the complete flow from WhatsApp message
        # through AI processing to final response
        pass
    
    @pytest.mark.asyncio
    async def test_black_tier_emergency_escalation(self):
        """Test emergency escalation for Black tier users"""
        # Test immediate escalation for emergency keywords
        pass
    
    @pytest.mark.asyncio
    async def test_ai_support_business_metrics(self):
        """Test business impact metrics of AI support system"""
        # Test cost savings, response time improvements, etc.
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])