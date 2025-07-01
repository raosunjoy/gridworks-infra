#!/usr/bin/env python3
"""
GridWorks HNI Portfolio Management System
========================================
Advanced portfolio management for High Net Worth Individual clients
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetClass(Enum):
    """Asset class categories"""
    EQUITY = "equity"
    DEBT = "debt"
    COMMODITIES = "commodities"
    CURRENCY = "currency"
    DERIVATIVES = "derivatives"
    REAL_ESTATE = "real_estate"
    ALTERNATIVE = "alternative"
    CASH = "cash"


class PortfolioType(Enum):
    """Portfolio management types"""
    CONSERVATIVE = "conservative"     # Low risk, stable returns
    BALANCED = "balanced"            # Moderate risk-return
    AGGRESSIVE = "aggressive"        # High risk, high return
    INCOME = "income"               # Dividend/income focused
    GROWTH = "growth"               # Capital appreciation
    CUSTOM = "custom"               # Customized allocation


class RiskProfile(Enum):
    """Client risk profiles"""
    VERY_LOW = "very_low"           # 0-10% equity
    LOW = "low"                     # 10-30% equity
    MODERATE = "moderate"           # 30-60% equity
    HIGH = "high"                   # 60-80% equity
    VERY_HIGH = "very_high"         # 80-100% equity


class RebalanceFrequency(Enum):
    """Portfolio rebalancing frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    THRESHOLD = "threshold"         # Based on deviation thresholds


@dataclass
class AssetAllocation:
    """Asset allocation target"""
    asset_class: AssetClass
    target_percentage: float
    min_percentage: float
    max_percentage: float
    current_percentage: float = 0.0
    current_value: float = 0.0
    
    @property
    def is_within_range(self) -> bool:
        """Check if current allocation is within range"""
        return self.min_percentage <= self.current_percentage <= self.max_percentage
    
    @property
    def deviation_from_target(self) -> float:
        """Calculate deviation from target"""
        return self.current_percentage - self.target_percentage


@dataclass
class PortfolioHolding:
    """Individual portfolio holding"""
    symbol: str
    name: str
    asset_class: AssetClass
    quantity: float
    current_price: float
    cost_basis: float
    market_value: float
    weight: float
    
    # Performance metrics
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_return: float = 0.0
    
    # Risk metrics
    beta: float = 1.0
    volatility: float = 0.0
    
    # Dividend/income
    annual_dividend: float = 0.0
    dividend_yield: float = 0.0
    
    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl


@dataclass
class PortfolioPerformance:
    """Portfolio performance metrics"""
    portfolio_id: str
    as_of_date: datetime
    
    # Value metrics
    total_value: float
    total_cost_basis: float
    cash_balance: float
    
    # Return metrics
    total_return: float
    total_return_pct: float
    ytd_return: float
    mtd_return: float
    
    # Risk metrics
    portfolio_beta: float
    portfolio_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    
    # Asset allocation
    equity_allocation: float
    debt_allocation: float
    cash_allocation: float
    other_allocation: float
    
    # Benchmark comparison
    benchmark_return: float
    alpha: float
    tracking_error: float
    information_ratio: float


@dataclass
class HNIPortfolio:
    """HNI Portfolio data structure"""
    portfolio_id: str
    client_id: str
    portfolio_name: str
    portfolio_type: PortfolioType
    risk_profile: RiskProfile
    
    # Financial details
    total_value: float
    cash_balance: float
    invested_amount: float
    
    # Configuration
    target_allocations: List[AssetAllocation]
    rebalance_frequency: RebalanceFrequency
    rebalance_threshold: float = 0.05  # 5% deviation threshold
    
    # Holdings
    holdings: List[PortfolioHolding] = field(default_factory=list)
    
    # Performance tracking
    performance_history: List[PortfolioPerformance] = field(default_factory=list)
    
    # Management
    created_at: datetime = field(default_factory=datetime.now)
    last_rebalanced: Optional[datetime] = None
    next_rebalance: Optional[datetime] = None
    manager_id: Optional[str] = None
    
    @property
    def current_allocation(self) -> Dict[AssetClass, float]:
        """Get current asset allocation percentages"""
        allocation = {}
        for holding in self.holdings:
            asset_class = holding.asset_class
            if asset_class not in allocation:
                allocation[asset_class] = 0.0
            allocation[asset_class] += holding.weight
        return allocation
    
    @property
    def needs_rebalancing(self) -> bool:
        """Check if portfolio needs rebalancing"""
        current_alloc = self.current_allocation
        
        for target in self.target_allocations:
            current_pct = current_alloc.get(target.asset_class, 0.0)
            deviation = abs(current_pct - target.target_percentage)
            
            if deviation > self.rebalance_threshold:
                return True
        
        return False


