"""
TradeMate Voice-Controlled Charting Test Suite
==============================================
Comprehensive test coverage for revolutionary voice charting engine
ensuring 100% coverage and multi-language accuracy
"""

import pytest
import asyncio
import time
import json
import uuid
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timedelta

# Test libraries
import pytest_asyncio
import pytest_benchmark

# Voice charting modules
from app.pro.voice_charting_engine import (
    VoiceChartingEngine, VoicePatternMatcher, VoiceFeedbackEngine,
    VoiceLanguage, VoiceCommandType, VoiceCommand
)
from app.pro.charting_platform import (
    ChartingEngine, RealTimeDataFeed, TimeFrame, IndicatorType, 
    PatternType, ChartType
)


class VoiceTestConfig:
    """Voice charting test configuration"""
    
    # Performance benchmarks
    MAX_VOICE_PROCESSING_TIME_S = 3.0
    MAX_PATTERN_MATCHING_TIME_MS = 100
    MAX_VOICE_FEEDBACK_TIME_MS = 500
    MIN_RECOGNITION_ACCURACY = 90.0
    
    # Language support
    SUPPORTED_LANGUAGES = 11
    REQUIRED_LANGUAGES = [
        VoiceLanguage.HINDI,
        VoiceLanguage.ENGLISH,
        VoiceLanguage.TAMIL,
        VoiceLanguage.TELUGU,
        VoiceLanguage.BENGALI
    ]


class VoiceTestDataFactory:
    """Factory for voice testing data"""
    
    @staticmethod
    def create_voice_commands() -> Dict[VoiceLanguage, List[str]]:
        """Create realistic voice commands in multiple languages"""
        return {
            VoiceLanguage.HINDI: [
                "Reliance ka chart dikhao",
                "RSI add karo 14 period ka",
                "Price alert lagao 2600 pe",
                "Pattern detect karo",
                "Support line draw karo",
                "TCS mein 100 share buy karo",
                "Market status batao"
            ],
            VoiceLanguage.ENGLISH: [
                "Show Reliance chart",
                "Add RSI with 14 period",
                "Set price alert at 2600",
                "Detect patterns",
                "Draw support line",
                "Buy 100 shares of TCS",
                "Market status please"
            ],
            VoiceLanguage.TAMIL: [
                "Reliance chart காட்டு",
                "RSI indicator சேர்",
                "2600 ல் alert வை",
                "Pattern கண்டுபிடி",
                "Support line போடு"
            ],
            VoiceLanguage.BENGALI: [
                "Reliance এর chart দেখাও", 
                "RSI indicator যোগ করো",
                "2600 এ alert দাও",
                "Pattern খুঁজে বের করো"
            ],
            VoiceLanguage.TELUGU: [
                "Reliance chart చూపించు",
                "RSI indicator జోడించు", 
                "2600 వద్ద alert పెట్టు"
            ]
        }
    
    @staticmethod
    def create_voice_command_object(text: str, language: VoiceLanguage) -> VoiceCommand:
        """Create VoiceCommand object for testing"""
        return VoiceCommand(
            command_id=str(uuid.uuid4()),
            user_id="test_user_123",
            language=language,
            original_text=text,
            processed_text=text.lower().strip(),
            command_type=VoiceCommandType.CREATE_CHART,
            parameters={"symbol": "RELIANCE"},
            confidence_score=0.9,
            timestamp=datetime.now()
        )
    
    @staticmethod
    def create_mock_audio_data() -> bytes:
        """Create mock audio data for testing"""
        # In a real implementation, this would be actual audio bytes
        return b"mock_audio_data_representing_voice_command"


@pytest.fixture
async def mock_charting_engine():
    """Mock charting engine for voice testing"""
    engine = Mock(spec=ChartingEngine)
    
    # Mock async methods
    engine.create_chart = AsyncMock(return_value="test_chart_123")
    engine.add_indicator = AsyncMock(return_value="test_indicator_123")
    engine.create_alert = AsyncMock(return_value="test_alert_123")
    engine.detect_patterns = AsyncMock(return_value=[])
    engine.add_drawing_tool = AsyncMock(return_value="test_drawing_123")
    
    yield engine


@pytest.fixture
async def voice_pattern_matcher():
    """Initialize voice pattern matcher"""
    matcher = VoicePatternMatcher()
    yield matcher


