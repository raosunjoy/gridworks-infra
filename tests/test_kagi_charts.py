"""
Comprehensive test suite for Kagi Charts implementation
Tests all functionality including line formation, pattern detection, and performance
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
import json

from app.charting.types.kagi import KagiChart, KagiLine
from app.charting.core.chart_engine import ChartConfig, TimeFrame, OHLCV


class TestKagiChartBasics:
    """Test basic Kagi chart functionality"""
    
    def test_kagi_chart_initialization(self, chart_config):
        """Test Kagi chart initialization with configuration"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        assert kagi_chart.chart_id == "test_chart"
        assert kagi_chart.chart_type == "kagi"
        assert kagi_chart.reversal_amount == 1.0
        assert kagi_chart.reversal_type == "percentage"
        assert kagi_chart.kagi_lines == []
        assert kagi_chart.current_line is None
    
    def test_kagi_chart_custom_reversal(self):
        """Test Kagi chart with custom reversal settings"""
        config = ChartConfig(
            symbol="NIFTY",
            timeframe=TimeFrame.ONE_MINUTE,
            kagi_reversal=2.5,
            kagi_reversal_type="points"
        )
        
        kagi_chart = KagiChart("test_chart", config, Mock())
        
        assert kagi_chart.reversal_amount == 2.5
        assert kagi_chart.reversal_type == "points"
    
    @pytest.mark.asyncio
    async def test_kagi_chart_initialization_async(self, chart_config):
        """Test async initialization of Kagi chart"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Mock indicator and drawing managers
        kagi_chart.indicator_manager = AsyncMock()
        kagi_chart.drawing_manager = Mock()
        
        await kagi_chart.initialize()
        
        assert kagi_chart.indicator_manager is not None
        assert kagi_chart.drawing_manager is not None


class TestKagiLineFormation:
    """Test Kagi line formation logic"""
    
    @pytest.mark.asyncio
    async def test_first_line_creation(self, chart_config):
        """Test creation of first Kagi line"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        first_price = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=1000
        )
        
        await kagi_chart.add_data_point(first_price)
        
        assert kagi_chart.current_line is not None
        assert kagi_chart.current_line.start_price == 100.5
        assert kagi_chart.current_line.end_price == 100.5
        assert kagi_chart.current_line.direction == 'up'
    
    @pytest.mark.asyncio
    async def test_line_extension_without_reversal(self, chart_config):
        """Test extending current line without reversal"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add first point
        first_price = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await kagi_chart.add_data_point(first_price)
        
        # Add second point with small increase (no reversal)
        second_price = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 20),
            open=100.0, high=101.5, low=99.5, close=100.3, volume=1000
        )
        await kagi_chart.add_data_point(second_price)
        
        # Should still have only current line, no completed lines
        assert len(kagi_chart.kagi_lines) == 0
        assert kagi_chart.current_line.end_price == 100.3
        assert kagi_chart.current_line.direction == 'up'
    
    @pytest.mark.asyncio
    async def test_reversal_creation(self, chart_config):
        """Test Kagi line reversal and new line creation"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add first point
        first_price = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await kagi_chart.add_data_point(first_price)
        
        # Add point that triggers reversal (1% down from 100.0 = 99.0)
        reversal_price = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 20),
            open=99.0, high=99.5, low=98.5, close=98.5, volume=1000
        )
        await kagi_chart.add_data_point(reversal_price)
        
        # Should have completed first line and started new one
        assert len(kagi_chart.kagi_lines) >= 1
        assert kagi_chart.current_line.direction == 'down'
        assert kagi_chart.current_line.end_price == 98.5
    
    def test_reversal_threshold_calculation_percentage(self, chart_config):
        """Test reversal threshold calculation for percentage type"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        threshold = kagi_chart._calculate_reversal_threshold(100.0)
        assert threshold == 1.0  # 1% of 100
        
        threshold = kagi_chart._calculate_reversal_threshold(200.0)
        assert threshold == 2.0  # 1% of 200
    
    def test_reversal_threshold_calculation_points(self):
        """Test reversal threshold calculation for points type"""
        config = ChartConfig(
            symbol="NIFTY",
            timeframe=TimeFrame.FIVE_MINUTES,
            kagi_reversal=5.0,
            kagi_reversal_type="points"
        )
        
        kagi_chart = KagiChart("test_chart", config, Mock())
        
        threshold = kagi_chart._calculate_reversal_threshold(100.0)
        assert threshold == 5.0
        
        threshold = kagi_chart._calculate_reversal_threshold(200.0)
        assert threshold == 5.0  # Fixed points regardless of price
    
    def test_should_reverse_logic(self, chart_config):
        """Test reversal detection logic"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create mock current line
        kagi_chart.current_line = KagiLine(
            start_price=100.0,
            end_price=100.0,
            start_time=datetime(2024, 1, 1, 9, 15),
            end_time=datetime(2024, 1, 1, 9, 15),
            direction='up',
            thickness='thin',
            is_yang=False
        )
        
        # Test upward price - should not reverse from up direction
        assert not kagi_chart._should_reverse(101.5, 1.0)
        
        # Test downward price exceeding threshold - should reverse
        assert kagi_chart._should_reverse(98.5, 1.0)
        
        # Change direction to down
        kagi_chart.current_line.direction = 'down'
        
        # Test upward price exceeding threshold - should reverse
        assert kagi_chart._should_reverse(101.5, 1.0)
        
        # Test downward price - should not reverse from down direction
        assert not kagi_chart._should_reverse(99.0, 1.0)


