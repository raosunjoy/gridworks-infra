#!/usr/bin/env python3
"""
GridWorks Options Strategy Builder
==================================
Interactive options strategy builder with voice commands and WhatsApp integration
"""

import asyncio
import json
import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import logging

from .gpt4_financial_coach import LanguageCode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptionType(Enum):
    """Option types"""
    CALL = "call"
    PUT = "put"


class OptionAction(Enum):
    """Option actions"""
    BUY = "buy"
    SELL = "sell"


class StrategyType(Enum):
    """Pre-defined options strategies"""
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    LONG_STRADDLE = "long_straddle"
    SHORT_STRADDLE = "short_straddle"
    IRON_BUTTERFLY = "iron_butterfly"
    COLLAR = "collar"
    LONG_STRANGLE = "long_strangle"


class MarketOutlook(Enum):
    """Market outlook for strategy selection"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    VOLATILE = "volatile"


@dataclass
class OptionLeg:
    """Individual option leg in a strategy"""
    option_type: OptionType
    action: OptionAction
    strike_price: float
    expiry_date: datetime
    quantity: int
    premium: float
    symbol: str
    
    @property
    def cost(self) -> float:
        """Calculate cost of this leg"""
        multiplier = 1 if self.action == OptionAction.BUY else -1
        return multiplier * self.premium * self.quantity


@dataclass
class OptionsStrategy:
    """Complete options strategy"""
    strategy_id: str
    strategy_type: StrategyType
    symbol: str
    legs: List[OptionLeg]
    market_outlook: MarketOutlook
    created_at: datetime
    user_id: str
    
    @property
    def net_premium(self) -> float:
        """Calculate net premium paid/received"""
        return sum(leg.cost for leg in self.legs)
    
    @property
    def max_profit(self) -> float:
        """Calculate maximum profit potential"""
        return self._calculate_payoff_at_expiry()["max_profit"]
    
    @property
    def max_loss(self) -> float:
        """Calculate maximum loss potential"""
        return self._calculate_payoff_at_expiry()["max_loss"]
    
    @property
    def breakeven_points(self) -> List[float]:
        """Calculate breakeven points"""
        return self._calculate_payoff_at_expiry()["breakeven_points"]
    
    def _calculate_payoff_at_expiry(self) -> Dict[str, Any]:
        """Calculate strategy payoff at expiry"""
        # Simplified payoff calculation
        # In real implementation, this would be more sophisticated
        
        if self.strategy_type == StrategyType.COVERED_CALL:
            call_leg = next(leg for leg in self.legs if leg.option_type == OptionType.CALL)
            max_profit = call_leg.premium * call_leg.quantity
            max_loss = float('inf')  # Unlimited downside from stock
            breakeven = call_leg.strike_price - call_leg.premium
            return {
                "max_profit": max_profit,
                "max_loss": max_loss,
                "breakeven_points": [breakeven]
            }
        
        elif self.strategy_type == StrategyType.PROTECTIVE_PUT:
            put_leg = next(leg for leg in self.legs if leg.option_type == OptionType.PUT)
            max_profit = float('inf')  # Unlimited upside from stock
            max_loss = put_leg.premium * put_leg.quantity
            breakeven = put_leg.strike_price + put_leg.premium
            return {
                "max_profit": max_profit,
                "max_loss": max_loss,
                "breakeven_points": [breakeven]
            }
        
        # Default calculation for complex strategies
        return {
            "max_profit": abs(self.net_premium),
            "max_loss": abs(self.net_premium),
            "breakeven_points": [self.legs[0].strike_price]
        }


@dataclass
class StrategyBuilderSession:
    """Interactive strategy building session"""
    session_id: str
    user_id: str
    current_step: str
    collected_data: Dict[str, Any]
    language: LanguageCode
    created_at: datetime
    last_activity: datetime


class VoicePatternMatcher:
    """Voice pattern matching for options commands"""
    
    STRATEGY_PATTERNS = {
        LanguageCode.ENGLISH: {
            StrategyType.COVERED_CALL: [
                r"covered call",
                r"sell call.*own stock",
                r"income.*strategy"
            ],
            StrategyType.PROTECTIVE_PUT: [
                r"protective put",
                r"insurance.*stock",
                r"hedge.*position"
            ],
            StrategyType.BULL_CALL_SPREAD: [
                r"bull call spread",
                r"bullish.*spread",
                r"limited.*upside"
            ]
        },
        LanguageCode.HINDI: {
            StrategyType.COVERED_CALL: [
                r"covered call",
                r"call bech.*stock.*paas",
                r"income.*strategy"
            ],
            StrategyType.PROTECTIVE_PUT: [
                r"protective put",
                r"stock.*bima",
                r"hedge.*karna"
            ]
        }
    }
    
    MARKET_OUTLOOK_PATTERNS = {
        LanguageCode.ENGLISH: {
            MarketOutlook.BULLISH: [r"bullish", r"going up", r"rise", r"increase"],
            MarketOutlook.BEARISH: [r"bearish", r"going down", r"fall", r"decrease"],
            MarketOutlook.NEUTRAL: [r"neutral", r"sideways", r"range bound"],
            MarketOutlook.VOLATILE: [r"volatile", r"big moves", r"uncertain"]
        },
        LanguageCode.HINDI: {
            MarketOutlook.BULLISH: [r"bullish", r"upar.*jayega", r"badhega"],
            MarketOutlook.BEARISH: [r"bearish", r"niche.*jayega", r"giregi"],
            MarketOutlook.NEUTRAL: [r"neutral", r"stable", r"same"],
            MarketOutlook.VOLATILE: [r"volatile", r"uncertain", r"pata.*nahi"]
        }
    }
    
    @classmethod
    def match_strategy(cls, text: str, language: LanguageCode) -> Optional[StrategyType]:
        """Match voice input to strategy type"""
        
        text_lower = text.lower()
        patterns = cls.STRATEGY_PATTERNS.get(language, {})
        
        for strategy_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in text_lower:
                    return strategy_type
        
        return None
    
    @classmethod
    def match_market_outlook(cls, text: str, language: LanguageCode) -> Optional[MarketOutlook]:
        """Match voice input to market outlook"""
        
        text_lower = text.lower()
        patterns = cls.MARKET_OUTLOOK_PATTERNS.get(language, {})
        
        for outlook, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in text_lower:
                    return outlook
        
        return None


class OptionsStrategyTemplates:
    """Pre-defined strategy templates"""
    
    @staticmethod
    def get_strategy_info(strategy_type: StrategyType, language: LanguageCode) -> Dict[str, str]:
        """Get strategy information in multiple languages"""
        
        strategy_info = {
            StrategyType.COVERED_CALL: {
                LanguageCode.ENGLISH: {
                    "name": "Covered Call",
                    "description": "Sell call options against stocks you own to generate income",
                    "market_view": "Neutral to slightly bullish",
                    "max_profit": "Call premium received",
                    "max_loss": "Unlimited (if stock falls)",
                    "best_for": "Income generation from existing stock holdings"
                },
                LanguageCode.HINDI: {
                    "name": "कवर्ड कॉल",
                    "description": "अपने शेयरों के खिलाफ कॉल ऑप्शन बेचकर आय उत्पन्न करें",
                    "market_view": "न्यूट्रल से हल्का बुलिश",
                    "max_profit": "कॉल प्रीमियम प्राप्त",
                    "max_loss": "असीमित (यदि शेयर गिरे)",
                    "best_for": "मौजूदा शेयर होल्डिंग से आय"
                }
            },
            StrategyType.PROTECTIVE_PUT: {
                LanguageCode.ENGLISH: {
                    "name": "Protective Put",
                    "description": "Buy put options to protect your stock investments",
                    "market_view": "Bullish but want downside protection",
                    "max_profit": "Unlimited (minus put premium)",
                    "max_loss": "Put premium paid",
                    "best_for": "Portfolio insurance"
                },
                LanguageCode.HINDI: {
                    "name": "प्रोटेक्टिव पुट",
                    "description": "अपने शेयर निवेश की सुरक्षा के लिए पुट ऑप्शन खरीदें",
                    "market_view": "बुलिश लेकिन नीचे की सुरक्षा चाहिए",
                    "max_profit": "असीमित (पुट प्रीमियम घटाकर)",
                    "max_loss": "पुट प्रीमियम भुगतान",
                    "best_for": "पोर्टफोलियो इंश्योरेंस"
                }
            }
        }
        
        return strategy_info.get(strategy_type, {}).get(
            language, 
            strategy_info.get(strategy_type, {}).get(LanguageCode.ENGLISH, {})
        )
    
    @staticmethod
    def create_covered_call_template(
        symbol: str, 
        stock_price: float, 
        call_strike: float, 
        call_premium: float,
        expiry_date: datetime,
        quantity: int = 100
    ) -> OptionsStrategy:
        """Create covered call strategy template"""
        
        call_leg = OptionLeg(
            option_type=OptionType.CALL,
            action=OptionAction.SELL,
            strike_price=call_strike,
            expiry_date=expiry_date,
            quantity=quantity,
            premium=call_premium,
            symbol=symbol
        )
        
        return OptionsStrategy(
            strategy_id=str(uuid.uuid4()),
            strategy_type=StrategyType.COVERED_CALL,
            symbol=symbol,
            legs=[call_leg],
            market_outlook=MarketOutlook.NEUTRAL,
            created_at=datetime.now(),
            user_id=""
        )
    
    @staticmethod
    def create_protective_put_template(
        symbol: str,
        stock_price: float,
        put_strike: float,
        put_premium: float,
        expiry_date: datetime,
        quantity: int = 100
    ) -> OptionsStrategy:
        """Create protective put strategy template"""
        
        put_leg = OptionLeg(
            option_type=OptionType.PUT,
            action=OptionAction.BUY,
            strike_price=put_strike,
            expiry_date=expiry_date,
            quantity=quantity,
            premium=put_premium,
            symbol=symbol
        )
        
        return OptionsStrategy(
            strategy_id=str(uuid.uuid4()),
            strategy_type=StrategyType.PROTECTIVE_PUT,
            symbol=symbol,
            legs=[put_leg],
            market_outlook=MarketOutlook.BULLISH,
            created_at=datetime.now(),
            user_id=""
        )


class OptionsStrategyBuilder:
    """Interactive options strategy builder"""
    
    def __init__(self):
        """Initialize the strategy builder"""
        self.active_sessions = {}
        self.strategy_templates = OptionsStrategyTemplates()
        self.voice_matcher = VoicePatternMatcher()
    
    async def start_strategy_session(
        self, 
        user_id: str, 
        language: LanguageCode = LanguageCode.ENGLISH
    ) -> Tuple[str, str]:
        """Start new strategy building session"""
        
        session_id = str(uuid.uuid4())
        
        session = StrategyBuilderSession(
            session_id=session_id,
            user_id=user_id,
            current_step="welcome",
            collected_data={},
            language=language,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        welcome_message = self._get_welcome_message(language)
        return session_id, welcome_message
    
    def _get_welcome_message(self, language: LanguageCode) -> str:
        """Get welcome message for strategy builder"""
        
        messages = {
            LanguageCode.ENGLISH: """*🎯 Options Strategy Builder*

