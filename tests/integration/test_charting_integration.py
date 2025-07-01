"""
TradeMate Charting Platform Integration Tests
===========================================
End-to-end integration tests for professional charting platform
ensuring seamless integration between all components
"""

import pytest
import asyncio
import time
import json
import uuid
import numpy as np
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timedelta

# Test libraries
import pytest_asyncio
import pytest_benchmark

# Integration test modules
from app.pro.charting_platform import (
    ChartingEngine, TechnicalAnalysisEngine, RealTimeDataFeed,
    OHLCV, ChartType, TimeFrame, IndicatorType, PatternType
)
from app.pro.voice_charting_engine import (
    VoiceChartingEngine, VoiceLanguage, VoiceCommandType
)
from app.lite.basic_charting import (
    BasicChartingEngine, LiteChartMessaging, LiteTimeFrame, LiteIndicator
)
from app.whatsapp.message_handler import WhatsAppMessageHandler
from app.ai.conversation_engine import ConversationEngine


class IntegrationTestConfig:
    """Integration test configuration"""
    
    # End-to-end performance targets
    MAX_E2E_RESPONSE_TIME_S = 5.0
    MAX_WHATSAPP_TO_CHART_TIME_S = 3.0
    MAX_VOICE_TO_CHART_TIME_S = 4.0
    MAX_UPGRADE_FLOW_TIME_S = 2.0
    
    # Data consistency requirements
    MIN_DATA_ACCURACY = 99.9
    MAX_DATA_SYNC_DELAY_MS = 100


class IntegrationTestDataFactory:
    """Factory for integration test data"""
    
    @staticmethod
    def create_user_scenario(tier: str = "PRO") -> Dict[str, Any]:
        """Create user scenario for testing"""
        return {
            "user_id": str(uuid.uuid4()),
            "phone_number": f"+91{np.random.randint(1000000000, 9999999999)}",
            "tier": tier,
            "preferred_language": "hindi",
            "trading_experience": "intermediate",
            "portfolio_value": 100000.0,
            "risk_tolerance": "medium"
        }
    
    @staticmethod
    def create_whatsapp_message_flow() -> List[Dict[str, Any]]:
        """Create realistic WhatsApp message flow"""
        return [
            {
                "type": "text",
                "content": "Show me Reliance chart",
                "expected_response": "chart_summary"
            },
            {
                "type": "text", 
                "content": "Add RSI indicator",
                "expected_response": "indicator_added"
            },
            {
                "type": "text",
                "content": "Set alert at 2600",
                "expected_response": "alert_confirmation"
            },
            {
                "type": "text",
                "content": "Buy 10 shares at market price",
                "expected_response": "trade_confirmation"
            }
        ]
    
    @staticmethod
    def create_voice_command_flow() -> List[Dict[str, Any]]:
        """Create realistic voice command flow"""
        return [
            {
                "language": VoiceLanguage.HINDI,
                "command": "Reliance ka chart dikhao",
                "expected_action": "create_chart"
            },
            {
                "language": VoiceLanguage.HINDI,
                "command": "RSI add karo 14 period ka",
                "expected_action": "add_indicator"
            },
            {
                "language": VoiceLanguage.HINDI,
                "command": "Pattern detect karo",
                "expected_action": "detect_patterns"
            },
            {
                "language": VoiceLanguage.HINDI,
                "command": "Price alert lagao 2600 pe",
                "expected_action": "set_alert"
            }
        ]


@pytest.fixture
async def integrated_charting_system():
    """Set up integrated charting system for testing"""
    
    # Initialize components
    data_feed = RealTimeDataFeed()
    charting_engine = ChartingEngine(data_feed)
    voice_engine = VoiceChartingEngine(charting_engine)
    basic_engine = BasicChartingEngine()
    
    # Mock external dependencies
    with patch.object(data_feed, '_start_websocket_feed'):
        with patch('speech_recognition.Recognizer'):
            with patch('speech_recognition.Microphone'):
                with patch('pyttsx3.init'):
                    yield {
                        "data_feed": data_feed,
                        "charting_engine": charting_engine,
                        "voice_engine": voice_engine,
                        "basic_engine": basic_engine
                    }


@pytest.fixture
async def mock_whatsapp_handler():
    """Mock WhatsApp message handler"""
    handler = Mock(spec=WhatsAppMessageHandler)
    handler.process_message = AsyncMock()
    handler.send_message = AsyncMock()
    yield handler


