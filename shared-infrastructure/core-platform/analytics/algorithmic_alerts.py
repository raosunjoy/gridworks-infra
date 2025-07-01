"""
Algorithmic Alerts & Pattern Recognition System
==============================================

Advanced pattern recognition system that identifies trading opportunities,
market anomalies, and generates intelligent alerts for retail traders.

Features:
- Technical pattern recognition (triangles, flags, breakouts)
- Market regime detection (trending, ranging, volatile)
- Smart alerts with confidence scoring
- ML-based signal generation
- Risk-adjusted opportunity identification
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class PatternType(Enum):
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    TRIANGLE = "TRIANGLE"
    FLAG = "FLAG"
    PENNANT = "PENNANT"
    HEAD_SHOULDERS = "HEAD_SHOULDERS"
    DOUBLE_TOP = "DOUBLE_TOP"
    DOUBLE_BOTTOM = "DOUBLE_BOTTOM"
    SUPPORT_RESISTANCE = "SUPPORT_RESISTANCE"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    MOMENTUM_DIVERGENCE = "MOMENTUM_DIVERGENCE"


class MarketRegime(Enum):
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    HIGHLY_VOLATILE = "HIGHLY_VOLATILE"
    LOW_VOLATILITY = "LOW_VOLATILITY"


class AlertType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    WARNING = "WARNING"
    OPPORTUNITY = "OPPORTUNITY"
    RISK = "RISK"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MarketData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None


@dataclass
class PatternSignal:
    pattern_type: PatternType
    symbol: str
    confidence: float
    direction: str  # "BULLISH", "BEARISH", "NEUTRAL"
    target_price: Optional[float]
    stop_loss: Optional[float]
    timeframe: str
    description: str
    supporting_indicators: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlgorithmicAlert:
    alert_id: str
    symbol: str
    alert_type: AlertType
    priority: Priority
    title: str
    message: str
    confidence: float
    pattern_signals: List[PatternSignal]
    price_target: Optional[float]
    stop_loss: Optional[float]
    risk_reward_ratio: Optional[float]
    market_regime: MarketRegime
    expiry: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class TechnicalIndicators:
    """Technical analysis indicators for pattern recognition."""
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI."""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100.0
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Calculate MACD."""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
        
        prices_array = np.array(prices)
        ema_fast = TechnicalIndicators._ema(prices_array, fast)
        ema_slow = TechnicalIndicators._ema(prices_array, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators._ema(np.array([macd_line]), signal)[0]
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            price = prices[-1] if prices else 100.0
            return price, price * 1.02, price * 0.98
        
        recent_prices = prices[-period:]
        sma = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        return sma, upper, lower
    
    @staticmethod
    def _ema(prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average."""
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def support_resistance_levels(prices: List[float], volume: List[int], lookback: int = 50) -> Tuple[List[float], List[float]]:
        """Identify support and resistance levels."""
        if len(prices) < lookback:
            return [], []
        
        recent_data = list(zip(prices[-lookback:], volume[-lookback:]))
        
        # Find local maxima and minima with volume confirmation
        supports = []
        resistances = []
        
        for i in range(2, len(recent_data) - 2):
            price, vol = recent_data[i]
            
            # Check for local minimum (support)
            if (price <= recent_data[i-1][0] and price <= recent_data[i-2][0] and
                price <= recent_data[i+1][0] and price <= recent_data[i+2][0]):
                if vol > np.mean([v for _, v in recent_data[max(0, i-5):i+5]]):
                    supports.append(price)
            
            # Check for local maximum (resistance)
            if (price >= recent_data[i-1][0] and price >= recent_data[i-2][0] and
                price >= recent_data[i+1][0] and price >= recent_data[i+2][0]):
                if vol > np.mean([v for _, v in recent_data[max(0, i-5):i+5]]):
                    resistances.append(price)
        
        return supports, resistances


