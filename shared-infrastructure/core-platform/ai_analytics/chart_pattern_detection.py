#!/usr/bin/env python3
"""
GridWorks AI Chart Pattern Detection System
==========================================
Advanced pattern recognition using YOLOv8 and computer vision for Indian markets
"""

import asyncio
import cv2
import numpy as np
import pandas as pd
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import base64
from pathlib import Path
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Technical chart patterns for detection"""
    # Classic Reversal Patterns
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    
    # Continuation Patterns
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    WEDGE_RISING = "wedge_rising"
    WEDGE_FALLING = "wedge_falling"
    FLAG_BULLISH = "flag_bullish"
    FLAG_BEARISH = "flag_bearish"
    PENNANT = "pennant"
    
    # Rectangle Patterns
    RECTANGLE_BULLISH = "rectangle_bullish"
    RECTANGLE_BEARISH = "rectangle_bearish"
    
    # Candlestick Patterns
    DOJI = "doji"
    HAMMER = "hammer"
    HANGING_MAN = "hanging_man"
    SHOOTING_STAR = "shooting_star"
    ENGULFING_BULLISH = "engulfing_bullish"
    ENGULFING_BEARISH = "engulfing_bearish"
    
    # Indian Market Specific
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    HARAMI_BULLISH = "harami_bullish"
    HARAMI_BEARISH = "harami_bearish"


class ConfidenceLevel(Enum):
    """Pattern detection confidence levels"""
    VERY_HIGH = "very_high"  # 90%+
    HIGH = "high"           # 80-90%
    MEDIUM = "medium"       # 60-80%
    LOW = "low"            # 40-60%
    VERY_LOW = "very_low"  # <40%


class MarketCondition(Enum):
    """Market condition context"""
    BULLISH_TREND = "bullish_trend"
    BEARISH_TREND = "bearish_trend"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


@dataclass
class PatternDetection:
    """Detected chart pattern result"""
    pattern_id: str
    pattern_type: PatternType
    confidence: float
    confidence_level: ConfidenceLevel
    symbol: str
    timeframe: str
    detection_time: datetime
    price_levels: Dict[str, float]  # Support, resistance, target levels
    market_condition: MarketCondition
    expected_move: Dict[str, float]  # Direction and magnitude
    risk_reward_ratio: float
    validity_period: timedelta
    pattern_coordinates: List[Tuple[int, int]]  # Chart coordinates
    pattern_image_base64: Optional[str] = None
    voice_alert_triggered: bool = False
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if pattern has high confidence"""
        return self.confidence >= 0.8
    
    @property
    def expected_direction(self) -> str:
        """Get expected price direction"""
        return "bullish" if self.expected_move.get("direction", 0) > 0 else "bearish"


