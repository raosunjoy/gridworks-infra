"""
Comprehensive Test Suite for AI Intelligence Service
Tests Global Morning Pulse and Intelligence-as-a-Service functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal

from app.ai_intelligence.intelligence_engine import (
    AIIntelligence,
    UserTier,
    CorrelationAnalyzer,
    TradeIdeaGenerator,
    VoiceNoteGenerator,
    MarketDataProcessor
)


class TestUserTier:
    """Test UserTier enum for Intelligence service"""
    
    def test_user_tier_values(self):
        """Test all tier values exist"""
        assert UserTier.LITE.value == "lite"
        assert UserTier.PRO.value == "pro"
        assert UserTier.BLACK.value == "black"
    
    def test_user_tier_from_string(self):
        """Test tier creation from string"""
        assert UserTier("lite") == UserTier.LITE
        assert UserTier("pro") == UserTier.PRO
        assert UserTier("black") == UserTier.BLACK


class TestMarketDataProcessor:
    """Test market data processing functionality"""
    
    @pytest.fixture
    def processor(self):
        return MarketDataProcessor()
    
    @pytest.mark.asyncio
    async def test_fetch_nasdaq_data(self, processor):
        """Test fetching NASDAQ market data"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "chart": {
                    "result": [{
                        "meta": {
                            "regularMarketPrice": 15500.25,
                            "previousClose": 15600.00,
                            "chartPreviousClose": 15600.00
                        },
                        "indicators": {
                            "quote": [{
                                "close": [15500.25, 15525.50, 15480.75]
                            }]
                        }
                    }]
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            nasdaq_data = await processor.fetch_nasdaq_data()
            
            assert nasdaq_data["current_price"] == 15500.25
            assert nasdaq_data["previous_close"] == 15600.00
            assert nasdaq_data["change_percent"] == pytest.approx(-0.64, rel=1e-2)
            assert len(nasdaq_data["recent_prices"]) == 3
    
    @pytest.mark.asyncio
    async def test_fetch_indian_indices(self, processor):
        """Test fetching Indian market indices"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "NIFTY_50": {
                    "current": 18500.25,
                    "previous_close": 18600.00,
                    "change": -99.75
                },
                "SENSEX": {
                    "current": 62500.50,
                    "previous_close": 62800.00,
                    "change": -299.50
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            indian_data = await processor.fetch_indian_indices()
            
            assert indian_data["NIFTY_50"]["current"] == 18500.25
            assert indian_data["NIFTY_50"]["change_percent"] == pytest.approx(-0.536, rel=1e-2)
            assert indian_data["SENSEX"]["current"] == 62500.50
    
    @pytest.mark.asyncio
    async def test_fetch_sector_data(self, processor):
        """Test fetching sector performance data"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "sectors": {
                    "IT": {"change_percent": -1.25, "volume_ratio": 1.45},
                    "Banking": {"change_percent": 0.85, "volume_ratio": 1.20},
                    "Energy": {"change_percent": 2.30, "volume_ratio": 1.80}
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            sector_data = await processor.fetch_sector_data()
            
            assert sector_data["IT"]["change_percent"] == -1.25
            assert sector_data["Banking"]["change_percent"] == 0.85
            assert sector_data["Energy"]["change_percent"] == 2.30
    
    @pytest.mark.asyncio
    async def test_get_commodity_prices(self, processor):
        """Test fetching commodity prices"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "commodities": {
                    "CRUDE_OIL": {"price": 85.25, "change_percent": 3.2},
                    "GOLD": {"price": 2050.50, "change_percent": -0.8},
                    "SILVER": {"price": 25.75, "change_percent": 1.5}
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            commodity_data = await processor.get_commodity_prices()
            
            assert commodity_data["CRUDE_OIL"]["price"] == 85.25
            assert commodity_data["CRUDE_OIL"]["change_percent"] == 3.2
            assert commodity_data["GOLD"]["change_percent"] == -0.8


class TestCorrelationAnalyzer:
    """Test correlation analysis between global and Indian markets"""
    
    @pytest.fixture
    def analyzer(self):
        return CorrelationAnalyzer()
    
    def test_calculate_correlation_strength(self, analyzer):
        """Test correlation strength calculation"""
        nasdaq_change = -1.2
        nifty_change = -0.8
        
        correlation = analyzer.calculate_correlation_strength(nasdaq_change, nifty_change)
        
        assert correlation["strength"] == "moderate"  # Both negative, moderate correlation
        assert correlation["direction"] == "positive"
        assert 0.4 <= correlation["coefficient"] <= 0.8
    
    def test_analyze_sector_impact(self, analyzer):
        """Test sector impact analysis"""
        nasdaq_change = -1.5
        sector_data = {
            "IT": {"change_percent": -1.25, "volume_ratio": 1.45},
            "Banking": {"change_percent": 0.85, "volume_ratio": 1.20}
        }
        
        impact = analyzer.analyze_sector_impact(nasdaq_change, sector_data)
        
        assert "IT" in impact["high_impact_sectors"]
        assert impact["IT"]["correlation"] == "strong"  # IT follows NASDAQ closely
        assert impact["Banking"]["correlation"] == "weak"  # Banking opposite to NASDAQ
    
    def test_generate_correlation_insights(self, analyzer):
        """Test generation of correlation insights"""
        market_data = {
            "nasdaq": {"change_percent": -1.2},
            "nifty": {"change_percent": -0.8},
            "sectors": {
                "IT": {"change_percent": -1.1, "volume_ratio": 1.3}
            }
        }
        
        insights = analyzer.generate_correlation_insights(market_data)
        
        assert len(insights) >= 1
        assert any("IT" in insight for insight in insights)
        assert any("NASDAQ" in insight for insight in insights)


class TestTradeIdeaGenerator:
    """Test trade idea generation functionality"""
    
    @pytest.fixture
    def generator(self):
        return TradeIdeaGenerator()
    
    def test_generate_ideas_for_pro_tier(self, generator):
        """Test trade idea generation for Pro tier"""
        market_data = {
            "nasdaq": {"change_percent": -1.2},
            "sectors": {
                "IT": {"change_percent": -1.1, "volume_ratio": 1.3},
                "Energy": {"change_percent": 2.5, "volume_ratio": 1.8}
            },
            "commodities": {
                "CRUDE_OIL": {"change_percent": 3.2}
            }
        }
        
        ideas = generator.generate_ideas(market_data, UserTier.PRO)
        
        assert len(ideas) == 3  # Pro tier gets 3 ideas
        
        # Check structure of ideas
        for idea in ideas:
            assert "symbol" in idea
            assert "action" in idea
            assert "entry_price" in idea
            assert "stop_loss" in idea
            assert "target" in idea
            assert "confidence" in idea
            assert "reasoning" in idea
            assert "timeframe" in idea
    
    def test_generate_ideas_for_black_tier(self, generator):
        """Test trade idea generation for Black tier"""
        market_data = {
            "nasdaq": {"change_percent": 0.8},
            "sectors": {"Banking": {"change_percent": 1.2}},
            "institutional_flows": {
                "fii_activity": "buying",
                "dii_activity": "selling"
            }
        }
        
        ideas = generator.generate_ideas(market_data, UserTier.BLACK)
        
        assert len(ideas) == 10  # Black tier gets 10 ideas
        
        # Black tier should have more sophisticated ideas
        sophisticated_idea = ideas[0]
        assert "institutional_context" in sophisticated_idea
        assert sophisticated_idea["complexity"] == "high"
    
    def test_calculate_confidence_score(self, generator):
        """Test confidence score calculation"""
        idea_context = {
            "nasdaq_alignment": True,
            "sector_strength": "high",
            "volume_confirmation": True,
            "technical_setup": "bullish"
        }
        
        confidence = generator.calculate_confidence_score(idea_context)
        
        assert 70 <= confidence <= 95  # High confidence due to all positive factors
    
    def test_add_risk_management(self, generator):
        """Test risk management addition to trade ideas"""
        base_idea = {
            "symbol": "RELIANCE",
            "action": "BUY",
            "entry_price": 2450.00
        }
        
        enhanced_idea = generator.add_risk_management(base_idea)
        
        assert "stop_loss" in enhanced_idea
        assert "target" in enhanced_idea
        assert "position_size" in enhanced_idea
        assert enhanced_idea["stop_loss"] < enhanced_idea["entry_price"]  # For buy order
        assert enhanced_idea["target"] > enhanced_idea["entry_price"]


class TestVoiceNoteGenerator:
    """Test voice note generation functionality"""
    
    @pytest.fixture
    def voice_generator(self):
        return VoiceNoteGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_voice_script_pro(self, voice_generator):
        """Test voice script generation for Pro tier"""
        market_summary = {
            "nasdaq_change": -1.2,
            "nifty_impact": -0.8,
            "key_sectors": ["IT", "Energy"],
            "trade_ideas": [
                {"symbol": "TCS", "action": "SHORT", "confidence": 75}
            ]
        }
        
        script = await voice_generator.generate_voice_script(market_summary, UserTier.PRO)
        
        assert "Good morning" in script
        assert "NASDAQ" in script
        assert "TCS" in script
        assert len(script.split()) >= 30  # Substantial content
        assert len(script.split()) <= 80  # But not too long for 30-second limit
    
    @pytest.mark.asyncio
    async def test_generate_voice_script_black(self, voice_generator):
        """Test voice script generation for Black tier"""
        market_summary = {
            "nasdaq_change": 0.5,
            "institutional_flows": {
                "fii_buying": 1500,
                "dii_selling": 800
            },
            "trade_ideas": [
                {"symbol": "HDFC", "action": "BUY", "institutional_context": "Large FII buying"}
            ]
        }
        
        script = await voice_generator.generate_voice_script(market_summary, UserTier.BLACK)
        
        assert "institutional" in script.lower()
        assert "FII" in script
        assert "HDFC" in script
        assert len(script.split()) >= 100  # More detailed for Black tier
    
    @pytest.mark.asyncio
    @patch('app.ai_intelligence.intelligence_engine.openai')
    async def test_convert_to_audio(self, mock_openai, voice_generator):
        """Test converting script to audio"""
        mock_openai.audio.speech.create = AsyncMock(return_value=MagicMock(
            content=b"fake_audio_data"
        ))
        
        script = "Good morning! NASDAQ is down 1.2%..."
        
        audio_data = await voice_generator.convert_to_audio(script, "english")
        
        assert audio_data == b"fake_audio_data"
        mock_openai.audio.speech.create.assert_called_once()
    
    def test_adapt_script_for_language(self, voice_generator):
        """Test script adaptation for different languages"""
        english_script = "Good morning! NASDAQ is down 1.2%"
        
        hindi_script = voice_generator.adapt_script_for_language(english_script, "hindi")
        
        assert "नमस्ते" in hindi_script or "सुप्रभात" in hindi_script
        assert "NASDAQ" in hindi_script  # Technical terms preserved


class TestAIIntelligence:
    """Test main AI Intelligence service class"""
    
    @pytest.fixture
    def ai_intelligence(self):
        return AIIntelligence()
    
    @pytest.mark.asyncio
    @patch('app.ai_intelligence.intelligence_engine.MarketDataProcessor')
    @patch('app.ai_intelligence.intelligence_engine.CorrelationAnalyzer')
    @patch('app.ai_intelligence.intelligence_engine.TradeIdeaGenerator')
    @patch('app.ai_intelligence.intelligence_engine.VoiceNoteGenerator')
    async def test_generate_morning_pulse_pro(
        self, mock_voice, mock_trader, mock_analyzer, mock_processor, ai_intelligence
    ):
        """Test morning pulse generation for Pro tier"""
        # Mock market data
        mock_processor_instance = Mock()
        mock_processor_instance.fetch_nasdaq_data = AsyncMock(return_value={
            "current_price": 15500, "change_percent": -1.2
        })
        mock_processor_instance.fetch_indian_indices = AsyncMock(return_value={
            "NIFTY_50": {"current": 18500, "change_percent": -0.8}
        })
        mock_processor_instance.fetch_sector_data = AsyncMock(return_value={
            "IT": {"change_percent": -1.1}
        })
        mock_processor.return_value = mock_processor_instance
        
        # Mock correlation analysis
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.generate_correlation_insights = Mock(return_value=[
            "IT stocks may face pressure from NASDAQ decline"
        ])
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Mock trade ideas
        mock_trader_instance = Mock()
        mock_trader_instance.generate_ideas = Mock(return_value=[
            {"symbol": "TCS", "action": "SHORT", "confidence": 75}
        ])
        mock_trader.return_value = mock_trader_instance
        
        # Mock voice generation
        mock_voice_instance = Mock()
        mock_voice_instance.generate_voice_script = AsyncMock(return_value="Voice script...")
        mock_voice_instance.convert_to_audio = AsyncMock(return_value=b"audio_data")
        mock_voice.return_value = mock_voice_instance
        
        # Test generation
        result = await ai_intelligence.generate_morning_pulse(
            user_id="pro_user_123",
            user_tier=UserTier.PRO,
            delivery_channels=["whatsapp", "app"],
            language="english"
        )
        
        assert result["success"] is True
        assert result["format"] == "voice_plus_text"
        assert "content" in result
        assert "voice_note_url" in result
        assert len(result["content"]["trade_ideas"]) > 0
        assert result["content"]["market_summary"]["nasdaq_change"] == -1.2
    
    @pytest.mark.asyncio
    async def test_generate_morning_pulse_lite_teaser(self, ai_intelligence):
        """Test morning pulse teaser for Lite tier"""
        result = await ai_intelligence.generate_morning_pulse(
            user_id="lite_user_123", 
            user_tier=UserTier.LITE
        )
        
        assert result["success"] is True
        assert result["format"] == "teaser"
        assert "locked_content" in result["content"]
        assert "upsell_message" in result["content"]
        assert result["content"]["trade_ideas_count"] == 0  # No ideas for Lite
    
    @pytest.mark.asyncio
    @patch('app.ai_intelligence.intelligence_engine.MarketDataProcessor')
    async def test_generate_morning_pulse_black_institutional(
        self, mock_processor, ai_intelligence
    ):
        """Test morning pulse generation for Black tier with institutional data"""
        # Mock comprehensive market data
        mock_processor_instance = Mock()
        mock_processor_instance.fetch_nasdaq_data = AsyncMock(return_value={
            "current_price": 15500, "change_percent": -1.2
        })
        mock_processor_instance.fetch_indian_indices = AsyncMock(return_value={
            "NIFTY_50": {"current": 18500, "change_percent": -0.8}
        })
        mock_processor_instance.fetch_sector_data = AsyncMock(return_value={})
        mock_processor_instance.fetch_institutional_flows = AsyncMock(return_value={
            "fii_net_position": -2400,
            "dii_net_position": 1800
        })
        mock_processor_instance.fetch_block_deals = AsyncMock(return_value=[
            {"stock": "RELIANCE", "volume": 1000000, "price": 2450}
        ])
        mock_processor.return_value = mock_processor_instance
        
        result = await ai_intelligence.generate_morning_pulse(
            user_id="black_user_123",
            user_tier=UserTier.BLACK
        )
        
        assert result["success"] is True
        assert result["format"] == "institutional_report"
        assert "institutional_intelligence" in result["content"]
        assert "fii_flows" in result["content"]["institutional_intelligence"]
        assert "block_deals" in result["content"]["institutional_intelligence"]
    
    @pytest.mark.asyncio
    async def test_create_custom_alert(self, ai_intelligence):
        """Test custom alert creation"""
        alert_config = {
            "symbol": "RELIANCE",
            "condition": "price_above",
            "threshold": 2500,
            "notification_channels": ["whatsapp", "email"]
        }
        
        result = await ai_intelligence.create_custom_alert(
            user_id="user_123",
            alert_config=alert_config
        )
        
        assert result["success"] is True
        assert "alert_id" in result
        assert result["alert_config"]["symbol"] == "RELIANCE"
        assert result["alert_config"]["threshold"] == 2500
    
    @pytest.mark.asyncio
    async def test_get_historical_performance(self, ai_intelligence):
        """Test getting historical performance of trade ideas"""
        result = await ai_intelligence.get_historical_performance(
            user_id="user_123",
            days_back=30
        )
        
        assert result["success"] is True
        assert "performance_metrics" in result
        assert "win_rate" in result["performance_metrics"]
        assert "average_return" in result["performance_metrics"]
        assert "total_ideas" in result["performance_metrics"]
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, ai_intelligence):
        """Test service health status"""
        status = await ai_intelligence.get_health_status()
        
        assert status["status"] in ["healthy", "degraded", "unhealthy"]
        assert "uptime" in status
        assert "last_check" in status
        assert "service_metrics" in status
    
    @pytest.mark.asyncio
    async def test_shutdown(self, ai_intelligence):
        """Test service shutdown"""
        await ai_intelligence.shutdown()
        
        # After shutdown, service should not be accessible
        # This test ensures cleanup happens properly


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def ai_intelligence(self):
        return AIIntelligence()
    
    @pytest.mark.asyncio
    async def test_market_data_fetch_failure(self, ai_intelligence):
        """Test handling of market data fetch failures"""
        with patch('app.ai_intelligence.intelligence_engine.MarketDataProcessor') as mock_processor:
            mock_processor_instance = Mock()
            mock_processor_instance.fetch_nasdaq_data = AsyncMock(
                side_effect=Exception("Market data API down")
            )
            mock_processor.return_value = mock_processor_instance
            
            result = await ai_intelligence.generate_morning_pulse(
                user_id="user_123",
                user_tier=UserTier.PRO
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "fallback_content" in result
    
    @pytest.mark.asyncio
    async def test_voice_generation_failure(self, ai_intelligence):
        """Test handling of voice generation failures"""
        with patch('app.ai_intelligence.intelligence_engine.VoiceNoteGenerator') as mock_voice:
            mock_voice_instance = Mock()
            mock_voice_instance.generate_voice_script = AsyncMock(return_value="Script")
            mock_voice_instance.convert_to_audio = AsyncMock(
                side_effect=Exception("Voice API error")
            )
            mock_voice.return_value = mock_voice_instance
            
            with patch('app.ai_intelligence.intelligence_engine.MarketDataProcessor') as mock_processor:
                mock_processor_instance = Mock()
                mock_processor_instance.fetch_nasdaq_data = AsyncMock(return_value={
                    "current_price": 15500, "change_percent": -1.2
                })
                mock_processor_instance.fetch_indian_indices = AsyncMock(return_value={
                    "NIFTY_50": {"current": 18500, "change_percent": -0.8}
                })
                mock_processor_instance.fetch_sector_data = AsyncMock(return_value={})
                mock_processor.return_value = mock_processor_instance
                
                result = await ai_intelligence.generate_morning_pulse(
                    user_id="user_123",
                    user_tier=UserTier.PRO
                )
                
                # Should still succeed with text-only format
                assert result["success"] is True
                assert result["format"] == "text_only"  # Fallback format
    
    @pytest.mark.asyncio
    async def test_invalid_user_tier(self, ai_intelligence):
        """Test handling of invalid user tier"""
        with pytest.raises(ValueError):
            await ai_intelligence.generate_morning_pulse(
                user_id="user_123",
                user_tier="invalid_tier"
            )
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, ai_intelligence):
        """Test rate limiting functionality"""
        user_id = "rate_limited_user"
        
        # Simulate multiple rapid requests
        tasks = []
        for i in range(10):
            task = ai_intelligence.generate_morning_pulse(
                user_id=user_id,
                user_tier=UserTier.PRO
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Some requests should be rate limited
        rate_limited_count = sum(
            1 for result in results 
            if isinstance(result, dict) and not result.get("success") and "rate_limit" in result.get("error", "")
        )
        
        assert rate_limited_count > 0  # At least some should be rate limited


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    @pytest.fixture
    def ai_intelligence(self):
        return AIIntelligence()
    
    @pytest.mark.asyncio
    async def test_complete_morning_pulse_workflow(self, ai_intelligence):
        """Test complete morning pulse generation workflow"""
        with patch('app.ai_intelligence.intelligence_engine.MarketDataProcessor') as mock_processor:
            # Setup comprehensive mock data
            mock_processor_instance = Mock()
            mock_processor_instance.fetch_nasdaq_data = AsyncMock(return_value={
                "current_price": 15500, "change_percent": -1.2, "volume_ratio": 1.3
            })
            mock_processor_instance.fetch_indian_indices = AsyncMock(return_value={
                "NIFTY_50": {"current": 18500, "change_percent": -0.8, "volume": 145000000}
            })
            mock_processor_instance.fetch_sector_data = AsyncMock(return_value={
                "IT": {"change_percent": -1.1, "volume_ratio": 1.4},
                "Banking": {"change_percent": 0.3, "volume_ratio": 1.1}
            })
            mock_processor_instance.get_commodity_prices = AsyncMock(return_value={
                "CRUDE_OIL": {"price": 85.25, "change_percent": 3.2}
            })
            mock_processor.return_value = mock_processor_instance
            
            # Test Pro tier workflow
            result = await ai_intelligence.generate_morning_pulse(
                user_id="integration_user",
                user_tier=UserTier.PRO,
                delivery_channels=["whatsapp", "app"],
                language="english"
            )
            
            # Verify complete workflow
            assert result["success"] is True
            assert "content" in result
            assert "market_summary" in result["content"]
            assert "trade_ideas" in result["content"]
            assert "correlation_insights" in result["content"]
            assert "voice_note_url" in result
            
            # Verify data flow
            assert result["content"]["market_summary"]["nasdaq_change"] == -1.2
            assert len(result["content"]["trade_ideas"]) > 0
            assert len(result["content"]["correlation_insights"]) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])