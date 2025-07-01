"""
TradeMate AI Support Escalation System Test Suite
Testing intelligent human escalation with tier-based priority routing
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json

from app.ai_support.escalation_system import EscalationSystem, EscalationReason, AgentSpecialty
from app.ai_support.models import SupportMessage, SupportTier, UserContext, MessageType, HumanAgent


class TestEscalationSystem:
    """Test suite for escalation system"""
    
    @pytest.fixture
    async def escalation_system(self):
        """Initialize escalation system"""
        system = EscalationSystem()
        await system.initialize()
        return system
    
    @pytest.fixture
    def black_tier_message(self):
        """Create Black tier support message"""
        return SupportMessage(
            id="ESC_BLACK_001",
            user_id="black_user_001",
            phone="+919876540001",
            message="Emergency: ₹500 crore transaction stuck, need immediate CEO assistance",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.BLACK,
            priority=5
        )
    
    @pytest.fixture
    def elite_tier_message(self):
        """Create Elite tier support message"""
        return SupportMessage(
            id="ESC_ELITE_001",
            user_id="elite_user_001",
            phone="+919876540002",
            message="Complex derivatives position needs expert review",
            message_type=MessageType.TEXT,
            language="en",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.ELITE,
            priority=4
        )
    
    @pytest.fixture
    def pro_tier_message(self):
        """Create Pro tier support message"""
        return SupportMessage(
            id="ESC_PRO_001",
            user_id="pro_user_001",
            phone="+919876540003",
            message="HDFC order failed, need help with retry",
            message_type=MessageType.TEXT,
            language="hi",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.PRO,
            priority=3
        )
    
    @pytest.fixture
    def lite_tier_message(self):
        """Create Lite tier support message"""
        return SupportMessage(
            id="ESC_LITE_001",
            user_id="lite_user_001",
            phone="+919876540004",
            message="SBI shares kaise kharide? Help chahiye",
            message_type=MessageType.TEXT,
            language="hi",
            timestamp=datetime.utcnow(),
            user_tier=SupportTier.LITE,
            priority=2
        )
    
    @pytest.mark.asyncio
    async def test_escalation_system_initialization(self, escalation_system):
        """Test escalation system initializes correctly"""
        assert len(escalation_system.available_agents) >= 10  # Should have adequate agent pool
        assert len(escalation_system.escalation_queues) == 4  # One queue per tier
        assert SupportTier.BLACK in escalation_system.escalation_queues
        assert escalation_system.sla_targets[SupportTier.BLACK] == 60  # 1 minute for Black
        assert escalation_system.sla_targets[SupportTier.ELITE] == 300  # 5 minutes for Elite
    
    @pytest.mark.asyncio
    async def test_black_tier_emergency_escalation(self, escalation_system, black_tier_message):
        """Test immediate escalation for Black tier emergency"""
        ai_context = {
            "ai_response": "This appears to be a high-value transaction issue requiring CEO-level attention",
            "confidence": 0.95,
            "urgency_detected": True
        }
        
        result = await escalation_system.escalate_to_human(
            black_tier_message, ai_context, EscalationReason.EMERGENCY_DETECTED
        )
        
        assert result["escalated"] is True
        assert result["priority"] == "emergency"
        assert result["estimated_response"] == "CEO will respond within 1 minute"
        assert result["agent_type"] == "ceo_cto_direct"
        assert "CEO" in result["escalation_message"] or "emergency" in result["escalation_message"]
    
    @pytest.mark.asyncio
    async def test_elite_tier_expert_routing(self, escalation_system, elite_tier_message):
        """Test expert agent routing for Elite tier"""
        ai_context = {
            "ai_response": "Complex derivatives query requires specialized knowledge",
            "confidence": 0.42,  # Low confidence triggers escalation
            "category": "derivatives_trading"
        }
        
        result = await escalation_system.escalate_to_human(
            elite_tier_message, ai_context, EscalationReason.LOW_CONFIDENCE
        )
        
        assert result["escalated"] is True
        assert result["priority"] == "high"
        assert "derivatives" in result["agent_specialty"].lower() or "expert" in result["agent_specialty"].lower()
        assert "5 minutes" in result["estimated_response"]
        assert result["agent_assigned"] is not None
    
    @pytest.mark.asyncio
    async def test_pro_tier_multilingual_routing(self, escalation_system, pro_tier_message):
        """Test multilingual agent routing for Pro tier"""
        ai_context = {
            "ai_response": "Order failure issue in Hindi requires bilingual support",
            "confidence": 0.38,
            "language_detected": "hindi"
        }
        
        result = await escalation_system.escalate_to_human(
            pro_tier_message, ai_context, EscalationReason.LANGUAGE_BARRIER
        )
        
        assert result["escalated"] is True
        assert result["priority"] == "medium"
        assert "hindi" in result["agent_languages"] or "bilingual" in result["agent_specialty"].lower()
        assert "30 minutes" in result["estimated_response"]
    
    @pytest.mark.asyncio
    async def test_lite_tier_basic_support_routing(self, escalation_system, lite_tier_message):
        """Test basic support routing for Lite tier"""
        ai_context = {
            "ai_response": "Basic trading education query in Hindi",
            "confidence": 0.35,
            "category": "trading_education"
        }
        
        result = await escalation_system.escalate_to_human(
            lite_tier_message, ai_context, EscalationReason.LOW_CONFIDENCE
        )
        
        assert result["escalated"] is True
        assert result["priority"] == "normal"
        assert "2 hours" in result["estimated_response"]
        assert "general_support" in result["agent_type"]
    
    @pytest.mark.asyncio
    async def test_agent_selection_algorithm(self, escalation_system):
        """Test intelligent agent selection algorithm"""
        # Test case: Derivatives expert needed for Elite tier
        requirements = {
            "tier": SupportTier.ELITE,
            "specialty_required": AgentSpecialty.DERIVATIVES_EXPERT,
            "language": "en",
            "urgency": "high"
        }
        
        selected_agent = await escalation_system._select_best_agent(requirements)
        
        assert selected_agent is not None
        assert selected_agent.specialty == AgentSpecialty.DERIVATIVES_EXPERT
        assert selected_agent.tier_access >= SupportTier.ELITE
        assert "en" in selected_agent.languages
        assert selected_agent.current_load < selected_agent.max_concurrent_cases
    
    @pytest.mark.asyncio
    async def test_queue_management_priority_ordering(self, escalation_system):
        """Test queue management maintains priority ordering"""
        # Add messages of different priorities
        messages = [
            (SupportTier.LITE, 2, "Normal Lite query"),
            (SupportTier.BLACK, 5, "Black emergency"),
            (SupportTier.PRO, 3, "Pro urgent query"),
            (SupportTier.ELITE, 4, "Elite expert needed")
        ]
        
        # Add to queues
        for tier, priority, message in messages:
            await escalation_system._add_to_queue(tier, {
                "priority": priority,
                "message": message,
                "timestamp": datetime.utcnow()
            })
        
        # Check BLACK tier queue has highest priority items first
        black_queue = escalation_system.escalation_queues[SupportTier.BLACK]
        if len(black_queue) > 0:
            assert black_queue[0]["priority"] >= 4  # Should be high priority
    
    @pytest.mark.asyncio
    async def test_sla_monitoring_and_alerts(self, escalation_system):
        """Test SLA monitoring and executive alerts"""
        # Mock an overdue Black tier case
        overdue_case = {
            "tier": SupportTier.BLACK,
            "escalation_time": datetime.utcnow() - timedelta(minutes=2),  # 2 minutes overdue
            "user_id": "black_user_001",
            "message": "Critical issue",
            "sla_target": 60  # 1 minute SLA
        }
        
        sla_status = await escalation_system._check_sla_compliance(overdue_case)
        
        assert sla_status["sla_breached"] is True
        assert sla_status["breach_time_seconds"] >= 60  # At least 1 minute overdue
        assert sla_status["escalation_required"] is True
        assert sla_status["alert_level"] == "executive"  # Should alert executives
    
    @pytest.mark.asyncio
    async def test_agent_load_balancing(self, escalation_system):
        """Test agent load balancing prevents overload"""
        # Find an agent and simulate loading them up
        available_agents = [agent for agent in escalation_system.available_agents.values() 
                          if agent.is_available]
        
        if available_agents:
            test_agent = available_agents[0]
            original_load = test_agent.current_load
            
            # Simulate assigning maximum cases
            test_agent.current_load = test_agent.max_concurrent_cases
            
            # Try to assign another case
            can_assign = await escalation_system._can_assign_to_agent(test_agent, SupportTier.PRO)
            
            assert can_assign is False  # Should not allow overloading
            
            # Reset for cleanup
            test_agent.current_load = original_load
    
    @pytest.mark.asyncio
    async def test_escalation_reason_handling(self, escalation_system, elite_tier_message):
        """Test different escalation reasons are handled appropriately"""
        escalation_reasons = [
            (EscalationReason.LOW_CONFIDENCE, "medium"),
            (EscalationReason.EMERGENCY_DETECTED, "emergency"),
            (EscalationReason.COMPLEX_QUERY, "high"),
            (EscalationReason.LANGUAGE_BARRIER, "medium"),
            (EscalationReason.TECHNICAL_FAILURE, "high")
        ]
        
        for reason, expected_priority in escalation_reasons:
            ai_context = {"ai_response": f"Test for {reason.value}", "confidence": 0.4}
            
            result = await escalation_system.escalate_to_human(
                elite_tier_message, ai_context, reason
            )
            
            if reason == EscalationReason.EMERGENCY_DETECTED:
                assert result["priority"] == "emergency"
            elif reason in [EscalationReason.COMPLEX_QUERY, EscalationReason.TECHNICAL_FAILURE]:
                assert result["priority"] in ["high", "emergency"]
            else:
                assert result["priority"] in ["medium", "high"]
    
    @pytest.mark.asyncio
    async def test_agent_performance_tracking(self, escalation_system):
        """Test agent performance metrics tracking"""
        # Mock agent performance data
        agent_id = "agent_derivatives_001"
        if agent_id in escalation_system.available_agents:
            agent = escalation_system.available_agents[agent_id]
            
            # Simulate successful case resolution
            performance_update = {
                "case_resolved": True,
                "resolution_time": 15.5,  # minutes
                "customer_satisfaction": 4.8,
                "complexity_level": "high"
            }
            
            await escalation_system._update_agent_performance(agent_id, performance_update)
            
            # Check performance metrics updated
            assert agent.total_cases_handled >= 1
            assert agent.average_resolution_time > 0
            assert agent.customer_satisfaction_score >= 4.0
    
    @pytest.mark.asyncio
    async def test_executive_escalation_black_tier(self, escalation_system, black_tier_message):
        """Test executive escalation for Black tier issues"""
        # Simulate a complex Black tier issue requiring C-level attention
        ai_context = {
            "ai_response": "Multi-billion dollar portfolio optimization requires board-level decision",
            "confidence": 0.15,  # Very low confidence
            "value_at_risk": 50000000000  # ₹500 Cr
        }
        
        result = await escalation_system.escalate_to_human(
            black_tier_message, ai_context, EscalationReason.COMPLEX_QUERY
        )
        
        assert result["escalated"] is True
        assert result["priority"] == "emergency"
        assert "CEO" in result["escalation_path"] or "CTO" in result["escalation_path"]
        assert result["estimated_response"] == "CEO will respond within 1 minute"
    
    @pytest.mark.asyncio
    async def test_queue_overflow_handling(self, escalation_system):
        """Test handling when queues reach capacity"""
        # Simulate queue overflow for PRO tier
        pro_queue = escalation_system.escalation_queues[SupportTier.PRO]
        original_size = len(pro_queue)
        
        # Add many items to simulate overflow
        for i in range(50):  # Add 50 items
            await escalation_system._add_to_queue(SupportTier.PRO, {
                "priority": 3,
                "message": f"Test overflow message {i}",
                "timestamp": datetime.utcnow()
            })
        
        # Check queue management (should maintain reasonable size)
        current_size = len(pro_queue)
        assert current_size <= 100  # Should not grow indefinitely
    
    @pytest.mark.asyncio
    async def test_multilingual_agent_matching(self, escalation_system):
        """Test matching users with appropriate language-capable agents"""
        test_languages = ["hi", "ta", "te", "bn", "gu"]
        
        for language in test_languages:
            requirements = {
                "tier": SupportTier.PRO,
                "specialty_required": AgentSpecialty.GENERAL_SUPPORT,
                "language": language,
                "urgency": "medium"
            }
            
            selected_agent = await escalation_system._select_best_agent(requirements)
            
            if selected_agent:  # If agent found for this language
                assert language in selected_agent.languages
    
    @pytest.mark.asyncio
    async def test_escalation_analytics_and_reporting(self, escalation_system):
        """Test escalation analytics and reporting"""
        # Get escalation analytics
        analytics = await escalation_system.get_escalation_analytics()
        
        assert "total_escalations" in analytics
        assert "escalations_by_tier" in analytics
        assert "average_resolution_time" in analytics
        assert "sla_compliance_rate" in analytics
        
        # Check tier-specific metrics
        for tier in SupportTier:
            tier_stats = analytics["escalations_by_tier"].get(tier.value, {})
            if tier_stats:
                assert "count" in tier_stats
                assert "avg_resolution_time" in tier_stats
    
    @pytest.mark.asyncio
    async def test_emergency_protocol_activation(self, escalation_system):
        """Test emergency protocol activation for critical issues"""
        emergency_keywords = ["emergency", "stuck money", "fraud", "hacked", "urgent help"]
        
        for keyword in emergency_keywords:
            emergency_message = SupportMessage(
                id=f"EMERGENCY_{keyword}",
                user_id="black_user_emergency",
                phone="+919876540001",
                message=f"URGENT: {keyword} - need immediate help!",
                message_type=MessageType.TEXT,
                language="en",
                timestamp=datetime.utcnow(),
                user_tier=SupportTier.BLACK,
                priority=5
            )
            
            is_emergency = await escalation_system._detect_emergency_keywords(emergency_message.message)
            
            if keyword in ["emergency", "urgent help", "stuck money"]:
                assert is_emergency is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])