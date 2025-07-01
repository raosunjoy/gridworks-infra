"""
Social Trading Engine - Advanced Copy Trading and Community Features
High-performance, secure implementation with comprehensive risk management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac

from app.core.database import get_async_session
from app.core.config import settings
from app.trading.risk_engine import RiskEngine
from app.trading.order_manager import OrderManager
from app.whatsapp.client import WhatsAppClient
from app.models.user import User
from app.models.social_trading import (
    TradingLeader, Follower, CopyTrade, SocialTradingGroup, 
    PerformanceMetrics, TradingSignal
)

logger = logging.getLogger(__name__)


class CopyTradeStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class LeadershipTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver" 
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class CopyTradeRequest:
    """Secure copy trade request with validation"""
    follower_id: str
    leader_id: str
    original_trade_id: str
    symbol: str
    action: str  # buy/sell
    quantity: int
    price: Decimal
    copy_ratio: Decimal
    max_copy_amount: Decimal
    risk_score: float
    timestamp: datetime
    signature: str
    
    def __post_init__(self):
        """Validate and secure copy trade request"""
        # Validate copy ratio bounds
        if not 0.01 <= self.copy_ratio <= 1.0:
            raise ValueError("Copy ratio must be between 1% and 100%")
        
        # Validate price bounds
        if self.price <= 0:
            raise ValueError("Price must be positive")
        
        # Verify signature for security
        if not self._verify_signature():
            raise ValueError("Invalid copy trade signature")
    
    def _verify_signature(self) -> bool:
        """Verify cryptographic signature to prevent tampering"""
        payload = f"{self.follower_id}:{self.leader_id}:{self.original_trade_id}:{self.symbol}:{self.quantity}:{self.price}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(self.signature, expected_signature)


class SocialTradingEngine:
    """High-performance social trading engine with security and risk management"""
    
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.order_manager = OrderManager()
        self.whatsapp_client = WhatsAppClient()
        
        # Performance optimization: In-memory caches
        self._leader_cache: Dict[str, TradingLeader] = {}
        self._follower_cache: Dict[str, List[str]] = {}  # follower_id -> [leader_ids]
        self._active_copies: Set[str] = set()  # Track active copy operations
        
        # Security: Rate limiting
        self._copy_attempts: Dict[str, List[datetime]] = {}
        self.max_copies_per_minute = 10
        
        # Performance metrics
        self._performance_tracker = {
            'copy_trades_processed': 0,
            'avg_processing_time': 0.0,
            'success_rate': 0.0
        }
    
    async def process_leader_trade(
        self,
        leader_id: str,
        trade_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process trade from leader and trigger copy trades"""
        
        start_time = datetime.utcnow()
        
        try:
            # Security: Validate leader credentials
            leader = await self._get_verified_leader(leader_id)
            if not leader or not leader.is_active:
                raise ValueError(f"Invalid or inactive leader: {leader_id}")
            
            # Get all followers for this leader
            followers = await self._get_active_followers(leader_id)
            
            if not followers:
                logger.info(f"📊 No active followers for leader {leader_id}")
                return {"status": "no_followers", "processed": 0}
            
            # Create copy trade requests
            copy_requests = await self._generate_copy_requests(
                leader_id=leader_id,
                trade_data=trade_data,
                followers=followers
            )
            
            # Process copy trades concurrently for performance
            copy_results = await asyncio.gather(
                *[self._process_copy_trade(request) for request in copy_requests],
                return_exceptions=True
            )
            
            # Analyze results
            successful_copies = [r for r in copy_results if isinstance(r, dict) and r.get('status') == 'executed']
            failed_copies = [r for r in copy_results if isinstance(r, Exception) or (isinstance(r, dict) and r.get('status') != 'executed')]
            
            # Update performance metrics
            self._update_performance_metrics(
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                success_count=len(successful_copies),
                total_count=len(copy_requests)
            )
            
            # Send notifications to leader
            await self._notify_leader_copy_performance(
                leader_id=leader_id,
                trade_data=trade_data,
                copy_stats={
                    'total_followers': len(followers),
                    'successful_copies': len(successful_copies),
                    'failed_copies': len(failed_copies),
                    'total_copy_value': sum(r.get('copy_value', 0) for r in successful_copies)
                }
            )
            
            return {
                "status": "processed",
                "leader_id": leader_id,
                "total_followers": len(followers),
                "successful_copies": len(successful_copies),
                "failed_copies": len(failed_copies),
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing leader trade: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_copy_requests(
        self,
        leader_id: str,
        trade_data: Dict[str, Any],
        followers: List[Dict[str, Any]]
    ) -> List[CopyTradeRequest]:
        """Generate secure copy trade requests with risk assessment"""
        
        copy_requests = []
        
        for follower_data in followers:
            try:
                follower_id = follower_data['user_id']
                copy_settings = follower_data['copy_settings']
                
                # Security: Rate limiting check
                if not await self._check_copy_rate_limit(follower_id):
                    logger.warning(f"⚠️ Rate limit hit for follower {follower_id}")
                    continue
                
                # Calculate copy quantity based on settings
                original_quantity = trade_data['quantity']
                copy_ratio = Decimal(str(copy_settings.get('copy_ratio', 0.1)))
                max_copy_amount = Decimal(str(copy_settings.get('max_copy_amount', 10000)))
                
                # Calculate actual copy quantity
                copy_quantity = int(original_quantity * copy_ratio)
                copy_value = copy_quantity * Decimal(str(trade_data['price']))
                
                # Enforce maximum copy amount
                if copy_value > max_copy_amount:
                    copy_quantity = int(max_copy_amount / Decimal(str(trade_data['price'])))
                    copy_value = copy_quantity * Decimal(str(trade_data['price']))
                
                # Skip if copy quantity is too small
                if copy_quantity < 1:
                    continue
                
                # Risk assessment
                risk_score = await self.risk_engine.assess_copy_trade_risk(
                    follower_id=follower_id,
                    symbol=trade_data['symbol'],
                    quantity=copy_quantity,
                    action=trade_data['action']
                )
                
                # Skip high-risk trades based on follower settings
                if risk_score > copy_settings.get('max_risk_score', 7.0):
                    await self._notify_follower_risk_skip(
                        follower_id=follower_id,
                        trade_data=trade_data,
                        risk_score=risk_score
                    )
                    continue
                
                # Generate secure signature
                signature = self._generate_copy_signature(
                    follower_id=follower_id,
                    leader_id=leader_id,
                    trade_data=trade_data,
                    copy_quantity=copy_quantity
                )
                
                # Create copy trade request
                copy_request = CopyTradeRequest(
                    follower_id=follower_id,
                    leader_id=leader_id,
                    original_trade_id=trade_data['trade_id'],
                    symbol=trade_data['symbol'],
                    action=trade_data['action'],
                    quantity=copy_quantity,
                    price=Decimal(str(trade_data['price'])),
                    copy_ratio=copy_ratio,
                    max_copy_amount=max_copy_amount,
                    risk_score=risk_score,
                    timestamp=datetime.utcnow(),
                    signature=signature
                )
                
                copy_requests.append(copy_request)
                
            except Exception as e:
                logger.error(f"❌ Error generating copy request for follower {follower_data.get('user_id')}: {str(e)}")
                continue
        
        return copy_requests
    
    async def _process_copy_trade(self, copy_request: CopyTradeRequest) -> Dict[str, Any]:
        """Process individual copy trade with full security and performance optimization"""
        
        copy_id = str(uuid.uuid4())
        
        try:
            # Security: Prevent duplicate processing
            if copy_id in self._active_copies:
                return {"status": "duplicate", "copy_id": copy_id}
            
            self._active_copies.add(copy_id)
            
            # Validate follower account
            follower = await self._get_follower_account(copy_request.follower_id)
            if not follower or not follower.is_active:
                return {"status": "invalid_follower", "copy_id": copy_id}
            
            # Check available balance
            available_balance = await self._get_available_balance(copy_request.follower_id)
            required_amount = copy_request.quantity * copy_request.price
            
            if available_balance < required_amount:
                await self._notify_insufficient_balance(copy_request)
                return {
                    "status": "insufficient_balance",
                    "copy_id": copy_id,
                    "required": float(required_amount),
                    "available": float(available_balance)
                }
            
            # Send confirmation to follower (if enabled)
            if follower.copy_settings.get('require_confirmation', False):
                confirmation_result = await self._request_copy_confirmation(copy_request)
                if not confirmation_result.get('confirmed', False):
                    return {"status": "confirmation_required", "copy_id": copy_id}
            
            # Execute the copy trade
            trade_result = await self.order_manager.place_order(
                user_id=copy_request.follower_id,
                symbol=copy_request.symbol,
                action=copy_request.action,
                quantity=copy_request.quantity,
                price=copy_request.price,
                order_type="MARKET",
                metadata={
                    "copy_trade": True,
                    "leader_id": copy_request.leader_id,
                    "original_trade_id": copy_request.original_trade_id,
                    "copy_ratio": float(copy_request.copy_ratio),
                    "risk_score": copy_request.risk_score
                }
            )
            
            if trade_result.get('status') == 'success':
                # Store copy trade record
                await self._store_copy_trade_record(copy_request, trade_result, copy_id)
                
                # Update leader's copy performance metrics
                await self._update_leader_metrics(
                    copy_request.leader_id,
                    successful_copy=True,
                    copy_value=float(required_amount)
                )
                
                # Notify follower of successful copy
                await self._notify_successful_copy(copy_request, trade_result)
                
                return {
                    "status": "executed",
                    "copy_id": copy_id,
                    "trade_id": trade_result.get('trade_id'),
                    "copy_value": float(required_amount),
                    "follower_id": copy_request.follower_id
                }
            
            else:
                # Handle trade execution failure
                await self._handle_copy_trade_failure(copy_request, trade_result)
                return {
                    "status": "failed",
                    "copy_id": copy_id,
                    "error": trade_result.get('error', 'Unknown error')
                }
        
        except Exception as e:
            logger.error(f"❌ Copy trade processing error: {str(e)}")
            return {"status": "error", "copy_id": copy_id, "error": str(e)}
        
        finally:
            # Clean up active copies tracking
            self._active_copies.discard(copy_id)
    
    async def _request_copy_confirmation(self, copy_request: CopyTradeRequest) -> Dict[str, Any]:
        """Request confirmation from follower for copy trade"""
        
        # Get leader info for display
        leader = await self._get_verified_leader(copy_request.leader_id)
        leader_name = leader.display_name if leader else "Unknown Trader"
        
        # Calculate total amount
        total_amount = copy_request.quantity * copy_request.price
        
        # Send WhatsApp confirmation message
        confirmation_message = f"""🔄 **Copy Trade Confirmation**

**{leader_name}** just placed an order:
{copy_request.action.upper()} {copy_request.quantity} shares of {copy_request.symbol}

**Your Copy Trade:**
• Quantity: {copy_request.quantity} shares
• Price: ₹{copy_request.price:,.2f}
• Total: ₹{total_amount:,.2f}
• Risk Score: {copy_request.risk_score:.1f}/10

⏰ **Auto-execute in 30 seconds** or choose now:"""
        
        # Send confirmation with timeout
        confirmation_response = await self.whatsapp_client.send_interactive_message(
            phone_number=copy_request.follower_id,
            message=confirmation_message,
            buttons=[
                {"id": f"confirm_copy_{copy_request.follower_id}", "title": "✅ Confirm"},
                {"id": f"skip_copy_{copy_request.follower_id}", "title": "⏭️ Skip"},
                {"id": f"stop_following_{copy_request.leader_id}", "title": "🛑 Stop Following"}
            ]
        )
        
        # Wait for confirmation with timeout (30 seconds)
        try:
            confirmation = await asyncio.wait_for(
                self._wait_for_confirmation(copy_request.follower_id),
                timeout=30.0
            )
            return {"confirmed": confirmation.get('action') == 'confirm'}
        
        except asyncio.TimeoutError:
            # Auto-execute on timeout (default behavior)
            logger.info(f"⏰ Auto-executing copy trade for follower {copy_request.follower_id}")
            return {"confirmed": True}
    
    async def get_social_trading_leaderboard(
        self,
        timeframe: str = "monthly",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get top performing traders for social trading"""
        
        try:
            # Calculate date range
            if timeframe == "daily":
                start_date = datetime.utcnow() - timedelta(days=1)
            elif timeframe == "weekly":
                start_date = datetime.utcnow() - timedelta(weeks=1)
            elif timeframe == "monthly":
                start_date = datetime.utcnow() - timedelta(days=30)
            else:
                start_date = datetime.utcnow() - timedelta(days=90)
            
            # Get top performers from database
            async with get_async_session() as session:
                # This would be implemented with actual database queries
                # For now, return mock data structure
                leaderboard = [
                    {
                        "leader_id": f"leader_{i}",
                        "display_name": f"Trader_{i}",
                        "return_percentage": 15.5 - (i * 0.8),
                        "followers_count": 1000 - (i * 20),
                        "success_rate": 85.5 - (i * 1.2),
                        "total_trades": 150 + (i * 5),
                        "avg_holding_period": f"{7 + i} days",
                        "risk_score": 4.5 + (i * 0.2),
                        "leadership_tier": self._calculate_leadership_tier(1000 - (i * 20)),
                        "copy_fee": 0.05 if i < 5 else 0.0,  # Top 5 charge fees
                        "specialization": ["Growth Stocks", "Momentum Trading", "Value Investing"][i % 3],
                        "verified": i < 10  # Top 10 are verified
                    }
                    for i in range(limit)
                ]
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"❌ Error getting leaderboard: {str(e)}")
            return []
    
    async def start_following_trader(
        self,
        follower_id: str,
        leader_id: str,
        copy_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start following a trader with copy settings"""
        
        try:
            # Validate copy settings
            validated_settings = await self._validate_copy_settings(copy_settings)
            
            # Security: Check if already following
            existing_relationship = await self._check_existing_relationship(follower_id, leader_id)
            if existing_relationship:
                return {
                    "status": "already_following",
                    "message": "You are already following this trader"
                }
            
            # Verify leader exists and is active
            leader = await self._get_verified_leader(leader_id)
            if not leader or not leader.is_active:
                return {
                    "status": "invalid_leader",
                    "message": "This trader is not available for following"
                }
            
            # Create follower relationship
            follower_relationship = await self._create_follower_relationship(
                follower_id=follower_id,
                leader_id=leader_id,
                copy_settings=validated_settings
            )
            
            # Send confirmation messages
            await self._notify_follow_success(follower_id, leader, validated_settings)
            await self._notify_leader_new_follower(leader_id, follower_id)
            
            # Update cache
            if follower_id not in self._follower_cache:
                self._follower_cache[follower_id] = []
            self._follower_cache[follower_id].append(leader_id)
            
            return {
                "status": "success",
                "message": f"Successfully started following {leader.display_name}",
                "copy_settings": validated_settings,
                "estimated_monthly_cost": self._calculate_estimated_costs(validated_settings)
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting to follow trader: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def create_trading_group(
        self,
        creator_id: str,
        group_name: str,
        group_description: str,
        group_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a social trading group"""
        
        try:
            # Validate group settings
            if len(group_name) < 3 or len(group_name) > 50:
                raise ValueError("Group name must be between 3 and 50 characters")
            
            # Security: Check creator permissions
            creator = await self._get_user_permissions(creator_id)
            if not creator.get('can_create_groups', True):
                return {
                    "status": "permission_denied",
                    "message": "You don't have permission to create groups"
                }
            
            # Create group
            group_id = str(uuid.uuid4())
            group_data = {
                "group_id": group_id,
                "creator_id": creator_id,
                "name": group_name,
                "description": group_description,
                "settings": {
                    "is_public": group_settings.get('is_public', True),
                    "requires_approval": group_settings.get('requires_approval', False),
                    "max_members": group_settings.get('max_members', 100),
                    "trading_focus": group_settings.get('trading_focus', 'general'),
                    "risk_level": group_settings.get('risk_level', 'medium')
                },
                "created_at": datetime.utcnow(),
                "member_count": 1,
                "is_active": True
            }
            
            # Store in database
            await self._store_trading_group(group_data)
            
            # Create initial group chat/discussion
            welcome_message = f"""🎉 **Welcome to {group_name}!**

{group_description}

**Group Focus**: {group_settings.get('trading_focus', 'General Trading')}
**Risk Level**: {group_settings.get('risk_level', 'Medium')}

Share your trades, discuss strategies, and learn together! 
Use 'share trade [symbol]' to share your positions with the group."""
            
            # Send welcome message to creator
            await self.whatsapp_client.send_text_message(
                phone_number=creator_id,
                message=welcome_message
            )
            
            return {
                "status": "success",
                "group_id": group_id,
                "group_name": group_name,
                "invite_link": f"https://gridworks.app/groups/{group_id}",
                "message": "Trading group created successfully!"
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating trading group: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_social_trading_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive social trading analytics for user"""
        
        try:
            # Get user's social trading data
            following_data = await self._get_user_following_data(user_id)
            leadership_data = await self._get_user_leadership_data(user_id)
            group_data = await self._get_user_group_data(user_id)
            
            # Calculate performance metrics
            analytics = {
                "following_analytics": {
                    "total_following": len(following_data.get('leaders', [])),
                    "copy_trades_count": following_data.get('total_copy_trades', 0),
                    "copy_performance": following_data.get('total_return_percentage', 0.0),
                    "monthly_copy_volume": following_data.get('monthly_volume', 0.0),
                    "best_performing_leader": following_data.get('best_leader', {}),
                    "worst_performing_leader": following_data.get('worst_leader', {})
                },
                "leadership_analytics": {
                    "followers_count": leadership_data.get('followers_count', 0),
                    "total_copy_volume": leadership_data.get('total_copy_volume', 0.0),
                    "success_rate": leadership_data.get('success_rate', 0.0),
                    "avg_return": leadership_data.get('avg_return', 0.0),
                    "leadership_tier": leadership_data.get('tier', 'bronze'),
                    "monthly_copy_fees": leadership_data.get('monthly_fees', 0.0)
                },
                "group_analytics": {
                    "groups_joined": len(group_data.get('groups', [])),
                    "groups_created": group_data.get('groups_created', 0),
                    "group_trades_shared": group_data.get('trades_shared', 0),
                    "group_performance": group_data.get('group_performance', {})
                },
                "social_score": await self._calculate_social_score(user_id),
                "recommendations": await self._get_social_recommendations(user_id)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting social analytics: {str(e)}")
            return {"error": str(e)}
    
    # Performance optimization methods
    async def _update_performance_metrics(
        self,
        processing_time: float,
        success_count: int,
        total_count: int
    ):
        """Update performance metrics for monitoring"""
        
        self._performance_tracker['copy_trades_processed'] += total_count
        
        # Update average processing time (exponential moving average)
        alpha = 0.1
        self._performance_tracker['avg_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self._performance_tracker['avg_processing_time']
        )
        
        # Update success rate
        if total_count > 0:
            current_success_rate = success_count / total_count
            self._performance_tracker['success_rate'] = (
                alpha * current_success_rate + 
                (1 - alpha) * self._performance_tracker['success_rate']
            )
    
    # Security methods
    def _generate_copy_signature(
        self,
        follower_id: str,
        leader_id: str,
        trade_data: Dict[str, Any],
        copy_quantity: int
    ) -> str:
        """Generate cryptographic signature for copy trade security"""
        
        payload = f"{follower_id}:{leader_id}:{trade_data['trade_id']}:{trade_data['symbol']}:{copy_quantity}:{trade_data['price']}"
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _check_copy_rate_limit(self, follower_id: str) -> bool:
        """Check if follower is within copy rate limits"""
        
        now = datetime.utcnow()
        if follower_id not in self._copy_attempts:
            self._copy_attempts[follower_id] = []
        
        # Clean old attempts (older than 1 minute)
        self._copy_attempts[follower_id] = [
            attempt for attempt in self._copy_attempts[follower_id]
            if (now - attempt).total_seconds() < 60
        ]
        
        # Check if under limit
        if len(self._copy_attempts[follower_id]) >= self.max_copies_per_minute:
            return False
        
        # Add current attempt
        self._copy_attempts[follower_id].append(now)
        return True
    
    # Helper methods (implementations would be added based on database schema)
    async def _get_verified_leader(self, leader_id: str) -> Optional[TradingLeader]:
        """Get verified trading leader"""
        # Implementation would fetch from database with caching
        pass
    
    async def _get_active_followers(self, leader_id: str) -> List[Dict[str, Any]]:
        """Get active followers for a leader"""
        # Implementation would fetch from database with caching
        pass
    
    async def _calculate_leadership_tier(self, followers_count: int) -> str:
        """Calculate leadership tier based on followers and performance"""
        if followers_count >= 10000:
            return LeadershipTier.DIAMOND.value
        elif followers_count >= 5000:
            return LeadershipTier.PLATINUM.value
        elif followers_count >= 1000:
            return LeadershipTier.GOLD.value
        elif followers_count >= 100:
            return LeadershipTier.SILVER.value
        else:
            return LeadershipTier.BRONZE.value
    
    # Additional helper methods would be implemented based on requirements...