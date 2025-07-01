#!/usr/bin/env python3
"""
TradeMate Institutional Features Simple Test Suite
=================================================
Working test suite with correct imports and dependencies
"""

import asyncio
import pytest
import sys
import os
import logging
from datetime import datetime, timedelta

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestOrderManagement:
    """Test Advanced Order Management System"""
    
    def test_order_type_enum(self):
        """Test OrderType enum exists and has required values"""
        from institutional.advanced_order_management import OrderType
        
        # Check essential order types exist
        assert hasattr(OrderType, 'MARKET')
        assert hasattr(OrderType, 'LIMIT')
        assert hasattr(OrderType, 'TWAP')
        assert hasattr(OrderType, 'VWAP')
        assert hasattr(OrderType, 'ICEBERG')
        assert hasattr(OrderType, 'BRACKET')
        
        # Test enum values
        assert OrderType.MARKET.value == "market"
        assert OrderType.LIMIT.value == "limit"
        assert OrderType.TWAP.value == "twap"
    
    def test_order_status_enum(self):
        """Test OrderStatus enum"""
        from institutional.advanced_order_management import OrderStatus
        
        assert hasattr(OrderStatus, 'NEW')
        assert hasattr(OrderStatus, 'PENDING_NEW')
        assert hasattr(OrderStatus, 'FILLED')
        assert hasattr(OrderStatus, 'CANCELLED')
    
    def test_advanced_order_creation(self):
        """Test AdvancedOrder object creation"""
        from institutional.advanced_order_management import AdvancedOrder, OrderType, OrderStatus
        
        order = AdvancedOrder(
            order_id="TEST_001",
            client_id="CLIENT_001",
            symbol="RELIANCE",
            order_type=OrderType.LIMIT,
            side="BUY",
            quantity=100,
            price=2450.50
        )
        
        assert order.order_id == "TEST_001"
        assert order.symbol == "RELIANCE"
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == 100
        assert order.price == 2450.50
    
    def test_execution_engine_creation(self):
        """Test ExecutionEngine creation"""
        from institutional.advanced_order_management import ExecutionEngine
        
        engine = ExecutionEngine()
        assert engine is not None
        assert hasattr(engine, 'execute_order')
    
    def test_order_validator_creation(self):
        """Test OrderValidator creation"""
        from institutional.advanced_order_management import OrderValidator
        
        validator = OrderValidator()
        assert validator is not None
        assert hasattr(validator, 'validate_order')


class TestPortfolioManagement:
    """Test HNI Portfolio Management System"""
    
    def test_portfolio_type_enum(self):
        """Test PortfolioType enum"""
        from institutional.hni_portfolio_management import PortfolioType
        
        assert hasattr(PortfolioType, 'CONSERVATIVE')
        assert hasattr(PortfolioType, 'BALANCED')
        assert hasattr(PortfolioType, 'AGGRESSIVE')
        assert hasattr(PortfolioType, 'INCOME')
        assert hasattr(PortfolioType, 'GROWTH')
    
    def test_risk_profile_enum(self):
        """Test RiskProfile enum"""
        from institutional.hni_portfolio_management import RiskProfile
        
        assert hasattr(RiskProfile, 'VERY_LOW')
        assert hasattr(RiskProfile, 'LOW')
        assert hasattr(RiskProfile, 'MODERATE')
        assert hasattr(RiskProfile, 'HIGH')
        assert hasattr(RiskProfile, 'VERY_HIGH')
    
    def test_asset_class_enum(self):
        """Test AssetClass enum"""
        from institutional.hni_portfolio_management import AssetClass
        
        assert hasattr(AssetClass, 'EQUITY')
        assert hasattr(AssetClass, 'DEBT')
        assert hasattr(AssetClass, 'COMMODITIES')
        assert hasattr(AssetClass, 'CURRENCY')
    
    def test_hni_portfolio_creation(self):
        """Test HNIPortfolio creation"""
        from institutional.hni_portfolio_management import (
            HNIPortfolio, PortfolioType, RiskProfile
        )
        
        portfolio = HNIPortfolio(
            portfolio_id="PORT_001",
            client_id="CLIENT_001",
            name="Test HNI Portfolio",
            portfolio_type=PortfolioType.BALANCED,
            risk_profile=RiskProfile.MODERATE,
            investment_amount=10000000.0  # ₹1 Cr
        )
        
        assert portfolio.portfolio_id == "PORT_001"
        assert portfolio.portfolio_type == PortfolioType.BALANCED
        assert portfolio.investment_amount == 10000000.0
    
    def test_portfolio_manager_creation(self):
        """Test HNIPortfolioManager creation"""
        from institutional.hni_portfolio_management import HNIPortfolioManager
        
        manager = HNIPortfolioManager()
        assert manager is not None
        assert hasattr(manager, 'create_portfolio')
        assert hasattr(manager, 'optimize_portfolio')
    
    def test_portfolio_optimizer_creation(self):
        """Test PortfolioOptimizer creation"""
        from institutional.hni_portfolio_management import PortfolioOptimizer
        
        optimizer = PortfolioOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_mean_variance')


