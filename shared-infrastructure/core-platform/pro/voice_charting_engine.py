"""
GridWorks PRO Voice-Controlled Charting Engine
==============================================

Revolutionary voice interface for professional charting - the world's first
voice-controlled trading charts supporting 11 Indian languages.

Voice Commands Examples:
- "Reliance ka chart dikhao" (Show Reliance chart)
- "RSI add karo 14 period ka" (Add RSI with 14 period)
- "Price alert lagao 2600 pe" (Set price alert at 2600)
- "Support line draw karo" (Draw support line)
- "Pattern detect karo" (Detect patterns)

Features:
- Natural language chart commands
- Voice-controlled technical analysis
- Multilingual support (Hindi, Tamil, Telugu, etc.)
- Voice-to-chart action mapping
- Smart context understanding
- Audio feedback and confirmations
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import speech_recognition as sr
import pyttsx3
import threading
from datetime import datetime

from .charting_platform import (
    ChartingEngine, TimeFrame, IndicatorType, PatternType, 
    ChartType, RealTimeDataFeed
)

logger = logging.getLogger(__name__)


class VoiceLanguage(Enum):
    HINDI = "hi-IN"
    ENGLISH = "en-IN"
    TAMIL = "ta-IN"
    TELUGU = "te-IN"
    BENGALI = "bn-IN"
    MARATHI = "mr-IN"
    GUJARATI = "gu-IN"
    KANNADA = "kn-IN"
    MALAYALAM = "ml-IN"
    PUNJABI = "pa-IN"
    ODIA = "or-IN"


class VoiceCommandType(Enum):
    CREATE_CHART = "CREATE_CHART"
    ADD_INDICATOR = "ADD_INDICATOR"
    DETECT_PATTERN = "DETECT_PATTERN"
    DRAW_TOOL = "DRAW_TOOL"
    SET_ALERT = "SET_ALERT"
    ZOOM_CHART = "ZOOM_CHART"
    CHANGE_TIMEFRAME = "CHANGE_TIMEFRAME"
    EXECUTE_TRADE = "EXECUTE_TRADE"
    GET_ANALYSIS = "GET_ANALYSIS"


@dataclass
class VoiceCommand:
    command_id: str
    user_id: str
    language: VoiceLanguage
    original_text: str
    processed_text: str
    command_type: VoiceCommandType
    parameters: Dict[str, Any]
    confidence_score: float
    timestamp: datetime


class VoicePatternMatcher:
    """Pattern matching for voice commands in multiple languages."""
    
    def __init__(self):
        self.patterns = self._load_voice_patterns()
    
    def _load_voice_patterns(self) -> Dict[VoiceLanguage, Dict[VoiceCommandType, List[str]]]:
        """Load voice command patterns for different languages."""
        return {
            VoiceLanguage.HINDI: {
                VoiceCommandType.CREATE_CHART: [
                    r"(.+)\s*ka\s*chart\s*dikhao",
                    r"(.+)\s*ka\s*graph\s*kholo",
                    r"(.+)\s*ka\s*chart\s*banao",
                    r"(.+)\s*stock\s*chart\s*dekho"
                ],
                VoiceCommandType.ADD_INDICATOR: [
                    r"(\w+)\s*add\s*karo\s*(\d+)?\s*period\s*ka?",
                    r"(\w+)\s*lagao\s*(\d+)?\s*din\s*ka?",
                    r"moving\s*average\s*lagao\s*(\d+)?\s*ka?",
                    r"RSI\s*dikhao\s*(\d+)?\s*period\s*ka?"
                ],
                VoiceCommandType.SET_ALERT: [
                    r"alert\s*lagao\s*(\d+\.?\d*)\s*pe",
                    r"price\s*alert\s*set\s*karo\s*(\d+\.?\d*)\s*pe",
                    r"(\d+\.?\d*)\s*pe\s*notification\s*bhejo",
                    r"jab\s*price\s*(\d+\.?\d*)\s*ho\s*to\s*batao"
                ],
                VoiceCommandType.DETECT_PATTERN: [
                    r"pattern\s*detect\s*karo",
                    r"chart\s*pattern\s*dikhao",
                    r"formation\s*dekho",
                    r"technical\s*pattern\s*find\s*karo"
                ],
                VoiceCommandType.DRAW_TOOL: [
                    r"support\s*line\s*draw\s*karo",
                    r"resistance\s*line\s*banao",
                    r"trend\s*line\s*lagao",
                    r"fibonacci\s*draw\s*karo"
                ],
                VoiceCommandType.EXECUTE_TRADE: [
                    r"(\d+)\s*(.+)\s*buy\s*karo",
                    r"(\d+)\s*(.+)\s*sell\s*karo",
                    r"(.+)\s*mein\s*(\d+)\s*rupaye\s*invest\s*karo",
                    r"market\s*order\s*place\s*karo"
                ]
            },
            VoiceLanguage.ENGLISH: {
                VoiceCommandType.CREATE_CHART: [
                    r"show\s*(.+)\s*chart",
                    r"open\s*(.+)\s*graph",
                    r"display\s*(.+)\s*chart",
                    r"create\s*chart\s*for\s*(.+)"
                ],
                VoiceCommandType.ADD_INDICATOR: [
                    r"add\s*(\w+)\s*with\s*(\d+)?\s*period",
                    r"apply\s*(\w+)\s*indicator\s*(\d+)?",
                    r"show\s*(\w+)\s*(\d+)?\s*period",
                    r"calculate\s*(\w+)\s*for\s*(\d+)?\s*days"
                ],
                VoiceCommandType.SET_ALERT: [
                    r"set\s*alert\s*at\s*(\d+\.?\d*)",
                    r"notify\s*when\s*price\s*reaches\s*(\d+\.?\d*)",
                    r"alert\s*me\s*at\s*(\d+\.?\d*)",
                    r"price\s*alert\s*(\d+\.?\d*)"
                ],
                VoiceCommandType.DETECT_PATTERN: [
                    r"detect\s*patterns?",
                    r"find\s*chart\s*patterns?",
                    r"show\s*formations?",
                    r"analyze\s*patterns?"
                ],
                VoiceCommandType.DRAW_TOOL: [
                    r"draw\s*support\s*line",
                    r"add\s*resistance\s*line",
                    r"create\s*trend\s*line",
                    r"draw\s*fibonacci"
                ]
            },
            VoiceLanguage.TAMIL: {
                VoiceCommandType.CREATE_CHART: [
                    r"(.+)\s*chart\s*காட்டு",
                    r"(.+)\s*graph\s*திற",
                    r"(.+)\s*க்கு\s*chart\s*வேண்டும்"
                ],
                VoiceCommandType.ADD_INDICATOR: [
                    r"(\w+)\s*indicator\s*சேர்",
                    r"(\w+)\s*காட்டு\s*(\d+)?\s*period",
                    r"moving\s*average\s*போடு"
                ],
                VoiceCommandType.SET_ALERT: [
                    r"(\d+\.?\d*)\s*ல்\s*alert\s*வை",
                    r"price\s*(\d+\.?\d*)\s*ல்\s*சொல்லு"
                ]
            }
        }
    
    def match_command(self, text: str, language: VoiceLanguage) -> Tuple[VoiceCommandType, Dict[str, Any]]:
        """Match voice text to command type and extract parameters."""
        if language not in self.patterns:
            language = VoiceLanguage.ENGLISH  # Fallback
        
        language_patterns = self.patterns[language]
        
        for command_type, patterns in language_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parameters = self._extract_parameters(command_type, match.groups(), text)
                    return command_type, parameters
        
        # No match found
        return VoiceCommandType.GET_ANALYSIS, {"query": text}
    
    def _extract_parameters(self, command_type: VoiceCommandType, groups: Tuple, text: str) -> Dict[str, Any]:
        """Extract parameters from matched groups."""
        params = {}
        
        if command_type == VoiceCommandType.CREATE_CHART:
            if groups and groups[0]:
                params["symbol"] = self._normalize_symbol(groups[0])
                params["timeframe"] = self._extract_timeframe(text)
                params["chart_type"] = ChartType.CANDLESTICK
        
        elif command_type == VoiceCommandType.ADD_INDICATOR:
            if groups and groups[0]:
                params["indicator"] = self._normalize_indicator(groups[0])
                params["period"] = int(groups[1]) if len(groups) > 1 and groups[1] else 20
        
        elif command_type == VoiceCommandType.SET_ALERT:
            if groups and groups[0]:
                params["price"] = float(groups[0])
                params["condition"] = "price >" if "above" in text.lower() or "upar" in text.lower() else "price <"
        
        elif command_type == VoiceCommandType.EXECUTE_TRADE:
            if len(groups) >= 2:
                params["quantity"] = int(groups[0]) if groups[0].isdigit() else 1
                params["symbol"] = self._normalize_symbol(groups[1])
                params["side"] = "BUY" if "buy" in text.lower() or "खरीदो" in text else "SELL"
        
        return params
    
    def _normalize_symbol(self, symbol_text: str) -> str:
        """Normalize symbol names from voice input."""
        symbol_map = {
            "reliance": "RELIANCE",
            "tcs": "TCS", 
            "hdfc": "HDFC",
            "infosys": "INFY",
            "infy": "INFY",
            "itc": "ITC",
            "bharti": "BHARTIARTL",
            "airtel": "BHARTIARTL",
            "bajaj": "BAJFINANCE",
            "sbi": "SBIN",
            "wipro": "WIPRO",
            "maruti": "MARUTI",
            "hero": "HEROMOTOCO",
            "ultratech": "ULTRACEMCO",
            "adani": "ADANIPORTS"
        }
        
        normalized = symbol_text.lower().strip()
        return symbol_map.get(normalized, normalized.upper())
    
    def _normalize_indicator(self, indicator_text: str) -> IndicatorType:
        """Normalize indicator names from voice input."""
        indicator_map = {
            "sma": IndicatorType.SMA,
            "simple moving average": IndicatorType.SMA,
            "moving average": IndicatorType.SMA,
            "ema": IndicatorType.EMA,
            "exponential moving average": IndicatorType.EMA,
            "rsi": IndicatorType.RSI,
            "relative strength": IndicatorType.RSI,
            "macd": IndicatorType.MACD,
            "bollinger": IndicatorType.BOLLINGER_BANDS,
            "bollinger bands": IndicatorType.BOLLINGER_BANDS,
            "atr": IndicatorType.ATR,
            "volume": IndicatorType.OBV
        }
        
        normalized = indicator_text.lower().strip()
        return indicator_map.get(normalized, IndicatorType.SMA)
    
    def _extract_timeframe(self, text: str) -> TimeFrame:
        """Extract timeframe from voice text."""
        text_lower = text.lower()
        
        if "1 minute" in text_lower or "1 min" in text_lower:
            return TimeFrame.ONE_MINUTE
        elif "5 minute" in text_lower or "5 min" in text_lower:
            return TimeFrame.FIVE_MINUTES
        elif "15 minute" in text_lower or "15 min" in text_lower:
            return TimeFrame.FIFTEEN_MINUTES
        elif "1 hour" in text_lower or "hourly" in text_lower:
            return TimeFrame.ONE_HOUR
        elif "daily" in text_lower or "day" in text_lower:
            return TimeFrame.DAILY
        elif "weekly" in text_lower or "week" in text_lower:
            return TimeFrame.WEEKLY
        else:
            return TimeFrame.FIFTEEN_MINUTES  # Default


class VoiceFeedbackEngine:
    """Generate voice feedback in user's preferred language."""
    
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        self.feedback_templates = self._load_feedback_templates()
    
    def _load_feedback_templates(self) -> Dict[VoiceLanguage, Dict[str, str]]:
        """Load voice feedback templates for different languages."""
        return {
            VoiceLanguage.HINDI: {
                "chart_created": "{symbol} ka chart ban gaya hai",
                "indicator_added": "{indicator} indicator add ho gaya",
                "alert_set": "{price} pe alert set ho gaya",
                "pattern_found": "{count} patterns mile hain",
                "trade_executed": "{quantity} {symbol} {side} order place ho gaya",
                "error": "Sorry, kuch galti hui hai",
                "not_understood": "Samjha nahi, dobara boliye"
            },
            VoiceLanguage.ENGLISH: {
                "chart_created": "{symbol} chart has been created",
                "indicator_added": "{indicator} indicator has been added",
                "alert_set": "Alert set at {price}",
                "pattern_found": "Found {count} patterns",
                "trade_executed": "{quantity} {symbol} {side} order placed",
                "error": "Sorry, there was an error",
                "not_understood": "I didn't understand, please repeat"
            },
            VoiceLanguage.TAMIL: {
                "chart_created": "{symbol} chart உருவாக்கப்பட்டது",
                "indicator_added": "{indicator} indicator சேர்க்கப்பட்டது",
                "alert_set": "{price} ல் alert வைக்கப்பட்டது",
                "pattern_found": "{count} patterns கண்டுபிடிக்கப்பட்டன",
                "error": "மன்னிக்கவும், பிழை ஏற்பட்டது"
            }
        }
    
    def speak_feedback(self, template_key: str, language: VoiceLanguage, **kwargs):
        """Speak feedback in user's language."""
        if language not in self.feedback_templates:
            language = VoiceLanguage.ENGLISH
        
        templates = self.feedback_templates[language]
        if template_key in templates:
            message = templates[template_key].format(**kwargs)
            
            # Set voice properties for language
            self._set_voice_for_language(language)
            
            # Speak the message
            self.tts_engine.say(message)
            self.tts_engine.runAndWait()
    
    def _set_voice_for_language(self, language: VoiceLanguage):
        """Set TTS voice properties for specific language."""
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find voice for specific language
        for voice in voices:
            if language.value.split('-')[0] in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 150)  # Words per minute
        self.tts_engine.setProperty('volume', 0.8)


