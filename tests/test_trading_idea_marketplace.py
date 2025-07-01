"""
Comprehensive test suite for Trading Idea Marketplace
Tests idea publishing, subscriptions, ratings, and marketplace functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
import json
import uuid

from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.features.trading_idea_marketplace import (
    TradingIdeaMarketplace,
    TradingIdeaRequest,
    IdeaSubscriptionRequest,
    IdeaRatingRequest,
    MarketplaceSearchRequest,
    ExpertProfileRequest,
    IdeaType,
    RiskLevel,
    TimeHorizon
)


class TestTradingIdeaMarketplaceInit:
    """Test Trading Idea Marketplace initialization"""
    
    def test_marketplace_initialization(self):
        """Test marketplace initialization with default settings"""
        marketplace = TradingIdeaMarketplace()
        
        assert marketplace.payment_processor is not None
        assert marketplace.performance_tracker is not None
        assert marketplace.notification_service is not None
        assert marketplace.zk_verification is not None
        
        # Check subscription pricing structure
        assert 'MONTHLY' in marketplace.subscription_pricing
        assert 'QUARTERLY' in marketplace.subscription_pricing
        assert 'YEARLY' in marketplace.subscription_pricing
        assert 'LIFETIME' in marketplace.subscription_pricing
        
        # Check each subscription type has tier pricing
        for subscription_type in marketplace.subscription_pricing:
            assert 'BASIC' in marketplace.subscription_pricing[subscription_type]
            assert 'PREMIUM' in marketplace.subscription_pricing[subscription_type]
            assert 'VIP' in marketplace.subscription_pricing[subscription_type]
        
        # Check expert tiers
        assert 'BASIC' in marketplace.expert_tiers
        assert 'PREMIUM' in marketplace.expert_tiers
        assert 'VIP' in marketplace.expert_tiers
    
    def test_subscription_pricing_structure(self):
        """Test subscription pricing structure and values"""
        marketplace = TradingIdeaMarketplace()
        
        # Verify pricing increases with tier and duration
        monthly_basic = marketplace.subscription_pricing['MONTHLY']['BASIC']
        monthly_premium = marketplace.subscription_pricing['MONTHLY']['PREMIUM']
        monthly_vip = marketplace.subscription_pricing['MONTHLY']['VIP']
        
        assert monthly_basic < monthly_premium < monthly_vip
        
        # Verify quarterly has discount
        quarterly_basic = marketplace.subscription_pricing['QUARTERLY']['BASIC']
        assert quarterly_basic < monthly_basic * 3  # Should be discounted
        
        # Verify yearly has better discount
        yearly_basic = marketplace.subscription_pricing['YEARLY']['BASIC']
        assert yearly_basic < monthly_basic * 12  # Should be heavily discounted
    
    def test_expert_tier_criteria(self):
        """Test expert tier criteria are progressive"""
        marketplace = TradingIdeaMarketplace()
        
        basic = marketplace.expert_tiers['BASIC']
        premium = marketplace.expert_tiers['PREMIUM']
        vip = marketplace.expert_tiers['VIP']
        
        # Success rate should increase
        assert basic['min_success_rate'] < premium['min_success_rate'] < vip['min_success_rate']
        
        # Idea count should increase
        assert basic['min_ideas'] < premium['min_ideas'] < vip['min_ideas']
        
        # Follower count should increase
        assert basic['min_followers'] < premium['min_followers'] < vip['min_followers']
        
        # Max premium price should increase
        assert basic['max_premium_price'] < premium['max_premium_price'] < vip['max_premium_price']


class TestTradingIdeaPublishing:
    """Test trading idea publishing functionality"""
    
    @pytest.mark.asyncio
    async def test_successful_idea_publishing(
        self, 
        db_session, 
        expert_user,
        mock_zk_verification,
        mock_notification_service
    ):
        """Test successful trading idea publishing"""
        marketplace = TradingIdeaMarketplace()
        marketplace.zk_verification = mock_zk_verification
        marketplace.notification_service = mock_notification_service
        
        # Mock ZK proof generation
        mock_zk_verification.generate_idea_proof.return_value = "zk_proof_idea_123"
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM'}):
            with patch.object(marketplace, '_notify_idea_subscribers') as mock_notify:
                
                idea_request = TradingIdeaRequest(
                    title="RELIANCE Bullish Breakout Setup",
                    description="Strong breakout above key resistance with high volume confirmation. Target 2800, SL 2450.",
                    idea_type=IdeaType.TRADE_SIGNAL,
                    category="EQUITY",
                    symbol="RELIANCE",
                    target_price=2800.0,
                    stop_loss=2450.0,
                    entry_price=2500.0,
                    risk_level=RiskLevel.MEDIUM,
                    time_horizon=TimeHorizon.SHORT_TERM,
                    expected_returns="10-12%",
                    technical_rationale="RSI oversold bounce, MACD bullish crossover, breakout above 20-day MA with volume",
                    fundamental_rationale="Q3 results expected to be strong, oil prices stabilizing",
                    is_premium=True,
                    premium_price=Decimal("99.00"),
                    tags=["breakout", "volume", "technical", "momentum"]
                )
                
                result = await marketplace.publish_trading_idea(
                    db_session, expert_user.id, idea_request
                )
                
                assert result['success'] is True
                assert 'idea_id' in result
                assert result['title'] == "RELIANCE Bullish Breakout Setup"
                assert result['symbol'] == "RELIANCE"
                assert result['is_premium'] is True
                assert result['premium_price'] == 99.0
                assert result['zk_proof'] == "zk_proof_idea_123"
                assert result['performance_tracking_started'] is True
                
                # Verify services were called
                mock_zk_verification.generate_idea_proof.assert_called_once()
                mock_notify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_idea_publishing_non_expert(self, db_session, test_user):
        """Test idea publishing by non-expert should fail"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_validate_expert_user', return_value=None):
            
            idea_request = TradingIdeaRequest(
                title="Test Idea",
                description="This should fail as user is not an expert",
                idea_type=IdeaType.TECHNICAL_ANALYSIS,
                category="EQUITY",
                symbol="RELIANCE",
                risk_level=RiskLevel.LOW,
                time_horizon=TimeHorizon.INTRADAY,
                technical_rationale="Basic technical analysis"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await marketplace.publish_trading_idea(
                    db_session, test_user.id, idea_request
                )
            
            assert exc_info.value.status_code == 403
            assert "Only verified experts can publish" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_premium_price_exceeds_tier_limit(self, db_session, expert_user):
        """Test premium price validation against expert tier"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'BASIC'}):  # BASIC tier has lower price limit
            
            idea_request = TradingIdeaRequest(
                title="Expensive Idea",
                description="This idea has premium price exceeding BASIC tier limit",
                idea_type=IdeaType.TRADE_SIGNAL,
                category="EQUITY",
                symbol="RELIANCE",
                risk_level=RiskLevel.HIGH,
                time_horizon=TimeHorizon.MEDIUM_TERM,
                technical_rationale="Advanced analysis",
                is_premium=True,
                premium_price=Decimal("500.00")  # Exceeds BASIC tier limit
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await marketplace.publish_trading_idea(
                    db_session, expert_user.id, idea_request
                )
            
            assert exc_info.value.status_code == 400
            assert "Premium price exceeds tier limit" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_free_idea_publishing(self, db_session, expert_user, mock_zk_verification):
        """Test publishing free (non-premium) trading idea"""
        marketplace = TradingIdeaMarketplace()
        marketplace.zk_verification = mock_zk_verification
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'BASIC'}):
            with patch.object(marketplace, '_notify_idea_subscribers'):
                
                idea_request = TradingIdeaRequest(
                    title="Free Market Outlook",
                    description="General market outlook for the week ahead",
                    idea_type=IdeaType.MARKET_OUTLOOK,
                    category="INDEX",
                    symbol="NIFTY",
                    risk_level=RiskLevel.LOW,
                    time_horizon=TimeHorizon.MEDIUM_TERM,
                    technical_rationale="Technical outlook for next week",
                    is_premium=False,  # Free idea
                    tags=["market", "outlook", "weekly"]
                )
                
                result = await marketplace.publish_trading_idea(
                    db_session, expert_user.id, idea_request
                )
                
                assert result['success'] is True
                assert result['is_premium'] is False
                assert result['premium_price'] is None
    
    @pytest.mark.asyncio
    async def test_educational_content_publishing(self, db_session, expert_user):
        """Test publishing educational content"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'VIP'}):
            with patch.object(marketplace, '_notify_idea_subscribers'):
                with patch.object(marketplace.zk_verification, 'generate_idea_proof',
                                 return_value="zk_proof_edu_123"):
                    
                    idea_request = TradingIdeaRequest(
                        title="Options Trading Masterclass",
                        description="Complete guide to options trading strategies with real examples",
                        idea_type=IdeaType.EDUCATIONAL_CONTENT,
                        category="OPTIONS",
                        symbol="NIFTY",
                        risk_level=RiskLevel.HIGH,
                        time_horizon=TimeHorizon.LONG_TERM,
                        technical_rationale="Educational content covering advanced options strategies",
                        is_premium=True,
                        premium_price=Decimal("1999.00"),
                        tags=["education", "options", "strategies", "advanced"]
                    )
                    
                    result = await marketplace.publish_trading_idea(
                        db_session, expert_user.id, idea_request
                    )
                    
                    assert result['success'] is True
                    assert result['premium_price'] == 1999.0


class TestMarketplaceSearch:
    """Test marketplace search functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_search(self, db_session, test_user):
        """Test basic marketplace search"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock database query results
        mock_ideas = [
            Mock(
                id='idea_1',
                expert_user_id='expert_1',
                title='RELIANCE Buy Signal',
                description='Strong bullish signal',
                idea_type='TRADE_SIGNAL',
                category='EQUITY',
                symbol='RELIANCE',
                risk_level='MEDIUM',
                time_horizon='SHORT_TERM',
                target_price=2800.0,
                stop_loss=2450.0,
                entry_price=2500.0,
                expected_returns='10-12%',
                is_premium=True,
                premium_price=Decimal('99.00'),
                tags='["breakout", "volume"]',
                average_rating=Decimal('4.5'),
                created_at=datetime.utcnow()
            )
        ]
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.order_by.return_value.count.return_value = 1
            mock_query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_ideas
            
            with patch.object(marketplace, '_get_user_subscriptions', return_value=set()):
                with patch.object(marketplace, '_get_expert_info',
                                 return_value={'expert_id': 'expert_1', 'name': 'Expert Trader'}):
                    with patch.object(marketplace, '_get_idea_performance',
                                     return_value={'status': 'ACTIVE', 'pnl_percentage': 5.2}):
                        
                        search_request = MarketplaceSearchRequest(
                            query="RELIANCE",
                            category="EQUITY",
                            risk_level=RiskLevel.MEDIUM,
                            limit=20
                        )
                        
                        result = await marketplace.search_marketplace(
                            db_session, test_user.id, search_request
                        )
                        
                        assert len(result['ideas']) == 1
                        assert result['total_count'] == 1
                        
                        idea = result['ideas'][0]
                        assert idea['idea_id'] == 'idea_1'
                        assert idea['symbol'] == 'RELIANCE'
                        assert idea['is_premium'] is True
                        assert idea['is_subscribed'] is False  # Not subscribed
    
    @pytest.mark.asyncio
    async def test_search_with_subscription_access(self, db_session, test_user):
        """Test search results with subscription access"""
        marketplace = TradingIdeaMarketplace()
        
        mock_ideas = [
            Mock(
                id='idea_1',
                expert_user_id='expert_1',
                title='Premium Signal',
                description='Full premium content should be visible',
                idea_type='TRADE_SIGNAL',
                symbol='NIFTY',
                is_premium=True,
                premium_price=Decimal('199.00'),
                target_price=18500.0,
                stop_loss=18200.0,
                entry_price=18300.0,
                tags='["premium", "signal"]',
                created_at=datetime.utcnow()
            )
        ]
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.order_by.return_value.count.return_value = 1
            mock_query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_ideas
            
            with patch.object(marketplace, '_get_user_subscriptions', 
                             return_value={'expert_1'}):  # User is subscribed
                with patch.object(marketplace, '_get_expert_info',
                                 return_value={'expert_id': 'expert_1', 'name': 'Expert'}):
                    with patch.object(marketplace, '_get_idea_performance',
                                     return_value={'status': 'ACTIVE'}):
                        
                        search_request = MarketplaceSearchRequest(
                            symbol="NIFTY",
                            is_premium=True
                        )
                        
                        result = await marketplace.search_marketplace(
                            db_session, test_user.id, search_request
                        )
                        
                        idea = result['ideas'][0]
                        assert idea['is_subscribed'] is True
                        assert idea['target_price'] == 18500.0  # Full content visible
                        assert idea['stop_loss'] == 18200.0
                        assert "Full premium content" in idea['description']
    
    @pytest.mark.asyncio
    async def test_search_filtering(self, db_session, test_user):
        """Test search with various filters"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = mock_query.return_value.filter
            
            search_request = MarketplaceSearchRequest(
                query="breakout",
                category="EQUITY",
                idea_type=IdeaType.TRADE_SIGNAL,
                risk_level=RiskLevel.HIGH,
                time_horizon=TimeHorizon.SHORT_TERM,
                expert_user_id="expert_123",
                is_premium=True,
                sort_by="rating",
                sort_order="desc"
            )
            
            await marketplace.search_marketplace(db_session, test_user.id, search_request)
            
            # Verify filters were applied (mock was called with filters)
            assert mock_filter.call_count > 0
    
    @pytest.mark.asyncio
    async def test_search_pagination(self, db_session, test_user):
        """Test search pagination"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.order_by.return_value.count.return_value = 50
            mock_query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
            
            with patch.object(marketplace, '_get_user_subscriptions', return_value=set()):
                
                search_request = MarketplaceSearchRequest(
                    offset=20,
                    limit=10
                )
                
                result = await marketplace.search_marketplace(
                    db_session, test_user.id, search_request
                )
                
                assert result['total_count'] == 50
                assert result['page_info']['offset'] == 20
                assert result['page_info']['limit'] == 10
                assert result['page_info']['has_next'] is True  # 20 + 10 < 50


class TestExpertSubscriptions:
    """Test expert subscription functionality"""
    
    @pytest.mark.asyncio
    async def test_successful_subscription(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_payment_processor,
        mock_notification_service
    ):
        """Test successful expert subscription"""
        marketplace = TradingIdeaMarketplace()
        marketplace.payment_processor = mock_payment_processor
        marketplace.notification_service = mock_notification_service
        
        # Mock successful payment
        mock_payment_processor.process_subscription_payment.return_value = {
            'success': True,
            'transaction_id': 'txn_123456'
        }
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM', 'name': 'Expert Trader'}):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None  # No existing subscription
                
                subscription_request = IdeaSubscriptionRequest(
                    expert_user_id=expert_user.id,
                    subscription_type="MONTHLY",
                    auto_renew=True
                )
                
                result = await marketplace.subscribe_to_expert(
                    db_session, test_user.id, subscription_request
                )
                
                assert result['success'] is True
                assert 'subscription_id' in result
                assert result['expert_name'] == 'Expert Trader'
                assert result['subscription_type'] == 'MONTHLY'
                assert result['price_paid'] == float(marketplace.subscription_pricing['MONTHLY']['PREMIUM'])
                assert result['access_granted'] is True
                
                # Verify payment was processed
                mock_payment_processor.process_subscription_payment.assert_called_once()
                
                # Verify notification was sent
                mock_notification_service.send_subscription_confirmation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscription_to_non_expert(self, db_session, test_user):
        """Test subscription to non-expert should fail"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_validate_expert_user', return_value=None):
            
            subscription_request = IdeaSubscriptionRequest(
                expert_user_id="non_expert_user",
                subscription_type="MONTHLY"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await marketplace.subscribe_to_expert(
                    db_session, test_user.id, subscription_request
                )
            
            assert exc_info.value.status_code == 404
            assert "Expert not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_duplicate_subscription(self, db_session, test_user, expert_user):
        """Test duplicate subscription should fail"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'BASIC'}):
            
            # Mock existing active subscription
            mock_existing_subscription = Mock()
            mock_existing_subscription.status = 'ACTIVE'
            
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = mock_existing_subscription
                
                subscription_request = IdeaSubscriptionRequest(
                    expert_user_id=expert_user.id,
                    subscription_type="QUARTERLY"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    await marketplace.subscribe_to_expert(
                        db_session, test_user.id, subscription_request
                    )
                
                assert exc_info.value.status_code == 400
                assert "Already subscribed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_payment_failure(self, db_session, test_user, expert_user, mock_payment_processor):
        """Test subscription with payment failure"""
        marketplace = TradingIdeaMarketplace()
        marketplace.payment_processor = mock_payment_processor
        
        # Mock payment failure
        mock_payment_processor.process_subscription_payment.return_value = {
            'success': False,
            'error': 'Card declined'
        }
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'BASIC'}):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                subscription_request = IdeaSubscriptionRequest(
                    expert_user_id=expert_user.id,
                    subscription_type="YEARLY"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    await marketplace.subscribe_to_expert(
                        db_session, test_user.id, subscription_request
                    )
                
                assert exc_info.value.status_code == 402
                assert "Payment processing failed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_subscription_pricing_calculation(self, db_session, test_user, expert_user):
        """Test subscription pricing calculation for different tiers and durations"""
        marketplace = TradingIdeaMarketplace()
        
        test_cases = [
            ('BASIC', 'MONTHLY'),
            ('PREMIUM', 'QUARTERLY'),
            ('VIP', 'YEARLY'),
            ('BASIC', 'LIFETIME')
        ]
        
        for tier, duration in test_cases:
            with patch.object(marketplace, '_validate_expert_user',
                             return_value={'tier': tier}):
                with patch.object(db_session, 'query') as mock_query:
                    mock_query.return_value.filter.return_value.first.return_value = None
                    
                    with patch.object(marketplace.payment_processor, 'process_subscription_payment',
                                     return_value={'success': True, 'transaction_id': 'txn_123'}):
                        
                        subscription_request = IdeaSubscriptionRequest(
                            expert_user_id=expert_user.id,
                            subscription_type=duration
                        )
                        
                        result = await marketplace.subscribe_to_expert(
                            db_session, test_user.id, subscription_request
                        )
                        
                        expected_price = marketplace.subscription_pricing[duration][tier]
                        assert result['price_paid'] == float(expected_price)


class TestIdeaRating:
    """Test trading idea rating functionality"""
    
    @pytest.mark.asyncio
    async def test_successful_rating(self, db_session, test_user, sample_trading_idea):
        """Test successful idea rating"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_check_idea_access', return_value=True):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None  # No existing rating
                
                with patch.object(marketplace, '_update_idea_average_rating') as mock_update:
                    with patch.object(marketplace, '_get_idea_average_rating', return_value=4.2):
                        
                        rating_request = IdeaRatingRequest(
                            idea_id=sample_trading_idea.id,
                            rating=4,
                            review="Great analysis with clear entry/exit points",
                            performance_accuracy=5
                        )
                        
                        result = await marketplace.rate_trading_idea(
                            db_session, test_user.id, rating_request
                        )
                        
                        assert result['success'] is True
                        assert result['idea_id'] == sample_trading_idea.id
                        assert result['your_rating'] == 4
                        assert result['review_added'] is True
                        assert result['new_average_rating'] == 4.2
                        
                        # Verify average rating was updated
                        mock_update.assert_called_once_with(db_session, sample_trading_idea.id)
    
    @pytest.mark.asyncio
    async def test_rating_update(self, db_session, test_user, sample_trading_idea):
        """Test updating existing rating"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock existing rating
        mock_existing_rating = Mock()
        mock_existing_rating.rating = 3
        mock_existing_rating.review = "Initial review"
        
        with patch.object(marketplace, '_check_idea_access', return_value=True):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = mock_existing_rating
                
                with patch.object(marketplace, '_update_idea_average_rating'):
                    with patch.object(marketplace, '_get_idea_average_rating', return_value=4.5):
                        
                        rating_request = IdeaRatingRequest(
                            idea_id=sample_trading_idea.id,
                            rating=5,
                            review="Updated review - even better results!",
                            performance_accuracy=5
                        )
                        
                        result = await marketplace.rate_trading_idea(
                            db_session, test_user.id, rating_request
                        )
                        
                        assert result['success'] is True
                        assert result['your_rating'] == 5
                        
                        # Verify existing rating was updated
                        assert mock_existing_rating.rating == 5
                        assert mock_existing_rating.review == "Updated review - even better results!"
    
    @pytest.mark.asyncio
    async def test_rating_without_access(self, db_session, test_user, sample_trading_idea):
        """Test rating without idea access should fail"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(marketplace, '_check_idea_access', return_value=False):
            
            rating_request = IdeaRatingRequest(
                idea_id=sample_trading_idea.id,
                rating=4,
                review="Should not be allowed"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await marketplace.rate_trading_idea(
                    db_session, test_user.id, rating_request
                )
            
            assert exc_info.value.status_code == 403
            assert "Must be subscribed to rate premium ideas" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_rating_non_existent_idea(self, db_session, test_user):
        """Test rating non-existent idea should fail"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None  # No idea found
            
            rating_request = IdeaRatingRequest(
                idea_id="non_existent_idea",
                rating=5,
                review="This should fail"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await marketplace.rate_trading_idea(
                    db_session, test_user.id, rating_request
                )
            
            assert exc_info.value.status_code == 404
            assert "Trading idea not found" in str(exc_info.value.detail)


class TestMarketplaceStats:
    """Test marketplace statistics functionality"""
    
    @pytest.mark.asyncio
    async def test_marketplace_stats_calculation(self, db_session):
        """Test marketplace statistics calculation"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock database queries
        with patch.object(db_session, 'query') as mock_query:
            # Mock idea count
            mock_query.return_value.filter.return_value.count.side_effect = [
                250,  # total_ideas
                45,   # active_experts
                1500  # total_subscriptions
            ]
            
            # Mock performance records
            mock_performance_records = [
                Mock(success_achieved=True),
                Mock(success_achieved=True),
                Mock(success_achieved=False),
                Mock(success_achieved=True),
                Mock(success_achieved=False)
            ]
            mock_query.return_value.filter.return_value.all.side_effect = [
                mock_performance_records,  # Performance records
                []  # Featured ideas (will be mocked separately)
            ]
            
            # Mock featured ideas query
            featured_mock = Mock()
            featured_mock.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_query.return_value.filter.return_value.filter.return_value = featured_mock
            
            with patch.object(marketplace, '_get_expert_info', return_value={'expert_id': 'expert_1'}):
                with patch.object(marketplace, '_get_idea_performance', return_value={'status': 'ACTIVE'}):
                    
                    result = await marketplace.get_marketplace_stats(db_session)
                    
                    assert result['total_ideas'] == 250
                    assert result['active_experts'] == 45
                    assert result['total_subscribers'] == 1500
                    assert result['success_rate'] == 60.0  # 3 out of 5 successful
                    assert 'featured_ideas' in result
                    assert 'categories' in result
                    assert 'subscription_tiers' in result
    
    @pytest.mark.asyncio
    async def test_marketplace_stats_no_performance_data(self, db_session):
        """Test marketplace stats with no performance data"""
        marketplace = TradingIdeaMarketplace()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.count.side_effect = [100, 20, 500]
            mock_query.return_value.filter.return_value.all.side_effect = [[], []]  # No performance data
            
            # Mock featured ideas query
            featured_mock = Mock()
            featured_mock.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_query.return_value.filter.return_value.filter.return_value = featured_mock
            
            result = await marketplace.get_marketplace_stats(db_session)
            
            assert result['success_rate'] == 0.0  # No data means 0% success rate
    
    @pytest.mark.asyncio
    async def test_featured_ideas_selection(self, db_session):
        """Test featured ideas selection criteria"""
        marketplace = TradingIdeaMarketplace()
        
        # Create mock featured ideas
        mock_featured_ideas = [
            Mock(
                id='featured_1',
                expert_user_id='expert_1',
                title='Top Rated Signal',
                description='High rated trading signal' * 10,  # Long description to test truncation
                symbol='RELIANCE',
                is_premium=True,
                premium_price=Decimal('299.00'),
                average_rating=Decimal('4.8'),
                created_at=datetime.utcnow()
            )
        ]
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.count.side_effect = [100, 20, 500]
            mock_query.return_value.filter.return_value.all.side_effect = [[], mock_featured_ideas]
            
            # Mock featured ideas query chain
            featured_mock = Mock()
            featured_mock.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_featured_ideas
            mock_query.return_value.filter.return_value.filter.return_value = featured_mock
            
            with patch.object(marketplace, '_get_expert_info',
                             return_value={'expert_id': 'expert_1', 'name': 'Top Expert'}):
                with patch.object(marketplace, '_get_idea_performance',
                                 return_value={'status': 'ACTIVE', 'pnl_percentage': 8.5}):
                    
                    result = await marketplace.get_marketplace_stats(db_session)
                    
                    assert len(result['featured_ideas']) == 1
                    featured = result['featured_ideas'][0]
                    assert featured['idea_id'] == 'featured_1'
                    assert featured['rating'] == 4.8
                    assert featured['description'].endswith('...')  # Should be truncated


class TestMarketplaceHelpers:
    """Test marketplace helper methods"""
    
    @pytest.mark.asyncio
    async def test_validate_expert_user_success(self, db_session, expert_user):
        """Test successful expert user validation"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock expert profile
        mock_expert_profile = Mock()
        mock_expert_profile.user_id = expert_user.id
        mock_expert_profile.is_active = True
        mock_expert_profile.application_status = 'APPROVED'
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_expert_profile
            
            with patch.object(marketplace, '_get_expert_stats',
                             return_value={'success_rate': 0.75, 'total_ideas': 60, 'followers': 25}):
                with patch.object(db_session, 'query') as mock_user_query:
                    mock_user_profile = Mock()
                    mock_user_profile.display_name = 'Expert Trader'
                    mock_user_query.return_value.filter.return_value.first.return_value = mock_user_profile
                    
                    result = await marketplace._validate_expert_user(db_session, expert_user.id)
                    
                    assert result['is_expert'] is True
                    assert result['name'] == 'Expert Trader'
                    assert result['tier'] in ['BASIC', 'PREMIUM', 'VIP']
                    assert 'stats' in result
    
    @pytest.mark.asyncio
    async def test_get_expert_stats(self, db_session, expert_user):
        """Test expert statistics calculation"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock performance records
        mock_performance_records = [
            Mock(success_achieved=True),
            Mock(success_achieved=True),
            Mock(success_achieved=False),
            Mock(success_achieved=True)
        ]
        
        with patch.object(db_session, 'query') as mock_query:
            # Mock ideas count
            mock_query.return_value.filter.return_value.count.side_effect = [
                25,  # total_ideas
                15   # followers (subscriptions)
            ]
            
            # Mock performance records
            join_mock = Mock()
            join_mock.filter.return_value.all.return_value = mock_performance_records
            mock_query.return_value.join.return_value = join_mock
            
            stats = await marketplace._get_expert_stats(db_session, expert_user.id)
            
            assert stats['total_ideas'] == 25
            assert stats['success_rate'] == 0.75  # 3 out of 4 successful
            assert stats['followers'] == 15
            assert stats['completed_ideas'] == 4
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions(self, db_session, test_user):
        """Test user subscriptions retrieval"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock active subscriptions
        mock_subscriptions = [
            Mock(expert_user_id='expert_1'),
            Mock(expert_user_id='expert_2'),
            Mock(expert_user_id='expert_3')
        ]
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = mock_subscriptions
            
            subscriptions = await marketplace._get_user_subscriptions(db_session, test_user.id)
            
            assert subscriptions == {'expert_1', 'expert_2', 'expert_3'}
    
    @pytest.mark.asyncio
    async def test_check_idea_access_owner(self, db_session, test_user):
        """Test idea access check for idea owner"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock idea owned by user
        mock_idea = Mock()
        mock_idea.expert_user_id = test_user.id
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_idea
            
            has_access = await marketplace._check_idea_access(db_session, test_user.id, 'idea_123')
            
            assert has_access is True
    
    @pytest.mark.asyncio
    async def test_check_idea_access_free_idea(self, db_session, test_user):
        """Test idea access check for free idea"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock free idea
        mock_idea = Mock()
        mock_idea.expert_user_id = 'other_user'
        mock_idea.is_premium = False
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_idea
            
            has_access = await marketplace._check_idea_access(db_session, test_user.id, 'idea_123')
            
            assert has_access is True
    
    @pytest.mark.asyncio
    async def test_check_idea_access_premium_with_subscription(self, db_session, test_user):
        """Test idea access check for premium idea with subscription"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock premium idea
        mock_idea = Mock()
        mock_idea.expert_user_id = 'expert_user'
        mock_idea.is_premium = True
        
        # Mock active subscription
        mock_subscription = Mock()
        mock_subscription.status = 'ACTIVE'
        mock_subscription.expires_at = datetime.utcnow() + timedelta(days=30)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.side_effect = [
                mock_idea,  # First call for idea
                mock_subscription  # Second call for subscription
            ]
            
            has_access = await marketplace._check_idea_access(db_session, test_user.id, 'idea_123')
            
            assert has_access is True
    
    @pytest.mark.asyncio
    async def test_check_idea_access_premium_without_subscription(self, db_session, test_user):
        """Test idea access check for premium idea without subscription"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock premium idea
        mock_idea = Mock()
        mock_idea.expert_user_id = 'expert_user'
        mock_idea.is_premium = True
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.side_effect = [
                mock_idea,  # First call for idea
                None  # No subscription found
            ]
            
            has_access = await marketplace._check_idea_access(db_session, test_user.id, 'idea_123')
            
            assert has_access is False


class TestMarketplaceAPIEndpoints:
    """Test marketplace API endpoints"""
    
    def test_publish_idea_endpoint(self, test_client, expert_auth_headers):
        """Test /api/v1/marketplace/publish-idea endpoint"""
        idea_data = {
            "title": "NIFTY Bullish Setup",
            "description": "Strong bullish setup forming on NIFTY with volume confirmation",
            "idea_type": "TRADE_SIGNAL",
            "category": "INDEX",
            "symbol": "NIFTY",
            "target_price": 19000.0,
            "stop_loss": 18500.0,
            "entry_price": 18700.0,
            "risk_level": "MEDIUM",
            "time_horizon": "SHORT_TERM",
            "expected_returns": "8-10%",
            "technical_rationale": "Breakout above key resistance with RSI bullish divergence",
            "is_premium": True,
            "premium_price": 199.0,
            "tags": ["breakout", "momentum", "index"]
        }
        
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.publish_trading_idea.return_value = {
                'success': True,
                'idea_id': 'idea_123',
                'title': 'NIFTY Bullish Setup',
                'symbol': 'NIFTY',
                'is_premium': True,
                'premium_price': 199.0,
                'zk_proof': 'zk_proof_123'
            }
            
            response = test_client.post(
                "/api/v1/marketplace/publish-idea",
                json=idea_data,
                headers=expert_auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['idea_id'] == 'idea_123'
    
    def test_search_endpoint(self, test_client, auth_headers):
        """Test /api/v1/marketplace/search endpoint"""
        search_data = {
            "query": "RELIANCE",
            "category": "EQUITY",
            "risk_level": "MEDIUM",
            "limit": 10,
            "offset": 0
        }
        
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.search_marketplace.return_value = {
                'ideas': [
                    {
                        'idea_id': 'idea_1',
                        'title': 'RELIANCE Buy Signal',
                        'symbol': 'RELIANCE',
                        'is_premium': True,
                        'rating': 4.5
                    }
                ],
                'total_count': 1,
                'page_info': {
                    'offset': 0,
                    'limit': 10,
                    'has_next': False
                }
            }
            
            response = test_client.post(
                "/api/v1/marketplace/search",
                json=search_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data['ideas']) == 1
            assert data['total_count'] == 1
    
    def test_subscribe_endpoint(self, test_client, auth_headers):
        """Test /api/v1/marketplace/subscribe endpoint"""
        subscription_data = {
            "expert_user_id": "expert_123",
            "subscription_type": "MONTHLY",
            "auto_renew": True
        }
        
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.subscribe_to_expert.return_value = {
                'success': True,
                'subscription_id': 'sub_123',
                'expert_name': 'Expert Trader',
                'subscription_type': 'MONTHLY',
                'price_paid': 999.0,
                'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'access_granted': True
            }
            
            response = test_client.post(
                "/api/v1/marketplace/subscribe",
                json=subscription_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['subscription_id'] == 'sub_123'
    
    def test_rate_idea_endpoint(self, test_client, auth_headers):
        """Test /api/v1/marketplace/rate-idea endpoint"""
        rating_data = {
            "idea_id": "idea_123",
            "rating": 5,
            "review": "Excellent analysis with great results!",
            "performance_accuracy": 5
        }
        
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.rate_trading_idea.return_value = {
                'success': True,
                'idea_id': 'idea_123',
                'your_rating': 5,
                'review_added': True,
                'new_average_rating': 4.6
            }
            
            response = test_client.post(
                "/api/v1/marketplace/rate-idea",
                json=rating_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['your_rating'] == 5
    
    def test_stats_endpoint(self, test_client):
        """Test /api/v1/marketplace/stats endpoint"""
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.get_marketplace_stats.return_value = {
                'total_ideas': 500,
                'active_experts': 75,
                'success_rate': 72.5,
                'total_subscribers': 2500,
                'featured_ideas': [],
                'categories': ['EQUITY', 'OPTIONS', 'FUTURES', 'CRYPTO', 'FOREX'],
                'subscription_tiers': ['BASIC', 'PREMIUM', 'VIP']
            }
            
            response = test_client.get("/api/v1/marketplace/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data['total_ideas'] == 500
            assert data['success_rate'] == 72.5
    
    def test_health_endpoint(self, test_client):
        """Test /api/v1/marketplace/health endpoint"""
        response = test_client.get("/api/v1/marketplace/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['marketplace'] == 'operational'
        assert 'features' in data


class TestMarketplaceIntegration:
    """Integration tests for marketplace functionality"""
    
    @pytest.mark.asyncio
    async def test_complete_marketplace_workflow(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_payment_processor,
        mock_zk_verification
    ):
        """Test complete marketplace workflow from publishing to subscription to rating"""
        marketplace = TradingIdeaMarketplace()
        marketplace.payment_processor = mock_payment_processor
        marketplace.zk_verification = mock_zk_verification
        
        # Step 1: Expert publishes idea
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM'}):
            with patch.object(marketplace, '_notify_idea_subscribers'):
                
                idea_request = TradingIdeaRequest(
                    title="Complete Workflow Test Idea",
                    description="Testing complete marketplace workflow",
                    idea_type=IdeaType.TRADE_SIGNAL,
                    category="EQUITY",
                    symbol="TESTSTOCK",
                    risk_level=RiskLevel.MEDIUM,
                    time_horizon=TimeHorizon.SHORT_TERM,
                    technical_rationale="Test rationale",
                    is_premium=True,
                    premium_price=Decimal("99.00")
                )
                
                publish_result = await marketplace.publish_trading_idea(
                    db_session, expert_user.id, idea_request
                )
                
                assert publish_result['success'] is True
                idea_id = publish_result['idea_id']
        
        # Step 2: User subscribes to expert
        mock_payment_processor.process_subscription_payment.return_value = {
            'success': True,
            'transaction_id': 'txn_workflow_123'
        }
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM', 'name': 'Expert'}):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                subscription_request = IdeaSubscriptionRequest(
                    expert_user_id=expert_user.id,
                    subscription_type="MONTHLY"
                )
                
                subscription_result = await marketplace.subscribe_to_expert(
                    db_session, test_user.id, subscription_request
                )
                
                assert subscription_result['success'] is True
        
        # Step 3: User rates the idea
        with patch.object(marketplace, '_check_idea_access', return_value=True):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.side_effect = [
                    Mock(id=idea_id),  # Idea exists
                    None  # No existing rating
                ]
                
                with patch.object(marketplace, '_update_idea_average_rating'):
                    with patch.object(marketplace, '_get_idea_average_rating', return_value=4.5):
                        
                        rating_request = IdeaRatingRequest(
                            idea_id=idea_id,
                            rating=5,
                            review="Excellent workflow test!"
                        )
                        
                        rating_result = await marketplace.rate_trading_idea(
                            db_session, test_user.id, rating_request
                        )
                        
                        assert rating_result['success'] is True
                        assert rating_result['your_rating'] == 5
        
        # Verify complete workflow
        assert publish_result['idea_id'] == idea_id
        assert subscription_result['expert_name'] == 'Expert'
        assert rating_result['idea_id'] == idea_id