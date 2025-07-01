"""
GridWorks B2B Services - AI Suite Unit Tests
Comprehensive test coverage for AI Suite services
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json
from typing import Dict, Any

from ...ai_suite.support_engine import SupportEngine, SupportRequest, SupportResponse
from ...ai_suite.intelligence_engine import IntelligenceEngine, IntelligenceRequest, IntelligenceResponse
from ...ai_suite.moderator_engine import ModerationEngine, ModerationRequest, ModerationResponse
from ...config import settings


class TestSupportEngine:
    """Test suite for AI Support Engine."""
    
    @pytest_asyncio.fixture
    async def support_engine(self, mock_redis):
        """Create SupportEngine instance with mocked dependencies."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            with patch('anthropic.AsyncAnthropic') as mock_anthropic:
                mock_openai_client = AsyncMock()
                mock_anthropic_client = AsyncMock()
                mock_openai.return_value = mock_openai_client
                mock_anthropic.return_value = mock_anthropic_client
                
                engine = SupportEngine()
                engine.redis_client = mock_redis
                engine.openai_client = mock_openai_client
                engine.anthropic_client = mock_anthropic_client
                
                return engine
    
    @pytest_asyncio.fixture
    async def sample_support_request(self):
        """Sample support request for testing."""
        return SupportRequest(
            user_message="What is NIFTY 50 and how does it work?",
            language="en",
            user_context={
                "user_id": "test_user_123",
                "client_id": "test_client_456",
                "tier": "enterprise",
                "preferences": {"complexity": "advanced", "format": "detailed"}
            },
            conversation_history=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ],
            channel="whatsapp",
            audio_format="mp3"
        )
    
    async def test_support_request_processing_success(self, support_engine, sample_support_request, test_db_session):
        """Test successful support request processing."""
        # Mock OpenAI response
        mock_openai_response = MagicMock()
        mock_openai_response.choices = [MagicMock()]
        mock_openai_response.choices[0].message.content = "NIFTY 50 is India's premier stock market index..."
        mock_openai_response.usage.total_tokens = 150
        
        support_engine.openai_client.chat.completions.create.return_value = mock_openai_response
        
        # Mock text-to-speech
        mock_audio_response = b"fake_audio_data"
        support_engine.openai_client.audio.speech.create.return_value = AsyncMock()
        support_engine.openai_client.audio.speech.create.return_value.content = mock_audio_response
        
        # Process request
        response = await support_engine.process_support_request(sample_support_request, test_db_session)
        
        # Verify response
        assert isinstance(response, SupportResponse)
        assert response.response_text == "NIFTY 50 is India's premier stock market index..."
        assert response.language == "en"
        assert response.confidence_score >= 0.8
        assert response.response_time_ms > 0
        assert response.model_used == "gpt-4-turbo"
        assert response.response_audio is not None
        assert len(response.follow_up_suggestions) >= 2
    
    async def test_multi_language_support(self, support_engine, test_db_session):
        """Test multi-language support functionality."""
        # Test different languages
        languages = ["hi", "ta", "te", "mr", "gu", "bn", "kn", "ml", "pa", "or", "as"]
        
        for lang in languages:
            request = SupportRequest(
                user_message="What is stock market?",
                language=lang,
                user_context={"user_id": "test", "client_id": "test", "tier": "growth"},
                conversation_history=[],
                channel="api"
            )
            
            # Mock response for each language
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = f"Stock market explanation in {lang}"
            mock_response.usage.total_tokens = 100
            
            support_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await support_engine.process_support_request(request, test_db_session)
            
            assert response.language == lang
            assert response.response_text == f"Stock market explanation in {lang}"
    
    async def test_financial_domain_expertise(self, support_engine, test_db_session):
        """Test financial domain expertise validation."""
        financial_queries = [
            "Explain derivative trading",
            "What is P/E ratio?",
            "How does FII impact markets?",
            "Explain mutual fund NAV",
            "What are IPO regulations?"
        ]
        
        for query in financial_queries:
            request = SupportRequest(
                user_message=query,
                language="en",
                user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
                conversation_history=[],
                channel="api"
            )
            
            # Mock financial expertise response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = f"Expert financial explanation for: {query}"
            mock_response.usage.total_tokens = 200
            
            support_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await support_engine.process_support_request(request, test_db_session)
            
            # Financial queries should have high confidence
            assert response.confidence_score >= 0.9
            assert "expert" in response.response_text.lower() or "financial" in response.response_text.lower()
    
    async def test_tier_based_response_quality(self, support_engine, test_db_session):
        """Test tier-based response quality differentiation."""
        query = "Explain options trading"
        
        # Test different tiers
        tiers = ["growth", "enterprise", "quantum"]
        
        for tier in tiers:
            request = SupportRequest(
                user_message=query,
                language="en",
                user_context={"user_id": "test", "client_id": "test", "tier": tier},
                conversation_history=[],
                channel="api"
            )
            
            # Mock tier-specific response
            response_quality = {"growth": "basic", "enterprise": "detailed", "quantum": "comprehensive"}
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = f"{response_quality[tier]} explanation of options trading"
            mock_response.usage.total_tokens = {"growth": 100, "enterprise": 200, "quantum": 300}[tier]
            
            support_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await support_engine.process_support_request(request, test_db_session)
            
            assert response_quality[tier] in response.response_text
            
            # Higher tiers should get more comprehensive responses
            if tier == "quantum":
                assert len(response.follow_up_suggestions) >= 5
            elif tier == "enterprise":
                assert len(response.follow_up_suggestions) >= 3
    
    async def test_conversation_context_handling(self, support_engine, test_db_session):
        """Test conversation context and memory handling."""
        # Build conversation history
        conversation_history = [
            {"role": "user", "content": "What is NIFTY?"},
            {"role": "assistant", "content": "NIFTY is India's stock market index..."},
            {"role": "user", "content": "How is it calculated?"},
            {"role": "assistant", "content": "NIFTY is calculated using free-float market cap..."}
        ]
        
        request = SupportRequest(
            user_message="What are the top companies in it?",
            language="en",
            user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
            conversation_history=conversation_history,
            channel="api"
        )
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Top NIFTY companies include Reliance, TCS, HDFC Bank..."
        mock_response.usage.total_tokens = 180
        
        support_engine.openai_client.chat.completions.create.return_value = mock_response
        
        response = await support_engine.process_support_request(request, test_db_session)
        
        # Should understand context and provide relevant answer about NIFTY companies
        assert "reliance" in response.response_text.lower() or "tcs" in response.response_text.lower()
        assert response.confidence_score >= 0.85
    
    async def test_rate_limiting_and_caching(self, support_engine, test_db_session):
        """Test rate limiting and response caching."""
        request = SupportRequest(
            user_message="What is equity?",
            language="en",
            user_context={"user_id": "test_user", "client_id": "test_client", "tier": "growth"},
            conversation_history=[],
            channel="api"
        )
        
        # Mock cached response
        cached_response = {
            "response_text": "Cached: Equity represents ownership in a company...",
            "confidence_score": 0.92,
            "model_used": "cached",
            "cached": True
        }
        
        support_engine.redis_client.get.return_value = json.dumps(cached_response)
        
        response = await support_engine.process_support_request(request, test_db_session)
        
        # Should return cached response
        assert "Cached:" in response.response_text
        assert response.model_used == "cached"
        
        # Verify cache key was checked
        expected_cache_key = f"support_cache:test_client:test_user:en:{hash(request.user_message)}"
        support_engine.redis_client.get.assert_called()
    
    async def test_error_handling_and_fallback(self, support_engine, test_db_session):
        """Test error handling and fallback mechanisms."""
        request = SupportRequest(
            user_message="What is cryptocurrency?",
            language="en",
            user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
            conversation_history=[],
            channel="api"
        )
        
        # Mock OpenAI failure
        support_engine.openai_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        
        # Mock Anthropic fallback success
        mock_anthropic_response = MagicMock()
        mock_anthropic_response.content = [MagicMock()]
        mock_anthropic_response.content[0].text = "Fallback: Cryptocurrency is a digital currency..."
        mock_anthropic_response.usage.input_tokens = 50
        mock_anthropic_response.usage.output_tokens = 100
        
        support_engine.anthropic_client.messages.create.return_value = mock_anthropic_response
        
        response = await support_engine.process_support_request(request, test_db_session)
        
        # Should fallback to Anthropic
        assert "Fallback:" in response.response_text
        assert response.model_used == "claude-3-opus"
        assert response.confidence_score >= 0.0  # Should still provide a response
    
    async def test_audio_response_generation(self, support_engine, test_db_session):
        """Test audio response generation for different formats."""
        request = SupportRequest(
            user_message="Explain mutual funds",
            language="en",
            user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
            conversation_history=[],
            channel="whatsapp",
            audio_format="mp3"
        )
        
        # Mock text response
        mock_text_response = MagicMock()
        mock_text_response.choices = [MagicMock()]
        mock_text_response.choices[0].message.content = "Mutual funds are investment vehicles..."
        mock_text_response.usage.total_tokens = 150
        
        support_engine.openai_client.chat.completions.create.return_value = mock_text_response
        
        # Mock audio generation
        mock_audio_data = b"fake_mp3_audio_data"
        mock_audio_response = AsyncMock()
        mock_audio_response.content = mock_audio_data
        
        support_engine.openai_client.audio.speech.create.return_value = mock_audio_response
        
        response = await support_engine.process_support_request(request, test_db_session)
        
        # Should include audio response
        assert response.response_audio is not None
        assert response.response_audio == mock_audio_data
        
        # Verify audio generation was called with correct parameters
        support_engine.openai_client.audio.speech.create.assert_called_once()
        call_args = support_engine.openai_client.audio.speech.create.call_args
        assert call_args[1]["input"] == "Mutual funds are investment vehicles..."
        assert call_args[1]["voice"] == "alloy"
        assert call_args[1]["response_format"] == "mp3"