class PortfolioConstructor:
    """Advanced portfolio construction engine"""
    
    def __init__(self):
        """Initialize portfolio constructor"""
        self.universe = {}  # Available securities universe
        self.risk_models = {}
        self.optimization_constraints = {}
        
        # Initialize default allocations
        self._initialize_default_allocations()
    
    def _initialize_default_allocations(self):
        """Initialize default asset allocations by risk profile"""
        self.default_allocations = {
            RiskProfile.VERY_LOW: [
                AssetAllocation(AssetClass.EQUITY, 10.0, 0.0, 20.0),
                AssetAllocation(AssetClass.DEBT, 70.0, 60.0, 80.0),
                AssetAllocation(AssetClass.CASH, 20.0, 10.0, 40.0)
            ],
            RiskProfile.LOW: [
                AssetAllocation(AssetClass.EQUITY, 25.0, 15.0, 35.0),
                AssetAllocation(AssetClass.DEBT, 60.0, 50.0, 70.0),
                AssetAllocation(AssetClass.CASH, 15.0, 5.0, 25.0)
            ],
            RiskProfile.MODERATE: [
                AssetAllocation(AssetClass.EQUITY, 50.0, 40.0, 60.0),
                AssetAllocation(AssetClass.DEBT, 35.0, 25.0, 45.0),
                AssetAllocation(AssetClass.CASH, 10.0, 5.0, 20.0),
                AssetAllocation(AssetClass.COMMODITIES, 5.0, 0.0, 10.0)
            ],
            RiskProfile.HIGH: [
                AssetAllocation(AssetClass.EQUITY, 70.0, 60.0, 80.0),
                AssetAllocation(AssetClass.DEBT, 20.0, 10.0, 30.0),
                AssetAllocation(AssetClass.COMMODITIES, 5.0, 0.0, 15.0),
                AssetAllocation(AssetClass.CASH, 5.0, 0.0, 15.0)
            ],
            RiskProfile.VERY_HIGH: [
                AssetAllocation(AssetClass.EQUITY, 85.0, 75.0, 95.0),
                AssetAllocation(AssetClass.DERIVATIVES, 10.0, 0.0, 20.0),
                AssetAllocation(AssetClass.CASH, 5.0, 0.0, 15.0)
            ]
        }
    
    async def create_portfolio(
        self,
        client_id: str,
        portfolio_name: str,
        portfolio_type: PortfolioType,
        risk_profile: RiskProfile,
        initial_amount: float,
        custom_allocations: Optional[List[AssetAllocation]] = None
    ) -> HNIPortfolio:
        """Create new HNI portfolio"""
        
        portfolio_id = str(uuid.uuid4())
        
        # Use custom allocations or defaults
        target_allocations = custom_allocations or self.default_allocations[risk_profile]
        
        # Create portfolio
        portfolio = HNIPortfolio(
            portfolio_id=portfolio_id,
            client_id=client_id,
            portfolio_name=portfolio_name,
            portfolio_type=portfolio_type,
            risk_profile=risk_profile,
            total_value=initial_amount,
            cash_balance=initial_amount,
            invested_amount=0.0,
            target_allocations=target_allocations,
            rebalance_frequency=RebalanceFrequency.QUARTERLY
        )
        
        # Initial portfolio construction
        await self._construct_initial_portfolio(portfolio)
        
        logger.info(f"Created HNI portfolio {portfolio_id} for client {client_id}")
        return portfolio
    
    async def _construct_initial_portfolio(self, portfolio: HNIPortfolio):
        """Construct initial portfolio based on allocations"""
        
        # Get recommended securities for each asset class
        recommended_securities = await self._get_recommended_securities(portfolio)
        
        # Allocate funds based on target allocations
        for allocation in portfolio.target_allocations:
            allocation_amount = portfolio.total_value * (allocation.target_percentage / 100)
            
            if allocation_amount > 0:
                securities = recommended_securities.get(allocation.asset_class, [])
                
                if securities:
                    # Distribute allocation among securities
                    await self._allocate_to_securities(
                        portfolio, 
                        securities, 
                        allocation_amount,
                        allocation.asset_class
                    )
        
        # Update portfolio metrics
        await self._update_portfolio_metrics(portfolio)
    
    async def _get_recommended_securities(self, portfolio: HNIPortfolio) -> Dict[AssetClass, List[Dict]]:
        """Get recommended securities for each asset class"""
        
        # Mock recommended securities (replace with actual research/selection logic)
        recommendations = {
            AssetClass.EQUITY: [
                {'symbol': 'RELIANCE', 'name': 'Reliance Industries', 'weight': 0.3, 'price': 2420.0},
                {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'weight': 0.25, 'price': 3680.0},
                {'symbol': 'HDFC', 'name': 'HDFC Bank', 'weight': 0.2, 'price': 1580.0},
                {'symbol': 'INFY', 'name': 'Infosys', 'weight': 0.15, 'price': 1420.0},
                {'symbol': 'ITC', 'name': 'ITC Limited', 'weight': 0.1, 'price': 310.0}
            ],
            AssetClass.DEBT: [
                {'symbol': 'GILT_10Y', 'name': '10 Year Government Bond', 'weight': 0.4, 'price': 100.0},
                {'symbol': 'CORP_AAA', 'name': 'AAA Corporate Bond Fund', 'weight': 0.3, 'price': 100.0},
                {'symbol': 'LIQUID_FUND', 'name': 'Liquid Fund', 'weight': 0.3, 'price': 100.0}
            ],
            AssetClass.COMMODITIES: [
                {'symbol': 'GOLD_ETF', 'name': 'Gold ETF', 'weight': 0.6, 'price': 5500.0},
                {'symbol': 'SILVER_ETF', 'name': 'Silver ETF', 'weight': 0.4, 'price': 70000.0}
            ],
            AssetClass.CASH: [
                {'symbol': 'CASH', 'name': 'Cash/Money Market', 'weight': 1.0, 'price': 1.0}
            ]
        }
        
        return recommendations
    
    async def _allocate_to_securities(
        self,
        portfolio: HNIPortfolio,
        securities: List[Dict],
        total_amount: float,
        asset_class: AssetClass
    ):
        """Allocate amount to securities within asset class"""
        
        for security in securities:
            security_amount = total_amount * security['weight']
            quantity = security_amount / security['price']
            
            holding = PortfolioHolding(
                symbol=security['symbol'],
                name=security['name'],
                asset_class=asset_class,
                quantity=quantity,
                current_price=security['price'],
                cost_basis=security['price'],
                market_value=security_amount,
                weight=security_amount / portfolio.total_value * 100
            )
            
            portfolio.holdings.append(holding)
            portfolio.cash_balance -= security_amount
            portfolio.invested_amount += security_amount
    
    async def _update_portfolio_metrics(self, portfolio: HNIPortfolio):
        """Update portfolio performance metrics"""
        
        # Update holding weights
        for holding in portfolio.holdings:
            holding.weight = (holding.market_value / portfolio.total_value) * 100
        
        # Update asset allocations
        for allocation in portfolio.target_allocations:
            current_value = sum(
                h.market_value for h in portfolio.holdings 
                if h.asset_class == allocation.asset_class
            )
            allocation.current_value = current_value
            allocation.current_percentage = (current_value / portfolio.total_value) * 100