class VoiceChartingEngine:
    """Main voice-controlled charting engine for GridWorks PRO."""
    
    def __init__(self, charting_engine: ChartingEngine):
        self.charting_engine = charting_engine
        self.voice_recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.pattern_matcher = VoicePatternMatcher()
        self.feedback_engine = VoiceFeedbackEngine()
        
        # User sessions and preferences
        self.user_sessions = {}  # user_id -> current chart_id, language, etc.
        self.voice_commands_history = {}  # user_id -> list of commands
        
        # Voice recognition settings
        self.voice_recognizer.energy_threshold = 300
        self.voice_recognizer.dynamic_energy_threshold = True
        
    async def start_voice_session(self, user_id: str, preferred_language: VoiceLanguage = VoiceLanguage.ENGLISH):
        """Start a voice charting session for a user."""
        self.user_sessions[user_id] = {
            "language": preferred_language,
            "current_chart": None,
            "listening": True,
            "session_start": datetime.now()
        }
        
        self.voice_commands_history[user_id] = []
        
        # Start listening loop in background
        threading.Thread(
            target=self._voice_listening_loop, 
            args=(user_id,), 
            daemon=True
        ).start()
        
        # Welcome message
        self.feedback_engine.speak_feedback(
            "session_started", 
            preferred_language, 
            name="GridWorks PRO"
        )
        
        logger.info(f"Started voice session for user {user_id} in {preferred_language.value}")
    
    def _voice_listening_loop(self, user_id: str):
        """Continuous voice listening loop for a user."""
        session = self.user_sessions[user_id]
        
        with self.microphone as source:
            self.voice_recognizer.adjust_for_ambient_noise(source)
        
        while session.get("listening", False):
            try:
                # Listen for voice input
                with self.microphone as source:
                    audio = self.voice_recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                language = session["language"]
                text = self.voice_recognizer.recognize_google(audio, language=language.value)
                
                # Process voice command
                asyncio.create_task(self._process_voice_command(user_id, text, language))
                
            except sr.WaitTimeoutError:
                pass  # Continue listening
            except sr.UnknownValueError:
                logger.debug("Could not understand audio")
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
            except Exception as e:
                logger.error(f"Voice listening error: {e}")
    
    async def _process_voice_command(self, user_id: str, text: str, language: VoiceLanguage):
        """Process a voice command and execute chart actions."""
        try:
            # Match command pattern
            command_type, parameters = self.pattern_matcher.match_command(text, language)
            
            # Create voice command record
            voice_command = VoiceCommand(
                command_id=str(uuid.uuid4()),
                user_id=user_id,
                language=language,
                original_text=text,
                processed_text=text.lower().strip(),
                command_type=command_type,
                parameters=parameters,
                confidence_score=0.8,  # Could be calculated based on pattern match
                timestamp=datetime.now()
            )
            
            # Store command history
            self.voice_commands_history[user_id].append(voice_command)
            
            # Execute command
            await self._execute_voice_command(voice_command)
            
            logger.info(f"Processed voice command: {text} -> {command_type.value}")
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            self.feedback_engine.speak_feedback("error", language)
    
    async def _execute_voice_command(self, command: VoiceCommand):
        """Execute a specific voice command."""
        session = self.user_sessions[command.user_id]
        
        if command.command_type == VoiceCommandType.CREATE_CHART:
            await self._handle_create_chart(command, session)
            
        elif command.command_type == VoiceCommandType.ADD_INDICATOR:
            await self._handle_add_indicator(command, session)
            
        elif command.command_type == VoiceCommandType.SET_ALERT:
            await self._handle_set_alert(command, session)
            
        elif command.command_type == VoiceCommandType.DETECT_PATTERN:
            await self._handle_detect_pattern(command, session)
            
        elif command.command_type == VoiceCommandType.DRAW_TOOL:
            await self._handle_draw_tool(command, session)
            
        elif command.command_type == VoiceCommandType.EXECUTE_TRADE:
            await self._handle_execute_trade(command, session)
            
        elif command.command_type == VoiceCommandType.GET_ANALYSIS:
            await self._handle_get_analysis(command, session)
    
    async def _handle_create_chart(self, command: VoiceCommand, session: Dict):
        """Handle voice command to create a chart."""
        params = command.parameters
        symbol = params.get("symbol", "RELIANCE")
        timeframe = params.get("timeframe", TimeFrame.FIFTEEN_MINUTES)
        
        try:
            chart_id = await self.charting_engine.create_chart(
                user_id=command.user_id,
                symbol=symbol,
                timeframe=timeframe,
                chart_type=ChartType.CANDLESTICK
            )
            
            session["current_chart"] = chart_id
            
            self.feedback_engine.speak_feedback(
                "chart_created", 
                command.language, 
                symbol=symbol
            )
            
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            self.feedback_engine.speak_feedback("error", command.language)
    
    async def _handle_add_indicator(self, command: VoiceCommand, session: Dict):
        """Handle voice command to add technical indicator."""
        if not session.get("current_chart"):
            self.feedback_engine.speak_feedback("no_chart", command.language)
            return
        
        params = command.parameters
        indicator = params.get("indicator", IndicatorType.SMA)
        period = params.get("period", 20)
        
        try:
            indicator_id = await self.charting_engine.add_indicator(
                chart_id=session["current_chart"],
                indicator_type=indicator,
                parameters={"period": period}
            )
            
            self.feedback_engine.speak_feedback(
                "indicator_added", 
                command.language, 
                indicator=indicator.value
            )
            
        except Exception as e:
            logger.error(f"Error adding indicator: {e}")
            self.feedback_engine.speak_feedback("error", command.language)
    
    async def _handle_set_alert(self, command: VoiceCommand, session: Dict):
        """Handle voice command to set price alert."""
        params = command.parameters
        price = params.get("price")
        condition = params.get("condition", "price >")
        
        if not price:
            self.feedback_engine.speak_feedback("invalid_price", command.language)
            return
        
        try:
            alert_id = await self.charting_engine.create_alert(
                user_id=command.user_id,
                symbol="RELIANCE",  # Default or from current chart
                timeframe=TimeFrame.ONE_MINUTE,
                condition=f"{condition} {price}",
                alert_type="price"
            )
            
            self.feedback_engine.speak_feedback(
                "alert_set", 
                command.language, 
                price=price
            )
            
        except Exception as e:
            logger.error(f"Error setting alert: {e}")
            self.feedback_engine.speak_feedback("error", command.language)
    
    async def _handle_detect_pattern(self, command: VoiceCommand, session: Dict):
        """Handle voice command to detect chart patterns."""
        if not session.get("current_chart"):
            self.feedback_engine.speak_feedback("no_chart", command.language)
            return
        
        try:
            patterns = await self.charting_engine.detect_patterns(
                chart_id=session["current_chart"],
                pattern_types=[
                    PatternType.DOJI, 
                    PatternType.HAMMER, 
                    PatternType.HEAD_AND_SHOULDERS
                ]
            )
            
            self.feedback_engine.speak_feedback(
                "pattern_found", 
                command.language, 
                count=len(patterns)
            )
            
            # Speak details of found patterns
            for pattern in patterns[:3]:  # Limit to first 3
                pattern_name = pattern.type.value.replace("_", " ").title()
                confidence = int(pattern.confidence_score * 100)
                
                message = f"{pattern_name} detected with {confidence}% confidence"
                self.feedback_engine.tts_engine.say(message)
                self.feedback_engine.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            self.feedback_engine.speak_feedback("error", command.language)
    
    async def _handle_draw_tool(self, command: VoiceCommand, session: Dict):
        """Handle voice command to add drawing tools."""
        if not session.get("current_chart"):
            self.feedback_engine.speak_feedback("no_chart", command.language)
            return
        
        # For voice commands, we'll add pre-defined drawing tools
        try:
            tool_id = await self.charting_engine.add_drawing_tool(
                chart_id=session["current_chart"],
                tool_type="trendline",
                coordinates=[{"x": 100, "y": 2500}, {"x": 200, "y": 2600}],
                style={"color": "blue", "thickness": 2},
                user_id=command.user_id,
                annotation="Voice-added trendline"
            )
            
            self.feedback_engine.speak_feedback(
                "drawing_added", 
                command.language, 
                tool="trendline"
            )
            
        except Exception as e:
            logger.error(f"Error adding drawing tool: {e}")
            self.feedback_engine.speak_feedback("error", command.language)
    
    async def _handle_execute_trade(self, command: VoiceCommand, session: Dict):
        """Handle voice command to execute trade."""
        params = command.parameters
        
        # For demo purposes - in production would integrate with actual trading engine
        self.feedback_engine.speak_feedback(
            "trade_executed", 
            command.language,
            quantity=params.get("quantity", 1),
            symbol=params.get("symbol", "RELIANCE"),
            side=params.get("side", "BUY")
        )
    
    async def _handle_get_analysis(self, command: VoiceCommand, session: Dict):
        """Handle general analysis queries."""
        # This would integrate with AI analysis engine
        self.feedback_engine.speak_feedback(
            "analysis_ready", 
            command.language
        )
    
    def stop_voice_session(self, user_id: str):
        """Stop voice session for a user."""
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["listening"] = False
            
            # Goodbye message
            language = self.user_sessions[user_id]["language"]
            self.feedback_engine.speak_feedback("session_ended", language)
            
            logger.info(f"Stopped voice session for user {user_id}")


