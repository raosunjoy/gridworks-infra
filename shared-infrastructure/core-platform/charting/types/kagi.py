"""?
Kagi Chart Implementation

Kagi charts are a Japanese charting technique that filters out noise to show
pure price movement. Lines change direction only when price moves beyond
a specified reversal amount.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from app.charting.core.chart_engine import Chart, ChartConfig, OHLCV
from app.charting.indicators.manager import IndicatorManager
from app.charting.drawing_tools.manager import DrawingToolsManager

@dataclass
class KagiLine:
    """Represents a single Kagi line"""
    start_price: float
    end_price: float
    start_time: datetime
    end_time: datetime
    direction: str  # 'up' or 'down'
    thickness: str  # 'thin' or 'thick'
    is_yang: bool  # True for yang (thick up), False for yin (thick down)

class KagiChart(Chart):
    """Kagi chart implementation with traditional Japanese charting principles"""
    
    def __init__(self, chart_id: str, config: ChartConfig, engine):
        super().__init__(chart_id, config, engine)
        self.chart_type = "kagi"
        
        # Kagi-specific configuration
        self.reversal_amount = config.kagi_reversal or 1.0  # Default 1% reversal
        self.reversal_type = config.kagi_reversal_type or "percentage"  # "percentage" or "points"
        
        # Kagi lines data
        self.kagi_lines: List[KagiLine] = []
        self.current_line: Optional[KagiLine] = None
        self.last_direction = None
        
        # State tracking
        self.shoulder_levels = []  # Support/resistance levels
        self.yang_yin_transitions = []  # Trend change points
        
        # Performance metrics
        self.calculation_times = []
    
    async def initialize(self):
        """Initialize Kagi chart with indicators and drawing tools"""
        
        self.indicator_manager = IndicatorManager(self)
        self.drawing_manager = DrawingToolsManager(self)
        
        # Pre-calculate if data exists
        if self.data:
            await self._calculate_kagi_lines()
    
    async def add_data_point(self, ohlcv: OHLCV):
        """Add new data point and update Kagi lines"""
        
        self.data.append(ohlcv)
        await self._update_kagi_lines(ohlcv)
        
        # Update indicators
        if self.indicator_manager:
            await self.indicator_manager.update_all(ohlcv)
    
    async def _calculate_kagi_lines(self):
        """Calculate all Kagi lines from historical data"""
        
        if len(self.data) < 2:
            return
        
        start_time = datetime.now()
        
        # Reset state
        self.kagi_lines = []
        self.current_line = None
        self.shoulder_levels = []
        self.yang_yin_transitions = []
        
        # Start with first data point
        first_point = self.data[0]
        self.current_line = KagiLine(
            start_price=first_point.close,
            end_price=first_point.close,
            start_time=first_point.timestamp,
            end_time=first_point.timestamp,
            direction='up',
            thickness='thin',
            is_yang=False
        )
        
        # Process each subsequent data point
        for i in range(1, len(self.data)):
            await self._process_price_point(self.data[i])
        
        # Finalize current line if exists
        if self.current_line:
            self.kagi_lines.append(self.current_line)
        
        # Calculate shoulder levels and transitions
        await self._calculate_shoulder_levels()
        await self._calculate_yang_yin_transitions()
        
        # Track performance
        calculation_time = (datetime.now() - start_time).total_seconds() * 1000
        self.calculation_times.append(calculation_time)
    
    async def _update_kagi_lines(self, ohlcv: OHLCV):
        """Update Kagi lines with new price data"""
        
        await self._process_price_point(ohlcv)
        
        # Update shoulder levels and transitions
        await self._calculate_shoulder_levels()
        await self._calculate_yang_yin_transitions()
    
    async def _process_price_point(self, ohlcv: OHLCV):
        """Process a single price point for Kagi line formation"""
        
        if not self.current_line:
            return
        
        current_price = ohlcv.close
        reversal_threshold = self._calculate_reversal_threshold(self.current_line.end_price)
        
        # Check for reversal
        if self._should_reverse(current_price, reversal_threshold):
            await self._create_new_line(current_price, ohlcv.timestamp)
        else:
            # Extend current line
            self.current_line.end_price = current_price
            self.current_line.end_time = ohlcv.timestamp
            
            # Update direction if needed
            if current_price > self.current_line.start_price:
                self.current_line.direction = 'up'
            elif current_price < self.current_line.start_price:
                self.current_line.direction = 'down'
    
    def _calculate_reversal_threshold(self, base_price: float) -> float:
        """Calculate the price threshold needed for reversal"""
        
        if self.reversal_type == "percentage":
            return base_price * (self.reversal_amount / 100)
        else:  # points
            return self.reversal_amount
    
    def _should_reverse(self, current_price: float, threshold: float) -> bool:
        """Determine if price movement warrants a reversal"""
        
        if not self.current_line:
            return False
        
        price_change = abs(current_price - self.current_line.start_price)
        
        # Check if movement is significant enough and in opposite direction
        if price_change >= threshold:
            if self.current_line.direction == 'up' and current_price < self.current_line.start_price:
                return True
            elif self.current_line.direction == 'down' and current_price > self.current_line.start_price:
                return True
        
        return False
    
    async def _create_new_line(self, price: float, timestamp: datetime):
        """Create a new Kagi line when reversal occurs"""
        
        # Finalize current line
        if self.current_line:
            self.kagi_lines.append(self.current_line)
        
        # Determine new direction
        new_direction = 'up' if price > self.current_line.end_price else 'down'
        
        # Determine thickness (yang/yin)
        is_yang, thickness = self._determine_line_thickness(price, new_direction)
        
        # Create new line
        self.current_line = KagiLine(
            start_price=self.current_line.end_price,
            end_price=price,
            start_time=self.current_line.end_time,
            end_time=timestamp,
            direction=new_direction,
            thickness=thickness,
            is_yang=is_yang
        )
    
    def _determine_line_thickness(self, price: float, direction: str) -> Tuple[bool, str]:
        """Determine if line should be thick (yang/yin) or thin"""
        
        if not self.kagi_lines:
            return False, 'thin'
        
        # Find previous shoulder levels
        recent_highs = [line.end_price for line in self.kagi_lines[-10:] 
                       if line.direction == 'up']
        recent_lows = [line.end_price for line in self.kagi_lines[-10:] 
                      if line.direction == 'down']
        
        if direction == 'up':
            # Yang line: breaks above previous high
            if recent_highs and price > max(recent_highs):
                return True, 'thick'
        else:
            # Yin line: breaks below previous low
            if recent_lows and price < min(recent_lows):
                return True, 'thick'
        
        return False, 'thin'
    
    async def _calculate_shoulder_levels(self):
        """Calculate support and resistance levels from Kagi lines"""
        
        self.shoulder_levels = []
        
        if len(self.kagi_lines) < 3:
            return
        
        # Find turning points that act as shoulders
        for i in range(1, len(self.kagi_lines) - 1):
            prev_line = self.kagi_lines[i-1]
            current_line = self.kagi_lines[i]
            next_line = self.kagi_lines[i+1]
            
            # Identify shoulder highs (resistance)
            if (prev_line.direction == 'up' and current_line.direction == 'down' and 
                next_line.direction == 'up'):
                self.shoulder_levels.append({
                    'price': current_line.start_price,
                    'type': 'resistance',
                    'strength': self._calculate_level_strength(current_line.start_price, 'high'),
                    'timestamp': current_line.start_time
                })
            
            # Identify shoulder lows (support)
            elif (prev_line.direction == 'down' and current_line.direction == 'up' and 
                  next_line.direction == 'down'):
                self.shoulder_levels.append({
                    'price': current_line.start_price,
                    'type': 'support',
                    'strength': self._calculate_level_strength(current_line.start_price, 'low'),
                    'timestamp': current_line.start_time
                })
    
    def _calculate_level_strength(self, price: float, level_type: str) -> float:
        """Calculate the strength of a support/resistance level"""
        
        touches = 0
        tolerance = price * 0.001  # 0.1% tolerance
        
        for line in self.kagi_lines:
            if level_type == 'high':
                if abs(line.end_price - price) <= tolerance and line.direction == 'up':
                    touches += 1
            else:  # low
                if abs(line.end_price - price) <= tolerance and line.direction == 'down':
                    touches += 1
        
        return min(touches / len(self.kagi_lines) * 10, 5.0)  # Scale 0-5
    
    async def _calculate_yang_yin_transitions(self):
        """Calculate major trend transitions (yang to yin and vice versa)"""
        
        self.yang_yin_transitions = []
        
        for i in range(1, len(self.kagi_lines)):
            prev_line = self.kagi_lines[i-1]
            current_line = self.kagi_lines[i]
            
            # Yang to Yin transition (bullish to bearish)
            if (prev_line.thickness == 'thick' and prev_line.direction == 'up' and
                current_line.thickness == 'thick' and current_line.direction == 'down'):
                self.yang_yin_transitions.append({
                    'type': 'yang_to_yin',
                    'timestamp': current_line.start_time,
                    'price': current_line.start_price,
                    'signal': 'bearish_reversal',
                    'strength': 'strong'
                })
            
            # Yin to Yang transition (bearish to bullish)
            elif (prev_line.thickness == 'thick' and prev_line.direction == 'down' and
                  current_line.thickness == 'thick' and current_line.direction == 'up'):
                self.yang_yin_transitions.append({
                    'type': 'yin_to_yang',
                    'timestamp': current_line.start_time,
                    'price': current_line.start_price,
                    'signal': 'bullish_reversal',
                    'strength': 'strong'
                })
    
    async def detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect Kagi-specific patterns"""
        
        patterns = []
        
        if len(self.kagi_lines) < 5:
            return patterns
        
        # Pattern 1: Three Buddha Top (Triple Top)
        three_buddha = await self._detect_three_buddha_pattern()
        if three_buddha:
            patterns.append(three_buddha)
        
        # Pattern 2: Three River Bottom (Triple Bottom)
        three_river = await self._detect_three_river_pattern()
        if three_river:
            patterns.append(three_river)
        
        # Pattern 3: Kagi Breakout
        breakout = await self._detect_kagi_breakout()
        if breakout:
            patterns.append(breakout)
        
        # Pattern 4: Shoulder Line Break
        shoulder_break = await self._detect_shoulder_break()
        if shoulder_break:
            patterns.append(shoulder_break)
        
        return patterns
    
    async def _detect_three_buddha_pattern(self) -> Optional[Dict[str, Any]]:
        """Detect Three Buddha Top pattern (bearish reversal)"""
        
        if len(self.kagi_lines) < 7:
            return None
        
        # Look for three consecutive peaks at similar levels
        recent_lines = self.kagi_lines[-7:]
        peaks = []
        
        for i, line in enumerate(recent_lines):
            if (i > 0 and i < len(recent_lines) - 1 and
                line.direction == 'up' and
                recent_lines[i-1].direction == 'down' and
                recent_lines[i+1].direction == 'down'):
                peaks.append(line.end_price)
        
        if len(peaks) >= 3:
            # Check if peaks are at similar levels (within 2%)
            peak_range = max(peaks) - min(peaks)
            avg_peak = sum(peaks) / len(peaks)
            
            if peak_range / avg_peak <= 0.02:  # Within 2%
                return {
                    'pattern': 'three_buddha_top',
                    'type': 'bearish',
                    'confidence': 0.85,
                    'description': 'Three Buddha Top pattern detected - bearish reversal signal',
                    'peak_levels': peaks,
                    'target_price': min(peaks) * 0.95  # 5% below lowest peak
                }
        
        return None
    
    async def _detect_three_river_pattern(self) -> Optional[Dict[str, Any]]:
        """Detect Three River Bottom pattern (bullish reversal)"""
        
        if len(self.kagi_lines) < 7:
            return None
        
        # Look for three consecutive troughs at similar levels
        recent_lines = self.kagi_lines[-7:]
        troughs = []
        
        for i, line in enumerate(recent_lines):
            if (i > 0 and i < len(recent_lines) - 1 and
                line.direction == 'down' and
                recent_lines[i-1].direction == 'up' and
                recent_lines[i+1].direction == 'up'):
                troughs.append(line.end_price)
        
        if len(troughs) >= 3:
            # Check if troughs are at similar levels (within 2%)
            trough_range = max(troughs) - min(troughs)
            avg_trough = sum(troughs) / len(troughs)
            
            if trough_range / avg_trough <= 0.02:  # Within 2%
                return {
                    'pattern': 'three_river_bottom',
                    'type': 'bullish',
                    'confidence': 0.85,
                    'description': 'Three River Bottom pattern detected - bullish reversal signal',
                    'trough_levels': troughs,
                    'target_price': max(troughs) * 1.05  # 5% above highest trough
                }
        
        return None
    
    async def _detect_kagi_breakout(self) -> Optional[Dict[str, Any]]:
        """Detect Kagi breakout pattern"""
        
        if len(self.kagi_lines) < 3:
            return None
        
        latest_line = self.kagi_lines[-1]
        
        # Check for thick line breakout
        if latest_line.thickness == 'thick':
            # Find recent consolidation range
            consolidation_lines = self.kagi_lines[-10:]
            prices = [line.end_price for line in consolidation_lines[:-1]]
            
            if prices:
                range_high = max(prices)
                range_low = min(prices)
                
                if latest_line.direction == 'up' and latest_line.end_price > range_high:
                    return {
                        'pattern': 'kagi_breakout',
                        'type': 'bullish',
                        'confidence': 0.80,
                        'description': 'Bullish Kagi breakout above consolidation range',
                        'breakout_level': range_high,
                        'target_price': latest_line.end_price * 1.1
                    }
                elif latest_line.direction == 'down' and latest_line.end_price < range_low:
                    return {
                        'pattern': 'kagi_breakout',
                        'type': 'bearish',
                        'confidence': 0.80,
                        'description': 'Bearish Kagi breakdown below consolidation range',
                        'breakdown_level': range_low,
                        'target_price': latest_line.end_price * 0.9
                    }
        
        return None
    
    async def _detect_shoulder_break(self) -> Optional[Dict[str, Any]]:
        """Detect shoulder line break pattern"""
        
        if not self.shoulder_levels or len(self.kagi_lines) < 2:
            return None
        
        latest_line = self.kagi_lines[-1]
        
        # Check if latest line breaks through significant shoulder level
        for shoulder in self.shoulder_levels[-5:]:  # Check recent shoulders
            if shoulder['strength'] >= 3.0:  # Strong level
                if (latest_line.direction == 'up' and 
                    latest_line.end_price > shoulder['price'] and
                    shoulder['type'] == 'resistance'):
                    return {
                        'pattern': 'shoulder_break',
                        'type': 'bullish',
                        'confidence': min(0.7 + shoulder['strength'] * 0.1, 0.95),
                        'description': f'Bullish break above resistance shoulder at {shoulder["price"]:.2f}',
                        'shoulder_level': shoulder['price'],
                        'target_price': shoulder['price'] * 1.08
                    }
                elif (latest_line.direction == 'down' and 
                      latest_line.end_price < shoulder['price'] and
                      shoulder['type'] == 'support'):
                    return {
                        'pattern': 'shoulder_break',
                        'type': 'bearish',
                        'confidence': min(0.7 + shoulder['strength'] * 0.1, 0.95),
                        'description': f'Bearish break below support shoulder at {shoulder["price"]:.2f}',
                        'shoulder_level': shoulder['price'],
                        'target_price': shoulder['price'] * 0.92
                    }
        
        return None
    
    def get_current_trend(self) -> Dict[str, Any]:
        """Get current Kagi trend analysis"""
        
        if not self.kagi_lines:
            return {'trend': 'neutral', 'strength': 0, 'confidence': 0}
        
        latest_line = self.kagi_lines[-1]
        
        # Analyze recent lines for trend
        recent_lines = self.kagi_lines[-5:]
        up_lines = sum(1 for line in recent_lines if line.direction == 'up')
        down_lines = sum(1 for line in recent_lines if line.direction == 'down')
        thick_lines = sum(1 for line in recent_lines if line.thickness == 'thick')
        
        # Determine trend
        if up_lines > down_lines:
            trend = 'bullish'
            strength = (up_lines / len(recent_lines)) * 100
        elif down_lines > up_lines:
            trend = 'bearish'
            strength = (down_lines / len(recent_lines)) * 100
        else:
            trend = 'neutral'
            strength = 50
        
        # Factor in line thickness
        thickness_factor = thick_lines / len(recent_lines)
        confidence = min(strength + (thickness_factor * 20), 95)
        
        return {
            'trend': trend,
            'strength': round(strength, 1),
            'confidence': round(confidence, 1),
            'current_line': {
                'direction': latest_line.direction,
                'thickness': latest_line.thickness,
                'is_yang': latest_line.is_yang
            },
            'yang_yin_state': 'yang' if latest_line.is_yang else 'yin'
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive Kagi chart analytics"""
        
        if not self.kagi_lines:
            return {}
        
        # Performance metrics
        avg_calc_time = sum(self.calculation_times) / len(self.calculation_times) if self.calculation_times else 0
        
        # Line statistics
        total_lines = len(self.kagi_lines)
        thick_lines = sum(1 for line in self.kagi_lines if line.thickness == 'thick')
        yang_lines = sum(1 for line in self.kagi_lines if line.is_yang)
        
        return {
            'total_kagi_lines': total_lines,
            'thick_lines_count': thick_lines,
            'thick_lines_percentage': round((thick_lines / total_lines) * 100, 1),
            'yang_lines_count': yang_lines,
            'yang_percentage': round((yang_lines / total_lines) * 100, 1),
            'shoulder_levels_count': len(self.shoulder_levels),
            'trend_transitions': len(self.yang_yin_transitions),
            'reversal_amount': self.reversal_amount,
            'reversal_type': self.reversal_type,
            'average_calculation_time_ms': round(avg_calc_time, 2),
            'current_trend': self.get_current_trend()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Kagi chart to dictionary for API responses"""
        
        return {
            'chart_id': self.chart_id,
            'chart_type': self.chart_type,
            'symbol': self.config.symbol,
            'timeframe': self.config.timeframe.value,
            'reversal_amount': self.reversal_amount,
            'reversal_type': self.reversal_type,
            'kagi_lines': [
                {
                    'start_price': line.start_price,
                    'end_price': line.end_price,
                    'start_time': line.start_time.isoformat(),
                    'end_time': line.end_time.isoformat(),
                    'direction': line.direction,
                    'thickness': line.thickness,
                    'is_yang': line.is_yang
                }
                for line in self.kagi_lines
            ],
            'shoulder_levels': self.shoulder_levels,
            'yang_yin_transitions': self.yang_yin_transitions,
            'analytics': self.get_analytics(),
            'trend_analysis': self.get_current_trend()
        }