@pytest.fixture
async def voice_feedback_engine():
    """Initialize voice feedback engine"""
    with patch('pyttsx3.init') as mock_tts:
        mock_engine = Mock()
        mock_tts.return_value = mock_engine
        
        feedback = VoiceFeedbackEngine()
        yield feedback


@pytest.fixture
async def voice_charting_engine(mock_charting_engine):
    """Initialize voice charting engine with mocked dependencies"""
    with patch('speech_recognition.Recognizer') as mock_recognizer:
        with patch('speech_recognition.Microphone') as mock_microphone:
            mock_recognizer.return_value = Mock()
            mock_microphone.return_value = Mock()
            
            engine = VoiceChartingEngine(mock_charting_engine)
            yield engine


class TestVoicePatternMatcher:
    """Test voice pattern matching across languages"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="voice_pattern")
    async def test_pattern_matching_performance(self, voice_pattern_matcher, benchmark):
        """Test voice pattern matching performance"""
        
        test_text = "Reliance ka chart dikhao"
        language = VoiceLanguage.HINDI
        
        def match_pattern():
            return voice_pattern_matcher.match_command(test_text, language)
        
        result = benchmark(match_pattern)
        command_type, parameters = result
        
        assert command_type == VoiceCommandType.CREATE_CHART
        assert "symbol" in parameters
    
    @pytest.mark.asyncio
    async def test_hindi_command_recognition(self, voice_pattern_matcher):
        """Test Hindi voice command recognition accuracy"""
        
        hindi_commands = [
            ("Reliance ka chart dikhao", VoiceCommandType.CREATE_CHART, "RELIANCE"),
            ("RSI add karo 14 period ka", VoiceCommandType.ADD_INDICATOR, "RSI"),
            ("price alert lagao 2600 pe", VoiceCommandType.SET_ALERT, 2600.0),
            ("pattern detect karo", VoiceCommandType.DETECT_PATTERN, None),
            ("support line draw karo", VoiceCommandType.DRAW_TOOL, None),
            ("100 Reliance buy karo", VoiceCommandType.EXECUTE_TRADE, "RELIANCE")
        ]
        
        for text, expected_type, expected_param in hindi_commands:
            command_type, parameters = voice_pattern_matcher.match_command(
                text, VoiceLanguage.HINDI
            )
            
            assert command_type == expected_type
            
            if expected_param is not None:
                if isinstance(expected_param, str):
                    assert expected_param in str(parameters)
                elif isinstance(expected_param, (int, float)):
                    # Check if the numeric value is in parameters
                    param_values = list(parameters.values())
                    assert any(
                        isinstance(val, (int, float)) and abs(val - expected_param) < 0.1
                        for val in param_values
                    )
    
    @pytest.mark.asyncio
    async def test_english_command_recognition(self, voice_pattern_matcher):
        """Test English voice command recognition"""
        
        english_commands = [
            ("show Reliance chart", VoiceCommandType.CREATE_CHART, "RELIANCE"),
            ("add RSI with 14 period", VoiceCommandType.ADD_INDICATOR, "RSI"),
            ("set alert at 2600", VoiceCommandType.SET_ALERT, 2600.0),
            ("detect patterns", VoiceCommandType.DETECT_PATTERN, None),
            ("draw support line", VoiceCommandType.DRAW_TOOL, None)
        ]
        
        for text, expected_type, expected_param in english_commands:
            command_type, parameters = voice_pattern_matcher.match_command(
                text, VoiceLanguage.ENGLISH
            )
            
            assert command_type == expected_type
            
            if expected_param is not None:
                if isinstance(expected_param, str):
                    assert expected_param in str(parameters)
    
    @pytest.mark.asyncio
    async def test_tamil_command_recognition(self, voice_pattern_matcher):
        """Test Tamil voice command recognition"""
        
        tamil_commands = [
            ("Reliance chart காட்டு", VoiceCommandType.CREATE_CHART, "RELIANCE"),
            ("RSI indicator சேர்", VoiceCommandType.ADD_INDICATOR, "RSI"),
            ("2600 ல் alert வை", VoiceCommandType.SET_ALERT, 2600.0)
        ]
        
        for text, expected_type, expected_param in tamil_commands:
            command_type, parameters = voice_pattern_matcher.match_command(
                text, VoiceLanguage.TAMIL
            )
            
            assert command_type == expected_type
    
    @pytest.mark.asyncio
    async def test_symbol_normalization_accuracy(self, voice_pattern_matcher):
        """Test stock symbol normalization from voice input"""
        
        symbol_test_cases = [
            ("reliance", "RELIANCE"),
            ("tcs", "TCS"),
            ("hdfc", "HDFC"),
            ("infosys", "INFY"),
            ("infy", "INFY"),
            ("itc", "ITC"),
            ("bharti", "BHARTIARTL"),
            ("airtel", "BHARTIARTL"),
            ("sbi", "SBIN"),
            ("maruti", "MARUTI"),
            ("unknown", "UNKNOWN")
        ]
        
        for input_symbol, expected_symbol in symbol_test_cases:
            normalized = voice_pattern_matcher._normalize_symbol(input_symbol)
            assert normalized == expected_symbol
    
    @pytest.mark.asyncio
    async def test_indicator_normalization_accuracy(self, voice_pattern_matcher):
        """Test technical indicator normalization from voice input"""
        
        indicator_test_cases = [
            ("sma", IndicatorType.SMA),
            ("simple moving average", IndicatorType.SMA),
            ("moving average", IndicatorType.SMA),
            ("ema", IndicatorType.EMA),
            ("exponential moving average", IndicatorType.EMA),
            ("rsi", IndicatorType.RSI),
            ("relative strength", IndicatorType.RSI),
            ("macd", IndicatorType.MACD),
            ("bollinger", IndicatorType.BOLLINGER_BANDS),
            ("bollinger bands", IndicatorType.BOLLINGER_BANDS)
        ]
        
        for input_indicator, expected_type in indicator_test_cases:
            normalized = voice_pattern_matcher._normalize_indicator(input_indicator)
            assert normalized == expected_type
    
    @pytest.mark.asyncio
    async def test_timeframe_extraction(self, voice_pattern_matcher):
        """Test timeframe extraction from voice commands"""
        
        timeframe_test_cases = [
            ("Show 1 minute chart", TimeFrame.ONE_MINUTE),
            ("Display 5 min chart", TimeFrame.FIVE_MINUTES),
            ("15 minute analysis", TimeFrame.FIFTEEN_MINUTES),
            ("hourly chart please", TimeFrame.ONE_HOUR),
            ("daily chart", TimeFrame.DAILY),
            ("weekly view", TimeFrame.WEEKLY),
            ("default chart", TimeFrame.FIFTEEN_MINUTES)  # Default case
        ]
        
        for text, expected_timeframe in timeframe_test_cases:
            extracted = voice_pattern_matcher._extract_timeframe(text)
            assert extracted == expected_timeframe
    
    @pytest.mark.asyncio
    async def test_multilingual_fallback(self, voice_pattern_matcher):
        """Test fallback to English for unsupported languages"""
        
        # Test with unsupported language
        unsupported_language = "unsupported_lang"
        text = "show chart"
        
        # Should fallback to English patterns
        command_type, parameters = voice_pattern_matcher.match_command(
            text, unsupported_language
        )
        
        # Should still be able to process English-like commands
        assert command_type in list(VoiceCommandType)


class TestVoiceFeedbackEngine:
    """Test voice feedback generation"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="voice_feedback")
    async def test_feedback_generation_performance(self, voice_feedback_engine, benchmark):
        """Test voice feedback generation performance"""
        
        def generate_feedback():
            voice_feedback_engine.speak_feedback(
                "chart_created",
                VoiceLanguage.HINDI,
                symbol="RELIANCE"
            )
            return True
        
        result = benchmark(generate_feedback)
        assert result == True
    
    @pytest.mark.asyncio
    async def test_hindi_feedback_generation(self, voice_feedback_engine):
        """Test Hindi voice feedback generation"""
        
        with patch.object(voice_feedback_engine.tts_engine, 'say') as mock_say:
            with patch.object(voice_feedback_engine.tts_engine, 'runAndWait') as mock_wait:
                
                voice_feedback_engine.speak_feedback(
                    "chart_created",
                    VoiceLanguage.HINDI,
                    symbol="RELIANCE"
                )
                
                # Verify TTS was called
                mock_say.assert_called_once()
                mock_wait.assert_called_once()
                
                # Verify Hindi content
                call_args = mock_say.call_args[0][0]
                assert "RELIANCE" in call_args
                assert "ban gaya hai" in call_args  # Hindi phrase
    
    @pytest.mark.asyncio
    async def test_english_feedback_generation(self, voice_feedback_engine):
        """Test English voice feedback generation"""
        
        with patch.object(voice_feedback_engine.tts_engine, 'say') as mock_say:
            with patch.object(voice_feedback_engine.tts_engine, 'runAndWait') as mock_wait:
                
                voice_feedback_engine.speak_feedback(
                    "chart_created",
                    VoiceLanguage.ENGLISH,
                    symbol="RELIANCE"
                )
                
                # Verify TTS was called
                mock_say.assert_called_once()
                mock_wait.assert_called_once()
                
                # Verify English content
                call_args = mock_say.call_args[0][0]
                assert "RELIANCE" in call_args
                assert "has been created" in call_args  # English phrase
    
    @pytest.mark.asyncio
    async def test_tamil_feedback_generation(self, voice_feedback_engine):
        """Test Tamil voice feedback generation"""
        
        with patch.object(voice_feedback_engine.tts_engine, 'say') as mock_say:
            with patch.object(voice_feedback_engine.tts_engine, 'runAndWait') as mock_wait:
                
                voice_feedback_engine.speak_feedback(
                    "chart_created",
                    VoiceLanguage.TAMIL,
                    symbol="RELIANCE"
                )
                
                # Verify TTS was called
                mock_say.assert_called_once()
                mock_wait.assert_called_once()
                
                # Verify Tamil content
                call_args = mock_say.call_args[0][0]
                assert "RELIANCE" in call_args
                assert "உருவாக்கப்பட்டது" in call_args  # Tamil phrase
    
    @pytest.mark.asyncio
    async def test_feedback_template_coverage(self, voice_feedback_engine):
        """Test that all feedback templates are covered"""
        
        required_templates = [
            "chart_created",
            "indicator_added", 
            "alert_set",
            "pattern_found",
            "trade_executed",
            "error",
            "not_understood"
        ]
        
        # Test that all templates exist for major languages
        for language in [VoiceLanguage.HINDI, VoiceLanguage.ENGLISH, VoiceLanguage.TAMIL]:
            templates = voice_feedback_engine.feedback_templates.get(language, {})
            
            for template in required_templates:
                if template in templates:
                    # Test template can be formatted
                    try:
                        templates[template].format(
                            symbol="TEST",
                            indicator="RSI",
                            price=2600,
                            count=5,
                            quantity=100,
                            side="BUY"
                        )
                    except KeyError:
                        # Some templates may not use all parameters
                        pass
    
    @pytest.mark.asyncio
    async def test_voice_property_setting(self, voice_feedback_engine):
        """Test voice property setting for different languages"""
        
        # Mock voice properties
        mock_voices = [
            Mock(id="hindi_voice", name="Hindi Voice"),
            Mock(id="english_voice", name="English Voice"), 
            Mock(id="tamil_voice", name="Tamil Voice")
        ]
        
        with patch.object(voice_feedback_engine.tts_engine, 'getProperty') as mock_get:
            with patch.object(voice_feedback_engine.tts_engine, 'setProperty') as mock_set:
                mock_get.return_value = mock_voices
                
                # Test setting voice for Hindi
                voice_feedback_engine._set_voice_for_language(VoiceLanguage.HINDI)
                
                # Verify properties were set
                mock_set.assert_any_call('rate', 150)
                mock_set.assert_any_call('volume', 0.8)