I'll help you build the perfect options strategy based on your market outlook and goals.

*Popular Strategies:*
1️⃣ Covered Call - Generate income from stocks
2️⃣ Protective Put - Protect your portfolio
3️⃣ Bull Call Spread - Limited upside play
4️⃣ Bear Put Spread - Limited downside play

*Voice Commands:*
🎤 "I want a covered call strategy"
🎤 "Show me protective put"
🎤 "Market is bullish, suggest strategy"

Type a strategy name or describe your market view to get started!""",

            LanguageCode.HINDI: """*🎯 ऑप्शन्स स्ट्रैटेजी बिल्डर*

मैं आपके मार्केट आउटलुक और लक्ष्यों के आधार पर सही ऑप्शन्स स्ट्रैटेजी बनाने में मदद करूंगा।

*लोकप्रिय रणनीतियां:*
1️⃣ कवर्ड कॉल - शेयरों से आय जेनरेट करें
2️⃣ प्रोटेक्टिव पुट - अपने पोर्टफोलियो को सुरक्षित करें
3️⃣ बुल कॉल स्प्रेड - सीमित ऊपरी खेल
4️⃣ बियर पुट स्प्रेड - सीमित निचली खेल

*वॉयस कमांड्स:*
🎤 "मुझे covered call strategy चाहिए"
🎤 "Protective put दिखाओ"
🎤 "Market bullish है, strategy suggest करो"

