"""
AI-Powered Portfolio Manager - Subscription-based Investment Advisory
Revolutionary AI-driven portfolio management for passive investors
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import json
import numpy as np
from scipy.optimize import minimize
import pandas as pd

from app.core.config import settings
from app.core.enterprise_architecture import PerformanceConfig, ServiceTier
from app.ai.market_intelligence import MarketIntelligenceEngine
from app.trading.order_manager import OrderManager
from app.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)


class SubscriptionTier(Enum):
    BASIC = "basic"          # ₹99/month - Basic portfolio management
    PREMIUM = "premium"      # ₹299/month - Advanced strategies + research
    ELITE = "elite"          # ₹999/month - Personalized advisor + priority


class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"    # 15-25% equity, 75-85% debt
    MODERATE = "moderate"           # 40-60% equity, 40-60% debt
    AGGRESSIVE = "aggressive"       # 70-90% equity, 10-30% debt
    DYNAMIC = "dynamic"            # AI-managed allocation based on market


class RebalancingFrequency(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    TRIGGER_BASED = "trigger_based"  # Rebalance when allocation drifts >5%


class InvestmentObjective(Enum):
    WEALTH_CREATION = "wealth_creation"
    INCOME_GENERATION = "income_generation"
    CAPITAL_PRESERVATION = "capital_preservation"
    TAX_SAVING = "tax_saving"
    RETIREMENT_PLANNING = "retirement_planning"


@dataclass
class AIPortfolioStrategy:
    """AI-generated portfolio strategy definition"""
    strategy_id: str
    user_id: str
    strategy_name: str
    risk_tolerance: RiskTolerance
    investment_objective: InvestmentObjective
    target_allocation: Dict[str, float]  # asset_class -> percentage
    recommended_instruments: List[Dict[str, Any]]
    expected_return: float  # Annual expected return %
    volatility: float      # Expected annual volatility %
    sharpe_ratio: float    # Risk-adjusted return metric
    max_drawdown: float    # Maximum expected loss %
    rebalancing_frequency: RebalancingFrequency
    ai_confidence_score: float  # 0-1 confidence in strategy
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class PortfolioSubscription:
    """User's AI portfolio management subscription"""
    subscription_id: str
    user_id: str
    tier: SubscriptionTier
    monthly_fee: Decimal
    strategy_id: str
    auto_invest_amount: Decimal  # Monthly SIP amount
    is_active: bool = True
    next_billing_date: datetime = None
    created_at: datetime = None
    performance_since_inception: float = 0.0
    total_invested: Decimal = Decimal('0')
    current_value: Decimal = Decimal('0')
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.next_billing_date is None:
            self.next_billing_date = self.created_at + timedelta(days=30)


