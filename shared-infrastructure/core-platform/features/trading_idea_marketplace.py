"""
Trading Idea Marketplace

A comprehensive platform for trading ideas, signals, and educational content
with verified performance tracking, subscription management, and community features.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.logging import logger
from app.models.marketplace import TradingIdea, IdeaCategory, IdeaSubscription, IdeaPerformance
from app.models.payments import PaymentTransaction, SubscriptionPlan
from app.models.social import ExpertProfile, UserProfile
from app.services.payment_processor import PaymentProcessor
from app.services.performance_tracker import PerformanceTracker
from app.services.notification_service import NotificationService
from app.services.zk_verification import ZKVerificationService

router = APIRouter(prefix="/api/v1/marketplace", tags=["trading-marketplace"])

# Enums
class IdeaType(str, Enum):
    TRADE_SIGNAL = "TRADE_SIGNAL"
    TECHNICAL_ANALYSIS = "TECHNICAL_ANALYSIS"
    EDUCATIONAL_CONTENT = "EDUCATIONAL_CONTENT"
    MARKET_OUTLOOK = "MARKET_OUTLOOK"
    STRATEGY_GUIDE = "STRATEGY_GUIDE"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class TimeHorizon(str, Enum):
    INTRADAY = "INTRADAY"
    SHORT_TERM = "SHORT_TERM"  # 1-7 days
    MEDIUM_TERM = "MEDIUM_TERM"  # 1-4 weeks
    LONG_TERM = "LONG_TERM"  # 1+ months

# Pydantic Models
class TradingIdeaRequest(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=2000)
    idea_type: IdeaType
    category: str  # "EQUITY", "OPTIONS", "FUTURES", "CRYPTO", "FOREX"
    symbol: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    entry_price: Optional[float] = None
    risk_level: RiskLevel
    time_horizon: TimeHorizon
    expected_returns: Optional[str] = None  # "10-15%", "₹500-1000"
    chart_analysis: Optional[Dict[str, Any]] = None
    technical_rationale: str = Field(..., min_length=100)
    fundamental_rationale: Optional[str] = None
    is_premium: bool = Field(default=False)
    premium_price: Optional[Decimal] = None
    tags: List[str] = Field(default_factory=list)

class IdeaSubscriptionRequest(BaseModel):
    expert_user_id: str
    subscription_type: str = Field(..., regex="^(MONTHLY|QUARTERLY|YEARLY|LIFETIME)$")
    auto_renew: bool = Field(default=True)

class IdeaRatingRequest(BaseModel):
    idea_id: str
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=500)
    performance_accuracy: Optional[int] = Field(None, ge=1, le=5)

class MarketplaceSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    idea_type: Optional[IdeaType] = None
    risk_level: Optional[RiskLevel] = None
    time_horizon: Optional[TimeHorizon] = None
    min_rating: Optional[float] = None
    is_premium: Optional[bool] = None
    expert_user_id: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: str = Field(default="created_at", regex="^(created_at|rating|performance|price|popularity)$")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

# Response Models
class TradingIdeaResponse(BaseModel):
    idea_id: str
    title: str
    description: str
    idea_type: str
    category: str
    symbol: str
    expert_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    pricing: Dict[str, Any]
    created_at: str
    is_subscribed: bool

class MarketplaceStatsResponse(BaseModel):
    total_ideas: int
    active_experts: int
    success_rate: float
    total_subscribers: int
    featured_ideas: List[TradingIdeaResponse]

class TradingIdeaMarketplace:
    """Main marketplace manager for trading ideas"""
    
    def __init__(self):
        self.payment_processor = PaymentProcessor()
        self.performance_tracker = PerformanceTracker()
        self.notification_service = NotificationService()
        self.zk_verification = ZKVerificationService()
        
        # Pricing tiers for expert subscriptions
        self.subscription_pricing = {
            'MONTHLY': {
                'BASIC': Decimal('299'),
                'PREMIUM': Decimal('999'),
                'VIP': Decimal('2499')
            },
            'QUARTERLY': {
                'BASIC': Decimal('799'),  # 10% discount
                'PREMIUM': Decimal('2699'),
                'VIP': Decimal('6749')
            },
            'YEARLY': {
                'BASIC': Decimal('2999'),  # 16% discount
                'PREMIUM': Decimal('9999'),
                'VIP': Decimal('24999')
            },
            'LIFETIME': {
                'BASIC': Decimal('9999'),
                'PREMIUM': Decimal('29999'),
                'VIP': Decimal('74999')
            }
        }
        
        # Expert tier criteria
        self.expert_tiers = {
            'BASIC': {
                'min_success_rate': 0.60,
                'min_ideas': 20,
                'min_followers': 50,
                'max_premium_price': Decimal('99')
            },
            'PREMIUM': {
                'min_success_rate': 0.70,
                'min_ideas': 50,
                'min_followers': 200,
                'max_premium_price': Decimal('499')
            },
            'VIP': {
                'min_success_rate': 0.80,
                'min_ideas': 100,
                'min_followers': 1000,
                'max_premium_price': Decimal('1999')
            }
        }
    
    async def publish_trading_idea(
        self, 
        db: Session, 
        user_id: str, 
        idea_request: TradingIdeaRequest
    ) -> Dict[str, Any]:
        """Publish a new trading idea to the marketplace"""
        
        try:
            # Validate user is an expert
            expert_profile = await self._validate_expert_user(db, user_id)
            if not expert_profile:
                raise HTTPException(
                    status_code=403,
                    detail="Only verified experts can publish trading ideas"
                )
            
            # Validate premium pricing against expert tier
            if idea_request.is_premium and idea_request.premium_price:
                tier_limit = self.expert_tiers[expert_profile['tier']]['max_premium_price']
                if idea_request.premium_price > tier_limit:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Premium price exceeds tier limit of ₹{tier_limit}"
                    )
            
            # Generate ZK proof for idea authenticity
            zk_proof = await self.zk_verification.generate_idea_proof(
                expert_user_id=user_id,
                idea_content=idea_request.dict(),
                timestamp=datetime.utcnow()
            )
            
            # Create trading idea
            idea_id = str(uuid.uuid4())
            
            trading_idea = TradingIdea(
                id=idea_id,
                expert_user_id=user_id,
                title=idea_request.title,
                description=idea_request.description,
                idea_type=idea_request.idea_type.value,
                category=idea_request.category,
                symbol=idea_request.symbol,
                target_price=idea_request.target_price,
                stop_loss=idea_request.stop_loss,
                entry_price=idea_request.entry_price,
                risk_level=idea_request.risk_level.value,
                time_horizon=idea_request.time_horizon.value,
                expected_returns=idea_request.expected_returns,
                chart_analysis=json.dumps(idea_request.chart_analysis or {}),
                technical_rationale=idea_request.technical_rationale,
                fundamental_rationale=idea_request.fundamental_rationale,
                is_premium=idea_request.is_premium,
                premium_price=idea_request.premium_price,
                tags=json.dumps(idea_request.tags),
                zk_proof=zk_proof,
                status='ACTIVE',
                created_at=datetime.utcnow()
            )
            
            db.add(trading_idea)
            
            # Initialize performance tracking
            performance_record = IdeaPerformance(
                id=str(uuid.uuid4()),
                idea_id=idea_id,
                entry_timestamp=datetime.utcnow(),
                initial_price=idea_request.entry_price,
                target_price=idea_request.target_price,
                stop_loss=idea_request.stop_loss,
                status='ACTIVE',
                created_at=datetime.utcnow()
            )
            
            db.add(performance_record)
            
            # Send notifications to subscribers
            await self._notify_idea_subscribers(db, user_id, trading_idea)
            
            db.commit()
            
            return {
                'success': True,
                'idea_id': idea_id,
                'title': idea_request.title,
                'category': idea_request.category,
                'symbol': idea_request.symbol,
                'is_premium': idea_request.is_premium,
                'premium_price': float(idea_request.premium_price) if idea_request.premium_price else None,
                'zk_proof': zk_proof,
                'performance_tracking_started': True
            }
        
        except Exception as e:
            logger.error(f"Trading idea publication error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def search_marketplace(
        self, 
        db: Session, 
        user_id: str, 
        search_request: MarketplaceSearchRequest
    ) -> Dict[str, Any]:
        """Search trading ideas in marketplace"""
        
        try:
            # Build query
            query = db.query(TradingIdea).filter(
                TradingIdea.status == 'ACTIVE'
            )
            
            # Apply filters
            if search_request.query:
                query = query.filter(
                    TradingIdea.title.contains(search_request.query) |
                    TradingIdea.description.contains(search_request.query) |
                    TradingIdea.symbol.contains(search_request.query)
                )
            
            if search_request.category:
                query = query.filter(TradingIdea.category == search_request.category)
            
            if search_request.idea_type:
                query = query.filter(TradingIdea.idea_type == search_request.idea_type.value)
            
            if search_request.risk_level:
                query = query.filter(TradingIdea.risk_level == search_request.risk_level.value)
            
            if search_request.time_horizon:
                query = query.filter(TradingIdea.time_horizon == search_request.time_horizon.value)
            
            if search_request.expert_user_id:
                query = query.filter(TradingIdea.expert_user_id == search_request.expert_user_id)
            
            if search_request.is_premium is not None:
                query = query.filter(TradingIdea.is_premium == search_request.is_premium)
            
            # Apply sorting
            if search_request.sort_by == 'rating':
                # Join with ratings for sorting
                query = query.order_by(
                    TradingIdea.average_rating.desc() if search_request.sort_order == 'desc' 
                    else TradingIdea.average_rating.asc()
                )
            elif search_request.sort_by == 'created_at':
                query = query.order_by(
                    TradingIdea.created_at.desc() if search_request.sort_order == 'desc'
                    else TradingIdea.created_at.asc()
                )
            elif search_request.sort_by == 'price':
                query = query.order_by(
                    TradingIdea.premium_price.desc() if search_request.sort_order == 'desc'
                    else TradingIdea.premium_price.asc()
                )
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            ideas = query.offset(search_request.offset).limit(search_request.limit).all()
            
            # Get user's subscriptions
            user_subscriptions = await self._get_user_subscriptions(db, user_id)
            
            # Format results
            formatted_ideas = []
            for idea in ideas:
                expert_info = await self._get_expert_info(db, idea.expert_user_id)
                performance_metrics = await self._get_idea_performance(db, idea.id)
                
                is_subscribed = (
                    idea.expert_user_id in user_subscriptions or
                    not idea.is_premium or
                    idea.expert_user_id == user_id
                )
                
                formatted_ideas.append({
                    'idea_id': idea.id,
                    'title': idea.title,
                    'description': idea.description if is_subscribed else idea.description[:200] + "...",
                    'idea_type': idea.idea_type,
                    'category': idea.category,
                    'symbol': idea.symbol,
                    'risk_level': idea.risk_level,
                    'time_horizon': idea.time_horizon,
                    'target_price': idea.target_price if is_subscribed else None,
                    'stop_loss': idea.stop_loss if is_subscribed else None,
                    'entry_price': idea.entry_price,
                    'expected_returns': idea.expected_returns,
                    'is_premium': idea.is_premium,
                    'premium_price': float(idea.premium_price) if idea.premium_price else None,
                    'tags': json.loads(idea.tags),
                    'expert_info': expert_info,
                    'performance_metrics': performance_metrics,
                    'rating': float(idea.average_rating) if idea.average_rating else 0.0,
                    'created_at': idea.created_at.isoformat(),
                    'is_subscribed': is_subscribed
                })
            
            return {
                'ideas': formatted_ideas,
                'total_count': total_count,
                'page_info': {
                    'offset': search_request.offset,
                    'limit': search_request.limit,
                    'has_next': search_request.offset + search_request.limit < total_count
                }
            }
        
        except Exception as e:
            logger.error(f"Marketplace search error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def subscribe_to_expert(
        self, 
        db: Session, 
        user_id: str, 
        subscription_request: IdeaSubscriptionRequest
    ) -> Dict[str, Any]:
        """Subscribe to expert's premium content"""
        
        try:
            # Validate expert exists
            expert_profile = await self._validate_expert_user(db, subscription_request.expert_user_id)
            if not expert_profile:
                raise HTTPException(
                    status_code=404,
                    detail="Expert not found"
                )
            
            # Check if already subscribed
            existing_subscription = db.query(IdeaSubscription).filter(
                IdeaSubscription.subscriber_user_id == user_id,
                IdeaSubscription.expert_user_id == subscription_request.expert_user_id,
                IdeaSubscription.status == 'ACTIVE'
            ).first()
            
            if existing_subscription:
                raise HTTPException(
                    status_code=400,
                    detail="Already subscribed to this expert"
                )
            
            # Calculate pricing
            expert_tier = expert_profile['tier']
            subscription_price = self.subscription_pricing[subscription_request.subscription_type][expert_tier]
            
            # Process payment
            payment_result = await self.payment_processor.process_subscription_payment(
                user_id=user_id,
                amount=subscription_price,
                subscription_type=subscription_request.subscription_type,
                expert_user_id=subscription_request.expert_user_id
            )
            
            if not payment_result['success']:
                raise HTTPException(
                    status_code=402,
                    detail="Payment processing failed"
                )
            
            # Calculate subscription end date
            subscription_duration = {
                'MONTHLY': timedelta(days=30),
                'QUARTERLY': timedelta(days=90),
                'YEARLY': timedelta(days=365),
                'LIFETIME': timedelta(days=36500)  # 100 years
            }
            
            subscription_id = str(uuid.uuid4())
            
            subscription = IdeaSubscription(
                id=subscription_id,
                subscriber_user_id=user_id,
                expert_user_id=subscription_request.expert_user_id,
                subscription_type=subscription_request.subscription_type,
                price_paid=subscription_price,
                auto_renew=subscription_request.auto_renew,
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + subscription_duration[subscription_request.subscription_type],
                payment_transaction_id=payment_result['transaction_id'],
                status='ACTIVE',
                created_at=datetime.utcnow()
            )
            
            db.add(subscription)
            
            # Send confirmation notifications
            await self.notification_service.send_subscription_confirmation(
                subscriber_user_id=user_id,
                expert_user_id=subscription_request.expert_user_id,
                subscription_type=subscription_request.subscription_type
            )
            
            db.commit()
            
            return {
                'success': True,
                'subscription_id': subscription_id,
                'expert_name': expert_profile['name'],
                'subscription_type': subscription_request.subscription_type,
                'price_paid': float(subscription_price),
                'expires_at': subscription.expires_at.isoformat(),
                'access_granted': True
            }
        
        except Exception as e:
            logger.error(f"Expert subscription error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def rate_trading_idea(
        self, 
        db: Session, 
        user_id: str, 
        rating_request: IdeaRatingRequest
    ) -> Dict[str, Any]:
        """Rate and review a trading idea"""
        
        try:
            # Validate idea exists
            idea = db.query(TradingIdea).filter(TradingIdea.id == rating_request.idea_id).first()
            if not idea:
                raise HTTPException(status_code=404, detail="Trading idea not found")
            
            # Check if user has access to rate (subscribed or free idea)
            has_access = await self._check_idea_access(db, user_id, rating_request.idea_id)
            if not has_access:
                raise HTTPException(
                    status_code=403,
                    detail="Must be subscribed to rate premium ideas"
                )
            
            # Check if user already rated this idea
            existing_rating = db.query(IdeaRating).filter(
                IdeaRating.idea_id == rating_request.idea_id,
                IdeaRating.user_id == user_id
            ).first()
            
            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating_request.rating
                existing_rating.review = rating_request.review
                existing_rating.performance_accuracy = rating_request.performance_accuracy
                existing_rating.updated_at = datetime.utcnow()
            else:
                # Create new rating
                rating = IdeaRating(
                    id=str(uuid.uuid4()),
                    idea_id=rating_request.idea_id,
                    user_id=user_id,
                    rating=rating_request.rating,
                    review=rating_request.review,
                    performance_accuracy=rating_request.performance_accuracy,
                    created_at=datetime.utcnow()
                )
                db.add(rating)
            
            # Recalculate average rating
            await self._update_idea_average_rating(db, rating_request.idea_id)
            
            db.commit()
            
            return {
                'success': True,
                'idea_id': rating_request.idea_id,
                'your_rating': rating_request.rating,
                'review_added': bool(rating_request.review),
                'new_average_rating': await self._get_idea_average_rating(db, rating_request.idea_id)
            }
        
        except Exception as e:
            logger.error(f"Idea rating error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_marketplace_stats(self, db: Session) -> Dict[str, Any]:
        """Get marketplace statistics and featured content"""
        
        try:
            # Basic stats
            total_ideas = db.query(TradingIdea).filter(TradingIdea.status == 'ACTIVE').count()
            active_experts = db.query(ExpertProfile).filter(
                ExpertProfile.is_active == True,
                ExpertProfile.application_status == 'APPROVED'
            ).count()
            total_subscriptions = db.query(IdeaSubscription).filter(
                IdeaSubscription.status == 'ACTIVE'
            ).count()
            
            # Calculate overall success rate
            performance_records = db.query(IdeaPerformance).filter(
                IdeaPerformance.status.in_(['COMPLETED', 'STOPPED'])
            ).all()
            
            if performance_records:
                successful_ideas = sum(1 for p in performance_records if p.success_achieved)
                success_rate = successful_ideas / len(performance_records)
            else:
                success_rate = 0.0
            
            # Get featured ideas (top-rated recent ideas)
            featured_ideas = db.query(TradingIdea).filter(
                TradingIdea.status == 'ACTIVE',
                TradingIdea.average_rating >= 4.0,
                TradingIdea.created_at >= datetime.utcnow() - timedelta(days=7)
            ).order_by(TradingIdea.average_rating.desc()).limit(5).all()
            
            formatted_featured = []
            for idea in featured_ideas:
                expert_info = await self._get_expert_info(db, idea.expert_user_id)
                performance_metrics = await self._get_idea_performance(db, idea.id)
                
                formatted_featured.append({
                    'idea_id': idea.id,
                    'title': idea.title,
                    'description': idea.description[:200] + "...",
                    'symbol': idea.symbol,
                    'expert_info': expert_info,
                    'rating': float(idea.average_rating) if idea.average_rating else 0.0,
                    'performance_metrics': performance_metrics,
                    'is_premium': idea.is_premium,
                    'premium_price': float(idea.premium_price) if idea.premium_price else None
                })
            
            return {
                'total_ideas': total_ideas,
                'active_experts': active_experts,
                'success_rate': round(success_rate * 100, 1),
                'total_subscribers': total_subscriptions,
                'featured_ideas': formatted_featured,
                'categories': [
                    'EQUITY', 'OPTIONS', 'FUTURES', 'CRYPTO', 'FOREX'
                ],
                'subscription_tiers': list(self.subscription_pricing['MONTHLY'].keys())
            }
        
        except Exception as e:
            logger.error(f"Marketplace stats error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Private helper methods
    async def _validate_expert_user(self, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """Validate if user is an expert and get tier info"""
        
        expert_profile = db.query(ExpertProfile).filter(
            ExpertProfile.user_id == user_id,
            ExpertProfile.is_active == True,
            ExpertProfile.application_status == 'APPROVED'
        ).first()
        
        if not expert_profile:
            return None
        
        # Determine expert tier based on performance
        stats = await self._get_expert_stats(db, user_id)
        
        tier = 'BASIC'
        for tier_name, criteria in self.expert_tiers.items():
            if (stats['success_rate'] >= criteria['min_success_rate'] and
                stats['total_ideas'] >= criteria['min_ideas'] and
                stats['followers'] >= criteria['min_followers']):
                tier = tier_name
        
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        return {
            'is_expert': True,
            'name': user_profile.display_name if user_profile else 'Expert',
            'tier': tier,
            'stats': stats
        }
    
    async def _get_expert_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get expert performance statistics"""
        
        total_ideas = db.query(TradingIdea).filter(
            TradingIdea.expert_user_id == user_id,
            TradingIdea.status == 'ACTIVE'
        ).count()
        
        # Calculate success rate from performance records
        performance_records = db.query(IdeaPerformance).join(
            TradingIdea, IdeaPerformance.idea_id == TradingIdea.id
        ).filter(
            TradingIdea.expert_user_id == user_id,
            IdeaPerformance.status.in_(['COMPLETED', 'STOPPED'])
        ).all()
        
        if performance_records:
            successful = sum(1 for p in performance_records if p.success_achieved)
            success_rate = successful / len(performance_records)
        else:
            success_rate = 0.0
        
        # Get follower count (subscribers)
        followers = db.query(IdeaSubscription).filter(
            IdeaSubscription.expert_user_id == user_id,
            IdeaSubscription.status == 'ACTIVE'
        ).count()
        
        return {
            'total_ideas': total_ideas,
            'success_rate': success_rate,
            'followers': followers,
            'completed_ideas': len(performance_records)
        }
    
    async def _notify_idea_subscribers(self, db: Session, expert_user_id: str, idea: TradingIdea):
        """Notify subscribers about new idea publication"""
        
        subscribers = db.query(IdeaSubscription).filter(
            IdeaSubscription.expert_user_id == expert_user_id,
            IdeaSubscription.status == 'ACTIVE'
        ).all()
        
        for subscription in subscribers:
            await self.notification_service.send_new_idea_notification(
                subscriber_user_id=subscription.subscriber_user_id,
                expert_user_id=expert_user_id,
                idea_title=idea.title,
                idea_symbol=idea.symbol,
                idea_id=idea.id
            )
    
    async def _get_user_subscriptions(self, db: Session, user_id: str) -> Set[str]:
        """Get set of expert IDs user is subscribed to"""
        
        subscriptions = db.query(IdeaSubscription).filter(
            IdeaSubscription.subscriber_user_id == user_id,
            IdeaSubscription.status == 'ACTIVE',
            IdeaSubscription.expires_at > datetime.utcnow()
        ).all()
        
        return {sub.expert_user_id for sub in subscriptions}
    
    async def _get_expert_info(self, db: Session, expert_user_id: str) -> Dict[str, Any]:
        """Get expert information for display"""
        
        expert_profile = db.query(ExpertProfile).filter(
            ExpertProfile.user_id == expert_user_id
        ).first()
        
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == expert_user_id
        ).first()
        
        stats = await self._get_expert_stats(db, expert_user_id)
        
        return {
            'expert_id': expert_user_id,
            'name': user_profile.display_name if user_profile else 'Expert',
            'specialization': json.loads(expert_profile.specialization) if expert_profile else [],
            'success_rate': round(stats['success_rate'] * 100, 1),
            'total_ideas': stats['total_ideas'],
            'followers': stats['followers'],
            'verified': expert_profile.application_status == 'APPROVED' if expert_profile else False
        }
    
    async def _get_idea_performance(self, db: Session, idea_id: str) -> Dict[str, Any]:
        """Get performance metrics for an idea"""
        
        performance = db.query(IdeaPerformance).filter(
            IdeaPerformance.idea_id == idea_id
        ).first()
        
        if not performance:
            return {'status': 'NO_DATA'}
        
        return {
            'status': performance.status,
            'current_price': float(performance.current_price) if performance.current_price else None,
            'pnl_percentage': float(performance.pnl_percentage) if performance.pnl_percentage else None,
            'max_drawdown': float(performance.max_drawdown) if performance.max_drawdown else None,
            'success_achieved': performance.success_achieved,
            'days_active': (datetime.utcnow() - performance.entry_timestamp).days,
            'last_updated': performance.updated_at.isoformat() if performance.updated_at else None
        }
    
    async def _check_idea_access(self, db: Session, user_id: str, idea_id: str) -> bool:
        """Check if user has access to view/rate an idea"""
        
        idea = db.query(TradingIdea).filter(TradingIdea.id == idea_id).first()
        if not idea:
            return False
        
        # Own ideas are always accessible
        if idea.expert_user_id == user_id:
            return True
        
        # Free ideas are accessible to all
        if not idea.is_premium:
            return True
        
        # Check subscription for premium ideas
        subscription = db.query(IdeaSubscription).filter(
            IdeaSubscription.subscriber_user_id == user_id,
            IdeaSubscription.expert_user_id == idea.expert_user_id,
            IdeaSubscription.status == 'ACTIVE',
            IdeaSubscription.expires_at > datetime.utcnow()
        ).first()
        
        return subscription is not None
    
    async def _update_idea_average_rating(self, db: Session, idea_id: str):
        """Update the average rating for an idea"""
        
        ratings = db.query(IdeaRating).filter(IdeaRating.idea_id == idea_id).all()
        
        if ratings:
            average_rating = sum(r.rating for r in ratings) / len(ratings)
            
            idea = db.query(TradingIdea).filter(TradingIdea.id == idea_id).first()
            if idea:
                idea.average_rating = average_rating
                idea.total_ratings = len(ratings)
    
    async def _get_idea_average_rating(self, db: Session, idea_id: str) -> float:
        """Get current average rating for an idea"""
        
        idea = db.query(TradingIdea).filter(TradingIdea.id == idea_id).first()
        return float(idea.average_rating) if idea and idea.average_rating else 0.0


# Initialize marketplace manager
marketplace = TradingIdeaMarketplace()


# API Endpoints
@router.post("/publish-idea")
async def publish_trading_idea(
    idea_request: TradingIdeaRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a new trading idea"""
    
    result = await marketplace.publish_trading_idea(
        db, user["id"], idea_request
    )
    
    return result


@router.post("/search")
async def search_marketplace(
    search_request: MarketplaceSearchRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search trading ideas in marketplace"""
    
    result = await marketplace.search_marketplace(
        db, user["id"], search_request
    )
    
    return result


@router.post("/subscribe")
async def subscribe_to_expert(
    subscription_request: IdeaSubscriptionRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to expert's premium content"""
    
    result = await marketplace.subscribe_to_expert(
        db, user["id"], subscription_request
    )
    
    return result


@router.post("/rate-idea")
async def rate_trading_idea(
    rating_request: IdeaRatingRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate and review a trading idea"""
    
    result = await marketplace.rate_trading_idea(
        db, user["id"], rating_request
    )
    
    return result


@router.get("/stats", response_model=MarketplaceStatsResponse)
async def get_marketplace_stats(
    db: Session = Depends(get_db)
):
    """Get marketplace statistics and featured content"""
    
    result = await marketplace.get_marketplace_stats(db)
    
    return MarketplaceStatsResponse(**result)


@router.get("/my-ideas")
async def get_my_ideas(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's published trading ideas"""
    
    query = db.query(TradingIdea).filter(
        TradingIdea.expert_user_id == user["id"]
    )
    
    if status:
        query = query.filter(TradingIdea.status == status)
    
    ideas = query.order_by(TradingIdea.created_at.desc()).limit(limit).all()
    
    formatted_ideas = []
    for idea in ideas:
        performance_metrics = await marketplace._get_idea_performance(db, idea.id)
        
        formatted_ideas.append({
            'idea_id': idea.id,
            'title': idea.title,
            'symbol': idea.symbol,
            'idea_type': idea.idea_type,
            'category': idea.category,
            'status': idea.status,
            'is_premium': idea.is_premium,
            'premium_price': float(idea.premium_price) if idea.premium_price else None,
            'rating': float(idea.average_rating) if idea.average_rating else 0.0,
            'total_ratings': idea.total_ratings or 0,
            'performance_metrics': performance_metrics,
            'created_at': idea.created_at.isoformat()
        })
    
    return {'ideas': formatted_ideas}


@router.get("/my-subscriptions")
async def get_my_subscriptions(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active subscriptions"""
    
    subscriptions = db.query(IdeaSubscription).filter(
        IdeaSubscription.subscriber_user_id == user["id"],
        IdeaSubscription.status == 'ACTIVE'
    ).all()
    
    formatted_subscriptions = []
    for sub in subscriptions:
        expert_info = await marketplace._get_expert_info(db, sub.expert_user_id)
        
        formatted_subscriptions.append({
            'subscription_id': sub.id,
            'expert_info': expert_info,
            'subscription_type': sub.subscription_type,
            'price_paid': float(sub.price_paid),
            'expires_at': sub.expires_at.isoformat(),
            'auto_renew': sub.auto_renew,
            'started_at': sub.started_at.isoformat()
        })
    
    return {'subscriptions': formatted_subscriptions}


@router.get("/pricing")
async def get_subscription_pricing():
    """Get subscription pricing information"""
    
    return {
        'pricing_tiers': marketplace.subscription_pricing,
        'expert_tiers': marketplace.expert_tiers,
        'currency': 'INR'
    }


# Health check
@router.get("/health")
async def marketplace_health_check():
    """Health check for trading idea marketplace"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "marketplace": "operational",
        "features": {
            "idea_publishing": True,
            "expert_subscriptions": True,
            "performance_tracking": True,
            "zk_verification": True,
            "payment_processing": True,
            "rating_system": True
        },
        "subscription_tiers": list(marketplace.subscription_pricing['MONTHLY'].keys()),
        "supported_categories": ["EQUITY", "OPTIONS", "FUTURES", "CRYPTO", "FOREX"]
    }