शुरू करने के लिए स्ट्रैटेजी का नाम टाइप करें या अपना मार्केट व्यू बताएं!"""
        }
        
        return messages.get(language, messages[LanguageCode.ENGLISH])
    
    async def process_user_input(
        self, 
        session_id: str, 
        user_input: str
    ) -> Tuple[bool, str]:
        """Process user input in strategy building session"""
        
        if session_id not in self.active_sessions:
            return False, "Session not found. Please start a new strategy building session."
        
        session = self.active_sessions[session_id]
        session.last_activity = datetime.now()
        
        try:
            response = await self._handle_user_input(session, user_input)
            return True, response
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return False, "Sorry, I encountered an error. Please try again."
    
    async def _handle_user_input(
        self, 
        session: StrategyBuilderSession, 
        user_input: str
    ) -> str:
        """Handle user input based on current session step"""
        
        if session.current_step == "welcome":
            return await self._handle_strategy_selection(session, user_input)
        elif session.current_step == "strategy_selected":
            return await self._handle_symbol_input(session, user_input)
        elif session.current_step == "symbol_collected":
            return await self._handle_market_outlook(session, user_input)
        elif session.current_step == "outlook_collected":
            return await self._handle_parameters_input(session, user_input)
        elif session.current_step == "parameters_collected":
            return await self._generate_strategy(session, user_input)
        else:
            return "Session state error. Please start a new session."
    
    async def _handle_strategy_selection(
        self, 
        session: StrategyBuilderSession, 
        user_input: str
    ) -> str:
        """Handle strategy type selection"""
        
        # Try voice pattern matching first
        strategy_type = self.voice_matcher.match_strategy(user_input, session.language)
        
        if not strategy_type:
            # Try keyword matching
            user_input_lower = user_input.lower()
            if "covered call" in user_input_lower or "1" in user_input:
                strategy_type = StrategyType.COVERED_CALL
            elif "protective put" in user_input_lower or "2" in user_input:
                strategy_type = StrategyType.PROTECTIVE_PUT
            elif "bull call" in user_input_lower or "3" in user_input:
                strategy_type = StrategyType.BULL_CALL_SPREAD
            elif "bear put" in user_input_lower or "4" in user_input:
                strategy_type = StrategyType.BEAR_PUT_SPREAD
        
        if strategy_type:
            session.collected_data["strategy_type"] = strategy_type
            session.current_step = "strategy_selected"
            
            # Get strategy info
            strategy_info = self.strategy_templates.get_strategy_info(
                strategy_type, session.language
            )
            
            if session.language == LanguageCode.HINDI:
                return f"""*✅ रणनीति चुनी गई: {strategy_info['name']}*