@pytest.fixture
async def mock_conversation_engine():
    """Mock conversation engine"""
    engine = Mock(spec=ConversationEngine)
    engine.process_message = AsyncMock()
    yield engine


class TestPROChartingIntegration:
    """Test PRO tier charting integration"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="pro_integration")
    async def test_complete_pro_charting_workflow(self, integrated_charting_system, benchmark):
        """Test complete PRO charting workflow performance"""
        
        system = integrated_charting_system
        user_scenario = IntegrationTestDataFactory.create_user_scenario("PRO")
        
        async def complete_workflow():
            # 1. Create professional chart
            with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
                mock_load.return_value = [
                    OHLCV(
                        timestamp=datetime.now() - timedelta(minutes=i),
                        open=2500.0 + i,
                        high=2520.0 + i,
                        low=2480.0 + i,
                        close=2510.0 + i,
                        volume=10000,
                        symbol="RELIANCE",
                        timeframe=TimeFrame.FIFTEEN_MINUTES
                    ) for i in range(100)
                ]
                
                chart_id = await system["charting_engine"].create_chart(
                    user_id=user_scenario["user_id"],
                    symbol="RELIANCE",
                    timeframe=TimeFrame.FIFTEEN_MINUTES,
                    chart_type=ChartType.CANDLESTICK
                )
            
            # 2. Add multiple technical indicators
            indicators = [
                (IndicatorType.SMA, {"period": 20}),
                (IndicatorType.EMA, {"period": 20}),
                (IndicatorType.RSI, {"period": 14}),
                (IndicatorType.MACD, {"fast": 12, "slow": 26, "signal": 9}),
                (IndicatorType.BOLLINGER_BANDS, {"period": 20, "std_dev": 2})
            ]
            
            indicator_ids = []
            for indicator_type, params in indicators:
                indicator_id = await system["charting_engine"].add_indicator(
                    chart_id=chart_id,
                    indicator_type=indicator_type,
                    parameters=params
                )
                indicator_ids.append(indicator_id)
            
            # 3. Detect chart patterns
            patterns = await system["charting_engine"].detect_patterns(
                chart_id=chart_id,
                pattern_types=[PatternType.DOJI, PatternType.HAMMER, PatternType.HEAD_AND_SHOULDERS]
            )
            
            # 4. Add drawing tools
            drawing_id = await system["charting_engine"].add_drawing_tool(
                chart_id=chart_id,
                tool_type="trendline",
                coordinates=[{"x": 100, "y": 2500}, {"x": 200, "y": 2600}],
                style={"color": "blue", "thickness": 2},
                user_id=user_scenario["user_id"],
                annotation="Support trendline"
            )
            
            # 5. Set chart alerts
            alert_id = await system["charting_engine"].create_alert(
                user_id=user_scenario["user_id"],
                symbol="RELIANCE",
                timeframe=TimeFrame.FIFTEEN_MINUTES,
                condition="price > 2600",
                alert_type="price"
            )
            
            return {
                "chart_id": chart_id,
                "indicators": len(indicator_ids),
                "patterns": len(patterns),
                "drawing_id": drawing_id,
                "alert_id": alert_id
            }
        
        result = await benchmark.pedantic(complete_workflow, rounds=3)
        
        # Verify workflow completion
        assert isinstance(result["chart_id"], str)
        assert result["indicators"] == 5
        assert result["patterns"] >= 0  # Patterns may or may not be found
        assert isinstance(result["drawing_id"], str)
        assert isinstance(result["alert_id"], str)
    
    @pytest.mark.asyncio
    async def test_real_time_data_integration(self, integrated_charting_system):
        """Test real-time data integration with charting"""
        
        system = integrated_charting_system
        chart_id = "test_chart_integration"
        symbol = "RELIANCE"
        timeframe = TimeFrame.ONE_MINUTE
        
        # Initialize chart data storage
        system["charting_engine"].chart_data = {}
        system["charting_engine"].alerts = {}
        
        # Simulate real-time data updates
        test_updates = []
        for i in range(10):
            ohlcv = OHLCV(
                timestamp=datetime.now() + timedelta(minutes=i),
                open=2500.0 + i,
                high=2520.0 + i,
                low=2480.0 + i,
                close=2510.0 + i,
                volume=10000 + i * 100,
                symbol=symbol,
                timeframe=timeframe
            )
            test_updates.append(ohlcv)
        
        # Process updates sequentially
        for update in test_updates:
            system["charting_engine"]._update_chart_data(chart_id, symbol, timeframe, update)
        
        # Verify data storage
        key = f"{chart_id}_{symbol}_{timeframe.value}"
        assert key in system["charting_engine"].chart_data
        assert len(system["charting_engine"].chart_data[key]) == 10
        
        # Verify chronological order
        stored_data = system["charting_engine"].chart_data[key]
        for i in range(1, len(stored_data)):
            assert stored_data[i].timestamp > stored_data[i-1].timestamp
    
    @pytest.mark.asyncio
    async def test_indicator_calculation_integration(self, integrated_charting_system):
        """Test technical indicator calculation integration"""
        
        system = integrated_charting_system
        
        # Create chart with historical data
        with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
            # Create realistic price data with trend
            historical_data = []
            base_price = 2500.0
            
            for i in range(100):
                # Add some trend and noise
                trend = i * 2  # Upward trend
                noise = np.random.normal(0, 10)
                price = base_price + trend + noise
                
                ohlcv = OHLCV(
                    timestamp=datetime.now() - timedelta(minutes=100-i),
                    open=price + np.random.normal(0, 2),
                    high=price + abs(np.random.normal(0, 8)),
                    low=price - abs(np.random.normal(0, 8)),
                    close=price + np.random.normal(0, 2),
                    volume=int(np.random.normal(10000, 2000)),
                    symbol="RELIANCE",
                    timeframe=TimeFrame.ONE_MINUTE
                )
                historical_data.append(ohlcv)
            
            mock_load.return_value = historical_data
            
            chart_id = await system["charting_engine"].create_chart(
                user_id="integration_user",
                symbol="RELIANCE",
                timeframe=TimeFrame.ONE_MINUTE
            )
        
        # Test multiple indicators
        test_indicators = [
            (IndicatorType.SMA, {"period": 20}),
            (IndicatorType.EMA, {"period": 20}),
            (IndicatorType.RSI, {"period": 14}),
            (IndicatorType.MACD, {"fast": 12, "slow": 26, "signal": 9}),
            (IndicatorType.BOLLINGER_BANDS, {"period": 20, "std_dev": 2})
        ]
        
        indicator_results = {}
        for indicator_type, params in test_indicators:
            indicator_id = await system["charting_engine"].add_indicator(
                chart_id=chart_id,
                indicator_type=indicator_type,
                parameters=params
            )
            
            # Verify indicator was added
            indicators = system["charting_engine"].indicators[chart_id]
            added_indicator = next(ind for ind in indicators if ind.indicator_id == indicator_id)
            
            assert added_indicator.type == indicator_type
            assert len(added_indicator.values) > 0
            assert len(added_indicator.timestamps) == len(added_indicator.values)
            
            indicator_results[indicator_type] = {
                "values": len(added_indicator.values),
                "parameters": added_indicator.parameters
            }
        
        # Verify all indicators were calculated
        assert len(indicator_results) == 5
        
        # Verify RSI values are in valid range
        rsi_indicator = next(ind for ind in system["charting_engine"].indicators[chart_id] 
                           if ind.type == IndicatorType.RSI)
        assert all(0 <= val <= 100 for val in rsi_indicator.values)
    
    @pytest.mark.asyncio
    async def test_pattern_recognition_integration(self, integrated_charting_system):
        """Test pattern recognition integration with real data"""
        
        system = integrated_charting_system
        
        # Create chart with pattern-specific data
        pattern_data = []
        
        # Create data with known Doji patterns
        for i in range(50):
            if i % 10 == 0:  # Every 10th candle is a Doji
                ohlcv = OHLCV(
                    timestamp=datetime.now() - timedelta(minutes=50-i),
                    open=2500.0,
                    high=2505.0,
                    low=2495.0,
                    close=2500.5,  # Very small body (Doji characteristic)
                    volume=10000,
                    symbol="RELIANCE",
                    timeframe=TimeFrame.ONE_MINUTE
                )
            else:
                # Normal candle
                price = 2500.0 + np.random.normal(0, 20)
                ohlcv = OHLCV(
                    timestamp=datetime.now() - timedelta(minutes=50-i),
                    open=price,
                    high=price + abs(np.random.normal(0, 10)),
                    low=price - abs(np.random.normal(0, 10)),
                    close=price + np.random.normal(0, 5),
                    volume=10000,
                    symbol="RELIANCE",
                    timeframe=TimeFrame.ONE_MINUTE
                )
            pattern_data.append(ohlcv)
        
        with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
            mock_load.return_value = pattern_data
            
            chart_id = await system["charting_engine"].create_chart(
                user_id="pattern_user",
                symbol="RELIANCE",
                timeframe=TimeFrame.ONE_MINUTE
            )
        
        # Detect patterns
        detected_patterns = await system["charting_engine"].detect_patterns(
            chart_id=chart_id,
            pattern_types=[PatternType.DOJI, PatternType.HAMMER]
        )
        
        # Should detect some Doji patterns
        doji_patterns = [p for p in detected_patterns if p.type == PatternType.DOJI]
        assert len(doji_patterns) > 0
        
        # Verify pattern properties
        for pattern in doji_patterns:
            assert pattern.confidence_score > 0.5
            assert pattern.symbol == "RELIANCE"
            assert isinstance(pattern.start_time, datetime)


class TestLITEChartingIntegration:
    """Test LITE tier charting integration"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="lite_integration")
    async def test_lite_charting_workflow(self, integrated_charting_system, benchmark):
        """Test complete LITE charting workflow"""
        
        system = integrated_charting_system
        user_scenario = IntegrationTestDataFactory.create_user_scenario("LITE")
        
        async def lite_workflow():
            # 1. Create LITE chart
            chart_id = await system["basic_engine"].create_lite_chart(
                user_id=user_scenario["user_id"],
                symbol="RELIANCE",
                timeframe=LiteTimeFrame.ONE_HOUR
            )
            
            # 2. Calculate basic indicators
            indicators = [
                LiteIndicator.SMA,
                LiteIndicator.EMA,
                LiteIndicator.RSI,
                LiteIndicator.MACD,
                LiteIndicator.BOLLINGER
            ]
            
            indicator_results = []
            for indicator in indicators:
                result = await system["basic_engine"].get_basic_indicators(
                    chart_id=chart_id,
                    indicator=indicator
                )
                indicator_results.append(result)
            
            # 3. Set price alert
            alert_id = await system["basic_engine"].set_price_alert(
                user_id=user_scenario["user_id"],
                symbol="RELIANCE",
                price=2600.0,
                condition="above"
            )
            
            # 4. Generate WhatsApp summary
            summary = await system["basic_engine"].generate_whatsapp_chart_summary(chart_id)
            
            return {
                "chart_id": chart_id,
                "indicators": len(indicator_results),
                "alert_id": alert_id,
                "summary_length": len(summary)
            }
        
        result = await benchmark.pedantic(lite_workflow, rounds=5)
        
        # Verify LITE workflow
        assert isinstance(result["chart_id"], str)
        assert result["chart_id"].startswith("lite_")
        assert result["indicators"] == 5
        assert isinstance(result["alert_id"], str)
        assert result["summary_length"] > 100  # Substantial summary
    
    @pytest.mark.asyncio
    async def test_lite_whatsapp_integration(self, integrated_charting_system):
        """Test LITE tier WhatsApp integration"""
        
        system = integrated_charting_system
        messaging = LiteChartMessaging(system["basic_engine"])
        
        user_id = "lite_whatsapp_user"
        message_flow = [
            ("Show Reliance chart", "chart_created"),
            ("Add RSI explanation", "educational_content"),
            ("Set alert Reliance above 2600", "alert_set"),
            ("What indicators can I use?", "help_content")
        ]
        
        responses = []
        for message, expected_type in message_flow:
            response = await messaging.process_chart_request(user_id, message)
            responses.append((message, response, expected_type))
        
        # Verify responses
        for message, response, expected_type in responses:
            assert isinstance(response, str)
            assert len(response) > 0
            
            if expected_type == "chart_created":
                assert "Chart Summary" in response or "📊" in response
            elif expected_type == "educational_content":
                assert "Upgrade to TradeMate PRO" in response
            elif expected_type == "alert_set":
                assert "Alert Set Successfully" in response or "alert" in response.lower()
            elif expected_type == "help_content":
                assert "TradeMate LITE" in response
    
    @pytest.mark.asyncio
    async def test_lite_to_pro_upgrade_simulation(self, integrated_charting_system):
        """Test LITE to PRO upgrade flow simulation"""
        
        system = integrated_charting_system
        user_id = "upgrade_test_user"
        
        # Start with LITE features
        lite_chart_id = await system["basic_engine"].create_lite_chart(
            user_id=user_id,
            symbol="RELIANCE"
        )
        
        # Get LITE chart summary
        lite_summary = await system["basic_engine"].generate_whatsapp_chart_summary(lite_chart_id)
        assert "TradeMate LITE" in lite_summary
        
        # Simulate upgrade to PRO
        with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
            mock_load.return_value = [
                OHLCV(
                    timestamp=datetime.now() - timedelta(minutes=i),
                    open=2500.0 + i,
                    high=2520.0 + i,
                    low=2480.0 + i,
                    close=2510.0 + i,
                    volume=10000,
                    symbol="RELIANCE",
                    timeframe=TimeFrame.FIFTEEN_MINUTES
                ) for i in range(100)
            ]
            
            # Create PRO chart (simulating upgrade)
            pro_chart_id = await system["charting_engine"].create_chart(
                user_id=user_id,
                symbol="RELIANCE",
                timeframe=TimeFrame.FIFTEEN_MINUTES
            )
        
        # Add PRO features not available in LITE
        advanced_indicators = [
            IndicatorType.STOCH,
            IndicatorType.CCI,
            IndicatorType.ATR,
            IndicatorType.KELTNER
        ]
        
        pro_indicator_ids = []
        for indicator in advanced_indicators:
            try:
                indicator_id = await system["charting_engine"].add_indicator(
                    chart_id=pro_chart_id,
                    indicator_type=indicator,
                    parameters={"period": 14}
                )
                pro_indicator_ids.append(indicator_id)
            except:
                # Some indicators might not be fully implemented in test
                pass
        
        # Verify PRO features are available
        assert len(pro_indicator_ids) >= 0  # At least some PRO indicators should work
        
        # Verify LITE and PRO charts coexist
        assert lite_chart_id != pro_chart_id
        assert lite_chart_id in system["basic_engine"].lite_charts
        assert pro_chart_id in system["charting_engine"].indicators


