#!/usr/bin/env python3
"""
TradeMate Institutional Features Integration Test
===============================================
End-to-end integration validation for Phase 2B.3
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from institutional.advanced_order_management import AdvancedOrderManager, Order, OrderType
from institutional.hni_portfolio_management import HNIPortfolioManager, Portfolio, PortfolioType, RiskProfile
from institutional.api_trading_interface import InstitutionalAPIInterface, APIClient, APIClientType, PermissionLevel
from institutional.institutional_risk_management import (
    InstitutionalRiskManager, RiskLimit, RiskLimitType, Position, AssetClass
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstitutionalIntegrationTester:
    """End-to-end integration tester for institutional features"""
    
    def __init__(self):
        self.order_manager = AdvancedOrderManager()
        self.portfolio_manager = HNIPortfolioManager()
        self.api_interface = InstitutionalAPIInterface()
        self.risk_manager = InstitutionalRiskManager()
        
        self.test_results = []
    
    async def run_integration_tests(self):
        """Run comprehensive integration tests"""
        logger.info("🚀 Starting Institutional Features Integration Tests")
        logger.info("=" * 60)
        
        # Test scenarios
        await self._test_complete_order_lifecycle()
        await self._test_portfolio_with_risk_management()
        await self._test_api_to_execution_flow()
        await self._test_risk_limit_enforcement()
        await self._test_institutional_rebalancing()
        
        # Generate test report
        self._generate_test_report()
    
    async def _test_complete_order_lifecycle(self):
        """Test complete order lifecycle from creation to execution"""
        logger.info("\n📋 Testing Complete Order Lifecycle...")
        
        try:
            # Setup client and risk limits
            client_id = "INT_TEST_CLIENT_001"
            
            # Add risk limits
            portfolio_limit = RiskLimit(
                limit_id="PORT_LIMIT_001",
                client_id=client_id,
                limit_type=RiskLimitType.PORTFOLIO_LIMIT,
                limit_value=50000000.0,  # ₹5 Cr
                is_hard_limit=True
            )
            await self.risk_manager.add_risk_limit(portfolio_limit)
            
            position_limit = RiskLimit(
                limit_id="POS_LIMIT_001",
                client_id=client_id,
                limit_type=RiskLimitType.POSITION_LIMIT,
                limit_value=5000000.0,  # ₹50 Lakh per position
                is_hard_limit=True
            )
            await self.risk_manager.add_risk_limit(position_limit)
            
            # Create orders of different types
            orders = [
                Order(
                    order_id="INT_ORDER_001",
                    client_id=client_id,
                    symbol="RELIANCE",
                    order_type=OrderType.LIMIT,
                    side="BUY",
                    quantity=1000,
                    price=2450.50
                ),
                Order(
                    order_id="INT_ORDER_002",
                    client_id=client_id,
                    symbol="TCS",
                    order_type=OrderType.TWAP,
                    side="BUY",
                    quantity=500,
                    price=3200.00,
                    execution_time=60
                ),
                Order(
                    order_id="INT_ORDER_003",
                    client_id=client_id,
                    symbol="HDFC",
                    order_type=OrderType.ICEBERG,
                    side="BUY",
                    quantity=2000,
                    price=1650.75,
                    display_quantity=200
                )
            ]
            
            successful_orders = 0
            
            for order in orders:
                # Pre-trade risk validation
                validation_result, error_msg = await self.risk_manager.validate_order_pre_trade(order)
                
                if validation_result:
                    # Place order
                    execution_result = await self.order_manager.place_order(order)
                    
                    if execution_result:
                        successful_orders += 1
                        
                        # Update position for risk monitoring
                        position = Position(
                            client_id=order.client_id,
                            symbol=order.symbol,
                            quantity=order.quantity,
                            avg_price=order.price,
                            current_price=order.price,
                            market_value=order.quantity * order.price,
                            unrealized_pnl=0.0,
                            realized_pnl=0.0,
                            sector="Technology" if order.symbol == "TCS" else "Energy",
                            asset_class=AssetClass.EQUITY
                        )
                        
                        await self.risk_manager.update_position(position)
                        logger.info(f"  ✅ {order.symbol} {order.order_type.value} order executed")
                    else:
                        logger.warning(f"  ⚠️ {order.symbol} order execution failed")
                else:
                    logger.warning(f"  ⚠️ {order.symbol} order rejected: {error_msg}")
            
            # Calculate risk metrics
            risk_metrics = await self.risk_manager.calculate_risk_metrics(client_id)
            
            success = successful_orders >= 2 and risk_metrics is not None
            self.test_results.append({
                "test": "Complete Order Lifecycle",
                "success": success,
                "details": f"Executed {successful_orders}/3 orders, Risk metrics calculated: {risk_metrics is not None}"
            })
            
            if success:
                logger.info("  ✅ Complete order lifecycle test PASSED")
            else:
                logger.error("  ❌ Complete order lifecycle test FAILED")
                
        except Exception as e:
            logger.error(f"  ❌ Order lifecycle test error: {e}")
            self.test_results.append({
                "test": "Complete Order Lifecycle",
                "success": False,
                "details": f"Error: {e}"
            })
    
    async def _test_portfolio_with_risk_management(self):
        """Test portfolio management integrated with risk controls"""
        logger.info("\n💼 Testing Portfolio Management with Risk Controls...")
        
        try:
            client_id = "INT_TEST_CLIENT_002"
            
            # Create HNI portfolio
            portfolio = Portfolio(
                portfolio_id="INT_PORTFOLIO_001",
                client_id=client_id,
                name="HNI Balanced Growth Portfolio",
                portfolio_type=PortfolioType.BALANCED,
                risk_profile=RiskProfile.MODERATE,
                target_allocation={
                    "EQUITY": 0.6,
                    "DEBT": 0.3,
                    "CASH": 0.1
                },
                investment_amount=20000000.0  # ₹2 Cr
            )
            
            portfolio_result = await self.portfolio_manager.create_portfolio(portfolio)
            
            # Add portfolio-specific risk limits
            concentration_limit = RiskLimit(
                limit_id="CONC_LIMIT_001",
                client_id=client_id,
                limit_type=RiskLimitType.CONCENTRATION_LIMIT,
                limit_value=0.15,  # 15% max concentration
                is_hard_limit=True
            )
            await self.risk_manager.add_risk_limit(concentration_limit)
            
            # Get portfolio analytics
            analytics = await self.portfolio_manager.get_portfolio_analytics(portfolio.portfolio_id, client_id)
            
            # Simulate rebalancing
            current_weights = {"EQUITY": 0.7, "DEBT": 0.25, "CASH": 0.05}
            rebalancing_trades = await self.portfolio_manager.calculate_rebalancing_trades(
                portfolio.portfolio_id, current_weights
            )
            
            success = (portfolio_result is not None and 
                      analytics is not None and 
                      rebalancing_trades is not None)
            
            self.test_results.append({
                "test": "Portfolio with Risk Management",
                "success": success,
                "details": f"Portfolio created: {portfolio_result is not None}, Analytics: {analytics is not None}, Rebalancing: {rebalancing_trades is not None}"
            })
            
            if success:
                logger.info("  ✅ Portfolio management with risk controls test PASSED")
            else:
                logger.error("  ❌ Portfolio management test FAILED")
                
        except Exception as e:
            logger.error(f"  ❌ Portfolio management test error: {e}")
            self.test_results.append({
                "test": "Portfolio with Risk Management",
                "success": False,
                "details": f"Error: {e}"
            })
    
    async def _test_api_to_execution_flow(self):
        """Test API interface to order execution flow"""
        logger.info("\n🔌 Testing API to Execution Flow...")
        
        try:
            # Create API client
            api_client = APIClient(
                client_id="API_INT_CLIENT_001",
                client_name="Integration Test API Client",
                client_type=APIClientType.INSTITUTIONAL,
                permission_level=PermissionLevel.FULL_ACCESS,
                api_key="INT_TEST_API_KEY",
                secret_key="INT_TEST_SECRET",
                rate_limit=2000,
                max_order_value=20000000.0
            )
            
            # Test authentication
            auth_result = await self.api_interface._authenticate_client(
                api_client.api_key, api_client.secret_key
            )
            
            # Test rate limiting
            rate_limit_passed = True
            for i in range(10):
                if not await self.api_interface._check_rate_limit(api_client.client_id):
                    rate_limit_passed = False
                    break
            
            # Test order validation
            from institutional.api_trading_interface import OrderRequest
            order_request = OrderRequest(
                symbol="RELIANCE",
                order_type="LIMIT",
                side="BUY",
                quantity=500,
                price=2450.50
            )
            
            validation_passed = True
            try:
                await self.api_interface._validate_order(order_request, api_client)
            except:
                validation_passed = False
            
            success = rate_limit_passed and validation_passed
            
            self.test_results.append({
                "test": "API to Execution Flow",
                "success": success,
                "details": f"Rate limiting: {rate_limit_passed}, Validation: {validation_passed}"
            })
            
            if success:
                logger.info("  ✅ API to execution flow test PASSED")
            else:
                logger.error("  ❌ API to execution flow test FAILED")
                
        except Exception as e:
            logger.error(f"  ❌ API flow test error: {e}")
            self.test_results.append({
                "test": "API to Execution Flow",
                "success": False,
                "details": f"Error: {e}"
            })
    
    async def _test_risk_limit_enforcement(self):
        """Test risk limit enforcement across all components"""
        logger.info("\n🛡️ Testing Risk Limit Enforcement...")
        
        try:
            client_id = "RISK_TEST_CLIENT_001"
            
            # Setup very strict limits for testing
            strict_portfolio_limit = RiskLimit(
                limit_id="STRICT_PORT_001",
                client_id=client_id,
                limit_type=RiskLimitType.PORTFOLIO_LIMIT,
                limit_value=1000000.0,  # ₹10 Lakh - very low
                is_hard_limit=True
            )
            await self.risk_manager.add_risk_limit(strict_portfolio_limit)
            
            # Try to place order that would breach limit
            large_order = Order(
                order_id="LARGE_ORDER_TEST",
                client_id=client_id,
                symbol="RELIANCE",
                order_type=OrderType.LIMIT,
                side="BUY",
                quantity=1000,
                price=2450.50  # Total value: ₹24.5 Lakh > ₹10 Lakh limit
            )
            
            # Should be rejected
            validation_result, error_msg = await self.risk_manager.validate_order_pre_trade(large_order)
            
            # Check if alert was generated
            alerts = await self.risk_manager.get_client_alerts(client_id)
            alert_generated = len(alerts) > 0
            
            # Also test placing a smaller valid order
            small_order = Order(
                order_id="SMALL_ORDER_TEST",
                client_id=client_id,
                symbol="RELIANCE",
                order_type=OrderType.LIMIT,
                side="BUY",
                quantity=100,
                price=2450.50  # Total value: ₹2.45 Lakh < ₹10 Lakh limit
            )
            
            small_validation_result, _ = await self.risk_manager.validate_order_pre_trade(small_order)
            
            success = (not validation_result and  # Large order rejected
                      small_validation_result and   # Small order accepted
                      alert_generated)               # Alert generated
            
            self.test_results.append({
                "test": "Risk Limit Enforcement",
                "success": success,
                "details": f"Large order rejected: {not validation_result}, Small order accepted: {small_validation_result}, Alert generated: {alert_generated}"
            })
            
            if success:
                logger.info("  ✅ Risk limit enforcement test PASSED")
            else:
                logger.error("  ❌ Risk limit enforcement test FAILED")
                
        except Exception as e:
            logger.error(f"  ❌ Risk limit enforcement test error: {e}")
            self.test_results.append({
                "test": "Risk Limit Enforcement",
                "success": False,
                "details": f"Error: {e}"
            })
    
    async def _test_institutional_rebalancing(self):
        """Test institutional portfolio rebalancing with order generation"""
        logger.info("\n⚖️ Testing Institutional Rebalancing...")
        
        try:
            client_id = "REBAL_TEST_CLIENT_001"
            
            # Create institutional portfolio
            institutional_portfolio = Portfolio(
                portfolio_id="INST_REBAL_PORTFOLIO_001",
                client_id=client_id,
                name="Institutional Rebalancing Portfolio",
                portfolio_type=PortfolioType.AGGRESSIVE,
                risk_profile=RiskProfile.HIGH,
                target_allocation={
                    "EQUITY": 0.8,
                    "DEBT": 0.15,
                    "CASH": 0.05
                },
                investment_amount=100000000.0  # ₹10 Cr
            )
            
            portfolio_created = await self.portfolio_manager.create_portfolio(institutional_portfolio)
            
            # Add appropriate risk limits for institutional client
            institutional_limit = RiskLimit(
                limit_id="INST_LIMIT_001",
                client_id=client_id,
                limit_type=RiskLimitType.PORTFOLIO_LIMIT,
                limit_value=120000000.0,  # ₹12 Cr
                is_hard_limit=False  # Soft limit for institutional
            )
            await self.risk_manager.add_risk_limit(institutional_limit)
            
            # Simulate current allocation drift
            current_weights = {"EQUITY": 0.85, "DEBT": 0.12, "CASH": 0.03}
            
            # Calculate rebalancing trades
            rebalancing_trades = await self.portfolio_manager.calculate_rebalancing_trades(
                institutional_portfolio.portfolio_id, current_weights
            )
            
            rebalancing_orders_placed = 0
            
            # Execute rebalancing through order manager
            if rebalancing_trades:
                for trade in rebalancing_trades:
                    rebalancing_order = Order(
                        order_id=f"REBAL_ORDER_{rebalancing_orders_placed + 1}",
                        client_id=client_id,
                        symbol=trade.get("symbol", "REBAL_SYMBOL"),
                        order_type=OrderType.VWAP,  # Use VWAP for institutional rebalancing
                        side=trade.get("side", "BUY"),
                        quantity=abs(trade.get("quantity", 1000)),
                        price=trade.get("price", 1000.0),
                        execution_time=120  # 2-hour VWAP
                    )
                    
                    # Validate and place order
                    validation_result, _ = await self.risk_manager.validate_order_pre_trade(rebalancing_order)
                    
                    if validation_result:
                        execution_result = await self.order_manager.place_order(rebalancing_order)
                        if execution_result:
                            rebalancing_orders_placed += 1
            
            # Calculate updated risk metrics
            final_risk_metrics = await self.risk_manager.calculate_risk_metrics(client_id)
            
            success = (portfolio_created is not None and 
                      rebalancing_trades is not None and 
                      rebalancing_orders_placed > 0 and 
                      final_risk_metrics is not None)
            
            self.test_results.append({
                "test": "Institutional Rebalancing",
                "success": success,
                "details": f"Portfolio created: {portfolio_created is not None}, Rebalancing orders: {rebalancing_orders_placed}, Risk metrics: {final_risk_metrics is not None}"
            })
            
            if success:
                logger.info("  ✅ Institutional rebalancing test PASSED")
            else:
                logger.error("  ❌ Institutional rebalancing test FAILED")
                
        except Exception as e:
            logger.error(f"  ❌ Institutional rebalancing test error: {e}")
            self.test_results.append({
                "test": "Institutional Rebalancing",
                "success": False,
                "details": f"Error: {e}"
            })
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 60)
        logger.info("INSTITUTIONAL FEATURES INTEGRATION TEST REPORT")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Total Integration Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        # Detailed results
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{i}. {result['test']}: {status}")
            logger.info(f"   Details: {result['details']}")
            logger.info("")
        
        # Overall assessment
        if failed_tests == 0:
            logger.info("🎉 ALL INTEGRATION TESTS PASSED!")
            logger.info("✅ Phase 2B.3 Institutional Features COMPLETE")
            logger.info("✅ System ready for production deployment")
        else:
            logger.warning(f"⚠️ {failed_tests} integration tests failed")
            logger.warning("❌ Review and fix issues before deployment")
        
        return failed_tests == 0


async def main():
    """Main integration test runner"""
    logger.info("TradeMate Phase 2B.3 Institutional Features Integration Test")
    logger.info("Starting end-to-end validation...")
    
    tester = InstitutionalIntegrationTester()
    await tester.run_integration_tests()


if __name__ == "__main__":
    asyncio.run(main())