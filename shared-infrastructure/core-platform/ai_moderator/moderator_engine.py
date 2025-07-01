"""
AI Moderator Engine
Intelligent moderation for WhatsApp trading groups with spam detection and call tracking
"""

import asyncio
import openai
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import hashlib
from decimal import Decimal
import nltk
from textblob import TextBlob

logger = logging.getLogger(__name__)


class MessageType(Enum):
    TRADING_CALL = "trading_call"
    MARKET_ANALYSIS = "market_analysis"
    SPAM = "spam"
    SOCIAL = "social"
    QUESTION = "question"
    PROMOTIONAL = "promotional"
    ADMIN = "admin"


class CallType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    OPTION_BUY = "option_buy"
    OPTION_SELL = "option_sell"
    FUTURE_LONG = "future_long"
    FUTURE_SHORT = "future_short"


class UrgencyLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class GroupMessage:
    """WhatsApp group message structure"""
    message_id: str
    user_id: str
    username: str
    content: str
    timestamp: datetime
    group_id: str
    reply_to: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    language: str = "english"


@dataclass
class TradingCall:
    """Parsed trading call structure"""
    call_id: str
    expert_id: str
    group_id: str
    symbol: str
    call_type: CallType
    entry_price: Optional[float]
    target_price: Optional[float]
    stop_loss: Optional[float]
    quantity: Optional[int]
    timeframe: Optional[str]
    rationale: Optional[str]
    confidence: float
    timestamp: datetime
    raw_message: str
    formatted_call: str
    risk_level: str = "medium"


@dataclass
class ModerationAction:
    """Moderation action taken by AI"""
    action_id: str
    message_id: str
    action_type: str  # delete, warn, highlight, format, escalate
    reason: str
    confidence: float
    auto_executed: bool
    human_review_required: bool
    timestamp: datetime


