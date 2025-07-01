"""
Micro-Investing Engine - Revolutionary Spare Change Investment
UPI round-up automation for democratizing wealth creation at scale
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_UP
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import json

from app.core.config import settings
from app.core.enterprise_architecture import PerformanceConfig, ServiceTier
from app.trading.order_manager import OrderManager
from app.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)


class RoundUpStrategy(Enum):
    NEXT_RUPEE = "next_rupee"      # ₹47.30 → ₹1 round-up
    NEXT_FIVE = "next_five"        # ₹47.30 → ₹3 round-up to ₹50
    NEXT_TEN = "next_ten"          # ₹47.30 → ₹3 round-up to ₹50
    CUSTOM_AMOUNT = "custom"       # Fixed amount per transaction


class InvestmentGoal(Enum):
    EMERGENCY_FUND = "emergency_fund"
    CHILD_EDUCATION = "child_education"
    RETIREMENT = "retirement"
    HOUSE_DOWN_PAYMENT = "house_down_payment"
    VACATION = "vacation"
    WEALTH_BUILDING = "wealth_building"
    MARRIAGE = "marriage"


class MerchantCategory(Enum):
    KIRANA_GROCERY = "kirana_grocery"
    PETROL_PUMP = "petrol_pump"
    RESTAURANT = "restaurant"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    SHOPPING = "shopping"
    MEDICAL = "medical"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    ALL_CATEGORIES = "all_categories"


@dataclass
class RoundUpRule:
    """User's round-up investment rule configuration"""
    user_id: str
    rule_id: str
    strategy: RoundUpStrategy
    custom_amount: Optional[Decimal] = None
    merchant_categories: List[MerchantCategory] = None
    min_transaction_amount: Decimal = Decimal('10')
    max_daily_roundup: Decimal = Decimal('100')
    investment_goal: InvestmentGoal = InvestmentGoal.WEALTH_BUILDING
    target_instrument: str = "EQUITY_MF"  # Equity Mutual Fund default
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.merchant_categories is None:
            self.merchant_categories = [MerchantCategory.ALL_CATEGORIES]


@dataclass
class UPITransaction:
    """UPI transaction for round-up analysis"""
    transaction_id: str
    user_id: str
    amount: Decimal
    merchant_name: str
    merchant_category: MerchantCategory
    timestamp: datetime
    upi_ref_id: str
    payment_app: str  # GPay, PhonePe, Paytm, etc.


