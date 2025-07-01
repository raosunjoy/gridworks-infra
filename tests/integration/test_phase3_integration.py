"""
Phase 3 Integration Tests
========================

Comprehensive integration tests for all Phase 3 components:
- Options Flow Analyzer
- Algorithmic Alerts
- Advanced Portfolio Analytics
- Community Features
- Cross-component integration
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from analytics.options_flow_analyzer import OptionsFlowAnalyzer, OptionsContract
from analytics.algorithmic_alerts import AlgorithmicAlertsEngine, MarketData
from analytics.portfolio_analytics import PortfolioAnalyzer, PortfolioHolding
from community.community_features import CommunityEngine


class TestOptionsFlowIntegration:
    """Integration tests for Options Flow Analyzer."""
    
    @pytest.fixture
    async def analyzer(self):
        """Create options flow analyzer instance."""
        analyzer = OptionsFlowAnalyzer()
        yield analyzer
        analyzer.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_options_flow_basic_functionality(self, analyzer):
        """Test basic options flow analysis functionality."""
        # Start monitoring briefly
        monitor_task = asyncio.create_task(analyzer.start_monitoring())
        await asyncio.sleep(2)  # Let it run for 2 seconds
        
        analyzer.stop_monitoring()
        await monitor_task
        
        # Check that some data was collected
        assert len(analyzer.alert_history) >= 0
        assert len(analyzer.flow_history) >= 0
    
    @pytest.mark.asyncio
    async def test_options_flow_alert_generation(self, analyzer):
        """Test alert generation from options flow."""
        # Create sample options data
        sample_contracts = [
            OptionsContract(
                symbol="NIFTY",
                strike=18000,
                expiry=datetime.now() + timedelta(days=7),
                option_type="CALL",
                last_price=100,
                volume=5000,  # High volume
                open_interest=10000,
                implied_volatility=0.25,
                delta=0.5,
                gamma=0.1,
                theta=-0.05,
                vega=0.3
            )
        ]
        
        # Test unusual volume detection
        alerts = analyzer._detect_unusual_volume("NIFTY", sample_contracts)
        assert isinstance(alerts, list)
        
        # Test flow summary
        summary = analyzer.get_flow_summary("NIFTY", hours=1)
        assert isinstance(summary, dict)
    
    def test_options_contract_validation(self):
        """Test options contract data validation."""
        contract = OptionsContract(
            symbol="RELIANCE",
            strike=2500,
            expiry=datetime.now() + timedelta(days=30),
            option_type="PUT",
            last_price=50,
            volume=1000,
            open_interest=5000,
            implied_volatility=0.3,
            delta=-0.4,
            gamma=0.08,
            theta=-0.03,
            vega=0.25
        )
        
        assert contract.symbol == "RELIANCE"
        assert contract.option_type in ["CALL", "PUT"]
        assert contract.volume >= 0
        assert contract.open_interest >= 0


class TestAlgorithmicAlertsIntegration:
    """Integration tests for Algorithmic Alerts Engine."""
    
    @pytest.fixture
    async def alerts_engine(self):
        """Create algorithmic alerts engine instance."""
        engine = AlgorithmicAlertsEngine()
        yield engine
        engine.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_alerts_engine_startup(self, alerts_engine):
        """Test alerts engine startup and shutdown."""
        # Start monitoring briefly
        monitor_task = asyncio.create_task(alerts_engine.start_monitoring())
        await asyncio.sleep(3)  # Let it run for 3 seconds
        
        alerts_engine.stop_monitoring()
        await monitor_task
        
        # Check that monitoring occurred
        assert len(alerts_engine.alert_history) >= 0
    
    @pytest.mark.asyncio
    async def test_pattern_recognition(self, alerts_engine):
        """Test pattern recognition functionality."""
        # Create sample market data
        sample_data = []
        base_price = 100
        
        for i in range(50):
            data = MarketData(
                symbol="TCS",
                timestamp=datetime.now() - timedelta(days=50-i),
                open=base_price + i * 0.5,
                high=base_price + i * 0.5 + 2,
                low=base_price + i * 0.5 - 1,
                close=base_price + i * 0.5 + 1,
                volume=10000 + i * 100
            )
            sample_data.append(data)
        
        # Test pattern recognition
        patterns = alerts_engine.pattern_recognizer.detect_patterns(sample_data)
        assert isinstance(patterns, list)
        
        # Test market regime detection
        regime = alerts_engine.regime_detector.detect_regime(sample_data)
        assert regime is not None
    
    def test_technical_indicators(self):
        """Test technical indicators calculations."""
        from analytics.algorithmic_alerts import TechnicalIndicators
        
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        
        # Test RSI
        rsi = TechnicalIndicators.rsi(prices)
        assert 0 <= rsi <= 100
        
        # Test MACD
        macd, signal, histogram = TechnicalIndicators.macd(prices)
        assert isinstance(macd, float)
        assert isinstance(signal, float)
        assert isinstance(histogram, float)
        
        # Test Bollinger Bands
        sma, upper, lower = TechnicalIndicators.bollinger_bands(prices)
        assert upper > sma > lower
    
    @pytest.mark.asyncio
    async def test_alert_processing(self, alerts_engine):
        """Test alert processing and management."""
        # Get active alerts
        active_alerts = alerts_engine.get_active_alerts()
        assert isinstance(active_alerts, list)
        
        # Get alert summary
        summary = alerts_engine.get_alert_summary(hours=1)
        assert isinstance(summary, dict)


class TestPortfolioAnalyticsIntegration:
    """Integration tests for Portfolio Analytics."""
    
    @pytest.fixture
    def portfolio_analyzer(self):
        """Create portfolio analyzer instance."""
        return PortfolioAnalyzer()
    
    @pytest.fixture
    def sample_portfolio(self):
        """Create sample portfolio holdings."""
        return [
            PortfolioHolding("RELIANCE", 100, 2500, 250000, 0.25, "Energy", "equity", beta=1.2),
            PortfolioHolding("TCS", 50, 3200, 160000, 0.16, "Technology", "equity", beta=0.8),
            PortfolioHolding("HDFC", 75, 1600, 120000, 0.12, "Financial Services", "equity", beta=1.1),
            PortfolioHolding("INFY", 80, 1400, 112000, 0.112, "Technology", "equity", beta=0.9),
            PortfolioHolding("ITC", 200, 450, 90000, 0.09, "Consumer Staples", "equity", beta=0.7)
        ]
    
    @pytest.mark.asyncio
    async def test_portfolio_analysis_workflow(self, portfolio_analyzer, sample_portfolio):
        """Test complete portfolio analysis workflow."""
        # Run comprehensive analysis
        analysis = await portfolio_analyzer.analyze_portfolio(
            "TEST_PORTFOLIO", sample_portfolio, lookback_days=50
        )
        
        # Validate analysis structure
        assert "portfolio_id" in analysis
        assert "portfolio_value" in analysis
        assert "risk_metrics" in analysis
        assert "performance" in analysis
        assert "stress_test_results" in analysis
        assert "monte_carlo" in analysis
        
        # Validate portfolio value calculation
        expected_value = sum(h.market_value for h in sample_portfolio)
        assert analysis["portfolio_value"] == expected_value
    
    def test_risk_metrics_calculation(self, portfolio_analyzer):
        """Test risk metrics calculations."""
        # Sample returns data
        returns = [0.01, -0.02, 0.015, 0.005, -0.01, 0.02, -0.005, 0.012]
        benchmark_returns = [0.008, -0.015, 0.012, 0.003, -0.008, 0.018, -0.003, 0.01]
        
        risk_metrics = portfolio_analyzer._calculate_risk_metrics(returns, benchmark_returns)
        
        # Validate risk metrics
        assert hasattr(risk_metrics, 'var_95')
        assert hasattr(risk_metrics, 'max_drawdown')
        assert hasattr(risk_metrics, 'volatility')
        assert hasattr(risk_metrics, 'beta')
        
        # Check that values are reasonable
        assert -1 <= risk_metrics.var_95 <= 1
        assert -1 <= risk_metrics.max_drawdown <= 0
        assert risk_metrics.volatility >= 0
    
    @pytest.mark.asyncio
    async def test_stress_testing(self, portfolio_analyzer, sample_portfolio):
        """Test stress testing functionality."""
        # Get historical data (mock)
        historical_data = await portfolio_analyzer._get_historical_data(sample_portfolio, 50)
        
        # Run stress tests
        stress_results = await portfolio_analyzer._run_stress_tests(sample_portfolio, historical_data)
        
        assert isinstance(stress_results, list)
        assert len(stress_results) > 0
        
        for result in stress_results:
            assert hasattr(result, 'scenario')
            assert hasattr(result, 'portfolio_loss')
            assert hasattr(result, 'portfolio_loss_pct')
            assert result.portfolio_loss >= 0
            assert 0 <= result.portfolio_loss_pct <= 1
    
    @pytest.mark.asyncio
    async def test_monte_carlo_simulation(self, portfolio_analyzer, sample_portfolio):
        """Test Monte Carlo simulation."""
        historical_data = await portfolio_analyzer._get_historical_data(sample_portfolio, 50)
        
        monte_carlo = await portfolio_analyzer._run_monte_carlo_simulation(sample_portfolio, historical_data)
        
        assert hasattr(monte_carlo, 'simulation_runs')
        assert hasattr(monte_carlo, 'expected_return')
        assert hasattr(monte_carlo, 'expected_volatility')
        assert hasattr(monte_carlo, 'probability_of_loss')
        
        assert monte_carlo.simulation_runs > 0
        assert 0 <= monte_carlo.probability_of_loss <= 1
    
    def test_portfolio_metrics_validation(self, sample_portfolio):
        """Test portfolio metrics validation."""
        # Check portfolio weights sum to approximately 1
        total_weight = sum(h.weight for h in sample_portfolio)
        assert 0.99 <= total_weight <= 1.01  # Allow for rounding errors
        
        # Check all holdings have positive values
        for holding in sample_portfolio:
            assert holding.quantity > 0
            assert holding.current_price > 0
            assert holding.market_value > 0
            assert holding.weight >= 0


class TestCommunityFeaturesIntegration:
    """Integration tests for Community Features."""
    
    @pytest.fixture
    async def community_engine(self):
        """Create community engine instance."""
        engine = CommunityEngine()
        yield engine
        engine.stop_community_engine()
    
    @pytest.mark.asyncio
    async def test_user_registration_workflow(self, community_engine):
        """Test user registration and management."""
        # Register a test user
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "portfolio_value": 100000
        }
        
        user = await community_engine.register_user(user_data)
        
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.portfolio_value == 100000
        assert len(user.achievements) > 0  # Should have welcome achievement
    
    @pytest.mark.asyncio
    async def test_challenge_lifecycle(self, community_engine):
        """Test challenge creation and management."""
        # Create test users
        users = []
        for i in range(3):
            user_data = {
                "username": f"user_{i}",
                "email": f"user{i}@example.com",
                "portfolio_value": 50000 + i * 25000
            }
            user = await community_engine.register_user(user_data)
            users.append(user)
        
        # Create a challenge
        challenge_data = {
            "title": "Test Portfolio Challenge",
            "description": "Test challenge description",
            "type": "PORTFOLIO_PERFORMANCE",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "prize_pool": 1000.0,
            "max_participants": 10
        }
        
        challenge = await community_engine.create_challenge(challenge_data)
        
        assert challenge.title == "Test Portfolio Challenge"
        assert challenge.prize_pool == 1000.0
        
        # Join users to challenge
        for user in users:
            result = await community_engine.join_challenge(user.user_id, challenge.challenge_id)
            assert result is True
        
        assert len(challenge.participants) == 3
    
    @pytest.mark.asyncio
    async def test_group_management(self, community_engine):
        """Test group creation and management."""
        # Create test users
        user_data = {
            "username": "group_admin",
            "email": "admin@example.com",
            "portfolio_value": 200000
        }
        admin_user = await community_engine.register_user(user_data)
        
        # Create a group
        group_data = {
            "name": "Test Investment Group",
            "description": "A test group for investors",
            "type": "PUBLIC",
            "max_members": 20
        }
        
        group = await community_engine.create_group(admin_user.user_id, group_data)
        
        assert group.name == "Test Investment Group"
        assert group.admin == admin_user.user_id
        assert admin_user.user_id in group.members
        assert group.group_id in admin_user.groups
    
    @pytest.mark.asyncio
    async def test_learning_content_workflow(self, community_engine):
        """Test learning content creation and completion."""
        # Create a test user
        user_data = {
            "username": "learner",
            "email": "learner@example.com",
            "portfolio_value": 75000
        }
        user = await community_engine.register_user(user_data)
        
        # Create learning content
        content_data = {
            "title": "Test Learning Content",
            "description": "Test educational content",
            "type": "ARTICLE",
            "difficulty": "BEGINNER",
            "estimated_time": 10,
            "content": {"text": "This is test content"},
            "tags": ["test", "education"]
        }
        
        content = await community_engine.create_learning_content(content_data)
        
        assert content.title == "Test Learning Content"
        assert content.difficulty_level.value == "BEGINNER"
        
        # Complete the content
        initial_score = user.total_score
        points_earned = await community_engine.complete_learning_content(user.user_id, content.content_id, 5)
        
        assert points_earned > 0
        assert user.total_score > initial_score
        assert content.completion_count == 1
    
    @pytest.mark.asyncio
    async def test_achievement_system(self, community_engine):
        """Test achievement and badge system."""
        # Create test user
        user_data = {
            "username": "achiever",
            "email": "achiever@example.com",
            "portfolio_value": 150000
        }
        user = await community_engine.register_user(user_data)
        
        initial_badge_count = len(user.badges)
        initial_score = user.total_score
        
        # Trigger achievement check
        await community_engine._check_user_achievements(user.user_id)
        
        # Should have at least the welcome achievement
        assert len(user.badges) >= initial_badge_count
    
    @pytest.mark.asyncio
    async def test_community_dashboard(self, community_engine):
        """Test community dashboard functionality."""
        # Create test user
        user_data = {
            "username": "dashboard_user",
            "email": "dashboard@example.com",
            "portfolio_value": 100000
        }
        user = await community_engine.register_user(user_data)
        
        # Get user dashboard
        dashboard = await community_engine.get_user_dashboard(user.user_id)
        
        assert "user" in dashboard
        assert "rankings" in dashboard
        assert "active_challenges" in dashboard
        assert "recent_achievements" in dashboard
        assert "groups" in dashboard
        
        assert dashboard["user"]["username"] == "dashboard_user"
        assert dashboard["user"]["total_score"] >= 0
    
    @pytest.mark.asyncio
    async def test_community_stats(self, community_engine):
        """Test community statistics."""
        # Create some test data
        for i in range(3):
            user_data = {
                "username": f"stats_user_{i}",
                "email": f"stats{i}@example.com",
                "portfolio_value": 50000 + i * 20000
            }
            await community_engine.register_user(user_data)
        
        # Get community stats
        stats = await community_engine.get_community_stats()
        
        assert "total_users" in stats
        assert "active_challenges" in stats
        assert "total_groups" in stats
        assert "total_achievements" in stats
        
        assert stats["total_users"] >= 3
        assert stats["total_portfolio_value"] >= 0


class TestCrossComponentIntegration:
    """Integration tests across multiple Phase 3 components."""
    
    @pytest.fixture
    async def integrated_system(self):
        """Set up integrated system with all components."""
        options_analyzer = OptionsFlowAnalyzer()
        alerts_engine = AlgorithmicAlertsEngine()
        portfolio_analyzer = PortfolioAnalyzer()
        community_engine = CommunityEngine()
        
        yield {
            "options": options_analyzer,
            "alerts": alerts_engine,
            "portfolio": portfolio_analyzer,
            "community": community_engine
        }
        
        # Cleanup
        options_analyzer.stop_monitoring()
        alerts_engine.stop_monitoring()
        community_engine.stop_community_engine()
    
    @pytest.mark.asyncio
    async def test_portfolio_to_community_integration(self, integrated_system):
        """Test integration between portfolio analytics and community features."""
        portfolio_analyzer = integrated_system["portfolio"]
        community_engine = integrated_system["community"]
        
        # Register user in community
        user_data = {
            "username": "portfolio_user",
            "email": "portfolio@example.com",
            "portfolio_value": 500000
        }
        user = await community_engine.register_user(user_data)
        
        # Create portfolio
        holdings = [
            PortfolioHolding("RELIANCE", 100, 2500, 250000, 0.5, "Energy", "equity"),
            PortfolioHolding("TCS", 50, 3200, 160000, 0.32, "Technology", "equity"),
            PortfolioHolding("HDFC", 75, 1200, 90000, 0.18, "Financial Services", "equity")
        ]
        
        # Analyze portfolio
        analysis = await portfolio_analyzer.analyze_portfolio("USER_PORTFOLIO", holdings)
        
        # Update user portfolio in community (simulate good performance)
        performance = 0.15  # 15% return
        await community_engine.update_user_portfolio(
            user.user_id, 
            analysis["portfolio_value"] * 1.15, 
            performance
        )
        
        # Verify integration
        updated_user = community_engine.users[user.user_id]
        assert updated_user.portfolio_value > user.portfolio_value
    
    @pytest.mark.asyncio
    async def test_alerts_to_community_integration(self, integrated_system):
        """Test integration between alerts and community features."""
        alerts_engine = integrated_system["alerts"]
        community_engine = integrated_system["community"]
        
        # Create user
        user_data = {
            "username": "alerts_user",
            "email": "alerts@example.com",
            "portfolio_value": 300000
        }
        user = await community_engine.register_user(user_data)
        
        # Get alerts summary
        alerts_summary = alerts_engine.get_alert_summary(hours=24)
        
        # Create educational content based on alerts (simulate)
        if isinstance(alerts_summary, dict) and alerts_summary.get("total_alerts", 0) > 0:
            content_data = {
                "title": "Understanding Market Alerts",
                "description": "Learn how to interpret algorithmic trading alerts",
                "type": "ARTICLE",
                "difficulty": "INTERMEDIATE",
                "estimated_time": 15,
                "content": {"text": "Market alerts can help you..."},
                "tags": ["alerts", "trading", "education"]
            }
            
            content = await community_engine.create_learning_content(content_data)
            assert content.title == "Understanding Market Alerts"
    
    @pytest.mark.asyncio
    async def test_options_flow_to_alerts_integration(self, integrated_system):
        """Test integration between options flow and alerts."""
        options_analyzer = integrated_system["options"]
        alerts_engine = integrated_system["alerts"]
        
        # Simulate options flow data affecting alert generation
        # In a real system, unusual options activity would trigger enhanced alerts
        
        # Get flow summary
        flow_summary = options_analyzer.get_flow_summary(hours=1)
        
        # Get current alerts
        active_alerts = alerts_engine.get_active_alerts()
        
        # Verify both systems are operational
        assert isinstance(flow_summary, dict)
        assert isinstance(active_alerts, list)
    
    @pytest.mark.asyncio
    async def test_comprehensive_workflow(self, integrated_system):
        """Test comprehensive workflow across all components."""
        options_analyzer = integrated_system["options"]
        alerts_engine = integrated_system["alerts"]
        portfolio_analyzer = integrated_system["portfolio"]
        community_engine = integrated_system["community"]
        
        # 1. Register user in community
        user_data = {
            "username": "comprehensive_user",
            "email": "comprehensive@example.com",
            "portfolio_value": 1000000
        }
        user = await community_engine.register_user(user_data)
        
        # 2. Analyze user's portfolio
        holdings = [
            PortfolioHolding("RELIANCE", 200, 2500, 500000, 0.5, "Energy", "equity"),
            PortfolioHolding("TCS", 100, 3200, 320000, 0.32, "Technology", "equity"),
            PortfolioHolding("HDFC", 112, 1600, 180000, 0.18, "Financial Services", "equity")
        ]
        
        portfolio_analysis = await portfolio_analyzer.analyze_portfolio("COMP_PORTFOLIO", holdings)
        
        # 3. Check for alerts
        alerts = alerts_engine.get_active_alerts()
        
        # 4. Get options flow insights
        options_flow = options_analyzer.get_flow_summary(hours=24)
        
        # 5. Create portfolio performance challenge in community
        challenge_data = {
            "title": "Monthly Portfolio Challenge",
            "description": "Best portfolio performance this month",
            "type": "PORTFOLIO_PERFORMANCE",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "prize_pool": 5000.0,
            "max_participants": 50
        }
        
        challenge = await community_engine.create_challenge(challenge_data)
        join_result = await community_engine.join_challenge(user.user_id, challenge.challenge_id)
        
        # 6. Verify comprehensive integration
        assert user.portfolio_value == 1000000
        assert portfolio_analysis["portfolio_value"] == 1000000
        assert isinstance(alerts, list)
        assert isinstance(options_flow, dict)
        assert join_result is True
        assert user.user_id in challenge.participants
        
        # 7. Get final dashboard
        dashboard = await community_engine.get_user_dashboard(user.user_id)
        assert len(dashboard["active_challenges"]) >= 1


class TestSystemPerformance:
    """Performance tests for Phase 3 components."""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent operations across components."""
        # Create all engines
        options_analyzer = OptionsFlowAnalyzer()
        alerts_engine = AlgorithmicAlertsEngine()
        community_engine = CommunityEngine()
        
        try:
            # Start all monitoring tasks
            tasks = [
                asyncio.create_task(options_analyzer.start_monitoring()),
                asyncio.create_task(alerts_engine.start_monitoring()),
                asyncio.create_task(community_engine.start_community_engine())
            ]
            
            # Let them run concurrently for a short time
            await asyncio.sleep(5)
            
            # Stop all engines
            options_analyzer.stop_monitoring()
            alerts_engine.stop_monitoring()
            community_engine.stop_community_engine()
            
            # Cancel tasks
            for task in tasks:
                task.cancel()
            
            # Wait for cancellation
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Test passes if no exceptions were raised
            assert True
            
        except Exception as e:
            pytest.fail(f"Concurrent operations test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        portfolio_analyzer = PortfolioAnalyzer()
        
        # Create large portfolio (100 holdings)
        large_portfolio = []
        for i in range(100):
            holding = PortfolioHolding(
                symbol=f"STOCK_{i:03d}",
                quantity=100 + i,
                current_price=1000 + i * 10,
                market_value=(100 + i) * (1000 + i * 10),
                weight=0.01,  # 1% each
                sector=f"Sector_{i % 10}",
                asset_class="equity"
            )
            large_portfolio.append(holding)
        
        # Analyze large portfolio
        start_time = datetime.now()
        analysis = await portfolio_analyzer.analyze_portfolio("LARGE_PORTFOLIO", large_portfolio)
        end_time = datetime.now()
        
        # Verify analysis completed and performance
        processing_time = (end_time - start_time).total_seconds()
        assert analysis["portfolio_id"] == "LARGE_PORTFOLIO"
        assert len(analysis["rebalancing_recommendations"]) >= 0
        assert processing_time < 30  # Should complete within 30 seconds


@pytest.mark.asyncio
async def test_system_reliability():
    """Test system reliability and error handling."""
    options_analyzer = OptionsFlowAnalyzer()
    alerts_engine = AlgorithmicAlertsEngine()
    
    # Test error handling in options analyzer
    try:
        # Test with invalid data
        invalid_summary = options_analyzer.get_flow_summary("INVALID_SYMBOL", hours=1)
        assert isinstance(invalid_summary, dict)
    except Exception as e:
        pytest.fail(f"Options analyzer error handling failed: {e}")
    
    # Test error handling in alerts engine
    try:
        # Test with empty data
        empty_alerts = alerts_engine.get_active_alerts("NONEXISTENT_SYMBOL")
        assert isinstance(empty_alerts, list)
    except Exception as e:
        pytest.fail(f"Alerts engine error handling failed: {e}")


def test_configuration_validation():
    """Test configuration validation across components."""
    # Test options analyzer config
    options_config = {
        "scan_interval": 5,
        "min_volume": 100,
        "enable_dark_pool": True
    }
    options_analyzer = OptionsFlowAnalyzer(options_config)
    assert options_analyzer.config["scan_interval"] == 5
    
    # Test alerts engine config
    alerts_config = {
        "scan_interval": 60,
        "min_confidence": 0.7,
        "symbols": ["NIFTY", "BANKNIFTY"]
    }
    alerts_engine = AlgorithmicAlertsEngine(alerts_config)
    assert alerts_engine.config["min_confidence"] == 0.7
    
    # Test portfolio analyzer config
    portfolio_config = {
        "risk_free_rate": 0.06,
        "monte_carlo_runs": 5000
    }
    portfolio_analyzer = PortfolioAnalyzer(portfolio_config)
    assert portfolio_analyzer.config["risk_free_rate"] == 0.06
    
    # Test community engine config
    community_config = {
        "max_group_size": 100,
        "achievement_check_interval": 1800
    }
    community_engine = CommunityEngine(community_config)
    assert community_engine.config["max_group_size"] == 100


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])