"""
Advanced Risk Management Engine
Behavioral Finance, VaR Analysis, Portfolio Optimization, and Real-time Risk Monitoring
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from decimal import Decimal
from dataclasses import dataclass, asdict
from enum import Enum
import scipy.stats as stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

from app.core.config import settings
from app.core.enterprise_architecture import PerformanceConfig, ServiceTier
from app.models.user import User, Portfolio, Trade

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class BehavioralBias(Enum):
    OVERCONFIDENCE = "overconfidence"
    LOSS_AVERSION = "loss_aversion"
    ANCHORING = "anchoring"
    CONFIRMATION = "confirmation"
    HERDING = "herding"
    FOMO = "fomo"
    REVENGE_TRADING = "revenge_trading"
    RECENCY_BIAS = "recency_bias"


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for portfolio analysis"""
    portfolio_value: float
    daily_var_95: float
    daily_var_99: float
    expected_shortfall: float
    maximum_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float
    alpha: float
    volatility: float
    correlation_score: float
    concentration_risk: float
    liquidity_risk: float
    stress_test_results: Dict[str, float]
    risk_score: float
    risk_level: RiskLevel
    recommendations: List[str]


@dataclass
class BehavioralAnalysis:
    """Behavioral finance analysis of user trading patterns"""
    user_id: str
    analysis_period: int  # days
    detected_biases: List[BehavioralBias]
    overtrading_score: float
    revenge_trading_score: float
    fomo_score: float
    loss_aversion_score: float
    confidence_score: float
    discipline_score: float
    behavioral_risk_score: float
    improvement_suggestions: List[str]
    intervention_triggers: List[str]


