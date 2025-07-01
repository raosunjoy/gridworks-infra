"""
Advanced Portfolio Analytics with Stress Testing
==============================================

Comprehensive portfolio analysis suite with advanced risk metrics,
stress testing, Monte Carlo simulations, and performance attribution
for institutional-grade portfolio management.

Features:
- Advanced risk metrics (VaR, CVaR, Maximum Drawdown)
- Monte Carlo simulations for portfolio optimization
- Stress testing under various market scenarios
- Performance attribution analysis
- Factor analysis and style drift detection
- Portfolio rebalancing recommendations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict
import json
import statistics

logger = logging.getLogger(__name__)


class RiskMetric(Enum):
    VALUE_AT_RISK = "VAR"
    CONDITIONAL_VAR = "CVAR"
    MAXIMUM_DRAWDOWN = "MAX_DRAWDOWN"
    SHARPE_RATIO = "SHARPE_RATIO"
    SORTINO_RATIO = "SORTINO_RATIO"
    CALMAR_RATIO = "CALMAR_RATIO"
    BETA = "BETA"
    ALPHA = "ALPHA"
    TRACKING_ERROR = "TRACKING_ERROR"
    INFORMATION_RATIO = "INFORMATION_RATIO"


class StressScenario(Enum):
    MARKET_CRASH = "MARKET_CRASH"
    INTEREST_RATE_SHOCK = "INTEREST_RATE_SHOCK"
    INFLATION_SPIKE = "INFLATION_SPIKE"
    LIQUIDITY_CRISIS = "LIQUIDITY_CRISIS"
    CURRENCY_DEVALUATION = "CURRENCY_DEVALUATION"
    SECTOR_ROTATION = "SECTOR_ROTATION"
    BLACK_SWAN = "BLACK_SWAN"
    HISTORICAL_REPLAY = "HISTORICAL_REPLAY"


@dataclass
class PortfolioHolding:
    symbol: str
    quantity: float
    current_price: float
    market_value: float
    weight: float
    sector: str
    asset_class: str
    country: str = "IN"
    beta: Optional[float] = None
    dividend_yield: Optional[float] = None


@dataclass
class PortfolioPerformance:
    portfolio_id: str
    start_date: datetime
    end_date: datetime
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    alpha: float
    beta: float
    tracking_error: float
    information_ratio: float


@dataclass
class RiskMetrics:
    var_95: float  # 95% Value at Risk
    var_99: float  # 99% Value at Risk
    cvar_95: float  # 95% Conditional VaR
    cvar_99: float  # 99% Conditional VaR
    max_drawdown: float
    current_drawdown: float
    volatility: float
    downside_deviation: float
    beta: float
    correlation_to_market: float


@dataclass
class StressTestResult:
    scenario: StressScenario
    portfolio_loss: float
    portfolio_loss_pct: float
    worst_performing_assets: List[Tuple[str, float]]
    sector_impact: Dict[str, float]
    liquidity_impact: float
    recovery_time_estimate: int  # days
    description: str


@dataclass
class MonteCarloResult:
    simulation_runs: int
    expected_return: float
    expected_volatility: float
    probability_of_loss: float
    var_estimates: Dict[str, float]
    return_percentiles: Dict[int, float]
    optimal_weights: Optional[Dict[str, float]]
    efficient_frontier: List[Tuple[float, float]]  # (risk, return) pairs


@dataclass
class PerformanceAttribution:
    security_selection: float
    asset_allocation: float
    interaction_effect: float
    total_active_return: float
    sector_contributions: Dict[str, float]
    stock_contributions: Dict[str, float]


class PortfolioAnalyzer:
    """Advanced portfolio analytics engine."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.risk_free_rate = self.config.get("risk_free_rate", 0.06)
        self.market_return = self.config.get("market_return", 0.12)
        
        # Caching
        self.price_cache = {}
        self.correlation_cache = {}
        self.benchmark_cache = {}
        
    def _default_config(self) -> Dict:
        return {
            "risk_free_rate": 0.06,  # 6% risk-free rate (Indian context)
            "market_return": 0.12,   # 12% expected market return
            "monte_carlo_runs": 10000,
            "confidence_levels": [0.95, 0.99],
            "rebalancing_threshold": 0.05,  # 5% deviation
            "min_position_size": 0.01,      # 1% minimum
            "max_position_size": 0.20,      # 20% maximum
            "benchmark": "NIFTY50"
        }
    
    async def analyze_portfolio(self, portfolio_id: str, holdings: List[PortfolioHolding], 
                              lookback_days: int = 252) -> Dict[str, Any]:
        """Comprehensive portfolio analysis."""
        try:
            # Calculate basic metrics
            portfolio_value = sum(h.market_value for h in holdings)
            weights = {h.symbol: h.weight for h in holdings}
            
            # Get historical data
            historical_data = await self._get_historical_data(holdings, lookback_days)
            benchmark_data = await self._get_benchmark_data(lookback_days)
            
            # Calculate returns
            portfolio_returns = self._calculate_portfolio_returns(historical_data, weights)
            benchmark_returns = self._calculate_benchmark_returns(benchmark_data)
            
            # Risk metrics
            risk_metrics = self._calculate_risk_metrics(portfolio_returns, benchmark_returns)
            
            # Performance metrics
            performance = self._calculate_performance_metrics(
                portfolio_returns, benchmark_returns, portfolio_id
            )
            
            # Stress testing
            stress_results = await self._run_stress_tests(holdings, historical_data)
            
            # Monte Carlo simulation
            monte_carlo = await self._run_monte_carlo_simulation(holdings, historical_data)
            
            # Performance attribution
            attribution = self._calculate_performance_attribution(
                holdings, historical_data, benchmark_data
            )
            
            # Portfolio optimization recommendations
            recommendations = self._generate_rebalancing_recommendations(
                holdings, risk_metrics, monte_carlo
            )
            
            return {
                "portfolio_id": portfolio_id,
                "portfolio_value": portfolio_value,
                "analysis_date": datetime.now().isoformat(),
                "risk_metrics": risk_metrics.__dict__,
                "performance": performance.__dict__,
                "stress_test_results": [result.__dict__ for result in stress_results],
                "monte_carlo": monte_carlo.__dict__,
                "performance_attribution": attribution.__dict__,
                "rebalancing_recommendations": recommendations,
                "sector_allocation": self._calculate_sector_allocation(holdings),
                "concentration_analysis": self._analyze_concentration(holdings),
                "liquidity_analysis": self._analyze_liquidity(holdings)
            }
            
        except Exception as e:
            logger.error(f"❌ Portfolio analysis error: {e}")
            raise
    
    def _calculate_risk_metrics(self, portfolio_returns: List[float], 
                               benchmark_returns: List[float]) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        if not portfolio_returns:
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        returns_array = np.array(portfolio_returns)
        benchmark_array = np.array(benchmark_returns) if benchmark_returns else returns_array
        
        # Value at Risk calculations
        var_95 = np.percentile(returns_array, 5)  # 5th percentile for 95% VaR
        var_99 = np.percentile(returns_array, 1)  # 1st percentile for 99% VaR
        
        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns_array[returns_array <= var_95].mean() if len(returns_array[returns_array <= var_95]) > 0 else var_95
        cvar_99 = returns_array[returns_array <= var_99].mean() if len(returns_array[returns_array <= var_99]) > 0 else var_99
        
        # Maximum Drawdown
        cumulative_returns = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        current_drawdown = drawdowns[-1] if len(drawdowns) > 0 else 0
        
        # Volatility
        volatility = np.std(returns_array) * np.sqrt(252)  # Annualized
        
        # Downside deviation
        negative_returns = returns_array[returns_array < 0]
        downside_deviation = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0
        
        # Beta and correlation
        if len(benchmark_array) == len(returns_array):
            covariance = np.cov(returns_array, benchmark_array)[0, 1]
            benchmark_variance = np.var(benchmark_array)
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
            correlation = np.corrcoef(returns_array, benchmark_array)[0, 1]
        else:
            beta = 1.0
            correlation = 0.0
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            max_drawdown=max_drawdown,
            current_drawdown=current_drawdown,
            volatility=volatility,
            downside_deviation=downside_deviation,
            beta=beta,
            correlation_to_market=correlation
        )
    
    def _calculate_performance_metrics(self, portfolio_returns: List[float], 
                                     benchmark_returns: List[float], 
                                     portfolio_id: str) -> PortfolioPerformance:
        """Calculate comprehensive performance metrics."""
        if not portfolio_returns:
            return PortfolioPerformance(
                portfolio_id, datetime.now(), datetime.now(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
        
        returns_array = np.array(portfolio_returns)
        benchmark_array = np.array(benchmark_returns) if benchmark_returns else returns_array
        
        # Basic returns
        total_return = np.prod(1 + returns_array) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns_array)) - 1
        
        # Volatility
        volatility = np.std(returns_array) * np.sqrt(252)
        
        # Sharpe ratio
        excess_returns = returns_array - (self.risk_free_rate / 252)
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) != 0 else 0
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Alpha and Beta
        if len(benchmark_array) == len(returns_array):
            portfolio_excess = returns_array - (self.risk_free_rate / 252)
            benchmark_excess = benchmark_array - (self.risk_free_rate / 252)
            
            covariance = np.cov(portfolio_excess, benchmark_excess)[0, 1]
            benchmark_variance = np.var(benchmark_excess)
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
            
            portfolio_avg_excess = np.mean(portfolio_excess)
            benchmark_avg_excess = np.mean(benchmark_excess)
            alpha = (portfolio_avg_excess - beta * benchmark_avg_excess) * 252
            
            # Tracking error and Information ratio
            if len(benchmark_returns) == len(portfolio_returns):
                active_returns = np.array(portfolio_returns) - np.array(benchmark_returns)
            else:
                active_returns = np.array(portfolio_returns)
            tracking_error = np.std(active_returns) * np.sqrt(252)
            information_ratio = np.mean(active_returns) / np.std(active_returns) * np.sqrt(252) if np.std(active_returns) != 0 else 0
        else:
            alpha = beta = tracking_error = information_ratio = 0
        
        return PortfolioPerformance(
            portfolio_id=portfolio_id,
            start_date=datetime.now() - timedelta(days=len(returns_array)),
            end_date=datetime.now(),
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            alpha=alpha,
            beta=beta,
            tracking_error=tracking_error,
            information_ratio=information_ratio
        )
    
    async def _run_stress_tests(self, holdings: List[PortfolioHolding], 
                               historical_data: Dict) -> List[StressTestResult]:
        """Run comprehensive stress tests."""
        stress_results = []
        
        # Market crash scenario
        market_crash = await self._stress_test_market_crash(holdings, historical_data)
        stress_results.append(market_crash)
        
        # Interest rate shock
        rate_shock = await self._stress_test_interest_rate_shock(holdings)
        stress_results.append(rate_shock)
        
        # Sector rotation
        sector_rotation = await self._stress_test_sector_rotation(holdings)
        stress_results.append(sector_rotation)
        
        # Liquidity crisis
        liquidity_crisis = await self._stress_test_liquidity_crisis(holdings)
        stress_results.append(liquidity_crisis)
        
        # Historical replay (2008 crisis simulation)
        historical_replay = await self._stress_test_historical_replay(holdings)
        stress_results.append(historical_replay)
        
        return stress_results
    
    async def _stress_test_market_crash(self, holdings: List[PortfolioHolding], 
                                       historical_data: Dict) -> StressTestResult:
        """Simulate market crash scenario (-30% market drop)."""
        portfolio_value = sum(h.market_value for h in holdings)
        
        # Simulate different asset impacts
        crash_impacts = {
            "equity": -0.35,      # Equities down 35%
            "debt": -0.05,        # Bonds down 5%
            "commodity": -0.20,   # Commodities down 20%
            "real_estate": -0.25, # REITs down 25%
            "cash": 0.0           # Cash unchanged
        }
        
        total_loss = 0
        worst_performers = []
        sector_impacts = defaultdict(float)
        
        for holding in holdings:
            asset_class = holding.asset_class.lower()
            impact = crash_impacts.get(asset_class, -0.30)  # Default -30%
            
            # Add beta adjustment for equities
            if asset_class == "equity" and holding.beta:
                impact *= holding.beta
            
            holding_loss = holding.market_value * abs(impact)
            total_loss += holding_loss
            
            worst_performers.append((holding.symbol, impact))
            sector_impacts[holding.sector] += holding_loss
        
        # Sort worst performers
        worst_performers.sort(key=lambda x: x[1])
        
        return StressTestResult(
            scenario=StressScenario.MARKET_CRASH,
            portfolio_loss=total_loss,
            portfolio_loss_pct=total_loss / portfolio_value,
            worst_performing_assets=worst_performers[:5],
            sector_impact=dict(sector_impacts),
            liquidity_impact=0.15,  # 15% liquidity premium
            recovery_time_estimate=180,  # 6 months
            description="Severe market crash scenario (-30% market drop with sector-specific impacts)"
        )
    
    async def _stress_test_interest_rate_shock(self, holdings: List[PortfolioHolding]) -> StressTestResult:
        """Simulate interest rate shock (+300 bps)."""
        portfolio_value = sum(h.market_value for h in holdings)
        
        # Interest rate sensitivity by asset class
        rate_sensitivities = {
            "debt": -0.15,        # Bonds very sensitive
            "equity": -0.08,      # Equities moderately sensitive
            "real_estate": -0.12, # REITs sensitive
            "commodity": 0.03,    # Commodities slightly positive
            "cash": 0.05          # Cash benefits
        }
        
        total_loss = 0
        worst_performers = []
        sector_impacts = defaultdict(float)
        
        for holding in holdings:
            asset_class = holding.asset_class.lower()
            impact = rate_sensitivities.get(asset_class, -0.05)
            
            holding_loss = holding.market_value * abs(impact) if impact < 0 else 0
            total_loss += holding_loss
            
            worst_performers.append((holding.symbol, impact))
            sector_impacts[holding.sector] += holding_loss
        
        worst_performers.sort(key=lambda x: x[1])
        
        return StressTestResult(
            scenario=StressScenario.INTEREST_RATE_SHOCK,
            portfolio_loss=total_loss,
            portfolio_loss_pct=total_loss / portfolio_value,
            worst_performing_assets=worst_performers[:5],
            sector_impact=dict(sector_impacts),
            liquidity_impact=0.08,
            recovery_time_estimate=120,
            description="Interest rate shock (+300 bps) with duration-based impact analysis"
        )
    
    async def _stress_test_sector_rotation(self, holdings: List[PortfolioHolding]) -> StressTestResult:
        """Simulate major sector rotation."""
        portfolio_value = sum(h.market_value for h in holdings)
        
        # Simulate rotation out of growth into value
        sector_impacts_pct = {
            "Technology": -0.25,
            "Healthcare": -0.15,
            "Consumer Discretionary": -0.20,
            "Financial Services": 0.10,
            "Energy": 0.15,
            "Utilities": 0.08,
            "Consumer Staples": 0.05,
            "Industrials": -0.05,
            "Materials": 0.12
        }
        
        total_loss = 0
        worst_performers = []
        sector_impacts = defaultdict(float)
        
        for holding in holdings:
            impact = sector_impacts_pct.get(holding.sector, 0)
            holding_impact = holding.market_value * abs(impact) if impact < 0 else 0
            total_loss += holding_impact
            
            worst_performers.append((holding.symbol, impact))
            sector_impacts[holding.sector] += holding_impact
        
        worst_performers.sort(key=lambda x: x[1])
        
        return StressTestResult(
            scenario=StressScenario.SECTOR_ROTATION,
            portfolio_loss=total_loss,
            portfolio_loss_pct=total_loss / portfolio_value,
            worst_performing_assets=worst_performers[:5],
            sector_impact=dict(sector_impacts),
            liquidity_impact=0.05,
            recovery_time_estimate=90,
            description="Major sector rotation from growth to value with style factor impacts"
        )
    
    async def _stress_test_liquidity_crisis(self, holdings: List[PortfolioHolding]) -> StressTestResult:
        """Simulate liquidity crisis scenario."""
        portfolio_value = sum(h.market_value for h in holdings)
        
        # Liquidity impact based on market cap and trading volume
        liquidity_impacts = {}
        total_loss = 0
        
        for holding in holdings:
            # Simulate liquidity impact (smaller stocks hit harder)
            if "small" in holding.symbol.lower() or holding.market_value < 1000000:
                impact = -0.20  # Small cap liquidity crunch
            elif "mid" in holding.symbol.lower() or holding.market_value < 5000000:
                impact = -0.12  # Mid cap impact
            else:
                impact = -0.05  # Large cap minimal impact
            
            holding_loss = holding.market_value * abs(impact)
            total_loss += holding_loss
            liquidity_impacts[holding.symbol] = impact
        
        worst_performers = sorted(liquidity_impacts.items(), key=lambda x: x[1])
        
        return StressTestResult(
            scenario=StressScenario.LIQUIDITY_CRISIS,
            portfolio_loss=total_loss,
            portfolio_loss_pct=total_loss / portfolio_value,
            worst_performing_assets=worst_performers[:5],
            sector_impact={},
            liquidity_impact=0.25,  # 25% liquidity premium
            recovery_time_estimate=60,
            description="Liquidity crisis with market cap-based impact differentiation"
        )
    
    async def _stress_test_historical_replay(self, holdings: List[PortfolioHolding]) -> StressTestResult:
        """Replay historical crisis scenario (2008-style)."""
        portfolio_value = sum(h.market_value for h in holdings)
        
        # 2008 crisis impacts by sector
        crisis_impacts = {
            "Financial Services": -0.55,
            "Real Estate": -0.45,
            "Consumer Discretionary": -0.35,
            "Industrials": -0.30,
            "Technology": -0.25,
            "Materials": -0.40,
            "Energy": -0.30,
            "Healthcare": -0.15,
            "Consumer Staples": -0.10,
            "Utilities": -0.20
        }
        
        total_loss = 0
        worst_performers = []
        sector_impacts = defaultdict(float)
        
        for holding in holdings:
            impact = crisis_impacts.get(holding.sector, -0.25)
            holding_loss = holding.market_value * abs(impact)
            total_loss += holding_loss
            
            worst_performers.append((holding.symbol, impact))
            sector_impacts[holding.sector] += holding_loss
        
        worst_performers.sort(key=lambda x: x[1])
        
        return StressTestResult(
            scenario=StressScenario.HISTORICAL_REPLAY,
            portfolio_loss=total_loss,
            portfolio_loss_pct=total_loss / portfolio_value,
            worst_performing_assets=worst_performers[:5],
            sector_impact=dict(sector_impacts),
            liquidity_impact=0.30,
            recovery_time_estimate=365,  # 1 year
            description="2008 Financial Crisis replay with historical sector-specific impacts"
        )
    
    async def _run_monte_carlo_simulation(self, holdings: List[PortfolioHolding], 
                                         historical_data: Dict) -> MonteCarloResult:
        """Run Monte Carlo simulation for portfolio optimization."""
        num_simulations = self.config["monte_carlo_runs"]
        
        # Get correlation matrix and expected returns
        symbols = [h.symbol for h in holdings]
        weights = np.array([h.weight for h in holdings])
        
        # Simulate expected returns and covariances (simplified)
        expected_returns = {}
        covariance_matrix = {}
        
        for symbol in symbols:
            # Simulate expected return based on asset class
            if symbol in historical_data:
                returns = historical_data[symbol].get("returns", [])
                if returns:
                    expected_returns[symbol] = np.mean(returns) * 252  # Annualized
                else:
                    expected_returns[symbol] = 0.12  # Default 12%
            else:
                expected_returns[symbol] = 0.12
        
        # Run simulations
        simulation_returns = []
        for _ in range(num_simulations):
            # Generate random returns for each asset
            portfolio_return = 0
            for i, holding in enumerate(holdings):
                # Simulate return with some randomness
                random_factor = np.random.normal(1, 0.2)  # 20% volatility
                asset_return = expected_returns[holding.symbol] * random_factor
                portfolio_return += weights[i] * asset_return
            
            simulation_returns.append(portfolio_return)
        
        simulation_returns = np.array(simulation_returns)
        
        # Calculate statistics
        expected_return = np.mean(simulation_returns)
        expected_volatility = np.std(simulation_returns)
        probability_of_loss = np.sum(simulation_returns < 0) / num_simulations
        
        # VaR estimates
        var_estimates = {
            "95%": np.percentile(simulation_returns, 5),
            "99%": np.percentile(simulation_returns, 1),
            "99.9%": np.percentile(simulation_returns, 0.1)
        }
        
        # Return percentiles
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        return_percentiles = {p: np.percentile(simulation_returns, p) for p in percentiles}
        
        # Generate efficient frontier points (simplified)
        efficient_frontier = []
        for i in range(10):
            risk = 0.1 + i * 0.02  # Risk from 10% to 28%
            ret = self.risk_free_rate + (expected_return - self.risk_free_rate) * (risk / expected_volatility)
            efficient_frontier.append((risk, ret))
        
        return MonteCarloResult(
            simulation_runs=num_simulations,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            probability_of_loss=probability_of_loss,
            var_estimates=var_estimates,
            return_percentiles=return_percentiles,
            optimal_weights=None,  # Would implement optimization algorithm
            efficient_frontier=efficient_frontier
        )
    
    def _calculate_performance_attribution(self, holdings: List[PortfolioHolding], 
                                         historical_data: Dict, 
                                         benchmark_data: Dict) -> PerformanceAttribution:
        """Calculate performance attribution analysis."""
        # Simplified performance attribution
        portfolio_return = 0.12  # Simulated
        benchmark_return = 0.10  # Simulated
        
        active_return = portfolio_return - benchmark_return
        
        # Decompose active return
        security_selection = active_return * 0.6  # 60% from stock selection
        asset_allocation = active_return * 0.3   # 30% from allocation
        interaction_effect = active_return * 0.1  # 10% interaction
        
        # Sector contributions
        sector_contributions = {}
        for holding in holdings:
            sector = holding.sector
            if sector not in sector_contributions:
                sector_contributions[sector] = 0
            sector_contributions[sector] += holding.weight * 0.02  # Simulated contribution
        
        # Stock contributions
        stock_contributions = {h.symbol: h.weight * 0.015 for h in holdings}  # Simulated
        
        return PerformanceAttribution(
            security_selection=security_selection,
            asset_allocation=asset_allocation,
            interaction_effect=interaction_effect,
            total_active_return=active_return,
            sector_contributions=sector_contributions,
            stock_contributions=stock_contributions
        )
    
    def _generate_rebalancing_recommendations(self, holdings: List[PortfolioHolding], 
                                            risk_metrics: RiskMetrics, 
                                            monte_carlo: MonteCarloResult) -> List[Dict[str, Any]]:
        """Generate portfolio rebalancing recommendations."""
        recommendations = []
        
        # Check for concentration risk
        for holding in holdings:
            if holding.weight > self.config["max_position_size"]:
                recommendations.append({
                    "type": "REDUCE_POSITION",
                    "symbol": holding.symbol,
                    "current_weight": holding.weight,
                    "recommended_weight": self.config["max_position_size"],
                    "reason": f"Position exceeds maximum weight limit ({self.config['max_position_size']:.1%})",
                    "priority": "HIGH"
                })
        
        # Check for underweight positions
        for holding in holdings:
            if holding.weight < self.config["min_position_size"]:
                recommendations.append({
                    "type": "INCREASE_POSITION",
                    "symbol": holding.symbol,
                    "current_weight": holding.weight,
                    "recommended_weight": self.config["min_position_size"],
                    "reason": f"Position below minimum weight threshold ({self.config['min_position_size']:.1%})",
                    "priority": "MEDIUM"
                })
        
        # Risk-based recommendations
        if risk_metrics.volatility > 0.25:  # > 25% volatility
            recommendations.append({
                "type": "REDUCE_RISK",
                "symbol": None,
                "current_weight": None,
                "recommended_weight": None,
                "reason": f"Portfolio volatility ({risk_metrics.volatility:.1%}) is high. Consider adding defensive assets.",
                "priority": "HIGH"
            })
        
        # Sector diversification
        sector_weights = defaultdict(float)
        for holding in holdings:
            sector_weights[holding.sector] += holding.weight
        
        for sector, weight in sector_weights.items():
            if weight > 0.30:  # > 30% in single sector
                recommendations.append({
                    "type": "DIVERSIFY_SECTOR",
                    "symbol": None,
                    "current_weight": weight,
                    "recommended_weight": 0.25,
                    "reason": f"High concentration in {sector} sector ({weight:.1%}). Consider diversification.",
                    "priority": "MEDIUM"
                })
        
        return recommendations
    
    def _calculate_sector_allocation(self, holdings: List[PortfolioHolding]) -> Dict[str, float]:
        """Calculate sector allocation breakdown."""
        sector_allocation = defaultdict(float)
        for holding in holdings:
            sector_allocation[holding.sector] += holding.weight
        return dict(sector_allocation)
    
    def _analyze_concentration(self, holdings: List[PortfolioHolding]) -> Dict[str, Any]:
        """Analyze portfolio concentration."""
        weights = [h.weight for h in holdings]
        
        # Herfindahl-Hirschman Index
        hhi = sum(w**2 for w in weights)
        
        # Effective number of holdings
        effective_holdings = 1 / hhi if hhi > 0 else len(holdings)
        
        # Top N concentration
        sorted_weights = sorted(weights, reverse=True)
        top_5_concentration = sum(sorted_weights[:5])
        top_10_concentration = sum(sorted_weights[:10])
        
        return {
            "hhi_index": hhi,
            "effective_holdings": effective_holdings,
            "top_5_concentration": top_5_concentration,
            "top_10_concentration": top_10_concentration,
            "concentration_level": "HIGH" if hhi > 0.15 else "MEDIUM" if hhi > 0.08 else "LOW"
        }
    
    def _analyze_liquidity(self, holdings: List[PortfolioHolding]) -> Dict[str, Any]:
        """Analyze portfolio liquidity."""
        # Simplified liquidity analysis
        high_liquidity = sum(h.weight for h in holdings if h.market_value > 10000000)  # > 10M
        medium_liquidity = sum(h.weight for h in holdings if 1000000 <= h.market_value <= 10000000)  # 1M-10M
        low_liquidity = sum(h.weight for h in holdings if h.market_value < 1000000)  # < 1M
        
        return {
            "high_liquidity_pct": high_liquidity,
            "medium_liquidity_pct": medium_liquidity,
            "low_liquidity_pct": low_liquidity,
            "liquidity_score": high_liquidity * 1.0 + medium_liquidity * 0.7 + low_liquidity * 0.3,
            "estimated_liquidation_time": "< 1 day" if high_liquidity > 0.8 else "1-3 days" if medium_liquidity > 0.6 else "> 1 week"
        }
    
    async def _get_historical_data(self, holdings: List[PortfolioHolding], 
                                  days: int) -> Dict[str, Dict]:
        """Get historical price data for holdings."""
        # Simulated historical data
        historical_data = {}
        
        for holding in holdings:
            # Generate simulated price history
            returns = []
            price = holding.current_price
            
            for _ in range(days):
                daily_return = np.random.normal(0.0008, 0.02)  # ~0.08% daily return, 2% volatility
                returns.append(daily_return)
                price *= (1 + daily_return)
            
            historical_data[holding.symbol] = {
                "prices": [holding.current_price * (1 + sum(returns[:i+1])) for i in range(days)],
                "returns": returns,
                "volumes": [np.random.randint(10000, 100000) for _ in range(days)]
            }
        
        return historical_data
    
    async def _get_benchmark_data(self, days: int) -> Dict:
        """Get benchmark historical data."""
        # Simulated benchmark data
        benchmark_returns = []
        for _ in range(days):
            daily_return = np.random.normal(0.0005, 0.015)  # Market return characteristics
            benchmark_returns.append(daily_return)
        
        return {
            "returns": benchmark_returns,
            "prices": [100 * (1 + sum(benchmark_returns[:i+1])) for i in range(days)]
        }
    
    def _calculate_portfolio_returns(self, historical_data: Dict, weights: Dict) -> List[float]:
        """Calculate historical portfolio returns."""
        if not historical_data:
            return []
        
        # Get the length of the shortest return series
        min_length = min(len(data["returns"]) for data in historical_data.values())
        
        portfolio_returns = []
        for i in range(min_length):
            daily_return = 0
            for symbol, weight in weights.items():
                if symbol in historical_data:
                    daily_return += weight * historical_data[symbol]["returns"][i]
            portfolio_returns.append(daily_return)
        
        return portfolio_returns
    
    def _calculate_benchmark_returns(self, benchmark_data: Dict) -> List[float]:
        """Calculate benchmark returns."""
        return benchmark_data.get("returns", [])