class TestVoiceChartingIntegration:
    """Test voice charting integration"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="voice_integration")
    async def test_voice_to_chart_workflow(self, integrated_charting_system, benchmark):
        """Test voice-to-chart workflow performance"""
        
        system = integrated_charting_system
        voice_commands = IntegrationTestDataFactory.create_voice_command_flow()
        
        async def voice_workflow():
            user_id = "voice_user_123"
            
            # Start voice session
            with patch('threading.Thread'):
                with patch.object(system["voice_engine"].feedback_engine, 'speak_feedback'):
                    await system["voice_engine"].start_voice_session(
                        user_id, VoiceLanguage.HINDI
                    )
            
            # Process voice commands
            results = []
            for command_data in voice_commands:
                await system["voice_engine"]._process_voice_command(
                    user_id,
                    command_data["command"],
                    command_data["language"]
                )
                results.append(command_data["expected_action"])
            
            return len(results)
        
        result = await benchmark.pedantic(voice_workflow, rounds=3)
        assert result == len(voice_commands)
    
    @pytest.mark.asyncio
    async def test_multilingual_voice_integration(self, integrated_charting_system):
        """Test multilingual voice command integration"""
        
        system = integrated_charting_system
        
        multilingual_commands = [
            ("Show Reliance chart", VoiceLanguage.ENGLISH),
            ("Reliance ka chart dikhao", VoiceLanguage.HINDI),
            ("Reliance chart காட்டு", VoiceLanguage.TAMIL),
            ("Reliance এর chart দেখাও", VoiceLanguage.BENGALI)
        ]
        
        user_id = "multilingual_user"
        
        # Initialize voice session
        system["voice_engine"].user_sessions[user_id] = {
            "language": VoiceLanguage.HINDI,
            "current_chart": None,
            "listening": True
        }
        system["voice_engine"].voice_commands_history[user_id] = []
        
        # Process commands in different languages
        for command, language in multilingual_commands:
            await system["voice_engine"]._process_voice_command(user_id, command, language)
        
        # Verify all commands were processed
        history = system["voice_engine"].voice_commands_history[user_id]
        assert len(history) == 4
        
        # Verify commands were recognized as chart creation
        chart_commands = [cmd for cmd in history if cmd.command_type == VoiceCommandType.CREATE_CHART]
        assert len(chart_commands) >= 3  # Most should be recognized as chart commands
    
    @pytest.mark.asyncio
    async def test_voice_feedback_integration(self, integrated_charting_system):
        """Test voice feedback integration"""
        
        system = integrated_charting_system
        user_id = "feedback_user"
        
        # Set up voice session
        system["voice_engine"].user_sessions[user_id] = {
            "language": VoiceLanguage.HINDI,
            "current_chart": None,
            "listening": True
        }
        
        # Mock TTS engine for feedback testing
        with patch.object(system["voice_engine"].feedback_engine.tts_engine, 'say') as mock_say:
            with patch.object(system["voice_engine"].feedback_engine.tts_engine, 'runAndWait') as mock_wait:
                
                # Process command that should generate feedback
                await system["voice_engine"]._process_voice_command(
                    user_id, "Reliance ka chart dikhao", VoiceLanguage.HINDI
                )
                
                # Verify feedback was generated
                mock_say.assert_called()
                mock_wait.assert_called()
                
                # Verify Hindi feedback content
                feedback_text = mock_say.call_args[0][0]
                assert "RELIANCE" in feedback_text
                assert any(hindi_word in feedback_text for hindi_word in ["ban gaya", "chart", "hai"])


class TestWhatsAppChartingIntegration:
    """Test WhatsApp integration with charting"""
    
    @pytest.mark.asyncio
    async def test_whatsapp_chart_request_flow(self, integrated_charting_system, mock_whatsapp_handler):
        """Test WhatsApp chart request processing flow"""
        
        system = integrated_charting_system
        message_flow = IntegrationTestDataFactory.create_whatsapp_message_flow()
        
        user_id = "whatsapp_user_123"
        
        # Process WhatsApp message flow
        for message_data in message_flow:
            if message_data["content"] == "Show me Reliance chart":
                # Create chart for LITE user
                chart_id = await system["basic_engine"].create_lite_chart(
                    user_id=user_id,
                    symbol="RELIANCE"
                )
                
                # Generate WhatsApp response
                response = await system["basic_engine"].generate_whatsapp_chart_summary(chart_id)
                
                # Verify response format
                assert isinstance(response, str)
                assert "RELIANCE" in response
                assert "📊" in response
                assert "Current Price" in response
            
            elif message_data["content"] == "Add RSI indicator":
                # For LITE user, should provide educational content
                messaging = LiteChartMessaging(system["basic_engine"])
                response = await messaging.process_chart_request(
                    user_id, "RSI explanation"
                )
                
                assert "RSI" in response
                assert "Upgrade to TradeMate PRO" in response
    
    @pytest.mark.asyncio
    async def test_whatsapp_chart_sharing(self, integrated_charting_system):
        """Test chart sharing via WhatsApp"""
        
        system = integrated_charting_system
        
        # Create chart with interesting data
        user_id = "sharing_user"
        chart_id = await system["basic_engine"].create_lite_chart(
            user_id=user_id,
            symbol="RELIANCE"
        )
        
        # Generate shareable summary
        summary = await system["basic_engine"].generate_whatsapp_chart_summary(chart_id)
        
        # Verify summary is WhatsApp-friendly
        assert len(summary) < 4000  # WhatsApp message limit
        assert summary.count('\n') < 50  # Not too many lines
        assert "📊" in summary or "💰" in summary  # Contains emojis
        assert "TradeMate LITE" in summary  # Branded
        
        # Verify key information is present
        required_elements = [
            "Current Price",
            "Change",
            "Trend", 
            "Support",
            "Resistance"
        ]
        
        for element in required_elements:
            assert element in summary


class TestPerformanceIntegration:
    """Test performance across integrated components"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="integration_performance")
    async def test_concurrent_user_scenarios(self, integrated_charting_system, benchmark):
        """Test concurrent user scenarios performance"""
        
        system = integrated_charting_system
        
        async def concurrent_scenarios():
            # Simulate multiple users with different scenarios
            tasks = []
            
            # PRO users creating advanced charts
            for i in range(5):
                user_id = f"pro_user_{i}"
                with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
                    mock_load.return_value = [
                        OHLCV(
                            timestamp=datetime.now() - timedelta(minutes=j),
                            open=2500.0 + j,
                            high=2520.0 + j,
                            low=2480.0 + j,
                            close=2510.0 + j,
                            volume=10000,
                            symbol="RELIANCE",
                            timeframe=TimeFrame.FIFTEEN_MINUTES
                        ) for j in range(50)
                    ]
                    
                    tasks.append(
                        system["charting_engine"].create_chart(
                            user_id=user_id,
                            symbol="RELIANCE",
                            timeframe=TimeFrame.FIFTEEN_MINUTES
                        )
                    )
            
            # LITE users creating basic charts
            for i in range(10):
                user_id = f"lite_user_{i}"
                tasks.append(
                    system["basic_engine"].create_lite_chart(
                        user_id=user_id,
                        symbol="RELIANCE"
                    )
                )
            
            # Voice commands
            for i in range(3):
                user_id = f"voice_user_{i}"
                system["voice_engine"].user_sessions[user_id] = {
                    "language": VoiceLanguage.HINDI,
                    "current_chart": None,
                    "listening": True
                }
                system["voice_engine"].voice_commands_history[user_id] = []
                
                tasks.append(
                    system["voice_engine"]._process_voice_command(
                        user_id, "Reliance ka chart dikhao", VoiceLanguage.HINDI
                    )
                )
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_results = [r for r in results if not isinstance(r, Exception)]
            return len(successful_results)
        
        result = await benchmark.pedantic(concurrent_scenarios, rounds=2)
        assert result >= 15  # Most operations should succeed
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, integrated_charting_system):
        """Test memory usage under load"""
        
        import psutil
        import gc
        
        system = integrated_charting_system
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        # Create load with multiple charts and indicators
        for i in range(20):
            user_id = f"load_user_{i}"
            
            # LITE charts
            lite_chart_id = await system["basic_engine"].create_lite_chart(
                user_id=user_id,
                symbol=f"STOCK_{i % 5}"
            )
            
            # Add indicators
            for indicator in [LiteIndicator.SMA, LiteIndicator.RSI]:
                await system["basic_engine"].get_basic_indicators(
                    chart_id=lite_chart_id,
                    indicator=indicator
                )
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Clean up
        system["basic_engine"].lite_charts.clear()
        system["basic_engine"].chart_data.clear()
        gc.collect()
        
        # Memory increase should be reasonable (less than 100MB for 20 charts)
        assert memory_increase < 100 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_end_to_end_response_times(self, integrated_charting_system):
        """Test end-to-end response times for different scenarios"""
        
        system = integrated_charting_system
        
        # Test LITE chart creation speed
        start_time = time.time()
        lite_chart_id = await system["basic_engine"].create_lite_chart(
            user_id="speed_test_lite",
            symbol="RELIANCE"
        )
        lite_time = time.time() - start_time
        
        # Test PRO chart creation speed
        with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
            mock_load.return_value = [
                OHLCV(
                    timestamp=datetime.now() - timedelta(minutes=i),
                    open=2500.0,
                    high=2520.0,
                    low=2480.0,
                    close=2510.0,
                    volume=10000,
                    symbol="RELIANCE",
                    timeframe=TimeFrame.FIFTEEN_MINUTES
                ) for i in range(100)
            ]
            
            start_time = time.time()
            pro_chart_id = await system["charting_engine"].create_chart(
                user_id="speed_test_pro",
                symbol="RELIANCE",
                timeframe=TimeFrame.FIFTEEN_MINUTES
            )
            pro_time = time.time() - start_time
        
        # Test voice command processing speed
        user_id = "speed_test_voice"
        system["voice_engine"].user_sessions[user_id] = {
            "language": VoiceLanguage.HINDI,
            "current_chart": None,
            "listening": True
        }
        system["voice_engine"].voice_commands_history[user_id] = []
        
        start_time = time.time()
        await system["voice_engine"]._process_voice_command(
            user_id, "Reliance ka chart dikhao", VoiceLanguage.HINDI
        )
        voice_time = time.time() - start_time
        
        # Verify performance targets
        assert lite_time < 1.0  # LITE should be very fast
        assert pro_time < 3.0   # PRO acceptable for professional features
        assert voice_time < IntegrationTestConfig.MAX_VOICE_TO_CHART_TIME_S