class TestRiskManagement:
    """Test Institutional Risk Management System"""
    
    def test_risk_limit_type_enum(self):
        """Test RiskLimitType enum"""
        from institutional.institutional_risk_management import RiskLimitType
        
        assert hasattr(RiskLimitType, 'POSITION_LIMIT')
        assert hasattr(RiskLimitType, 'PORTFOLIO_LIMIT')
        assert hasattr(RiskLimitType, 'VAR_LIMIT')
        assert hasattr(RiskLimitType, 'LEVERAGE_LIMIT')
        assert hasattr(RiskLimitType, 'CONCENTRATION_LIMIT')
    
    def test_risk_level_enum(self):
        """Test RiskLevel enum"""
        from institutional.institutional_risk_management import RiskLevel
        
        assert hasattr(RiskLevel, 'LOW')
        assert hasattr(RiskLevel, 'MEDIUM')
        assert hasattr(RiskLevel, 'HIGH')
        assert hasattr(RiskLevel, 'CRITICAL')
        assert hasattr(RiskLevel, 'BREACH')
    
    def test_alert_type_enum(self):
        """Test AlertType enum"""
        from institutional.institutional_risk_management import AlertType
        
        assert hasattr(AlertType, 'LIMIT_APPROACHING')
        assert hasattr(AlertType, 'LIMIT_BREACHED')
        assert hasattr(AlertType, 'UNUSUAL_ACTIVITY')
        assert hasattr(AlertType, 'MARGIN_CALL')
    
    def test_risk_limit_creation(self):
        """Test RiskLimit creation"""
        from institutional.institutional_risk_management import RiskLimit, RiskLimitType
        
        risk_limit = RiskLimit(
            limit_id="LIMIT_001",
            client_id="CLIENT_001",
            limit_type=RiskLimitType.PORTFOLIO_LIMIT,
            limit_value=10000000.0,
            is_hard_limit=True
        )
        
        assert risk_limit.limit_id == "LIMIT_001"
        assert risk_limit.limit_type == RiskLimitType.PORTFOLIO_LIMIT
        assert risk_limit.limit_value == 10000000.0
        assert risk_limit.is_hard_limit is True
    
    def test_position_creation(self):
        """Test Position creation"""
        from institutional.institutional_risk_management import Position, AssetClass
        
        position = Position(
            client_id="CLIENT_001",
            symbol="RELIANCE",
            quantity=100,
            avg_price=2400.00,
            current_price=2450.50,
            market_value=245050.0,
            unrealized_pnl=5050.0,
            realized_pnl=0.0,
            sector="Energy",
            asset_class=AssetClass.EQUITY
        )
        
        assert position.symbol == "RELIANCE"
        assert position.quantity == 100
        assert position.market_value == 245050.0
        assert position.notional_value > 0
        assert position.pnl_percentage > 0
    
    def test_risk_manager_creation(self):
        """Test InstitutionalRiskManager creation"""
        from institutional.institutional_risk_management import InstitutionalRiskManager
        
        risk_manager = InstitutionalRiskManager()
        assert risk_manager is not None
        assert hasattr(risk_manager, 'add_risk_limit')
        assert hasattr(risk_manager, 'validate_order_pre_trade')
        assert hasattr(risk_manager, 'calculate_risk_metrics')
    
    def test_volatility_calculator_creation(self):
        """Test VolatilityCalculator creation"""
        from institutional.institutional_risk_management import VolatilityCalculator
        
        vol_calc = VolatilityCalculator()
        assert vol_calc is not None
        assert hasattr(vol_calc, 'calculate_volatility')
        assert hasattr(vol_calc, 'calculate_var')


class TestAPIInterface:
    """Test Institutional API Trading Interface"""
    
    def test_api_client_type_enum(self):
        """Test APIClientType enum"""
        from institutional.api_trading_interface import APIClientType
        
        assert hasattr(APIClientType, 'INSTITUTIONAL')
        assert hasattr(APIClientType, 'HNI')
        assert hasattr(APIClientType, 'HEDGE_FUND')
        assert hasattr(APIClientType, 'PROPRIETARY')
    
    def test_permission_level_enum(self):
        """Test PermissionLevel enum"""
        from institutional.api_trading_interface import PermissionLevel
        
        assert hasattr(PermissionLevel, 'READ_ONLY')
        assert hasattr(PermissionLevel, 'TRADE_ENABLED')
        assert hasattr(PermissionLevel, 'PORTFOLIO_MANAGEMENT')
        assert hasattr(PermissionLevel, 'FULL_ACCESS')
    
    def test_api_client_creation(self):
        """Test APIClient creation"""
        from institutional.api_trading_interface import (
            APIClient, APIClientType, PermissionLevel
        )
        
        client = APIClient(
            client_id="API_CLIENT_001",
            client_name="Test Client",
            client_type=APIClientType.INSTITUTIONAL,
            permission_level=PermissionLevel.FULL_ACCESS,
            api_key="TEST_KEY",
            secret_key="TEST_SECRET"
        )
        
        assert client.client_id == "API_CLIENT_001"
        assert client.client_type == APIClientType.INSTITUTIONAL
        assert client.permission_level == PermissionLevel.FULL_ACCESS
    
    def test_order_request_creation(self):
        """Test OrderRequest model"""
        from institutional.api_trading_interface import OrderRequest
        
        order_request = OrderRequest(
            symbol="RELIANCE",
            order_type="LIMIT",
            side="BUY",
            quantity=100,
            price=2450.50
        )
        
        assert order_request.symbol == "RELIANCE"
        assert order_request.order_type == "LIMIT"
        assert order_request.quantity == 100
    
    def test_api_interface_creation(self):
        """Test InstitutionalAPIInterface creation"""
        from institutional.api_trading_interface import InstitutionalAPIInterface
        
        api_interface = InstitutionalAPIInterface()
        assert api_interface is not None
        assert hasattr(api_interface, 'app')
        assert hasattr(api_interface, '_authenticate_client')