class SpamDetector:
    """Advanced spam and pump-dump detection"""
    
    def __init__(self):
        self.spam_patterns = {
            "pump_dump": [
                r"guaranteed profit",
                r"sure shot",
                r"100% profit",
                r"doubling money",
                r"secret tip",
                r"insider information"
            ],
            "promotional": [
                r"join my channel",
                r"paid calls",
                r"premium group",
                r"subscription",
                r"telegram\.me",
                r"t\.me"
            ],
            "scam": [
                r"recovery.*loss",
                r"get back.*money",
                r"investment.*scheme",
                r"mlm",
                r"pyramid"
            ],
            "excessive_repetition": [],  # Will be dynamically filled
            "fake_urgency": [
                r"hurry.*limited",
                r"only.*left",
                r"last chance",
                r"expires.*today"
            ]
        }
        
        self.suspicious_keywords = [
            "jackpot", "lottery", "winner", "selected", "congratulations",
            "bitcoin", "crypto", "forex", "binary", "recovery"
        ]
        
        # User behavior tracking
        self.user_message_history = {}
        self.user_spam_scores = {}
    
    async def analyze_message(self, message: GroupMessage) -> Dict[str, Any]:
        """Comprehensive spam analysis"""
        
        spam_score = 0
        detected_patterns = []
        
        content_lower = message.content.lower()
        
        # Pattern-based detection
        for category, patterns in self.spam_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    spam_score += 0.3
                    detected_patterns.append(f"{category}: {pattern}")
        
        # Keyword-based detection
        keyword_count = sum(1 for keyword in self.suspicious_keywords if keyword in content_lower)
        spam_score += keyword_count * 0.2
        
        # User behavior analysis
        user_behavior_score = await self._analyze_user_behavior(message)
        spam_score += user_behavior_score
        
        # Repetition detection
        repetition_score = await self._detect_repetition(message)
        spam_score += repetition_score
        
        # Language analysis
        language_score = await self._analyze_language_quality(message)
        spam_score += language_score
        
        # URL analysis
        url_score = await self._analyze_urls(message)
        spam_score += url_score
        
        return {
            "spam_score": min(spam_score, 1.0),
            "is_spam": spam_score > 0.6,
            "detected_patterns": detected_patterns,
            "confidence": min(spam_score * 1.2, 1.0),
            "risk_level": self._get_risk_level(spam_score)
        }
    
    async def _analyze_user_behavior(self, message: GroupMessage) -> float:
        """Analyze user posting behavior patterns"""
        
        user_id = message.user_id
        current_time = message.timestamp
        
        # Initialize user history if not exists
        if user_id not in self.user_message_history:
            self.user_message_history[user_id] = []
        
        user_history = self.user_message_history[user_id]
        
        # Add current message
        user_history.append({
            "timestamp": current_time,
            "content": message.content,
            "group_id": message.group_id
        })
        
        # Keep only last 24 hours
        cutoff_time = current_time - timedelta(hours=24)
        user_history = [msg for msg in user_history if msg["timestamp"] > cutoff_time]
        self.user_message_history[user_id] = user_history
        
        behavior_score = 0
        
        # Check message frequency (red flag if >10 messages/hour)
        recent_messages = [msg for msg in user_history if msg["timestamp"] > current_time - timedelta(hours=1)]
        if len(recent_messages) > 10:
            behavior_score += 0.4
        
        # Check cross-group posting (same message in multiple groups)
        if len(user_history) > 1:
            current_content = message.content.lower()
            similar_messages = [
                msg for msg in user_history[-5:] 
                if self._similarity_score(current_content, msg["content"].lower()) > 0.8
            ]
            if len(similar_messages) > 2:
                behavior_score += 0.3
        
        # Check new user aggressive posting
        if len(user_history) < 5 and len(recent_messages) > 3:
            behavior_score += 0.2
        
        return behavior_score
    
    async def _detect_repetition(self, message: GroupMessage) -> float:
        """Detect repetitive content"""
        
        content = message.content.lower()
        repetition_score = 0
        
        # Character repetition (e.g., "!!!!!!")
        char_patterns = re.findall(r'(.)\1{4,}', content)
        repetition_score += len(char_patterns) * 0.1
        
        # Word repetition
        words = content.split()
        if len(words) > 3:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            max_freq = max(word_freq.values())
            if max_freq > 3:
                repetition_score += 0.2
        
        # Caps lock abuse
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.7 and len(content) > 10:
            repetition_score += 0.3
        
        return min(repetition_score, 0.5)
    
    async def _analyze_language_quality(self, message: GroupMessage) -> float:
        """Analyze language quality and coherence"""
        
        content = message.content
        quality_score = 0
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in content if not c.isalnum() and not c.isspace()) / max(len(content), 1)
        if special_char_ratio > 0.4:
            quality_score += 0.2
        
        # Check for coherence using TextBlob
        try:
            blob = TextBlob(content)
            if len(blob.sentences) > 0:
                # Very short or very long sentences can be suspicious
                avg_sentence_length = len(content.split()) / len(blob.sentences)
                if avg_sentence_length < 2 or avg_sentence_length > 50:
                    quality_score += 0.1
        except:
            quality_score += 0.1  # Parsing error usually indicates poor quality
        
        return min(quality_score, 0.3)
    
    async def _analyze_urls(self, message: GroupMessage) -> float:
        """Analyze URLs in the message"""
        
        content = message.content
        url_score = 0
        
        # Find URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        
        # Suspicious domains
        suspicious_domains = [
            "bit.ly", "tinyurl.com", "telegram.me", "t.me",
            "whatsapp.com", "wa.me", "short.link"
        ]
        
        for url in urls:
            # Check for URL shorteners (often used in spam)
            if any(domain in url for domain in suspicious_domains):
                url_score += 0.3
            
            # Multiple URLs in single message
            if len(urls) > 2:
                url_score += 0.2
        
        return min(url_score, 0.4)
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        
        # Simple Jaccard similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
    
    def _get_risk_level(self, spam_score: float) -> str:
        """Convert spam score to risk level"""
        
        if spam_score > 0.8:
            return "critical"
        elif spam_score > 0.6:
            return "high"
        elif spam_score > 0.4:
            return "medium"
        else:
            return "low"


