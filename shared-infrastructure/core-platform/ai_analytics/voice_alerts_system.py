#!/usr/bin/env python3
"""
GridWorks Voice Alerts System
============================
AI-powered voice alerts for chart patterns and market events in 11 Indian languages
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import time

# Import pattern detection system
from .chart_pattern_detection import PatternDetection, PatternType, ConfidenceLevel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of voice alerts"""
    PATTERN_DETECTED = "pattern_detected"
    PRICE_TARGET_HIT = "price_target_hit"
    BREAKOUT_ALERT = "breakout_alert"
    VOLUME_SPIKE = "volume_spike"
    TECHNICAL_SIGNAL = "technical_signal"
    RISK_WARNING = "risk_warning"
    PROFIT_BOOKING = "profit_booking"
    STOP_LOSS_HIT = "stop_loss_hit"


class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"     # Immediate action required
    HIGH = "high"            # Important but not urgent
    MEDIUM = "medium"        # Regular updates
    LOW = "low"             # Educational/FYI


class VoiceLanguage(Enum):
    """Supported voice languages"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


@dataclass
class VoiceAlert:
    """Voice alert data structure"""
    alert_id: str
    alert_type: AlertType
    priority: AlertPriority
    symbol: str
    language: VoiceLanguage
    message_template: str
    message_variables: Dict[str, Any]
    audio_url: Optional[str]
    created_at: datetime
    scheduled_at: Optional[datetime]
    delivered_at: Optional[datetime]
    user_id: str
    pattern_id: Optional[str] = None
    expiry_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    
    @property
    def final_message(self) -> str:
        """Generate final message with variables"""
        try:
            return self.message_template.format(**self.message_variables)
        except KeyError as e:
            logger.warning(f"Missing variable in alert template: {e}")
            return self.message_template
    
    @property
    def is_expired(self) -> bool:
        """Check if alert has expired"""
        return self.expiry_time and datetime.now() > self.expiry_time
    
    @property
    def should_retry(self) -> bool:
        """Check if alert should be retried"""
        return self.retry_count < self.max_retries and not self.is_expired


class VoiceAlertTemplates:
    """Multi-language voice alert templates"""
    
    PATTERN_ALERTS = {
        VoiceLanguage.ENGLISH: {
            PatternType.HEAD_AND_SHOULDERS: "Alert! {symbol} showing Head and Shoulders pattern with {confidence:.0%} confidence. Expected bearish move of {magnitude:.1%}. Consider profit booking or short position.",
            PatternType.DOUBLE_TOP: "Double Top pattern detected in {symbol} with {confidence:.0%} confidence. Resistance at ₹{resistance}. Target: ₹{target}.",
            PatternType.ASCENDING_TRIANGLE: "Bullish Ascending Triangle in {symbol}! Breakout expected above ₹{resistance}. Target: ₹{target}.",
            PatternType.HAMMER: "Hammer candlestick formed in {symbol} at ₹{current_price}. Potential reversal signal with {confidence:.0%} confidence.",
            PatternType.DOJI: "Doji pattern in {symbol} indicates market indecision. Watch for breakout direction from ₹{current_price}."
        },
        
        VoiceLanguage.HINDI: {
            PatternType.HEAD_AND_SHOULDERS: "अलर्ट! {symbol} में Head and Shoulders पैटर्न दिख रहा है {confidence:.0%} कॉन्फिडेंस के साथ। {magnitude:.1%} गिरावट की संभावना। प्रॉफिट बुकिंग या शॉर्ट पोजीशन पर विचार करें।",
            PatternType.DOUBLE_TOP: "{symbol} में Double Top पैटर्न मिला है {confidence:.0%} कॉन्फिडेंस के साथ। रेजिस्टेंस ₹{resistance} पर। टारगेट: ₹{target}।",
            PatternType.ASCENDING_TRIANGLE: "{symbol} में बुलिश Ascending Triangle! ₹{resistance} के ऊपर ब्रेकआउट की उम्मीद। टारगेट: ₹{target}।",
            PatternType.HAMMER: "{symbol} में ₹{current_price} पर Hammer कैंडलस्टिक बना है। {confidence:.0%} कॉन्फिडेंस के साथ रिवर्सल संकेत।",
            PatternType.DOJI: "{symbol} में Doji पैटर्न मार्केट की अनिश्चितता दर्शाता है। ₹{current_price} से ब्रेकआउट दिशा देखें।"
        },
        
        VoiceLanguage.TAMIL: {
            PatternType.HEAD_AND_SHOULDERS: "எச்சரிக்கை! {symbol} இல் Head and Shoulders பேட்டர்ன் {confidence:.0%} நம்பிக்கையுடன் காணப்படுகிறது। {magnitude:.1%} கீழ்நோக்கிய நகர்வு எதிர்பார்க்கப்படுகிறது।",
            PatternType.DOUBLE_TOP: "{symbol} இல் Double Top பேட்டர்ன் {confidence:.0%} நம்பிக்கையுடன் கண்டறியப்பட்டது। எதிர்ப்பு ₹{resistance}. இலக்கு: ₹{target}.",
            PatternType.ASCENDING_TRIANGLE: "{symbol} இல் ஏறுமுக Ascending Triangle! ₹{resistance} மேல் பிரேக்அவுட் எதிர்பார்க்கப்படுகிறது।",
            PatternType.HAMMER: "{symbol} இல் ₹{current_price} இல் Hammer கேண்டில்ஸ்டிக் உருவானது। {confidence:.0%} நம்பிக்கையுடன் திருப்பு சிக்னல்.",
            PatternType.DOJI: "{symbol} இல் Doji பேட்டர்ன் சந்தையின் குழப்பத்தைக் காட்டுகிறது।"
        },
        
        VoiceLanguage.TELUGU: {
            PatternType.HEAD_AND_SHOULDERS: "హెచ్చరిక! {symbol} లో Head and Shoulders పేట్టర్న్ {confidence:.0%} కాన్ఫిడెన్స్ తో కనిపిస్తుంది। {magnitude:.1%} తగ్గుదల అంచనా।",
            PatternType.DOUBLE_TOP: "{symbol} లో Double Top పేట్టర్న్ {confidence:.0%} కాన్ఫిడెన్స్ తో గుర్తించబడింది। రెసిస్టెన్స్ ₹{resistance}. టార్గెట్: ₹{target}.",
            PatternType.ASCENDING_TRIANGLE: "{symbol} లో బుల్లిష్ Ascending Triangle! ₹{resistance} పైన బ్రేక్అవుట్ ఆశించవచ్చు।",
            PatternType.HAMMER: "{symbol} లో ₹{current_price} వద్ద Hammer క్యాండిల్స్టిక్ ఏర్పడింది। {confidence:.0%} కాన్ఫిడెన్స్ తో రివర్సల్ సిగ్నల్.",
            PatternType.DOJI: "{symbol} లో Doji పేట్టర్న్ మార్కెట్ అనిశ్చితిని చూపిస్తుంది।"
        },
        
        VoiceLanguage.BENGALI: {
            PatternType.HEAD_AND_SHOULDERS: "সতর্কতা! {symbol} এ Head and Shoulders প্যাটার্ন {confidence:.0%} আত্মবিশ্বাসের সাথে দেখা যাচ্ছে। {magnitude:.1%} পতনের সম্ভাবনা।",
            PatternType.DOUBLE_TOP: "{symbol} এ Double Top প্যাটার্ন {confidence:.0%} আত্মবিশ্বাসের সাথে চিহ্নিত। রেজিস্ট্যান্স ₹{resistance}। লক্ষ্য: ₹{target}।",
            PatternType.ASCENDING_TRIANGLE: "{symbol} এ বুলিশ Ascending Triangle! ₹{resistance} এর উপরে ব্রেকআউট প্রত্যাশিত।",
            PatternType.HAMMER: "{symbol} এ ₹{current_price} এ Hammer ক্যান্ডেলস্টিক গঠিত। {confidence:.0%} আত্মবিশ্বাসের সাথে রিভার্সাল সিগন্যাল।",
            PatternType.DOJI: "{symbol} এ Doji প্যাটার্ন বাজারের অনিশ্চয়তা নির্দেশ করে।"
        }
    }
    
    PRICE_ALERTS = {
        VoiceLanguage.ENGLISH: {
            "target_hit": "{symbol} has reached your target price of ₹{target_price}. Current price: ₹{current_price}. Consider booking profits.",
            "stop_loss": "Stop loss triggered for {symbol} at ₹{stop_price}. Current price: ₹{current_price}. Position closed to limit losses.",
            "breakout": "Breakout alert! {symbol} has broken above resistance at ₹{resistance_price}. Current price: ₹{current_price}.",
            "breakdown": "Breakdown alert! {symbol} has fallen below support at ₹{support_price}. Current price: ₹{current_price}."
        },
        
        VoiceLanguage.HINDI: {
            "target_hit": "{symbol} आपके टारगेट प्राइस ₹{target_price} पर पहुँच गया है। मौजूदा कीमत: ₹{current_price}। प्रॉफिट बुकिंग पर विचार करें।",
            "stop_loss": "{symbol} के लिए ₹{stop_price} पर स्टॉप लॉस ट्रिगर हुआ। मौजूदा कीमत: ₹{current_price}। नुकसान सीमित करने के लिए पोजीशन बंद।",
            "breakout": "ब्रेकआउट अलर्ट! {symbol} ने ₹{resistance_price} रेजिस्टेंस को तोड़ दिया है। मौजूदा कीमत: ₹{current_price}।",
            "breakdown": "ब्रेकडाउन अलर्ट! {symbol} ₹{support_price} सपोर्ट के नीचे गिर गया है। मौजूदा कीमत: ₹{current_price}।"
        },
        
        VoiceLanguage.TAMIL: {
            "target_hit": "{symbol} உங்கள் இலக்கு விலை ₹{target_price} ஐ எட்டியுள்ளது। தற்போதைய விலை: ₹{current_price}. லாபம் பெறுவதைக் கருத்தில் கொள்ளுங்கள்।",
            "stop_loss": "{symbol} க்கு ₹{stop_price} இல் ஸ்டாப் லாஸ் தூண்டப்பட்டது। தற்போதைய விலை: ₹{current_price}।",
            "breakout": "பிரேக்அவுட் எச்சரிக்கை! {symbol} ₹{resistance_price} எதிர்ப்பை உடைத்துள்ளது।",
            "breakdown": "பிரேக்டவுன் எச்சரிக்கை! {symbol} ₹{support_price} ஆதரவின் கீழ் வீழ்ந்துள்ளது।"
        }
    }
    
    TECHNICAL_ALERTS = {
        VoiceLanguage.ENGLISH: {
            "rsi_overbought": "{symbol} RSI shows overbought at {rsi_value}. Consider profit booking or short opportunity.",
            "rsi_oversold": "{symbol} RSI shows oversold at {rsi_value}. Potential buying opportunity.",
            "macd_bullish": "MACD bullish crossover in {symbol}. Momentum turning positive.",
            "volume_spike": "Unusual volume spike in {symbol}. Volume: {volume} vs average {avg_volume}.",
            "bollinger_squeeze": "Bollinger Bands squeeze in {symbol}. Expecting high volatility breakout."
        },
        
        VoiceLanguage.HINDI: {
            "rsi_overbought": "{symbol} का RSI {rsi_value} पर ओवरबॉट दिखा रहा है। प्रॉफिट बुकिंग या शॉर्ट अवसर पर विचार करें।",
            "rsi_oversold": "{symbol} का RSI {rsi_value} पर ओवरसोल्ड दिखा रहा है। खरीदारी का अवसर हो सकता है।",
            "macd_bullish": "{symbol} में MACD बुलिश क्रॉसओवर। मोमेंटम पॉजिटिव हो रहा है।",
            "volume_spike": "{symbol} में असामान्य वॉल्यूम स्पाइक। वॉल्यूम: {volume} बनाम औसत {avg_volume}।",
            "bollinger_squeeze": "{symbol} में Bollinger Bands स्क्वीज। उच्च वोलैटिलिटी ब्रेकआउट की उम्मीद।"
        }
    }


class VoiceAlertEngine:
    """Core voice alert generation and management engine"""
    
    def __init__(self):
        """Initialize voice alert engine"""
        self.templates = VoiceAlertTemplates()
        self.active_alerts = {}
        self.alert_history = []
        self.user_preferences = {}
        
        # Mock TTS engine (replace with actual implementation)
        self.tts_engine = self._initialize_mock_tts()
    
    def _initialize_mock_tts(self):
        """Initialize mock Text-to-Speech engine"""
        class MockTTSEngine:
            async def generate_audio(self, text: str, language: VoiceLanguage) -> str:
                # Mock audio generation - return a mock URL
                mock_url = f"https://audio-cdn.gridworks.com/{uuid.uuid4()}.mp3"
                logger.info(f"Mock TTS generated for: {text[:50]}...")
                return mock_url
        
        return MockTTSEngine()
    
    async def create_pattern_alert(
        self, 
        pattern: PatternDetection, 
        user_id: str, 
        language: VoiceLanguage = VoiceLanguage.ENGLISH
    ) -> VoiceAlert:
        """Create voice alert for detected pattern"""
        
        # Get pattern-specific template
        pattern_templates = self.templates.PATTERN_ALERTS.get(language, self.templates.PATTERN_ALERTS[VoiceLanguage.ENGLISH])
        template = pattern_templates.get(pattern.pattern_type)
        
        if not template:
            # Fallback to generic pattern alert
            template = "Pattern detected in {symbol}: {pattern_type} with {confidence:.0%} confidence."
        
        # Prepare message variables
        message_variables = {
            'symbol': pattern.symbol,
            'pattern_type': pattern.pattern_type.value.replace('_', ' ').title(),
            'confidence': pattern.confidence,
            'magnitude': pattern.expected_move.get('magnitude', 0.05),
            'current_price': pattern.price_levels.get('current', 0),
            'resistance': pattern.price_levels.get('resistance', 0),
            'support': pattern.price_levels.get('support', 0),
            'target': pattern.price_levels.get('target', 0)
        }
        
        # Determine priority based on confidence and pattern type
        priority = self._determine_alert_priority(pattern)
        
        # Create alert
        alert = VoiceAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.PATTERN_DETECTED,
            priority=priority,
            symbol=pattern.symbol,
            language=language,
            message_template=template,
            message_variables=message_variables,
            audio_url=None,
            created_at=datetime.now(),
            scheduled_at=datetime.now(),
            delivered_at=None,
            user_id=user_id,
            pattern_id=pattern.pattern_id,
            expiry_time=datetime.now() + pattern.validity_period
        )
        
        # Generate audio
        audio_url = await self._generate_audio(alert)
        alert.audio_url = audio_url
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        
        logger.info(f"Created pattern alert for {pattern.symbol}: {pattern.pattern_type.value}")
        return alert
    
    async def create_price_alert(
        self,
        symbol: str,
        alert_type: str,  # "target_hit", "stop_loss", "breakout", "breakdown"
        price_data: Dict[str, float],
        user_id: str,
        language: VoiceLanguage = VoiceLanguage.ENGLISH
    ) -> VoiceAlert:
        """Create voice alert for price events"""
        
        # Get price-specific template
        price_templates = self.templates.PRICE_ALERTS.get(language, self.templates.PRICE_ALERTS[VoiceLanguage.ENGLISH])
        template = price_templates.get(alert_type, "Price alert for {symbol}: {current_price}")
        
        # Determine priority
        priority_map = {
            "stop_loss": AlertPriority.CRITICAL,
            "target_hit": AlertPriority.HIGH,
            "breakout": AlertPriority.HIGH,
            "breakdown": AlertPriority.MEDIUM
        }
        priority = priority_map.get(alert_type, AlertPriority.MEDIUM)
        
        # Create alert
        alert = VoiceAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.PRICE_TARGET_HIT if "target" in alert_type else AlertType.BREAKOUT_ALERT,
            priority=priority,
            symbol=symbol,
            language=language,
            message_template=template,
            message_variables={**price_data, 'symbol': symbol},
            audio_url=None,
            created_at=datetime.now(),
            scheduled_at=datetime.now(),
            delivered_at=None,
            user_id=user_id,
            expiry_time=datetime.now() + timedelta(hours=4)
        )
        
        # Generate audio
        audio_url = await self._generate_audio(alert)
        alert.audio_url = audio_url
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        
        return alert
    
    async def create_technical_alert(
        self,
        symbol: str,
        indicator: str,
        indicator_data: Dict[str, Any],
        user_id: str,
        language: VoiceLanguage = VoiceLanguage.ENGLISH
    ) -> VoiceAlert:
        """Create voice alert for technical indicators"""
        
        # Get technical alert template
        tech_templates = self.templates.TECHNICAL_ALERTS.get(language, self.templates.TECHNICAL_ALERTS[VoiceLanguage.ENGLISH])
        template = tech_templates.get(indicator, "Technical signal in {symbol}: {indicator}")
        
        # Create alert
        alert = VoiceAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.TECHNICAL_SIGNAL,
            priority=AlertPriority.MEDIUM,
            symbol=symbol,
            language=language,
            message_template=template,
            message_variables={**indicator_data, 'symbol': symbol, 'indicator': indicator},
            audio_url=None,
            created_at=datetime.now(),
            scheduled_at=datetime.now(),
            delivered_at=None,
            user_id=user_id,
            expiry_time=datetime.now() + timedelta(hours=2)
        )
        
        # Generate audio
        audio_url = await self._generate_audio(alert)
        alert.audio_url = audio_url
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        
        return alert
    
    async def _generate_audio(self, alert: VoiceAlert) -> str:
        """Generate audio for voice alert"""
        try:
            message = alert.final_message
            audio_url = await self.tts_engine.generate_audio(message, alert.language)
            return audio_url
        except Exception as e:
            logger.error(f"Error generating audio for alert {alert.alert_id}: {e}")
            return None
    
    def _determine_alert_priority(self, pattern: PatternDetection) -> AlertPriority:
        """Determine alert priority based on pattern characteristics"""
        
        # High confidence patterns get higher priority
        if pattern.confidence >= 0.9:
            return AlertPriority.CRITICAL
        elif pattern.confidence >= 0.8:
            return AlertPriority.HIGH
        elif pattern.confidence >= 0.6:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
        
        # Major reversal patterns get higher priority
        major_patterns = [
            PatternType.HEAD_AND_SHOULDERS,
            PatternType.DOUBLE_TOP,
            PatternType.DOUBLE_BOTTOM
        ]
        
        if pattern.pattern_type in major_patterns:
            return min(AlertPriority.HIGH, AlertPriority(pattern.confidence * 4))
        
        return AlertPriority.MEDIUM
    
    async def deliver_alert(self, alert: VoiceAlert) -> bool:
        """Deliver voice alert to user"""
        try:
            # In production, this would integrate with WhatsApp Business API
            # For now, we'll simulate delivery
            
            logger.info(f"Delivering alert {alert.alert_id} to user {alert.user_id}")
            logger.info(f"Message: {alert.final_message}")
            logger.info(f"Audio URL: {alert.audio_url}")
            
            # Mark as delivered
            alert.delivered_at = datetime.now()
            
            # Move to history
            self.alert_history.append(alert)
            
            # Remove from active alerts
            if alert.alert_id in self.active_alerts:
                del self.active_alerts[alert.alert_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error delivering alert {alert.alert_id}: {e}")
            alert.retry_count += 1
            return False
    
    async def process_pending_alerts(self):
        """Process all pending alerts for delivery"""
        current_time = datetime.now()
        
        # Get alerts ready for delivery
        ready_alerts = [
            alert for alert in self.active_alerts.values()
            if (alert.scheduled_at <= current_time and 
                alert.delivered_at is None and 
                not alert.is_expired)
        ]
        
        # Sort by priority
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3
        }
        
        ready_alerts.sort(key=lambda a: priority_order[a.priority])
        
        # Deliver alerts
        for alert in ready_alerts:
            success = await self.deliver_alert(alert)
            
            if not success and alert.should_retry:
                # Schedule retry
                alert.scheduled_at = current_time + timedelta(minutes=5)
                logger.info(f"Scheduled retry for alert {alert.alert_id}")
        
        # Clean up expired alerts
        await self._cleanup_expired_alerts()
    
    async def _cleanup_expired_alerts(self):
        """Remove expired alerts"""
        expired_alert_ids = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.is_expired
        ]
        
        for alert_id in expired_alert_ids:
            expired_alert = self.active_alerts.pop(alert_id)
            logger.info(f"Removed expired alert {alert_id} for {expired_alert.symbol}")
    
    async def get_user_alerts(self, user_id: str, limit: int = 20) -> List[VoiceAlert]:
        """Get recent alerts for a user"""
        user_alerts = [
            alert for alert in self.alert_history
            if alert.user_id == user_id
        ]
        
        # Sort by creation time (newest first)
        user_alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return user_alerts[:limit]
    
    async def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set user alert preferences"""
        self.user_preferences[user_id] = {
            'language': preferences.get('language', VoiceLanguage.ENGLISH),
            'min_confidence': preferences.get('min_confidence', 0.7),
            'enabled_patterns': preferences.get('enabled_patterns', list(PatternType)),
            'quiet_hours': preferences.get('quiet_hours', []),
            'max_alerts_per_day': preferences.get('max_alerts_per_day', 20)
        }
        
        logger.info(f"Updated alert preferences for user {user_id}")
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        total_alerts = len(self.alert_history)
        
        if total_alerts == 0:
            return {'total_alerts': 0}
        
        # Group by type
        type_counts = {}
        for alert in self.alert_history:
            alert_type = alert.alert_type.value
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # Group by priority
        priority_counts = {}
        for alert in self.alert_history:
            priority = alert.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Group by language
        language_counts = {}
        for alert in self.alert_history:
            lang = alert.language.value
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Calculate delivery success rate
        delivered_alerts = len([a for a in self.alert_history if a.delivered_at])
        success_rate = delivered_alerts / total_alerts if total_alerts > 0 else 0
        
        return {
            'total_alerts': total_alerts,
            'delivered_alerts': delivered_alerts,
            'success_rate': success_rate,
            'active_alerts': len(self.active_alerts),
            'type_distribution': type_counts,
            'priority_distribution': priority_counts,
            'language_distribution': language_counts,
            'avg_delivery_time': '2.3 seconds'  # Mock value
        }


