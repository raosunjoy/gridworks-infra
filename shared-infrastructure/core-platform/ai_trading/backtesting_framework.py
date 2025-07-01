#!/usr/bin/env python3
"""
GridWorks Backtesting Framework
==============================
Advanced backtesting engine optimized for Indian markets with realistic simulation
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
import copy

# Import trading engine components
from .algorithmic_trading_engine import (
    TradingStrategy, TradingSignal, StrategyType, OrderType, TimeFrame,
    StrategyPerformance, MarketData, AlgorithmicTradingEngine
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionModel(Enum):
    """Order execution models for backtesting"""
    PERFECT = "perfect"  # Instant execution at signal price
    REALISTIC = "realistic"  # Market impact, slippage, delays
    CONSERVATIVE = "conservative"  # Higher costs, realistic delays
    INDIAN_MARKET = "indian_market"  # NSE/BSE specific execution


class CostModel(Enum):
    """Transaction cost models"""
    ZERO_COST = "zero_cost"
    FLAT_FEE = "flat_fee"
    PERCENTAGE = "percentage"
    INDIAN_RETAIL = "indian_retail"  # Typical retail brokerage
    INDIAN_INSTITUTIONAL = "indian_institutional"  # Institution rates


@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    start_date: datetime
    end_date: datetime
    initial_capital: float
    execution_model: ExecutionModel
    cost_model: CostModel
    benchmark_symbol: str
    risk_free_rate: float = 0.065  # Indian 10-year bond yield
    
    # Indian market specific
    market_hours_start: str = "09:15"  # NSE opening
    market_hours_end: str = "15:30"    # NSE closing
    settlement_days: int = 2           # T+2 settlement
    
    # Execution parameters
    slippage_model: Dict[str, float] = field(default_factory=lambda: {
        'market_impact': 0.0005,  # 5 bps
        'bid_ask_spread': 0.0003,  # 3 bps
        'timing_cost': 0.0002     # 2 bps
    })
    
    # Cost parameters
    transaction_costs: Dict[str, float] = field(default_factory=lambda: {
        'brokerage': 0.0003,      # 3 bps
        'stt': 0.001,             # STT 10 bps on sell
        'exchange_charges': 0.0000345,
        'gst': 0.18,              # 18% on brokerage
        'stamp_duty': 0.00003     # 3 paisa per 100 rupees
    })


@dataclass
class Trade:
    """Individual trade record"""
    trade_id: str
    strategy_id: str
    signal_id: str
    symbol: str
    side: str  # "buy" or "sell"
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    entry_time: datetime
    exit_time: Optional[datetime]
    pnl: Optional[float]
    commission: float
    slippage: float
    tags: List[str] = field(default_factory=list)


@dataclass
class Position:
    """Current position in a security"""
    symbol: str
    quantity: int
    avg_cost: float
    market_value: float
    unrealized_pnl: float
    entry_time: datetime
    last_update: datetime


@dataclass
class BacktestResults:
    """Comprehensive backtesting results"""
    config: BacktestConfig
    start_date: datetime
    end_date: datetime
    duration_days: int
    
    # Capital and returns
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    
    # Risk metrics
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    var_95: float
    cvar_95: float
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    largest_win: float
    largest_loss: float
    
    # Indian market specific
    long_trades: int
    short_trades: int
    avg_trade_duration: float
    trades_per_month: float
    
    # Benchmark comparison
    benchmark_return: float
    alpha: float
    beta: float
    information_ratio: float
    tracking_error: float
    
    # Equity curve
    equity_curve: List[Dict[str, Any]]
    monthly_returns: Dict[str, float]
    yearly_returns: Dict[str, float]
    
    # Trade details
    all_trades: List[Trade]
    strategy_performance: Dict[str, StrategyPerformance]


class IndianMarketSimulator:
    """Simulates Indian market conditions and execution"""
    
    def __init__(self, config: BacktestConfig):
        """Initialize market simulator"""
        self.config = config
        self.current_time = config.start_date
        self.market_impact_cache = {}
    
    def is_market_open(self, timestamp: datetime) -> bool:
        """Check if market is open at given time"""
        if timestamp.weekday() >= 5:  # Weekend
            return False
        
        # Check Indian holidays (simplified)
        indian_holidays = [
            datetime(2024, 1, 26),  # Republic Day
            datetime(2024, 8, 15),  # Independence Day
            datetime(2024, 10, 2),  # Gandhi Jayanti
            # Add more holidays as needed
        ]
        
        if timestamp.date() in [h.date() for h in indian_holidays]:
            return False
        
        # Check market hours
        market_start = datetime.combine(timestamp.date(), 
                                      datetime.strptime(self.config.market_hours_start, "%H:%M").time())
        market_end = datetime.combine(timestamp.date(),
                                    datetime.strptime(self.config.market_hours_end, "%H:%M").time())
        
        return market_start <= timestamp <= market_end
    
    async def get_execution_price(
        self, 
        signal: TradingSignal, 
        market_data: Dict[str, Any],
        quantity: int
    ) -> Tuple[float, float]:
        """Get realistic execution price with slippage"""
        
        base_price = signal.entry_price
        total_slippage = 0.0
        
        if self.config.execution_model == ExecutionModel.PERFECT:
            return base_price, 0.0
        
        # Market impact based on order size
        market_impact = self._calculate_market_impact(signal.symbol, quantity, market_data)
        
        # Bid-ask spread
        bid_ask_spread = self.config.slippage_model.get('bid_ask_spread', 0.0003)
        
        # Timing cost (price moves between signal and execution)
        timing_cost = self.config.slippage_model.get('timing_cost', 0.0002)
        
        # Apply slippage based on order side
        if signal.signal_type == "buy":
            total_slippage = market_impact + bid_ask_spread/2 + timing_cost
            execution_price = base_price * (1 + total_slippage)
        else:
            total_slippage = market_impact + bid_ask_spread/2 + timing_cost
            execution_price = base_price * (1 - total_slippage)
        
        return execution_price, total_slippage * base_price
    
    def _calculate_market_impact(self, symbol: str, quantity: int, market_data: Dict[str, Any]) -> float:
        """Calculate market impact based on order size"""
        
        # Get average daily volume (mock implementation)
        avg_daily_volume = market_data.get('avg_volume', 1000000)
        
        # Calculate participation rate
        participation_rate = quantity / avg_daily_volume
        
        # Market impact model (square root law)
        base_impact = self.config.slippage_model.get('market_impact', 0.0005)
        market_impact = base_impact * np.sqrt(participation_rate * 100)
        
        # Cap at reasonable levels
        return min(market_impact, 0.01)  # Max 100 bps impact
    
    async def calculate_transaction_costs(
        self, 
        symbol: str, 
        quantity: int, 
        price: float, 
        side: str
    ) -> float:
        """Calculate realistic Indian market transaction costs"""
        
        trade_value = quantity * price
        total_cost = 0.0
        
        if self.config.cost_model == CostModel.ZERO_COST:
            return 0.0
        
        elif self.config.cost_model == CostModel.INDIAN_RETAIL:
            # Brokerage (typically 0.03% or ₹20 per executed order, whichever is lower)
            brokerage = min(trade_value * 0.0003, 20.0)
            
            # STT (Securities Transaction Tax) - 0.1% on sell side for delivery
            stt = trade_value * 0.001 if side == "sell" else 0.0
            
            # Exchange charges (NSE: 0.00345% on turnover)
            exchange_charges = trade_value * 0.0000345
            
            # GST on brokerage and exchange charges
            gst = (brokerage + exchange_charges) * 0.18
            
            # SEBI charges (₹10 per crore)
            sebi_charges = trade_value * 0.0000001
            
            # Stamp duty (0.003% on buy side)
            stamp_duty = trade_value * 0.00003 if side == "buy" else 0.0
            
            total_cost = brokerage + stt + exchange_charges + gst + sebi_charges + stamp_duty
        
        elif self.config.cost_model == CostModel.INDIAN_INSTITUTIONAL:
            # Lower institutional rates
            brokerage = trade_value * 0.0001  # 1 bps
            stt = trade_value * 0.001 if side == "sell" else 0.0
            exchange_charges = trade_value * 0.0000345
            gst = (brokerage + exchange_charges) * 0.18
            stamp_duty = trade_value * 0.00003 if side == "buy" else 0.0
            
            total_cost = brokerage + stt + exchange_charges + gst + stamp_duty
        
        return total_cost


class BacktestingEngine:
    """Advanced backtesting engine"""
    
    def __init__(self, config: BacktestConfig):
        """Initialize backtesting engine"""
        self.config = config
        self.market_simulator = IndianMarketSimulator(config)
        
        # Portfolio state
        self.current_capital = config.initial_capital
        self.positions = {}
        self.pending_orders = {}
        self.completed_trades = []
        
        # Performance tracking
        self.equity_curve = []
        self.daily_returns = []
        self.benchmark_data = {}
        
        # Strategy tracking
        self.strategy_performance = {}
    
    async def run_backtest(
        self, 
        strategies: Dict[str, TradingStrategy], 
        market_data: pd.DataFrame
    ) -> BacktestResults:
        """Run comprehensive backtest"""
        
        logger.info(f"Starting backtest from {self.config.start_date} to {self.config.end_date}")
        
        # Initialize strategies
        for strategy_id, strategy in strategies.items():
            self.strategy_performance[strategy_id] = copy.deepcopy(strategy.performance)
        
        # Simulate trading day by day
        current_date = self.config.start_date
        day_count = 0
        
        while current_date <= self.config.end_date:
            
            if self.market_simulator.is_market_open(current_date):
                await self._simulate_trading_day(current_date, strategies, market_data)
                day_count += 1
            
            # Update equity curve
            await self._update_equity_curve(current_date)
            
            current_date += timedelta(days=1)
            
            # Progress logging
            if day_count % 50 == 0:
                logger.info(f"Processed {day_count} trading days, current capital: ₹{self.current_capital:,.2f}")
        
        # Generate comprehensive results
        results = await self._generate_results()
        
        logger.info(f"Backtest completed. Final return: {results.total_return:.2%}")
        return results
    
    async def _simulate_trading_day(
        self, 
        date: datetime, 
        strategies: Dict[str, TradingStrategy], 
        market_data: pd.DataFrame
    ):
        """Simulate a single trading day"""
        
        # Get market data for the day
        day_data = self._get_market_data_for_date(date, market_data)
        
        if day_data.empty:
            return
        
        # Generate signals from all strategies
        all_signals = []
        for strategy_id, strategy in strategies.items():
            try:
                # Prepare historical data up to current date
                historical_data = market_data[market_data['timestamp'] <= date]
                
                if len(historical_data) < 20:  # Need minimum history
                    continue
                
                # Generate signal
                current_price = day_data['close'].iloc[-1] if not day_data.empty else 100.0
                signal = await strategy.generate_signal(historical_data, current_price)
                
                if signal:
                    all_signals.append(signal)
                    
            except Exception as e:
                logger.error(f"Error generating signal for {strategy_id}: {e}")
        
        # Execute signals
        for signal in all_signals:
            await self._execute_signal(signal, day_data, date)
        
        # Update positions with current market prices
        await self._update_positions(day_data)
        
        # Check for position exits (stop losses, take profits)
        await self._check_position_exits(day_data, date)
    
    def _get_market_data_for_date(self, date: datetime, market_data: pd.DataFrame) -> pd.DataFrame:
        """Get market data for specific date"""
        
        # For demo, create mock data
        if market_data.empty:
            return pd.DataFrame()
        
        # Find closest date in market data
        market_data['date_only'] = pd.to_datetime(market_data['timestamp']).dt.date
        target_date = date.date()
        
        day_data = market_data[market_data['date_only'] == target_date]
        
        if day_data.empty:
            # Use last available data
            day_data = market_data.tail(1)
        
        return day_data
    
    async def _execute_signal(self, signal: TradingSignal, market_data: pd.DataFrame, date: datetime):
        """Execute a trading signal"""
        
        # Calculate position size in shares
        position_value = self.current_capital * signal.position_size
        current_price = signal.entry_price
        quantity = int(position_value / current_price)
        
        if quantity == 0:
            return
        
        # Get execution price with slippage
        execution_price, slippage_cost = await self.market_simulator.get_execution_price(
            signal, market_data.iloc[-1].to_dict(), quantity
        )
        
        # Calculate transaction costs
        transaction_cost = await self.market_simulator.calculate_transaction_costs(
            signal.symbol, quantity, execution_price, signal.signal_type
        )
        
        # Check if we have enough capital
        total_cost = quantity * execution_price + transaction_cost + slippage_cost
        
        if signal.signal_type == "buy" and total_cost > self.current_capital:
            logger.warning(f"Insufficient capital for {signal.symbol} trade")
            return
        
        # Execute trade
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            strategy_id=signal.strategy_id,
            signal_id=signal.signal_id,
            symbol=signal.symbol,
            side=signal.signal_type,
            quantity=quantity if signal.signal_type == "buy" else -quantity,
            entry_price=execution_price,
            exit_price=None,
            entry_time=date,
            exit_time=None,
            pnl=None,
            commission=transaction_cost,
            slippage=slippage_cost
        )
        
        # Update portfolio
        if signal.signal_type == "buy":
            self.current_capital -= total_cost
            self._add_position(signal.symbol, quantity, execution_price, date)
        else:
            # Short selling (if supported)
            self.current_capital += (quantity * execution_price - transaction_cost - slippage_cost)
            self._add_position(signal.symbol, -quantity, execution_price, date)
        
        self.completed_trades.append(trade)
        
        logger.debug(f"Executed {signal.signal_type} {quantity} {signal.symbol} at ₹{execution_price:.2f}")
    
    def _add_position(self, symbol: str, quantity: int, price: float, timestamp: datetime):
        """Add or update position"""
        
        if symbol in self.positions:
            # Update existing position
            position = self.positions[symbol]
            total_quantity = position.quantity + quantity
            
            if total_quantity == 0:
                # Position closed
                del self.positions[symbol]
            else:
                # Update average cost
                total_cost = (position.quantity * position.avg_cost + quantity * price)
                position.avg_cost = total_cost / total_quantity
                position.quantity = total_quantity
                position.last_update = timestamp
        else:
            # New position
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_cost=price,
                market_value=quantity * price,
                unrealized_pnl=0.0,
                entry_time=timestamp,
                last_update=timestamp
            )
    
    async def _update_positions(self, market_data: pd.DataFrame):
        """Update position values with current market prices"""
        
        for position in self.positions.values():
            # Get current price for symbol
            symbol_data = market_data[market_data.get('symbol', '') == position.symbol]
            
            if not symbol_data.empty:
                current_price = symbol_data['close'].iloc[-1]
                position.market_value = position.quantity * current_price
                position.unrealized_pnl = (current_price - position.avg_cost) * position.quantity
    
    async def _check_position_exits(self, market_data: pd.DataFrame, date: datetime):
        """Check for stop loss and take profit exits"""
        
        positions_to_close = []
        
        for symbol, position in self.positions.items():
            # Get current price
            symbol_data = market_data[market_data.get('symbol', '') == symbol]
            
            if symbol_data.empty:
                continue
            
            current_price = symbol_data['close'].iloc[-1]
            
            # Simple exit logic (can be enhanced)
            pnl_pct = (current_price - position.avg_cost) / position.avg_cost
            
            # Exit conditions
            should_exit = False
            exit_reason = ""
            
            if position.quantity > 0:  # Long position
                if pnl_pct <= -0.05:  # 5% stop loss
                    should_exit = True
                    exit_reason = "stop_loss"
                elif pnl_pct >= 0.10:  # 10% take profit
                    should_exit = True
                    exit_reason = "take_profit"
            else:  # Short position
                if pnl_pct >= 0.05:  # 5% stop loss for short
                    should_exit = True
                    exit_reason = "stop_loss"
                elif pnl_pct <= -0.10:  # 10% take profit for short
                    should_exit = True
                    exit_reason = "take_profit"
            
            if should_exit:
                positions_to_close.append((symbol, current_price, exit_reason))
        
        # Close positions
        for symbol, exit_price, reason in positions_to_close:
            await self._close_position(symbol, exit_price, date, reason)
    
    async def _close_position(self, symbol: str, exit_price: float, date: datetime, reason: str):
        """Close a position"""
        
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Calculate transaction costs for closing
        transaction_cost = await self.market_simulator.calculate_transaction_costs(
            symbol, abs(position.quantity), exit_price, "sell" if position.quantity > 0 else "buy"
        )
        
        # Calculate P&L
        pnl = (exit_price - position.avg_cost) * position.quantity - transaction_cost
        
        # Update capital
        if position.quantity > 0:  # Closing long position
            proceeds = position.quantity * exit_price - transaction_cost
            self.current_capital += proceeds
        else:  # Closing short position
            cost = abs(position.quantity) * exit_price + transaction_cost
            self.current_capital -= cost
        
        # Create exit trade record
        exit_trade = Trade(
            trade_id=str(uuid.uuid4()),
            strategy_id="position_management",
            signal_id="exit",
            symbol=symbol,
            side="sell" if position.quantity > 0 else "buy",
            quantity=-position.quantity,  # Opposite of original position
            entry_price=position.avg_cost,
            exit_price=exit_price,
            entry_time=position.entry_time,
            exit_time=date,
            pnl=pnl,
            commission=transaction_cost,
            slippage=0.0,
            tags=[reason]
        )
        
        self.completed_trades.append(exit_trade)
        
        # Remove position
        del self.positions[symbol]
        
        logger.debug(f"Closed {symbol} position: P&L = ₹{pnl:.2f} ({reason})")
    
    async def _update_equity_curve(self, date: datetime):
        """Update equity curve with current portfolio value"""
        
        # Calculate current portfolio value
        cash = self.current_capital
        position_value = sum(pos.market_value for pos in self.positions.values())
        total_equity = cash + position_value
        
        # Calculate daily return
        if self.equity_curve:
            prev_equity = self.equity_curve[-1]['equity']
            daily_return = (total_equity - prev_equity) / prev_equity
        else:
            daily_return = 0.0
        
        self.equity_curve.append({
            'date': date,
            'equity': total_equity,
            'cash': cash,
            'positions_value': position_value,
            'daily_return': daily_return
        })
        
        self.daily_returns.append(daily_return)
    
    async def _generate_results(self) -> BacktestResults:
        """Generate comprehensive backtest results"""
        
        # Basic calculations
        initial_capital = self.config.initial_capital
        final_capital = self.equity_curve[-1]['equity'] if self.equity_curve else initial_capital
        total_return = (final_capital - initial_capital) / initial_capital
        
        duration_days = (self.config.end_date - self.config.start_date).days
        duration_years = duration_days / 365.25
        annualized_return = (final_capital / initial_capital) ** (1 / duration_years) - 1 if duration_years > 0 else 0
        
        # Risk metrics
        daily_returns_array = np.array(self.daily_returns[1:])  # Exclude first day
        volatility = np.std(daily_returns_array) * np.sqrt(252) if len(daily_returns_array) > 0 else 0
        
        sharpe_ratio = (annualized_return - self.config.risk_free_rate) / volatility if volatility > 0 else 0
        
        # Drawdown calculation
        equity_values = [point['equity'] for point in self.equity_curve]
        running_max = np.maximum.accumulate(equity_values)
        drawdown = (equity_values - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Trade statistics
        completed_trades = [t for t in self.completed_trades if t.pnl is not None]
        winning_trades = len([t for t in completed_trades if t.pnl > 0])
        losing_trades = len([t for t in completed_trades if t.pnl <= 0])
        
        win_rate = winning_trades / len(completed_trades) if completed_trades else 0
        avg_win = np.mean([t.pnl for t in completed_trades if t.pnl > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([abs(t.pnl) for t in completed_trades if t.pnl <= 0]) if losing_trades > 0 else 0
        
        profit_factor = (avg_win * winning_trades) / (avg_loss * losing_trades) if losing_trades > 0 and avg_loss > 0 else 0
        
        # More advanced metrics (simplified)
        sortino_ratio = sharpe_ratio * 1.2  # Approximation
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0
        var_95 = np.percentile(daily_returns_array, 5) if len(daily_returns_array) > 0 else 0
        
        # Monthly and yearly returns
        monthly_returns = {}
        yearly_returns = {}
        
        for point in self.equity_curve:
            month_key = point['date'].strftime("%Y-%m")
            year_key = str(point['date'].year)
            
            if month_key not in monthly_returns:
                monthly_returns[month_key] = point['daily_return']
            else:
                monthly_returns[month_key] = (1 + monthly_returns[month_key]) * (1 + point['daily_return']) - 1
            
            if year_key not in yearly_returns:
                yearly_returns[year_key] = point['daily_return']
            else:
                yearly_returns[year_key] = (1 + yearly_returns[year_key]) * (1 + point['daily_return']) - 1
        
        # Create results object
        results = BacktestResults(
            config=self.config,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            duration_days=duration_days,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=30,  # Simplified
            var_95=var_95,
            cvar_95=var_95 * 1.3,  # Approximation
            total_trades=len(completed_trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            largest_win=max([t.pnl for t in completed_trades], default=0),
            largest_loss=min([t.pnl for t in completed_trades], default=0),
            long_trades=len([t for t in completed_trades if t.quantity > 0]),
            short_trades=len([t for t in completed_trades if t.quantity < 0]),
            avg_trade_duration=2.5,  # Simplified
            trades_per_month=len(completed_trades) / (duration_days / 30.4) if duration_days > 0 else 0,
            benchmark_return=0.15,  # Mock benchmark return
            alpha=annualized_return - 0.15,  # Alpha vs benchmark
            beta=1.1,  # Simplified
            information_ratio=0.5,  # Simplified
            tracking_error=0.03,  # Simplified
            equity_curve=self.equity_curve,
            monthly_returns=monthly_returns,
            yearly_returns=yearly_returns,
            all_trades=self.completed_trades,
            strategy_performance=self.strategy_performance
        )
        
        return results


# Example usage and testing
async def main():
    """Example backtesting"""
    
    # Create backtest configuration
    config = BacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31),
        initial_capital=1000000.0,  # 10 lakh
        execution_model=ExecutionModel.REALISTIC,
        cost_model=CostModel.INDIAN_RETAIL,
        benchmark_symbol="NIFTY50"
    )
    
    # Create mock strategies
    from .algorithmic_trading_engine import MeanReversionStrategy, MomentumStrategy
    
    strategies = {
        "mean_reversion_RELIANCE": MeanReversionStrategy(
            "mr_1", 
            StrategyType.MEAN_REVERSION,
            {'lookback_window': 20, 'entry_threshold': 2.0}
        ),
        "momentum_RELIANCE": MomentumStrategy(
            "mom_1",
            StrategyType.MOMENTUM,
            {'momentum_period': 10, 'strength_threshold': 0.02}
        )
    }
    
    # Create mock market data
    dates = pd.date_range(start=config.start_date, end=config.end_date, freq='D')
    market_data = pd.DataFrame({
        'timestamp': dates,
        'symbol': 'RELIANCE',
        'open': 2400 + np.random.normal(0, 50, len(dates)),
        'high': 2450 + np.random.normal(0, 60, len(dates)),
        'low': 2350 + np.random.normal(0, 40, len(dates)),
        'close': 2420 + np.random.normal(0, 55, len(dates)),
        'volume': np.random.randint(1000000, 3000000, len(dates))
    })
    
    # Run backtest
    engine = BacktestingEngine(config)
    results = await engine.run_backtest(strategies, market_data)
    
    # Display results
    print("=== BACKTEST RESULTS ===")
    print(f"Period: {results.start_date.date()} to {results.end_date.date()}")
    print(f"Initial Capital: ₹{results.initial_capital:,.2f}")
    print(f"Final Capital: ₹{results.final_capital:,.2f}")
    print(f"Total Return: {results.total_return:.2%}")
    print(f"Annualized Return: {results.annualized_return:.2%}")
    print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {results.max_drawdown:.2%}")
    print(f"Win Rate: {results.win_rate:.1%}")
    print(f"Total Trades: {results.total_trades}")
    print(f"Profit Factor: {results.profit_factor:.2f}")


if __name__ == "__main__":
    asyncio.run(main())