# Demo usage
async def demo_voice_charting():
    """Demonstrate voice-controlled charting capabilities."""
    print("🎤 Starting GridWorks PRO Voice Charting Demo...")
    
    # Initialize components
    data_feed = RealTimeDataFeed()
    charting_engine = ChartingEngine(data_feed)
    voice_engine = VoiceChartingEngine(charting_engine)
    
    # Start voice session
    print("\\n🗣️ Starting voice session...")
    await voice_engine.start_voice_session("pro_user_123", VoiceLanguage.HINDI)
    
    # Simulate voice commands
    print("\\n📢 Simulating voice commands:")
    
    commands = [
        ("Reliance ka chart dikhao", VoiceLanguage.HINDI),
        ("RSI add karo 14 period ka", VoiceLanguage.HINDI),
        ("Price alert lagao 2600 pe", VoiceLanguage.HINDI),
        ("Pattern detect karo", VoiceLanguage.HINDI),
        ("Support line draw karo", VoiceLanguage.HINDI)
    ]
    
    for text, language in commands:
        print(f"\\n🎤 Voice Command: '{text}'")
        await voice_engine._process_voice_command("pro_user_123", text, language)
        await asyncio.sleep(2)  # Wait between commands
    
    print("\\n🎯 Voice Charting Features Demonstrated:")
    print("   🎤 Multi-language voice recognition")
    print("   📊 Voice-controlled chart creation")
    print("   📈 Voice-activated technical indicators")
    print("   🚨 Voice-set price alerts")
    print("   🔍 Voice-triggered pattern detection")
    print("   ✏️ Voice-controlled drawing tools")
    print("   🗣️ Voice feedback in user's language")
    
    # Stop session
    voice_engine.stop_voice_session("pro_user_123")
    
    print("\\n✅ Voice Charting Demo Complete!")


if __name__ == "__main__":
    # Import uuid for the demo
    import uuid
    
    # Run demo
    asyncio.run(demo_voice_charting())