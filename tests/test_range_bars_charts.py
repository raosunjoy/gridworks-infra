"""
Comprehensive test suite for Range Bars Charts implementation
Tests all functionality including bar formation, pattern detection, and analytics
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
import json

from app.charting.types.range_bars import RangeBarsChart, RangeBar
from app.charting.core.chart_engine import ChartConfig, TimeFrame, OHLCV


class TestRangeBarsBasics:
    """Test basic Range Bars chart functionality"""
    
    def test_range_bars_initialization(self, chart_config):
        """Test Range Bars chart initialization with configuration"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        assert range_chart.chart_id == "test_chart"
        assert range_chart.chart_type == "range_bars"
        assert range_chart.range_size == 5.0  # From chart_config fixture
        assert range_chart.range_type == "points"
        assert range_chart.range_bars == []
        assert range_chart.current_bar is None
    
    def test_range_bars_custom_settings(self):
        """Test Range Bars chart with custom range settings"""
        config = ChartConfig(
            symbol="NIFTY",
            timeframe=TimeFrame.ONE_MINUTE,
            range_size=2.5,
            range_type="percentage"
        )
        
        range_chart = RangeBarsChart("test_chart", config, Mock())
        
        assert range_chart.range_size == 2.5
        assert range_chart.range_type == "percentage"
    
    def test_default_range_size_calculation(self):
        """Test automatic range size calculation for different symbols"""
        config = ChartConfig(
            symbol="RELIANCE",
            timeframe=TimeFrame.FIVE_MINUTES
        )
        
        range_chart = RangeBarsChart("test_chart", config, Mock())
        
        # Should calculate appropriate range size for RELIANCE
        assert range_chart.range_size == 5.0  # From default_ranges
    
    def test_unknown_symbol_default_range(self):
        """Test default range size for unknown symbol"""
        config = ChartConfig(
            symbol="UNKNOWN_STOCK",
            timeframe=TimeFrame.FIVE_MINUTES
        )
        
        range_chart = RangeBarsChart("test_chart", config, Mock())
        
        # Should use conservative default
        assert range_chart.range_size == 1.0
    
    @pytest.mark.asyncio
    async def test_range_bars_initialization_async(self, chart_config):
        """Test async initialization of Range Bars chart"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Mock managers
        range_chart.indicator_manager = AsyncMock()
        range_chart.drawing_manager = Mock()
        
        await range_chart.initialize()
        
        assert range_chart.indicator_manager is not None
        assert range_chart.drawing_manager is not None


class TestRangeBarFormation:
    """Test Range Bar formation logic"""
    
    @pytest.mark.asyncio
    async def test_first_bar_creation(self, chart_config):
        """Test creation of first Range Bar"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        first_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=1000
        )
        
        await range_chart.add_data_point(first_tick)
        
        assert range_chart.current_bar is not None
        assert range_chart.current_bar.open_price == 100.5
        assert range_chart.current_bar.close_price == 100.5
        assert range_chart.current_bar.high_price == 100.5
        assert range_chart.current_bar.low_price == 100.5
        assert range_chart.current_bar.volume == 1000
        assert range_chart.current_bar.tick_count == 1
    
    @pytest.mark.asyncio
    async def test_bar_extension_within_range(self, chart_config):
        """Test extending bar within range limit"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # First tick
        first_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await range_chart.add_data_point(first_tick)
        
        # Second tick within range (range_size = 5.0)
        second_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 16),
            open=100.0, high=102.0, low=99.0, close=102.0, volume=500
        )
        await range_chart.add_data_point(second_tick)
        
        # Should still be extending current bar
        assert len(range_chart.range_bars) == 0  # No completed bars yet
        assert range_chart.current_bar.high_price == 102.0
        assert range_chart.current_bar.low_price == 100.0
        assert range_chart.current_bar.close_price == 102.0
        assert range_chart.current_bar.volume == 1500
        assert range_chart.current_bar.tick_count == 2
        assert range_chart.current_bar.is_up_bar is True  # close > open
    
    @pytest.mark.asyncio
    async def test_bar_completion_points_range(self, chart_config):
        """Test bar completion with points-based range"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # First tick
        first_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await range_chart.add_data_point(first_tick)
        
        # Second tick that completes range (range_size = 5.0 points)
        completion_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 16),
            open=100.0, high=105.5, low=100.0, close=105.0, volume=500
        )
        await range_chart.add_data_point(completion_tick)
        
        # Should have completed first bar and started new one
        assert len(range_chart.range_bars) == 1
        
        completed_bar = range_chart.range_bars[0]
        assert completed_bar.high_price == 105.5
        assert completed_bar.low_price == 100.0
        assert completed_bar.range_size == 5.0
        assert completed_bar.tick_count == 2
        
        # New bar should be started
        assert range_chart.current_bar is not None
        assert range_chart.current_bar.open_price == 105.0
    
    @pytest.mark.asyncio
    async def test_bar_completion_percentage_range(self):
        """Test bar completion with percentage-based range"""
        config = ChartConfig(
            symbol="NIFTY",
            timeframe=TimeFrame.FIVE_MINUTES,
            range_size=2.0,  # 2% range
            range_type="percentage"
        )
        
        range_chart = RangeBarsChart("test_chart", config, Mock())
        
        # First tick
        first_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=1000.0, high=1001.0, low=999.0, close=1000.0, volume=1000
        )
        await range_chart.add_data_point(first_tick)
        
        # Tick that completes 2% range (1000 + 2% = 1020)
        completion_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 16),
            open=1000.0, high=1021.0, low=1000.0, close=1020.0, volume=500
        )
        await range_chart.add_data_point(completion_tick)
        
        # Should complete the bar
        assert len(range_chart.range_bars) == 1
        
        completed_bar = range_chart.range_bars[0]
        range_percentage = ((completed_bar.high_price - completed_bar.low_price) / completed_bar.open_price) * 100
        assert range_percentage >= 2.0
    
    def test_is_range_complete_points(self, chart_config):
        """Test range completion detection for points"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create current bar
        range_chart.current_bar = RangeBar(
            open_price=100.0,
            high_price=104.0,
            low_price=100.0,
            close_price=104.0,
            volume=1000,
            start_time=datetime(2024, 1, 1, 9, 15),
            end_time=datetime(2024, 1, 1, 9, 16),
            range_size=5.0,
            tick_count=2,
            is_up_bar=True
        )
        
        # Range is 4.0, should not be complete (need 5.0)
        assert not range_chart._is_range_complete()
        
        # Extend range to 5.0
        range_chart.current_bar.high_price = 105.0
        assert range_chart._is_range_complete()
    
    def test_is_range_complete_percentage(self):
        """Test range completion detection for percentage"""
        config = ChartConfig(
            symbol="TEST",
            timeframe=TimeFrame.FIVE_MINUTES,
            range_size=2.0,
            range_type="percentage"
        )
        
        range_chart = RangeBarsChart("test_chart", config, Mock())
        
        # Create current bar
        range_chart.current_bar = RangeBar(
            open_price=100.0,
            high_price=101.5,  # 1.5% range
            low_price=100.0,
            close_price=101.5,
            volume=1000,
            start_time=datetime(2024, 1, 1, 9, 15),
            end_time=datetime(2024, 1, 1, 9, 16),
            range_size=2.0,
            tick_count=2,
            is_up_bar=True
        )
        
        # 1.5% range, should not be complete (need 2.0%)
        assert not range_chart._is_range_complete()
        
        # Extend to 2.0%
        range_chart.current_bar.high_price = 102.0
        assert range_chart._is_range_complete()


class TestRangeBarsAnalytics:
    """Test Range Bars analytics calculations"""
    
    @pytest.mark.asyncio
    async def test_price_levels_calculation(self, chart_config):
        """Test price level clustering calculation"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create sample bars with clustered price levels
        bars = []
        for i in range(10):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=5,
                is_up_bar=True
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        await range_chart._calculate_price_levels()
        
        # Should identify price clusters
        assert len(range_chart.price_levels) > 0
        
        for level in range_chart.price_levels:
            assert 'price' in level
            assert 'strength' in level
            assert 'type' in level
            assert level['strength'] > 0
            assert level['strength'] <= 5.0
    
    @pytest.mark.asyncio
    async def test_volume_clusters_calculation(self, chart_config):
        """Test volume concentration area calculation"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create bars with high volume at specific price levels
        bars = []
        for i in range(15):
            # Concentrate volume around 102-103 price level
            if 102 <= (100 + i * 0.5) <= 103:
                volume = 5000  # High volume
            else:
                volume = 1000  # Normal volume
            
            bar = RangeBar(
                open_price=100.0 + i * 0.5,
                high_price=105.0 + i * 0.5,
                low_price=100.0 + i * 0.5,
                close_price=103.0 + i * 0.5,
                volume=volume,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=3,
                is_up_bar=True
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        await range_chart._calculate_volume_clusters()
        
        # Should identify volume clusters
        assert len(range_chart.volume_clusters) > 0
        
        for cluster in range_chart.volume_clusters:
            assert 'price' in cluster
            assert 'volume' in cluster
            assert 'volume_percentage' in cluster
            assert cluster['volume_percentage'] >= 5.0  # Minimum threshold
    
    @pytest.mark.asyncio
    async def test_breakout_levels_calculation(self, chart_config):
        """Test breakout level identification"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create consolidation pattern with clear resistance/support
        bars = []
        base_price = 100.0
        
        # Create 20 bars in consolidation (100-105 range)
        for i in range(20):
            high_price = min(105.0, base_price + (i % 3) + 2)  # Resistance around 105
            low_price = max(100.0, base_price + (i % 2))       # Support around 100
            
            bar = RangeBar(
                open_price=base_price + 1,
                high_price=high_price,
                low_price=low_price,
                close_price=base_price + 2,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=4,
                is_up_bar=True
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        await range_chart._calculate_breakout_levels()
        
        # Should identify potential breakout levels
        assert len(range_chart.breakout_levels) > 0
        
        for breakout in range_chart.breakout_levels:
            assert 'price' in breakout
            assert 'type' in breakout
            assert 'direction' in breakout
            assert 'strength' in breakout
            assert breakout['type'] in ['resistance_breakout', 'support_breakdown']
    
    @pytest.mark.asyncio
    async def test_insufficient_data_analytics(self, chart_config):
        """Test analytics with insufficient data"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Add only 3 bars (need more for meaningful analytics)
        for i in range(3):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=2,
                is_up_bar=True
            )
            range_chart.range_bars.append(bar)
        
        await range_chart._calculate_price_levels()
        await range_chart._calculate_volume_clusters()
        await range_chart._calculate_breakout_levels()
        
        # Should handle gracefully with minimal data
        # Some analytics might be empty, but shouldn't crash
        assert isinstance(range_chart.price_levels, list)
        assert isinstance(range_chart.volume_clusters, list)
        assert isinstance(range_chart.breakout_levels, list)


class TestRangeBarsPatternDetection:
    """Test Range Bars pattern detection"""
    
    @pytest.mark.asyncio
    async def test_range_expansion_pattern(self, chart_config):
        """Test range expansion pattern detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create pattern with decreasing tick count (faster bar formation)
        bars = []
        
        # Previous period with higher tick count
        for i in range(10):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=20,  # High tick count (slow bar formation)
                is_up_bar=True
            )
            bars.append(bar)
        
        # Recent period with lower tick count (fast bar formation)
        for i in range(10):
            bar = RangeBar(
                open_price=110.0 + i,
                high_price=115.0 + i,
                low_price=110.0 + i,
                close_price=113.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 25 + i),
                end_time=datetime(2024, 1, 1, 9, 26 + i),
                range_size=5.0,
                tick_count=10,  # Lower tick count (fast bar formation)
                is_up_bar=True
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        pattern = await range_chart._detect_range_expansion()
        
        assert pattern is not None
        assert pattern['pattern'] == 'range_expansion'
        assert pattern['type'] == 'volatility_increase'
        assert pattern['confidence'] >= 0.7
        assert 'recent_avg_ticks' in pattern
        assert 'expansion_factor' in pattern
    
    @pytest.mark.asyncio
    async def test_range_contraction_pattern(self, chart_config):
        """Test range contraction pattern detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create pattern with increasing tick count (slower bar formation)
        bars = []
        
        # Previous period with lower tick count
        for i in range(10):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=10,  # Lower tick count
                is_up_bar=True
            )
            bars.append(bar)
        
        # Recent period with higher tick count
        for i in range(10):
            bar = RangeBar(
                open_price=110.0 + i,
                high_price=115.0 + i,
                low_price=110.0 + i,
                close_price=113.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 25 + i),
                end_time=datetime(2024, 1, 1, 9, 26 + i),
                range_size=5.0,
                tick_count=20,  # Higher tick count (slower formation)
                is_up_bar=True
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        pattern = await range_chart._detect_range_contraction()
        
        assert pattern is not None
        assert pattern['pattern'] == 'range_contraction'
        assert pattern['type'] == 'volatility_decrease'
        assert pattern['confidence'] >= 0.7
        assert 'contraction_factor' in pattern
    
    @pytest.mark.asyncio
    async def test_volume_breakout_pattern(self, chart_config):
        """Test volume breakout pattern detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create volume spike pattern
        bars = []
        
        # Baseline period with normal volume
        for i in range(10):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000,  # Normal volume
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=15,
                is_up_bar=True
            )
            bars.append(bar)
        
        # Recent period with volume spike
        for i in range(5):
            bar = RangeBar(
                open_price=110.0 + i,
                high_price=115.0 + i,
                low_price=110.0 + i,
                close_price=114.0 + i,  # Strong up movement
                volume=3000,  # 3x normal volume
                start_time=datetime(2024, 1, 1, 9, 25 + i),
                end_time=datetime(2024, 1, 1, 9, 26 + i),
                range_size=5.0,
                tick_count=10,
                is_up_bar=True
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        pattern = await range_chart._detect_volume_breakout()
        
        assert pattern is not None
        assert pattern['pattern'] == 'volume_breakout'
        assert pattern['type'] == 'bullish'  # Latest bar is up
        assert pattern['confidence'] >= 0.8
        assert 'volume_increase' in pattern
        assert pattern['volume_increase'] >= 2.0
    
    @pytest.mark.asyncio
    async def test_false_breakout_pattern(self, chart_config):
        """Test false breakout pattern detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Setup breakout levels
        range_chart.breakout_levels = [
            {
                'price': 105.0,
                'type': 'resistance_breakout',
                'direction': 'bullish',
                'strength': 3
            }
        ]
        
        # Create false breakout pattern
        bars = []
        
        # Initial bars that break through level
        for i in range(3):
            bar = RangeBar(
                open_price=104.0 + i,
                high_price=107.0 + i,  # Breaks above 105
                low_price=104.0 + i,
                close_price=106.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=10,
                is_up_bar=True
            )
            bars.append(bar)
        
        # Reversal bars that fall back below level
        for i in range(2):
            bar = RangeBar(
                open_price=106.0 - i,
                high_price=106.0 - i,
                low_price=101.0 - i,
                close_price=102.0 - i,  # Closes below 105
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 18 + i),
                end_time=datetime(2024, 1, 1, 9, 19 + i),
                range_size=5.0,
                tick_count=12,
                is_up_bar=False
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        pattern = await range_chart._detect_false_breakout()
        
        assert pattern is not None
        assert pattern['pattern'] == 'false_breakout'
        assert pattern['type'] == 'reversal'
        assert pattern['confidence'] >= 0.7
        assert pattern['failed_level'] == 105.0
        assert pattern['reversal_signal'] == 'bearish'
    
    @pytest.mark.asyncio
    async def test_comprehensive_pattern_detection(self, chart_config):
        """Test comprehensive pattern detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create complex bar data
        bars = []
        for i in range(25):
            bar = RangeBar(
                open_price=100.0 + i * 0.5,
                high_price=105.0 + i * 0.5,
                low_price=100.0 + i * 0.5,
                close_price=103.0 + i * 0.5,
                volume=1000 + i * 100,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=15 - i % 5,  # Varying tick counts
                is_up_bar=i % 3 != 2  # Mostly up bars
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        patterns = await range_chart.detect_patterns()
        
        assert isinstance(patterns, list)
        
        # Verify pattern structure
        for pattern in patterns:
            assert 'pattern' in pattern
            assert 'confidence' in pattern
            assert 0 <= pattern['confidence'] <= 1
            assert 'description' in pattern


class TestRangeBarsTrendAnalysis:
    """Test Range Bars trend analysis"""
    
    def test_current_trend_bullish(self, chart_config):
        """Test bullish trend detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create mostly up bars with volume confirmation
        bars = []
        for i in range(10):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=104.0 + i,  # Consistently closing higher
                volume=1500 if i % 2 == 0 else 800,  # Higher volume on up bars
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=10,
                is_up_bar=True  # All up bars
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        trend = range_chart.get_current_trend()
        
        assert trend['trend'] == 'bullish'
        assert trend['strength'] > 50
        assert trend['confidence'] > 50
        assert trend['up_bars'] == 10
        assert trend['down_bars'] == 0
        assert trend['volume_bias'] == 'bullish'
    
    def test_current_trend_bearish(self, chart_config):
        """Test bearish trend detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create mostly down bars
        bars = []
        for i in range(10):
            bar = RangeBar(
                open_price=110.0 - i,
                high_price=110.0 - i,
                low_price=105.0 - i,
                close_price=106.0 - i,  # Consistently closing lower
                volume=1200 if i % 2 == 0 else 600,  # Higher volume on down bars
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=12,
                is_up_bar=False  # All down bars
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        trend = range_chart.get_current_trend()
        
        assert trend['trend'] == 'bearish'
        assert trend['strength'] > 50
        assert trend['up_bars'] == 0
        assert trend['down_bars'] == 10
        assert trend['volume_bias'] == 'bearish'
    
    def test_current_trend_neutral(self, chart_config):
        """Test neutral trend detection"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Create equal up and down bars
        bars = []
        for i in range(10):
            is_up = i % 2 == 0
            bar = RangeBar(
                open_price=100.0 + i * 0.1,
                high_price=105.0 + i * 0.1,
                low_price=100.0 + i * 0.1,
                close_price=(104.0 + i * 0.1) if is_up else (101.0 + i * 0.1),
                volume=1000,  # Equal volume
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=10,
                is_up_bar=is_up
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        
        trend = range_chart.get_current_trend()
        
        assert trend['trend'] == 'neutral'
        assert trend['strength'] == 50
        assert trend['up_bars'] == 5
        assert trend['down_bars'] == 5
    
    def test_trend_with_insufficient_data(self, chart_config):
        """Test trend analysis with insufficient data"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Add only 3 bars
        for i in range(3):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=10,
                is_up_bar=True
            )
            range_chart.range_bars.append(bar)
        
        trend = range_chart.get_current_trend()
        
        # Should still provide valid trend analysis
        assert trend['trend'] in ['bullish', 'bearish', 'neutral']
        assert 0 <= trend['strength'] <= 100
        assert 0 <= trend['confidence'] <= 100


class TestRangeBarsAnalyticsOutput:
    """Test Range Bars analytics and output"""
    
    def test_analytics_calculation(self, chart_config):
        """Test comprehensive analytics calculation"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Add sample bars
        bars = []
        for i in range(15):
            bar = RangeBar(
                open_price=100.0 + i,
                high_price=105.0 + i,
                low_price=100.0 + i,
                close_price=103.0 + i,
                volume=1000 + i * 100,
                start_time=datetime(2024, 1, 1, 9, 15 + i),
                end_time=datetime(2024, 1, 1, 9, 16 + i),
                range_size=5.0,
                tick_count=10 + i % 5,
                is_up_bar=i % 3 != 2  # 2/3 up bars
            )
            bars.append(bar)
        
        range_chart.range_bars = bars
        range_chart.calculation_times = [25.0, 30.0, 28.0]
        range_chart.average_ticks_per_bar = 12.5
        range_chart.price_levels = [{'price': 105.0, 'strength': 3.0}]
        range_chart.volume_clusters = [{'price': 102.0, 'volume': 5000}]
        range_chart.breakout_levels = [{'price': 110.0, 'direction': 'bullish'}]
        
        analytics = range_chart.get_analytics()
        
        assert analytics['total_range_bars'] == 15
        assert analytics['up_bars_count'] == 10  # 2/3 of 15
        assert analytics['up_bars_percentage'] == 66.7
        assert analytics['average_ticks_per_bar'] == 12.5
        assert analytics['range_size'] == 5.0
        assert analytics['range_type'] == "points"
        assert analytics['price_levels_count'] == 1
        assert analytics['volume_clusters_count'] == 1
        assert analytics['breakout_levels_count'] == 1
        assert analytics['average_calculation_time_ms'] == 27.67
        assert 'current_trend' in analytics
    
    def test_analytics_empty_chart(self, chart_config):
        """Test analytics with empty chart"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        analytics = range_chart.get_analytics()
        
        assert analytics == {}
    
    def test_chart_serialization(self, chart_config):
        """Test chart serialization to dictionary"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Add sample bar
        bar = RangeBar(
            open_price=100.0,
            high_price=105.0,
            low_price=100.0,
            close_price=103.0,
            volume=1500,
            start_time=datetime(2024, 1, 1, 9, 15),
            end_time=datetime(2024, 1, 1, 9, 16),
            range_size=5.0,
            tick_count=8,
            is_up_bar=True
        )
        range_chart.range_bars = [bar]
        
        chart_dict = range_chart.to_dict()
        
        assert chart_dict['chart_id'] == "test_chart"
        assert chart_dict['chart_type'] == "range_bars"
        assert chart_dict['symbol'] == "RELIANCE"
        assert chart_dict['range_size'] == 5.0
        assert chart_dict['range_type'] == "points"
        assert len(chart_dict['range_bars']) == 1
        
        bar_data = chart_dict['range_bars'][0]
        assert bar_data['open'] == 100.0
        assert bar_data['high'] == 105.0
        assert bar_data['low'] == 100.0
        assert bar_data['close'] == 103.0
        assert bar_data['volume'] == 1500
        assert bar_data['tick_count'] == 8
        assert bar_data['is_up_bar'] is True


class TestRangeBarsPerformance:
    """Test Range Bars performance and optimization"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, chart_config):
        """Test performance with large dataset"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        start_time = datetime.now()
        
        # Process large number of ticks
        for i in range(5000):
            tick = OHLCV(
                timestamp=datetime(2024, 1, 1, 9, 15) + timedelta(seconds=i),
                open=100.0 + i * 0.001,
                high=100.0 + i * 0.001 + 0.1,
                low=100.0 + i * 0.001 - 0.05,
                close=100.0 + i * 0.001 + (i % 7 - 3) * 0.02,
                volume=1000 + i % 100
            )
            await range_chart.add_data_point(tick)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        # Should process efficiently (< 10 seconds for 5000 ticks)
        assert processing_time < 10000
        
        # Should have created reasonable number of bars
        assert len(range_chart.range_bars) > 10
        assert len(range_chart.range_bars) < 1000  # Much fewer than ticks
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self, chart_config):
        """Test memory usage stays reasonable"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Add many ticks that form bars
        for i in range(10000):
            # Create pattern that completes bars regularly
            price_cycle = 100.0 + (i // 100) * 10 + (i % 20) * 0.5
            
            tick = OHLCV(
                timestamp=datetime(2024, 1, 1, 9, 15) + timedelta(seconds=i),
                open=price_cycle,
                high=price_cycle + 1.0,
                low=price_cycle - 0.5,
                close=price_cycle + 0.3,
                volume=1000
            )
            await range_chart.add_data_point(tick)
        
        # Memory usage should be reasonable
        # Check that completed bars don't accumulate excessively
        total_bars = len(range_chart.range_bars)
        assert total_bars < 2000  # Should be much less than input ticks
        
        # Analytics should still be fast
        if range_chart.calculation_times:
            avg_time = sum(range_chart.calculation_times) / len(range_chart.calculation_times)
            assert avg_time < 200  # < 200ms average


class TestRangeBarsErrorHandling:
    """Test Range Bars error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_tick_data(self, chart_config):
        """Test handling of invalid tick data"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Test with invalid close price
        invalid_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0,
            high=101.0,
            low=99.0,
            close=float('inf'),  # Invalid price
            volume=1000
        )
        
        # Should handle gracefully
        try:
            await range_chart.add_data_point(invalid_tick)
        except Exception as e:
            # Should handle with appropriate error
            assert "price" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_zero_volume_handling(self, chart_config):
        """Test handling of zero volume ticks"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # First normal tick
        normal_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await range_chart.add_data_point(normal_tick)
        
        # Zero volume tick
        zero_volume_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 16),
            open=100.0, high=102.0, low=100.0, close=101.0, volume=0
        )
        
        # Should handle without crashing
        await range_chart.add_data_point(zero_volume_tick)
        
        # Bar should still be updated
        assert range_chart.current_bar is not None
        assert range_chart.current_bar.close_price == 101.0
    
    @pytest.mark.asyncio
    async def test_extreme_price_gaps(self, chart_config):
        """Test handling of extreme price gaps"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Normal starting tick
        start_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await range_chart.add_data_point(start_tick)
        
        # Extreme gap up
        gap_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 16),
            open=100.0, high=500.0, low=100.0, close=450.0, volume=1000
        )
        
        # Should complete bar due to extreme range
        await range_chart.add_data_point(gap_tick)
        
        # Should have completed at least one bar
        assert len(range_chart.range_bars) > 0 or range_chart.current_bar is not None
    
    def test_invalid_range_configuration(self):
        """Test handling of invalid range configuration"""
        # Test with negative range size
        config = ChartConfig(
            symbol="TEST",
            timeframe=TimeFrame.FIVE_MINUTES,
            range_size=-1.0,
            range_type="points"
        )
        
        range_chart = RangeBarsChart("test_chart", config, Mock())
        
        # Should use positive range size or default
        assert range_chart.range_size > 0
    
    @pytest.mark.asyncio
    async def test_out_of_order_timestamps(self, chart_config):
        """Test handling of out-of-order timestamps"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Add tick with later timestamp
        later_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 20),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await range_chart.add_data_point(later_tick)
        
        # Add tick with earlier timestamp
        earlier_tick = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=102.0, low=100.0, close=101.0, volume=500
        )
        
        # Should handle gracefully (may ignore or process differently)
        await range_chart.add_data_point(earlier_tick)
        
        # Should not crash and maintain valid state
        assert range_chart.current_bar is not None


# Integration tests
class TestRangeBarsIntegration:
    """Integration tests for Range Bars with other components"""
    
    @pytest.mark.asyncio
    async def test_range_bars_with_indicators(self, chart_config):
        """Test Range Bars integration with indicators"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Mock indicator manager
        mock_indicator_manager = AsyncMock()
        range_chart.indicator_manager = mock_indicator_manager
        
        # Add ticks that complete bars
        for i in range(10):
            tick = OHLCV(
                timestamp=datetime(2024, 1, 1, 9, 15) + timedelta(minutes=i),
                open=100.0 + i * 6,  # Large movements to complete bars
                high=106.0 + i * 6,
                low=100.0 + i * 6,
                close=105.0 + i * 6,
                volume=1000
            )
            await range_chart.add_data_point(tick)
        
        # Should call indicator updates when bars complete
        assert mock_indicator_manager.update_all.call_count > 0
    
    @pytest.mark.asyncio
    async def test_real_time_processing(self, chart_config):
        """Test real-time tick processing"""
        range_chart = RangeBarsChart("test_chart", chart_config, Mock())
        
        # Simulate real-time tick stream
        base_price = 100.0
        
        for i in range(100):
            # Realistic price movement
            price_change = (i % 10 - 5) * 0.1
            current_price = base_price + price_change
            
            tick = OHLCV(
                timestamp=datetime(2024, 1, 1, 9, 15) + timedelta(seconds=i * 10),
                open=current_price,
                high=current_price + 0.05,
                low=current_price - 0.03,
                close=current_price + 0.02,
                volume=1000 + i % 50
            )
            
            await range_chart.add_data_point(tick)
        
        # Should have processed all ticks
        assert len(range_chart.data) == 100
        
        # Should have some completed bars
        total_bars = len(range_chart.range_bars)
        if range_chart.current_bar:
            total_bars += 1
        
        assert total_bars > 0
        assert total_bars < 100  # Should filter noise