@dataclass
class PortfolioRecommendation:
    """AI-generated portfolio recommendation"""
    recommendation_id: str
    user_id: str
    recommendation_type: str  # 'rebalance', 'new_investment', 'exit', 'switch'
    title: str
    description: str
    rationale: str  # AI's reasoning
    priority: str   # 'high', 'medium', 'low'
    expected_impact: str  # Expected return/risk impact
    action_required: bool
    suggested_actions: List[Dict[str, Any]]
    confidence_score: float
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class AIPortfolioManager:
    """
    AI-Powered Portfolio Manager for subscription-based advisory
    Democratizing professional portfolio management for every Indian
    """
    
    def __init__(self):
        # Performance configuration
        self.performance_config = PerformanceConfig(
            max_response_time_ms=5000,  # Portfolio analysis can take longer
            max_concurrent_requests=1000,
            cache_ttl_seconds=3600,
            rate_limit_per_minute=100,
            circuit_breaker_threshold=3,
            service_tier=ServiceTier.HIGH
        )
        
        # Core components
        self.market_intelligence = MarketIntelligenceEngine()
        self.order_manager = OrderManager()
        self.whatsapp_client = WhatsAppClient()
        
        # Subscription tiers and pricing
        self.subscription_tiers = {
            SubscriptionTier.BASIC: {
                'monthly_fee': Decimal('99'),
                'features': [
                    'AI-generated portfolio strategy',
                    'Monthly rebalancing recommendations',
                    'Basic performance reporting',
                    'WhatsApp advisory alerts'
                ],
                'max_portfolio_value': Decimal('500000'),  # ₹5L limit
                'research_reports': 0,
                'personal_advisor_access': False
            },
            SubscriptionTier.PREMIUM: {
                'monthly_fee': Decimal('299'),
                'features': [
                    'Advanced AI strategies with market timing',
                    'Weekly portfolio optimization',
                    'Detailed performance analytics',
                    'Market research reports',
                    'Tax optimization suggestions'
                ],
                'max_portfolio_value': Decimal('2000000'),  # ₹20L limit
                'research_reports': 4,  # per month
                'personal_advisor_access': False
            },
            SubscriptionTier.ELITE: {
                'monthly_fee': Decimal('999'),
                'features': [
                    'Personalized AI advisor with learning',
                    'Real-time portfolio monitoring',
                    'Priority customer support',
                    'Unlimited research and analysis',
                    'Advanced tax and estate planning',
                    'Direct advisor WhatsApp access'
                ],
                'max_portfolio_value': None,  # No limit
                'research_reports': -1,  # Unlimited
                'personal_advisor_access': True
            }
        }
        
        # Model portfolios for different risk profiles
        self.model_portfolios = {
            RiskTolerance.CONSERVATIVE: {
                'equity_mf': 20,      # Large cap equity mutual funds
                'debt_mf': 60,        # Debt mutual funds
                'gold_etf': 10,       # Gold ETF
                'liquid_fund': 10     # Liquid funds
            },
            RiskTolerance.MODERATE: {
                'equity_mf': 50,      # Mix of large/mid cap
                'debt_mf': 30,        # Debt funds
                'gold_etf': 10,       # Gold ETF
                'international_mf': 10  # International equity
            },
            RiskTolerance.AGGRESSIVE: {
                'equity_mf': 70,      # Large/mid/small cap mix
                'debt_mf': 15,        # Short duration debt
                'gold_etf': 5,        # Gold
                'international_mf': 10  # International exposure
            }
        }
        
        # Asset class expected returns (annual %)
        self.expected_returns = {
            'equity_mf': 12.0,
            'debt_mf': 7.0,
            'gold_etf': 8.0,
            'liquid_fund': 5.0,
            'international_mf': 10.0
        }
        
        # Risk metrics (annual volatility %)
        self.volatility = {
            'equity_mf': 18.0,
            'debt_mf': 4.0,
            'gold_etf': 15.0,
            'liquid_fund': 1.0,
            'international_mf': 20.0
        }
    
    async def initialize(self):
        """Initialize AI Portfolio Manager"""
        
        try:
            logger.info("🤖 Initializing AI Portfolio Manager...")
            
            # Initialize market intelligence
            await self.market_intelligence.initialize()
            
            # Start background portfolio monitoring
            asyncio.create_task(self._background_portfolio_monitor())
            
            # Start subscription billing processor
            asyncio.create_task(self._subscription_billing_processor())
            
            # Load historical market data for AI training
            await self._load_market_data()
            
            logger.info("✅ AI Portfolio Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Portfolio Manager: {str(e)}")
            raise
    
    async def create_subscription(
        self,
        user_id: str,
        phone_number: str,
        tier: SubscriptionTier,
        risk_tolerance: RiskTolerance,
        investment_objective: InvestmentObjective,
        monthly_sip_amount: Decimal,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new AI portfolio management subscription"""
        
        try:
            logger.info(f"🤖 Creating portfolio subscription for user {user_id}")
            
            # Validate subscription eligibility
            eligibility = await self._check_subscription_eligibility(user_id, tier, monthly_sip_amount)
            if not eligibility['eligible']:
                return {
                    'success': False,
                    'error': eligibility['reason'],
                    'recommendation': eligibility.get('recommendation')
                }
            
            # Generate AI portfolio strategy
            strategy = await self._generate_ai_strategy(
                user_id=user_id,
                risk_tolerance=risk_tolerance,
                investment_objective=investment_objective,
                user_profile=user_profile,
                sip_amount=monthly_sip_amount
            )
            
            # Create subscription
            subscription_id = str(uuid.uuid4())
            
            subscription = PortfolioSubscription(
                subscription_id=subscription_id,
                user_id=user_id,
                tier=tier,
                monthly_fee=self.subscription_tiers[tier]['monthly_fee'],
                strategy_id=strategy.strategy_id,
                auto_invest_amount=monthly_sip_amount
            )
            
            # Store subscription and strategy
            await self._store_subscription(subscription)
            await self._store_strategy(strategy)
            
            # Send welcome message with strategy details
            welcome_message = await self._generate_welcome_message(subscription, strategy)
            await self.whatsapp_client.send_interactive_message(
                phone_number=phone_number,
                message=welcome_message['content'],
                buttons=welcome_message['buttons']
            )
            
            # Schedule first investment
            await self._schedule_first_investment(subscription, strategy)
            
            return {
                'success': True,
                'subscription_id': subscription_id,
                'strategy_id': strategy.strategy_id,
                'tier': tier.value,
                'monthly_fee': float(subscription.monthly_fee),
                'strategy_name': strategy.strategy_name,
                'expected_annual_return': f"{strategy.expected_return:.1f}%",
                'portfolio_allocation': strategy.target_allocation,
                'first_investment_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'welcome_message_sent': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_ai_strategy(
        self,
        user_id: str,
        risk_tolerance: RiskTolerance,
        investment_objective: InvestmentObjective,
        user_profile: Dict[str, Any],
        sip_amount: Decimal
    ) -> AIPortfolioStrategy:
        """Generate AI-powered portfolio strategy"""
        
        try:
            # Get current market intelligence
            market_data = await self.market_intelligence.get_comprehensive_analysis()
            
            # Base allocation from model portfolio
            base_allocation = self.model_portfolios[risk_tolerance].copy()
            
            # AI adjustments based on market conditions
            if market_data['market_sentiment'] == 'bearish':
                # Reduce equity exposure in bearish markets
                base_allocation = await self._adjust_for_bearish_market(base_allocation)
            elif market_data['market_sentiment'] == 'bullish':
                # Increase equity exposure in bullish markets
                base_allocation = await self._adjust_for_bullish_market(base_allocation, risk_tolerance)
            
            # Adjust for investment objective
            base_allocation = await self._adjust_for_objective(base_allocation, investment_objective)
            
            # Optimize using Modern Portfolio Theory
            optimized_allocation = await self._optimize_portfolio(base_allocation, sip_amount)
            
            # Select specific instruments
            recommended_instruments = await self._select_instruments(optimized_allocation, sip_amount)
            
            # Calculate expected metrics
            expected_return = self._calculate_expected_return(optimized_allocation)
            volatility = self._calculate_portfolio_volatility(optimized_allocation)
            sharpe_ratio = (expected_return - 6.0) / volatility  # Assuming 6% risk-free rate
            max_drawdown = self._estimate_max_drawdown(optimized_allocation, volatility)
            
            # Generate strategy name
            strategy_name = await self._generate_strategy_name(risk_tolerance, investment_objective, market_data)
            
            # AI confidence score based on market conditions and data quality
            confidence_score = await self._calculate_confidence_score(market_data, user_profile)
            
            strategy = AIPortfolioStrategy(
                strategy_id=str(uuid.uuid4()),
                user_id=user_id,
                strategy_name=strategy_name,
                risk_tolerance=risk_tolerance,
                investment_objective=investment_objective,
                target_allocation=optimized_allocation,
                recommended_instruments=recommended_instruments,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                rebalancing_frequency=RebalancingFrequency.QUARTERLY,
                ai_confidence_score=confidence_score
            )
            
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Error generating AI strategy: {str(e)}")
            raise
    
    async def get_portfolio_recommendations(
        self,
        user_id: str,
        phone_number: str
    ) -> Dict[str, Any]:
        """Get AI-generated portfolio recommendations"""
        
        try:
            # Get user's subscription
            subscription = await self._get_user_subscription(user_id)
            if not subscription or not subscription.is_active:
                return {
                    'success': False,
                    'message': 'No active portfolio subscription found',
                    'recommendation': 'Subscribe to AI Portfolio Manager to get personalized recommendations'
                }
            
            # Get current portfolio state
            portfolio_state = await self._get_current_portfolio(user_id)
            
            # Get strategy
            strategy = await self._get_strategy(subscription.strategy_id)
            
            # Analyze current market conditions
            market_analysis = await self.market_intelligence.get_comprehensive_analysis()
            
            # Generate recommendations using AI
            recommendations = await self._generate_recommendations(
                portfolio_state, strategy, market_analysis, subscription
            )
            
            if recommendations:
                # Send recommendations via WhatsApp
                recommendation_message = await self._format_recommendations_message(recommendations)
                await self.whatsapp_client.send_interactive_message(
                    phone_number=phone_number,
                    message=recommendation_message['content'],
                    buttons=recommendation_message['buttons']
                )
                
                return {
                    'success': True,
                    'recommendations_count': len(recommendations),
                    'recommendations': [asdict(rec) for rec in recommendations],
                    'message_sent': True
                }
            else:
                await self.whatsapp_client.send_text_message(
                    phone_number=phone_number,
                    message="🤖 **Portfolio Status: Optimal**\n\nYour portfolio is currently well-balanced and aligned with your strategy. No immediate action required.\n\n📊 Current allocation matches target\n✅ Risk levels within acceptable range\n📈 Performance on track with expectations\n\nI'll continue monitoring and notify you of any opportunities!"
                )
                
                return {
                    'success': True,
                    'recommendations_count': 0,
                    'message': 'Portfolio is optimally balanced',
                    'message_sent': True
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_recommendations(
        self,
        portfolio_state: Dict[str, Any],
        strategy: AIPortfolioStrategy,
        market_analysis: Dict[str, Any],
        subscription: PortfolioSubscription
    ) -> List[PortfolioRecommendation]:
        """Generate AI-powered portfolio recommendations"""
        
        recommendations = []
        
        try:
            # Check for rebalancing needs
            rebalance_rec = await self._check_rebalancing_need(portfolio_state, strategy)
            if rebalance_rec:
                recommendations.append(rebalance_rec)
            
            # Check for market opportunity recommendations
            if subscription.tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ELITE]:
                market_recs = await self._generate_market_opportunity_recommendations(
                    portfolio_state, strategy, market_analysis
                )
                recommendations.extend(market_recs)
            
            # Check for tax optimization (Elite tier)
            if subscription.tier == SubscriptionTier.ELITE:
                tax_recs = await self._generate_tax_optimization_recommendations(
                    portfolio_state, strategy
                )
                recommendations.extend(tax_recs)
            
            # Risk management recommendations
            risk_recs = await self._generate_risk_management_recommendations(
                portfolio_state, strategy, market_analysis
            )
            recommendations.extend(risk_recs)
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {str(e)}")
        
        return recommendations
    
    async def get_portfolio_performance(
        self,
        user_id: str,
        phone_number: str,
        period: str = "ytd"  # ytd, 1y, 3y, inception
    ) -> Dict[str, Any]:
        """Get comprehensive portfolio performance analytics"""
        
        try:
            # Get subscription and portfolio data
            subscription = await self._get_user_subscription(user_id)
            if not subscription:
                return {'error': 'No active subscription found'}
            
            portfolio_data = await self._get_portfolio_performance_data(user_id, period)
            benchmark_data = await self._get_benchmark_performance(period)
            
            # Calculate performance metrics
            performance_metrics = {
                'absolute_return': portfolio_data['total_return'],
                'annualized_return': portfolio_data['annualized_return'],
                'vs_benchmark': portfolio_data['total_return'] - benchmark_data['total_return'],
                'volatility': portfolio_data['volatility'],
                'sharpe_ratio': portfolio_data['sharpe_ratio'],
                'max_drawdown': portfolio_data['max_drawdown'],
                'alpha': portfolio_data['alpha'],
                'beta': portfolio_data['beta']
            }
            
            # Generate performance message
            performance_message = f"""🤖 **AI Portfolio Performance Report**
📊 **Period**: {period.upper()}

💰 **Returns**
• Your Portfolio: {performance_metrics['absolute_return']:+.1f}%
• Benchmark (Nifty 50): {benchmark_data['total_return']:+.1f}%  
• Outperformance: {performance_metrics['vs_benchmark']:+.1f}%

📈 **Risk Metrics**
• Annual Return: {performance_metrics['annualized_return']:.1f}%
• Volatility: {performance_metrics['volatility']:.1f}%
• Sharpe Ratio: {performance_metrics['sharpe_ratio']:.2f}
• Max Drawdown: {performance_metrics['max_drawdown']:.1f}%

🎯 **Portfolio Health**
• Risk-adjusted Performance: {"Excellent" if performance_metrics['sharpe_ratio'] > 1.0 else "Good" if performance_metrics['sharpe_ratio'] > 0.5 else "Needs Attention"}
• Correlation to Market: {performance_metrics['beta']:.2f}
• Alpha Generation: {performance_metrics['alpha']:+.1f}%

💡 **AI Insights**: {"Your portfolio is outperforming the market with controlled risk. The AI strategy is working well!" if performance_metrics['vs_benchmark'] > 0 else "Market headwinds affecting performance. Consider rebalancing opportunities."}"""
            
            await self.whatsapp_client.send_text_message(phone_number, performance_message)
            
            return {
                'success': True,
                'performance_metrics': performance_metrics,
                'portfolio_value': portfolio_data['current_value'],
                'total_invested': portfolio_data['total_invested'],
                'message_sent': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting portfolio performance: {str(e)}")
            return {'error': str(e)}
    
    async def _background_portfolio_monitor(self):
        """Background monitoring of all portfolios"""
        
        while True:
            try:
                # Get all active subscriptions
                active_subscriptions = await self._get_all_active_subscriptions()
                
                for subscription in active_subscriptions:
                    # Check for urgent recommendations
                    urgent_recs = await self._check_urgent_recommendations(subscription)
                    
                    if urgent_recs:
                        # Send urgent alerts
                        await self._send_urgent_alerts(subscription, urgent_recs)
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Portfolio monitor error: {str(e)}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _subscription_billing_processor(self):
        """Process subscription billing"""
        
        while True:
            try:
                # Get subscriptions due for billing
                due_subscriptions = await self._get_subscriptions_due_for_billing()
                
                for subscription in due_subscriptions:
                    # Process billing
                    billing_result = await self._process_subscription_billing(subscription)
                    
                    if not billing_result['success']:
                        # Handle billing failure
                        await self._handle_billing_failure(subscription, billing_result)
                
                # Check daily at 9 AM
                await asyncio.sleep(86400)  # 24 hours
                
            except Exception as e:
                logger.error(f"❌ Billing processor error: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    # Helper methods for portfolio optimization
    def _calculate_expected_return(self, allocation: Dict[str, float]) -> float:
        """Calculate portfolio expected return"""
        expected_return = 0.0
        for asset, weight in allocation.items():
            expected_return += (weight / 100) * self.expected_returns.get(asset, 8.0)
        return expected_return
    
    def _calculate_portfolio_volatility(self, allocation: Dict[str, float]) -> float:
        """Calculate portfolio volatility"""
        volatility = 0.0
        for asset, weight in allocation.items():
            volatility += ((weight / 100) ** 2) * (self.volatility.get(asset, 15.0) ** 2)
        return volatility ** 0.5
    
    def _estimate_max_drawdown(self, allocation: Dict[str, float], volatility: float) -> float:
        """Estimate maximum drawdown based on allocation and volatility"""
        # Conservative estimate: 2.5 * volatility
        return min(volatility * 2.5, 50.0)  # Cap at 50%
    
    # Database operations (to be implemented based on schema)
    async def _store_subscription(self, subscription: PortfolioSubscription):
        """Store subscription in database"""
        pass
    
    async def _store_strategy(self, strategy: AIPortfolioStrategy):
        """Store strategy in database"""
        pass
    
    async def _get_user_subscription(self, user_id: str) -> Optional[PortfolioSubscription]:
        """Get user's active subscription"""
        # Implementation depends on database schema
        return None
    
    # Additional helper methods would be implemented here...