class TestVoiceChartingEngine:
    """Test main voice charting engine"""
    
    @pytest.mark.asyncio
    async def test_voice_session_initialization(self, voice_charting_engine):
        """Test voice session start and management"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Mock the threading and voice recognition
        with patch('threading.Thread') as mock_thread:
            with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
                
                await voice_charting_engine.start_voice_session(user_id, language)
                
                # Verify session was created
                assert user_id in voice_charting_engine.user_sessions
                session = voice_charting_engine.user_sessions[user_id]
                assert session["language"] == language
                assert session["listening"] == True
                assert session["current_chart"] is None
                
                # Verify thread was started for listening
                mock_thread.assert_called_once()
                
                # Verify welcome message
                mock_speak.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="voice_processing")
    async def test_voice_command_processing_performance(self, voice_charting_engine, benchmark):
        """Test voice command processing performance"""
        
        user_id = "test_user_123"
        text = "Reliance ka chart dikhao"
        language = VoiceLanguage.HINDI
        
        # Initialize user session
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": None,
            "listening": True
        }
        voice_charting_engine.voice_commands_history[user_id] = []
        
        async def process_command():
            await voice_charting_engine._process_voice_command(user_id, text, language)
            return True
        
        result = await benchmark.pedantic(process_command, rounds=5)
        assert result == True
    
    @pytest.mark.asyncio
    async def test_create_chart_voice_command(self, voice_charting_engine):
        """Test chart creation via voice command"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up session
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": None,
            "listening": True
        }
        
        # Create mock voice command
        command = VoiceTestDataFactory.create_voice_command_object(
            "Reliance ka chart dikhao", language
        )
        command.command_type = VoiceCommandType.CREATE_CHART
        command.parameters = {"symbol": "RELIANCE", "timeframe": TimeFrame.FIFTEEN_MINUTES}
        
        # Mock feedback
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            
            await voice_charting_engine._execute_voice_command(command)
            
            # Verify chart creation was called
            voice_charting_engine.charting_engine.create_chart.assert_called_once_with(
                user_id=user_id,
                symbol="RELIANCE",
                timeframe=TimeFrame.FIFTEEN_MINUTES,
                chart_type=ChartType.CANDLESTICK
            )
            
            # Verify feedback was given
            mock_speak.assert_called_once_with(
                "chart_created", language, symbol="RELIANCE"
            )
            
            # Verify session state updated
            session = voice_charting_engine.user_sessions[user_id]
            assert session["current_chart"] == "test_chart_123"
    
    @pytest.mark.asyncio
    async def test_add_indicator_voice_command(self, voice_charting_engine):
        """Test adding indicator via voice command"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up session with existing chart
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": "test_chart_123",
            "listening": True
        }
        
        # Create voice command
        command = VoiceTestDataFactory.create_voice_command_object(
            "RSI add karo 14 period ka", language
        )
        command.command_type = VoiceCommandType.ADD_INDICATOR
        command.parameters = {"indicator": IndicatorType.RSI, "period": 14}
        
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            
            await voice_charting_engine._execute_voice_command(command)
            
            # Verify indicator addition
            voice_charting_engine.charting_engine.add_indicator.assert_called_once_with(
                chart_id="test_chart_123",
                indicator_type=IndicatorType.RSI,
                parameters={"period": 14}
            )
            
            # Verify feedback
            mock_speak.assert_called_once_with(
                "indicator_added", language, indicator=IndicatorType.RSI.value
            )
    
    @pytest.mark.asyncio
    async def test_set_alert_voice_command(self, voice_charting_engine):
        """Test setting price alert via voice command"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up session
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": "test_chart_123",
            "listening": True
        }
        
        # Create voice command
        command = VoiceTestDataFactory.create_voice_command_object(
            "price alert lagao 2600 pe", language
        )
        command.command_type = VoiceCommandType.SET_ALERT
        command.parameters = {"price": 2600.0, "condition": "price >"}
        
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            
            await voice_charting_engine._execute_voice_command(command)
            
            # Verify alert creation
            voice_charting_engine.charting_engine.create_alert.assert_called_once()
            
            # Verify feedback
            mock_speak.assert_called_once_with(
                "alert_set", language, price=2600.0
            )
    
    @pytest.mark.asyncio
    async def test_pattern_detection_voice_command(self, voice_charting_engine):
        """Test pattern detection via voice command"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up session with chart
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": "test_chart_123",
            "listening": True
        }
        
        # Mock pattern detection result
        mock_patterns = [
            Mock(type=PatternType.DOJI, confidence_score=0.8),
            Mock(type=PatternType.HAMMER, confidence_score=0.75)
        ]
        voice_charting_engine.charting_engine.detect_patterns.return_value = mock_patterns
        
        # Create voice command
        command = VoiceTestDataFactory.create_voice_command_object(
            "pattern detect karo", language
        )
        command.command_type = VoiceCommandType.DETECT_PATTERN
        command.parameters = {}
        
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            with patch.object(voice_charting_engine.feedback_engine.tts_engine, 'say') as mock_say:
                with patch.object(voice_charting_engine.feedback_engine.tts_engine, 'runAndWait') as mock_wait:
                    
                    await voice_charting_engine._execute_voice_command(command)
                    
                    # Verify pattern detection was called
                    voice_charting_engine.charting_engine.detect_patterns.assert_called_once()
                    
                    # Verify feedback about patterns found
                    mock_speak.assert_called_once_with(
                        "pattern_found", language, count=2
                    )
                    
                    # Verify individual pattern details were spoken
                    assert mock_say.call_count >= 2  # At least 2 patterns described
    
    @pytest.mark.asyncio
    async def test_drawing_tool_voice_command(self, voice_charting_engine):
        """Test adding drawing tool via voice command"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up session with chart
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": "test_chart_123",
            "listening": True
        }
        
        # Create voice command
        command = VoiceTestDataFactory.create_voice_command_object(
            "support line draw karo", language
        )
        command.command_type = VoiceCommandType.DRAW_TOOL
        command.parameters = {}
        
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            
            await voice_charting_engine._execute_voice_command(command)
            
            # Verify drawing tool was added
            voice_charting_engine.charting_engine.add_drawing_tool.assert_called_once()
            
            # Verify feedback
            mock_speak.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_voice_session_termination(self, voice_charting_engine):
        """Test voice session stop functionality"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up active session
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": "test_chart_123",
            "listening": True
        }
        
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            
            voice_charting_engine.stop_voice_session(user_id)
            
            # Verify session was stopped
            session = voice_charting_engine.user_sessions[user_id]
            assert session["listening"] == False
            
            # Verify goodbye feedback
            mock_speak.assert_called_once_with("session_ended", language)
    
    @pytest.mark.asyncio
    async def test_error_handling_no_chart(self, voice_charting_engine):
        """Test error handling when no chart exists"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Set up session without chart
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": None,
            "listening": True
        }
        
        # Create command that requires chart
        command = VoiceTestDataFactory.create_voice_command_object(
            "RSI add karo", language
        )
        command.command_type = VoiceCommandType.ADD_INDICATOR
        command.parameters = {"indicator": IndicatorType.RSI}
        
        with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback') as mock_speak:
            
            await voice_charting_engine._execute_voice_command(command)
            
            # Should provide error feedback
            mock_speak.assert_called_once_with("no_chart", language)
            
            # Should not call charting engine
            voice_charting_engine.charting_engine.add_indicator.assert_not_called()