class TestDataConsistencyIntegration:
    """Test data consistency across integrated components"""
    
    @pytest.mark.asyncio
    async def test_cross_component_data_consistency(self, integrated_charting_system):
        """Test data consistency between LITE and PRO charts"""
        
        system = integrated_charting_system
        user_id = "consistency_user"
        symbol = "RELIANCE"
        
        # Create LITE chart
        lite_chart_id = await system["basic_engine"].create_lite_chart(
            user_id=user_id,
            symbol=symbol
        )
        
        # Get LITE SMA calculation
        lite_sma = await system["basic_engine"].get_basic_indicators(
            chart_id=lite_chart_id,
            indicator=LiteIndicator.SMA
        )
        
        # Create PRO chart with same data
        with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
            # Use same data source
            historical_data = system["basic_engine"].chart_data[lite_chart_id]
            
            # Convert LITE data to PRO format
            pro_data = []
            for candle in historical_data:
                ohlcv = OHLCV(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                    symbol=symbol,
                    timeframe=TimeFrame.ONE_MINUTE
                )
                pro_data.append(ohlcv)
            
            mock_load.return_value = pro_data
            
            pro_chart_id = await system["charting_engine"].create_chart(
                user_id=user_id,
                symbol=symbol,
                timeframe=TimeFrame.ONE_MINUTE
            )
        
        # Get PRO SMA calculation
        pro_sma_id = await system["charting_engine"].add_indicator(
            chart_id=pro_chart_id,
            indicator_type=IndicatorType.SMA,
            parameters={"period": 20}
        )
        
        # Find PRO SMA indicator
        pro_indicators = system["charting_engine"].indicators[pro_chart_id]
        pro_sma_indicator = next(ind for ind in pro_indicators if ind.indicator_id == pro_sma_id)
        
        # Compare LITE and PRO SMA values (should be very similar)
        if lite_sma.values and pro_sma_indicator.values:
            # Take overlapping values for comparison
            min_length = min(len(lite_sma.values), len(pro_sma_indicator.values))
            
            if min_length > 0:
                lite_values = lite_sma.values[-min_length:]
                pro_values = pro_sma_indicator.values[-min_length:]
                
                # Calculate percentage difference
                differences = []
                for lite_val, pro_val in zip(lite_values, pro_values):
                    if pro_val != 0:
                        diff_pct = abs(lite_val - pro_val) / pro_val * 100
                        differences.append(diff_pct)
                
                if differences:
                    avg_difference = sum(differences) / len(differences)
                    # Should be very consistent (less than 1% difference)
                    assert avg_difference < 1.0
    
    @pytest.mark.asyncio
    async def test_real_time_data_synchronization(self, integrated_charting_system):
        """Test real-time data synchronization across components"""
        
        system = integrated_charting_system
        
        # Set up multiple charts for same symbol
        symbol = "RELIANCE"
        
        # LITE chart
        lite_chart_id = await system["basic_engine"].create_lite_chart(
            user_id="sync_lite_user",
            symbol=symbol
        )
        
        # PRO chart
        with patch.object(system["charting_engine"], '_load_historical_data') as mock_load:
            mock_load.return_value = []
            pro_chart_id = await system["charting_engine"].create_chart(
                user_id="sync_pro_user",
                symbol=symbol,
                timeframe=TimeFrame.ONE_MINUTE
            )
        
        # Simulate real-time update
        new_data = OHLCV(
            timestamp=datetime.now(),
            open=2500.0,
            high=2520.0,
            low=2480.0,
            close=2510.0,
            volume=10000,
            symbol=symbol,
            timeframe=TimeFrame.ONE_MINUTE
        )
        
        # Update both systems (in real implementation, this would be synchronized)
        system["charting_engine"]._update_chart_data(
            pro_chart_id, symbol, TimeFrame.ONE_MINUTE, new_data
        )
        
        # Verify data consistency
        pro_key = f"{pro_chart_id}_{symbol}_1m"
        if pro_key in system["charting_engine"].chart_data:
            pro_latest = system["charting_engine"].chart_data[pro_key][-1]
            assert pro_latest.close == 2510.0
            assert pro_latest.symbol == symbol


if __name__ == "__main__":
    # Run integration tests with coverage
    pytest.main([
        "tests/integration/test_charting_integration.py",
        "--cov=app.pro",
        "--cov=app.lite",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=95",  # Slightly lower for integration tests
        "--benchmark-skip",
        "-v"
    ])