@dataclass
class ChartData:
    """Chart data for pattern detection"""
    symbol: str
    timeframe: str
    timestamps: List[datetime]
    open_prices: List[float]
    high_prices: List[float]
    low_prices: List[float]
    close_prices: List[float]
    volumes: List[float]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame"""
        return pd.DataFrame({
            'timestamp': self.timestamps,
            'open': self.open_prices,
            'high': self.high_prices,
            'low': self.low_prices,
            'close': self.close_prices,
            'volume': self.volumes
        })


class YOLOv8PatternDetector:
    """YOLOv8-based chart pattern detection"""
    
    def __init__(self, model_path: str = None):
        """Initialize YOLOv8 detector"""
        self.model_path = model_path or "models/chart_patterns_yolov8.pt"
        self.model = None
        self.pattern_classes = self._initialize_pattern_classes()
        
        # Mock YOLOv8 for development (replace with actual ultralytics import)
        self._initialize_mock_model()
    
    def _initialize_pattern_classes(self) -> Dict[int, PatternType]:
        """Initialize pattern class mapping"""
        return {
            0: PatternType.HEAD_AND_SHOULDERS,
            1: PatternType.INVERSE_HEAD_AND_SHOULDERS,
            2: PatternType.DOUBLE_TOP,
            3: PatternType.DOUBLE_BOTTOM,
            4: PatternType.ASCENDING_TRIANGLE,
            5: PatternType.DESCENDING_TRIANGLE,
            6: PatternType.SYMMETRICAL_TRIANGLE,
            7: PatternType.FLAG_BULLISH,
            8: PatternType.FLAG_BEARISH,
            9: PatternType.RECTANGLE_BULLISH,
            10: PatternType.RECTANGLE_BEARISH,
            11: PatternType.WEDGE_RISING,
            12: PatternType.WEDGE_FALLING,
            13: PatternType.DOJI,
            14: PatternType.HAMMER,
            15: PatternType.SHOOTING_STAR
        }
    
    def _initialize_mock_model(self):
        """Initialize mock YOLOv8 model for development"""
        # In production, replace with: from ultralytics import YOLO
        class MockYOLOModel:
            def predict(self, image, conf=0.6):
                # Mock prediction with realistic pattern detection
                mock_results = []
                
                # Simulate detecting a head and shoulders pattern
                if np.random.random() > 0.7:  # 30% chance of detection
                    class MockResult:
                        def __init__(self):
                            self.boxes = MockBoxes()
                    
                    class MockBoxes:
                        def __init__(self):
                            # Mock bounding box [x1, y1, x2, y2, confidence, class]
                            self.data = np.array([[100, 50, 400, 200, 0.85, 0]])  # Head and shoulders
                    
                    mock_results.append(MockResult())
                
                return mock_results
        
        self.model = MockYOLOModel()
        logger.info("Mock YOLOv8 model initialized for development")
    
    async def detect_patterns(self, chart_image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect patterns in chart image using YOLOv8"""
        try:
            # Run YOLOv8 inference
            results = self.model.predict(chart_image, conf=0.6)
            
            detected_patterns = []
            
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    boxes = result.boxes.data.cpu().numpy() if hasattr(result.boxes.data, 'cpu') else result.boxes.data
                    
                    for box in boxes:
                        x1, y1, x2, y2, confidence, class_id = box
                        
                        pattern_type = self.pattern_classes.get(int(class_id))
                        if pattern_type:
                            pattern_info = {
                                'pattern_type': pattern_type,
                                'confidence': float(confidence),
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                            }
                            detected_patterns.append(pattern_info)
            
            return detected_patterns
            
        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")
            return []