class TradingCallParser:
    """Parse and structure trading calls from messages"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        
        # Common patterns for trading calls
        self.call_patterns = {
            "buy_patterns": [
                r"buy\s+([A-Z]+)",
                r"long\s+([A-Z]+)",
                r"([A-Z]+)\s+buy",
                r"go\s+long\s+([A-Z]+)"
            ],
            "sell_patterns": [
                r"sell\s+([A-Z]+)",
                r"short\s+([A-Z]+)",
                r"([A-Z]+)\s+sell",
                r"go\s+short\s+([A-Z]+)"
            ],
            "price_patterns": [
                r"@\s*₹?(\d+(?:\.\d+)?)",
                r"around\s+₹?(\d+(?:\.\d+)?)",
                r"price\s+₹?(\d+(?:\.\d+)?)",
                r"₹(\d+(?:\.\d+)?)"
            ],
            "target_patterns": [
                r"target\s+₹?(\d+(?:\.\d+)?)",
                r"tgt\s+₹?(\d+(?:\.\d+)?)",
                r"tp\s+₹?(\d+(?:\.\d+)?)"
            ],
            "stoploss_patterns": [
                r"sl\s+₹?(\d+(?:\.\d+)?)",
                r"stop\s*loss\s+₹?(\d+(?:\.\d+)?)",
                r"stoploss\s+₹?(\d+(?:\.\d+)?)"
            ]
        }
        
        # Indian stock symbols (would be loaded from database in production)
        self.indian_stocks = [
            "RELIANCE", "TCS", "INFY", "HDFC", "ICICI", "SBI", "ITC",
            "HDFCBANK", "BHARTIARTL", "LT", "ASIANPAINT", "MARUTI",
            "TITAN", "SUNPHARMA", "ULTRACEMCO", "ONGC", "TECHM",
            "NESTLEIND", "HCLTECH", "KOTAKBANK", "WIPRO", "ADANIPORTS"
        ]
    
    async def extract_trading_call(self, message: GroupMessage) -> Optional[TradingCall]:
        """Extract trading call from message"""
        
        content = message.content.upper()
        
        # Quick check for trading keywords
        trading_keywords = ["BUY", "SELL", "LONG", "SHORT", "TARGET", "ENTRY", "EXIT"]
        if not any(keyword in content for keyword in trading_keywords):
            return None
        
        # Extract components
        symbol = await self._extract_symbol(content)
        if not symbol:
            return None
        
        call_type = await self._extract_call_type(content)
        entry_price = await self._extract_price(content, "entry")
        target_price = await self._extract_price(content, "target")
        stop_loss = await self._extract_price(content, "stoploss")
        
        # Use AI for complex parsing if needed
        if not call_type or (not entry_price and not target_price):
            ai_parsed = await self._ai_parse_call(message.content)
            if ai_parsed:
                call_type = ai_parsed.get("call_type", call_type)
                entry_price = ai_parsed.get("entry_price", entry_price)
                target_price = ai_parsed.get("target_price", target_price)
                stop_loss = ai_parsed.get("stop_loss", stop_loss)
        
        if call_type:
            # Generate call ID
            call_id = hashlib.md5(f"{message.user_id}_{message.timestamp}_{symbol}".encode()).hexdigest()[:8]
            
            # Create formatted call
            formatted_call = await self._format_call(
                symbol, call_type, entry_price, target_price, stop_loss
            )
            
            return TradingCall(
                call_id=call_id,
                expert_id=message.user_id,
                group_id=message.group_id,
                symbol=symbol,
                call_type=call_type,
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                quantity=None,
                timeframe=await self._extract_timeframe(content),
                rationale=await self._extract_rationale(message.content),
                confidence=0.8,  # Would be calculated based on completeness
                timestamp=message.timestamp,
                raw_message=message.content,
                formatted_call=formatted_call
            )
        
        return None
    
    async def _extract_symbol(self, content: str) -> Optional[str]:
        """Extract stock symbol from content"""
        
        # Look for known Indian stocks
        for stock in self.indian_stocks:
            if stock in content:
                return stock
        
        # Look for NSE patterns
        nse_pattern = r'([A-Z]{2,10})\.NS'
        nse_match = re.search(nse_pattern, content)
        if nse_match:
            return nse_match.group(1)
        
        # Look for standalone symbols
        symbol_pattern = r'\b([A-Z]{2,8})\b'
        symbols = re.findall(symbol_pattern, content)
        
        # Filter to likely stock symbols (not common words)
        common_words = ["BUY", "SELL", "TARGET", "STOP", "LOSS", "PRICE", "NSE", "BSE"]
        for symbol in symbols:
            if symbol not in common_words and len(symbol) >= 3:
                return symbol
        
        return None
    
    async def _extract_call_type(self, content: str) -> Optional[CallType]:
        """Extract call type from content"""
        
        if any(pattern in content for pattern in ["BUY", "LONG", "GO LONG"]):
            if "OPTION" in content or "CALL" in content:
                return CallType.OPTION_BUY
            elif "FUTURE" in content or "FUT" in content:
                return CallType.FUTURE_LONG
            else:
                return CallType.BUY
        
        elif any(pattern in content for pattern in ["SELL", "SHORT", "GO SHORT"]):
            if "OPTION" in content or "PUT" in content:
                return CallType.OPTION_SELL
            elif "FUTURE" in content or "FUT" in content:
                return CallType.FUTURE_SHORT
            else:
                return CallType.SELL
        
        elif "HOLD" in content:
            return CallType.HOLD
        
        return None
    
    async def _extract_price(self, content: str, price_type: str) -> Optional[float]:
        """Extract price from content"""
        
        if price_type == "entry":
            patterns = self.call_patterns["price_patterns"]
        elif price_type == "target":
            patterns = self.call_patterns["target_patterns"]
        elif price_type == "stoploss":
            patterns = self.call_patterns["stoploss_patterns"]
        else:
            return None
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    async def _extract_timeframe(self, content: str) -> Optional[str]:
        """Extract timeframe from content"""
        
        timeframe_patterns = {
            "intraday": ["INTRADAY", "TODAY", "DAY TRADE"],
            "swing": ["SWING", "DAYS", "WEEK"],
            "positional": ["POSITIONAL", "MONTHS", "LONG TERM"]
        }
        
        content_upper = content.upper()
        
        for timeframe, patterns in timeframe_patterns.items():
            if any(pattern in content_upper for pattern in patterns):
                return timeframe
        
        return "intraday"  # Default
    
    async def _extract_rationale(self, content: str) -> Optional[str]:
        """Extract rationale/reasoning from content"""
        
        # Look for common rationale keywords
        rationale_keywords = ["BECAUSE", "DUE TO", "EXPECTING", "SUPPORT", "RESISTANCE", "BREAKOUT"]
        
        sentences = content.split('.')
        for sentence in sentences:
            if any(keyword in sentence.upper() for keyword in rationale_keywords):
                return sentence.strip()
        
        # If no explicit rationale, return None
        return None
    
    async def _ai_parse_call(self, content: str) -> Optional[Dict[str, Any]]:
        """Use AI to parse complex trading calls"""
        
        prompt = f"""