class PortfolioOptimizer:
    """Modern Portfolio Theory optimization"""
    
    def __init__(self):
        """Initialize portfolio optimizer"""
        self.risk_free_rate = 0.065  # 6.5% risk-free rate
        self.optimization_methods = {
            'mean_variance': self._mean_variance_optimization,
            'risk_parity': self._risk_parity_optimization,
            'black_litterman': self._black_litterman_optimization,
            'maximum_diversification': self._maximum_diversification
        }
    
    async def optimize_portfolio(
        self,
        portfolio: HNIPortfolio,
        method: str = 'mean_variance',
        constraints: Optional[Dict] = None
    ) -> Dict[str, float]:
        """Optimize portfolio allocation"""
        
        if method not in self.optimization_methods:
            logger.error(f"Unknown optimization method: {method}")
            return {}
        
        # Get historical data for optimization
        historical_data = await self._get_historical_data(portfolio)
        
        # Run optimization
        optimized_weights = await self.optimization_methods[method](
            historical_data, constraints or {}
        )
        
        logger.info(f"Portfolio optimization completed using {method}")
        return optimized_weights
    
    async def _get_historical_data(self, portfolio: HNIPortfolio) -> pd.DataFrame:
        """Get historical return data for optimization"""
        
        # Mock historical returns (replace with actual data)
        symbols = [h.symbol for h in portfolio.holdings]
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')  # 1 year daily
        
        data = {}
        for symbol in symbols:
            # Generate mock returns with different characteristics
            if symbol.startswith('GILT') or symbol.startswith('CORP'):
                # Debt: lower volatility, stable returns
                returns = np.random.normal(0.0002, 0.01, len(dates))  # 0.02% daily, 1% vol
            elif symbol in ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ITC']:
                # Equity: higher volatility
                returns = np.random.normal(0.0005, 0.02, len(dates))  # 0.05% daily, 2% vol
            elif 'ETF' in symbol:
                # Commodities: medium volatility
                returns = np.random.normal(0.0003, 0.015, len(dates))  # 0.03% daily, 1.5% vol
            else:
                # Default
                returns = np.random.normal(0.0004, 0.018, len(dates))
            
            data[symbol] = returns
        
        return pd.DataFrame(data, index=dates)
    
    async def _mean_variance_optimization(
        self, 
        returns_data: pd.DataFrame, 
        constraints: Dict
    ) -> Dict[str, float]:
        """Mean-variance optimization (Markowitz)"""
        
        # Calculate expected returns and covariance matrix
        expected_returns = returns_data.mean() * 252  # Annualized
        cov_matrix = returns_data.cov() * 252  # Annualized
        
        # Mock optimization (replace with actual optimization library like cvxpy)
        n_assets = len(returns_data.columns)
        
        # Equal weight as starting point
        weights = np.ones(n_assets) / n_assets
        
        # Apply simple optimization logic
        risk_adjusted_returns = expected_returns / np.sqrt(np.diag(cov_matrix))
        weights = risk_adjusted_returns / risk_adjusted_returns.sum()
        
        # Apply constraints
        min_weight = constraints.get('min_weight', 0.05)
        max_weight = constraints.get('max_weight', 0.4)
        
        weights = np.clip(weights, min_weight, max_weight)
        weights = weights / weights.sum()  # Renormalize
        
        return dict(zip(returns_data.columns, weights))
    
    async def _risk_parity_optimization(
        self, 
        returns_data: pd.DataFrame, 
        constraints: Dict
    ) -> Dict[str, float]:
        """Risk parity optimization"""
        
        # Calculate volatilities
        volatilities = returns_data.std() * np.sqrt(252)
        
        # Inverse volatility weights
        inv_vol_weights = 1 / volatilities
        weights = inv_vol_weights / inv_vol_weights.sum()
        
        return dict(zip(returns_data.columns, weights))
    
    async def _black_litterman_optimization(
        self, 
        returns_data: pd.DataFrame, 
        constraints: Dict
    ) -> Dict[str, float]:
        """Black-Litterman optimization"""
        
        # Simplified Black-Litterman (full implementation requires market cap data)
        # Start with market cap weights (mock)
        n_assets = len(returns_data.columns)
        market_weights = np.ones(n_assets) / n_assets
        
        # Apply views (mock - in practice, use analyst views)
        expected_returns = returns_data.mean() * 252
        
        # Combine market equilibrium with views
        weights = market_weights * (1 + expected_returns * 0.1)  # Simple adjustment
        weights = weights / weights.sum()
        
        return dict(zip(returns_data.columns, weights))
    
    async def _maximum_diversification(
        self, 
        returns_data: pd.DataFrame, 
        constraints: Dict
    ) -> Dict[str, float]:
        """Maximum diversification optimization"""
        
        # Calculate correlations
        corr_matrix = returns_data.corr()
        
        # Diversification ratio = weighted avg volatility / portfolio volatility
        # Maximize by minimizing correlations
        
        # Simplified: use inverse correlation weights
        avg_correlations = corr_matrix.mean()
        inv_corr_weights = 1 / (1 + avg_correlations)
        weights = inv_corr_weights / inv_corr_weights.sum()
        
        return dict(zip(returns_data.columns, weights))