class TraditionalPatternDetector:
    """Traditional algorithmic pattern detection as fallback"""
    
    def __init__(self):
        """Initialize traditional pattern detector"""
        self.min_pattern_length = 10
        self.price_tolerance = 0.02  # 2% tolerance for pattern matching
    
    async def detect_head_and_shoulders(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Detect head and shoulders pattern"""
        if len(df) < 20:
            return None
        
        high_prices = df['high'].values
        close_prices = df['close'].values
        
        # Find potential peaks
        peaks = self._find_peaks(high_prices, min_distance=5)
        
        if len(peaks) >= 3:
            # Check for head and shoulders structure
            left_shoulder, head, right_shoulder = peaks[-3:]
            
            # Validate pattern structure
            if (high_prices[head] > high_prices[left_shoulder] and 
                high_prices[head] > high_prices[right_shoulder] and
                abs(high_prices[left_shoulder] - high_prices[right_shoulder]) / high_prices[head] < self.price_tolerance):
                
                # Calculate neckline
                neckline = min(close_prices[left_shoulder:head+1].min(), 
                              close_prices[head:right_shoulder+1].min())
                
                # Calculate target
                head_to_neckline = high_prices[head] - neckline
                target = neckline - head_to_neckline
                
                confidence = self._calculate_pattern_confidence(
                    high_prices, [left_shoulder, head, right_shoulder], "head_and_shoulders"
                )
                
                return {
                    'pattern_type': PatternType.HEAD_AND_SHOULDERS,
                    'confidence': confidence,
                    'key_points': [left_shoulder, head, right_shoulder],
                    'neckline': neckline,
                    'target': target,
                    'resistance': high_prices[head]
                }
        
        return None
    
    async def detect_double_top(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Detect double top pattern"""
        if len(df) < 15:
            return None
        
        high_prices = df['high'].values
        
        # Find peaks
        peaks = self._find_peaks(high_prices, min_distance=5)
        
        if len(peaks) >= 2:
            peak1, peak2 = peaks[-2:]
            
            # Check if peaks are approximately equal
            if abs(high_prices[peak1] - high_prices[peak2]) / high_prices[peak1] < self.price_tolerance:
                # Find valley between peaks
                valley_idx = peak1 + np.argmin(high_prices[peak1:peak2])
                valley_price = high_prices[valley_idx]
                
                # Calculate target
                peak_to_valley = high_prices[peak1] - valley_price
                target = valley_price - peak_to_valley
                
                confidence = self._calculate_pattern_confidence(
                    high_prices, [peak1, valley_idx, peak2], "double_top"
                )
                
                return {
                    'pattern_type': PatternType.DOUBLE_TOP,
                    'confidence': confidence,
                    'peaks': [peak1, peak2],
                    'valley': valley_idx,
                    'resistance': max(high_prices[peak1], high_prices[peak2]),
                    'support': valley_price,
                    'target': target
                }
        
        return None
    
    async def detect_triangle_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        high_prices = df['high'].values
        low_prices = df['low'].values
        
        # Find peaks and troughs
        peaks = self._find_peaks(high_prices, min_distance=3)
        troughs = self._find_peaks(-low_prices, min_distance=3)
        
        if len(peaks) >= 2 and len(troughs) >= 2:
            # Calculate trend lines
            peak_slope = self._calculate_slope(peaks[-2:], high_prices)
            trough_slope = self._calculate_slope(troughs[-2:], low_prices)
            
            # Determine triangle type
            if abs(peak_slope) < 0.001:  # Horizontal resistance
                pattern_type = PatternType.ASCENDING_TRIANGLE
                confidence = 0.75
            elif abs(trough_slope) < 0.001:  # Horizontal support
                pattern_type = PatternType.DESCENDING_TRIANGLE
                confidence = 0.75
            elif peak_slope < 0 and trough_slope > 0:  # Converging lines
                pattern_type = PatternType.SYMMETRICAL_TRIANGLE
                confidence = 0.70
            else:
                return patterns
            
            patterns.append({
                'pattern_type': pattern_type,
                'confidence': confidence,
                'peaks': peaks[-2:],
                'troughs': troughs[-2:],
                'upper_trendline_slope': peak_slope,
                'lower_trendline_slope': trough_slope
            })
        
        return patterns
    
    def _find_peaks(self, data: np.ndarray, min_distance: int = 5) -> List[int]:
        """Find peaks in price data"""
        peaks = []
        
        for i in range(min_distance, len(data) - min_distance):
            is_peak = True
            
            # Check if current point is higher than surrounding points
            for j in range(-min_distance, min_distance + 1):
                if j != 0 and data[i] <= data[i + j]:
                    is_peak = False
                    break
            
            if is_peak:
                peaks.append(i)
        
        return peaks
    
    def _calculate_slope(self, indices: List[int], prices: np.ndarray) -> float:
        """Calculate slope between two points"""
        if len(indices) < 2:
            return 0.0
        
        x1, x2 = indices[0], indices[1]
        y1, y2 = prices[x1], prices[x2]
        
        return (y2 - y1) / (x2 - x1) if x2 != x1 else 0.0
    
    def _calculate_pattern_confidence(self, prices: np.ndarray, key_points: List[int], pattern_type: str) -> float:
        """Calculate confidence score for detected pattern"""
        base_confidence = 0.6
        
        # Add confidence based on pattern clarity
        if pattern_type == "head_and_shoulders":
            if len(key_points) == 3:
                left_shoulder, head, right_shoulder = key_points
                
                # Check symmetry
                symmetry_score = 1 - abs(prices[left_shoulder] - prices[right_shoulder]) / prices[head]
                
                # Check head prominence
                head_prominence = (prices[head] - max(prices[left_shoulder], prices[right_shoulder])) / prices[head]
                
                confidence_boost = min(0.3, symmetry_score * 0.2 + head_prominence * 0.1)
                base_confidence += confidence_boost
        
        elif pattern_type == "double_top":
            if len(key_points) == 3:
                peak1, valley, peak2 = key_points
                
                # Check peak equality
                peak_equality = 1 - abs(prices[peak1] - prices[peak2]) / max(prices[peak1], prices[peak2])
                
                confidence_boost = min(0.25, peak_equality * 0.25)
                base_confidence += confidence_boost
        
        return min(0.95, base_confidence)


class ChartPatternAnalyzer:
    """Main chart pattern analysis engine"""
    
    def __init__(self):
        """Initialize pattern analyzer"""
        self.yolo_detector = YOLOv8PatternDetector()
        self.traditional_detector = TraditionalPatternDetector()
        self.detected_patterns = {}
        self.pattern_history = []
    
    async def analyze_chart(self, chart_data: ChartData, chart_image: np.ndarray = None) -> List[PatternDetection]:
        """Comprehensive chart pattern analysis"""
        detected_patterns = []
        
        try:
            # Method 1: YOLOv8 Computer Vision Detection
            if chart_image is not None:
                cv_patterns = await self.yolo_detector.detect_patterns(chart_image)
                detected_patterns.extend(await self._process_cv_patterns(cv_patterns, chart_data))
            
            # Method 2: Traditional Algorithmic Detection
            df = chart_data.to_dataframe()
            traditional_patterns = await self._detect_traditional_patterns(df, chart_data)
            detected_patterns.extend(traditional_patterns)
            
            # Method 3: Candlestick Pattern Detection
            candlestick_patterns = await self._detect_candlestick_patterns(df, chart_data)
            detected_patterns.extend(candlestick_patterns)
            
            # Deduplicate and rank patterns
            final_patterns = self._deduplicate_patterns(detected_patterns)
            
            # Store in history
            self.pattern_history.extend(final_patterns)
            
            # Keep only recent patterns
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.pattern_history = [p for p in self.pattern_history if p.detection_time > cutoff_time]
            
            return final_patterns
            
        except Exception as e:
            logger.error(f"Error in chart pattern analysis: {e}")
            return []
    
    async def _process_cv_patterns(self, cv_patterns: List[Dict], chart_data: ChartData) -> List[PatternDetection]:
        """Process computer vision detected patterns"""
        processed_patterns = []
        
        for cv_pattern in cv_patterns:
            # Create PatternDetection from CV result
            pattern_detection = PatternDetection(
                pattern_id=str(uuid.uuid4()),
                pattern_type=cv_pattern['pattern_type'],
                confidence=cv_pattern['confidence'],
                confidence_level=self._get_confidence_level(cv_pattern['confidence']),
                symbol=chart_data.symbol,
                timeframe=chart_data.timeframe,
                detection_time=datetime.now(),
                price_levels=self._calculate_price_levels(cv_pattern, chart_data),
                market_condition=self._assess_market_condition(chart_data),
                expected_move=self._calculate_expected_move(cv_pattern['pattern_type'], chart_data),
                risk_reward_ratio=self._calculate_risk_reward(cv_pattern['pattern_type']),
                validity_period=self._get_pattern_validity_period(cv_pattern['pattern_type']),
                pattern_coordinates=[(cv_pattern['bbox'][0], cv_pattern['bbox'][1]), 
                                   (cv_pattern['bbox'][2], cv_pattern['bbox'][3])]
            )
            
            processed_patterns.append(pattern_detection)
        
        return processed_patterns
    
    async def _detect_traditional_patterns(self, df: pd.DataFrame, chart_data: ChartData) -> List[PatternDetection]:
        """Detect patterns using traditional algorithms"""
        patterns = []
        
        # Head and Shoulders
        h_s_pattern = await self.traditional_detector.detect_head_and_shoulders(df)
        if h_s_pattern:
            patterns.append(self._create_pattern_detection(h_s_pattern, chart_data))
        
        # Double Top
        double_top = await self.traditional_detector.detect_double_top(df)
        if double_top:
            patterns.append(self._create_pattern_detection(double_top, chart_data))
        
        # Triangle Patterns
        triangle_patterns = await self.traditional_detector.detect_triangle_patterns(df)
        for triangle in triangle_patterns:
            patterns.append(self._create_pattern_detection(triangle, chart_data))
        
        return patterns
    
    async def _detect_candlestick_patterns(self, df: pd.DataFrame, chart_data: ChartData) -> List[PatternDetection]:
        """Detect candlestick patterns"""
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        # Get recent candlesticks
        recent_candles = df.tail(3)
        
        # Doji pattern
        for idx, row in recent_candles.iterrows():
            body_size = abs(row['close'] - row['open'])
            total_range = row['high'] - row['low']
            
            if body_size / total_range < 0.1:  # Small body relative to range
                doji_pattern = PatternDetection(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.DOJI,
                    confidence=0.8,
                    confidence_level=ConfidenceLevel.HIGH,
                    symbol=chart_data.symbol,
                    timeframe=chart_data.timeframe,
                    detection_time=datetime.now(),
                    price_levels={'doji_price': row['close']},
                    market_condition=self._assess_market_condition(chart_data),
                    expected_move={'direction': 0, 'magnitude': 0.02},
                    risk_reward_ratio=1.5,
                    validity_period=timedelta(hours=4),
                    pattern_coordinates=[]
                )
                patterns.append(doji_pattern)
        
        # Hammer pattern
        last_candle = recent_candles.iloc[-1]
        body_size = abs(last_candle['close'] - last_candle['open'])
        lower_shadow = min(last_candle['close'], last_candle['open']) - last_candle['low']
        upper_shadow = last_candle['high'] - max(last_candle['close'], last_candle['open'])
        
        if lower_shadow > 2 * body_size and upper_shadow < body_size:
            hammer_pattern = PatternDetection(
                pattern_id=str(uuid.uuid4()),
                pattern_type=PatternType.HAMMER,
                confidence=0.75,
                confidence_level=ConfidenceLevel.HIGH,
                symbol=chart_data.symbol,
                timeframe=chart_data.timeframe,
                detection_time=datetime.now(),
                price_levels={'hammer_low': last_candle['low'], 'resistance': last_candle['high']},
                market_condition=self._assess_market_condition(chart_data),
                expected_move={'direction': 1, 'magnitude': 0.03},
                risk_reward_ratio=2.0,
                validity_period=timedelta(hours=8),
                pattern_coordinates=[]
            )
            patterns.append(hammer_pattern)
        
        return patterns
    
    def _create_pattern_detection(self, pattern_dict: Dict, chart_data: ChartData) -> PatternDetection:
        """Create PatternDetection from traditional algorithm result"""
        return PatternDetection(
            pattern_id=str(uuid.uuid4()),
            pattern_type=pattern_dict['pattern_type'],
            confidence=pattern_dict['confidence'],
            confidence_level=self._get_confidence_level(pattern_dict['confidence']),
            symbol=chart_data.symbol,
            timeframe=chart_data.timeframe,
            detection_time=datetime.now(),
            price_levels={k: v for k, v in pattern_dict.items() if isinstance(v, (int, float))},
            market_condition=self._assess_market_condition(chart_data),
            expected_move=self._calculate_expected_move(pattern_dict['pattern_type'], chart_data),
            risk_reward_ratio=self._calculate_risk_reward(pattern_dict['pattern_type']),
            validity_period=self._get_pattern_validity_period(pattern_dict['pattern_type']),
            pattern_coordinates=[]
        )
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to level"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _assess_market_condition(self, chart_data: ChartData) -> MarketCondition:
        """Assess current market condition"""
        if len(chart_data.close_prices) < 20:
            return MarketCondition.SIDEWAYS
        
        recent_prices = chart_data.close_prices[-20:]
        trend_slope = (recent_prices[-1] - recent_prices[0]) / len(recent_prices)
        
        # Calculate volatility
        returns = [recent_prices[i] / recent_prices[i-1] - 1 for i in range(1, len(recent_prices))]
        volatility = np.std(returns) if returns else 0
        
        if volatility > 0.03:  # 3% daily volatility
            return MarketCondition.HIGH_VOLATILITY
        elif volatility < 0.01:  # 1% daily volatility
            return MarketCondition.LOW_VOLATILITY
        elif trend_slope > 0.001:
            return MarketCondition.BULLISH_TREND
        elif trend_slope < -0.001:
            return MarketCondition.BEARISH_TREND
        else:
            return MarketCondition.SIDEWAYS
    
    def _calculate_expected_move(self, pattern_type: PatternType, chart_data: ChartData) -> Dict[str, float]:
        """Calculate expected price move for pattern"""
        base_magnitude = 0.05  # 5% default move
        
        direction_map = {
            PatternType.HEAD_AND_SHOULDERS: -1,
            PatternType.INVERSE_HEAD_AND_SHOULDERS: 1,
            PatternType.DOUBLE_TOP: -1,
            PatternType.DOUBLE_BOTTOM: 1,
            PatternType.ASCENDING_TRIANGLE: 1,
            PatternType.DESCENDING_TRIANGLE: -1,
            PatternType.FLAG_BULLISH: 1,
            PatternType.FLAG_BEARISH: -1,
            PatternType.HAMMER: 1,
            PatternType.SHOOTING_STAR: -1,
        }
        
        direction = direction_map.get(pattern_type, 0)
        
        # Adjust magnitude based on pattern type
        if pattern_type in [PatternType.HEAD_AND_SHOULDERS, PatternType.DOUBLE_TOP]:
            magnitude = 0.08  # Larger moves for major reversal patterns
        elif pattern_type in [PatternType.TRIANGLE_PATTERNS]:
            magnitude = 0.06  # Medium moves for continuation patterns
        else:
            magnitude = base_magnitude
        
        return {
            'direction': direction,
            'magnitude': magnitude,
            'probability': 0.70  # 70% probability of move
        }
    
    def _calculate_risk_reward(self, pattern_type: PatternType) -> float:
        """Calculate risk-reward ratio for pattern"""
        risk_reward_map = {
            PatternType.HEAD_AND_SHOULDERS: 3.0,
            PatternType.DOUBLE_TOP: 2.5,
            PatternType.ASCENDING_TRIANGLE: 2.0,
            PatternType.FLAG_BULLISH: 2.5,
            PatternType.HAMMER: 2.0,
            PatternType.DOJI: 1.5,
        }
        
        return risk_reward_map.get(pattern_type, 2.0)
    
    def _get_pattern_validity_period(self, pattern_type: PatternType) -> timedelta:
        """Get validity period for pattern"""
        validity_map = {
            PatternType.HEAD_AND_SHOULDERS: timedelta(days=5),
            PatternType.DOUBLE_TOP: timedelta(days=3),
            PatternType.ASCENDING_TRIANGLE: timedelta(days=7),
            PatternType.FLAG_BULLISH: timedelta(hours=12),
            PatternType.HAMMER: timedelta(hours=8),
            PatternType.DOJI: timedelta(hours=4),
        }
        
        return validity_map.get(pattern_type, timedelta(days=2))
    
    def _calculate_price_levels(self, cv_pattern: Dict, chart_data: ChartData) -> Dict[str, float]:
        """Calculate price levels from CV pattern"""
        # Use recent price data to estimate levels
        recent_high = max(chart_data.high_prices[-20:]) if len(chart_data.high_prices) >= 20 else chart_data.high_prices[-1]
        recent_low = min(chart_data.low_prices[-20:]) if len(chart_data.low_prices) >= 20 else chart_data.low_prices[-1]
        current_price = chart_data.close_prices[-1]
        
        return {
            'resistance': recent_high,
            'support': recent_low,
            'current': current_price,
            'target': current_price * 1.05 if cv_pattern['pattern_type'].value.endswith('bullish') else current_price * 0.95
        }
    
    def _deduplicate_patterns(self, patterns: List[PatternDetection]) -> List[PatternDetection]:
        """Remove duplicate patterns and keep highest confidence"""
        if not patterns:
            return []
        
        # Group by pattern type and symbol
        pattern_groups = {}
        for pattern in patterns:
            key = f"{pattern.symbol}_{pattern.pattern_type.value}"
            if key not in pattern_groups:
                pattern_groups[key] = []
            pattern_groups[key].append(pattern)
        
        # Keep highest confidence pattern from each group
        deduplicated = []
        for group in pattern_groups.values():
            best_pattern = max(group, key=lambda p: p.confidence)
            deduplicated.append(best_pattern)
        
        # Sort by confidence
        return sorted(deduplicated, key=lambda p: p.confidence, reverse=True)
    
    async def get_pattern_summary(self, symbol: str = None, min_confidence: float = 0.6) -> Dict[str, Any]:
        """Get summary of detected patterns"""
        relevant_patterns = [
            p for p in self.pattern_history 
            if (symbol is None or p.symbol == symbol) and p.confidence >= min_confidence
        ]
        
        if not relevant_patterns:
            return {'total_patterns': 0, 'patterns': []}
        
        # Group by confidence level
        confidence_summary = {
            'very_high': len([p for p in relevant_patterns if p.confidence_level == ConfidenceLevel.VERY_HIGH]),
            'high': len([p for p in relevant_patterns if p.confidence_level == ConfidenceLevel.HIGH]),
            'medium': len([p for p in relevant_patterns if p.confidence_level == ConfidenceLevel.MEDIUM])
        }
        
        # Group by pattern type
        pattern_type_summary = {}
        for pattern in relevant_patterns:
            pattern_type = pattern.pattern_type.value
            if pattern_type not in pattern_type_summary:
                pattern_type_summary[pattern_type] = 0
            pattern_type_summary[pattern_type] += 1
        
        return {
            'total_patterns': len(relevant_patterns),
            'confidence_summary': confidence_summary,
            'pattern_type_summary': pattern_type_summary,
            'patterns': [asdict(p) for p in relevant_patterns[:10]]  # Top 10 patterns
        }


# Example usage and testing
async def main():
    """Example usage of chart pattern detection"""
    
    # Create sample chart data
    sample_data = ChartData(
        symbol="RELIANCE",
        timeframe="1D",
        timestamps=[datetime.now() - timedelta(days=i) for i in range(30, 0, -1)],
        open_prices=[2400 + np.random.normal(0, 50) for _ in range(30)],
        high_prices=[2450 + np.random.normal(0, 60) for _ in range(30)],
        low_prices=[2350 + np.random.normal(0, 40) for _ in range(30)],
        close_prices=[2420 + np.random.normal(0, 45) for _ in range(30)],
        volumes=[1000000 + np.random.normal(0, 200000) for _ in range(30)]
    )
    
    # Initialize pattern analyzer
    analyzer = ChartPatternAnalyzer()
    
    # Analyze patterns
    patterns = await analyzer.analyze_chart(sample_data)
    
    print(f"Detected {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"- {pattern.pattern_type.value}: {pattern.confidence:.2f} confidence")
        print(f"  Expected move: {pattern.expected_direction} ({pattern.expected_move['magnitude']:.1%})")
        print(f"  Risk-reward: {pattern.risk_reward_ratio}:1")
        print(f"  Valid until: {pattern.detection_time + pattern.validity_period}")
        print()
    
    # Get summary
    summary = await analyzer.get_pattern_summary("RELIANCE")
    print(f"Pattern Summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())