class TestIntelligenceEngine:
    """Test suite for AI Intelligence Engine."""
    
    @pytest_asyncio.fixture
    async def intelligence_engine(self, mock_redis):
        """Create IntelligenceEngine instance with mocked dependencies."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            with patch('requests.get') as mock_requests:
                mock_openai_client = AsyncMock()
                mock_openai.return_value = mock_openai_client
                
                engine = IntelligenceEngine()
                engine.redis_client = mock_redis
                engine.openai_client = mock_openai_client
                
                return engine
    
    async def test_morning_pulse_generation(self, intelligence_engine, test_db_session):
        """Test morning pulse intelligence generation."""
        request = IntelligenceRequest(
            intelligence_type="morning_pulse",
            market_region="india",
            user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
            custom_parameters={"focus_sectors": ["banking", "it", "pharma"]}
        )
        
        # Mock market data APIs
        mock_market_data = {
            "nifty_50": 21500.0,
            "sensex": 71000.0,
            "bank_nifty": 46500.0,
            "volatility": "moderate",
            "global_cues": {"nasdaq": 15800, "dow": 37000, "us_futures": "positive"}
        }
        
        intelligence_engine.redis_client.get.return_value = json.dumps(mock_market_data)
        
        # Mock AI analysis
        mock_ai_response = MagicMock()
        mock_ai_response.choices = [MagicMock()]
        mock_ai_response.choices[0].message.content = json.dumps({
            "summary": "Markets opened positive with strong global cues. Banking sector shows momentum.",
            "key_insights": [
                "US futures indicate positive opening",
                "Banking stocks outperforming on rate expectations",
                "IT sector mixed on global concerns"
            ],
            "risk_level": "moderate",
            "actionable_recommendations": [
                "Consider banking sector exposure",
                "Monitor IT stock movements"
            ]
        })
        mock_ai_response.usage.total_tokens = 250
        
        intelligence_engine.openai_client.chat.completions.create.return_value = mock_ai_response
        
        response = await intelligence_engine.process_intelligence_request(request, test_db_session)
        
        # Verify response
        assert isinstance(response, IntelligenceResponse)
        assert response.intelligence_type == "morning_pulse"
        assert response.market_region == "india"
        assert "positive" in response.summary.lower()
        assert len(response.key_insights) >= 2
        assert len(response.actionable_recommendations) >= 1
        assert response.risk_level in ["low", "moderate", "high"]
        assert response.confidence_score >= 0.8
    
    async def test_global_correlation_analysis(self, intelligence_engine, test_db_session):
        """Test global market correlation analysis."""
        request = IntelligenceRequest(
            intelligence_type="global_correlation",
            market_region="india",
            user_context={"user_id": "test", "client_id": "test", "tier": "quantum"},
            custom_parameters={
                "correlation_markets": ["nasdaq", "dow", "ftse", "nikkei"],
                "timeframe": "1M",
                "sectors": ["technology", "banking", "energy"]
            }
        )
        
        # Mock correlation data
        mock_correlation_data = {
            "india_nasdaq_correlation": 0.75,
            "india_dow_correlation": 0.68,
            "sector_correlations": {
                "technology": {"nasdaq": 0.85, "dow": 0.70},
                "banking": {"nasdaq": 0.60, "dow": 0.75},
                "energy": {"nasdaq": 0.45, "dow": 0.80}
            },
            "historical_patterns": ["Strong correlation during tech rallies", "Divergence during local events"]
        }
        
        # Mock AI analysis
        mock_ai_response = MagicMock()
        mock_ai_response.choices = [MagicMock()]
        mock_ai_response.choices[0].message.content = json.dumps({
            "summary": "Strong correlation observed between Indian tech and NASDAQ movements",
            "key_insights": [
                "Technology sector shows 85% correlation with NASDAQ",
                "Banking sector more correlated with Dow Jones",
                "Energy sector shows mixed correlation patterns"
            ],
            "correlation_strength": "strong",
            "risk_level": "moderate",
            "actionable_recommendations": [
                "Monitor NASDAQ for tech stock direction",
                "Use Dow for banking sector insights"
            ]
        })
        mock_ai_response.usage.total_tokens = 300
        
        intelligence_engine.openai_client.chat.completions.create.return_value = mock_ai_response
        intelligence_engine.redis_client.get.return_value = json.dumps(mock_correlation_data)
        
        response = await intelligence_engine.process_intelligence_request(request, test_db_session)
        
        assert response.intelligence_type == "global_correlation"
        assert "correlation" in response.summary.lower()
        assert len(response.data_points) > 0
        assert "correlation_strength" in response.supporting_data
    
    async def test_institutional_flow_analysis(self, intelligence_engine, test_db_session):
        """Test institutional money flow analysis."""
        request = IntelligenceRequest(
            intelligence_type="institutional_flow",
            market_region="india",
            user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
            custom_parameters={
                "flow_types": ["fii", "dii", "mutual_funds"],
                "timeframe": "1W"
            }
        )
        
        # Mock institutional flow data
        mock_flow_data = {
            "fii_flows": {"equity": 2500, "debt": 1200, "net": 3700},
            "dii_flows": {"equity": -800, "debt": 500, "net": -300},
            "mutual_fund_flows": {"equity": 1200, "debt": 800, "net": 2000},
            "sector_flows": {
                "banking": 1500,
                "it": 2000,
                "pharma": -500,
                "auto": 300
            }
        }
        
        # Mock AI analysis
        mock_ai_response = MagicMock()
        mock_ai_response.choices = [MagicMock()]
        mock_ai_response.choices[0].message.content = json.dumps({
            "summary": "Strong FII inflows of ₹3700Cr this week, offsetting DII outflows",
            "key_insights": [
                "FII showing confidence in Indian markets",
                "DII booking profits after recent rally",
                "Strong flows into IT and Banking sectors"
            ],
            "flow_sentiment": "positive",
            "risk_level": "low",
            "actionable_recommendations": [
                "FII inflows likely to support market levels",
                "Focus on IT and Banking beneficiaries"
            ]
        })
        mock_ai_response.usage.total_tokens = 280
        
        intelligence_engine.openai_client.chat.completions.create.return_value = mock_ai_response
        intelligence_engine.redis_client.get.return_value = json.dumps(mock_flow_data)
        
        response = await intelligence_engine.process_intelligence_request(request, test_db_session)
        
        assert response.intelligence_type == "institutional_flow"
        assert "fii" in response.summary.lower() or "inflows" in response.summary.lower()
        assert response.risk_level == "low"
        assert "flow_sentiment" in response.supporting_data
    
    async def test_tier_based_intelligence_depth(self, intelligence_engine, test_db_session):
        """Test intelligence depth based on client tier."""
        request_base = {
            "intelligence_type": "morning_pulse",
            "market_region": "india",
            "custom_parameters": {}
        }
        
        tiers = ["growth", "enterprise", "quantum"]
        
        for tier in tiers:
            request = IntelligenceRequest(
                **request_base,
                user_context={"user_id": f"test_{tier}", "client_id": "test", "tier": tier}
            )
            
            # Mock tier-specific response depth
            depth_levels = {
                "growth": {"insights": 2, "recommendations": 1, "data_points": 3},
                "enterprise": {"insights": 4, "recommendations": 3, "data_points": 6},
                "quantum": {"insights": 6, "recommendations": 5, "data_points": 10}
            }
            
            tier_data = depth_levels[tier]
            mock_ai_response = MagicMock()
            mock_ai_response.choices = [MagicMock()]
            mock_ai_response.choices[0].message.content = json.dumps({
                "summary": f"{tier} level market analysis",
                "key_insights": [f"Insight {i+1}" for i in range(tier_data["insights"])],
                "actionable_recommendations": [f"Recommendation {i+1}" for i in range(tier_data["recommendations"])],
                "risk_level": "moderate"
            })
            mock_ai_response.usage.total_tokens = 100 + (50 * (tiers.index(tier) + 1))
            
            intelligence_engine.openai_client.chat.completions.create.return_value = mock_ai_response
            
            response = await intelligence_engine.process_intelligence_request(request, test_db_session)
            
            # Higher tiers should get more detailed analysis
            assert len(response.key_insights) == tier_data["insights"]
            assert len(response.actionable_recommendations) == tier_data["recommendations"]
            assert tier in response.summary


class TestModerationEngine:
    """Test suite for AI Moderator Engine."""
    
    @pytest_asyncio.fixture
    async def moderation_engine(self, mock_redis):
        """Create ModerationEngine instance with mocked dependencies."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_openai_client = AsyncMock()
            mock_openai.return_value = mock_openai_client
            
            engine = ModerationEngine()
            engine.redis_client = mock_redis
            engine.openai_client = mock_openai_client
            
            return engine
    
    async def test_spam_detection_high_accuracy(self, moderation_engine, test_db_session):
        """Test spam detection with high accuracy requirement."""
        spam_contents = [
            "🚀🚀 GUARANTEED RETURNS! Click here for 500% profit in 24 hours! 💰💰",
            "URGENT: Secret stock tip that will make you RICH! WhatsApp: +91XXXXXXXXX",
            "FREE CALLS! Join our premium group for ₹999 only. Limited time offer!!!",
            "INSIDER TRADING TIPS! Bank Nifty calls with 99% accuracy. Join now!",
            "Make ₹50,000 daily with our AI trading bot. No risk, only profits!"
        ]
        
        for spam_content in spam_contents:
            request = ModerationRequest(
                content=spam_content,
                content_type="text",
                user_context={"user_id": "test", "client_id": "test", "tier": "growth"},
                channel="whatsapp",
                metadata={"message_type": "broadcast"}
            )
            
            # Mock spam detection response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "action": "block",
                "confidence_score": 0.98,
                "spam_categories": ["financial_scam", "guaranteed_returns", "suspicious_links"],
                "risk_level": "high",
                "explanation": "Content contains typical spam patterns including guaranteed returns and urgent calls to action",
                "escalation_required": True
            })
            mock_response.usage.total_tokens = 120
            
            moderation_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await moderation_engine.moderate_content(request, test_db_session)
            
            assert isinstance(response, ModerationResponse)
            assert response.action == "block"
            assert response.confidence_score >= 0.95  # High accuracy requirement
            assert len(response.spam_categories) > 0
            assert response.risk_level == "high"
            assert response.escalation_required is True
    
    async def test_legitimate_content_approval(self, moderation_engine, test_db_session):
        """Test legitimate content gets approved."""
        legitimate_contents = [
            "NIFTY closed at 21,450 today, up 0.8% from yesterday's close.",
            "Banking sector analysis: HDFC Bank reported strong Q3 results with 15% YoY growth.",
            "Technical analysis of Reliance shows bullish momentum with RSI at 65.",
            "Market outlook: FII inflows of ₹2,500Cr this week indicate positive sentiment.",
            "Risk management tip: Always maintain stop-loss orders to protect your capital."
        ]
        
        for legitimate_content in legitimate_contents:
            request = ModerationRequest(
                content=legitimate_content,
                content_type="text",
                user_context={"user_id": "expert_user", "client_id": "test", "tier": "enterprise"},
                channel="telegram",
                metadata={"user_reputation": "high", "expert_verified": True}
            )
            
            # Mock legitimate content response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "action": "allow",
                "confidence_score": 0.95,
                "spam_categories": [],
                "risk_level": "low",
                "explanation": "Content appears to be legitimate financial analysis with no spam indicators",
                "escalation_required": False
            })
            mock_response.usage.total_tokens = 100
            
            moderation_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await moderation_engine.moderate_content(request, test_db_session)
            
            assert response.action == "allow"
            assert response.confidence_score >= 0.90
            assert len(response.spam_categories) == 0
            assert response.risk_level == "low"
            assert response.escalation_required is False
    
    async def test_expert_verification_system(self, moderation_engine, test_db_session):
        """Test expert verification and track record validation."""
        request = ModerationRequest(
            content="Based on my 15 years of experience, I predict NIFTY will reach 22,000 by Q2.",
            content_type="text",
            user_context={
                "user_id": "expert_123",
                "client_id": "test",
                "tier": "quantum",
                "expert_claims": {
                    "experience_years": 15,
                    "sebi_registration": "INH000001234",
                    "track_record": {"accuracy": 0.78, "total_calls": 250}
                }
            },
            channel="telegram",
            metadata={"requires_verification": True}
        )
        
        # Mock expert verification response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "action": "allow_with_verification",
            "confidence_score": 0.92,
            "spam_categories": [],
            "risk_level": "low",
            "explanation": "Expert credentials verified. Track record shows 78% accuracy over 250 calls.",
            "escalation_required": False,
            "verification_status": "verified",
            "expert_score": 0.85
        })
        mock_response.usage.total_tokens = 150
        
        moderation_engine.openai_client.chat.completions.create.return_value = mock_response
        
        response = await moderation_engine.moderate_content(request, test_db_session)
        
        assert response.action == "allow_with_verification"
        assert "verification_status" in response.metadata
        assert response.metadata["verification_status"] == "verified"
        assert "expert_score" in response.metadata
        assert response.confidence_score >= 0.90
    
    async def test_multi_channel_moderation(self, moderation_engine, test_db_session):
        """Test moderation across different channels."""
        channels = ["whatsapp", "telegram", "discord", "api", "web"]
        
        for channel in channels:
            request = ModerationRequest(
                content="Check out this amazing stock tip!",
                content_type="text",
                user_context={"user_id": "test", "client_id": "test", "tier": "growth"},
                channel=channel,
                metadata={"channel_specific": f"{channel}_metadata"}
            )
            
            # Mock channel-specific moderation
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            
            # Different channels might have different tolerance levels
            channel_actions = {
                "whatsapp": "flag",  # More strict due to spam potential
                "telegram": "allow",  # Moderate tolerance
                "discord": "allow",   # Community moderation
                "api": "allow",       # Programmatic access
                "web": "flag"        # Public facing
            }
            
            mock_response.choices[0].message.content = json.dumps({
                "action": channel_actions[channel],
                "confidence_score": 0.85,
                "spam_categories": ["promotional_content"] if channel in ["whatsapp", "web"] else [],
                "risk_level": "moderate",
                "explanation": f"Content moderated for {channel} channel with appropriate tolerance",
                "escalation_required": False
            })
            mock_response.usage.total_tokens = 110
            
            moderation_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await moderation_engine.moderate_content(request, test_db_session)
            
            assert response.action == channel_actions[channel]
            assert channel in response.explanation.lower()
    
    async def test_content_type_specific_moderation(self, moderation_engine, test_db_session):
        """Test moderation for different content types."""
        content_types = ["text", "image", "video", "audio", "document"]
        
        for content_type in content_types:
            request = ModerationRequest(
                content=f"Sample {content_type} content for moderation",
                content_type=content_type,
                user_context={"user_id": "test", "client_id": "test", "tier": "enterprise"},
                channel="api",
                metadata={"file_size": "1MB", "format": f"{content_type}_format"}
            )
            
            # Mock content type specific response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "action": "allow",
                "confidence_score": 0.88,
                "spam_categories": [],
                "risk_level": "low",
                "explanation": f"Content type {content_type} passed moderation checks",
                "escalation_required": False,
                "content_analysis": {
                    "type_specific_checks": f"{content_type}_verification_passed"
                }
            })
            mock_response.usage.total_tokens = 95
            
            moderation_engine.openai_client.chat.completions.create.return_value = mock_response
            
            response = await moderation_engine.moderate_content(request, test_db_session)
            
            assert response.action == "allow"
            assert content_type in response.explanation
            assert "content_analysis" in response.metadata
    
    async def test_escalation_workflow(self, moderation_engine, test_db_session):
        """Test escalation workflow for complex cases."""
        request = ModerationRequest(
            content="Borderline content that requires human review for accurate classification",
            content_type="text",
            user_context={"user_id": "ambiguous_user", "client_id": "test", "tier": "enterprise"},
            channel="telegram",
            metadata={"complexity": "high", "requires_human_review": True}
        )
        
        # Mock escalation response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "action": "escalate",
            "confidence_score": 0.65,  # Lower confidence triggers escalation
            "spam_categories": ["ambiguous_promotional"],
            "risk_level": "moderate",
            "explanation": "Content ambiguity requires human moderator review",
            "escalation_required": True,
            "escalation_reason": "low_confidence_classification",
            "recommended_actions": ["human_review", "context_analysis", "user_history_check"]
        })
        mock_response.usage.total_tokens = 130
        
        moderation_engine.openai_client.chat.completions.create.return_value = mock_response
        
        response = await moderation_engine.moderate_content(request, test_db_session)
        
        assert response.action == "escalate"
        assert response.confidence_score < 0.8  # Low confidence
        assert response.escalation_required is True
        assert "escalation_reason" in response.metadata
        assert len(response.recommended_actions) > 0
    
    async def test_performance_requirements(self, moderation_engine, test_db_session):
        """Test moderation performance requirements."""
        import time
        
        request = ModerationRequest(
            content="Performance test content for moderation speed",
            content_type="text",
            user_context={"user_id": "perf_test", "client_id": "test", "tier": "enterprise"},
            channel="api",
            metadata={}
        )
        
        # Mock fast response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "action": "allow",
            "confidence_score": 0.94,
            "spam_categories": [],
            "risk_level": "low",
            "explanation": "Fast moderation response",
            "escalation_required": False
        })
        mock_response.usage.total_tokens = 80
        
        moderation_engine.openai_client.chat.completions.create.return_value = mock_response
        
        start_time = time.time()
        response = await moderation_engine.moderate_content(request, test_db_session)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        # Performance requirements
        assert response.processing_time_ms <= 100  # Sub-100ms requirement
        assert processing_time_ms <= 200  # Allow for test overhead
        assert response.confidence_score >= 0.90  # Maintain high accuracy