*विवरण:* {strategy_info['description']}
*मार्केट व्यू:* {strategy_info['market_view']}
*अधिकतम लाभ:* {strategy_info['max_profit']}
*अधिकतम नुकसान:* {strategy_info['max_loss']}

अब बताएं कि आप किस शेयर के लिए यह रणनीति बनाना चाहते हैं?
उदाहरण: RELIANCE, TCS, HDFC"""
            else:
                return f"""*✅ Strategy Selected: {strategy_info['name']}*

*Description:* {strategy_info['description']}
*Market View:* {strategy_info['market_view']}
*Max Profit:* {strategy_info['max_profit']}
*Max Loss:* {strategy_info['max_loss']}

Now, which stock symbol would you like to build this strategy for?
Example: RELIANCE, TCS, HDFC"""
        
        else:
            if session.language == LanguageCode.HINDI:
                return """कृपया एक वैध रणनीति चुनें:

1️⃣ Covered Call
2️⃣ Protective Put  
3️⃣ Bull Call Spread
4️⃣ Bear Put Spread

या बताएं कि मार्केट के बारे में आपका क्या विचार है (bullish/bearish/neutral)"""
            else:
                return """Please select a valid strategy:

1️⃣ Covered Call
2️⃣ Protective Put
3️⃣ Bull Call Spread
4️⃣ Bear Put Spread

Or tell me your market outlook (bullish/bearish/neutral)"""
    
    async def _handle_symbol_input(
        self, 
        session: StrategyBuilderSession, 
        user_input: str
    ) -> str:
        """Handle stock symbol input"""
        
        # Normalize symbol
        symbol = user_input.strip().upper()
        
        # Validate symbol (simplified)
        valid_symbols = ["RELIANCE", "TCS", "HDFC", "INFY", "ITC", "SBIN", "ICICIBANK"]
        
        if symbol in valid_symbols or len(symbol) >= 3:
            session.collected_data["symbol"] = symbol
            session.current_step = "symbol_collected"
            
            if session.language == LanguageCode.HINDI:
                return f"""*✅ शेयर चुना गया: {symbol}*