class AdvancedRiskEngine:
    """
    Enterprise-grade risk management with behavioral finance integration
    Real-time portfolio monitoring and optimization
    """
    
    def __init__(self):
        # Performance configuration
        self.performance_config = PerformanceConfig(
            max_response_time_ms=200,
            max_concurrent_requests=10000,
            cache_ttl_seconds=60,
            rate_limit_per_minute=1000,
            circuit_breaker_threshold=3,
            service_tier=ServiceTier.HIGH
        )
        
        # Risk parameters
        self.risk_params = {
            'var_confidence_levels': [0.95, 0.99],
            'stress_scenarios': {
                'market_crash': -0.20,
                'sector_rotation': -0.15,
                'interest_rate_shock': -0.10,
                'currency_crisis': -0.25,
                'black_swan': -0.30
            },
            'correlation_threshold': 0.7,
            'concentration_limit': 0.15,  # 15% max in single stock
            'sector_limit': 0.30,  # 30% max in single sector
            'liquidity_threshold': 100000  # Minimum daily volume
        }
        
        # Behavioral thresholds
        self.behavioral_thresholds = {
            'overtrading': 20,  # trades per month
            'revenge_trading': 3,  # consecutive loss-revenge cycles
            'fomo_threshold': 0.15,  # buying after 15% run-up
            'loss_aversion': 2.5,  # loss aversion coefficient
            'max_drawdown_panic': 0.20  # 20% drawdown trigger
        }
        
        # Portfolio optimization parameters
        self.optimization_params = {
            'target_return': 0.15,  # 15% annual return target
            'max_volatility': 0.25,  # 25% max volatility
            'risk_free_rate': 0.06,  # 6% risk-free rate
            'transaction_cost': 0.001  # 0.1% transaction cost
        }
        
        # Cache for performance
        self.risk_cache = {}
        self.behavioral_cache = {}
    
    async def calculate_portfolio_risk(
        self,
        user_id: str,
        portfolio: Dict[str, Any],
        timeframe: int = 252  # Trading days
    ) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        
        try:
            logger.info(f"📊 Calculating portfolio risk for user {user_id}")
            
            # Get portfolio holdings and historical data
            holdings = portfolio.get('holdings', [])
            if not holdings:
                return self._create_empty_risk_metrics()
            
            # Fetch historical price data
            price_data = await self._fetch_portfolio_price_data(holdings, timeframe)
            
            # Calculate returns
            returns_data = await self._calculate_portfolio_returns(holdings, price_data)
            
            # Risk calculations
            risk_calculations = await asyncio.gather(
                self._calculate_var(returns_data),
                self._calculate_expected_shortfall(returns_data),
                self._calculate_maximum_drawdown(returns_data),
                self._calculate_sharpe_ratio(returns_data),
                self._calculate_beta_alpha(returns_data),
                self._calculate_concentration_risk(holdings),
                self._calculate_correlation_risk(holdings, price_data),
                self._calculate_liquidity_risk(holdings),
                self._run_stress_tests(holdings),
                return_exceptions=True
            )
            
            # Process results
            var_metrics = risk_calculations[0] if not isinstance(risk_calculations[0], Exception) else {}
            expected_shortfall = risk_calculations[1] if not isinstance(risk_calculations[1], Exception) else 0
            max_drawdown = risk_calculations[2] if not isinstance(risk_calculations[2], Exception) else 0
            sharpe_ratio = risk_calculations[3] if not isinstance(risk_calculations[3], Exception) else 0
            beta_alpha = risk_calculations[4] if not isinstance(risk_calculations[4], Exception) else {}
            concentration_risk = risk_calculations[5] if not isinstance(risk_calculations[5], Exception) else 0
            correlation_score = risk_calculations[6] if not isinstance(risk_calculations[6], Exception) else 0
            liquidity_risk = risk_calculations[7] if not isinstance(risk_calculations[7], Exception) else 0
            stress_results = risk_calculations[8] if not isinstance(risk_calculations[8], Exception) else {}
            
            # Calculate overall risk score
            risk_score = await self._calculate_overall_risk_score(
                var_metrics, expected_shortfall, max_drawdown, concentration_risk,
                correlation_score, liquidity_risk
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = await self._generate_risk_recommendations(
                risk_score, concentration_risk, correlation_score, stress_results
            )
            
            # Create risk metrics object
            portfolio_value = sum(holding.get('current_value', 0) for holding in holdings)
            volatility = np.std(returns_data) * np.sqrt(252) if len(returns_data) > 0 else 0
            
            risk_metrics = RiskMetrics(
                portfolio_value=portfolio_value,
                daily_var_95=var_metrics.get('var_95', 0),
                daily_var_99=var_metrics.get('var_99', 0),
                expected_shortfall=expected_shortfall,
                maximum_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=await self._calculate_sortino_ratio(returns_data),
                beta=beta_alpha.get('beta', 1.0),
                alpha=beta_alpha.get('alpha', 0.0),
                volatility=volatility,
                correlation_score=correlation_score,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk,
                stress_test_results=stress_results,
                risk_score=risk_score,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            # Cache results
            self.risk_cache[user_id] = {
                'metrics': risk_metrics,
                'timestamp': datetime.utcnow(),
                'ttl': 300  # 5 minutes
            }
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating portfolio risk: {str(e)}")
            return self._create_empty_risk_metrics()
    
    async def analyze_behavioral_patterns(
        self,
        user_id: str,
        trading_history: List[Dict[str, Any]],
        analysis_period: int = 90
    ) -> BehavioralAnalysis:
        """Analyze behavioral trading patterns and biases"""
        
        try:
            logger.info(f"🧠 Analyzing behavioral patterns for user {user_id}")
            
            # Filter recent trades
            cutoff_date = datetime.utcnow() - timedelta(days=analysis_period)
            recent_trades = [
                trade for trade in trading_history
                if datetime.fromisoformat(trade.get('timestamp', '2020-01-01')) >= cutoff_date
            ]
            
            if not recent_trades:
                return self._create_empty_behavioral_analysis(user_id, analysis_period)
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(recent_trades)
            
            # Behavioral analysis tasks
            behavioral_tasks = [
                self._detect_overtrading(df),
                self._detect_revenge_trading(df),
                self._detect_fomo_trading(df),
                self._analyze_loss_aversion(df),
                self._analyze_overconfidence(df),
                self._analyze_anchoring_bias(df),
                self._analyze_herding_behavior(df),
                self._calculate_trading_discipline(df)
            ]
            
            results = await asyncio.gather(*behavioral_tasks, return_exceptions=True)
            
            # Process behavioral analysis results
            overtrading_score = results[0] if not isinstance(results[0], Exception) else 0
            revenge_trading_score = results[1] if not isinstance(results[1], Exception) else 0
            fomo_score = results[2] if not isinstance(results[2], Exception) else 0
            loss_aversion_score = results[3] if not isinstance(results[3], Exception) else 0
            confidence_score = results[4] if not isinstance(results[4], Exception) else 0
            anchoring_score = results[5] if not isinstance(results[5], Exception) else 0
            herding_score = results[6] if not isinstance(results[6], Exception) else 0
            discipline_score = results[7] if not isinstance(results[7], Exception) else 0
            
            # Detect behavioral biases
            detected_biases = []
            if overtrading_score > 7: detected_biases.append(BehavioralBias.OVERCONFIDENCE)
            if revenge_trading_score > 5: detected_biases.append(BehavioralBias.REVENGE_TRADING)
            if fomo_score > 6: detected_biases.append(BehavioralBias.FOMO)
            if loss_aversion_score > 7: detected_biases.append(BehavioralBias.LOSS_AVERSION)
            if anchoring_score > 6: detected_biases.append(BehavioralBias.ANCHORING)
            if herding_score > 5: detected_biases.append(BehavioralBias.HERDING)
            
            # Calculate overall behavioral risk
            behavioral_risk_score = np.mean([
                overtrading_score, revenge_trading_score, fomo_score,
                loss_aversion_score, 10 - discipline_score  # Inverse discipline
            ])
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_behavioral_improvements(
                detected_biases, overtrading_score, revenge_trading_score,
                fomo_score, discipline_score
            )
            
            # Generate intervention triggers
            intervention_triggers = await self._generate_intervention_triggers(
                detected_biases, behavioral_risk_score
            )
            
            behavioral_analysis = BehavioralAnalysis(
                user_id=user_id,
                analysis_period=analysis_period,
                detected_biases=detected_biases,
                overtrading_score=overtrading_score,
                revenge_trading_score=revenge_trading_score,
                fomo_score=fomo_score,
                loss_aversion_score=loss_aversion_score,
                confidence_score=confidence_score,
                discipline_score=discipline_score,
                behavioral_risk_score=behavioral_risk_score,
                improvement_suggestions=improvement_suggestions,
                intervention_triggers=intervention_triggers
            )
            
            # Cache results
            self.behavioral_cache[user_id] = {
                'analysis': behavioral_analysis,
                'timestamp': datetime.utcnow(),
                'ttl': 3600  # 1 hour
            }
            
            return behavioral_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing behavioral patterns: {str(e)}")
            return self._create_empty_behavioral_analysis(user_id, analysis_period)
    
    async def optimize_portfolio(
        self,
        user_id: str,
        current_portfolio: Dict[str, Any],
        target_return: Optional[float] = None,
        max_volatility: Optional[float] = None
    ) -> Dict[str, Any]:
        """Optimize portfolio allocation using modern portfolio theory"""
        
        try:
            logger.info(f"🎯 Optimizing portfolio for user {user_id}")
            
            holdings = current_portfolio.get('holdings', [])
            if len(holdings) < 2:
                return {
                    'error': 'Portfolio optimization requires at least 2 holdings',
                    'recommendation': 'Diversify portfolio with additional stocks'
                }
            
            # Get historical data for optimization
            symbols = [holding['symbol'] for holding in holdings]
            price_data = await self._fetch_optimization_data(symbols, period=252)
            
            # Calculate expected returns and covariance matrix
            returns = price_data.pct_change().dropna()
            expected_returns = returns.mean() * 252  # Annualized
            cov_matrix = returns.cov() * 252  # Annualized
            
            # Set optimization parameters
            target_ret = target_return or self.optimization_params['target_return']
            max_vol = max_volatility or self.optimization_params['max_volatility']
            
            # Optimization constraints
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Weights sum to 1
                {'type': 'ineq', 'fun': lambda w: target_ret - np.dot(w, expected_returns)},  # Min return
                {'type': 'ineq', 'fun': lambda w: max_vol - np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))}  # Max vol
            ]
            
            # Bounds for weights (0% to 40% per stock)
            bounds = tuple((0, 0.4) for _ in range(len(symbols)))
            
            # Initial guess (equal weights)
            initial_weights = np.array([1/len(symbols)] * len(symbols))
            
            # Optimization objective (maximize Sharpe ratio)
            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.optimization_params['risk_free_rate']) / portfolio_vol
                return -sharpe_ratio  # Minimize negative Sharpe ratio
            
            # Run optimization
            optimization_result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if optimization_result.success:
                optimal_weights = optimization_result.x
                
                # Calculate optimized portfolio metrics
                opt_return = np.dot(optimal_weights, expected_returns)
                opt_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
                opt_sharpe = (opt_return - self.optimization_params['risk_free_rate']) / opt_volatility
                
                # Calculate current portfolio metrics for comparison
                current_weights = np.array([
                    holding['current_value'] / current_portfolio['total_value'] 
                    for holding in holdings
                ])
                current_return = np.dot(current_weights, expected_returns)
                current_volatility = np.sqrt(np.dot(current_weights.T, np.dot(cov_matrix, current_weights)))
                current_sharpe = (current_return - self.optimization_params['risk_free_rate']) / current_volatility
                
                # Generate rebalancing recommendations
                rebalancing_recommendations = []
                for i, symbol in enumerate(symbols):
                    current_weight = current_weights[i]
                    optimal_weight = optimal_weights[i]
                    weight_diff = optimal_weight - current_weight
                    
                    if abs(weight_diff) > 0.05:  # 5% threshold
                        action = "Increase" if weight_diff > 0 else "Decrease"
                        rebalancing_recommendations.append({
                            'symbol': symbol,
                            'action': action,
                            'current_weight': current_weight,
                            'optimal_weight': optimal_weight,
                            'weight_change': weight_diff,
                            'value_change': weight_diff * current_portfolio['total_value']
                        })
                
                return {
                    'success': True,
                    'optimization_successful': True,
                    'current_portfolio': {
                        'expected_return': current_return,
                        'volatility': current_volatility,
                        'sharpe_ratio': current_sharpe,
                        'weights': dict(zip(symbols, current_weights))
                    },
                    'optimized_portfolio': {
                        'expected_return': opt_return,
                        'volatility': opt_volatility,
                        'sharpe_ratio': opt_sharpe,
                        'weights': dict(zip(symbols, optimal_weights))
                    },
                    'improvements': {
                        'return_improvement': opt_return - current_return,
                        'volatility_change': opt_volatility - current_volatility,
                        'sharpe_improvement': opt_sharpe - current_sharpe
                    },
                    'rebalancing_recommendations': rebalancing_recommendations,
                    'implementation_cost': len(rebalancing_recommendations) * self.optimization_params['transaction_cost'],
                    'risk_reduction': max(0, current_volatility - opt_volatility)
                }
            
            else:
                return {
                    'success': False,
                    'error': 'Portfolio optimization failed to converge',
                    'recommendation': 'Current allocation may already be near-optimal'
                }
                
        except Exception as e:
            logger.error(f"❌ Error optimizing portfolio: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recommendation': 'Portfolio optimization temporarily unavailable'
            }
    
    async def real_time_risk_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Real-time risk monitoring with instant alerts"""
        
        try:
            # Get current portfolio and market data
            portfolio = await self._get_current_portfolio(user_id)
            market_data = await self._get_real_time_market_data()
            
            # Calculate real-time risk metrics
            current_risk = await self._calculate_real_time_risk(portfolio, market_data)
            
            # Check for risk threshold breaches
            risk_alerts = await self._check_risk_thresholds(user_id, current_risk)
            
            # Behavioral monitoring
            behavioral_alerts = await self._monitor_behavioral_risks(user_id)
            
            # Generate risk dashboard
            risk_dashboard = {
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'current_risk_score': current_risk.get('risk_score', 0),
                'risk_level': current_risk.get('risk_level', RiskLevel.MEDIUM),
                'portfolio_value': portfolio.get('total_value', 0),
                'daily_pnl': portfolio.get('day_pnl', 0),
                'portfolio_beta': current_risk.get('beta', 1.0),
                'active_alerts': risk_alerts + behavioral_alerts,
                'risk_breakdown': {
                    'market_risk': current_risk.get('market_risk', 0),
                    'concentration_risk': current_risk.get('concentration_risk', 0),
                    'liquidity_risk': current_risk.get('liquidity_risk', 0),
                    'behavioral_risk': current_risk.get('behavioral_risk', 0)
                },
                'recommendations': current_risk.get('recommendations', []),
                'next_review': (datetime.utcnow() + timedelta(hours=4)).isoformat()
            }
            
            return risk_dashboard
            
        except Exception as e:
            logger.error(f"❌ Error in real-time risk monitoring: {str(e)}")
            return {'error': str(e), 'user_id': user_id}
    
    # Helper methods for risk calculations
    async def _calculate_var(self, returns_data: np.ndarray) -> Dict[str, float]:
        """Calculate Value at Risk (VaR) at different confidence levels"""
        
        if len(returns_data) == 0:
            return {'var_95': 0, 'var_99': 0}
        
        var_95 = np.percentile(returns_data, 5)
        var_99 = np.percentile(returns_data, 1)
        
        return {'var_95': var_95, 'var_99': var_99}
    
    async def _calculate_expected_shortfall(self, returns_data: np.ndarray) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        
        if len(returns_data) == 0:
            return 0
        
        var_95 = np.percentile(returns_data, 5)
        tail_losses = returns_data[returns_data <= var_95]
        
        return np.mean(tail_losses) if len(tail_losses) > 0 else 0
    
    async def _detect_overtrading(self, trades_df: pd.DataFrame) -> float:
        """Detect overtrading patterns"""
        
        if len(trades_df) == 0:
            return 0
        
        # Calculate trade frequency
        trades_per_day = len(trades_df) / 30  # Assume 30-day period
        
        # Score based on frequency (0-10 scale)
        if trades_per_day > 5:
            return 10
        elif trades_per_day > 3:
            return 8
        elif trades_per_day > 2:
            return 6
        elif trades_per_day > 1:
            return 4
        else:
            return 2
    
    async def _detect_revenge_trading(self, trades_df: pd.DataFrame) -> float:
        """Detect revenge trading after losses"""
        
        if len(trades_df) < 3:
            return 0
        
        # Sort by timestamp
        trades_df = trades_df.sort_values('timestamp')
        
        # Calculate P&L for each trade
        trades_df['pnl'] = (trades_df['sell_price'] - trades_df['buy_price']) * trades_df['quantity']
        
        revenge_sequences = 0
        for i in range(1, len(trades_df) - 1):
            # Check if previous trade was a loss
            if trades_df.iloc[i-1]['pnl'] < 0:
                # Check if next trade is significantly larger
                prev_size = trades_df.iloc[i-1]['quantity'] * trades_df.iloc[i-1]['buy_price']
                next_size = trades_df.iloc[i]['quantity'] * trades_df.iloc[i]['buy_price']
                
                if next_size > prev_size * 1.5:  # 50% larger position
                    revenge_sequences += 1
        
        # Convert to 0-10 scale
        return min(revenge_sequences * 2, 10)
    
    # Additional helper methods would be implemented here...
    
    def _create_empty_risk_metrics(self) -> RiskMetrics:
        """Create empty risk metrics for error cases"""
        return RiskMetrics(
            portfolio_value=0,
            daily_var_95=0,
            daily_var_99=0,
            expected_shortfall=0,
            maximum_drawdown=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            beta=1.0,
            alpha=0,
            volatility=0,
            correlation_score=0,
            concentration_risk=0,
            liquidity_risk=0,
            stress_test_results={},
            risk_score=5,
            risk_level=RiskLevel.MEDIUM,
            recommendations=["Insufficient data for risk analysis"]
        )
    
    def _create_empty_behavioral_analysis(self, user_id: str, period: int) -> BehavioralAnalysis:
        """Create empty behavioral analysis for error cases"""
        return BehavioralAnalysis(
            user_id=user_id,
            analysis_period=period,
            detected_biases=[],
            overtrading_score=0,
            revenge_trading_score=0,
            fomo_score=0,
            loss_aversion_score=0,
            confidence_score=0,
            discipline_score=0,
            behavioral_risk_score=0,
            improvement_suggestions=["Insufficient trading history for analysis"],
            intervention_triggers=[]
        )