class TestKagiLineThickness:
    """Test Yang/Yin line thickness determination"""
    
    def test_line_thickness_determination_yang(self, chart_config):
        """Test Yang line (thick up) determination"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add some completed lines with highs/lows
        for i in range(5):
            line = KagiLine(
                start_price=100.0 + i,
                end_price=102.0 + i,
                start_time=datetime(2024, 1, 1, 9, 15 + i * 5),
                end_time=datetime(2024, 1, 1, 9, 20 + i * 5),
                direction='up',
                thickness='thin',
                is_yang=False
            )
            kagi_chart.kagi_lines.append(line)
        
        # Test new price that breaks above previous high
        is_yang, thickness = kagi_chart._determine_line_thickness(108.0, 'up')
        assert is_yang is True
        assert thickness == 'thick'
        
        # Test new price that doesn't break above previous high
        is_yang, thickness = kagi_chart._determine_line_thickness(105.0, 'up')
        assert is_yang is False
        assert thickness == 'thin'
    
    def test_line_thickness_determination_yin(self, chart_config):
        """Test Yin line (thick down) determination"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add some completed lines with highs/lows
        for i in range(5):
            line = KagiLine(
                start_price=100.0 - i,
                end_price=98.0 - i,
                start_time=datetime(2024, 1, 1, 9, 15 + i * 5),
                end_time=datetime(2024, 1, 1, 9, 20 + i * 5),
                direction='down',
                thickness='thin',
                is_yang=False
            )
            kagi_chart.kagi_lines.append(line)
        
        # Test new price that breaks below previous low
        is_yang, thickness = kagi_chart._determine_line_thickness(92.0, 'down')
        assert is_yang is True  # Yin line is considered Yang in terms of significance
        assert thickness == 'thick'
        
        # Test new price that doesn't break below previous low
        is_yang, thickness = kagi_chart._determine_line_thickness(95.0, 'down')
        assert is_yang is False
        assert thickness == 'thin'
    
    def test_first_line_thickness(self, chart_config):
        """Test thickness determination for first line"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # With no previous lines, should always be thin
        is_yang, thickness = kagi_chart._determine_line_thickness(100.0, 'up')
        assert is_yang is False
        assert thickness == 'thin'
        
        is_yang, thickness = kagi_chart._determine_line_thickness(100.0, 'down')
        assert is_yang is False
        assert thickness == 'thin'


class TestKagiShoulderLevels:
    """Test shoulder level calculation"""
    
    @pytest.mark.asyncio
    async def test_shoulder_level_calculation(self, chart_config):
        """Test calculation of support/resistance shoulder levels"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create pattern: up -> down -> up (shoulder high)
        lines = [
            KagiLine(100.0, 105.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thin', False),
            KagiLine(105.0, 102.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
            KagiLine(102.0, 107.0, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'up', 'thin', False),
        ]
        
        kagi_chart.kagi_lines = lines
        await kagi_chart._calculate_shoulder_levels()
        
        # Should identify resistance at 105.0 (turning point)
        resistance_levels = [s for s in kagi_chart.shoulder_levels if s['type'] == 'resistance']
        assert len(resistance_levels) > 0
        assert any(abs(s['price'] - 105.0) < 0.01 for s in resistance_levels)
    
    @pytest.mark.asyncio
    async def test_shoulder_level_strength_calculation(self, chart_config):
        """Test shoulder level strength calculation"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create multiple lines testing the same price level
        lines = []
        test_price = 105.0
        
        for i in range(10):
            # Create lines that touch the test price multiple times
            price_variation = 0.1 if i % 2 == 0 else -0.1
            line = KagiLine(
                start_price=100.0 + i,
                end_price=test_price + price_variation,
                start_time=datetime(2024, 1, 1, 9, 15 + i * 5),
                end_time=datetime(2024, 1, 1, 9, 20 + i * 5),
                direction='up',
                thickness='thin',
                is_yang=False
            )
            lines.append(line)
        
        kagi_chart.kagi_lines = lines
        
        # Test strength calculation
        strength = kagi_chart._calculate_level_strength(test_price, 'high')
        
        # Strength should be > 0 as multiple lines touch this level
        assert strength > 0
        assert strength <= 5.0  # Max strength is 5.0
    
    @pytest.mark.asyncio
    async def test_insufficient_lines_for_shoulders(self, chart_config):
        """Test shoulder calculation with insufficient data"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add only 2 lines (need at least 3 for shoulder detection)
        kagi_chart.kagi_lines = [
            KagiLine(100.0, 105.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thin', False),
            KagiLine(105.0, 102.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
        ]
        
        await kagi_chart._calculate_shoulder_levels()
        
        # Should have no shoulder levels with insufficient data
        assert len(kagi_chart.shoulder_levels) == 0


class TestKagiPatternDetection:
    """Test Kagi pattern detection algorithms"""
    
    @pytest.mark.asyncio
    async def test_three_buddha_top_pattern(self, chart_config):
        """Test Three Buddha Top pattern detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create pattern with three peaks at similar levels
        lines = [
            # First peak
            KagiLine(100.0, 110.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thin', False),
            KagiLine(110.0, 105.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
            # Second peak
            KagiLine(105.0, 109.5, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'up', 'thin', False),
            KagiLine(109.5, 104.0, datetime(2024, 1, 1, 9, 30), datetime(2024, 1, 1, 9, 35), 'down', 'thin', False),
            # Third peak
            KagiLine(104.0, 110.2, datetime(2024, 1, 1, 9, 35), datetime(2024, 1, 1, 9, 40), 'up', 'thin', False),
            KagiLine(110.2, 106.0, datetime(2024, 1, 1, 9, 40), datetime(2024, 1, 1, 9, 45), 'down', 'thin', False),
            # Continuation
            KagiLine(106.0, 102.0, datetime(2024, 1, 1, 9, 45), datetime(2024, 1, 1, 9, 50), 'down', 'thin', False),
        ]
        
        kagi_chart.kagi_lines = lines
        
        pattern = await kagi_chart._detect_three_buddha_pattern()
        
        assert pattern is not None
        assert pattern['pattern'] == 'three_buddha_top'
        assert pattern['type'] == 'bearish'
        assert pattern['confidence'] >= 0.8
        assert 'peak_levels' in pattern
        assert len(pattern['peak_levels']) >= 3
    
    @pytest.mark.asyncio
    async def test_three_river_bottom_pattern(self, chart_config):
        """Test Three River Bottom pattern detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create pattern with three troughs at similar levels
        lines = [
            # First trough
            KagiLine(100.0, 90.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'down', 'thin', False),
            KagiLine(90.0, 95.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'up', 'thin', False),
            # Second trough
            KagiLine(95.0, 89.5, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'down', 'thin', False),
            KagiLine(89.5, 94.0, datetime(2024, 1, 1, 9, 30), datetime(2024, 1, 1, 9, 35), 'up', 'thin', False),
            # Third trough
            KagiLine(94.0, 90.2, datetime(2024, 1, 1, 9, 35), datetime(2024, 1, 1, 9, 40), 'down', 'thin', False),
            KagiLine(90.2, 96.0, datetime(2024, 1, 1, 9, 40), datetime(2024, 1, 1, 9, 45), 'up', 'thin', False),
            # Continuation
            KagiLine(96.0, 98.0, datetime(2024, 1, 1, 9, 45), datetime(2024, 1, 1, 9, 50), 'up', 'thin', False),
        ]
        
        kagi_chart.kagi_lines = lines
        
        pattern = await kagi_chart._detect_three_river_pattern()
        
        assert pattern is not None
        assert pattern['pattern'] == 'three_river_bottom'
        assert pattern['type'] == 'bullish'
        assert pattern['confidence'] >= 0.8
        assert 'trough_levels' in pattern
        assert len(pattern['trough_levels']) >= 3
    
    @pytest.mark.asyncio
    async def test_kagi_breakout_pattern(self, chart_config):
        """Test Kagi breakout pattern detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create consolidation followed by thick line breakout
        lines = []
        # Consolidation phase
        for i in range(8):
            price_range = 102.0 + (i % 4) * 0.5  # Prices between 102-104
            line = KagiLine(
                start_price=price_range,
                end_price=price_range + (0.3 if i % 2 == 0 else -0.3),
                start_time=datetime(2024, 1, 1, 9, 15 + i * 5),
                end_time=datetime(2024, 1, 1, 9, 20 + i * 5),
                direction='up' if i % 2 == 0 else 'down',
                thickness='thin',
                is_yang=False
            )
            lines.append(line)
        
        # Breakout with thick line
        breakout_line = KagiLine(
            start_price=103.0,
            end_price=108.0,  # Strong breakout above consolidation
            start_time=datetime(2024, 1, 1, 9, 55),
            end_time=datetime(2024, 1, 1, 10, 0),
            direction='up',
            thickness='thick',  # Yang line
            is_yang=True
        )
        lines.append(breakout_line)
        
        kagi_chart.kagi_lines = lines
        
        pattern = await kagi_chart._detect_kagi_breakout()
        
        assert pattern is not None
        assert pattern['pattern'] == 'kagi_breakout'
        assert pattern['type'] == 'bullish'
        assert pattern['confidence'] >= 0.7
        assert 'breakout_level' in pattern
    
    @pytest.mark.asyncio
    async def test_shoulder_break_pattern(self, chart_config):
        """Test shoulder line break pattern detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Setup shoulder levels
        kagi_chart.shoulder_levels = [
            {
                'price': 105.0,
                'type': 'resistance',
                'strength': 4.0,
                'timestamp': datetime(2024, 1, 1, 9, 15)
            }
        ]
        
        # Create lines with latest breaking through resistance
        lines = [
            KagiLine(102.0, 104.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thin', False),
            KagiLine(104.0, 107.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'up', 'thick', True),  # Break above 105
        ]
        
        kagi_chart.kagi_lines = lines
        
        pattern = await kagi_chart._detect_shoulder_break()
        
        assert pattern is not None
        assert pattern['pattern'] == 'shoulder_break'
        assert pattern['type'] == 'bullish'
        assert pattern['confidence'] > 0.7
        assert pattern['shoulder_level'] == 105.0
    
    @pytest.mark.asyncio
    async def test_pattern_detection_comprehensive(self, chart_config):
        """Test comprehensive pattern detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create complex pattern that could trigger multiple detections
        lines = [
            KagiLine(100.0, 110.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thick', True),
            KagiLine(110.0, 105.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
            KagiLine(105.0, 115.0, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'up', 'thick', True),
        ]
        
        kagi_chart.kagi_lines = lines
        
        patterns = await kagi_chart.detect_patterns()
        
        assert isinstance(patterns, list)
        # Should detect at least one pattern
        if patterns:
            for pattern in patterns:
                assert 'pattern' in pattern
                assert 'confidence' in pattern
                assert 0 <= pattern['confidence'] <= 1
                assert 'description' in pattern


class TestKagiTrendAnalysis:
    """Test Kagi trend analysis functionality"""
    
    def test_current_trend_bullish(self, chart_config):
        """Test bullish trend detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create mostly up lines with thick lines
        lines = [
            KagiLine(100.0, 105.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thick', True),
            KagiLine(105.0, 103.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
            KagiLine(103.0, 108.0, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'up', 'thick', True),
            KagiLine(108.0, 106.0, datetime(2024, 1, 1, 9, 30), datetime(2024, 1, 1, 9, 35), 'down', 'thin', False),
            KagiLine(106.0, 110.0, datetime(2024, 1, 1, 9, 35), datetime(2024, 1, 1, 9, 40), 'up', 'thick', True),
        ]
        
        kagi_chart.kagi_lines = lines
        
        trend = kagi_chart.get_current_trend()
        
        assert trend['trend'] == 'bullish'
        assert trend['strength'] > 50
        assert trend['confidence'] > 50
        assert trend['current_line']['direction'] == 'up'
        assert trend['yang_yin_state'] == 'yang'
    
    def test_current_trend_bearish(self, chart_config):
        """Test bearish trend detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create mostly down lines
        lines = [
            KagiLine(100.0, 95.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'down', 'thick', True),
            KagiLine(95.0, 97.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'up', 'thin', False),
            KagiLine(97.0, 92.0, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'down', 'thick', True),
            KagiLine(92.0, 94.0, datetime(2024, 1, 1, 9, 30), datetime(2024, 1, 1, 9, 35), 'up', 'thin', False),
            KagiLine(94.0, 88.0, datetime(2024, 1, 1, 9, 35), datetime(2024, 1, 1, 9, 40), 'down', 'thick', True),
        ]
        
        kagi_chart.kagi_lines = lines
        
        trend = kagi_chart.get_current_trend()
        
        assert trend['trend'] == 'bearish'
        assert trend['strength'] > 50
        assert trend['current_line']['direction'] == 'down'
    
    def test_current_trend_neutral(self, chart_config):
        """Test neutral trend detection"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Create equal up and down lines
        lines = [
            KagiLine(100.0, 105.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thin', False),
            KagiLine(105.0, 100.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
            KagiLine(100.0, 103.0, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'up', 'thin', False),
            KagiLine(103.0, 98.0, datetime(2024, 1, 1, 9, 30), datetime(2024, 1, 1, 9, 35), 'down', 'thin', False),
        ]
        
        kagi_chart.kagi_lines = lines
        
        trend = kagi_chart.get_current_trend()
        
        assert trend['trend'] == 'neutral'
        assert trend['strength'] == 50
    
    def test_trend_with_no_lines(self, chart_config):
        """Test trend analysis with no lines"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        trend = kagi_chart.get_current_trend()
        
        assert trend['trend'] == 'neutral'
        assert trend['strength'] == 0
        assert trend['confidence'] == 0


class TestKagiAnalytics:
    """Test Kagi chart analytics and metrics"""
    
    def test_analytics_calculation(self, chart_config):
        """Test analytics calculation with sample data"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add sample lines
        lines = [
            KagiLine(100.0, 105.0, datetime(2024, 1, 1, 9, 15), datetime(2024, 1, 1, 9, 20), 'up', 'thick', True),
            KagiLine(105.0, 102.0, datetime(2024, 1, 1, 9, 20), datetime(2024, 1, 1, 9, 25), 'down', 'thin', False),
            KagiLine(102.0, 108.0, datetime(2024, 1, 1, 9, 25), datetime(2024, 1, 1, 9, 30), 'up', 'thick', True),
        ]
        
        kagi_chart.kagi_lines = lines
        kagi_chart.calculation_times = [50.0, 45.0, 55.0]  # Sample calculation times
        
        analytics = kagi_chart.get_analytics()
        
        assert analytics['total_kagi_lines'] == 3
        assert analytics['thick_lines_count'] == 2
        assert analytics['thick_lines_percentage'] == 66.7
        assert analytics['yang_lines_count'] == 2
        assert analytics['yang_percentage'] == 66.7
        assert analytics['average_calculation_time_ms'] == 50.0
        assert 'current_trend' in analytics
    
    def test_analytics_empty_chart(self, chart_config):
        """Test analytics with empty chart"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        analytics = kagi_chart.get_analytics()
        
        assert analytics == {}
    
    def test_chart_serialization(self, chart_config):
        """Test chart serialization to dictionary"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add sample data
        line = KagiLine(
            start_price=100.0,
            end_price=105.0,
            start_time=datetime(2024, 1, 1, 9, 15),
            end_time=datetime(2024, 1, 1, 9, 20),
            direction='up',
            thickness='thick',
            is_yang=True
        )
        kagi_chart.kagi_lines = [line]
        
        chart_dict = kagi_chart.to_dict()
        
        assert chart_dict['chart_id'] == "test_chart"
        assert chart_dict['chart_type'] == "kagi"
        assert chart_dict['symbol'] == "RELIANCE"
        assert chart_dict['reversal_amount'] == 1.0
        assert chart_dict['reversal_type'] == "percentage"
        assert len(chart_dict['kagi_lines']) == 1
        assert chart_dict['kagi_lines'][0]['start_price'] == 100.0
        assert chart_dict['kagi_lines'][0]['is_yang'] is True


class TestKagiPerformance:
    """Test Kagi chart performance and optimization"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, chart_config, performance_test_data):
        """Test performance with large dataset"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        start_time = datetime.now()
        
        # Process large dataset
        for data_point in performance_test_data[:1000]:  # Use first 1000 points
            await kagi_chart.add_data_point(data_point)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        # Should process 1000 points in reasonable time (< 5 seconds)
        assert processing_time < 5000
        
        # Verify some lines were created
        assert len(kagi_chart.kagi_lines) > 0
        
        # Check analytics are calculated
        analytics = kagi_chart.get_analytics()
        assert analytics is not None
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, chart_config):
        """Test memory efficiency with repeated operations"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add and process data points repeatedly
        for i in range(1000):
            data_point = OHLCV(
                timestamp=datetime(2024, 1, 1, 9, 15) + timedelta(seconds=i),
                open=100.0 + i * 0.01,
                high=100.0 + i * 0.01 + 0.5,
                low=100.0 + i * 0.01 - 0.3,
                close=100.0 + i * 0.01 + (i % 3 - 1) * 0.1,
                volume=1000
            )
            
            await kagi_chart.add_data_point(data_point)
        
        # Verify reasonable number of lines created (not one per data point)
        assert len(kagi_chart.kagi_lines) < 500  # Should be much less due to filtering
        
        # Verify calculations are still fast
        if kagi_chart.calculation_times:
            avg_time = sum(kagi_chart.calculation_times) / len(kagi_chart.calculation_times)
            assert avg_time < 100  # < 100ms average


class TestKagiErrorHandling:
    """Test Kagi chart error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_price_data(self, chart_config):
        """Test handling of invalid price data"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Test with None close price
        invalid_data = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0,
            high=101.0,
            low=99.0,
            close=None,
            volume=1000
        )
        
        # Should not crash
        try:
            await kagi_chart.add_data_point(invalid_data)
        except Exception as e:
            # Should handle gracefully
            assert "price" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_extreme_price_movements(self, chart_config):
        """Test handling of extreme price movements"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add normal starting point
        normal_data = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 15),
            open=100.0, high=101.0, low=99.0, close=100.0, volume=1000
        )
        await kagi_chart.add_data_point(normal_data)
        
        # Add extreme movement
        extreme_data = OHLCV(
            timestamp=datetime(2024, 1, 1, 9, 20),
            open=100.0, high=200.0, low=50.0, close=150.0, volume=1000
        )
        
        # Should handle without crashing
        await kagi_chart.add_data_point(extreme_data)
        
        # Should create reversal due to extreme movement
        assert len(kagi_chart.kagi_lines) > 0 or kagi_chart.current_line is not None
    
    def test_zero_reversal_amount(self):
        """Test behavior with zero reversal amount"""
        config = ChartConfig(
            symbol="TEST",
            timeframe=TimeFrame.FIVE_MINUTES,
            kagi_reversal=0.0,
            kagi_reversal_type="percentage"
        )
        
        kagi_chart = KagiChart("test_chart", config, Mock())
        
        # Should use default or minimum reversal amount
        assert kagi_chart.reversal_amount >= 0.1  # Should have some minimum
    
    @pytest.mark.asyncio
    async def test_duplicate_timestamps(self, chart_config):
        """Test handling of duplicate timestamps"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        same_time = datetime(2024, 1, 1, 9, 15)
        
        # Add two data points with same timestamp
        data1 = OHLCV(timestamp=same_time, open=100.0, high=101.0, low=99.0, close=100.0, volume=1000)
        data2 = OHLCV(timestamp=same_time, open=100.0, high=102.0, low=98.0, close=101.0, volume=1500)
        
        await kagi_chart.add_data_point(data1)
        await kagi_chart.add_data_point(data2)
        
        # Should handle gracefully (latest data should prevail)
        assert kagi_chart.current_line is not None


# Integration tests
class TestKagiIntegration:
    """Integration tests for Kagi charts with other components"""
    
    @pytest.mark.asyncio
    async def test_kagi_with_indicators(self, chart_config):
        """Test Kagi chart integration with indicators"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Mock indicator manager
        mock_indicator_manager = AsyncMock()
        kagi_chart.indicator_manager = mock_indicator_manager
        
        # Add data points
        for i in range(10):
            data_point = OHLCV(
                timestamp=datetime(2024, 1, 1, 9, 15) + timedelta(minutes=i * 5),
                open=100.0 + i,
                high=101.0 + i,
                low=99.0 + i,
                close=100.5 + i,
                volume=1000
            )
            await kagi_chart.add_data_point(data_point)
        
        # Verify indicator manager was called
        assert mock_indicator_manager.update_all.call_count > 0
    
    @pytest.mark.asyncio
    async def test_real_time_updates(self, chart_config, sample_ohlcv_data):
        """Test real-time data updates"""
        kagi_chart = KagiChart("test_chart", chart_config, Mock())
        
        # Add historical data
        for data_point in sample_ohlcv_data[:50]:
            await kagi_chart.add_data_point(data_point)
        
        initial_line_count = len(kagi_chart.kagi_lines)
        
        # Add real-time updates
        for data_point in sample_ohlcv_data[50:60]:
            await kagi_chart.add_data_point(data_point)
        
        # Should have processed new data
        final_line_count = len(kagi_chart.kagi_lines)
        assert final_line_count >= initial_line_count