class PortfolioRebalancer:
    """Portfolio rebalancing engine"""
    
    def __init__(self):
        """Initialize rebalancer"""
        self.rebalance_costs = 0.001  # 10 bps transaction costs
        self.min_trade_amount = 1000  # Minimum trade amount
    
    async def rebalance_portfolio(
        self,
        portfolio: HNIPortfolio,
        target_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """Rebalance portfolio to target allocations"""
        
        if not portfolio.needs_rebalancing and not target_weights:
            logger.info(f"Portfolio {portfolio.portfolio_id} does not need rebalancing")
            return []
        
        # Calculate required trades
        rebalance_trades = await self._calculate_rebalance_trades(portfolio, target_weights)
        
        # Filter out small trades
        significant_trades = [
            trade for trade in rebalance_trades 
            if abs(trade['trade_amount']) >= self.min_trade_amount
        ]
        
        if significant_trades:
            # Execute trades (in production, integrate with order management)
            await self._execute_rebalance_trades(portfolio, significant_trades)
            
            # Update portfolio
            portfolio.last_rebalanced = datetime.now()
            portfolio.next_rebalance = self._calculate_next_rebalance_date(portfolio)
            
            logger.info(f"Rebalanced portfolio {portfolio.portfolio_id} with {len(significant_trades)} trades")
        
        return significant_trades
    
    async def _calculate_rebalance_trades(
        self,
        portfolio: HNIPortfolio,
        target_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """Calculate required trades for rebalancing"""
        
        trades = []
        
        # If target weights provided, use them; otherwise use asset allocation targets
        if target_weights:
            # Security-level rebalancing
            total_value = portfolio.total_value
            
            for holding in portfolio.holdings:
                target_weight = target_weights.get(holding.symbol, 0.0)
                target_value = total_value * target_weight
                current_value = holding.market_value
                
                trade_amount = target_value - current_value
                
                if abs(trade_amount) > self.min_trade_amount:
                    trades.append({
                        'symbol': holding.symbol,
                        'current_value': current_value,
                        'target_value': target_value,
                        'trade_amount': trade_amount,
                        'trade_type': 'buy' if trade_amount > 0 else 'sell',
                        'quantity': abs(trade_amount) / holding.current_price
                    })
        
        else:
            # Asset class level rebalancing
            current_allocation = portfolio.current_allocation
            
            for target_alloc in portfolio.target_allocations:
                asset_class = target_alloc.asset_class
                current_pct = current_allocation.get(asset_class, 0.0)
                target_pct = target_alloc.target_percentage
                
                deviation = current_pct - target_pct
                
                if abs(deviation) > portfolio.rebalance_threshold:
                    trade_value = portfolio.total_value * (deviation / 100)
                    
                    # Find securities in this asset class for trading
                    asset_holdings = [h for h in portfolio.holdings if h.asset_class == asset_class]
                    
                    if asset_holdings:
                        # Distribute trade across holdings in asset class
                        for holding in asset_holdings:
                            holding_trade = trade_value * (holding.weight / current_pct)
                            
                            if abs(holding_trade) > self.min_trade_amount:
                                trades.append({
                                    'symbol': holding.symbol,
                                    'asset_class': asset_class.value,
                                    'current_value': holding.market_value,
                                    'trade_amount': -holding_trade,  # Negative because we're reducing overweight
                                    'trade_type': 'sell' if holding_trade > 0 else 'buy',
                                    'quantity': abs(holding_trade) / holding.current_price
                                })
        
        return trades
    
    async def _execute_rebalance_trades(self, portfolio: HNIPortfolio, trades: List[Dict]):
        """Execute rebalancing trades"""
        
        total_costs = 0.0
        
        for trade in trades:
            # Simulate trade execution
            trade_value = abs(trade['trade_amount'])
            transaction_cost = trade_value * self.rebalance_costs
            total_costs += transaction_cost
            
            # Update holding
            for holding in portfolio.holdings:
                if holding.symbol == trade['symbol']:
                    if trade['trade_type'] == 'buy':
                        holding.quantity += trade['quantity']
                        holding.market_value += trade_value
                        portfolio.cash_balance -= (trade_value + transaction_cost)
                    else:
                        holding.quantity -= trade['quantity']
                        holding.market_value -= trade_value
                        portfolio.cash_balance += (trade_value - transaction_cost)
                    break
        
        # Update portfolio total costs
        portfolio.total_value -= total_costs
        
        logger.info(f"Executed {len(trades)} rebalancing trades, total costs: ₹{total_costs:.2f}")
    
    def _calculate_next_rebalance_date(self, portfolio: HNIPortfolio) -> datetime:
        """Calculate next rebalance date"""
        
        frequency_map = {
            RebalanceFrequency.MONTHLY: timedelta(days=30),
            RebalanceFrequency.QUARTERLY: timedelta(days=90),
            RebalanceFrequency.SEMI_ANNUAL: timedelta(days=180),
            RebalanceFrequency.ANNUAL: timedelta(days=365)
        }
        
        if portfolio.rebalance_frequency == RebalanceFrequency.THRESHOLD:
            # Threshold-based rebalancing doesn't have fixed dates
            return None
        
        delta = frequency_map.get(portfolio.rebalance_frequency, timedelta(days=90))
        return datetime.now() + delta


class HNIPortfolioManager:
    """Main HNI portfolio management system"""
    
    def __init__(self):
        """Initialize HNI portfolio manager"""
        self.portfolios = {}
        self.constructor = PortfolioConstructor()
        self.optimizer = PortfolioOptimizer()
        self.rebalancer = PortfolioRebalancer()
        
        # Performance tracking
        self.benchmark_returns = {}
        self.risk_free_rate = 0.065
    
    async def create_hni_portfolio(
        self,
        client_id: str,
        portfolio_name: str,
        portfolio_type: PortfolioType,
        risk_profile: RiskProfile,
        initial_amount: float,
        custom_allocations: Optional[List[AssetAllocation]] = None
    ) -> str:
        """Create new HNI portfolio"""
        
        portfolio = await self.constructor.create_portfolio(
            client_id, portfolio_name, portfolio_type, risk_profile, 
            initial_amount, custom_allocations
        )
        
        self.portfolios[portfolio.portfolio_id] = portfolio
        
        logger.info(f"Created HNI portfolio {portfolio.portfolio_id} for ₹{initial_amount:,.0f}")
        return portfolio.portfolio_id
    
    async def optimize_portfolio_allocation(
        self,
        portfolio_id: str,
        optimization_method: str = 'mean_variance'
    ) -> bool:
        """Optimize portfolio allocation"""
        
        if portfolio_id not in self.portfolios:
            return False
        
        portfolio = self.portfolios[portfolio_id]
        
        # Get optimized weights
        optimized_weights = await self.optimizer.optimize_portfolio(
            portfolio, optimization_method
        )
        
        if optimized_weights:
            # Rebalance to optimized weights
            await self.rebalancer.rebalance_portfolio(portfolio, optimized_weights)
            logger.info(f"Optimized portfolio {portfolio_id} using {optimization_method}")
            return True
        
        return False
    
    async def rebalance_portfolio(self, portfolio_id: str) -> bool:
        """Rebalance portfolio to target allocations"""
        
        if portfolio_id not in self.portfolios:
            return False
        
        portfolio = self.portfolios[portfolio_id]
        trades = await self.rebalancer.rebalance_portfolio(portfolio)
        
        return len(trades) > 0
    
    async def update_portfolio_prices(self, portfolio_id: str, price_updates: Dict[str, float]):
        """Update portfolio with current market prices"""
        
        if portfolio_id not in self.portfolios:
            return
        
        portfolio = self.portfolios[portfolio_id]
        
        # Update holding prices and values
        for holding in portfolio.holdings:
            if holding.symbol in price_updates:
                old_price = holding.current_price
                new_price = price_updates[holding.symbol]
                
                holding.current_price = new_price
                holding.market_value = holding.quantity * new_price
                holding.unrealized_pnl = (new_price - holding.cost_basis) * holding.quantity
                
                # Update return metrics
                holding.total_return = holding.unrealized_pnl / (holding.cost_basis * holding.quantity)
        
        # Recalculate portfolio totals
        total_market_value = sum(h.market_value for h in portfolio.holdings) + portfolio.cash_balance
        portfolio.total_value = total_market_value
        
        # Update allocations
        await self.constructor._update_portfolio_metrics(portfolio)
        
        logger.debug(f"Updated prices for portfolio {portfolio_id}")
    
    async def get_portfolio_performance(self, portfolio_id: str) -> Optional[PortfolioPerformance]:
        """Get comprehensive portfolio performance"""
        
        if portfolio_id not in self.portfolios:
            return None
        
        portfolio = self.portfolios[portfolio_id]
        
        # Calculate performance metrics
        total_cost_basis = sum(h.cost_basis * h.quantity for h in portfolio.holdings)
        total_market_value = sum(h.market_value for h in portfolio.holdings)
        total_return = total_market_value - total_cost_basis
        total_return_pct = total_return / total_cost_basis if total_cost_basis > 0 else 0
        
        # Risk metrics (simplified)
        portfolio_beta = np.mean([h.beta * h.weight / 100 for h in portfolio.holdings])
        portfolio_volatility = 0.15  # Mock volatility
        sharpe_ratio = (total_return_pct - self.risk_free_rate) / portfolio_volatility
        
        # Asset allocation breakdown
        current_allocation = portfolio.current_allocation
        
        performance = PortfolioPerformance(
            portfolio_id=portfolio_id,
            as_of_date=datetime.now(),
            total_value=portfolio.total_value,
            total_cost_basis=total_cost_basis,
            cash_balance=portfolio.cash_balance,
            total_return=total_return,
            total_return_pct=total_return_pct,
            ytd_return=total_return_pct,  # Simplified
            mtd_return=total_return_pct / 12,  # Simplified
            portfolio_beta=portfolio_beta,
            portfolio_volatility=portfolio_volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sharpe_ratio * 1.2,  # Approximation
            max_drawdown=-0.05,  # Mock value
            var_95=-0.02,  # Mock value
            equity_allocation=current_allocation.get(AssetClass.EQUITY, 0.0),
            debt_allocation=current_allocation.get(AssetClass.DEBT, 0.0),
            cash_allocation=current_allocation.get(AssetClass.CASH, 0.0),
            other_allocation=sum(current_allocation.get(ac, 0.0) for ac in [AssetClass.COMMODITIES, AssetClass.DERIVATIVES]),
            benchmark_return=0.12,  # Mock benchmark
            alpha=total_return_pct - 0.12,
            tracking_error=0.03,  # Mock value
            information_ratio=(total_return_pct - 0.12) / 0.03
        )
        
        # Add to history
        portfolio.performance_history.append(performance)
        
        return performance
    
    async def get_portfolio_summary(self, portfolio_id: str) -> Optional[Dict]:
        """Get portfolio summary for reporting"""
        
        if portfolio_id not in self.portfolios:
            return None
        
        portfolio = self.portfolios[portfolio_id]
        performance = await self.get_portfolio_performance(portfolio_id)
        
        return {
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio.portfolio_name,
            'client_id': portfolio.client_id,
            'portfolio_type': portfolio.portfolio_type.value,
            'risk_profile': portfolio.risk_profile.value,
            'total_value': portfolio.total_value,
            'cash_balance': portfolio.cash_balance,
            'holdings_count': len(portfolio.holdings),
            'performance': performance,
            'needs_rebalancing': portfolio.needs_rebalancing,
            'last_rebalanced': portfolio.last_rebalanced,
            'next_rebalance': portfolio.next_rebalance
        }


# Example usage and testing
async def main():
    """Example usage of HNI portfolio management"""
    
    # Initialize portfolio manager
    manager = HNIPortfolioManager()
    
    print("=== HNI Portfolio Management System Demo ===")
    
    # Create HNI portfolio
    portfolio_id = await manager.create_hni_portfolio(
        client_id="HNI001",
        portfolio_name="Conservative Growth Portfolio",
        portfolio_type=PortfolioType.BALANCED,
        risk_profile=RiskProfile.MODERATE,
        initial_amount=10000000.0  # ₹1 crore
    )
    
    print(f"\n1. Created HNI Portfolio: {portfolio_id}")
    
    # Get initial portfolio summary
    summary = await manager.get_portfolio_summary(portfolio_id)
    print(f"   Initial Value: ₹{summary['total_value']:,.0f}")
    print(f"   Holdings: {summary['holdings_count']} securities")
    print(f"   Risk Profile: {summary['risk_profile']}")
    
    # Simulate price updates
    price_updates = {
        'RELIANCE': 2450.0,   # +1.24%
        'TCS': 3720.0,        # +1.09%
        'HDFC': 1590.0,       # +0.63%
        'INFY': 1435.0,       # +1.06%
        'ITC': 315.0          # +1.61%
    }
    
    print(f"\n2. Updating portfolio with market prices...")
    await manager.update_portfolio_prices(portfolio_id, price_updates)
    
    # Get updated performance
    performance = await manager.get_portfolio_performance(portfolio_id)
    print(f"   Updated Value: ₹{performance.total_value:,.0f}")
    print(f"   Total Return: ₹{performance.total_return:,.0f} ({performance.total_return_pct:.2%})")
    print(f"   Sharpe Ratio: {performance.sharpe_ratio:.2f}")
    
    # Check rebalancing needs
    portfolio = manager.portfolios[portfolio_id]
    if portfolio.needs_rebalancing:
        print(f"\n3. Portfolio needs rebalancing")
        await manager.rebalance_portfolio(portfolio_id)
        print(f"   Rebalancing completed")
    else:
        print(f"\n3. Portfolio is well balanced")
    
    # Optimize portfolio
    print(f"\n4. Optimizing portfolio allocation...")
    optimization_success = await manager.optimize_portfolio_allocation(
        portfolio_id, 'mean_variance'
    )
    
    if optimization_success:
        print(f"   Portfolio optimization completed")
        final_performance = await manager.get_portfolio_performance(portfolio_id)
        print(f"   Optimized Sharpe Ratio: {final_performance.sharpe_ratio:.2f}")
    
    print(f"\n=== HNI Portfolio Management Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())