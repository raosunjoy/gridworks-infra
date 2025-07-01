"""
Candlestick Chart Implementation

Professional candlestick charts matching Zerodha Kite quality
with enhanced features like pattern recognition and AI analysis.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass
import json

from ..core.chart_engine import Chart, OHLCV, ChartConfig
from ..indicators.manager import IndicatorManager
from ..drawing_tools.manager import DrawingToolManager
from app.core.logging import logger


@dataclass
class CandlePattern:
    """Detected candlestick pattern"""
    name: str
    type: str  # bullish/bearish/neutral
    confidence: float
    start_index: int
    end_index: int
    description: str
    action_suggestion: str


class CandlestickChart(Chart):
    """
    Professional candlestick chart implementation
    Features:
    - Real-time candlestick rendering
    - Pattern recognition (Doji, Hammer, Engulfing, etc.)
    - AI-powered analysis
    - Voice command support
    - One-click trading integration
    """
    
    def __init__(self, chart_id: str, config: ChartConfig, engine):
        super().__init__(chart_id, config, engine)
        
        self.indicator_manager = IndicatorManager(self)
        self.drawing_manager = DrawingToolManager(self)
        
        # Candlestick specific properties
        self.candle_patterns: List[CandlePattern] = []
        self.support_resistance_levels: List[float] = []
        
        # Performance optimization
        self.candle_cache: Dict[str, Any] = {}
        self.pattern_detection_interval = 10  # Check every 10 candles
        
    async def initialize(self):
        """Initialize candlestick chart with historical data"""
        
        # Load historical data based on timeframe
        historical_data = await self._load_historical_data()
        
        if historical_data:
            self.data = historical_data
            
            # Initial pattern detection
            await self._detect_candlestick_patterns()
            
            # Calculate initial support/resistance
            await self._calculate_support_resistance()
        
        logger.info(f"Initialized candlestick chart {self.id} with {len(self.data)} data points")
    
    async def add_data_point(self, data: OHLCV):
        """Add new candlestick data"""
        
        await super().add_data_point(data)
        
        # Check if we need to run pattern detection
        if len(self.data) % self.pattern_detection_interval == 0:
            await self._detect_candlestick_patterns()
        
        # Update support/resistance if significant move
        if await self._is_significant_move(data):
            await self._calculate_support_resistance()
    
    async def add_indicator(
        self,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> str:
        """Add technical indicator to candlestick chart"""
        
        indicator_id = await self.indicator_manager.add_indicator(
            indicator_type,
            params,
            self.data
        )
        
        self.indicators[indicator_id] = {
            "type": indicator_type,
            "params": params,
            "values": await self.indicator_manager.calculate(indicator_id, self.data)
        }
        
        return indicator_id
    
    async def add_drawing(
        self,
        drawing_type: str,
        points: List[Dict[str, float]],
        style: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add drawing tool to chart"""
        
        drawing_id = await self.drawing_manager.add_drawing(
            drawing_type,
            points,
            style or {}
        )
        
        self.drawings[drawing_id] = {
            "type": drawing_type,
            "points": points,
            "style": style,
            "created_at": datetime.now()
        }
        
        return drawing_id
    
    async def process_voice_command(self, command: str) -> Dict[str, Any]:
        """
        Process voice commands for candlestick chart
        Examples:
        - "Add 20 day moving average"
        - "Show me bullish patterns"
        - "Draw support line at 1500"
        - "Change to 15 minute timeframe"
        """
        
        command_lower = command.lower()
        
        # Indicator commands
        if "moving average" in command_lower or "ma" in command_lower:
            period = self._extract_number(command_lower, default=20)
            indicator_id = await self.add_indicator("SMA", {"period": period})
            return {
                "success": True,
                "action": "indicator_added",
                "message": f"Added {period}-period moving average",
                "indicator_id": indicator_id
            }
        
        # Pattern commands
        elif "pattern" in command_lower:
            if "bullish" in command_lower:
                patterns = [p for p in self.candle_patterns if p.type == "bullish"]
            elif "bearish" in command_lower:
                patterns = [p for p in self.candle_patterns if p.type == "bearish"]
            else:
                patterns = self.candle_patterns
            
            return {
                "success": True,
                "action": "patterns_shown",
                "patterns": [p.__dict__ for p in patterns[-5:]]  # Last 5 patterns
            }
        
        # Drawing commands
        elif "support" in command_lower or "resistance" in command_lower:
            level = self._extract_number(command_lower)
            if level:
                drawing_id = await self.add_drawing(
                    "horizontal_line",
                    [{"price": level}],
                    {"color": "green" if "support" in command_lower else "red"}
                )
                return {
                    "success": True,
                    "action": "drawing_added",
                    "message": f"Added {'support' if 'support' in command_lower else 'resistance'} at {level}",
                    "drawing_id": drawing_id
                }
        
        # Timeframe commands
        elif "minute" in command_lower or "hour" in command_lower or "day" in command_lower:
            # Extract timeframe and update
            # This would trigger a data reload
            pass
        
        return {
            "success": False,
            "message": "Command not understood. Try: 'Add 50 day moving average' or 'Show bullish patterns'"
        }
    
    async def detect_patterns(self) -> List[Dict[str, Any]]:
        """
        AI-powered pattern detection
        Detects: Head & Shoulders, Triangles, Flags, Wedges, etc.
        """
        
        patterns = []
        
        # Get recent price data for analysis
        if len(self.data) < 50:
            return patterns
        
        recent_data = self.data[-200:]  # Analyze last 200 candles
        
        # Convert to numpy arrays for efficient computation
        highs = np.array([d.high for d in recent_data])
        lows = np.array([d.low for d in recent_data])
        closes = np.array([d.close for d in recent_data])
        
        # Head and Shoulders detection
        h_s_pattern = await self._detect_head_shoulders(highs, lows, closes)
        if h_s_pattern:
            patterns.append(h_s_pattern)
        
        # Triangle patterns
        triangle = await self._detect_triangle_pattern(highs, lows)
        if triangle:
            patterns.append(triangle)
        
        # Double top/bottom
        double_pattern = await self._detect_double_top_bottom(highs, lows)
        if double_pattern:
            patterns.append(double_pattern)
        
        # Flag and Pennant
        flag = await self._detect_flag_pattern(highs, lows, closes)
        if flag:
            patterns.append(flag)
        
        return patterns
    
    async def create_alert(
        self,
        condition: Dict[str, Any],
        notification_channels: List[str]
    ) -> str:
        """
        Create smart alerts
        Conditions can be price-based, indicator-based, or pattern-based
        """
        
        import uuid
        alert_id = str(uuid.uuid4())
        
        self.alerts[alert_id] = {
            "condition": condition,
            "channels": notification_channels,
            "created_at": datetime.now(),
            "triggered": False,
            "trigger_count": 0
        }
        
        # Examples of conditions:
        # {"type": "price_cross", "level": 1500, "direction": "above"}
        # {"type": "indicator_cross", "indicator1": "price", "indicator2": "SMA_20"}
        # {"type": "pattern_detected", "pattern": "head_shoulders"}
        
        return alert_id
    
    async def generate_share_data(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate shareable chart data with analysis"""
        
        # Prepare chart snapshot
        snapshot = {
            "chart_id": self.id,
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe.value,
            "timestamp": datetime.now().isoformat(),
            "data_points": len(self.data),
            "last_price": self.data[-1].close if self.data else None,
            "indicators": list(self.indicators.keys()),
            "drawings": len(self.drawings),
            "patterns": [p.name for p in self.candle_patterns[-3:]],
            "analysis": await self._generate_ai_analysis()
        }
        
        # Add image URL if requested
        if options.get("include_image", True):
            image_data = await self.render_to_image(800, 600, "png")
            # In production, upload to S3 and return URL
            snapshot["image_url"] = "data:image/png;base64,..."  # Placeholder
        
        return snapshot
    
    async def render_to_image(self, width: int, height: int, format: str) -> bytes:
        """Render candlestick chart to image"""
        
        # This would use a charting library like matplotlib or plotly
        # For now, return placeholder
        return b"candlestick_chart_image_data"
    
    async def _load_historical_data(self) -> List[OHLCV]:
        """Load historical data for initialization"""
        
        # In production, this would fetch from database/API
        # For now, return empty list
        return []
    
    async def _detect_candlestick_patterns(self):
        """Detect candlestick patterns like Doji, Hammer, etc."""
        
        if len(self.data) < 5:
            return
        
        # Clear old patterns
        self.candle_patterns = []
        
        # Analyze recent candles
        for i in range(len(self.data) - 5, len(self.data)):
            candle = self.data[i]
            
            # Doji detection
            if self._is_doji(candle):
                self.candle_patterns.append(CandlePattern(
                    name="Doji",
                    type="neutral",
                    confidence=0.9,
                    start_index=i,
                    end_index=i,
                    description="Indecision pattern",
                    action_suggestion="Wait for confirmation"
                ))
            
            # Hammer detection
            if i > 0 and self._is_hammer(candle, self.data[i-1]):
                self.candle_patterns.append(CandlePattern(
                    name="Hammer",
                    type="bullish",
                    confidence=0.85,
                    start_index=i,
                    end_index=i,
                    description="Potential reversal",
                    action_suggestion="Consider long position"
                ))
            
            # Engulfing pattern
            if i > 0 and self._is_engulfing(self.data[i-1], candle):
                pattern_type = "bullish" if candle.close > candle.open else "bearish"
                self.candle_patterns.append(CandlePattern(
                    name=f"{pattern_type.capitalize()} Engulfing",
                    type=pattern_type,
                    confidence=0.9,
                    start_index=i-1,
                    end_index=i,
                    description="Strong reversal pattern",
                    action_suggestion=f"Consider {'long' if pattern_type == 'bullish' else 'short'} position"
                ))
    
    async def _calculate_support_resistance(self):
        """Calculate dynamic support and resistance levels"""
        
        if len(self.data) < 20:
            return
        
        # Get recent highs and lows
        recent_data = self.data[-100:]
        highs = [d.high for d in recent_data]
        lows = [d.low for d in recent_data]
        
        # Find local maxima and minima
        self.support_resistance_levels = []
        
        # Simple peak/trough detection
        for i in range(1, len(highs) - 1):
            # Resistance levels (peaks)
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                self.support_resistance_levels.append(highs[i])
            
            # Support levels (troughs)
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                self.support_resistance_levels.append(lows[i])
        
        # Sort and remove duplicates
        self.support_resistance_levels = sorted(set(self.support_resistance_levels))
    
    async def _is_significant_move(self, data: OHLCV) -> bool:
        """Check if price move is significant enough to recalculate S/R"""
        
        if len(self.data) < 2:
            return False
        
        prev_close = self.data[-2].close
        change_pct = abs((data.close - prev_close) / prev_close) * 100
        
        return change_pct > 2.0  # 2% move is significant
    
    async def _detect_head_shoulders(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """Detect head and shoulders pattern"""
        
        # Simplified H&S detection logic
        # In production, use more sophisticated algorithm
        
        if len(highs) < 50:
            return None
        
        # Find peaks
        peaks = []
        for i in range(10, len(highs) - 10):
            if highs[i] == max(highs[i-10:i+10]):
                peaks.append((i, highs[i]))
        
        # Need at least 3 peaks for H&S
        if len(peaks) >= 3:
            # Check if middle peak is highest (head)
            for i in range(1, len(peaks) - 1):
                left_shoulder = peaks[i-1][1]
                head = peaks[i][1]
                right_shoulder = peaks[i+1][1]
                
                if (head > left_shoulder and head > right_shoulder and
                    abs(left_shoulder - right_shoulder) / left_shoulder < 0.03):  # Shoulders roughly equal
                    
                    return {
                        "pattern": "head_and_shoulders",
                        "type": "bearish",
                        "confidence": 0.8,
                        "neckline": min(lows[peaks[i-1][0]:peaks[i+1][0]]),
                        "target": head - (head - min(lows[peaks[i-1][0]:peaks[i+1][0]])),
                        "description": "Bearish reversal pattern detected"
                    }
        
        return None
    
    async def _detect_triangle_pattern(
        self,
        highs: np.ndarray,
        lows: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        
        # Simplified triangle detection
        # In production, use trend line analysis
        
        if len(highs) < 30:
            return None
        
        # Check if highs are converging with lows
        recent_highs = highs[-30:]
        recent_lows = lows[-30:]
        
        # Calculate trend slopes
        high_slope = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
        low_slope = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
        
        # Ascending triangle: flat top, rising bottom
        if abs(high_slope) < 0.001 and low_slope > 0.001:
            return {
                "pattern": "ascending_triangle",
                "type": "bullish",
                "confidence": 0.75,
                "resistance": np.mean(recent_highs),
                "description": "Bullish continuation pattern"
            }
        
        # Descending triangle: falling top, flat bottom
        elif high_slope < -0.001 and abs(low_slope) < 0.001:
            return {
                "pattern": "descending_triangle",
                "type": "bearish",
                "confidence": 0.75,
                "support": np.mean(recent_lows),
                "description": "Bearish continuation pattern"
            }
        
        # Symmetrical triangle: converging lines
        elif high_slope < -0.001 and low_slope > 0.001:
            return {
                "pattern": "symmetrical_triangle",
                "type": "neutral",
                "confidence": 0.7,
                "description": "Continuation pattern, direction unclear"
            }
        
        return None
    
    async def _detect_double_top_bottom(
        self,
        highs: np.ndarray,
        lows: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """Detect double top or double bottom patterns"""
        
        # Simplified detection
        # Look for two similar peaks or troughs
        
        if len(highs) < 40:
            return None
        
        # Find recent peaks
        peaks = []
        for i in range(5, len(highs) - 5):
            if highs[i] == max(highs[i-5:i+5]):
                peaks.append((i, highs[i]))
        
        # Check for double top
        if len(peaks) >= 2:
            last_two_peaks = peaks[-2:]
            if abs(last_two_peaks[0][1] - last_two_peaks[1][1]) / last_two_peaks[0][1] < 0.02:
                return {
                    "pattern": "double_top",
                    "type": "bearish",
                    "confidence": 0.8,
                    "resistance": (last_two_peaks[0][1] + last_two_peaks[1][1]) / 2,
                    "description": "Bearish reversal pattern"
                }
        
        # Similar logic for double bottom with troughs
        
        return None
    
    async def _detect_flag_pattern(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """Detect flag and pennant patterns"""
        
        # Simplified flag detection
        # Look for strong move followed by consolidation
        
        if len(closes) < 20:
            return None
        
        # Check for strong prior move
        prior_move = closes[-20] - closes[-30]
        move_percent = abs(prior_move / closes[-30]) * 100
        
        if move_percent > 5:  # Strong move
            # Check for consolidation
            recent_range = max(highs[-10:]) - min(lows[-10:])
            prior_range = max(highs[-30:-20]) - min(lows[-30:-20])
            
            if recent_range < prior_range * 0.5:  # Consolidating
                return {
                    "pattern": "flag",
                    "type": "bullish" if prior_move > 0 else "bearish",
                    "confidence": 0.7,
                    "target": closes[-1] + prior_move,  # Measured move
                    "description": f"{'Bullish' if prior_move > 0 else 'Bearish'} continuation pattern"
                }
        
        return None
    
    async def _generate_ai_analysis(self) -> str:
        """Generate AI-powered analysis of current chart"""
        
        if not self.data:
            return "Insufficient data for analysis"
        
        # Basic analysis components
        last_price = self.data[-1].close
        price_change = 0
        if len(self.data) > 1:
            price_change = ((last_price - self.data[-2].close) / self.data[-2].close) * 100
        
        # Trend analysis
        trend = "neutral"
        if len(self.data) > 20:
            sma20 = np.mean([d.close for d in self.data[-20:]])
            if last_price > sma20 * 1.02:
                trend = "bullish"
            elif last_price < sma20 * 0.98:
                trend = "bearish"
        
        # Pattern summary
        recent_patterns = self.candle_patterns[-3:] if self.candle_patterns else []
        pattern_text = ", ".join([p.name for p in recent_patterns]) if recent_patterns else "No significant patterns"
        
        # Support/Resistance
        nearest_support = None
        nearest_resistance = None
        for level in self.support_resistance_levels:
            if level < last_price and (nearest_support is None or level > nearest_support):
                nearest_support = level
            elif level > last_price and (nearest_resistance is None or level < nearest_resistance):
                nearest_resistance = level
        
        analysis = f"""
Market Analysis for {self.config.symbol}:
- Current Price: ₹{last_price:.2f} ({price_change:+.2f}%)
- Trend: {trend.capitalize()}
- Recent Patterns: {pattern_text}
- Support: ₹{nearest_support:.2f if nearest_support else 'N/A'}
- Resistance: ₹{nearest_resistance:.2f if nearest_resistance else 'N/A'}
- Recommendation: {'Buy' if trend == 'bullish' else 'Sell' if trend == 'bearish' else 'Hold'}
        """.strip()
        
        return analysis
    
    def _is_doji(self, candle: OHLCV) -> bool:
        """Check if candle is a Doji"""
        body = abs(candle.close - candle.open)
        total_range = candle.high - candle.low
        
        if total_range == 0:
            return False
        
        return body / total_range < 0.1
    
    def _is_hammer(self, candle: OHLCV, prev_candle: OHLCV) -> bool:
        """Check if candle is a Hammer"""
        body = abs(candle.close - candle.open)
        lower_shadow = min(candle.open, candle.close) - candle.low
        upper_shadow = candle.high - max(candle.open, candle.close)
        
        # Hammer criteria
        return (
            lower_shadow > body * 2 and  # Long lower shadow
            upper_shadow < body * 0.5 and  # Small upper shadow
            candle.close < prev_candle.close  # In downtrend
        )
    
    def _is_engulfing(self, prev_candle: OHLCV, candle: OHLCV) -> bool:
        """Check if current candle engulfs previous"""
        prev_body = abs(prev_candle.close - prev_candle.open)
        curr_body = abs(candle.close - candle.open)
        
        # Current body must be larger
        if curr_body <= prev_body:
            return False
        
        # Bullish engulfing
        if prev_candle.close < prev_candle.open and candle.close > candle.open:
            return candle.open <= prev_candle.close and candle.close >= prev_candle.open
        
        # Bearish engulfing
        if prev_candle.close > prev_candle.open and candle.close < candle.open:
            return candle.open >= prev_candle.close and candle.close <= prev_candle.open
        
        return False
    
    def _extract_number(self, text: str, default: Optional[float] = None) -> Optional[float]:
        """Extract number from text"""
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        return float(numbers[0]) if numbers else default