class PatternAlertIntegration:
    """Integration between pattern detection and voice alerts"""
    
    def __init__(self, alert_engine: VoiceAlertEngine):
        """Initialize pattern alert integration"""
        self.alert_engine = alert_engine
        self.monitored_symbols = set()
        self.user_subscriptions = {}
    
    async def monitor_patterns_for_alerts(
        self, 
        patterns: List[PatternDetection], 
        user_subscriptions: Dict[str, Dict[str, Any]]
    ):
        """Monitor detected patterns and create alerts for subscribed users"""
        
        for pattern in patterns:
            # Check if pattern meets alert criteria
            if await self._should_alert_pattern(pattern):
                
                # Find users subscribed to this symbol
                interested_users = self._get_interested_users(pattern.symbol, user_subscriptions)
                
                for user_id, user_prefs in interested_users.items():
                    # Check user-specific criteria
                    if pattern.confidence >= user_prefs.get('min_confidence', 0.7):
                        
                        # Create alert
                        alert = await self.alert_engine.create_pattern_alert(
                            pattern=pattern,
                            user_id=user_id,
                            language=user_prefs.get('language', VoiceLanguage.ENGLISH)
                        )
                        
                        logger.info(f"Created pattern alert for user {user_id}: {pattern.pattern_type.value}")
    
    async def _should_alert_pattern(self, pattern: PatternDetection) -> bool:
        """Determine if pattern should trigger an alert"""
        
        # Minimum confidence threshold
        if pattern.confidence < 0.6:
            return False
        
        # Only alert on high-impact patterns
        high_impact_patterns = [
            PatternType.HEAD_AND_SHOULDERS,
            PatternType.DOUBLE_TOP,
            PatternType.DOUBLE_BOTTOM,
            PatternType.ASCENDING_TRIANGLE,
            PatternType.DESCENDING_TRIANGLE
        ]
        
        if pattern.pattern_type in high_impact_patterns:
            return True
        
        # For other patterns, require higher confidence
        return pattern.confidence >= 0.8
    
    def _get_interested_users(self, symbol: str, user_subscriptions: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get users interested in alerts for a symbol"""
        interested = {}
        
        for user_id, prefs in user_subscriptions.items():
            watched_symbols = prefs.get('watched_symbols', [])
            if symbol in watched_symbols or 'ALL' in watched_symbols:
                interested[user_id] = prefs
        
        return interested
    
    async def subscribe_user_to_symbol(self, user_id: str, symbol: str, preferences: Dict[str, Any]):
        """Subscribe user to pattern alerts for a symbol"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = {
                'watched_symbols': [],
                'min_confidence': 0.7,
                'language': VoiceLanguage.ENGLISH
            }
        
        self.user_subscriptions[user_id].update(preferences)
        
        if symbol not in self.user_subscriptions[user_id]['watched_symbols']:
            self.user_subscriptions[user_id]['watched_symbols'].append(symbol)
        
        self.monitored_symbols.add(symbol)
        
        logger.info(f"Subscribed user {user_id} to pattern alerts for {symbol}")


