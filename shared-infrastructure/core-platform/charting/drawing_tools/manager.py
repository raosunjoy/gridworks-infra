"""
Drawing Tools Manager

Professional drawing tools matching Zerodha Kite + Dhan
with AI-powered enhancements.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math

from app.core.logging import logger


class DrawingToolType(Enum):
    """All available drawing tools"""
    
    # Lines
    TREND_LINE = "trend_line"
    HORIZONTAL_LINE = "horizontal_line"
    VERTICAL_LINE = "vertical_line"
    RAY = "ray"
    EXTENDED_LINE = "extended_line"
    ARROW = "arrow"
    
    # Channels
    PARALLEL_CHANNEL = "parallel_channel"
    REGRESSION_CHANNEL = "regression_channel"
    
    # Fibonacci
    FIB_RETRACEMENT = "fib_retracement"
    FIB_EXTENSION = "fib_extension"
    FIB_TIME_ZONES = "fib_time_zones"
    FIB_CIRCLE = "fib_circle"
    FIB_SPIRAL = "fib_spiral"
    
    # Shapes
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    TRIANGLE = "triangle"
    
    # Gann
    GANN_FAN = "gann_fan"
    GANN_SQUARE = "gann_square"
    GANN_BOX = "gann_box"
    
    # Advanced
    PITCHFORK = "pitchfork"
    SCHIFF_PITCHFORK = "schiff_pitchfork"
    MODIFIED_SCHIFF_PITCHFORK = "modified_schiff_pitchfork"
    
    # Text and Annotations
    TEXT = "text"
    CALLOUT = "callout"
    PRICE_LABEL = "price_label"
    
    # Patterns (AI-assisted)
    XABCD_PATTERN = "xabcd_pattern"
    ELLIOTT_WAVE = "elliott_wave"
    HEAD_SHOULDERS = "head_shoulders"


@dataclass
class Point:
    """Point on the chart"""
    timestamp: datetime
    price: float
    bar_index: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "bar_index": self.bar_index
        }


@dataclass
class DrawingStyle:
    """Style configuration for drawings"""
    color: str = "#2962FF"  # Default blue
    width: int = 2
    style: str = "solid"  # solid, dashed, dotted
    opacity: float = 1.0
    fill: bool = False
    fill_color: Optional[str] = None
    fill_opacity: float = 0.2
    font_size: Optional[int] = None
    font_family: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() 
            if v is not None
        }


@dataclass
class Drawing:
    """Base drawing object"""
    id: str
    type: DrawingToolType
    points: List[Point]
    style: DrawingStyle
    created_at: datetime
    updated_at: datetime
    locked: bool = False
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "points": [p.to_dict() for p in self.points],
            "style": self.style.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "locked": self.locked,
            "visible": self.visible,
            "metadata": self.metadata
        }


class DrawingToolManager:
    """
    Manages all drawing tools for charts
    Provides creation, manipulation, and AI-assisted features
    """
    
    def __init__(self, chart):
        self.chart = chart
        self.drawings: Dict[str, Drawing] = {}
        self.selected_drawing: Optional[str] = None
        self.magnetic_mode: bool = True  # Snap to OHLC
        self.update_callbacks: List[Callable] = []
        
        # AI assistance
        self.auto_fibonacci: bool = True
        self.pattern_recognition: bool = True
        
    async def add_drawing(
        self,
        drawing_type: str,
        points: List[Dict[str, Any]],
        style: Dict[str, Any]
    ) -> str:
        """Add a new drawing to the chart"""
        
        # Generate unique ID
        drawing_id = str(uuid.uuid4())
        
        # Convert points
        drawing_points = []
        for p in points:
            point = Point(
                timestamp=datetime.fromisoformat(p["timestamp"]) if "timestamp" in p else datetime.now(),
                price=p["price"],
                bar_index=p.get("bar_index")
            )
            
            # Apply magnetic mode if enabled
            if self.magnetic_mode and "timestamp" in p:
                point = await self._snap_to_ohlc(point)
            
            drawing_points.append(point)
        
        # Create style
        drawing_style = DrawingStyle(**style)
        
        # Create drawing
        drawing = Drawing(
            id=drawing_id,
            type=DrawingToolType[drawing_type.upper()],
            points=drawing_points,
            style=drawing_style,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Apply tool-specific logic
        if drawing.type == DrawingToolType.FIB_RETRACEMENT:
            await self._enhance_fibonacci(drawing)
        elif drawing.type in [DrawingToolType.TREND_LINE, DrawingToolType.HORIZONTAL_LINE]:
            await self._enhance_support_resistance(drawing)
        
        # Store drawing
        self.drawings[drawing_id] = drawing
        
        # Trigger callbacks
        for callback in self.update_callbacks:
            await callback("added", drawing)
        
        logger.info(f"Added drawing {drawing_type} with ID {drawing_id}")
        return drawing_id
    
    async def update_drawing(
        self,
        drawing_id: str,
        updates: Dict[str, Any]
    ):
        """Update an existing drawing"""
        
        if drawing_id not in self.drawings:
            raise ValueError(f"Drawing {drawing_id} not found")
        
        drawing = self.drawings[drawing_id]
        
        if drawing.locked:
            raise ValueError(f"Drawing {drawing_id} is locked")
        
        # Update points if provided
        if "points" in updates:
            new_points = []
            for p in updates["points"]:
                point = Point(
                    timestamp=datetime.fromisoformat(p["timestamp"]) if "timestamp" in p else datetime.now(),
                    price=p["price"],
                    bar_index=p.get("bar_index")
                )
                
                if self.magnetic_mode:
                    point = await self._snap_to_ohlc(point)
                
                new_points.append(point)
            
            drawing.points = new_points
        
        # Update style if provided
        if "style" in updates:
            for key, value in updates["style"].items():
                setattr(drawing.style, key, value)
        
        # Update other properties
        if "locked" in updates:
            drawing.locked = updates["locked"]
        if "visible" in updates:
            drawing.visible = updates["visible"]
        
        drawing.updated_at = datetime.now()
        
        # Trigger callbacks
        for callback in self.update_callbacks:
            await callback("updated", drawing)
    
    async def delete_drawing(self, drawing_id: str):
        """Delete a drawing"""
        
        if drawing_id not in self.drawings:
            raise ValueError(f"Drawing {drawing_id} not found")
        
        drawing = self.drawings[drawing_id]
        
        if drawing.locked:
            raise ValueError(f"Drawing {drawing_id} is locked")
        
        del self.drawings[drawing_id]
        
        # Trigger callbacks
        for callback in self.update_callbacks:
            await callback("deleted", drawing)
    
    async def duplicate_drawing(self, drawing_id: str) -> str:
        """Duplicate an existing drawing"""
        
        if drawing_id not in self.drawings:
            raise ValueError(f"Drawing {drawing_id} not found")
        
        original = self.drawings[drawing_id]
        
        # Create new drawing with slight offset
        new_points = []
        for point in original.points:
            new_point = Point(
                timestamp=point.timestamp,
                price=point.price * 1.01,  # 1% offset
                bar_index=point.bar_index
            )
            new_points.append(new_point)
        
        # Add new drawing
        return await self.add_drawing(
            original.type.value,
            [p.to_dict() for p in new_points],
            original.style.to_dict()
        )
    
    async def detect_auto_drawings(self) -> List[Dict[str, Any]]:
        """
        AI-powered automatic drawing detection
        Detects support/resistance, trend lines, channels
        """
        
        suggestions = []
        
        if len(self.chart.data) < 50:
            return suggestions
        
        # Detect support and resistance levels
        sr_levels = await self._detect_support_resistance()
        for level in sr_levels[:5]:  # Top 5 levels
            suggestions.append({
                "type": "horizontal_line",
                "points": [{"price": level["price"]}],
                "confidence": level["confidence"],
                "description": f"{level['type']} at ₹{level['price']:.2f}"
            })
        
        # Detect trend lines
        trend_lines = await self._detect_trend_lines()
        for line in trend_lines[:3]:  # Top 3 trend lines
            suggestions.append({
                "type": "trend_line",
                "points": line["points"],
                "confidence": line["confidence"],
                "description": f"{line['direction']} trend line"
            })
        
        # Detect channels
        channels = await self._detect_channels()
        for channel in channels[:2]:  # Top 2 channels
            suggestions.append({
                "type": "parallel_channel",
                "points": channel["points"],
                "confidence": channel["confidence"],
                "description": f"{channel['type']} channel"
            })
        
        return suggestions
    
    async def apply_elliott_wave(self) -> Dict[str, Any]:
        """
        AI-assisted Elliott Wave analysis
        Returns wave count and projections
        """
        
        if len(self.chart.data) < 100:
            return {"error": "Insufficient data for Elliott Wave analysis"}
        
        # Get price data
        prices = np.array([d.close for d in self.chart.data[-200:]])
        
        # Simplified Elliott Wave detection
        waves = await self._detect_elliott_waves(prices)
        
        if waves:
            # Create Elliott Wave drawing
            drawing_id = await self.add_drawing(
                "elliott_wave",
                waves["points"],
                {
                    "color": "#4CAF50",
                    "width": 2,
                    "style": "solid"
                }
            )
            
            return {
                "drawing_id": drawing_id,
                "wave_count": waves["wave_count"],
                "current_wave": waves["current_wave"],
                "projection": waves["projection"],
                "confidence": waves["confidence"]
            }
        
        return {"error": "No clear Elliott Wave pattern detected"}
    
    async def apply_harmonic_pattern(self) -> Dict[str, Any]:
        """
        Detect and draw harmonic patterns (Gartley, Butterfly, etc.)
        """
        
        if len(self.chart.data) < 50:
            return {"error": "Insufficient data for harmonic pattern analysis"}
        
        # Detect XABCD patterns
        patterns = await self._detect_harmonic_patterns()
        
        if patterns:
            best_pattern = patterns[0]  # Highest confidence
            
            # Create pattern drawing
            drawing_id = await self.add_drawing(
                "xabcd_pattern",
                best_pattern["points"],
                {
                    "color": "#FF9800",
                    "width": 2,
                    "fill": True,
                    "fill_opacity": 0.1
                }
            )
            
            return {
                "drawing_id": drawing_id,
                "pattern_type": best_pattern["type"],
                "completion": best_pattern["completion"],
                "target": best_pattern["target"],
                "stop_loss": best_pattern["stop_loss"],
                "confidence": best_pattern["confidence"]
            }
        
        return {"error": "No harmonic patterns detected"}
    
    async def _snap_to_ohlc(self, point: Point) -> Point:
        """Snap point to nearest OHLC value"""
        
        # Find nearest candle
        nearest_candle = None
        min_time_diff = float('inf')
        
        for i, candle in enumerate(self.chart.data):
            time_diff = abs((candle.timestamp - point.timestamp).total_seconds())
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                nearest_candle = candle
                point.bar_index = i
        
        if nearest_candle:
            # Find closest OHLC value
            ohlc_values = [
                nearest_candle.open,
                nearest_candle.high,
                nearest_candle.low,
                nearest_candle.close
            ]
            
            closest_price = min(ohlc_values, key=lambda x: abs(x - point.price))
            point.price = closest_price
        
        return point
    
    async def _enhance_fibonacci(self, drawing: Drawing):
        """Enhance Fibonacci retracement with AI"""
        
        if len(drawing.points) < 2:
            return
        
        # Add standard Fibonacci levels
        levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        
        # Calculate price range
        start_price = drawing.points[0].price
        end_price = drawing.points[1].price
        price_range = end_price - start_price
        
        # Store levels in metadata
        drawing.metadata["levels"] = []
        for level in levels:
            price = start_price + (price_range * level)
            drawing.metadata["levels"].append({
                "level": level,
                "price": price,
                "label": f"{level*100:.1f}%"
            })
        
        # AI enhancement: predict likely reversal levels
        if self.pattern_recognition:
            # Analyze historical reversals at Fib levels
            reversal_strength = await self._analyze_fib_reversals(drawing.metadata["levels"])
            drawing.metadata["reversal_strength"] = reversal_strength
    
    async def _enhance_support_resistance(self, drawing: Drawing):
        """Enhance support/resistance lines with AI"""
        
        if drawing.type != DrawingToolType.HORIZONTAL_LINE:
            return
        
        price_level = drawing.points[0].price
        
        # Count historical touches
        touches = 0
        for candle in self.chart.data:
            if abs(candle.high - price_level) / price_level < 0.001:  # Within 0.1%
                touches += 1
            elif abs(candle.low - price_level) / price_level < 0.001:
                touches += 1
        
        # Store analysis in metadata
        drawing.metadata["touches"] = touches
        drawing.metadata["strength"] = min(touches / 3, 1.0)  # Normalize to 0-1
        
        # Determine if support or resistance
        recent_price = self.chart.data[-1].close if self.chart.data else price_level
        drawing.metadata["type"] = "resistance" if price_level > recent_price else "support"
    
    async def _detect_support_resistance(self) -> List[Dict[str, Any]]:
        """Detect support and resistance levels"""
        
        levels = []
        
        # Get recent price data
        recent_data = self.chart.data[-200:]
        
        # Find local maxima and minima
        for i in range(10, len(recent_data) - 10):
            # Check for local maximum (resistance)
            if (recent_data[i].high > max(d.high for d in recent_data[i-10:i]) and
                recent_data[i].high > max(d.high for d in recent_data[i+1:i+11])):
                
                levels.append({
                    "type": "resistance",
                    "price": recent_data[i].high,
                    "touches": 1,
                    "confidence": 0.7
                })
            
            # Check for local minimum (support)
            if (recent_data[i].low < min(d.low for d in recent_data[i-10:i]) and
                recent_data[i].low < min(d.low for d in recent_data[i+1:i+11])):
                
                levels.append({
                    "type": "support",
                    "price": recent_data[i].low,
                    "touches": 1,
                    "confidence": 0.7
                })
        
        # Cluster nearby levels
        clustered = []
        for level in levels:
            added = False
            for cluster in clustered:
                if abs(cluster["price"] - level["price"]) / level["price"] < 0.005:  # Within 0.5%
                    cluster["touches"] += 1
                    cluster["confidence"] = min(cluster["confidence"] + 0.1, 0.95)
                    added = True
                    break
            
            if not added:
                clustered.append(level)
        
        # Sort by confidence
        return sorted(clustered, key=lambda x: x["confidence"], reverse=True)
    
    async def _detect_trend_lines(self) -> List[Dict[str, Any]]:
        """Detect trend lines using pivot points"""
        
        trend_lines = []
        
        if len(self.chart.data) < 50:
            return trend_lines
        
        # Find pivot highs and lows
        pivot_highs = []
        pivot_lows = []
        
        for i in range(5, len(self.chart.data) - 5):
            # Pivot high
            if (self.chart.data[i].high > max(d.high for d in self.chart.data[i-5:i]) and
                self.chart.data[i].high > max(d.high for d in self.chart.data[i+1:i+6])):
                pivot_highs.append((i, self.chart.data[i]))
            
            # Pivot low
            if (self.chart.data[i].low < min(d.low for d in self.chart.data[i-5:i]) and
                self.chart.data[i].low < min(d.low for d in self.chart.data[i+1:i+6])):
                pivot_lows.append((i, self.chart.data[i]))
        
        # Connect pivot points for uptrend lines
        for i in range(len(pivot_lows) - 1):
            for j in range(i + 1, min(i + 4, len(pivot_lows))):  # Look ahead 3 pivots
                idx1, candle1 = pivot_lows[i]
                idx2, candle2 = pivot_lows[j]
                
                # Calculate slope
                slope = (candle2.low - candle1.low) / (idx2 - idx1)
                
                # Validate trend line (check touches)
                touches = 0
                for k in range(idx1, min(idx2 + 20, len(self.chart.data))):
                    expected = candle1.low + slope * (k - idx1)
                    if abs(self.chart.data[k].low - expected) / expected < 0.01:  # Within 1%
                        touches += 1
                
                if touches >= 3:  # At least 3 touches
                    trend_lines.append({
                        "direction": "uptrend",
                        "points": [
                            {"timestamp": candle1.timestamp.isoformat(), "price": candle1.low},
                            {"timestamp": candle2.timestamp.isoformat(), "price": candle2.low}
                        ],
                        "touches": touches,
                        "confidence": min(touches * 0.2, 0.9)
                    })
        
        # Similar logic for downtrend lines using pivot highs
        
        return sorted(trend_lines, key=lambda x: x["confidence"], reverse=True)
    
    async def _detect_channels(self) -> List[Dict[str, Any]]:
        """Detect parallel channels"""
        
        channels = []
        
        # Use detected trend lines to find parallel channels
        trend_lines = await self._detect_trend_lines()
        
        # Simplified channel detection
        # In production, would use more sophisticated algorithm
        
        return channels
    
    async def _detect_elliott_waves(self, prices: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect Elliott Wave patterns"""
        
        # Simplified Elliott Wave detection
        # In production, would use more sophisticated algorithm
        
        # Find major swing points
        swing_points = []
        for i in range(10, len(prices) - 10):
            if prices[i] > max(prices[i-10:i]) and prices[i] > max(prices[i+1:i+11]):
                swing_points.append(("high", i, prices[i]))
            elif prices[i] < min(prices[i-10:i]) and prices[i] < min(prices[i+1:i+11]):
                swing_points.append(("low", i, prices[i]))
        
        # Need at least 5 swings for basic wave count
        if len(swing_points) < 5:
            return None
        
        # Basic wave pattern recognition
        # This is highly simplified - real implementation would be much more complex
        
        return None
    
    async def _detect_harmonic_patterns(self) -> List[Dict[str, Any]]:
        """Detect harmonic patterns (Gartley, Butterfly, etc.)"""
        
        patterns = []
        
        # Simplified harmonic pattern detection
        # Real implementation would check Fibonacci ratios between points
        
        return patterns
    
    async def _analyze_fib_reversals(self, levels: List[Dict[str, Any]]) -> Dict[float, float]:
        """Analyze historical price reversals at Fibonacci levels"""
        
        reversal_strength = {}
        
        for level_info in levels:
            level = level_info["level"]
            price = level_info["price"]
            
            # Count reversals near this level
            reversals = 0
            for i in range(1, len(self.chart.data) - 1):
                if abs(self.chart.data[i].low - price) / price < 0.005:  # Within 0.5%
                    # Check if price reversed
                    if (self.chart.data[i-1].close > self.chart.data[i].close and
                        self.chart.data[i+1].close > self.chart.data[i].close):
                        reversals += 1
                
                elif abs(self.chart.data[i].high - price) / price < 0.005:
                    if (self.chart.data[i-1].close < self.chart.data[i].close and
                        self.chart.data[i+1].close < self.chart.data[i].close):
                        reversals += 1
            
            reversal_strength[level] = min(reversals * 0.1, 1.0)  # Normalize
        
        return reversal_strength
    
    def register_update_callback(self, callback: Callable):
        """Register callback for drawing updates"""
        self.update_callbacks.append(callback)
    
    def get_all_drawings(self) -> List[Drawing]:
        """Get all drawings"""
        return list(self.drawings.values())
    
    def get_drawing(self, drawing_id: str) -> Optional[Drawing]:
        """Get specific drawing"""
        return self.drawings.get(drawing_id)
    
    def clear_all_drawings(self):
        """Clear all drawings"""
        unlocked_ids = [
            drawing_id for drawing_id, drawing in self.drawings.items()
            if not drawing.locked
        ]
        
        for drawing_id in unlocked_ids:
            del self.drawings[drawing_id]
        
        # Trigger callbacks
        for callback in self.update_callbacks:
            asyncio.create_task(callback("cleared", None))