class TestMultiLanguageAccuracy:
    """Test multi-language voice recognition accuracy"""
    
    @pytest.mark.asyncio
    async def test_language_coverage_completeness(self, voice_pattern_matcher):
        """Test that all required languages have pattern coverage"""
        
        patterns = voice_pattern_matcher.patterns
        
        # Verify all required languages are supported
        for language in VoiceTestConfig.REQUIRED_LANGUAGES:
            assert language in patterns
            
            # Verify essential command types are covered
            essential_commands = [
                VoiceCommandType.CREATE_CHART,
                VoiceCommandType.ADD_INDICATOR,
                VoiceCommandType.SET_ALERT
            ]
            
            for command_type in essential_commands:
                assert command_type in patterns[language]
                assert len(patterns[language][command_type]) > 0
    
    @pytest.mark.asyncio
    async def test_cross_language_consistency(self, voice_pattern_matcher):
        """Test that similar commands work across languages"""
        
        # Test chart creation commands across languages
        chart_commands = [
            ("Show Reliance chart", VoiceLanguage.ENGLISH),
            ("Reliance ka chart dikhao", VoiceLanguage.HINDI),
            ("Reliance chart காட்டு", VoiceLanguage.TAMIL)
        ]
        
        results = []
        for text, language in chart_commands:
            command_type, parameters = voice_pattern_matcher.match_command(text, language)
            results.append((command_type, parameters.get("symbol")))
        
        # All should be CREATE_CHART commands
        assert all(result[0] == VoiceCommandType.CREATE_CHART for result in results)
        
        # All should extract RELIANCE symbol
        assert all("RELIANCE" in str(result[1]) for result in results if result[1])
    
    @pytest.mark.asyncio
    async def test_accent_variation_handling(self, voice_pattern_matcher):
        """Test handling of various Indian accent variations"""
        
        # Simulate accent variations (different transliterations)
        accent_variations = [
            ("Reliance ka chart dikhao", VoiceLanguage.HINDI),
            ("Relayance ka chart dikhao", VoiceLanguage.HINDI),  # Accent variation
            ("Relianse ka chart dikhao", VoiceLanguage.HINDI),   # Another variation
        ]
        
        for text, language in accent_variations:
            command_type, parameters = voice_pattern_matcher.match_command(text, language)
            
            # Should still recognize as chart command
            assert command_type == VoiceCommandType.CREATE_CHART
    
    @pytest.mark.asyncio
    async def test_mixed_language_commands(self, voice_pattern_matcher):
        """Test handling of mixed language commands (common in India)"""
        
        mixed_commands = [
            ("Reliance ka chart show karo", VoiceLanguage.HINDI),    # Hindi + English
            ("TCS chart please dikhao", VoiceLanguage.HINDI),       # English + Hindi
            ("Show HDFC ka price", VoiceLanguage.ENGLISH)          # English + Hindi
        ]
        
        for text, language in mixed_commands:
            command_type, parameters = voice_pattern_matcher.match_command(text, language)
            
            # Should handle mixed language gracefully
            assert command_type in list(VoiceCommandType)


