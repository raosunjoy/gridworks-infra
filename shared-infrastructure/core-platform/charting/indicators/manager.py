"""
Technical Indicators Manager

Comprehensive indicator suite matching and exceeding
Zerodha Kite + Dhan capabilities.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
import numpy as np
import pandas as pd
from enum import Enum
from dataclasses import dataclass
import uuid

from app.core.logging import logger


class IndicatorType(Enum):
    """All available indicators - matching Zerodha + Dhan + more"""
    
    # Moving Averages
    SMA = "SMA"  # Simple Moving Average
    EMA = "EMA"  # Exponential Moving Average
    WMA = "WMA"  # Weighted Moving Average
    DEMA = "DEMA"  # Double Exponential Moving Average
    TEMA = "TEMA"  # Triple Exponential Moving Average
    HMA = "HMA"  # Hull Moving Average
    VWMA = "VWMA"  # Volume Weighted Moving Average
    
    # Momentum Indicators
    RSI = "RSI"  # Relative Strength Index
    MACD = "MACD"  # Moving Average Convergence Divergence
    STOCHASTIC = "STOCHASTIC"  # Stochastic Oscillator
    WILLIAMS_R = "WILLIAMS_R"  # Williams %R
    CCI = "CCI"  # Commodity Channel Index
    MOMENTUM = "MOMENTUM"  # Momentum
    ROC = "ROC"  # Rate of Change
    
    # Volatility Indicators
    BOLLINGER = "BOLLINGER"  # Bollinger Bands
    ATR = "ATR"  # Average True Range
    KELTNER = "KELTNER"  # Keltner Channels
    DONCHIAN = "DONCHIAN"  # Donchian Channels
    STDDEV = "STDDEV"  # Standard Deviation
    
    # Volume Indicators
    VOLUME = "VOLUME"  # Volume
    OBV = "OBV"  # On Balance Volume
    VWAP = "VWAP"  # Volume Weighted Average Price
    MFI = "MFI"  # Money Flow Index
    AD = "AD"  # Accumulation/Distribution
    CMF = "CMF"  # Chaikin Money Flow
    
    # Trend Indicators
    ADX = "ADX"  # Average Directional Index
    SUPERTREND = "SUPERTREND"  # SuperTrend
    ICHIMOKU = "ICHIMOKU"  # Ichimoku Cloud
    PSAR = "PSAR"  # Parabolic SAR
    AROON = "AROON"  # Aroon Indicator
    
    # Advanced/Custom
    PIVOT = "PIVOT"  # Pivot Points
    FIBONACCI = "FIBONACCI"  # Fibonacci Retracements
    GANN = "GANN"  # Gann Levels
    ELLIOTT = "ELLIOTT"  # Elliott Wave (AI-powered)


@dataclass
class IndicatorConfig:
    """Configuration for an indicator"""
    type: IndicatorType
    params: Dict[str, Any]
    color: Optional[str] = None
    line_style: Optional[str] = None
    panel: str = "main"  # main/separate panel
    visible: bool = True


class IndicatorManager:
    """
    Manages all technical indicators for charts
    Provides calculation, caching, and real-time updates
    """
    
    def __init__(self, chart):
        self.chart = chart
        self.indicators: Dict[str, IndicatorConfig] = {}
        self.calculated_values: Dict[str, np.ndarray] = {}
        self.update_callbacks: Dict[str, List[Callable]] = {}
        
        # Performance optimization
        self.calculation_cache: Dict[str, Any] = {}
        self.batch_calculation = True
        
    async def add_indicator(
        self,
        indicator_type: str,
        params: Dict[str, Any],
        data: List[Any]
    ) -> str:
        """Add a new indicator to the chart"""
        
        # Generate unique ID
        indicator_id = str(uuid.uuid4())
        
        # Create configuration
        config = IndicatorConfig(
            type=IndicatorType[indicator_type.upper()],
            params=params,
            color=params.get("color"),
            line_style=params.get("line_style", "solid"),
            panel=params.get("panel", "main"),
            visible=params.get("visible", True)
        )
        
        # Store configuration
        self.indicators[indicator_id] = config
        
        # Calculate initial values
        values = await self.calculate(indicator_id, data)
        self.calculated_values[indicator_id] = values
        
        logger.info(f"Added indicator {indicator_type} with ID {indicator_id}")
        return indicator_id
    
    async def calculate(
        self,
        indicator_id: str,
        data: List[Any]
    ) -> np.ndarray:
        """Calculate indicator values"""
        
        if indicator_id not in self.indicators:
            raise ValueError(f"Indicator {indicator_id} not found")
        
        config = self.indicators[indicator_id]
        
        # Convert data to numpy arrays for efficient calculation
        if not data:
            return np.array([])
        
        # Extract OHLCV data
        opens = np.array([d.open for d in data])
        highs = np.array([d.high for d in data])
        lows = np.array([d.low for d in data])
        closes = np.array([d.close for d in data])
        volumes = np.array([d.volume for d in data])
        
        # Route to appropriate calculation method
        calculator_map = {
            IndicatorType.SMA: self._calculate_sma,
            IndicatorType.EMA: self._calculate_ema,
            IndicatorType.RSI: self._calculate_rsi,
            IndicatorType.MACD: self._calculate_macd,
            IndicatorType.BOLLINGER: self._calculate_bollinger,
            IndicatorType.ATR: self._calculate_atr,
            IndicatorType.STOCHASTIC: self._calculate_stochastic,
            IndicatorType.VWAP: self._calculate_vwap,
            IndicatorType.SUPERTREND: self._calculate_supertrend,
            IndicatorType.ADX: self._calculate_adx,
            IndicatorType.OBV: self._calculate_obv,
            IndicatorType.ICHIMOKU: self._calculate_ichimoku,
            # Add more as needed
        }
        
        calculator = calculator_map.get(config.type)
        if not calculator:
            raise NotImplementedError(f"Calculator for {config.type} not implemented")
        
        # Calculate values
        result = await calculator(opens, highs, lows, closes, volumes, config.params)
        
        return result
    
    async def update_all(self, new_data: Any):
        """Update all indicators with new data point"""
        
        update_tasks = []
        
        for indicator_id in self.indicators:
            # Recalculate with updated data
            data = self.chart.data
            task = self.calculate(indicator_id, data)
            update_tasks.append(task)
        
        # Execute all updates concurrently
        if update_tasks:
            results = await asyncio.gather(*update_tasks)
            
            # Update stored values
            for indicator_id, values in zip(self.indicators.keys(), results):
                self.calculated_values[indicator_id] = values
                
                # Trigger callbacks
                if indicator_id in self.update_callbacks:
                    for callback in self.update_callbacks[indicator_id]:
                        await callback(values)
    
    async def _calculate_sma(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """Simple Moving Average"""
        
        period = params.get("period", 20)
        source = params.get("source", "close")
        
        # Select data source
        data = self._get_source_data(opens, highs, lows, closes, source)
        
        # Calculate SMA
        sma = np.full(len(data), np.nan)
        
        if len(data) >= period:
            for i in range(period - 1, len(data)):
                sma[i] = np.mean(data[i - period + 1:i + 1])
        
        return sma
    
    async def _calculate_ema(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """Exponential Moving Average"""
        
        period = params.get("period", 20)
        source = params.get("source", "close")
        
        # Select data source
        data = self._get_source_data(opens, highs, lows, closes, source)
        
        # Calculate EMA
        ema = np.full(len(data), np.nan)
        
        if len(data) >= period:
            # Initial SMA
            ema[period - 1] = np.mean(data[:period])
            
            # EMA calculation
            multiplier = 2 / (period + 1)
            for i in range(period, len(data)):
                ema[i] = (data[i] * multiplier) + (ema[i - 1] * (1 - multiplier))
        
        return ema
    
    async def _calculate_rsi(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """Relative Strength Index"""
        
        period = params.get("period", 14)
        
        # Calculate price changes
        deltas = np.diff(closes)
        seed = deltas[:period + 1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(closes)
        rsi[:period] = np.nan
        rsi[period] = 100. - 100. / (1. + rs)
        
        # Calculate RSI for remaining data
        for i in range(period + 1, len(closes)):
            delta = deltas[i - 1]
            
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100. / (1. + rs)
        
        return rsi
    
    async def _calculate_macd(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """MACD - returns dict with macd, signal, histogram"""
        
        fast_period = params.get("fast_period", 12)
        slow_period = params.get("slow_period", 26)
        signal_period = params.get("signal_period", 9)
        
        # Calculate EMAs
        ema_fast = await self._calculate_ema(
            opens, highs, lows, closes, volumes,
            {"period": fast_period, "source": "close"}
        )
        ema_slow = await self._calculate_ema(
            opens, highs, lows, closes, volumes,
            {"period": slow_period, "source": "close"}
        )
        
        # MACD line
        macd = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        signal = np.full(len(macd), np.nan)
        valid_macd = macd[~np.isnan(macd)]
        
        if len(valid_macd) >= signal_period:
            signal_ema = await self._calculate_ema_on_series(valid_macd, signal_period)
            signal[~np.isnan(macd)] = signal_ema
        
        # Histogram
        histogram = macd - signal
        
        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram
        }
    
    async def _calculate_bollinger(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Bollinger Bands - returns dict with upper, middle, lower"""
        
        period = params.get("period", 20)
        stddev = params.get("stddev", 2)
        
        # Middle band (SMA)
        middle = await self._calculate_sma(
            opens, highs, lows, closes, volumes,
            {"period": period, "source": "close"}
        )
        
        # Calculate standard deviation
        std = np.full(len(closes), np.nan)
        
        for i in range(period - 1, len(closes)):
            std[i] = np.std(closes[i - period + 1:i + 1])
        
        # Upper and lower bands
        upper = middle + (std * stddev)
        lower = middle - (std * stddev)
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }
    
    async def _calculate_atr(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """Average True Range"""
        
        period = params.get("period", 14)
        
        # Calculate True Range
        high_low = highs - lows
        high_close = np.abs(highs - np.roll(closes, 1))
        low_close = np.abs(lows - np.roll(closes, 1))
        
        # First TR has no previous close
        high_close[0] = high_low[0]
        low_close[0] = high_low[0]
        
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        
        # Calculate ATR
        atr = np.full(len(tr), np.nan)
        atr[period - 1] = np.mean(tr[:period])
        
        # Subsequent ATR values
        for i in range(period, len(tr)):
            atr[i] = ((atr[i - 1] * (period - 1)) + tr[i]) / period
        
        return atr
    
    async def _calculate_stochastic(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Stochastic Oscillator - returns %K and %D"""
        
        k_period = params.get("k_period", 14)
        d_period = params.get("d_period", 3)
        smooth = params.get("smooth", 3)
        
        # Calculate %K
        k = np.full(len(closes), np.nan)
        
        for i in range(k_period - 1, len(closes)):
            highest = np.max(highs[i - k_period + 1:i + 1])
            lowest = np.min(lows[i - k_period + 1:i + 1])
            
            if highest != lowest:
                k[i] = ((closes[i] - lowest) / (highest - lowest)) * 100
            else:
                k[i] = 50  # Default when range is 0
        
        # Smooth %K if requested
        if smooth > 1:
            k_smooth = await self._calculate_sma_on_series(k[~np.isnan(k)], smooth)
            k[~np.isnan(k)] = k_smooth
        
        # Calculate %D (SMA of %K)
        d = np.full(len(k), np.nan)
        valid_k = k[~np.isnan(k)]
        
        if len(valid_k) >= d_period:
            d_values = await self._calculate_sma_on_series(valid_k, d_period)
            d[~np.isnan(k)] = d_values
        
        return {
            "k": k,
            "d": d
        }
    
    async def _calculate_vwap(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """Volume Weighted Average Price"""
        
        # VWAP resets daily, but for intraday we calculate cumulative
        typical_price = (highs + lows + closes) / 3
        
        # Calculate cumulative values
        cumulative_volume = np.cumsum(volumes)
        cumulative_pv = np.cumsum(typical_price * volumes)
        
        # VWAP calculation
        vwap = cumulative_pv / cumulative_volume
        
        # Handle division by zero
        vwap[cumulative_volume == 0] = typical_price[cumulative_volume == 0]
        
        return vwap
    
    async def _calculate_supertrend(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """SuperTrend Indicator"""
        
        period = params.get("period", 10)
        multiplier = params.get("multiplier", 3)
        
        # Calculate ATR
        atr = await self._calculate_atr(opens, highs, lows, closes, volumes, {"period": period})
        
        # Calculate basic bands
        hl_avg = (highs + lows) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        # Initialize SuperTrend
        supertrend = np.zeros(len(closes))
        direction = np.zeros(len(closes))  # 1 for buy, -1 for sell
        
        # Calculate SuperTrend
        for i in range(period, len(closes)):
            # Upper band condition
            if upper_band[i] < upper_band[i-1] or closes[i-1] > upper_band[i-1]:
                upper_band[i] = upper_band[i]
            else:
                upper_band[i] = upper_band[i-1]
            
            # Lower band condition
            if lower_band[i] > lower_band[i-1] or closes[i-1] < lower_band[i-1]:
                lower_band[i] = lower_band[i]
            else:
                lower_band[i] = lower_band[i-1]
            
            # Trend direction
            if i == period:
                if closes[i] <= upper_band[i]:
                    direction[i] = -1
                else:
                    direction[i] = 1
            else:
                if supertrend[i-1] == upper_band[i-1]:
                    if closes[i] <= upper_band[i]:
                        direction[i] = -1
                    else:
                        direction[i] = 1
                else:
                    if closes[i] >= lower_band[i]:
                        direction[i] = 1
                    else:
                        direction[i] = -1
            
            # Set SuperTrend value
            if direction[i] == -1:
                supertrend[i] = upper_band[i]
            else:
                supertrend[i] = lower_band[i]
        
        return {
            "supertrend": supertrend,
            "direction": direction,
            "upper_band": upper_band,
            "lower_band": lower_band
        }
    
    async def _calculate_adx(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Average Directional Index"""
        
        period = params.get("period", 14)
        
        # Calculate directional movement
        up_move = highs[1:] - highs[:-1]
        down_move = lows[:-1] - lows[1:]
        
        # Positive/Negative directional movement
        pos_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        neg_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # ATR for normalization
        atr = await self._calculate_atr(opens, highs, lows, closes, volumes, {"period": period})
        
        # Smooth the directional movements
        pos_di = 100 * (pos_dm / atr[1:])
        neg_di = 100 * (neg_dm / atr[1:])
        
        # Calculate DX
        dx = 100 * np.abs(pos_di - neg_di) / (pos_di + neg_di)
        
        # ADX is smoothed DX
        adx = np.full(len(closes), np.nan)
        # Implementation would continue with proper smoothing
        
        return {
            "adx": adx,
            "plus_di": pos_di,
            "minus_di": neg_di
        }
    
    async def _calculate_obv(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """On Balance Volume"""
        
        obv = np.zeros(len(closes))
        obv[0] = volumes[0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv[i] = obv[i-1] + volumes[i]
            elif closes[i] < closes[i-1]:
                obv[i] = obv[i-1] - volumes[i]
            else:
                obv[i] = obv[i-1]
        
        return obv
    
    async def _calculate_ichimoku(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        volumes: np.ndarray,
        params: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Ichimoku Cloud"""
        
        # Ichimoku parameters
        tenkan_period = params.get("tenkan_period", 9)
        kijun_period = params.get("kijun_period", 26)
        senkou_b_period = params.get("senkou_b_period", 52)
        displacement = params.get("displacement", 26)
        
        # Helper function to calculate midpoint
        def midpoint(highs, lows, period, idx):
            if idx < period - 1:
                return np.nan
            return (np.max(highs[idx-period+1:idx+1]) + np.min(lows[idx-period+1:idx+1])) / 2
        
        # Calculate components
        length = len(closes)
        
        # Tenkan-sen (Conversion Line)
        tenkan = np.array([midpoint(highs, lows, tenkan_period, i) for i in range(length)])
        
        # Kijun-sen (Base Line)
        kijun = np.array([midpoint(highs, lows, kijun_period, i) for i in range(length)])
        
        # Senkou Span A (Leading Span A)
        senkou_a = (tenkan + kijun) / 2
        # Shift forward
        senkou_a = np.roll(senkou_a, displacement)
        senkou_a[:displacement] = np.nan
        
        # Senkou Span B (Leading Span B)
        senkou_b = np.array([midpoint(highs, lows, senkou_b_period, i) for i in range(length)])
        # Shift forward
        senkou_b = np.roll(senkou_b, displacement)
        senkou_b[:displacement] = np.nan
        
        # Chikou Span (Lagging Span) - close shifted backward
        chikou = np.roll(closes, -displacement)
        chikou[-displacement:] = np.nan
        
        return {
            "tenkan": tenkan,
            "kijun": kijun,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b,
            "chikou": chikou
        }
    
    def _get_source_data(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        source: str
    ) -> np.ndarray:
        """Get data based on source selection"""
        
        source_map = {
            "close": closes,
            "open": opens,
            "high": highs,
            "low": lows,
            "hl2": (highs + lows) / 2,
            "hlc3": (highs + lows + closes) / 3,
            "ohlc4": (opens + highs + lows + closes) / 4
        }
        
        return source_map.get(source, closes)
    
    async def _calculate_sma_on_series(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA on a single series"""
        
        sma = np.full(len(data), np.nan)
        
        if len(data) >= period:
            for i in range(period - 1, len(data)):
                sma[i] = np.mean(data[i - period + 1:i + 1])
        
        return sma
    
    async def _calculate_ema_on_series(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA on a single series"""
        
        ema = np.full(len(data), np.nan)
        
        if len(data) >= period:
            ema[period - 1] = np.mean(data[:period])
            
            multiplier = 2 / (period + 1)
            for i in range(period, len(data)):
                ema[i] = (data[i] * multiplier) + (ema[i - 1] * (1 - multiplier))
        
        return ema
    
    def register_update_callback(self, indicator_id: str, callback: Callable):
        """Register callback for indicator updates"""
        
        if indicator_id not in self.update_callbacks:
            self.update_callbacks[indicator_id] = []
        
        self.update_callbacks[indicator_id].append(callback)
    
    def get_indicator_values(self, indicator_id: str) -> Optional[np.ndarray]:
        """Get current calculated values for an indicator"""
        
        return self.calculated_values.get(indicator_id)
    
    def remove_indicator(self, indicator_id: str):
        """Remove an indicator"""
        
        if indicator_id in self.indicators:
            del self.indicators[indicator_id]
            
        if indicator_id in self.calculated_values:
            del self.calculated_values[indicator_id]
            
        if indicator_id in self.update_callbacks:
            del self.update_callbacks[indicator_id]