अब बताएं कि {symbol} के लिए आपका मार्केट आउटलुक क्या है?

🎤 *वॉयस कमांड्स:*
• "Market bullish लग रहा है"
• "Bearish हो सकता है"
• "Neutral रहेगा"
• "Volatile होगा"

या टाइप करें: Bullish/Bearish/Neutral/Volatile"""
            else:
                return f"""*✅ Symbol Selected: {symbol}*

What's your market outlook for {symbol}?

🎤 *Voice Commands:*
• "Market looks bullish"
• "I think it's bearish"
• "Neutral outlook"
• "Expecting volatility"

Or type: Bullish/Bearish/Neutral/Volatile"""
        
        else:
            if session.language == LanguageCode.HINDI:
                return "कृपया एक वैध स्टॉक सिंबल डालें (जैसे: RELIANCE, TCS, HDFC)"
            else:
                return "Please enter a valid stock symbol (e.g., RELIANCE, TCS, HDFC)"
    
    async def _handle_market_outlook(
        self, 
        session: StrategyBuilderSession, 
        user_input: str
    ) -> str:
        """Handle market outlook input"""
        
        # Try voice pattern matching
        outlook = self.voice_matcher.match_market_outlook(user_input, session.language)
        
        if not outlook:
            # Try keyword matching
            user_input_lower = user_input.lower()
            if "bullish" in user_input_lower or "up" in user_input_lower:
                outlook = MarketOutlook.BULLISH
            elif "bearish" in user_input_lower or "down" in user_input_lower:
                outlook = MarketOutlook.BEARISH
            elif "neutral" in user_input_lower or "sideways" in user_input_lower:
                outlook = MarketOutlook.NEUTRAL
            elif "volatile" in user_input_lower or "uncertain" in user_input_lower:
                outlook = MarketOutlook.VOLATILE
        
        if outlook:
            session.collected_data["market_outlook"] = outlook
            session.current_step = "outlook_collected"
            
            # Generate strategy based on collected data
            return await self._generate_final_strategy(session)
        
        else:
            if session.language == LanguageCode.HINDI:
                return "कृपया अपना मार्केट आउटलुक बताएं: Bullish/Bearish/Neutral/Volatile"
            else:
                return "Please specify your market outlook: Bullish/Bearish/Neutral/Volatile"
    
    async def _generate_final_strategy(self, session: StrategyBuilderSession) -> str:
        """Generate and display final strategy"""
        
        strategy_type = session.collected_data["strategy_type"]
        symbol = session.collected_data["symbol"]
        outlook = session.collected_data["market_outlook"]
        
        # Get current market data (simplified - in real implementation, fetch from API)
        current_price = 2500  # Dummy price
        
        if strategy_type == StrategyType.COVERED_CALL:
            # Generate covered call strategy
            call_strike = current_price * 1.05  # 5% OTM
            call_premium = 50  # Dummy premium
            expiry_date = datetime.now() + timedelta(days=30)
            
            strategy = self.strategy_templates.create_covered_call_template(
                symbol=symbol,
                stock_price=current_price,
                call_strike=call_strike,
                call_premium=call_premium,
                expiry_date=expiry_date
            )
        
        elif strategy_type == StrategyType.PROTECTIVE_PUT:
            # Generate protective put strategy
            put_strike = current_price * 0.95  # 5% OTM
            put_premium = 40  # Dummy premium
            expiry_date = datetime.now() + timedelta(days=30)
            
            strategy = self.strategy_templates.create_protective_put_template(
                symbol=symbol,
                stock_price=current_price,
                put_strike=put_strike,
                put_premium=put_premium,
                expiry_date=expiry_date
            )
        
        else:
            # Default strategy
            strategy = self.strategy_templates.create_covered_call_template(
                symbol=symbol,
                stock_price=current_price,
                call_strike=current_price * 1.05,
                call_premium=50,
                expiry_date=datetime.now() + timedelta(days=30)
            )
        
        strategy.user_id = session.user_id
        
        # Format strategy display
        return self._format_strategy_display(strategy, session.language)
    
    def _format_strategy_display(
        self, 
        strategy: OptionsStrategy, 
        language: LanguageCode
    ) -> str:
        """Format strategy for WhatsApp display"""
        
        if language == LanguageCode.HINDI:
            template = f"""*🎯 आपकी ऑप्शन्स रणनीति तैयार है!*