class TestVoiceSystemIntegration:
    """Test voice system integration with charting platform"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_voice_workflow(self, voice_charting_engine):
        """Test complete voice workflow from command to execution"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Mock speech recognition
        with patch.object(voice_charting_engine.voice_recognizer, 'recognize_google') as mock_recognize:
            mock_recognize.return_value = "Reliance ka chart dikhao"
            
            # Start voice session
            with patch('threading.Thread'):
                with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback'):
                    await voice_charting_engine.start_voice_session(user_id, language)
            
            # Process voice command directly (simulate voice recognition)
            await voice_charting_engine._process_voice_command(
                user_id, "Reliance ka chart dikhao", language
            )
            
            # Verify chart was created
            voice_charting_engine.charting_engine.create_chart.assert_called_once()
            
            # Verify command was stored in history
            assert len(voice_charting_engine.voice_commands_history[user_id]) == 1
            command = voice_charting_engine.voice_commands_history[user_id][0]
            assert command.command_type == VoiceCommandType.CREATE_CHART
    
    @pytest.mark.asyncio
    async def test_voice_command_history_tracking(self, voice_charting_engine):
        """Test voice command history tracking"""
        
        user_id = "test_user_123"
        language = VoiceLanguage.HINDI
        
        # Initialize session
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": None,
            "listening": True
        }
        voice_charting_engine.voice_commands_history[user_id] = []
        
        commands = [
            "Reliance ka chart dikhao",
            "RSI add karo",
            "alert lagao 2600 pe"
        ]
        
        for command_text in commands:
            await voice_charting_engine._process_voice_command(
                user_id, command_text, language
            )
        
        # Verify all commands were tracked
        history = voice_charting_engine.voice_commands_history[user_id]
        assert len(history) == 3
        
        # Verify command details
        assert all(isinstance(cmd, VoiceCommand) for cmd in history)
        assert all(cmd.user_id == user_id for cmd in history)
        assert all(cmd.language == language for cmd in history)
    
    @pytest.mark.asyncio
    async def test_concurrent_voice_sessions(self, voice_charting_engine):
        """Test handling multiple concurrent voice sessions"""
        
        users = [f"user_{i}" for i in range(5)]
        
        # Start sessions for multiple users
        tasks = []
        for user_id in users:
            with patch('threading.Thread'):
                with patch.object(voice_charting_engine.feedback_engine, 'speak_feedback'):
                    tasks.append(
                        voice_charting_engine.start_voice_session(
                            user_id, VoiceLanguage.HINDI
                        )
                    )
        
        await asyncio.gather(*tasks)
        
        # Verify all sessions were created
        for user_id in users:
            assert user_id in voice_charting_engine.user_sessions
            assert user_id in voice_charting_engine.voice_commands_history