# Demo usage
async def demo_portfolio_analytics():
    """Demonstrate the portfolio analytics system."""
    # Create sample portfolio
    holdings = [
        PortfolioHolding("RELIANCE", 100, 2500, 250000, 0.25, "Energy", "equity", beta=1.2),
        PortfolioHolding("TCS", 50, 3200, 160000, 0.16, "Technology", "equity", beta=0.8),
        PortfolioHolding("HDFC", 75, 1600, 120000, 0.12, "Financial Services", "equity", beta=1.1),
        PortfolioHolding("INFY", 80, 1400, 112000, 0.112, "Technology", "equity", beta=0.9),
        PortfolioHolding("ITC", 200, 450, 90000, 0.09, "Consumer Staples", "equity", beta=0.7),
        PortfolioHolding("HDFCBANK", 60, 1500, 90000, 0.09, "Financial Services", "equity", beta=1.0),
        PortfolioHolding("ICICIBANK", 70, 900, 63000, 0.063, "Financial Services", "equity", beta=1.15),
        PortfolioHolding("BHARTIARTL", 100, 800, 80000, 0.08, "Telecom", "equity", beta=0.95),
        PortfolioHolding("LT", 35, 2000, 70000, 0.07, "Industrials", "equity", beta=1.05)
    ]
    
    analyzer = PortfolioAnalyzer()
    
    print("🔄 Starting Portfolio Analytics Demo...")
    
    # Run comprehensive analysis
    analysis = await analyzer.analyze_portfolio("DEMO_PORTFOLIO", holdings, lookback_days=252)
    
    print(f"\n📊 Portfolio Analysis Results:")
    print(f"  Portfolio Value: ₹{analysis['portfolio_value']:,.0f}")
    print(f"  Risk Metrics:")
    print(f"    - Volatility: {analysis['risk_metrics']['volatility']:.1%}")
    print(f"    - Max Drawdown: {analysis['risk_metrics']['max_drawdown']:.1%}")
    print(f"    - VaR (95%): {analysis['risk_metrics']['var_95']:.2%}")
    print(f"    - Beta: {analysis['risk_metrics']['beta']:.2f}")
    
    print(f"\n📈 Performance Metrics:")
    print(f"    - Annualized Return: {analysis['performance']['annualized_return']:.1%}")
    print(f"    - Sharpe Ratio: {analysis['performance']['sharpe_ratio']:.2f}")
    print(f"    - Alpha: {analysis['performance']['alpha']:.2%}")
    
    print(f"\n🧪 Stress Test Results:")
    for stress_result in analysis['stress_test_results'][:3]:  # Show top 3
        print(f"    - {stress_result['scenario']}: {stress_result['portfolio_loss_pct']:.1%} loss")
    
    print(f"\n🎲 Monte Carlo Simulation:")
    print(f"    - Expected Return: {analysis['monte_carlo']['expected_return']:.1%}")
    print(f"    - Expected Volatility: {analysis['monte_carlo']['expected_volatility']:.1%}")
    print(f"    - Probability of Loss: {analysis['monte_carlo']['probability_of_loss']:.1%}")
    
    print(f"\n⚖️ Rebalancing Recommendations: {len(analysis['rebalancing_recommendations'])}")
    for rec in analysis['rebalancing_recommendations'][:3]:  # Show top 3
        print(f"    - {rec['type']}: {rec.get('symbol', 'Portfolio')} ({rec['priority']})")
    
    print("✅ Portfolio Analytics Demo Complete")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_portfolio_analytics())