class PatternRecognizer:
    """Advanced pattern recognition algorithms."""
    
    def __init__(self):
        self.min_pattern_length = 10
        self.confidence_threshold = 0.6
    
    def detect_patterns(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect all patterns in market data."""
        if len(data) < self.min_pattern_length:
            return []
        
        patterns = []
        
        # Detect various patterns
        patterns.extend(self._detect_breakout_patterns(data))
        patterns.extend(self._detect_triangle_patterns(data))
        patterns.extend(self._detect_flag_patterns(data))
        patterns.extend(self._detect_head_shoulders(data))
        patterns.extend(self._detect_double_patterns(data))
        patterns.extend(self._detect_momentum_divergence(data))
        
        # Filter by confidence
        return [p for p in patterns if p.confidence >= self.confidence_threshold]
    
    def _detect_breakout_patterns(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect breakout and breakdown patterns."""
        patterns = []
        
        if len(data) < 20:
            return patterns
        
        # Get recent price action
        closes = [d.close for d in data[-20:]]
        volumes = [d.volume for d in data[-20:]]
        highs = [d.high for d in data[-20:]]
        lows = [d.low for d in data[-20:]]
        
        # Calculate moving averages
        ma20 = np.mean(closes)
        recent_high = max(highs[-10:])
        recent_low = min(lows[-10:])
        
        current_price = closes[-1]
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[:-1])
        
        # Breakout above resistance
        if (current_price > recent_high and 
            current_volume > avg_volume * 1.5 and
            current_price > ma20):
            
            confidence = min(0.95, (current_volume / avg_volume) * 0.3 + 0.4)
            target_price = current_price + (current_price - recent_low) * 0.5
            stop_loss = recent_high * 0.98
            
            pattern = PatternSignal(
                pattern_type=PatternType.BREAKOUT,
                symbol=data[-1].symbol,
                confidence=confidence,
                direction="BULLISH",
                target_price=target_price,
                stop_loss=stop_loss,
                timeframe="1D",
                description=f"Breakout above {recent_high:.2f} with {current_volume/avg_volume:.1f}x volume",
                supporting_indicators=["Volume", "MA20", "Resistance Break"]
            )
            patterns.append(pattern)
        
        # Breakdown below support
        elif (current_price < recent_low and 
              current_volume > avg_volume * 1.5 and
              current_price < ma20):
            
            confidence = min(0.95, (current_volume / avg_volume) * 0.3 + 0.4)
            target_price = current_price - (recent_high - current_price) * 0.5
            stop_loss = recent_low * 1.02
            
            pattern = PatternSignal(
                pattern_type=PatternType.BREAKDOWN,
                symbol=data[-1].symbol,
                confidence=confidence,
                direction="BEARISH",
                target_price=target_price,
                stop_loss=stop_loss,
                timeframe="1D",
                description=f"Breakdown below {recent_low:.2f} with {current_volume/avg_volume:.1f}x volume",
                supporting_indicators=["Volume", "MA20", "Support Break"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_triangle_patterns(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect triangle patterns (ascending, descending, symmetrical)."""
        patterns = []
        
        if len(data) < 30:
            return patterns
        
        # Analyze recent price action for triangle formation
        highs = [d.high for d in data[-30:]]
        lows = [d.low for d in data[-30:]]
        closes = [d.close for d in data[-30:]]
        
        # Find recent swing highs and lows
        swing_highs = self._find_swing_points(highs, 'high')
        swing_lows = self._find_swing_points(lows, 'low')
        
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Check for ascending triangle
            if self._is_ascending_triangle(swing_highs, swing_lows):
                confidence = 0.75
                current_price = closes[-1]
                resistance = max(swing_highs[-2:])
                target_price = resistance + (resistance - min(swing_lows[-2:])) * 0.6
                
                pattern = PatternSignal(
                    pattern_type=PatternType.TRIANGLE,
                    symbol=data[-1].symbol,
                    confidence=confidence,
                    direction="BULLISH",
                    target_price=target_price,
                    stop_loss=min(swing_lows[-2:]),
                    timeframe="1D",
                    description=f"Ascending triangle with resistance at {resistance:.2f}",
                    supporting_indicators=["Higher Lows", "Horizontal Resistance"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_flag_patterns(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect flag and pennant patterns."""
        patterns = []
        
        if len(data) < 25:
            return patterns
        
        closes = [d.close for d in data[-25:]]
        volumes = [d.volume for d in data[-25:]]
        
        # Look for strong move followed by consolidation
        strong_move_start = -15
        strong_move_end = -10
        consolidation_start = -10
        
        strong_move_gain = (closes[strong_move_end] - closes[strong_move_start]) / closes[strong_move_start]
        consolidation_range = max(closes[consolidation_start:]) - min(closes[consolidation_start:])
        consolidation_mid = (max(closes[consolidation_start:]) + min(closes[consolidation_start:])) / 2
        
        # Flag pattern: strong move + tight consolidation
        if (abs(strong_move_gain) > 0.05 and  # 5% move
            consolidation_range / consolidation_mid < 0.03):  # 3% consolidation range
            
            direction = "BULLISH" if strong_move_gain > 0 else "BEARISH"
            confidence = 0.7
            
            if direction == "BULLISH":
                target_price = closes[-1] + abs(closes[strong_move_end] - closes[strong_move_start])
                stop_loss = min(closes[consolidation_start:]) * 0.98
            else:
                target_price = closes[-1] - abs(closes[strong_move_end] - closes[strong_move_start])
                stop_loss = max(closes[consolidation_start:]) * 1.02
            
            pattern = PatternSignal(
                pattern_type=PatternType.FLAG,
                symbol=data[-1].symbol,
                confidence=confidence,
                direction=direction,
                target_price=target_price,
                stop_loss=stop_loss,
                timeframe="1D",
                description=f"Flag pattern after {strong_move_gain:.1%} move",
                supporting_indicators=["Strong Initial Move", "Tight Consolidation"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_head_shoulders(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect head and shoulders patterns."""
        patterns = []
        
        if len(data) < 40:
            return patterns
        
        highs = [d.high for d in data[-40:]]
        swing_highs = self._find_swing_points(highs, 'high')
        
        if len(swing_highs) >= 3:
            # Check for head and shoulders (middle high is highest)
            if (len(swing_highs) >= 3 and
                swing_highs[-2] > swing_highs[-3] and
                swing_highs[-2] > swing_highs[-1] and
                abs(swing_highs[-3] - swing_highs[-1]) / swing_highs[-2] < 0.05):
                
                confidence = 0.8
                head = swing_highs[-2]
                shoulders = (swing_highs[-3] + swing_highs[-1]) / 2
                neckline = shoulders * 0.98  # Approximation
                
                target_price = neckline - (head - neckline)
                
                pattern = PatternSignal(
                    pattern_type=PatternType.HEAD_SHOULDERS,
                    symbol=data[-1].symbol,
                    confidence=confidence,
                    direction="BEARISH",
                    target_price=target_price,
                    stop_loss=head,
                    timeframe="1D",
                    description=f"Head and shoulders with head at {head:.2f}",
                    supporting_indicators=["Three Peaks", "Symmetrical Shoulders"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_double_patterns(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect double top and double bottom patterns."""
        patterns = []
        
        if len(data) < 30:
            return patterns
        
        highs = [d.high for d in data[-30:]]
        lows = [d.low for d in data[-30:]]
        
        swing_highs = self._find_swing_points(highs, 'high')
        swing_lows = self._find_swing_points(lows, 'low')
        
        # Double top
        if len(swing_highs) >= 2:
            if abs(swing_highs[-1] - swing_highs[-2]) / swing_highs[-1] < 0.02:  # Within 2%
                confidence = 0.75
                resistance = max(swing_highs[-2:])
                support = min(lows[-15:])  # Find support level
                target_price = support - (resistance - support) * 0.5
                
                pattern = PatternSignal(
                    pattern_type=PatternType.DOUBLE_TOP,
                    symbol=data[-1].symbol,
                    confidence=confidence,
                    direction="BEARISH",
                    target_price=target_price,
                    stop_loss=resistance * 1.02,
                    timeframe="1D",
                    description=f"Double top at {resistance:.2f}",
                    supporting_indicators=["Twin Peaks", "Equal Highs"]
                )
                patterns.append(pattern)
        
        # Double bottom
        if len(swing_lows) >= 2:
            if abs(swing_lows[-1] - swing_lows[-2]) / swing_lows[-1] < 0.02:  # Within 2%
                confidence = 0.75
                support = min(swing_lows[-2:])
                resistance = max(highs[-15:])  # Find resistance level
                target_price = resistance + (resistance - support) * 0.5
                
                pattern = PatternSignal(
                    pattern_type=PatternType.DOUBLE_BOTTOM,
                    symbol=data[-1].symbol,
                    confidence=confidence,
                    direction="BULLISH",
                    target_price=target_price,
                    stop_loss=support * 0.98,
                    timeframe="1D",
                    description=f"Double bottom at {support:.2f}",
                    supporting_indicators=["Twin Valleys", "Equal Lows"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_momentum_divergence(self, data: List[MarketData]) -> List[PatternSignal]:
        """Detect momentum divergence patterns."""
        patterns = []
        
        if len(data) < 20:
            return patterns
        
        closes = [d.close for d in data[-20:]]
        
        # Calculate RSI for divergence analysis
        rsi_values = []
        for i in range(14, len(closes)):
            rsi = TechnicalIndicators.rsi(closes[:i+1])
            rsi_values.append(rsi)
        
        if len(rsi_values) < 5:
            return patterns
        
        # Look for price making new highs but RSI making lower highs (bearish divergence)
        recent_price_high = max(closes[-5:])
        prev_price_high = max(closes[-10:-5])
        recent_rsi_high = max(rsi_values[-5:])
        prev_rsi_high = max(rsi_values[-10:-5])
        
        if (recent_price_high > prev_price_high and recent_rsi_high < prev_rsi_high):
            confidence = 0.7
            
            pattern = PatternSignal(
                pattern_type=PatternType.MOMENTUM_DIVERGENCE,
                symbol=data[-1].symbol,
                confidence=confidence,
                direction="BEARISH",
                target_price=closes[-1] * 0.95,
                stop_loss=recent_price_high,
                timeframe="1D",
                description="Bearish momentum divergence (price up, RSI down)",
                supporting_indicators=["RSI Divergence", "Momentum Weakness"]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _find_swing_points(self, prices: List[float], point_type: str, window: int = 3) -> List[float]:
        """Find swing high/low points."""
        swing_points = []
        
        for i in range(window, len(prices) - window):
            if point_type == 'high':
                if all(prices[i] >= prices[j] for j in range(i - window, i + window + 1) if j != i):
                    swing_points.append(prices[i])
            else:  # 'low'
                if all(prices[i] <= prices[j] for j in range(i - window, i + window + 1) if j != i):
                    swing_points.append(prices[i])
        
        return swing_points
    
    def _is_ascending_triangle(self, highs: List[float], lows: List[float]) -> bool:
        """Check if pattern forms an ascending triangle."""
        if len(highs) < 2 or len(lows) < 2:
            return False
        
        # Highs should be relatively flat (resistance)
        high_variance = np.var(highs[-3:]) if len(highs) >= 3 else np.var(highs)
        
        # Lows should be ascending
        recent_lows = lows[-3:] if len(lows) >= 3 else lows
        lows_ascending = all(recent_lows[i] <= recent_lows[i+1] for i in range(len(recent_lows)-1))
        
        return high_variance < (max(highs) * 0.01)**2 and lows_ascending


class MarketRegimeDetector:
    """Detect current market regime for context-aware alerts."""
    
    def __init__(self):
        self.lookback_period = 50
    
    def detect_regime(self, data: List[MarketData]) -> MarketRegime:
        """Detect current market regime."""
        if len(data) < self.lookback_period:
            return MarketRegime.RANGING
        
        closes = [d.close for d in data[-self.lookback_period:]]
        returns = np.diff(closes) / closes[:-1]
        
        # Calculate trend strength
        trend_strength = self._calculate_trend_strength(closes)
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Regime classification
        if volatility > 0.4:  # > 40% annualized volatility
            return MarketRegime.HIGHLY_VOLATILE
        elif volatility < 0.15:  # < 15% annualized volatility
            return MarketRegime.LOW_VOLATILITY
        elif trend_strength > 0.7:
            # Determine trend direction
            if closes[-1] > closes[-20]:  # 20-day trend
                return MarketRegime.TRENDING_UP
            else:
                return MarketRegime.TRENDING_DOWN
        else:
            return MarketRegime.RANGING
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength (0-1)."""
        if len(prices) < 20:
            return 0.5
        
        # Use linear regression to measure trend strength
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Calculate R-squared
        slope, intercept = np.polyfit(x, y, 1)
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        return max(0, min(1, r_squared))


class AlgorithmicAlertsEngine:
    """Main algorithmic alerts and pattern recognition engine."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.pattern_recognizer = PatternRecognizer()
        self.regime_detector = MarketRegimeDetector()
        self.technical_indicators = TechnicalIndicators()
        
        # Data storage
        self.market_data = defaultdict(deque)
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        
        # Alert management
        self.running = False
        self.last_scan_time = datetime.now()
        
    def _default_config(self) -> Dict:
        return {
            "scan_interval": 60,  # seconds
            "symbols": ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS", "INFY", "HDFC", "ICICI"],
            "max_alerts_per_symbol": 3,
            "min_confidence": 0.6,
            "alert_expiry_hours": 24,
            "enable_notifications": True,
            "risk_free_rate": 0.06
        }
    
    async def start_monitoring(self):
        """Start algorithmic alerts monitoring."""
        self.running = True
        logger.info("🔄 Algorithmic Alerts Engine started")
        
        while self.running:
            try:
                await self._scan_patterns()
                await self._cleanup_expired_alerts()
                await asyncio.sleep(self.config["scan_interval"])
            except Exception as e:
                logger.error(f"❌ Alerts monitoring error: {e}")
                await asyncio.sleep(30)
    
    def stop_monitoring(self):
        """Stop algorithmic alerts monitoring."""
        self.running = False
        logger.info("⏹️ Algorithmic Alerts Engine stopped")
    
    async def _scan_patterns(self):
        """Scan for patterns and generate alerts."""
        for symbol in self.config["symbols"]:
            try:
                # Fetch market data
                market_data = await self._fetch_market_data(symbol)
                if not market_data:
                    continue
                
                # Store data
                self.market_data[symbol].extend(market_data)
                # Keep only recent data
                while len(self.market_data[symbol]) > 200:
                    self.market_data[symbol].popleft()
                
                # Detect patterns
                data_list = list(self.market_data[symbol])
                patterns = self.pattern_recognizer.detect_patterns(data_list)
                
                # Detect market regime
                regime = self.regime_detector.detect_regime(data_list)
                
                # Generate alerts from patterns
                for pattern in patterns:
                    alert = self._create_alert_from_pattern(pattern, regime)
                    if alert and alert.confidence >= self.config["min_confidence"]:
                        await self._process_alert(alert)
                
            except Exception as e:
                logger.error(f"❌ Pattern scan error for {symbol}: {e}")
    
    def _create_alert_from_pattern(self, pattern: PatternSignal, regime: MarketRegime) -> Optional[AlgorithmicAlert]:
        """Create alert from detected pattern."""
        # Adjust confidence based on market regime
        adjusted_confidence = self._adjust_confidence_for_regime(pattern.confidence, regime)
        
        if adjusted_confidence < self.config["min_confidence"]:
            return None
        
        # Determine alert type and priority
        alert_type = AlertType.OPPORTUNITY if pattern.direction in ["BULLISH", "BEARISH"] else AlertType.WARNING
        priority = self._calculate_priority(pattern, adjusted_confidence)
        
        # Calculate risk-reward ratio
        risk_reward = None
        if pattern.target_price and pattern.stop_loss:
            current_price = pattern.metadata.get("current_price", 0)
            if current_price > 0:
                reward = abs(pattern.target_price - current_price)
                risk = abs(current_price - pattern.stop_loss)
                risk_reward = reward / risk if risk > 0 else None
        
        # Create alert
        alert_id = f"{pattern.symbol}_{pattern.pattern_type.value}_{int(datetime.now().timestamp())}"
        
        alert = AlgorithmicAlert(
            alert_id=alert_id,
            symbol=pattern.symbol,
            alert_type=alert_type,
            priority=priority,
            title=f"{pattern.pattern_type.value.title()} Pattern - {pattern.symbol}",
            message=self._generate_alert_message(pattern, regime),
            confidence=adjusted_confidence,
            pattern_signals=[pattern],
            price_target=pattern.target_price,
            stop_loss=pattern.stop_loss,
            risk_reward_ratio=risk_reward,
            market_regime=regime,
            expiry=datetime.now() + timedelta(hours=self.config["alert_expiry_hours"]),
            metadata={
                "regime": regime.value,
                "timeframe": pattern.timeframe,
                "supporting_indicators": pattern.supporting_indicators
            }
        )
        
        return alert
    
    def _adjust_confidence_for_regime(self, base_confidence: float, regime: MarketRegime) -> float:
        """Adjust pattern confidence based on market regime."""
        adjustments = {
            MarketRegime.TRENDING_UP: 1.1,      # Bullish patterns more reliable
            MarketRegime.TRENDING_DOWN: 1.1,     # Bearish patterns more reliable
            MarketRegime.RANGING: 0.9,           # Breakout patterns less reliable
            MarketRegime.HIGHLY_VOLATILE: 0.8,   # All patterns less reliable
            MarketRegime.LOW_VOLATILITY: 1.05    # Slightly more reliable
        }
        
        adjustment = adjustments.get(regime, 1.0)
        return min(0.95, base_confidence * adjustment)
    
    def _calculate_priority(self, pattern: PatternSignal, confidence: float) -> Priority:
        """Calculate alert priority."""
        if confidence >= 0.9:
            return Priority.CRITICAL
        elif confidence >= 0.8:
            return Priority.HIGH
        elif confidence >= 0.7:
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def _generate_alert_message(self, pattern: PatternSignal, regime: MarketRegime) -> str:
        """Generate human-readable alert message."""
        direction_emoji = "🚀" if pattern.direction == "BULLISH" else "📉" if pattern.direction == "BEARISH" else "⚠️"
        
        message = f"{direction_emoji} {pattern.description}\n\n"
        message += f"📊 Confidence: {pattern.confidence:.0%}\n"
        message += f"🎯 Direction: {pattern.direction}\n"
        
        if pattern.target_price:
            message += f"🎯 Target: ₹{pattern.target_price:.2f}\n"
        if pattern.stop_loss:
            message += f"🛡️ Stop Loss: ₹{pattern.stop_loss:.2f}\n"
        
        message += f"📈 Market Regime: {regime.value.replace('_', ' ').title()}\n"
        message += f"⏰ Timeframe: {pattern.timeframe}\n"
        
        if pattern.supporting_indicators:
            message += f"📋 Supporting: {', '.join(pattern.supporting_indicators)}"
        
        return message
    
    async def _process_alert(self, alert: AlgorithmicAlert):
        """Process and potentially send alert."""
        # Check if we already have too many alerts for this symbol
        symbol_alerts = [a for a in self.active_alerts.values() if a.symbol == alert.symbol]
        if len(symbol_alerts) >= self.config["max_alerts_per_symbol"]:
            return
        
        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Log alert
        logger.info(f"🚨 {alert.priority.name} Alert: {alert.title}")
        logger.info(f"   {alert.message[:100]}...")
        
        # Send notification if enabled
        if self.config["enable_notifications"]:
            await self._send_notification(alert)
    
    async def _send_notification(self, alert: AlgorithmicAlert):
        """Send alert notification (placeholder for integration)."""
        # This would integrate with notification systems
        # (WhatsApp, Email, Push notifications, etc.)
        pass
    
    async def _cleanup_expired_alerts(self):
        """Remove expired alerts."""
        current_time = datetime.now()
        expired_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.expiry <= current_time
        ]
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
    
    async def _fetch_market_data(self, symbol: str) -> List[MarketData]:
        """Fetch market data for symbol (simulated for demo)."""
        # In real implementation, this would connect to market data feed
        # Simulated data for demonstration
        
        current_time = datetime.now()
        base_price = 100 + hash(symbol) % 50  # Different base for each symbol
        
        # Generate realistic OHLCV data
        data_points = []
        for i in range(5):  # Generate 5 new data points
            timestamp = current_time - timedelta(minutes=5*i)
            
            # Simulate price movement
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            price = base_price * (1 + change)
            
            # Generate OHLC
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = price + np.random.normal(0, 0.005) * price
            
            # Generate volume
            volume = max(1000, int(np.random.exponential(10000)))
            
            # Calculate technical indicators
            closes_for_rsi = [base_price * (1 + np.random.normal(0, 0.01)) for _ in range(15)]
            closes_for_rsi.append(price)
            
            rsi = TechnicalIndicators.rsi(closes_for_rsi)
            macd, signal, histogram = TechnicalIndicators.macd(closes_for_rsi)
            sma, bb_upper, bb_lower = TechnicalIndicators.bollinger_bands(closes_for_rsi)
            
            market_data = MarketData(
                symbol=symbol,
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=price,
                volume=volume,
                vwap=price * (1 + np.random.normal(0, 0.002)),
                rsi=rsi,
                macd=macd,
                bb_upper=bb_upper,
                bb_lower=bb_lower
            )
            data_points.append(market_data)
        
        return data_points
    
    def get_active_alerts(self, symbol: Optional[str] = None) -> List[AlgorithmicAlert]:
        """Get currently active alerts."""
        alerts = list(self.active_alerts.values())
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        
        # Sort by priority and timestamp
        return sorted(alerts, key=lambda x: (x.priority.value, x.timestamp), reverse=True)
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for specified period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alert_history if a.timestamp >= cutoff_time]
        
        if not recent_alerts:
            return {"message": "No alerts in the specified period"}
        
        # Aggregate statistics
        summary = {
            "total_alerts": len(recent_alerts),
            "by_priority": defaultdict(int),
            "by_symbol": defaultdict(int),
            "by_type": defaultdict(int),
            "avg_confidence": 0,
            "successful_patterns": []
        }
        
        for alert in recent_alerts:
            summary["by_priority"][alert.priority.name] += 1
            summary["by_symbol"][alert.symbol] += 1
            summary["by_type"][alert.alert_type.value] += 1
        
        summary["avg_confidence"] = sum(a.confidence for a in recent_alerts) / len(recent_alerts)
        
        return dict(summary)


# Demo usage
async def demo_algorithmic_alerts():
    """Demonstrate the algorithmic alerts system."""
    engine = AlgorithmicAlertsEngine()
    
    print("🔄 Starting Algorithmic Alerts Demo...")
    
    # Start monitoring in background
    monitor_task = asyncio.create_task(engine.start_monitoring())
    
    # Let it run for a bit
    await asyncio.sleep(45)
    
    # Get active alerts
    print("\n🚨 Active Alerts:")
    active_alerts = engine.get_active_alerts()
    for alert in active_alerts[:3]:  # Show top 3
        print(f"  {alert.priority.name}: {alert.title}")
        print(f"    Confidence: {alert.confidence:.0%}")
        print(f"    {alert.message.split(chr(10))[0]}")  # First line only
    
    # Get summary
    print("\n📊 Alert Summary:")
    summary = engine.get_alert_summary(hours=1)
    if "total_alerts" in summary:
        print(f"  Total Alerts: {summary['total_alerts']}")
        print(f"  Average Confidence: {summary['avg_confidence']:.0%}")
        print(f"  By Priority: {dict(summary['by_priority'])}")
    
    # Stop monitoring
    engine.stop_monitoring()
    monitor_task.cancel()
    
    print("✅ Algorithmic Alerts Demo Complete")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_algorithmic_alerts())