# Example usage and testing
async def main():
    """Example usage of voice alerts system"""
    
    # Initialize alert engine
    alert_engine = VoiceAlertEngine()
    
    # Create sample pattern detection (from previous module)
    from .chart_pattern_detection import PatternDetection, PatternType, ConfidenceLevel, MarketCondition
    
    sample_pattern = PatternDetection(
        pattern_id=str(uuid.uuid4()),
        pattern_type=PatternType.HEAD_AND_SHOULDERS,
        confidence=0.85,
        confidence_level=ConfidenceLevel.HIGH,
        symbol="RELIANCE",
        timeframe="1D",
        detection_time=datetime.now(),
        price_levels={'current': 2500, 'resistance': 2600, 'support': 2400, 'target': 2300},
        market_condition=MarketCondition.BEARISH_TREND,
        expected_move={'direction': -1, 'magnitude': 0.08},
        risk_reward_ratio=3.0,
        validity_period=timedelta(days=3),
        pattern_coordinates=[(100, 50), (400, 200)]
    )
    
    # Create pattern alert in Hindi
    alert = await alert_engine.create_pattern_alert(
        pattern=sample_pattern,
        user_id="user123",
        language=VoiceLanguage.HINDI
    )
    
    print(f"Created alert: {alert.alert_id}")
    print(f"Message: {alert.final_message}")
    print(f"Audio URL: {alert.audio_url}")
    print(f"Priority: {alert.priority.value}")
    
    # Create price alert
    price_alert = await alert_engine.create_price_alert(
        symbol="RELIANCE",
        alert_type="target_hit",
        price_data={'target_price': 2600, 'current_price': 2605},
        user_id="user123",
        language=VoiceLanguage.HINDI
    )
    
    print(f"\nPrice alert: {price_alert.final_message}")
    
    # Process pending alerts
    await alert_engine.process_pending_alerts()
    
    # Get statistics
    stats = await alert_engine.get_alert_statistics()
    print(f"\nAlert Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())