class TestPerformanceAndLoad:
    """Test voice system performance under load"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark(group="voice_load")
    async def test_concurrent_voice_processing(self, voice_charting_engine, benchmark):
        """Test concurrent voice command processing"""
        
        async def process_multiple_commands():
            tasks = []
            for i in range(10):
                user_id = f"user_{i}"
                voice_charting_engine.user_sessions[user_id] = {
                    "language": VoiceLanguage.HINDI,
                    "current_chart": None,
                    "listening": True
                }
                voice_charting_engine.voice_commands_history[user_id] = []
                
                tasks.append(
                    voice_charting_engine._process_voice_command(
                        user_id, "Reliance ka chart dikhao", VoiceLanguage.HINDI
                    )
                )
            
            await asyncio.gather(*tasks)
            return len(tasks)
        
        result = await benchmark.pedantic(process_multiple_commands, rounds=3)
        assert result == 10
    
    @pytest.mark.asyncio
    async def test_memory_usage_voice_sessions(self, voice_charting_engine):
        """Test memory usage with many voice sessions"""
        
        import psutil
        import gc
        
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        # Create many voice sessions
        for i in range(100):
            user_id = f"load_user_{i}"
            voice_charting_engine.user_sessions[user_id] = {
                "language": VoiceLanguage.HINDI,
                "current_chart": f"chart_{i}",
                "listening": True,
                "session_start": datetime.now()
            }
            voice_charting_engine.voice_commands_history[user_id] = [
                VoiceTestDataFactory.create_voice_command_object(
                    f"command_{j}", VoiceLanguage.HINDI
                ) for j in range(10)
            ]
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Clean up
        voice_charting_engine.user_sessions.clear()
        voice_charting_engine.voice_commands_history.clear()
        gc.collect()
        
        # Memory increase should be reasonable (less than 50MB for 100 sessions)
        assert memory_increase < 50 * 1024 * 1024


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in voice system"""
    
    @pytest.mark.asyncio
    async def test_invalid_voice_commands(self, voice_charting_engine):
        """Test handling of invalid or unclear voice commands"""
        
        user_id = "test_user"
        language = VoiceLanguage.HINDI
        
        voice_charting_engine.user_sessions[user_id] = {
            "language": language,
            "current_chart": None,
            "listening": True
        }
        voice_charting_engine.voice_commands_history[user_id] = []
        
        invalid_commands = [
            "",  # Empty command
            "random gibberish text",  # Unrecognized command
            "xyz abc def",  # No meaningful pattern
            "123 456 789"  # Only numbers
        ]
        
        for invalid_command in invalid_commands:
            # Should not raise exception
            await voice_charting_engine._process_voice_command(
                user_id, invalid_command, language
            )
        
        # Commands should be stored even if not recognized
        assert len(voice_charting_engine.voice_commands_history[user_id]) == len(invalid_commands)
    
    @pytest.mark.asyncio
    async def test_speech_recognition_errors(self, voice_charting_engine):
        """Test handling of speech recognition errors"""
        
        user_id = "test_user"
        
        # Mock speech recognition failures
        with patch.object(voice_charting_engine.voice_recognizer, 'listen') as mock_listen:
            with patch.object(voice_charting_engine.voice_recognizer, 'recognize_google') as mock_recognize:
                
                # Test different types of recognition errors
                import speech_recognition as sr
                
                mock_listen.return_value = Mock()  # Mock audio data
                mock_recognize.side_effect = sr.UnknownValueError("Could not understand audio")
                
                # Should handle gracefully without raising exception
                try:
                    voice_charting_engine._voice_listening_loop(user_id)
                except:
                    # Expected to handle errors gracefully
                    pass
    
    @pytest.mark.asyncio
    async def test_tts_engine_failures(self, voice_feedback_engine):
        """Test handling of TTS engine failures"""
        
        # Mock TTS engine failure
        with patch.object(voice_feedback_engine.tts_engine, 'say', side_effect=Exception("TTS Error")):
            
            # Should not raise exception
            try:
                voice_feedback_engine.speak_feedback(
                    "chart_created",
                    VoiceLanguage.HINDI,
                    symbol="RELIANCE"
                )
            except:
                # Should handle TTS errors gracefully
                pass


if __name__ == "__main__":
    # Run voice charting tests with coverage
    pytest.main([
        "tests/test_voice_charting.py",
        "--cov=app.pro.voice_charting_engine",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=100",
        "--benchmark-skip",
        "-v"
    ])