*रणनीति:* {strategy.strategy_type.value.replace('_', ' ').title()}
*शेयर:* {strategy.symbol}
*कुल प्रीमियम:* ₹{abs(strategy.net_premium):,.0f}

*रणनीति विवरण:*"""
            
            for i, leg in enumerate(strategy.legs, 1):
                action_text = "खरीदें" if leg.action == OptionAction.BUY else "बेचें"
                option_text = "कॉल" if leg.option_type == OptionType.CALL else "पुट"
                template += f"""
{i}. {action_text} {leg.quantity} {option_text} @ ₹{leg.strike_price}
   प्रीमियम: ₹{leg.premium}"""
            
            template += f"""

*रिस्क रिवार्ड:*
• अधिकतम लाभ: ₹{strategy.max_profit:,.0f}
• अधिकतम नुकसान: ₹{abs(strategy.max_loss):,.0f}
• ब्रेकइवन: ₹{strategy.breakeven_points[0]:,.0f}

*⚠️ रिस्क डिस्क्लेमर:*
यह केवल शैक्षिक उद्देश्य के लिए है। ऑप्शन्स ट्रेडिंग में जोखिम है। निवेश से पहले सलाह लें।

क्या आप यह रणनीति execute करना चाहते हैं?"""
        
        else:
            template = f"""*🎯 Your Options Strategy is Ready!*

*Strategy:* {strategy.strategy_type.value.replace('_', ' ').title()}
*Symbol:* {strategy.symbol}
*Net Premium:* ₹{abs(strategy.net_premium):,.0f}

*Strategy Details:*"""
            
            for i, leg in enumerate(strategy.legs, 1):
                action_text = "Buy" if leg.action == OptionAction.BUY else "Sell"
                option_text = "Call" if leg.option_type == OptionType.CALL else "Put"
                template += f"""
{i}. {action_text} {leg.quantity} {option_text} @ ₹{leg.strike_price}
   Premium: ₹{leg.premium}"""
            
            template += f"""

*Risk Reward:*
• Max Profit: ₹{strategy.max_profit:,.0f}
• Max Loss: ₹{abs(strategy.max_loss):,.0f}
• Breakeven: ₹{strategy.breakeven_points[0]:,.0f}

*⚠️ Risk Disclaimer:*
This is for educational purposes only. Options trading involves risks. Please consult before investing.

Would you like to execute this strategy?"""
        
        return template
    
    async def get_strategy_education(
        self, 
        strategy_type: StrategyType, 
        language: LanguageCode
    ) -> str:
        """Get educational content about a strategy"""
        
        strategy_info = self.strategy_templates.get_strategy_info(strategy_type, language)
        
        if language == LanguageCode.HINDI:
            return f"""*📚 {strategy_info['name']} - शिक्षा*

*क्या है:* {strategy_info['description']}

*कब उपयोग करें:* {strategy_info['best_for']}

*मार्केट व्यू:* {strategy_info['market_view']}

*फायदे:*
• {strategy_info['max_profit']}
• नियंत्रित जोखिम

*नुकसान:*
• {strategy_info['max_loss']}
• सीमित अपसाइड

*⚠️ महत्वपूर्ण:*
यह एक शैक्षिक विवरण है। वास्तविक ट्रेडिंग से पहले विस्तृत अध्ययन और सलाह आवश्यक है।"""
        
        else:
            return f"""*📚 {strategy_info['name']} - Education*

*What it is:* {strategy_info['description']}

*When to use:* {strategy_info['best_for']}

*Market View:* {strategy_info['market_view']}

*Advantages:*
• {strategy_info['max_profit']}
• Controlled risk

*Disadvantages:*
• {strategy_info['max_loss']}
• Limited upside

*⚠️ Important:*
This is educational content. Detailed study and consultation required before actual trading."""


# Example usage
async def main():
    """Example usage of Options Strategy Builder"""
    
    builder = OptionsStrategyBuilder()
    
    # Start session
    session_id, welcome_msg = await builder.start_strategy_session("user123", LanguageCode.HINDI)
    print(f"Welcome: {welcome_msg}")
    
    # Simulate user interaction
    inputs = [
        "covered call strategy चाहिए",
        "RELIANCE",
        "bullish लग रहा है"
    ]
    
    for user_input in inputs:
        success, response = await builder.process_user_input(session_id, user_input)
        print(f"\nUser: {user_input}")
        print(f"Response: {response}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())