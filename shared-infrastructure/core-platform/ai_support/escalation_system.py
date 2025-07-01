"""
Human Escalation System
Intelligent routing to human agents with tier-based priority
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import redis

from .models import (
    SupportMessage, SupportTier, AgentInfo, EscalationTicket,
    UserContext, UniversalQuery
)

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    BREAK = "break"


class EscalationReason(Enum):
    """Reasons for escalating to human agent"""
    LOW_CONFIDENCE = "low_confidence"
    COMPLEX_QUERY = "complex_query"
    USER_REQUEST = "user_request"
    AI_FAILURE = "ai_failure"
    COMPLAINT = "complaint"
    VIP_USER = "vip_user"


@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    total_queued: int
    average_wait_time: float
    longest_wait_time: float
    agents_available: int
    agents_busy: int
    resolution_rate: float


class HumanAgent:
    """Extended agent class with performance tracking"""
    
    def __init__(self, agent_data: Dict[str, Any]):
        self.agent_id = agent_data["agent_id"]
        self.name = agent_data["name"]
        self.tier_access = [SupportTier(tier) for tier in agent_data["tier_access"]]
        self.languages = agent_data["languages"]
        self.specializations = agent_data["specializations"]
        self.max_concurrent = agent_data.get("max_concurrent", 3)
        self.status = AgentStatus(agent_data.get("status", "available"))
        self.rating = agent_data.get("rating", 4.5)
        
        # Performance tracking
        self.current_load = 0
        self.total_resolved = 0
        self.average_resolution_time = 0.0
        self.last_activity = datetime.utcnow()
        self.shift_start = datetime.utcnow()
        self.shift_end = datetime.utcnow() + timedelta(hours=8)


class EscalationSystem:
    """Intelligent human agent routing and queue management"""
    
    def __init__(self):
        self.redis = redis.Redis(decode_responses=True)
        self.agents: Dict[str, HumanAgent] = {}
        
        # Queue configurations by tier
        self.queue_configs = {
            SupportTier.BLACK: {
                "max_wait_time": 60,  # 1 minute
                "auto_escalate_after": 30,
                "priority_weight": 10,
                "requires_senior_agent": True
            },
            SupportTier.ELITE: {
                "max_wait_time": 300,  # 5 minutes
                "auto_escalate_after": 180,
                "priority_weight": 8,
                "requires_senior_agent": True
            },
            SupportTier.PRO: {
                "max_wait_time": 1800,  # 30 minutes
                "auto_escalate_after": 900,
                "priority_weight": 6,
                "requires_senior_agent": False
            },
            SupportTier.LITE: {
                "max_wait_time": 7200,  # 2 hours
                "auto_escalate_after": 3600,
                "priority_weight": 4,
                "requires_senior_agent": False
            }
        }
        
        # Load initial agents
        asyncio.create_task(self._load_agents())
        
        # Start queue monitoring
        asyncio.create_task(self._monitor_queues())
    
    async def _load_agents(self):
        """Load agent configurations"""
        
        # Mock agent data (would come from database in production)
        mock_agents = [
            {
                "agent_id": "agent_black_001",
                "name": "Arjun Mehta",
                "tier_access": ["BLACK", "ELITE", "PRO", "LITE"],
                "languages": ["en", "hi"],
                "specializations": ["vip_service", "portfolio_management", "trading"],
                "max_concurrent": 2,
                "status": "available",
                "rating": 4.9
            },
            {
                "agent_id": "agent_elite_001", 
                "name": "Priya Sharma",
                "tier_access": ["ELITE", "PRO", "LITE"],
                "languages": ["en", "hi", "ta"],
                "specializations": ["portfolio_analysis", "trading", "kyc"],
                "max_concurrent": 3,
                "status": "available",
                "rating": 4.8
            },
            {
                "agent_id": "agent_pro_001",
                "name": "Vikram Singh",
                "tier_access": ["PRO", "LITE"],
                "languages": ["en", "hi", "pa"],
                "specializations": ["trading", "technical_support", "payments"],
                "max_concurrent": 4,
                "status": "available",
                "rating": 4.6
            },
            {
                "agent_id": "agent_lite_001",
                "name": "Rajesh Kumar",
                "tier_access": ["LITE"],
                "languages": ["en", "hi", "bn"],
                "specializations": ["basic_support", "kyc", "payments"],
                "max_concurrent": 5,
                "status": "available", 
                "rating": 4.4
            }
        ]
        
        for agent_data in mock_agents:
            agent = HumanAgent(agent_data)
            self.agents[agent.agent_id] = agent
        
        logger.info(f"Loaded {len(self.agents)} support agents")
    
    async def escalate_to_human(
        self,
        message: SupportMessage,
        ai_context: Dict[str, Any],
        reason: EscalationReason,
        category: str = "general"
    ) -> Dict[str, Any]:
        """Route message to appropriate human agent"""
        
        try:
            # Find best available agent
            agent = await self._find_best_agent(message, category)
            
            if agent:
                # Assign immediately
                ticket = await self._assign_to_agent(message, agent, ai_context, reason)
                
                # Notify agent
                await self._notify_agent(agent, ticket)
                
                # Send user confirmation
                await self._send_assignment_confirmation(message, agent, ticket)
                
                return {
                    "status": "assigned",
                    "agent": agent.name,
                    "agent_id": agent.agent_id,
                    "ticket_id": ticket.ticket_id,
                    "estimated_response": f"{self.queue_configs[message.user_tier]['max_wait_time'] // 60} minutes"
                }
            else:
                # Add to queue
                position = await self._add_to_queue(message, ai_context, reason, category)
                
                # Send queue confirmation
                await self._send_queue_confirmation(message, position)
                
                return {
                    "status": "queued",
                    "position": position,
                    "estimated_wait": await self._calculate_wait_time(message.user_tier, position)
                }
                
        except Exception as e:
            logger.error(f"Escalation failed: {e}")
            return {
                "status": "error",
                "message": "Escalation system unavailable"
            }
    
    async def _find_best_agent(
        self,
        message: SupportMessage,
        category: str
    ) -> Optional[HumanAgent]:
        """Find best available agent for user tier and requirements"""
        
        # Filter available agents
        available_agents = []
        
        for agent in self.agents.values():
            if (agent.status == AgentStatus.AVAILABLE and
                message.user_tier in agent.tier_access and
                message.language in agent.languages and
                agent.current_load < agent.max_concurrent):
                
                # Check specialization match
                if category in agent.specializations or "general" in agent.specializations:
                    available_agents.append(agent)
        
        if not available_agents:
            return None
        
        # Scoring algorithm for best agent
        def calculate_agent_score(agent: HumanAgent) -> float:
            score = 0.0
            
            # Tier compatibility (higher for exact tier match)
            if message.user_tier == SupportTier.BLACK and "vip_service" in agent.specializations:
                score += 10.0
            elif message.user_tier in agent.tier_access:
                score += 5.0
            
            # Language match
            if message.language in agent.languages:
                score += 3.0
            
            # Specialization match
            if category in agent.specializations:
                score += 4.0
            
            # Current load (prefer less busy agents)
            load_factor = 1.0 - (agent.current_load / agent.max_concurrent)
            score += load_factor * 2.0
            
            # Agent rating
            score += agent.rating
            
            # Priority for premium tiers
            tier_priority = {
                SupportTier.BLACK: 3.0,
                SupportTier.ELITE: 2.0,
                SupportTier.PRO: 1.0,
                SupportTier.LITE: 0.0
            }
            score += tier_priority.get(message.user_tier, 0.0)
            
            return score
        
        # Select best agent
        best_agent = max(available_agents, key=calculate_agent_score)
        return best_agent
    
    async def _assign_to_agent(
        self,
        message: SupportMessage,
        agent: HumanAgent,
        ai_context: Dict[str, Any],
        reason: EscalationReason
    ) -> EscalationTicket:
        """Assign ticket to specific agent"""
        
        # Create escalation ticket
        ticket = EscalationTicket(
            ticket_id=f"TM{int(time.time())}{message.user_tier.value[:1]}",
            user=message,
            ai_context=ai_context,
            assigned_agent=agent,
            priority=message.priority,
            created_at=datetime.utcnow(),
            estimated_resolution=datetime.utcnow() + timedelta(
                minutes=self.queue_configs[message.user_tier]["max_wait_time"] // 60
            ),
            status="assigned"
        )
        
        # Update agent load
        agent.current_load += 1
        agent.last_activity = datetime.utcnow()
        
        # Store ticket in Redis
        await self._store_ticket(ticket)
        
        logger.info(f"Assigned ticket {ticket.ticket_id} to agent {agent.name}")
        return ticket
    
    async def _add_to_queue(
        self,
        message: SupportMessage,
        ai_context: Dict[str, Any],
        reason: EscalationReason,
        category: str
    ) -> int:
        """Add message to tier-specific queue"""
        
        # Create queued ticket
        ticket = EscalationTicket(
            ticket_id=f"TM{int(time.time())}{message.user_tier.value[:1]}",
            user=message,
            ai_context=ai_context,
            assigned_agent=None,
            priority=message.priority,
            created_at=datetime.utcnow(),
            estimated_resolution=datetime.utcnow() + timedelta(
                minutes=self.queue_configs[message.user_tier]["max_wait_time"] // 60
            ),
            status="queued"
        )
        
        # Add to tier-specific queue
        queue_key = f"support_queue_{message.user_tier.value.lower()}"
        queue_data = {
            "ticket": asdict(ticket),
            "reason": reason.value,
            "category": category,
            "queued_at": time.time()
        }
        
        # Add with priority (BLACK goes first)
        priority_score = self.queue_configs[message.user_tier]["priority_weight"]
        await self.redis.zadd(queue_key, {json.dumps(queue_data): priority_score})
        
        # Get queue position
        position = await self.redis.zrank(queue_key, json.dumps(queue_data)) + 1
        
        logger.info(f"Added ticket {ticket.ticket_id} to queue position {position}")
        return position
    
    async def _notify_agent(self, agent: HumanAgent, ticket: EscalationTicket):
        """Send notification to assigned agent"""
        
        try:
            notification = {
                "type": "new_assignment",
                "ticket_id": ticket.ticket_id,
                "user_tier": ticket.user.user_tier.value,
                "user_phone": ticket.user.phone,
                "message": ticket.user.message,
                "priority": ticket.priority,
                "ai_context": ticket.ai_context,
                "estimated_resolution": ticket.estimated_resolution.isoformat()
            }
            
            # Send to agent's notification channel
            notification_key = f"agent_notifications:{agent.agent_id}"
            await self.redis.lpush(notification_key, json.dumps(notification))
            
            # Set expiry for notifications
            await self.redis.expire(notification_key, 3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Agent notification failed: {e}")
    
    async def _send_assignment_confirmation(
        self,
        message: SupportMessage,
        agent: HumanAgent,
        ticket: EscalationTicket
    ):
        """Send assignment confirmation to user"""
        
        tier_messages = {
            SupportTier.BLACK: f"◆ Your dedicated butler {agent.name} is taking over immediately. Ticket: {ticket.ticket_id}",
            SupportTier.ELITE: f"👑 Expert advisor {agent.name} is reviewing your case. Ticket: {ticket.ticket_id}",
            SupportTier.PRO: f"⚡ PRO specialist {agent.name} will assist you shortly. Ticket: {ticket.ticket_id}",
            SupportTier.LITE: f"Our support team will help you. Ticket: {ticket.ticket_id}"
        }
        
        confirmation = tier_messages.get(message.user_tier, tier_messages[SupportTier.LITE])
        
        # Would send via WhatsApp in production
        logger.info(f"Assignment confirmation: {confirmation}")
    
    async def _send_queue_confirmation(self, message: SupportMessage, position: int):
        """Send queue position confirmation to user"""
        
        wait_time = await self._calculate_wait_time(message.user_tier, position)
        
        tier_messages = {
            SupportTier.BLACK: f"◆ You're next in our exclusive queue. Butler available in {wait_time}",
            SupportTier.ELITE: f"👑 Position {position} in ELITE queue. Expert advisor in {wait_time}",
            SupportTier.PRO: f"⚡ Position {position} in PRO queue. Specialist in {wait_time}",
            SupportTier.LITE: f"Position {position} in queue. Support team available in {wait_time}"
        }
        
        confirmation = tier_messages.get(message.user_tier, tier_messages[SupportTier.LITE])
        
        # Would send via WhatsApp in production
        logger.info(f"Queue confirmation: {confirmation}")
    
    async def _calculate_wait_time(self, tier: SupportTier, position: int) -> str:
        """Calculate estimated wait time"""
        
        # Base time per position by tier
        time_per_position = {
            SupportTier.BLACK: 30,   # 30 seconds per position
            SupportTier.ELITE: 120,  # 2 minutes per position
            SupportTier.PRO: 300,    # 5 minutes per position
            SupportTier.LITE: 600    # 10 minutes per position
        }
        
        wait_seconds = time_per_position[tier] * position
        
        if wait_seconds < 60:
            return f"{wait_seconds} seconds"
        elif wait_seconds < 3600:
            return f"{wait_seconds // 60} minutes"
        else:
            return f"{wait_seconds // 3600} hours"
    
    async def _store_ticket(self, ticket: EscalationTicket):
        """Store ticket in Redis"""
        
        try:
            ticket_key = f"ticket:{ticket.ticket_id}"
            ticket_data = asdict(ticket)
            
            # Convert datetime objects to strings
            ticket_data["created_at"] = ticket.created_at.isoformat()
            ticket_data["estimated_resolution"] = ticket.estimated_resolution.isoformat()
            
            await self.redis.hset(ticket_key, mapping=ticket_data)
            await self.redis.expire(ticket_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Ticket storage failed: {e}")
    
    async def _monitor_queues(self):
        """Background queue monitoring and auto-escalation"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for tier in SupportTier:
                    await self._check_queue_sla(tier)
                    await self._auto_escalate_expired(tier)
                
            except Exception as e:
                logger.error(f"Queue monitoring error: {e}")
    
    async def _check_queue_sla(self, tier: SupportTier):
        """Check queue SLA compliance"""
        
        queue_key = f"support_queue_{tier.value.lower()}"
        queue_size = await self.redis.zcard(queue_key)
        
        if queue_size == 0:
            return
        
        config = self.queue_configs[tier]
        max_wait = config["max_wait_time"]
        
        # Get oldest item in queue
        oldest_items = await self.redis.zrange(queue_key, 0, 0, withscores=True)
        if oldest_items:
            oldest_data = json.loads(oldest_items[0][0])
            queued_at = oldest_data["queued_at"]
            wait_time = time.time() - queued_at
            
            if wait_time > max_wait:
                logger.warning(f"SLA breach for {tier.value}: {wait_time:.0f}s > {max_wait}s")
                await self._escalate_sla_breach(tier, oldest_data)
    
    async def _escalate_sla_breach(self, tier: SupportTier, queue_data: Dict[str, Any]):
        """Escalate SLA breach to management"""
        
        escalation = {
            "type": "sla_breach",
            "tier": tier.value,
            "ticket_id": queue_data["ticket"]["ticket_id"],
            "wait_time": time.time() - queue_data["queued_at"],
            "max_allowed": self.queue_configs[tier]["max_wait_time"],
            "timestamp": time.time()
        }
        
        # Send to management escalation queue
        await self.redis.lpush("sla_breaches", json.dumps(escalation))
        
        logger.error(f"SLA breach escalated: {escalation}")
    
    async def get_queue_metrics(self) -> Dict[str, QueueMetrics]:
        """Get queue performance metrics"""
        
        metrics = {}
        
        for tier in SupportTier:
            queue_key = f"support_queue_{tier.value.lower()}"
            queue_size = await self.redis.zcard(queue_key)
            
            # Calculate metrics (simplified)
            available_agents = sum(
                1 for agent in self.agents.values()
                if (agent.status == AgentStatus.AVAILABLE and
                    tier in agent.tier_access)
            )
            
            busy_agents = sum(
                1 for agent in self.agents.values()
                if (agent.status == AgentStatus.BUSY and
                    tier in agent.tier_access)
            )
            
            metrics[tier.value] = QueueMetrics(
                total_queued=queue_size,
                average_wait_time=0.0,  # Would calculate from historical data
                longest_wait_time=0.0,  # Would calculate from queue data
                agents_available=available_agents,
                agents_busy=busy_agents,
                resolution_rate=95.0    # Would calculate from ticket data
            )
        
        return metrics
    
    async def resolve_ticket(self, ticket_id: str, resolution: str, agent_id: str) -> bool:
        """Mark ticket as resolved"""
        
        try:
            # Get ticket
            ticket_key = f"ticket:{ticket_id}"
            ticket_data = await self.redis.hgetall(ticket_key)
            
            if not ticket_data:
                return False
            
            # Update agent load
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.current_load = max(0, agent.current_load - 1)
                agent.total_resolved += 1
            
            # Mark as resolved
            await self.redis.hset(ticket_key, "status", "resolved")
            await self.redis.hset(ticket_key, "resolution", resolution)
            await self.redis.hset(ticket_key, "resolved_at", datetime.utcnow().isoformat())
            
            logger.info(f"Ticket {ticket_id} resolved by agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ticket resolution failed: {e}")
            return False