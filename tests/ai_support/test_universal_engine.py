"""
TradeMate Universal AI Support Engine Test Suite
Testing the brilliant GPT-4 powered universal support AI
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.ai_support.universal_engine import UniversalAISupport, SupportCategory
from app.ai_support.models import SupportMessage, SupportTier, UserContext, MessageType, SupportResponse


class TestUniversalAISupport:
    """Test suite for Universal AI Support Engine"""
    
    @pytest.fixture
    async def ai_engine(self):
        """Initialize Universal AI Support engine"""
        engine = UniversalAISupport()
        return engine
    
    @pytest.fixture
    def sample_support_message(self):
        """Create sample support message for testing"""
        return SupportMessage(
            id="TM_MSG_001",
            user_id="test_user_001",
            phone="+919876543210",
            message="My order is stuck and I can't see my money",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.PRO,
            priority=4
        )
    
    @pytest.fixture
    def sample_user_context(self):
        """Create sample user context"""
        return UserContext(
            user_id="test_user_001",
            tier=SupportTier.PRO,
            name="Rajesh Kumar",
            portfolio_value=2000000,
            recent_orders=[
                {"id": "ORDER_001", "symbol": "TCS", "quantity": 50, "status": "pending"},
                {"id": "ORDER_002", "symbol": "INFY", "quantity": 25, "status": "completed"}
            ],
            balance=150000,
            kyc_status="verified",
            preferred_language="en",
            trading_history={"total_trades": 125, "success_rate": 96},
            risk_profile="moderate"
        )
    
    @pytest.mark.asyncio
    async def test_ai_engine_initialization(self, ai_engine):
        """Test AI engine initializes correctly"""
        assert ai_engine.model_name == "gpt-4"
        assert ai_engine.max_tokens == 300
        assert ai_engine.temperature == 0.3
        assert len(ai_engine.supported_languages) == 11  # 11 Indian languages
        assert "en" in ai_engine.supported_languages
        assert "hi" in ai_engine.supported_languages
    
    @pytest.mark.asyncio
    async def test_support_request_processing(self, ai_engine, sample_support_message, sample_user_context):
        """Test basic support request processing"""
        # Mock OpenAI response
        mock_openai_response = {
            "choices": [{
                "message": {
                    "content": "I understand your TCS order is pending. Let me check the status and help resolve this immediately. Your ₹1,92,500 investment is safe and will be processed within 2 minutes."
                }
            }],
            "usage": {"total_tokens": 85}
        }
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_openai_response):
            response = await ai_engine.process_support_request(sample_support_message, sample_user_context)
        
        assert isinstance(response, SupportResponse)
        assert "TCS" in response.message
        assert response.confidence > 0.8
        assert response.escalate is False
        assert response.category in [cat.value for cat in SupportCategory]
    
    @pytest.mark.asyncio
    async def test_query_classification_order_management(self, ai_engine):
        """Test classification of order management queries"""
        order_queries = [
            "My TCS order is stuck",
            "Order failed for RELIANCE shares",
            "Cancel my pending HDFC order",
            "Why is my SBI order taking so long?",
            "Order status check karna hai"
        ]
        
        for query in order_queries:
            classification = await ai_engine._classify_query(query, "en")
            assert classification["category"] == SupportCategory.ORDER_MANAGEMENT.value
            assert classification["urgency"] in ["low", "medium", "high"]
            assert "intent" in classification
    
    @pytest.mark.asyncio
    async def test_query_classification_portfolio_queries(self, ai_engine):
        """Test classification of portfolio-related queries"""
        portfolio_queries = [
            "What's my portfolio performance?",
            "Show me my holdings",
            "Portfolio balance check karna hai",
            "Investment summary chahiye",
            "My mutual fund returns"
        ]
        
        for query in portfolio_queries:
            classification = await ai_engine._classify_query(query, "en")
            assert classification["category"] == SupportCategory.PORTFOLIO_QUERIES.value
    
    @pytest.mark.asyncio
    async def test_query_classification_payment_issues(self, ai_engine):
        """Test classification of payment-related issues"""
        payment_queries = [
            "Money not credited to my account",
            "Payment failed for order",
            "Bank account se paisa nahi gaya",
            "UPI transaction stuck",
            "Refund kab milega?"
        ]
        
        for query in payment_queries:
            classification = await ai_engine._classify_query(query, "en")
            assert classification["category"] == SupportCategory.PAYMENT_ISSUES.value
            # Payment issues should typically be high urgency
            assert classification["urgency"] in ["medium", "high"]
    
    @pytest.mark.asyncio
    async def test_multilingual_support_hindi(self, ai_engine, sample_user_context):
        """Test Hindi language support"""
        hindi_message = SupportMessage(
            id="TM_MSG_HI_001",
            user_id="test_user_hindi",
            phone="+919876543210",
            message="Mera HDFC order fail kyun hua? Paisa kahan gaya?",
            message_type=MessageType.TEXT,
            language="hi",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.PRO,
            priority=4
        )
        
        mock_openai_response = {
            "choices": [{
                "message": {
                    "content": "मैं आपकी HDFC order की जांच कर रहा हूं। आपका पैसा सुरक्षित है और technical issue के कारण order fail हुआ है। 5 मिनट में refund process हो जाएगा।"
                }
            }],
            "usage": {"total_tokens": 92}
        }
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_openai_response):
            response = await ai_engine.process_support_request(hindi_message, sample_user_context)
        
        assert isinstance(response, SupportResponse)
        assert "HDFC" in response.message
        # Response should contain Hindi text
        assert any(char in response.message for char in "आएईओउ")
    
    @pytest.mark.asyncio
    async def test_escalation_trigger_low_confidence(self, ai_engine, sample_support_message, sample_user_context):
        """Test escalation when AI confidence is low"""
        # Mock OpenAI response with uncertain language
        mock_openai_response = {
            "choices": [{
                "message": {
                    "content": "I'm not entirely sure about this complex derivatives issue. This might require specialized assistance."
                }
            }],
            "usage": {"total_tokens": 45}
        }
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_openai_response):
            response = await ai_engine.process_support_request(sample_support_message, sample_user_context)
        
        # Low confidence should trigger escalation
        assert response.escalate is True
        assert response.confidence < 0.7
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, ai_engine):
        """Test AI confidence calculation based on response"""
        test_cases = [
            ("I have resolved your order issue completely.", 0.95),
            ("Your order should be processed soon.", 0.75),
            ("I'm not sure about this complex issue.", 0.4),
            ("This requires specialized help from our team.", 0.3)
        ]
        
        for ai_response, expected_confidence in test_cases:
            confidence = ai_engine._calculate_confidence(ai_response)
            assert abs(confidence - expected_confidence) < 0.15  # Allow some tolerance
    
    @pytest.mark.asyncio
    async def test_context_enrichment_order_details(self, ai_engine, sample_user_context):
        """Test context enrichment with user's order details"""
        support_message = SupportMessage(
            id="TM_MSG_002",
            user_id="test_user_001",
            phone="+919876543210",
            message="Check my TCS order status",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.PRO,
            priority=3
        )
        
        enriched_context = await ai_engine._enrich_context_with_user_data(support_message, sample_user_context)
        
        assert "TCS" in enriched_context
        assert "50 shares" in enriched_context  # From user's recent orders
        assert "pending" in enriched_context
        assert "ORDER_001" in enriched_context
    
    @pytest.mark.asyncio
    async def test_sebi_compliance_validation(self, ai_engine):
        """Test SEBI compliance validation in responses"""
        test_responses = [
            ("Buy this stock, guaranteed 50% returns!", False),  # Investment advice
            ("Your order status is pending.", True),  # Factual info
            ("This stock will definitely go up!", False),  # Market prediction
            ("I can help you check your portfolio balance.", True)  # Service info
        ]
        
        for response_text, should_be_compliant in test_responses:
            is_compliant = ai_engine._validate_sebi_compliance(response_text)
            assert is_compliant == should_be_compliant
    
    @pytest.mark.asyncio
    async def test_response_time_optimization(self, ai_engine, sample_support_message, sample_user_context):
        """Test response time optimization for different tiers"""
        # Mock faster response for higher tiers
        mock_openai_response = {
            "choices": [{
                "message": {
                    "content": "Quick response for tier-optimized processing."
                }
            }],
            "usage": {"total_tokens": 25}
        }
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_openai_response):
            start_time = asyncio.get_event_loop().time()
            response = await ai_engine.process_support_request(sample_support_message, sample_user_context)
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Should be fast for AI processing
            assert processing_time < 3.0  # Less than 3 seconds
            assert response.response_time < 3.0
    
    @pytest.mark.asyncio
    async def test_error_handling_openai_failure(self, ai_engine, sample_support_message, sample_user_context):
        """Test error handling when OpenAI API fails"""
        with patch('openai.ChatCompletion.acreate', side_effect=Exception("OpenAI API Error")):
            response = await ai_engine.process_support_request(sample_support_message, sample_user_context)
        
        # Should gracefully handle failure
        assert response.escalate is True
        assert "technical difficulties" in response.message.lower()
        assert response.confidence < 0.5
    
    @pytest.mark.asyncio
    async def test_suggested_actions_generation(self, ai_engine, sample_support_message, sample_user_context):
        """Test generation of suggested actions"""
        mock_openai_response = {
            "choices": [{
                "message": {
                    "content": "Your order is pending. I'll check the status and provide an update."
                }
            }],
            "usage": {"total_tokens": 55}
        }
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_openai_response):
            response = await ai_engine.process_support_request(sample_support_message, sample_user_context)
        
        assert len(response.suggested_actions) > 0
        assert any("check" in action.lower() for action in response.suggested_actions)
    
    @pytest.mark.asyncio
    async def test_language_detection_and_caching(self, ai_engine):
        """Test automatic language detection and caching"""
        test_messages = [
            ("My order is stuck", "en"),
            ("Mera order stuck hai", "hi"),
            ("என் ஆர்டர் நிலுவையில் உள்ளது", "ta"),
            ("నా ఆర్డర్ స్టక్ అయ్యింది", "te")
        ]
        
        for message, expected_lang in test_messages:
            detected_lang = await ai_engine._detect_language(message)
            assert detected_lang == expected_lang
    
    @pytest.mark.asyncio
    async def test_learning_from_interactions(self, ai_engine):
        """Test that AI learns from user interactions"""
        # This would test the learning mechanism
        # Currently mock implementation
        interaction_data = {
            "user_satisfaction": 0.95,
            "resolution_successful": True,
            "category": "order_management",
            "response_time": 2.1
        }
        
        learning_result = await ai_engine._learn_from_interaction(interaction_data)
        assert learning_result["learning_applied"] is True
    
    @pytest.mark.asyncio
    async def test_tier_specific_knowledge_base(self, ai_engine):
        """Test tier-specific knowledge base access"""
        black_tier_context = UserContext(
            user_id="black_user_001",
            tier=SupportTier.BLACK,
            name="Ultra Premium User",
            portfolio_value=500000000,
            recent_orders=[],
            balance=50000000,
            kyc_status="ultra_premium",
            preferred_language="en",
            trading_history={"total_trades": 5000, "success_rate": 99.5},
            risk_profile="ultra_aggressive"
        )
        
        knowledge = await ai_engine._get_tier_specific_knowledge(black_tier_context.tier)
        
        assert "concierge" in knowledge.lower()
        assert "exclusive" in knowledge.lower() or "premium" in knowledge.lower()
        assert len(knowledge) > 100  # Should have substantial tier-specific info


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])