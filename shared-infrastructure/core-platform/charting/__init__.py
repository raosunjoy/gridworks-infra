"""
GridWorks Advanced Charting Platform

Professional-grade charting solution with AI-powered features,
matching and exceeding Zerodha Kite and Dhan capabilities.

Features:
- Multiple chart types (Candlestick, Heikin Ashi, Renko, etc.)
- 50+ technical indicators
- Advanced drawing tools
- AI pattern recognition
- Voice command integration
- Real-time data streaming
- One-click trading from charts
"""

from .core.chart_engine import ChartEngine
from .core.chart_manager import ChartManager
from .types.candlestick import CandlestickChart
from .indicators.manager import IndicatorManager
from .drawing_tools.manager import DrawingToolManager

__version__ = "1.0.0"
__all__ = [
    "ChartEngine",
    "ChartManager", 
    "CandlestickChart",
    "IndicatorManager",
    "DrawingToolManager"
]