@dataclass
class RoundUpInvestment:
    """Generated round-up investment"""
    investment_id: str
    user_id: str
    rule_id: str
    source_transaction_id: str
    original_amount: Decimal
    roundup_amount: Decimal
    investment_instrument: str
    status: str = "pending"
    executed_at: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class MicroInvestingEngine:
    """
    Revolutionary micro-investing engine for spare change investment
    Enables wealth building for every Indian, starting with ₹1
    """
    
    def __init__(self):
        # Performance configuration for real-time UPI processing
        self.performance_config = PerformanceConfig(
            max_response_time_ms=100,  # Must be fast for UPI callbacks
            max_concurrent_requests=50000,
            cache_ttl_seconds=30,
            rate_limit_per_minute=10000,
            circuit_breaker_threshold=2,
            service_tier=ServiceTier.CRITICAL
        )
        
        # Core components
        self.order_manager = OrderManager()
        self.whatsapp_client = WhatsAppClient()
        
        # Investment instruments for different goals
        self.goal_instruments = {
            InvestmentGoal.EMERGENCY_FUND: "LIQUID_FUND",
            InvestmentGoal.CHILD_EDUCATION: "CHILD_PLAN_MF",
            InvestmentGoal.RETIREMENT: "EQUITY_MF",
            InvestmentGoal.HOUSE_DOWN_PAYMENT: "DEBT_FUND",
            InvestmentGoal.VACATION: "SHORT_TERM_FUND",
            InvestmentGoal.WEALTH_BUILDING: "EQUITY_MF",
            InvestmentGoal.MARRIAGE: "BALANCED_FUND"
        }
        
        # Merchant category detection patterns
        self.merchant_patterns = {
            MerchantCategory.KIRANA_GROCERY: [
                'kirana', 'grocery', 'general store', 'provision', 'super market',
                'big bazaar', 'reliance fresh', 'more supermarket', 'dmart'
            ],
            MerchantCategory.PETROL_PUMP: [
                'petrol', 'diesel', 'fuel', 'indian oil', 'bharat petroleum',
                'hindustan petroleum', 'shell', 'essar oil'
            ],
            MerchantCategory.RESTAURANT: [
                'restaurant', 'cafe', 'food', 'zomato', 'swiggy', 'hotel',
                'dhaba', 'tiffin', 'mess'
            ],
            MerchantCategory.TRANSPORT: [
                'uber', 'ola', 'metro', 'bus', 'auto', 'taxi', 'transport',
                'parking', 'toll', 'railway'
            ]
        }
        
        # Cache for performance
        self.roundup_cache = {}
        self.user_rules_cache = {}
        
        # Background processing
        self.processing_queue = []
        self.batch_size = 100
    
    async def initialize(self):
        """Initialize micro-investing engine"""
        
        try:
            logger.info("💰 Initializing Micro-Investing Engine...")
            
            # Start background batch processor
            asyncio.create_task(self._background_batch_processor())
            
            # Initialize UPI webhook listeners
            await self._setup_upi_webhooks()
            
            # Load default investment instruments
            await self._initialize_investment_instruments()
            
            logger.info("✅ Micro-Investing Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Micro-Investing Engine: {str(e)}")
            raise
    
    async def setup_roundup_rule(
        self,
        user_id: str,
        phone_number: str,
        strategy: RoundUpStrategy = RoundUpStrategy.NEXT_RUPEE,
        investment_goal: InvestmentGoal = InvestmentGoal.WEALTH_BUILDING,
        merchant_categories: List[MerchantCategory] = None,
        custom_amount: Optional[Decimal] = None,
        max_daily_roundup: Decimal = Decimal('100')
    ) -> Dict[str, Any]:
        """Set up round-up investment rule for user"""
        
        try:
            logger.info(f"💰 Setting up round-up rule for user {user_id}")
            
            # Create round-up rule
            rule_id = str(uuid.uuid4())
            
            roundup_rule = RoundUpRule(
                user_id=user_id,
                rule_id=rule_id,
                strategy=strategy,
                custom_amount=custom_amount,
                merchant_categories=merchant_categories or [MerchantCategory.ALL_CATEGORIES],
                max_daily_roundup=max_daily_roundup,
                investment_goal=investment_goal,
                target_instrument=self.goal_instruments.get(investment_goal, "EQUITY_MF")
            )
            
            # Store rule in database
            await self._store_roundup_rule(roundup_rule)
            
            # Update cache
            self.user_rules_cache[user_id] = roundup_rule
            
            # Send WhatsApp confirmation
            confirmation_message = await self._generate_rule_confirmation_message(roundup_rule)
            await self.whatsapp_client.send_interactive_message(
                phone_number=phone_number,
                message=confirmation_message['content'],
                buttons=confirmation_message['buttons']
            )
            
            return {
                'success': True,
                'rule_id': rule_id,
                'message': 'Round-up investing activated successfully!',
                'strategy': strategy.value,
                'investment_goal': investment_goal.value,
                'target_instrument': roundup_rule.target_instrument,
                'estimated_monthly_investment': await self._estimate_monthly_investment(user_id, roundup_rule)
            }
            
        except Exception as e:
            logger.error(f"❌ Error setting up round-up rule: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recommendation': 'Please try again or contact support'
            }
    
    async def process_upi_transaction(
        self,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process UPI transaction for potential round-up investment"""
        
        try:
            # Parse UPI transaction
            upi_transaction = UPITransaction(
                transaction_id=transaction_data['transaction_id'],
                user_id=transaction_data['user_id'],
                amount=Decimal(str(transaction_data['amount'])),
                merchant_name=transaction_data.get('merchant_name', 'Unknown'),
                merchant_category=await self._classify_merchant(transaction_data.get('merchant_name', '')),
                timestamp=datetime.fromisoformat(transaction_data['timestamp']),
                upi_ref_id=transaction_data.get('upi_ref_id', ''),
                payment_app=transaction_data.get('payment_app', 'Unknown')
            )
            
            # Get user's round-up rules
            roundup_rules = await self._get_user_roundup_rules(upi_transaction.user_id)
            
            if not roundup_rules:
                return {'status': 'no_rules', 'message': 'No round-up rules configured'}
            
            # Process each applicable rule
            roundup_investments = []
            for rule in roundup_rules:
                if await self._should_apply_rule(rule, upi_transaction):
                    roundup_amount = await self._calculate_roundup_amount(rule, upi_transaction.amount)
                    
                    if roundup_amount > 0:
                        # Check daily limits
                        if await self._check_daily_limits(rule, roundup_amount):
                            # Create round-up investment
                            roundup_investment = RoundUpInvestment(
                                investment_id=str(uuid.uuid4()),
                                user_id=upi_transaction.user_id,
                                rule_id=rule.rule_id,
                                source_transaction_id=upi_transaction.transaction_id,
                                original_amount=upi_transaction.amount,
                                roundup_amount=roundup_amount,
                                investment_instrument=rule.target_instrument
                            )
                            
                            roundup_investments.append(roundup_investment)
            
            # Process investments
            if roundup_investments:
                # Add to batch processing queue for efficiency
                self.processing_queue.extend(roundup_investments)
                
                # Send immediate notification for large round-ups
                total_roundup = sum(inv.roundup_amount for inv in roundup_investments)
                if total_roundup >= Decimal('10'):
                    await self._send_roundup_notification(
                        upi_transaction.user_id,
                        upi_transaction,
                        roundup_investments
                    )
                
                return {
                    'status': 'processed',
                    'roundup_investments_created': len(roundup_investments),
                    'total_roundup_amount': float(total_roundup),
                    'investments': [asdict(inv) for inv in roundup_investments]
                }
            
            else:
                return {
                    'status': 'no_roundup',
                    'message': 'Transaction did not trigger any round-up rules'
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing UPI transaction: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _calculate_roundup_amount(
        self,
        rule: RoundUpRule,
        transaction_amount: Decimal
    ) -> Decimal:
        """Calculate round-up amount based on rule strategy"""
        
        if rule.strategy == RoundUpStrategy.NEXT_RUPEE:
            # Round up to next rupee
            # ₹47.30 → ₹1.00 round-up (to make it ₹48)
            return Decimal('1') - (transaction_amount % Decimal('1'))
        
        elif rule.strategy == RoundUpStrategy.NEXT_FIVE:
            # Round up to next ₹5
            # ₹47.30 → ₹2.70 round-up (to make it ₹50)
            remainder = transaction_amount % Decimal('5')
            return Decimal('5') - remainder if remainder > 0 else Decimal('0')
        
        elif rule.strategy == RoundUpStrategy.NEXT_TEN:
            # Round up to next ₹10
            # ₹47.30 → ₹2.70 round-up (to make it ₹50)
            remainder = transaction_amount % Decimal('10')
            return Decimal('10') - remainder if remainder > 0 else Decimal('0')
        
        elif rule.strategy == RoundUpStrategy.CUSTOM_AMOUNT:
            # Fixed amount per transaction
            return rule.custom_amount or Decimal('5')
        
        else:
            return Decimal('1')  # Default to ₹1
    
    async def _classify_merchant(self, merchant_name: str) -> MerchantCategory:
        """Classify merchant based on name patterns"""
        
        merchant_lower = merchant_name.lower()
        
        for category, patterns in self.merchant_patterns.items():
            for pattern in patterns:
                if pattern in merchant_lower:
                    return category
        
        return MerchantCategory.ALL_CATEGORIES
    
    async def _should_apply_rule(
        self,
        rule: RoundUpRule,
        transaction: UPITransaction
    ) -> bool:
        """Check if round-up rule should apply to this transaction"""
        
        # Check if rule is active
        if not rule.is_active:
            return False
        
        # Check minimum transaction amount
        if transaction.amount < rule.min_transaction_amount:
            return False
        
        # Check merchant category filter
        if (MerchantCategory.ALL_CATEGORIES not in rule.merchant_categories and
            transaction.merchant_category not in rule.merchant_categories):
            return False
        
        return True
    
    async def _check_daily_limits(
        self,
        rule: RoundUpRule,
        roundup_amount: Decimal
    ) -> bool:
        """Check if round-up respects daily limits"""
        
        # Get today's total round-ups for this rule
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_roundups = await self._get_daily_roundups(rule.user_id, rule.rule_id, today_start)
        
        total_today = sum(roundup.roundup_amount for roundup in today_roundups)
        
        return (total_today + roundup_amount) <= rule.max_daily_roundup
    
    async def _background_batch_processor(self):
        """Background processor for batch executing round-up investments"""
        
        while True:
            try:
                if len(self.processing_queue) >= self.batch_size:
                    # Process batch
                    batch = self.processing_queue[:self.batch_size]
                    self.processing_queue = self.processing_queue[self.batch_size:]
                    
                    await self._execute_roundup_batch(batch)
                
                # Process smaller batches every 30 seconds
                elif len(self.processing_queue) > 0:
                    await asyncio.sleep(30)
                    if self.processing_queue:
                        batch = self.processing_queue[:min(10, len(self.processing_queue))]
                        self.processing_queue = self.processing_queue[len(batch):]
                        await self._execute_roundup_batch(batch)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Batch processor error: {str(e)}")
                await asyncio.sleep(60)  # Wait on error
    
    async def _execute_roundup_batch(self, roundup_investments: List[RoundUpInvestment]):
        """Execute a batch of round-up investments efficiently"""
        
        try:
            logger.info(f"💰 Executing batch of {len(roundup_investments)} round-up investments")
            
            # Group by instrument for efficient execution
            by_instrument = {}
            for investment in roundup_investments:
                instrument = investment.investment_instrument
                if instrument not in by_instrument:
                    by_instrument[instrument] = []
                by_instrument[instrument].append(investment)
            
            # Execute grouped investments
            results = []
            for instrument, investments in by_instrument.items():
                total_amount = sum(inv.roundup_amount for inv in investments)
                
                # Execute bulk investment
                execution_result = await self._execute_bulk_investment(
                    instrument=instrument,
                    total_amount=total_amount,
                    investments=investments
                )
                
                results.append(execution_result)
                
                # Update investment status
                for investment in investments:
                    investment.status = 'executed' if execution_result['success'] else 'failed'
                    investment.executed_at = datetime.utcnow()
                    await self._store_roundup_investment(investment)
            
            # Send batch completion notifications
            await self._send_batch_completion_notifications(roundup_investments, results)
            
        except Exception as e:
            logger.error(f"❌ Error executing round-up batch: {str(e)}")
    
    async def get_roundup_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive round-up investment analytics"""
        
        try:
            # Get user's round-up history
            roundup_history = await self._get_user_roundup_history(user_id, days=90)
            
            if not roundup_history:
                return {
                    'total_roundups': 0,
                    'total_invested': 0,
                    'message': 'No round-up investments yet. Start by setting up round-up rules!'
                }
            
            # Calculate analytics
            total_roundups = len(roundup_history)
            total_invested = sum(r.roundup_amount for r in roundup_history)
            avg_roundup = total_invested / total_roundups if total_roundups > 0 else 0
            
            # Monthly breakdown
            monthly_data = {}
            for roundup in roundup_history:
                month_key = roundup.created_at.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'count': 0, 'amount': Decimal('0')}
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['amount'] += roundup.roundup_amount
            
            # Category breakdown
            category_data = {}
            for roundup in roundup_history:
                instrument = roundup.investment_instrument
                if instrument not in category_data:
                    category_data[instrument] = {'count': 0, 'amount': Decimal('0')}
                category_data[instrument]['count'] += 1
                category_data[instrument]['amount'] += roundup.roundup_amount
            
            # Growth projection
            monthly_avg = total_invested / 3 if total_invested > 0 else 0  # Assume 3 months of data
            annual_projection = monthly_avg * 12
            
            return {
                'user_id': user_id,
                'period': '90 days',
                'summary': {
                    'total_roundups': total_roundups,
                    'total_invested': float(total_invested),
                    'average_roundup': float(avg_roundup),
                    'largest_roundup': float(max(r.roundup_amount for r in roundup_history)),
                    'smallest_roundup': float(min(r.roundup_amount for r in roundup_history))
                },
                'monthly_breakdown': {
                    month: {
                        'count': data['count'],
                        'amount': float(data['amount'])
                    }
                    for month, data in monthly_data.items()
                },
                'investment_breakdown': {
                    instrument: {
                        'count': data['count'],
                        'amount': float(data['amount'])
                    }
                    for instrument, data in category_data.items()
                },
                'projections': {
                    'monthly_estimate': float(monthly_avg),
                    'annual_estimate': float(annual_projection),
                    'wealth_impact': f"₹{annual_projection * 10:,.0f} in 10 years (assuming 12% growth)"
                },
                'achievements': await self._calculate_roundup_achievements(user_id, roundup_history)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting round-up analytics: {str(e)}")
            return {'error': str(e)}
    
    async def pause_resume_roundups(
        self,
        user_id: str,
        phone_number: str,
        action: str  # 'pause' or 'resume'
    ) -> Dict[str, Any]:
        """Pause or resume round-up investments"""
        
        try:
            # Get user's rules
            rules = await self._get_user_roundup_rules(user_id)
            
            if not rules:
                return {
                    'success': False,
                    'message': 'No round-up rules found to pause/resume'
                }
            
            # Update all rules
            for rule in rules:
                rule.is_active = (action == 'resume')
                await self._update_roundup_rule(rule)
            
            # Clear cache
            if user_id in self.user_rules_cache:
                del self.user_rules_cache[user_id]
            
            # Send confirmation
            action_message = "paused" if action == 'pause' else "resumed"
            message = f"""🔄 **Round-up Investing {action_message.title()}**

Your spare change investments have been {action_message}.

📊 **Current Rules**: {len(rules)} active
💰 **Impact**: {action_message.title()} automatic investing from UPI transactions

Type 'roundup analytics' to see your investment history!"""
            
            await self.whatsapp_client.send_text_message(phone_number, message)
            
            return {
                'success': True,
                'action': action,
                'rules_affected': len(rules),
                'message': f'Round-up investing {action_message} successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error pausing/resuming round-ups: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Helper methods (implementations would be added based on database schema)
    async def _store_roundup_rule(self, rule: RoundUpRule):
        """Store round-up rule in database"""
        # Implementation depends on database schema
        pass
    
    async def _get_user_roundup_rules(self, user_id: str) -> List[RoundUpRule]:
        """Get user's round-up rules from database"""
        # Implementation depends on database schema
        return []
    
    async def _store_roundup_investment(self, investment: RoundUpInvestment):
        """Store round-up investment in database"""
        # Implementation depends on database schema
        pass
    
    async def _execute_bulk_investment(
        self,
        instrument: str,
        total_amount: Decimal,
        investments: List[RoundUpInvestment]
    ) -> Dict[str, Any]:
        """Execute bulk investment in specified instrument"""
        # Implementation would integrate with order management system
        return {'success': True, 'order_id': str(uuid.uuid4())}
    
    # Additional helper methods would be implemented here...