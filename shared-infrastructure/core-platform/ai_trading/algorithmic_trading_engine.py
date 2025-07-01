#!/usr/bin/env python3
"""
GridWorks Advanced AI Trading Strategies Engine
==============================================
Machine learning-powered algorithmic trading with Indian market optimization
"""

import asyncio
import json
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging
from pathlib import Path
import time
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """AI trading strategy types"""
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    PAIRS_TRADING = "pairs_trading"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    ML_REGRESSION = "ml_regression"
    ML_CLASSIFICATION = "ml_classification"
    ENSEMBLE = "ensemble"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    SENTIMENT_BASED = "sentiment_based"
    PATTERN_BASED = "pattern_based"


class OrderType(Enum):
    """Advanced order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    BRACKET = "bracket"
    COVER = "cover"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"


class TimeFrame(Enum):
    """Trading timeframes"""
    TICK = "tick"
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"


class MarketRegime(Enum):
    """Market regime classification"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    CRISIS = "crisis"


@dataclass
class TradingSignal:
    """AI-generated trading signal"""
    signal_id: str
    strategy_id: str
    symbol: str
    signal_type: str  # "buy", "sell", "hold"
    confidence: float
    strength: float  # Signal strength 0-1
    entry_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    position_size: float
    timeframe: TimeFrame
    generated_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk-reward ratio"""
        if not self.target_price or not self.stop_loss:
            return 1.0
        
        if self.signal_type == "buy":
            risk = abs(self.entry_price - self.stop_loss)
            reward = abs(self.target_price - self.entry_price)
        else:
            risk = abs(self.stop_loss - self.entry_price)
            reward = abs(self.entry_price - self.target_price)
        
        return reward / risk if risk > 0 else 1.0


@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""
    strategy_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    calmar_ratio: float
    sortino_ratio: float
    var_95: float  # Value at Risk
    expected_shortfall: float
    beta: float
    alpha: float
    information_ratio: float
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None


class FeatureEngineer:
    """Advanced feature engineering for ML strategies"""
    
    def __init__(self):
        """Initialize feature engineer"""
        self.feature_cache = {}
    
    async def generate_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate comprehensive technical analysis features"""
        df = data.copy()
        
        # Price-based features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['price_change'] = df['close'] - df['open']
        df['price_range'] = df['high'] - df['low']
        df['body_size'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - np.maximum(df['open'], df['close'])
        df['lower_shadow'] = np.minimum(df['open'], df['close']) - df['low']
        
        # Moving averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
            df[f'price_to_sma_{period}'] = df['close'] / df[f'sma_{period}']
        
        # Volatility features
        df['volatility_10'] = df['returns'].rolling(window=10).std()
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        df['parkinson_vol'] = np.sqrt(np.log(df['high'] / df['low']) ** 2 / (4 * np.log(2)))
        
        # Momentum indicators
        df['rsi_14'] = self._calculate_rsi(df['close'], 14)
        df['rsi_21'] = self._calculate_rsi(df['close'], 21)
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_20'] = df['close'] / df['close'].shift(20) - 1
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        df['bb_upper'] = sma_20 + (2 * std_20)
        df['bb_lower'] = sma_20 - (2 * std_20)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume features
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']
        df['price_volume'] = df['close'] * df['volume']
        df['vwap'] = (df['price_volume'].rolling(window=20).sum() / 
                     df['volume'].rolling(window=20).sum())
        
        # Advanced features
        df['atr_14'] = self._calculate_atr(df, 14)
        df['stochastic_k'] = self._calculate_stochastic(df, 14)
        df['williams_r'] = self._calculate_williams_r(df, 14)
        
        # Market microstructure (if bid/ask available)
        if 'bid' in df.columns and 'ask' in df.columns:
            df['spread'] = df['ask'] - df['bid']
            df['mid_price'] = (df['bid'] + df['ask']) / 2
            df['price_to_mid'] = df['close'] / df['mid_price']
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(window=period).mean()
    
    def _calculate_stochastic(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Stochastic %K"""
        lowest_low = df['low'].rolling(window=period).min()
        highest_high = df['high'].rolling(window=period).max()
        return 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Williams %R"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        return -100 * (highest_high - df['close']) / (highest_high - lowest_low)
    
    async def generate_sentiment_features(self, symbol: str, data: pd.DataFrame) -> pd.DataFrame:
        """Generate sentiment-based features"""
        df = data.copy()
        
        # Mock sentiment features (replace with actual sentiment analysis)
        np.random.seed(42)  # For reproducible mock data
        df['news_sentiment'] = np.random.normal(0, 0.3, len(df))
        df['social_sentiment'] = np.random.normal(0, 0.25, len(df))
        df['analyst_sentiment'] = np.random.normal(0.1, 0.2, len(df))
        
        # Sentiment momentum
        df['sentiment_ma_5'] = df['news_sentiment'].rolling(window=5).mean()
        df['sentiment_change'] = df['news_sentiment'] - df['sentiment_ma_5']
        
        return df


class MLStrategyOptimizer:
    """Machine learning strategy optimization"""
    
    def __init__(self):
        """Initialize ML optimizer"""
        self.models = {}
        self.feature_importance = {}
        self.hyperparameters = {}
    
    async def optimize_strategy_parameters(
        self, 
        strategy_type: StrategyType,
        historical_data: pd.DataFrame,
        lookback_period: int = 252
    ) -> Dict[str, Any]:
        """Optimize strategy parameters using ML"""
        
        # Mock ML optimization (replace with actual sklearn/tensorflow)
        optimized_params = {
            StrategyType.MEAN_REVERSION: {
                'lookback_window': 20,
                'entry_threshold': 2.0,
                'exit_threshold': 0.5,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.015,
                'position_size_pct': 0.05
            },
            StrategyType.MOMENTUM: {
                'momentum_period': 10,
                'confirmation_period': 3,
                'strength_threshold': 0.02,
                'stop_loss_pct': 0.015,
                'take_profit_pct': 0.03,
                'position_size_pct': 0.08
            },
            StrategyType.ML_REGRESSION: {
                'n_estimators': 100,
                'max_depth': 8,
                'learning_rate': 0.1,
                'feature_selection_k': 20,
                'prediction_horizon': 5,
                'confidence_threshold': 0.7
            },
            StrategyType.ENSEMBLE: {
                'strategy_weights': [0.3, 0.3, 0.2, 0.2],
                'rebalance_frequency': 5,
                'confidence_threshold': 0.65,
                'correlation_threshold': 0.7
            }
        }.get(strategy_type, {})
        
        # Add market regime specific adjustments
        market_regime = await self._detect_market_regime(historical_data)
        regime_adjustments = self._get_regime_adjustments(market_regime)
        
        optimized_params.update(regime_adjustments)
        
        logger.info(f"Optimized parameters for {strategy_type.value}: {optimized_params}")
        return optimized_params
    
    async def _detect_market_regime(self, data: pd.DataFrame) -> MarketRegime:
        """Detect current market regime"""
        if len(data) < 50:
            return MarketRegime.SIDEWAYS
        
        # Calculate regime indicators
        recent_data = data.tail(50)
        returns = recent_data['close'].pct_change().dropna()
        
        # Trend detection
        price_trend = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
        
        # Volatility detection
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        
        if abs(price_trend) > 0.1:
            return MarketRegime.TRENDING_UP if price_trend > 0 else MarketRegime.TRENDING_DOWN
        elif volatility > 0.4:
            return MarketRegime.HIGH_VOLATILITY
        elif volatility < 0.15:
            return MarketRegime.LOW_VOLATILITY
        else:
            return MarketRegime.SIDEWAYS
    
    def _get_regime_adjustments(self, regime: MarketRegime) -> Dict[str, Any]:
        """Get parameter adjustments based on market regime"""
        adjustments = {
            MarketRegime.TRENDING_UP: {
                'momentum_boost': 1.2,
                'stop_loss_adjustment': 0.8,
                'position_size_multiplier': 1.1
            },
            MarketRegime.TRENDING_DOWN: {
                'momentum_boost': 0.8,
                'stop_loss_adjustment': 1.2,
                'position_size_multiplier': 0.9
            },
            MarketRegime.HIGH_VOLATILITY: {
                'stop_loss_adjustment': 1.5,
                'position_size_multiplier': 0.7,
                'confidence_threshold_increase': 0.1
            },
            MarketRegime.LOW_VOLATILITY: {
                'stop_loss_adjustment': 0.8,
                'position_size_multiplier': 1.2,
                'confidence_threshold_decrease': 0.05
            },
            MarketRegime.SIDEWAYS: {
                'mean_reversion_boost': 1.3,
                'momentum_reduction': 0.7
            }
        }.get(regime, {})
        
        return adjustments


class TradingStrategy:
    """Base class for AI trading strategies"""
    
    def __init__(self, strategy_id: str, strategy_type: StrategyType, parameters: Dict[str, Any]):
        """Initialize strategy"""
        self.strategy_id = strategy_id
        self.strategy_type = strategy_type
        self.parameters = parameters
        self.performance = StrategyPerformance(
            strategy_id=strategy_id,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            total_return=0.0,
            annualized_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            avg_win=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            calmar_ratio=0.0,
            sortino_ratio=0.0,
            var_95=0.0,
            expected_shortfall=0.0,
            beta=1.0,
            alpha=0.0,
            information_ratio=0.0
        )
        self.position = 0.0
        self.equity_curve = []
        self.trades = []
    
    async def generate_signal(self, data: pd.DataFrame, current_price: float) -> Optional[TradingSignal]:
        """Generate trading signal - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate_signal")
    
    async def update_performance(self, trade_result: Dict[str, Any]):
        """Update strategy performance metrics"""
        self.performance.total_trades += 1
        
        if trade_result['pnl'] > 0:
            self.performance.winning_trades += 1
            self.performance.avg_win = (
                (self.performance.avg_win * (self.performance.winning_trades - 1) + trade_result['pnl']) /
                self.performance.winning_trades
            )
        else:
            self.performance.losing_trades += 1
            self.performance.avg_loss = (
                (self.performance.avg_loss * (self.performance.losing_trades - 1) + abs(trade_result['pnl'])) /
                self.performance.losing_trades
            )
        
        self.performance.total_return += trade_result['pnl']
        self.performance.win_rate = self.performance.winning_trades / self.performance.total_trades
        
        if self.performance.losing_trades > 0:
            self.performance.profit_factor = (
                self.performance.avg_win * self.performance.winning_trades /
                (self.performance.avg_loss * self.performance.losing_trades)
            )
        
        # Update equity curve
        self.equity_curve.append({
            'timestamp': trade_result['timestamp'],
            'equity': sum(t.get('pnl', 0) for t in self.trades) + trade_result['pnl']
        })
        
        self.trades.append(trade_result)


class MeanReversionStrategy(TradingStrategy):
    """Mean reversion strategy implementation"""
    
    async def generate_signal(self, data: pd.DataFrame, current_price: float) -> Optional[TradingSignal]:
        """Generate mean reversion signal"""
        if len(data) < self.parameters.get('lookback_window', 20):
            return None
        
        lookback = self.parameters.get('lookback_window', 20)
        entry_threshold = self.parameters.get('entry_threshold', 2.0)
        
        # Calculate z-score
        recent_prices = data['close'].tail(lookback)
        mean_price = recent_prices.mean()
        std_price = recent_prices.std()
        
        if std_price == 0:
            return None
        
        z_score = (current_price - mean_price) / std_price
        
        # Generate signal
        if z_score > entry_threshold:  # Overbought
            signal_type = "sell"
            confidence = min(abs(z_score) / 3.0, 1.0)
            target_price = mean_price
            stop_loss = current_price * (1 + self.parameters.get('stop_loss_pct', 0.02))
        elif z_score < -entry_threshold:  # Oversold
            signal_type = "buy"
            confidence = min(abs(z_score) / 3.0, 1.0)
            target_price = mean_price
            stop_loss = current_price * (1 - self.parameters.get('stop_loss_pct', 0.02))
        else:
            return None
        
        if confidence < 0.5:
            return None
        
        return TradingSignal(
            signal_id=str(uuid.uuid4()),
            strategy_id=self.strategy_id,
            symbol=data['symbol'].iloc[-1] if 'symbol' in data.columns else 'UNKNOWN',
            signal_type=signal_type,
            confidence=confidence,
            strength=abs(z_score) / 3.0,
            entry_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=self.parameters.get('position_size_pct', 0.05),
            timeframe=TimeFrame.DAY_1,
            generated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            metadata={'z_score': z_score, 'mean_price': mean_price, 'std_price': std_price}
        )


class MomentumStrategy(TradingStrategy):
    """Momentum strategy implementation"""
    
    async def generate_signal(self, data: pd.DataFrame, current_price: float) -> Optional[TradingSignal]:
        """Generate momentum signal"""
        momentum_period = self.parameters.get('momentum_period', 10)
        strength_threshold = self.parameters.get('strength_threshold', 0.02)
        
        if len(data) < momentum_period + 5:
            return None
        
        # Calculate momentum
        past_price = data['close'].iloc[-(momentum_period + 1)]
        momentum = (current_price - past_price) / past_price
        
        # Calculate momentum strength using recent volatility
        recent_returns = data['close'].pct_change().tail(momentum_period)
        volatility = recent_returns.std()
        
        if volatility == 0:
            return None
        
        momentum_strength = abs(momentum) / volatility
        
        if momentum_strength < strength_threshold:
            return None
        
        # Generate signal
        if momentum > 0:  # Upward momentum
            signal_type = "buy"
            target_price = current_price * (1 + self.parameters.get('take_profit_pct', 0.03))
            stop_loss = current_price * (1 - self.parameters.get('stop_loss_pct', 0.015))
        else:  # Downward momentum
            signal_type = "sell"
            target_price = current_price * (1 - self.parameters.get('take_profit_pct', 0.03))
            stop_loss = current_price * (1 + self.parameters.get('stop_loss_pct', 0.015))
        
        confidence = min(momentum_strength / 0.1, 1.0)  # Normalize to 0-1
        
        return TradingSignal(
            signal_id=str(uuid.uuid4()),
            strategy_id=self.strategy_id,
            symbol=data['symbol'].iloc[-1] if 'symbol' in data.columns else 'UNKNOWN',
            signal_type=signal_type,
            confidence=confidence,
            strength=momentum_strength,
            entry_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=self.parameters.get('position_size_pct', 0.08),
            timeframe=TimeFrame.DAY_1,
            generated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=12),
            metadata={'momentum': momentum, 'momentum_strength': momentum_strength}
        )


class MLRegressionStrategy(TradingStrategy):
    """Machine learning regression-based strategy"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.trained = False
    
    async def generate_signal(self, data: pd.DataFrame, current_price: float) -> Optional[TradingSignal]:
        """Generate ML-based signal"""
        if not self.trained or len(data) < 100:
            return None
        
        # Generate features
        features_df = await self.feature_engineer.generate_technical_features(data)
        features_df = await self.feature_engineer.generate_sentiment_features(
            data['symbol'].iloc[-1] if 'symbol' in data.columns else 'UNKNOWN',
            features_df
        )
        
        # Mock ML prediction (replace with actual model)
        prediction_horizon = self.parameters.get('prediction_horizon', 5)
        
        # Simple mock prediction based on technical indicators
        latest_features = features_df.iloc[-1]
        
        # Mock prediction logic
        rsi = latest_features.get('rsi_14', 50)
        momentum = latest_features.get('momentum_10', 0)
        bb_position = latest_features.get('bb_position', 0.5)
        
        # Combine indicators for prediction
        prediction_score = (
            (50 - rsi) / 50 * 0.3 +  # RSI mean reversion
            momentum * 0.4 +  # Momentum
            (0.5 - bb_position) * 0.3  # Bollinger band position
        )
        
        predicted_return = prediction_score * 0.02  # Scale to realistic returns
        confidence = abs(prediction_score) if abs(prediction_score) < 1 else 1.0
        
        confidence_threshold = self.parameters.get('confidence_threshold', 0.7)
        if confidence < confidence_threshold:
            return None
        
        # Generate signal
        if predicted_return > 0.005:  # 0.5% threshold
            signal_type = "buy"
            target_price = current_price * (1 + abs(predicted_return))
            stop_loss = current_price * (1 - self.parameters.get('stop_loss_pct', 0.02))
        elif predicted_return < -0.005:
            signal_type = "sell"
            target_price = current_price * (1 - abs(predicted_return))
            stop_loss = current_price * (1 + self.parameters.get('stop_loss_pct', 0.02))
        else:
            return None
        
        return TradingSignal(
            signal_id=str(uuid.uuid4()),
            strategy_id=self.strategy_id,
            symbol=data['symbol'].iloc[-1] if 'symbol' in data.columns else 'UNKNOWN',
            signal_type=signal_type,
            confidence=confidence,
            strength=abs(predicted_return) * 50,  # Scale for display
            entry_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=self.parameters.get('position_size_pct', 0.06),
            timeframe=TimeFrame.DAY_1,
            generated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=8),
            metadata={
                'predicted_return': predicted_return,
                'prediction_features': latest_features.to_dict()
            }
        )
    
    async def train_model(self, historical_data: pd.DataFrame):
        """Train the ML model"""
        # Mock training (replace with actual ML training)
        self.trained = True
        logger.info(f"ML model trained for strategy {self.strategy_id}")


class AlgorithmicTradingEngine:
    """Main algorithmic trading engine"""
    
    def __init__(self):
        """Initialize trading engine"""
        self.strategies = {}
        self.active_signals = {}
        self.performance_tracker = {}
        self.feature_engineer = FeatureEngineer()
        self.ml_optimizer = MLStrategyOptimizer()
        self.market_data_cache = {}
        
        # Risk management
        self.max_position_size = 0.1  # 10% max position
        self.max_daily_loss = 0.02  # 2% max daily loss
        self.max_correlation = 0.7  # Max correlation between strategies
    
    async def create_strategy(
        self,
        strategy_type: StrategyType,
        symbol: str,
        timeframe: TimeFrame,
        custom_parameters: Dict[str, Any] = None
    ) -> str:
        """Create and optimize a new trading strategy"""
        
        strategy_id = f"{strategy_type.value}_{symbol}_{timeframe.value}_{str(uuid.uuid4())[:8]}"
        
        # Get optimized parameters
        historical_data = await self._get_historical_data(symbol, timeframe)
        optimized_params = await self.ml_optimizer.optimize_strategy_parameters(
            strategy_type, historical_data
        )
        
        # Apply custom parameters
        if custom_parameters:
            optimized_params.update(custom_parameters)
        
        # Create strategy instance
        strategy = self._create_strategy_instance(strategy_id, strategy_type, optimized_params)
        
        # Train ML models if needed
        if strategy_type in [StrategyType.ML_REGRESSION, StrategyType.ML_CLASSIFICATION]:
            await strategy.train_model(historical_data)
        
        self.strategies[strategy_id] = strategy
        
        logger.info(f"Created strategy {strategy_id} with parameters: {optimized_params}")
        return strategy_id
    
    def _create_strategy_instance(
        self, 
        strategy_id: str, 
        strategy_type: StrategyType, 
        parameters: Dict[str, Any]
    ) -> TradingStrategy:
        """Create strategy instance based on type"""
        
        strategy_classes = {
            StrategyType.MEAN_REVERSION: MeanReversionStrategy,
            StrategyType.MOMENTUM: MomentumStrategy,
            StrategyType.ML_REGRESSION: MLRegressionStrategy,
        }
        
        strategy_class = strategy_classes.get(strategy_type, TradingStrategy)
        return strategy_class(strategy_id, strategy_type, parameters)
    
    async def generate_signals(self, symbol: str, current_data: Dict[str, Any]) -> List[TradingSignal]:
        """Generate signals from all active strategies for a symbol"""
        signals = []
        
        # Get relevant strategies
        symbol_strategies = [
            strategy for strategy in self.strategies.values()
            if symbol in strategy.strategy_id
        ]
        
        if not symbol_strategies:
            return signals
        
        # Get market data
        market_data = await self._prepare_market_data(symbol, current_data)
        
        # Generate signals from each strategy
        for strategy in symbol_strategies:
            try:
                signal = await strategy.generate_signal(market_data, current_data['close'])
                if signal and await self._validate_signal(signal):
                    signals.append(signal)
                    self.active_signals[signal.signal_id] = signal
                    logger.info(f"Generated signal: {signal.signal_type} {signal.symbol} at {signal.entry_price}")
            except Exception as e:
                logger.error(f"Error generating signal for strategy {strategy.strategy_id}: {e}")
        
        return signals
    
    async def _prepare_market_data(self, symbol: str, current_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare market data for analysis"""
        
        # Mock historical data preparation (replace with actual data feed)
        dates = pd.date_range(end=datetime.now(), periods=200, freq='1D')
        
        # Generate realistic mock data
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        base_price = current_data.get('close', 100.0)
        returns = np.random.normal(0.001, 0.02, 200)  # Daily returns
        prices = [base_price]
        
        for i in range(1, 200):
            prices.append(prices[-1] * (1 + returns[i]))
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': [np.random.randint(100000, 1000000) for _ in range(200)],
            'symbol': symbol
        })
        
        # Update last row with current data
        df.iloc[-1] = {
            'timestamp': datetime.now(),
            'open': current_data.get('open', base_price),
            'high': current_data.get('high', base_price),
            'low': current_data.get('low', base_price),
            'close': current_data.get('close', base_price),
            'volume': current_data.get('volume', 500000),
            'symbol': symbol
        }
        
        # Generate features
        df = await self.feature_engineer.generate_technical_features(df)
        df = await self.feature_engineer.generate_sentiment_features(symbol, df)
        
        return df
    
    async def _get_historical_data(self, symbol: str, timeframe: TimeFrame) -> pd.DataFrame:
        """Get historical data for strategy optimization"""
        # Mock implementation - replace with actual data feed
        return await self._prepare_market_data(symbol, {'close': 100.0})
    
    async def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validate signal against risk management rules"""
        
        # Check position size limits
        if signal.position_size > self.max_position_size:
            logger.warning(f"Signal {signal.signal_id} exceeds max position size")
            return False
        
        # Check signal quality
        if signal.confidence < 0.5:
            logger.warning(f"Signal {signal.signal_id} has low confidence: {signal.confidence}")
            return False
        
        # Check risk-reward ratio
        if signal.risk_reward_ratio < 1.0:
            logger.warning(f"Signal {signal.signal_id} has poor risk-reward: {signal.risk_reward_ratio}")
            return False
        
        # Check for expired signals
        if signal.expires_at < datetime.now():
            logger.warning(f"Signal {signal.signal_id} has expired")
            return False
        
        return True
    
    async def get_strategy_performance(self, strategy_id: str) -> Optional[StrategyPerformance]:
        """Get performance metrics for a strategy"""
        if strategy_id not in self.strategies:
            return None
        
        return self.strategies[strategy_id].performance
    
    async def get_all_strategies_performance(self) -> Dict[str, StrategyPerformance]:
        """Get performance for all strategies"""
        return {
            strategy_id: strategy.performance
            for strategy_id, strategy in self.strategies.items()
        }
    
    async def update_strategy_performance(self, signal_id: str, trade_result: Dict[str, Any]):
        """Update strategy performance based on trade result"""
        if signal_id not in self.active_signals:
            return
        
        signal = self.active_signals[signal_id]
        strategy = self.strategies.get(signal.strategy_id)
        
        if strategy:
            await strategy.update_performance(trade_result)
            logger.info(f"Updated performance for strategy {signal.strategy_id}")
        
        # Remove from active signals
        del self.active_signals[signal_id]
    
    async def optimize_all_strategies(self):
        """Re-optimize all strategies based on recent performance"""
        for strategy in self.strategies.values():
            try:
                # Get recent historical data
                symbol = strategy.strategy_id.split('_')[1]  # Extract symbol from ID
                historical_data = await self._get_historical_data(symbol, TimeFrame.DAY_1)
                
                # Re-optimize parameters
                new_params = await self.ml_optimizer.optimize_strategy_parameters(
                    strategy.strategy_type, historical_data
                )
                
                # Update strategy parameters
                strategy.parameters.update(new_params)
                
                logger.info(f"Re-optimized strategy {strategy.strategy_id}")
                
            except Exception as e:
                logger.error(f"Error optimizing strategy {strategy.strategy_id}: {e}")
    
    async def get_portfolio_metrics(self) -> Dict[str, Any]:
        """Get overall portfolio performance metrics"""
        if not self.strategies:
            return {}
        
        # Aggregate performance across all strategies
        total_return = sum(s.performance.total_return for s in self.strategies.values())
        total_trades = sum(s.performance.total_trades for s in self.strategies.values())
        winning_trades = sum(s.performance.winning_trades for s in self.strategies.values())
        
        # Calculate portfolio-level metrics
        portfolio_win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate Sharpe ratio (simplified)
        returns = [s.performance.total_return for s in self.strategies.values()]
        portfolio_sharpe = (np.mean(returns) / np.std(returns)) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        return {
            'total_strategies': len(self.strategies),
            'active_signals': len(self.active_signals),
            'total_return': total_return,
            'total_trades': total_trades,
            'portfolio_win_rate': portfolio_win_rate,
            'portfolio_sharpe_ratio': portfolio_sharpe,
            'best_strategy': max(self.strategies.keys(), 
                               key=lambda k: self.strategies[k].performance.total_return) 
                               if self.strategies else None,
            'worst_strategy': min(self.strategies.keys(),
                                key=lambda k: self.strategies[k].performance.total_return)
                                if self.strategies else None
        }


# Example usage and testing
async def main():
    """Example usage of algorithmic trading engine"""
    
    # Initialize trading engine
    engine = AlgorithmicTradingEngine()
    
    # Create strategies
    print("Creating AI trading strategies...")
    
    strategy1_id = await engine.create_strategy(
        StrategyType.MEAN_REVERSION,
        "RELIANCE",
        TimeFrame.DAY_1
    )
    
    strategy2_id = await engine.create_strategy(
        StrategyType.MOMENTUM,
        "RELIANCE", 
        TimeFrame.DAY_1
    )
    
    strategy3_id = await engine.create_strategy(
        StrategyType.ML_REGRESSION,
        "RELIANCE",
        TimeFrame.DAY_1
    )
    
    print(f"Created strategies: {strategy1_id}, {strategy2_id}, {strategy3_id}")
    
    # Generate signals
    current_market_data = {
        'open': 2400.0,
        'high': 2450.0,
        'low': 2380.0,
        'close': 2420.0,
        'volume': 1500000
    }
    
    signals = await engine.generate_signals("RELIANCE", current_market_data)
    
    print(f"\nGenerated {len(signals)} signals:")
    for signal in signals:
        print(f"- {signal.signal_type.upper()} {signal.symbol} at ₹{signal.entry_price:.2f}")
        print(f"  Confidence: {signal.confidence:.2f}, Target: ₹{signal.target_price:.2f}")
        print(f"  Stop Loss: ₹{signal.stop_loss:.2f}, R:R = {signal.risk_reward_ratio:.2f}")
    
    # Simulate trade results and update performance
    if signals:
        for signal in signals[:2]:  # Update first 2 signals
            mock_trade_result = {
                'signal_id': signal.signal_id,
                'pnl': np.random.normal(50, 200),  # Random P&L
                'timestamp': datetime.now(),
                'entry_price': signal.entry_price,
                'exit_price': signal.entry_price * (1 + np.random.normal(0, 0.02))
            }
            
            await engine.update_strategy_performance(signal.signal_id, mock_trade_result)
    
    # Get performance metrics
    performance = await engine.get_all_strategies_performance()
    print(f"\nStrategy Performance:")
    for strategy_id, perf in performance.items():
        print(f"- {strategy_id[:30]}...")
        print(f"  Total Return: ₹{perf.total_return:.2f}")
        print(f"  Win Rate: {perf.win_rate:.1%}")
        print(f"  Total Trades: {perf.total_trades}")
    
    # Get portfolio metrics
    portfolio_metrics = await engine.get_portfolio_metrics()
    print(f"\nPortfolio Metrics: {portfolio_metrics}")


if __name__ == "__main__":
    asyncio.run(main())