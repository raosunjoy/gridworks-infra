"""?
Range Bars Chart Implementation

Range bars are price-based charts where each bar represents a fixed price range.
Unlike time-based charts, range bars ignore time and focus purely on price movement.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from app.charting.core.chart_engine import Chart, ChartConfig, OHLCV
from app.charting.indicators.manager import IndicatorManager
from app.charting.drawing_tools.manager import DrawingToolsManager

@dataclass
class RangeBar:
    """Represents a single Range Bar"""
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    start_time: datetime
    end_time: datetime
    range_size: float
    tick_count: int  # Number of ticks that formed this bar
    is_up_bar: bool  # True if close > open

class RangeBarsChart(Chart):
    """Range Bars chart implementation focusing on price movement"""
    
    def __init__(self, chart_id: str, config: ChartConfig, engine):
        super().__init__(chart_id, config, engine)
        self.chart_type = "range_bars"
        
        # Range bar specific configuration
        self.range_size = config.range_size or self._calculate_default_range_size()
        self.range_type = config.range_type or "points"  # "points" or "percentage"
        
        # Range bars data
        self.range_bars: List[RangeBar] = []
        self.current_bar: Optional[RangeBar] = None
        self.tick_buffer: List[OHLCV] = []  # Buffer for incomplete bars
        
        # State tracking
        self.price_levels = []  # Significant price levels
        self.volume_clusters = []  # Volume concentration areas
        self.breakout_levels = []  # Range breakout points
        
        # Performance metrics
        self.calculation_times = []
        self.average_ticks_per_bar = 0
    
    async def initialize(self):
        """Initialize Range Bars chart with indicators and drawing tools"""
        
        self.indicator_manager = IndicatorManager(self)
        self.drawing_manager = DrawingToolsManager(self)
        
        # Pre-calculate if data exists
        if self.data:
            await self._calculate_range_bars()
    
    def _calculate_default_range_size(self) -> float:
        """Calculate appropriate range size based on symbol and market"""
        
        # Default range sizes for common Indian instruments
        default_ranges = {
            'NIFTY': 25.0,
            'BANKNIFTY': 100.0,
            'SENSEX': 100.0,
            'RELIANCE': 5.0,
            'TCS': 10.0,
            'INFY': 5.0,
            'HDFC': 10.0,
            'ICICIBANK': 2.0,
            'HDFCBANK': 5.0,
            'ITC': 1.0
        }
        
        symbol = self.config.symbol.upper()
        
        # Check for exact match
        if symbol in default_ranges:
            return default_ranges[symbol]
        
        # Check for partial matches
        for key, value in default_ranges.items():
            if key in symbol:
                return value
        
        # Default fallback based on typical price ranges
        return 1.0  # Conservative default
    
    async def add_data_point(self, ohlcv: OHLCV):
        """Add new data point and update range bars"""
        
        self.data.append(ohlcv)
        self.tick_buffer.append(ohlcv)
        
        await self._update_range_bars(ohlcv)
        
        # Update indicators when bar completes
        if len(self.range_bars) > len(self.data) - len(self.tick_buffer):
            latest_bar = self.range_bars[-1]
            bar_ohlcv = OHLCV(
                timestamp=latest_bar.end_time,
                open=latest_bar.open_price,
                high=latest_bar.high_price,
                low=latest_bar.low_price,
                close=latest_bar.close_price,
                volume=latest_bar.volume
            )
            
            if self.indicator_manager:
                await self.indicator_manager.update_all(bar_ohlcv)
    
    async def _calculate_range_bars(self):
        """Calculate all range bars from historical data"""
        
        if len(self.data) < 1:
            return
        
        start_time = datetime.now()
        
        # Reset state
        self.range_bars = []
        self.current_bar = None
        self.tick_buffer = []
        
        # Process each data point
        for tick in self.data:
            self.tick_buffer.append(tick)
            await self._process_tick(tick)
        
        # Finalize any incomplete bar
        if self.current_bar and self.tick_buffer:
            self._finalize_current_bar()
        
        # Calculate analytics
        await self._calculate_price_levels()
        await self._calculate_volume_clusters()
        await self._calculate_breakout_levels()
        
        # Track performance
        calculation_time = (datetime.now() - start_time).total_seconds() * 1000
        self.calculation_times.append(calculation_time)
        
        # Update average ticks per bar
        if self.range_bars:
            total_ticks = sum(bar.tick_count for bar in self.range_bars)
            self.average_ticks_per_bar = total_ticks / len(self.range_bars)
    
    async def _update_range_bars(self, ohlcv: OHLCV):
        """Update range bars with new tick data"""
        
        await self._process_tick(ohlcv)
        
        # Update analytics if new bar completed
        if len(self.range_bars) > 0:
            await self._update_analytics()
    
    async def _process_tick(self, tick: OHLCV):
        """Process a single tick for range bar formation"""
        
        if not self.current_bar:
            # Start new bar
            self.current_bar = RangeBar(
                open_price=tick.close,
                high_price=tick.close,
                low_price=tick.close,
                close_price=tick.close,
                volume=tick.volume or 0,
                start_time=tick.timestamp,
                end_time=tick.timestamp,
                range_size=self.range_size,
                tick_count=1,
                is_up_bar=False
            )
            return
        
        # Update current bar
        self.current_bar.high_price = max(self.current_bar.high_price, tick.close)
        self.current_bar.low_price = min(self.current_bar.low_price, tick.close)
        self.current_bar.close_price = tick.close
        self.current_bar.volume += tick.volume or 0
        self.current_bar.end_time = tick.timestamp
        self.current_bar.tick_count += 1
        self.current_bar.is_up_bar = self.current_bar.close_price > self.current_bar.open_price
        
        # Check if range is complete
        if self._is_range_complete():
            self._finalize_current_bar()
            await self._start_new_bar(tick)
    
    def _is_range_complete(self) -> bool:
        """Check if current range bar has completed its range"""
        
        if not self.current_bar:
            return False
        
        current_range = self.current_bar.high_price - self.current_bar.low_price
        
        if self.range_type == "percentage":
            percentage_range = (current_range / self.current_bar.open_price) * 100
            return percentage_range >= self.range_size
        else:  # points
            return current_range >= self.range_size
    
    def _finalize_current_bar(self):
        """Finalize the current range bar and add to bars list"""
        
        if self.current_bar:
            self.range_bars.append(self.current_bar)
            self.tick_buffer = []  # Clear buffer
    
    async def _start_new_bar(self, tick: OHLCV):
        """Start a new range bar"""
        
        self.current_bar = RangeBar(
            open_price=tick.close,
            high_price=tick.close,
            low_price=tick.close,
            close_price=tick.close,
            volume=tick.volume or 0,
            start_time=tick.timestamp,
            end_time=tick.timestamp,
            range_size=self.range_size,
            tick_count=1,
            is_up_bar=False
        )
    
    async def _calculate_price_levels(self):
        """Calculate significant price levels from range bars"""
        
        self.price_levels = []
        
        if len(self.range_bars) < 5:
            return
        
        # Collect all price points
        price_points = []
        for bar in self.range_bars:
            price_points.extend([bar.open_price, bar.high_price, bar.low_price, bar.close_price])
        
        # Find price clusters (areas with high price concentration)
        price_points = sorted(price_points)
        tolerance = self.range_size * 0.5  # Half range size tolerance
        
        clusters = []
        current_cluster = [price_points[0]]
        
        for i in range(1, len(price_points)):
            if price_points[i] - price_points[i-1] <= tolerance:
                current_cluster.append(price_points[i])
            else:
                if len(current_cluster) >= 3:  # Minimum cluster size
                    clusters.append(current_cluster)
                current_cluster = [price_points[i]]
        
        # Add last cluster if significant
        if len(current_cluster) >= 3:
            clusters.append(current_cluster)
        
        # Convert clusters to price levels
        for cluster in clusters:
            avg_price = sum(cluster) / len(cluster)
            strength = len(cluster) / len(price_points) * 10  # Scale to 0-10
            
            self.price_levels.append({
                'price': avg_price,
                'strength': min(strength, 5.0),
                'type': 'cluster',
                'touch_count': len(cluster)
            })
        
        # Sort by strength
        self.price_levels.sort(key=lambda x: x['strength'], reverse=True)
    
    async def _calculate_volume_clusters(self):
        """Calculate volume concentration areas"""
        
        self.volume_clusters = []
        
        if len(self.range_bars) < 10:
            return
        
        # Group bars by price levels and sum volume
        price_volume_map = {}
        tolerance = self.range_size * 0.3
        
        for bar in self.range_bars:
            avg_price = (bar.high_price + bar.low_price) / 2
            
            # Find existing price level or create new one
            found_level = None
            for price_level in price_volume_map.keys():
                if abs(avg_price - price_level) <= tolerance:
                    found_level = price_level
                    break
            
            if found_level:
                price_volume_map[found_level] += bar.volume
            else:
                price_volume_map[avg_price] = bar.volume
        
        # Convert to volume clusters
        total_volume = sum(price_volume_map.values())
        
        for price, volume in price_volume_map.items():
            volume_percentage = (volume / total_volume) * 100
            
            if volume_percentage >= 5.0:  # Minimum 5% of total volume
                self.volume_clusters.append({
                    'price': price,
                    'volume': volume,
                    'volume_percentage': volume_percentage,
                    'type': 'high_volume' if volume_percentage >= 15 else 'medium_volume'
                })
        
        # Sort by volume percentage
        self.volume_clusters.sort(key=lambda x: x['volume_percentage'], reverse=True)
    
    async def _calculate_breakout_levels(self):
        """Calculate potential breakout levels"""
        
        self.breakout_levels = []
        
        if len(self.range_bars) < 20:
            return
        
        # Analyze recent price action for consolidation patterns
        recent_bars = self.range_bars[-20:]
        
        # Find consolidation ranges
        highs = [bar.high_price for bar in recent_bars]
        lows = [bar.low_price for bar in recent_bars]
        
        resistance_level = max(highs)
        support_level = min(lows)
        
        # Check for consolidation (limited range)
        price_range = resistance_level - support_level
        avg_range = sum(bar.high_price - bar.low_price for bar in recent_bars) / len(recent_bars)
        
        if price_range <= avg_range * 3:  # Consolidation detected
            # Count touches at levels
            resistance_touches = sum(1 for bar in recent_bars 
                                   if abs(bar.high_price - resistance_level) <= self.range_size * 0.2)
            support_touches = sum(1 for bar in recent_bars 
                                if abs(bar.low_price - support_level) <= self.range_size * 0.2)
            
            if resistance_touches >= 2:
                self.breakout_levels.append({
                    'price': resistance_level,
                    'type': 'resistance_breakout',
                    'direction': 'bullish',
                    'strength': min(resistance_touches, 5),
                    'target': resistance_level + (price_range * 1.5)
                })
            
            if support_touches >= 2:
                self.breakout_levels.append({
                    'price': support_level,
                    'type': 'support_breakdown',
                    'direction': 'bearish',
                    'strength': min(support_touches, 5),
                    'target': support_level - (price_range * 1.5)
                })
    
    async def _update_analytics(self):
        """Update analytics with latest data"""
        
        # Update only essential analytics for performance
        if len(self.range_bars) % 10 == 0:  # Update every 10 bars
            await self._calculate_price_levels()
            await self._calculate_volume_clusters()
            await self._calculate_breakout_levels()
    
    async def detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect Range Bar specific patterns"""
        
        patterns = []
        
        if len(self.range_bars) < 10:
            return patterns
        
        # Pattern 1: Range Expansion
        expansion = await self._detect_range_expansion()
        if expansion:
            patterns.append(expansion)
        
        # Pattern 2: Range Contraction
        contraction = await self._detect_range_contraction()
        if contraction:
            patterns.append(contraction)
        
        # Pattern 3: Volume Breakout
        volume_breakout = await self._detect_volume_breakout()
        if volume_breakout:
            patterns.append(volume_breakout)
        
        # Pattern 4: False Breakout
        false_breakout = await self._detect_false_breakout()
        if false_breakout:
            patterns.append(false_breakout)
        
        return patterns
    
    async def _detect_range_expansion(self) -> Optional[Dict[str, Any]]:
        """Detect range expansion pattern (increased volatility)"""
        
        if len(self.range_bars) < 20:
            return None
        
        recent_bars = self.range_bars[-10:]
        previous_bars = self.range_bars[-20:-10]
        
        # Calculate average tick count
        recent_avg_ticks = sum(bar.tick_count for bar in recent_bars) / len(recent_bars)
        previous_avg_ticks = sum(bar.tick_count for bar in previous_bars) / len(previous_bars)
        
        # Check for significant decrease in ticks per bar (faster bar formation)
        if recent_avg_ticks < previous_avg_ticks * 0.7:  # 30% fewer ticks
            return {
                'pattern': 'range_expansion',
                'type': 'volatility_increase',
                'confidence': 0.75,
                'description': 'Range expansion detected - increased volatility and faster bar formation',
                'recent_avg_ticks': round(recent_avg_ticks, 1),
                'previous_avg_ticks': round(previous_avg_ticks, 1),
                'expansion_factor': round(previous_avg_ticks / recent_avg_ticks, 2)
            }
        
        return None
    
    async def _detect_range_contraction(self) -> Optional[Dict[str, Any]]:
        """Detect range contraction pattern (decreased volatility)"""
        
        if len(self.range_bars) < 20:
            return None
        
        recent_bars = self.range_bars[-10:]
        previous_bars = self.range_bars[-20:-10]
        
        # Calculate average tick count
        recent_avg_ticks = sum(bar.tick_count for bar in recent_bars) / len(recent_bars)
        previous_avg_ticks = sum(bar.tick_count for bar in previous_bars) / len(previous_bars)
        
        # Check for significant increase in ticks per bar (slower bar formation)
        if recent_avg_ticks > previous_avg_ticks * 1.4:  # 40% more ticks
            return {
                'pattern': 'range_contraction',
                'type': 'volatility_decrease',
                'confidence': 0.70,
                'description': 'Range contraction detected - decreased volatility and slower bar formation',
                'recent_avg_ticks': round(recent_avg_ticks, 1),
                'previous_avg_ticks': round(previous_avg_ticks, 1),
                'contraction_factor': round(recent_avg_ticks / previous_avg_ticks, 2)
            }
        
        return None
    
    async def _detect_volume_breakout(self) -> Optional[Dict[str, Any]]:
        """Detect volume breakout pattern"""
        
        if len(self.range_bars) < 15:
            return None
        
        recent_bars = self.range_bars[-5:]
        baseline_bars = self.range_bars[-15:-5]
        
        # Calculate average volume
        recent_avg_volume = sum(bar.volume for bar in recent_bars) / len(recent_bars)
        baseline_avg_volume = sum(bar.volume for bar in baseline_bars) / len(baseline_bars)
        
        # Check for volume spike
        if recent_avg_volume > baseline_avg_volume * 2:  # 100% volume increase
            latest_bar = self.range_bars[-1]
            
            return {
                'pattern': 'volume_breakout',
                'type': 'bullish' if latest_bar.is_up_bar else 'bearish',
                'confidence': 0.80,
                'description': f'Volume breakout detected - {recent_avg_volume/baseline_avg_volume:.1f}x normal volume',
                'volume_increase': round((recent_avg_volume / baseline_avg_volume), 2),
                'direction': 'up' if latest_bar.is_up_bar else 'down'
            }
        
        return None
    
    async def _detect_false_breakout(self) -> Optional[Dict[str, Any]]:
        """Detect false breakout pattern"""
        
        if len(self.range_bars) < 10 or not self.breakout_levels:
            return None
        
        recent_bars = self.range_bars[-5:]
        
        for breakout_level in self.breakout_levels:
            # Check if price broke through level but then reversed
            broke_through = False
            reversed_back = False
            
            for bar in recent_bars[:3]:  # First 3 bars
                if breakout_level['direction'] == 'bullish':
                    if bar.high_price > breakout_level['price']:
                        broke_through = True
                else:  # bearish
                    if bar.low_price < breakout_level['price']:
                        broke_through = True
            
            for bar in recent_bars[3:]:  # Last 2 bars
                if breakout_level['direction'] == 'bullish':
                    if bar.close_price < breakout_level['price']:
                        reversed_back = True
                else:  # bearish
                    if bar.close_price > breakout_level['price']:
                        reversed_back = True
            
            if broke_through and reversed_back:
                return {
                    'pattern': 'false_breakout',
                    'type': 'reversal',
                    'confidence': 0.75,
                    'description': f'False breakout detected at {breakout_level["price"]:.2f}',
                    'failed_level': breakout_level['price'],
                    'original_direction': breakout_level['direction'],
                    'reversal_signal': 'bearish' if breakout_level['direction'] == 'bullish' else 'bullish'
                }
        
        return None
    
    def get_current_trend(self) -> Dict[str, Any]:
        """Get current trend analysis based on range bars"""
        
        if len(self.range_bars) < 5:
            return {'trend': 'neutral', 'strength': 0, 'confidence': 0}
        
        recent_bars = self.range_bars[-10:]
        
        # Count up and down bars
        up_bars = sum(1 for bar in recent_bars if bar.is_up_bar)
        down_bars = len(recent_bars) - up_bars
        
        # Analyze volume trend
        total_volume = sum(bar.volume for bar in recent_bars)
        up_volume = sum(bar.volume for bar in recent_bars if bar.is_up_bar)
        down_volume = total_volume - up_volume
        
        # Determine trend
        if up_bars > down_bars and up_volume > down_volume:
            trend = 'bullish'
            strength = (up_bars / len(recent_bars)) * 100
        elif down_bars > up_bars and down_volume > up_volume:
            trend = 'bearish'
            strength = (down_bars / len(recent_bars)) * 100
        else:
            trend = 'neutral'
            strength = 50
        
        # Calculate confidence based on volume confirmation
        volume_confirmation = max(up_volume, down_volume) / total_volume * 100
        confidence = min(strength + (volume_confirmation - 50), 95)
        
        return {
            'trend': trend,
            'strength': round(strength, 1),
            'confidence': round(max(confidence, 0), 1),
            'up_bars': up_bars,
            'down_bars': down_bars,
            'volume_bias': 'bullish' if up_volume > down_volume else 'bearish'
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive Range Bars analytics"""
        
        if not self.range_bars:
            return {}
        
        # Performance metrics
        avg_calc_time = sum(self.calculation_times) / len(self.calculation_times) if self.calculation_times else 0
        
        # Bar statistics
        total_bars = len(self.range_bars)
        up_bars = sum(1 for bar in self.range_bars if bar.is_up_bar)
        total_volume = sum(bar.volume for bar in self.range_bars)
        
        return {
            'total_range_bars': total_bars,
            'up_bars_count': up_bars,
            'up_bars_percentage': round((up_bars / total_bars) * 100, 1),
            'average_ticks_per_bar': round(self.average_ticks_per_bar, 1),
            'total_volume': total_volume,
            'average_volume_per_bar': round(total_volume / total_bars, 0),
            'range_size': self.range_size,
            'range_type': self.range_type,
            'price_levels_count': len(self.price_levels),
            'volume_clusters_count': len(self.volume_clusters),
            'breakout_levels_count': len(self.breakout_levels),
            'average_calculation_time_ms': round(avg_calc_time, 2),
            'current_trend': self.get_current_trend()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Range Bars chart to dictionary for API responses"""
        
        return {
            'chart_id': self.chart_id,
            'chart_type': self.chart_type,
            'symbol': self.config.symbol,
            'timeframe': self.config.timeframe.value,
            'range_size': self.range_size,
            'range_type': self.range_type,
            'range_bars': [
                {
                    'open': bar.open_price,
                    'high': bar.high_price,
                    'low': bar.low_price,
                    'close': bar.close_price,
                    'volume': bar.volume,
                    'start_time': bar.start_time.isoformat(),
                    'end_time': bar.end_time.isoformat(),
                    'tick_count': bar.tick_count,
                    'is_up_bar': bar.is_up_bar
                }
                for bar in self.range_bars
            ],
            'price_levels': self.price_levels,
            'volume_clusters': self.volume_clusters,
            'breakout_levels': self.breakout_levels,
            'analytics': self.get_analytics(),
            'trend_analysis': self.get_current_trend()
        }