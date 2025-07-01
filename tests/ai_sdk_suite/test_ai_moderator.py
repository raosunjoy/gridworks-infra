"""
Comprehensive Test Suite for AI Moderator Service
Tests Community-as-a-Service functionality with expert verification
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal

from app.ai_moderator.moderator_engine import (
    AIModerator,
    SpamDetector,
    ExpertVerificationEngine,
    GroupManager,
    PerformanceTracker,
    RevenueManager
)


class TestSpamDetector:
    """Test spam detection functionality"""
    
    @pytest.fixture
    def spam_detector(self):
        return SpamDetector()
    
    def test_detect_obvious_spam(self, spam_detector):
        """Test detection of obvious spam messages"""
        spam_messages = [
            "🔥🔥🔥 GUARANTEED PROFIT!!! Call now 9999999999 🔥🔥🔥",
            "Make ₹50,000 daily with our secret strategy! WhatsApp 8888888888",
            "FREE TIPS! SURE SHOT! 100% GUARANTEED! Contact immediately!"
        ]
        
        for message in spam_messages:
            result = spam_detector.analyze_message(message)
            assert result["is_spam"] is True
            assert result["confidence"] >= 0.9
            assert "promotional" in result["spam_indicators"]
    
    def test_detect_legitimate_messages(self, spam_detector):
        """Test legitimate trading messages are not flagged"""
        legitimate_messages = [
            "RELIANCE looking strong above 2450, watching for breakout",
            "Thanks for the TCS call, made good profit",
            "What's your view on banking sector after RBI policy?",
            "Stop loss hit on HDFC position, booking loss as planned"
        ]
        
        for message in legitimate_messages:
            result = spam_detector.analyze_message(message)
            assert result["is_spam"] is False
            assert result["confidence"] <= 0.3
    
    def test_detect_borderline_cases(self, spam_detector):
        """Test borderline cases with moderate confidence"""
        borderline_messages = [
            "Amazing returns this month! Check my track record",
            "Join my premium group for exclusive calls",
            "Contact me for stock recommendations"
        ]
        
        for message in borderline_messages:
            result = spam_detector.analyze_message(message)
            assert 0.3 < result["confidence"] < 0.7  # Moderate confidence
    
    def test_phone_number_detection(self, spam_detector):
        """Test phone number detection in spam"""
        message_with_phone = "Call me at 9876543210 for guaranteed profits"
        result = spam_detector.analyze_message(message_with_phone)
        
        assert result["is_spam"] is True
        assert "phone_number" in result["spam_indicators"]
        assert result["extracted_phone"] == "9876543210"
    
    def test_excessive_emojis_detection(self, spam_detector):
        """Test excessive emoji detection"""
        emoji_spam = "🔥💰📈🚀💎🔥💰📈🚀💎 SUPER PROFITS 🔥💰📈🚀💎🔥💰📈🚀💎"
        result = spam_detector.analyze_message(emoji_spam)
        
        assert result["is_spam"] is True
        assert "excessive_emojis" in result["spam_indicators"]
        assert result["emoji_count"] >= 10
    
    def test_repeated_text_detection(self, spam_detector):
        """Test detection of repeated text patterns"""
        repeated_text = "BUY BUY BUY NOW NOW NOW PROFIT PROFIT PROFIT"
        result = spam_detector.analyze_message(repeated_text)
        
        assert result["is_spam"] is True
        assert "repeated_text" in result["spam_indicators"]
    
    def test_update_spam_patterns(self, spam_detector):
        """Test updating spam detection patterns"""
        new_patterns = [
            r"\bcrypto\s+mining\b",
            r"\bget\s+rich\s+quick\b"
        ]
        
        spam_detector.update_spam_patterns(new_patterns)
        
        crypto_spam = "Join our crypto mining scheme for easy money"
        result = spam_detector.analyze_message(crypto_spam)
        
        assert result["is_spam"] is True
        assert "pattern_match" in result["spam_indicators"]


class TestExpertVerificationEngine:
    """Test expert verification and performance tracking"""
    
    @pytest.fixture
    def verification_engine(self):
        return ExpertVerificationEngine()
    
    def test_calculate_accuracy_score(self, verification_engine):
        """Test accuracy score calculation"""
        trade_calls = [
            {"prediction": "BUY", "entry_price": 2400, "actual_outcome": "profit", "return_pct": 5.2},
            {"prediction": "SELL", "entry_price": 1850, "actual_outcome": "profit", "return_pct": 3.1},
            {"prediction": "BUY", "entry_price": 3200, "actual_outcome": "loss", "return_pct": -2.5},
            {"prediction": "BUY", "entry_price": 1450, "actual_outcome": "profit", "return_pct": 8.7}
        ]
        
        accuracy = verification_engine.calculate_accuracy_score(trade_calls)
        
        assert accuracy["win_rate"] == 75.0  # 3 out of 4 profitable
        assert accuracy["average_return"] == pytest.approx(3.625, rel=1e-2)  # (5.2+3.1-2.5+8.7)/4
        assert accuracy["total_calls"] == 4
        assert accuracy["profitable_calls"] == 3
    
    def test_generate_zk_proof(self, verification_engine):
        """Test zero-knowledge proof generation for expert performance"""
        expert_data = {
            "expert_id": "expert_123",
            "win_rate": 73.5,
            "total_calls": 150,
            "average_return": 4.2,
            "period": "3_months"
        }
        
        zk_proof = verification_engine.generate_zk_proof(expert_data)
        
        assert zk_proof["expert_id"] == "expert_123"
        assert zk_proof["verified_performance"]["win_rate_range"] == "70-75%"  # Bucketed for privacy
        assert zk_proof["verified_performance"]["call_volume_range"] == "100-200"
        assert zk_proof["proof_hash"] is not None
        assert zk_proof["verification_timestamp"] is not None
        assert zk_proof["is_verified"] is True
    
    def test_verify_zk_proof(self, verification_engine):
        """Test verification of ZK proof"""
        # First generate a proof
        expert_data = {
            "expert_id": "expert_456",
            "win_rate": 68.2,
            "total_calls": 89,
            "average_return": 3.8
        }
        
        zk_proof = verification_engine.generate_zk_proof(expert_data)
        
        # Then verify it
        verification_result = verification_engine.verify_zk_proof(zk_proof)
        
        assert verification_result["is_valid"] is True
        assert verification_result["expert_verified"] is True
        assert "verification_details" in verification_result
    
    def test_expert_tier_classification(self, verification_engine):
        """Test expert tier classification based on performance"""
        # Bronze expert
        bronze_data = {"win_rate": 55.0, "total_calls": 25, "average_return": 2.1}
        bronze_tier = verification_engine.classify_expert_tier(bronze_data)
        assert bronze_tier["tier"] == "bronze"
        assert bronze_tier["revenue_share"] == 60  # 60% for bronze
        
        # Silver expert
        silver_data = {"win_rate": 65.0, "total_calls": 75, "average_return": 3.5}
        silver_tier = verification_engine.classify_expert_tier(silver_data)
        assert silver_tier["tier"] == "silver"
        assert silver_tier["revenue_share"] == 70  # 70% for silver
        
        # Gold expert
        gold_data = {"win_rate": 75.0, "total_calls": 150, "average_return": 5.2}
        gold_tier = verification_engine.classify_expert_tier(gold_data)
        assert gold_tier["tier"] == "gold"
        assert gold_tier["revenue_share"] == 80  # 80% for gold
        
        # Diamond expert
        diamond_data = {"win_rate": 85.0, "total_calls": 300, "average_return": 7.8}
        diamond_tier = verification_engine.classify_expert_tier(diamond_data)
        assert diamond_tier["tier"] == "diamond"
        assert diamond_tier["revenue_share"] == 85  # 85% for diamond
    
    def test_performance_tracking(self, verification_engine):
        """Test continuous performance tracking"""
        expert_id = "expert_789"
        
        # Add multiple trade calls over time
        calls = [
            {"symbol": "RELIANCE", "action": "BUY", "entry": 2400, "outcome": "profit", "return": 4.5},
            {"symbol": "TCS", "action": "SELL", "entry": 3600, "outcome": "profit", "return": 2.8},
            {"symbol": "HDFC", "action": "BUY", "entry": 1650, "outcome": "loss", "return": -1.5}
        ]
        
        for call in calls:
            verification_engine.track_trade_call(expert_id, call)
        
        performance = verification_engine.get_expert_performance(expert_id)
        
        assert performance["expert_id"] == expert_id
        assert performance["total_calls"] == 3
        assert performance["win_rate"] == pytest.approx(66.67, rel=1e-2)
        assert performance["average_return"] == pytest.approx(1.93, rel=1e-2)


class TestGroupManager:
    """Test expert group management functionality"""
    
    @pytest.fixture
    def group_manager(self):
        return GroupManager()
    
    @pytest.mark.asyncio
    async def test_create_expert_group(self, group_manager):
        """Test creating a new expert group"""
        group_config = {
            "name": "Pro Trading Signals",
            "description": "High-accuracy swing trading calls",
            "subscription_price": 1999,
            "max_members": 100,
            "expert_id": "expert_123",
            "category": "equity_trading"
        }
        
        result = await group_manager.create_expert_group(group_config)
        
        assert result["success"] is True
        assert result["group_id"] is not None
        assert result["group_config"]["name"] == "Pro Trading Signals"
        assert result["group_config"]["subscription_price"] == 1999
        assert result["moderation_enabled"] is True
        assert result["revenue_sharing_active"] is True
    
    @pytest.mark.asyncio
    async def test_moderate_group_message(self, group_manager):
        """Test message moderation in expert groups"""
        group_id = "group_123"
        message = {
            "user_id": "user_456",
            "content": "Great call on RELIANCE! Made 5% profit",
            "timestamp": datetime.now().isoformat()
        }
        
        result = await group_manager.moderate_message(group_id, message)
        
        assert result["action"] == "approve"
        assert result["spam_score"] < 0.3
        assert "moderation_reason" not in result  # Clean message
    
    @pytest.mark.asyncio
    async def test_moderate_spam_message(self, group_manager):
        """Test moderation of spam messages"""
        group_id = "group_123"
        spam_message = {
            "user_id": "spammer_789",
            "content": "🔥🔥 GUARANTEED PROFIT!!! Call 9999999999 🔥🔥",
            "timestamp": datetime.now().isoformat()
        }
        
        result = await group_manager.moderate_message(group_id, spam_message)
        
        assert result["action"] == "block"
        assert result["spam_score"] > 0.9
        assert "promotional" in result["moderation_reason"]
        assert result["auto_blocked"] is True
    
    @pytest.mark.asyncio
    async def test_add_member_to_group(self, group_manager):
        """Test adding members to expert groups"""
        group_id = "group_456"
        member_data = {
            "user_id": "new_member_123",
            "user_tier": "pro",
            "subscription_confirmed": True,
            "payment_method": "razorpay"
        }
        
        result = await group_manager.add_member(group_id, member_data)
        
        assert result["success"] is True
        assert result["member_id"] == "new_member_123"
        assert result["access_level"] == "full"
        assert result["subscription_active"] is True
    
    @pytest.mark.asyncio
    async def test_group_analytics(self, group_manager):
        """Test group analytics generation"""
        group_id = "group_789"
        
        analytics = await group_manager.get_group_analytics(group_id)
        
        assert "member_count" in analytics
        assert "engagement_metrics" in analytics
        assert "revenue_metrics" in analytics
        assert "expert_performance" in analytics
        assert "moderation_stats" in analytics
        
        # Check specific metrics
        assert analytics["engagement_metrics"]["daily_active_users"] >= 0
        assert analytics["revenue_metrics"]["monthly_revenue"] >= 0
        assert analytics["moderation_stats"]["spam_blocked_24h"] >= 0


class TestPerformanceTracker:
    """Test expert performance tracking system"""
    
    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()
    
    def test_record_trade_call(self, tracker):
        """Test recording trade calls"""
        trade_call = {
            "expert_id": "expert_123",
            "symbol": "RELIANCE",
            "action": "BUY",
            "entry_price": 2450,
            "target_price": 2550,
            "stop_loss": 2400,
            "reasoning": "Bullish breakout above resistance",
            "timeframe": "swing_trade",
            "confidence": 75
        }
        
        result = tracker.record_trade_call(trade_call)
        
        assert result["call_id"] is not None
        assert result["expert_id"] == "expert_123"
        assert result["status"] == "active"
        assert result["timestamp"] is not None
    
    def test_update_trade_outcome(self, tracker):
        """Test updating trade outcomes"""
        # First record a call
        trade_call = {
            "expert_id": "expert_456",
            "symbol": "TCS",
            "action": "SELL",
            "entry_price": 3600,
            "target_price": 3500,
            "stop_loss": 3650
        }
        
        call_result = tracker.record_trade_call(trade_call)
        call_id = call_result["call_id"]
        
        # Then update outcome
        outcome = {
            "call_id": call_id,
            "exit_price": 3520,
            "exit_reason": "target_reached",
            "return_percentage": 2.22,
            "outcome": "profit"
        }
        
        update_result = tracker.update_trade_outcome(outcome)
        
        assert update_result["success"] is True
        assert update_result["call_id"] == call_id
        assert update_result["final_return"] == 2.22
        assert update_result["status"] == "closed"
    
    def test_calculate_expert_metrics(self, tracker):
        """Test calculation of expert performance metrics"""
        expert_id = "expert_789"
        
        # Record multiple trades
        trades = [
            {"expert_id": expert_id, "symbol": "HDFC", "action": "BUY", "entry_price": 1650},
            {"expert_id": expert_id, "symbol": "ICICI", "action": "SELL", "entry_price": 950},
            {"expert_id": expert_id, "symbol": "SBI", "action": "BUY", "entry_price": 580}
        ]
        
        call_ids = []
        for trade in trades:
            result = tracker.record_trade_call(trade)
            call_ids.append(result["call_id"])
        
        # Update outcomes
        outcomes = [
            {"call_id": call_ids[0], "exit_price": 1700, "return_percentage": 3.03, "outcome": "profit"},
            {"call_id": call_ids[1], "exit_price": 920, "return_percentage": 3.16, "outcome": "profit"},
            {"call_id": call_ids[2], "exit_price": 565, "return_percentage": -2.59, "outcome": "loss"}
        ]
        
        for outcome in outcomes:
            tracker.update_trade_outcome(outcome)
        
        # Calculate metrics
        metrics = tracker.calculate_expert_metrics(expert_id)
        
        assert metrics["expert_id"] == expert_id
        assert metrics["total_calls"] == 3
        assert metrics["win_rate"] == pytest.approx(66.67, rel=1e-2)
        assert metrics["average_return"] == pytest.approx(1.2, rel=1e-2)
        assert metrics["profitable_calls"] == 2
        assert metrics["loss_calls"] == 1
    
    def test_get_leaderboard(self, tracker):
        """Test expert leaderboard generation"""
        leaderboard = tracker.get_expert_leaderboard(limit=10)
        
        assert len(leaderboard) <= 10
        
        if len(leaderboard) > 1:
            # Check if sorted by performance (win rate or average return)
            first_expert = leaderboard[0]
            second_expert = leaderboard[1]
            
            # First expert should have better or equal performance
            assert (first_expert["win_rate"] >= second_expert["win_rate"] or 
                   first_expert["average_return"] >= second_expert["average_return"])


class TestRevenueManager:
    """Test revenue management and sharing system"""
    
    @pytest.fixture
    def revenue_manager(self):
        return RevenueManager()
    
    def test_calculate_revenue_share(self, revenue_manager):
        """Test revenue share calculation"""
        group_revenue = {
            "group_id": "group_123",
            "monthly_revenue": 50000,  # ₹50,000
            "member_count": 25,
            "expert_tier": "gold"
        }
        
        shares = revenue_manager.calculate_revenue_share(group_revenue)
        
        assert shares["total_revenue"] == 50000
        assert shares["expert_share"] == 40000  # 80% for gold tier
        assert shares["platform_share"] == 10000  # 20% for platform
        assert shares["expert_percentage"] == 80
        assert shares["platform_percentage"] == 20
    
    def test_process_expert_payout(self, revenue_manager):
        """Test expert payout processing"""
        payout_data = {
            "expert_id": "expert_123",
            "group_id": "group_456",
            "revenue_amount": 75000,
            "expert_tier": "diamond",
            "period": "monthly",
            "bank_details": {
                "account_number": "1234567890",
                "ifsc": "HDFC0001234"
            }
        }
        
        result = revenue_manager.process_expert_payout(payout_data)
        
        assert result["success"] is True
        assert result["expert_payout"] == 63750  # 85% for diamond tier
        assert result["platform_fee"] == 11250  # 15% platform fee
        assert result["payout_id"] is not None
        assert result["status"] == "processed"
    
    def test_track_group_revenue(self, revenue_manager):
        """Test group revenue tracking"""
        revenue_event = {
            "group_id": "group_789",
            "event_type": "subscription",
            "amount": 1999,
            "user_id": "user_456",
            "payment_method": "upi",
            "timestamp": datetime.now().isoformat()
        }
        
        result = revenue_manager.track_revenue_event(revenue_event)
        
        assert result["success"] is True
        assert result["revenue_tracked"] == 1999
        assert result["group_id"] == "group_789"
        assert result["transaction_id"] is not None
    
    def test_generate_revenue_report(self, revenue_manager):
        """Test revenue report generation"""
        report_config = {
            "expert_id": "expert_123",
            "period": "monthly",
            "start_date": "2025-06-01",
            "end_date": "2025-06-30"
        }
        
        report = revenue_manager.generate_revenue_report(report_config)
        
        assert "expert_id" in report
        assert "total_revenue" in report
        assert "expert_earnings" in report
        assert "platform_fees" in report
        assert "group_breakdown" in report
        assert "payment_summary" in report
        
        # Verify calculations
        total_revenue = report["total_revenue"]
        expert_earnings = report["expert_earnings"]
        platform_fees = report["platform_fees"]
        
        assert total_revenue == expert_earnings + platform_fees


class TestAIModerator:
    """Test main AI Moderator service class"""
    
    @pytest.fixture
    def ai_moderator(self):
        return AIModerator()
    
    @pytest.mark.asyncio
    async def test_create_expert_group_flow(self, ai_moderator):
        """Test complete expert group creation flow"""
        group_request = {
            "expert_id": "expert_123",
            "group_config": {
                "name": "Elite Trading Signals",
                "description": "Premium swing trading calls with 75%+ accuracy",
                "subscription_price": 2999,
                "max_members": 50,
                "category": "swing_trading"
            },
            "expert_verification": {
                "win_rate": 76.5,
                "total_calls": 200,
                "average_return": 4.8
            }
        }
        
        result = await ai_moderator.create_expert_group(group_request)
        
        assert result["success"] is True
        assert result["group_id"] is not None
        assert result["expert_verified"] is True
        assert result["expert_tier"] == "gold"  # Based on performance
        assert result["revenue_share"] == 80  # Gold tier gets 80%
        assert result["moderation_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_moderate_group_activity(self, ai_moderator):
        """Test group activity moderation"""
        moderation_request = {
            "group_id": "group_123",
            "activity_type": "message",
            "content": {
                "user_id": "user_456",
                "message": "Thanks for the HDFC call! Made good profit",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        result = await ai_moderator.moderate_group_activity(moderation_request)
        
        assert result["action"] == "approve"
        assert result["confidence"] > 0.8
        assert result["spam_detected"] is False
    
    @pytest.mark.asyncio
    async def test_verify_expert_performance(self, ai_moderator):
        """Test expert performance verification"""
        verification_request = {
            "expert_id": "expert_456",
            "trade_history": [
                {"symbol": "RELIANCE", "action": "BUY", "entry": 2400, "exit": 2520, "return": 5.0},
                {"symbol": "TCS", "action": "SELL", "entry": 3600, "exit": 3480, "return": 3.33},
                {"symbol": "HDFC", "action": "BUY", "entry": 1650, "exit": 1590, "return": -3.64}
            ],
            "verification_period": "3_months"
        }
        
        result = await ai_moderator.verify_expert_performance(verification_request)
        
        assert result["verification_successful"] is True
        assert result["expert_metrics"]["win_rate"] == pytest.approx(66.67, rel=1e-2)
        assert result["expert_metrics"]["average_return"] > 0
        assert result["zk_proof"]["is_verified"] is True
        assert result["expert_tier"] in ["bronze", "silver", "gold", "diamond"]
    
    @pytest.mark.asyncio
    async def test_process_revenue_sharing(self, ai_moderator):
        """Test revenue sharing processing"""
        revenue_request = {
            "group_id": "group_789",
            "revenue_period": "monthly",
            "total_revenue": 125000,
            "expert_id": "expert_789",
            "expert_tier": "silver"
        }
        
        result = await ai_moderator.process_revenue_sharing(revenue_request)
        
        assert result["success"] is True
        assert result["expert_payout"] == 87500  # 70% for silver tier
        assert result["platform_revenue"] == 37500  # 30% for platform
        assert result["payout_scheduled"] is True
    
    @pytest.mark.asyncio
    async def test_get_group_analytics(self, ai_moderator):
        """Test comprehensive group analytics"""
        analytics_request = {
            "group_id": "group_456",
            "period": "weekly"
        }
        
        result = await ai_moderator.get_group_analytics(analytics_request)
        
        assert result["success"] is True
        assert "member_engagement" in result["analytics"]
        assert "revenue_metrics" in result["analytics"]
        assert "expert_performance" in result["analytics"]
        assert "moderation_stats" in result["analytics"]
        
        # Check key metrics
        assert "daily_active_members" in result["analytics"]["member_engagement"]
        assert "message_volume" in result["analytics"]["member_engagement"]
        assert "subscription_revenue" in result["analytics"]["revenue_metrics"]
        assert "spam_blocked" in result["analytics"]["moderation_stats"]
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, ai_moderator):
        """Test service health status"""
        status = await ai_moderator.get_health_status()
        
        assert status["status"] in ["healthy", "degraded", "unhealthy"]
        assert "uptime" in status
        assert "service_metrics" in status
        assert "active_groups" in status["service_metrics"]
        assert "total_experts" in status["service_metrics"]
        assert "messages_moderated_24h" in status["service_metrics"]
    
    @pytest.mark.asyncio
    async def test_shutdown(self, ai_moderator):
        """Test service shutdown"""
        await ai_moderator.shutdown()
        
        # Verify cleanup happens properly


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def ai_moderator(self):
        return AIModerator()
    
    @pytest.mark.asyncio
    async def test_invalid_expert_verification(self, ai_moderator):
        """Test handling of invalid expert verification data"""
        invalid_request = {
            "expert_id": "invalid_expert",
            "trade_history": [],  # Empty history
            "verification_period": "invalid_period"
        }
        
        result = await ai_moderator.verify_expert_performance(invalid_request)
        
        assert result["verification_successful"] is False
        assert "error" in result
        assert "insufficient_data" in result["error"]
    
    @pytest.mark.asyncio
    async def test_spam_detection_edge_cases(self, ai_moderator):
        """Test spam detection with edge cases"""
        edge_cases = [
            "",  # Empty message
            "a" * 5000,  # Very long message
            "🔥" * 100,  # Only emojis
            "123456789" * 50,  # Only numbers
        ]
        
        for message in edge_cases:
            moderation_request = {
                "group_id": "group_test",
                "activity_type": "message",
                "content": {
                    "user_id": "test_user",
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            result = await ai_moderator.moderate_group_activity(moderation_request)
            
            # Should handle gracefully without crashing
            assert "action" in result
            assert result["action"] in ["approve", "flag", "block"]
    
    @pytest.mark.asyncio
    async def test_concurrent_moderation_requests(self, ai_moderator):
        """Test handling concurrent moderation requests"""
        requests = []
        for i in range(10):
            request = {
                "group_id": f"group_{i}",
                "activity_type": "message",
                "content": {
                    "user_id": f"user_{i}",
                    "message": f"Test message {i}",
                    "timestamp": datetime.now().isoformat()
                }
            }
            requests.append(ai_moderator.moderate_group_activity(request))
        
        results = await asyncio.gather(*requests)
        
        # All requests should complete successfully
        assert len(results) == 10
        for result in results:
            assert "action" in result
            assert result["action"] in ["approve", "flag", "block"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])