class TestIntegrationScenarios:
    """Test basic integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_risk_manager_workflow(self):
        """Test basic risk manager workflow"""
        from institutional.institutional_risk_management import (
            InstitutionalRiskManager, RiskLimit, RiskLimitType
        )
        
        risk_manager = InstitutionalRiskManager()
        
        # Add risk limit
        risk_limit = RiskLimit(
            limit_id="INT_LIMIT_001",
            client_id="INT_CLIENT_001",
            limit_type=RiskLimitType.PORTFOLIO_LIMIT,
            limit_value=50000000.0,
            is_hard_limit=True
        )
        
        result = await risk_manager.add_risk_limit(risk_limit)
        assert result is True
        
        # Verify limit was added
        limits = risk_manager.risk_limits[risk_limit.client_id]
        assert len(limits) > 0
    
    @pytest.mark.asyncio
    async def test_portfolio_manager_workflow(self):
        """Test basic portfolio manager workflow"""
        from institutional.hni_portfolio_management import (
            HNIPortfolioManager, HNIPortfolio, PortfolioType, RiskProfile
        )
        
        portfolio_manager = HNIPortfolioManager()
        
        # Create portfolio
        portfolio = HNIPortfolio(
            portfolio_id="INT_PORT_001",
            client_id="INT_CLIENT_001",
            name="Integration Test Portfolio",
            portfolio_type=PortfolioType.BALANCED,
            risk_profile=RiskProfile.MODERATE,
            investment_amount=20000000.0
        )
        
        result = await portfolio_manager.create_portfolio(portfolio)
        assert result is not None


# Performance tests
class TestPerformance:
    """Test performance requirements"""
    
    def test_order_creation_performance(self):
        """Test order creation performance"""
        import time
        from institutional.advanced_order_management import AdvancedOrder, OrderType
        
        start_time = time.time()
        
        orders = []
        for i in range(1000):
            order = AdvancedOrder(
                order_id=f"PERF_{i}",
                client_id="PERF_CLIENT",
                symbol="RELIANCE",
                order_type=OrderType.LIMIT,
                side="BUY",
                quantity=100,
                price=2450.50
            )
            orders.append(order)
        
        creation_time = time.time() - start_time
        avg_time_per_order = (creation_time / 1000) * 1000  # ms
        
        logger.info(f"Order creation: {avg_time_per_order:.3f}ms per order")
        
        # Target: <1ms per order creation
        assert avg_time_per_order < 1.0, f"Order creation too slow: {avg_time_per_order}ms"
    
    def test_risk_calculation_performance(self):
        """Test risk calculation performance"""
        import time
        from institutional.institutional_risk_management import Position, AssetClass
        
        start_time = time.time()
        
        positions = []
        for i in range(100):
            position = Position(
                client_id="PERF_CLIENT",
                symbol=f"STOCK_{i}",
                quantity=100,
                avg_price=1000 + i,
                current_price=1000 + i + 10,
                market_value=(1000 + i + 10) * 100,
                unrealized_pnl=10 * 100,
                realized_pnl=0,
                sector=f"SECTOR_{i%5}",
                asset_class=AssetClass.EQUITY
            )
            positions.append(position)
        
        calculation_time = time.time() - start_time
        avg_time_per_position = (calculation_time / 100) * 1000  # ms
        
        logger.info(f"Position calculation: {avg_time_per_position:.3f}ms per position")
        
        # Target: <10ms per position
        assert avg_time_per_position < 10.0, f"Position calculation too slow: {avg_time_per_position}ms"


def test_module_imports():
    """Test that all modules can be imported successfully"""
    logger.info("Testing module imports...")
    
    # Test all institutional module imports
    try:
        import institutional.advanced_order_management
        import institutional.hni_portfolio_management
        import institutional.api_trading_interface
        import institutional.institutional_risk_management
        logger.info("✅ All institutional modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    # Run standalone test
    logger.info("🚀 TradeMate Institutional Features Test Suite")
    logger.info("=" * 60)
    
    # Test imports first
    if not test_module_imports():
        exit(1)
    
    # Run pytest
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    exit(result.returncode)