Parse this trading message and extract structured information:

Message: "{content}"

Extract:
1. Call type (buy/sell/hold)
2. Stock symbol
3. Entry price (if mentioned)
4. Target price (if mentioned)
5. Stop loss (if mentioned)

Return as JSON with keys: call_type, symbol, entry_price, target_price, stop_loss
If not found, use null.

Example: {{"call_type": "buy", "symbol": "TCS", "entry_price": 3900, "target_price": 4000, "stop_loss": 3850}}
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert call_type to enum
            if result.get("call_type"):
                call_type_map = {
                    "buy": CallType.BUY,
                    "sell": CallType.SELL,
                    "hold": CallType.HOLD
                }
                result["call_type"] = call_type_map.get(result["call_type"].lower())
            
            return result
            
        except Exception as e:
            logger.error(f"AI call parsing failed: {e}")
            return None
    
    async def _format_call(
        self, 
        symbol: str, 
        call_type: CallType, 
        entry_price: Optional[float],
        target_price: Optional[float], 
        stop_loss: Optional[float]
    ) -> str:
        """Format trading call for display"""
        
        formatted = f"🎯 TRADING CALL\n"
        formatted += f"📈 {symbol} - {call_type.value.upper()}"
        
        if entry_price:
            formatted += f" @ ₹{entry_price}"
        
        formatted += "\n"
        
        if target_price:
            formatted += f"🎯 Target: ₹{target_price}\n"
        
        if stop_loss:
            formatted += f"⛔ Stop Loss: ₹{stop_loss}\n"
        
        # Add risk warning
        formatted += "⚠️ Trade at your own risk"
        
        return formatted


class AIModerator:
    """Main AI Moderator class"""
    
    def __init__(self, group_config: Dict[str, Any]):
        self.group_id = group_config["group_id"]
        self.language = group_config.get("language", "english")
        self.moderation_level = group_config.get("moderation_level", "medium")
        
        self.spam_detector = SpamDetector()
        self.call_parser = TradingCallParser()
        
        # Moderation settings
        self.auto_delete_threshold = 0.8
        self.human_review_threshold = 0.6
        
        # Message tracking
        self.processed_messages = {}
        self.group_statistics = {
            "total_messages": 0,
            "spam_detected": 0,
            "calls_tracked": 0,
            "active_users": set()
        }
    
    async def process_message(self, message: GroupMessage) -> Dict[str, Any]:
        """Main message processing pipeline"""
        
        result = {
            "message_id": message.message_id,
            "processed": True,
            "actions": [],
            "moderation_required": False,
            "trading_call": None,
            "spam_analysis": None
        }
        
        try:
            # Update statistics
            self.group_statistics["total_messages"] += 1
            self.group_statistics["active_users"].add(message.user_id)
            
            # Step 1: Spam analysis
            spam_analysis = await self.spam_detector.analyze_message(message)
            result["spam_analysis"] = spam_analysis
            
            # Step 2: Handle spam
            if spam_analysis["is_spam"]:
                action = await self._handle_spam(message, spam_analysis)
                result["actions"].append(action)
                self.group_statistics["spam_detected"] += 1
                
                # If auto-deleted, don't process further
                if action.action_type == "delete":
                    return result
            
            # Step 3: Parse trading calls
            trading_call = await self.call_parser.extract_trading_call(message)
            if trading_call:
                result["trading_call"] = asdict(trading_call)
                action = await self._handle_trading_call(message, trading_call)
                result["actions"].append(action)
                self.group_statistics["calls_tracked"] += 1
            
            # Step 4: Enhance message if needed
            if not spam_analysis["is_spam"]:
                enhancement = await self._enhance_message(message)
                if enhancement:
                    result["actions"].append(enhancement)
            
            # Store processed message
            self.processed_messages[message.message_id] = {
                "timestamp": message.timestamp,
                "user_id": message.user_id,
                "spam_score": spam_analysis["spam_score"],
                "has_trading_call": trading_call is not None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            result["error"] = str(e)
            result["processed"] = False
            return result
    
    async def _handle_spam(self, message: GroupMessage, spam_analysis: Dict[str, Any]) -> ModerationAction:
        """Handle spam messages"""
        
        spam_score = spam_analysis["spam_score"]
        
        if spam_score >= self.auto_delete_threshold:
            # Auto-delete high-confidence spam
            action = ModerationAction(
                action_id=f"spam_{message.message_id}",
                message_id=message.message_id,
                action_type="delete",
                reason=f"Spam detected (score: {spam_score:.2f})",
                confidence=spam_analysis["confidence"],
                auto_executed=True,
                human_review_required=False,
                timestamp=datetime.now(timezone.utc)
            )
        
        elif spam_score >= self.human_review_threshold:
            # Flag for human review
            action = ModerationAction(
                action_id=f"review_{message.message_id}",
                message_id=message.message_id,
                action_type="flag_review",
                reason=f"Potential spam (score: {spam_score:.2f})",
                confidence=spam_analysis["confidence"],
                auto_executed=False,
                human_review_required=True,
                timestamp=datetime.now(timezone.utc)
            )
        
        else:
            # Low-confidence spam - just warn
            action = ModerationAction(
                action_id=f"warn_{message.message_id}",
                message_id=message.message_id,
                action_type="warn",
                reason=f"Low spam probability (score: {spam_score:.2f})",
                confidence=spam_analysis["confidence"],
                auto_executed=True,
                human_review_required=False,
                timestamp=datetime.now(timezone.utc)
            )
        
        return action
    
    async def _handle_trading_call(self, message: GroupMessage, trading_call: TradingCall) -> ModerationAction:
        """Handle trading call messages"""
        
        # Format and highlight the trading call
        action = ModerationAction(
            action_id=f"call_{trading_call.call_id}",
            message_id=message.message_id,
            action_type="highlight_call",
            reason="Trading call detected",
            confidence=trading_call.confidence,
            auto_executed=True,
            human_review_required=False,
            timestamp=datetime.now(timezone.utc)
        )
        
        return action
    
    async def _enhance_message(self, message: GroupMessage) -> Optional[ModerationAction]:
        """Enhance messages with additional context"""
        
        # Check if message needs market data enhancement
        if self._needs_market_data(message.content):
            action = ModerationAction(
                action_id=f"enhance_{message.message_id}",
                message_id=message.message_id,
                action_type="add_market_data",
                reason="Add real-time market data",
                confidence=0.9,
                auto_executed=True,
                human_review_required=False,
                timestamp=datetime.now(timezone.utc)
            )
            return action
        
        return None
    
    def _needs_market_data(self, content: str) -> bool:
        """Check if message needs market data enhancement"""
        
        # Simple check for stock symbols
        for stock in self.call_parser.indian_stocks:
            if stock in content.upper():
                return True
        
        return False
    
    async def get_group_analytics(self) -> Dict[str, Any]:
        """Get group performance analytics"""
        
        return {
            "group_id": self.group_id,
            "statistics": {
                **self.group_statistics,
                "active_users": len(self.group_statistics["active_users"]),
                "spam_rate": self.group_statistics["spam_detected"] / max(self.group_statistics["total_messages"], 1),
                "call_rate": self.group_statistics["calls_tracked"] / max(self.group_statistics["total_messages"], 1)
            },
            "recent_activity": await self._get_recent_activity(),
            "top_contributors": await self._get_top_contributors()
        }
    
    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent activity summary"""
        
        # In production, this would query the database
        return [
            {"type": "trading_call", "count": 5, "timeframe": "last_hour"},
            {"type": "spam_detected", "count": 2, "timeframe": "last_hour"},
            {"type": "messages", "count": 47, "timeframe": "last_hour"}
        ]
    
    async def _get_top_contributors(self) -> List[Dict[str, Any]]:
        """Get top contributing users"""
        
        # In production, this would analyze user contributions
        return [
            {"user_id": "expert_1", "calls": 12, "accuracy": 0.73},
            {"user_id": "expert_2", "calls": 8, "accuracy": 0.81},
            {"user_id": "expert_3", "calls": 6, "accuracy": 0.67}
        ]


class GroupManager:
    """Manages multiple groups and their configurations"""
    
    def __init__(self):
        self.active_groups = {}
        self.group_configs = {}
    
    async def create_group(self, group_config: Dict[str, Any]) -> AIModerator:
        """Create and configure a new group"""
        
        group_id = group_config["group_id"]
        
        # Validate configuration
        required_fields = ["group_id", "name", "max_members"]
        for field in required_fields:
            if field not in group_config:
                raise ValueError(f"Missing required field: {field}")
        
        # Create moderator instance
        moderator = AIModerator(group_config)
        
        # Store group
        self.active_groups[group_id] = moderator
        self.group_configs[group_id] = group_config
        
        logger.info(f"Created group {group_id} with {group_config.get('max_members', 50)} max members")
        
        return moderator
    
    async def get_group_moderator(self, group_id: str) -> Optional[AIModerator]:
        """Get moderator for a specific group"""
        
        return self.active_groups.get(group_id)
    
    async def get_network_analytics(self) -> Dict[str, Any]:
        """Get analytics across all groups"""
        
        total_groups = len(self.active_groups)
        total_messages = sum(
            moderator.group_statistics["total_messages"] 
            for moderator in self.active_groups.values()
        )
        total_spam = sum(
            moderator.group_statistics["spam_detected"] 
            for moderator in self.active_groups.values()
        )
        total_calls = sum(
            moderator.group_statistics["calls_tracked"] 
            for moderator in self.active_groups.values()
        )
        
        return {
            "network_summary": {
                "total_groups": total_groups,
                "total_messages": total_messages,
                "total_spam_detected": total_spam,
                "total_calls_tracked": total_calls,
                "spam_rate": total_spam / max(total_messages, 1),
                "call_rate": total_calls / max(total_messages, 1)
            },
            "top_performing_groups": await self._get_top_groups(),
            "network_health": await self._calculate_network_health()
        }
    
    async def _get_top_groups(self) -> List[Dict[str, Any]]:
        """Get top performing groups"""
        
        group_performance = []
        
        for group_id, moderator in self.active_groups.items():
            stats = moderator.group_statistics
            performance_score = (
                stats["calls_tracked"] * 2 +  # Trading calls are valuable
                stats["total_messages"] * 0.1 -  # Activity is good
                stats["spam_detected"] * 1  # Spam is bad
            )
            
            group_performance.append({
                "group_id": group_id,
                "name": self.group_configs[group_id].get("name", group_id),
                "performance_score": performance_score,
                "calls": stats["calls_tracked"],
                "messages": stats["total_messages"],
                "spam": stats["spam_detected"]
            })
        
        # Sort by performance score
        group_performance.sort(key=lambda x: x["performance_score"], reverse=True)
        
        return group_performance[:10]  # Top 10 groups
    
    async def _calculate_network_health(self) -> Dict[str, Any]:
        """Calculate overall network health metrics"""
        
        if not self.active_groups:
            return {"score": 0, "status": "no_groups"}
        
        # Calculate various health metrics
        avg_spam_rate = sum(
            moderator.group_statistics["spam_detected"] / max(moderator.group_statistics["total_messages"], 1)
            for moderator in self.active_groups.values()
        ) / len(self.active_groups)
        
        avg_activity = sum(
            len(moderator.group_statistics["active_users"])
            for moderator in self.active_groups.values()
        ) / len(self.active_groups)
        
        # Health score (0-100)
        health_score = min(100, max(0, 
            100 - (avg_spam_rate * 50) + (min(avg_activity, 20) * 2)
        ))
        
        if health_score > 80:
            status = "excellent"
        elif health_score > 60:
            status = "good"
        elif health_score > 40:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "score": round(health_score, 1),
            "status": status,
            "avg_spam_rate": round(avg_spam_rate * 100, 2),
            "avg_activity": round(avg_activity, 1)
        }