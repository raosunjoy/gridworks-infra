#!/usr/bin/env python3
"""
GridWorks Institutional Risk Management System
============================================
Real-time position monitoring, limits, and compliance for institutional clients
"""

import asyncio
import json
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging
from pathlib import Path
import time
import threading
from collections import defaultdict, deque
import redis

from .advanced_order_management import OrderType, OrderStatus, Order
from .hni_portfolio_management import Portfolio, AssetClass, RiskProfile

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLimitType(Enum):
    """Risk limit types"""
    POSITION_LIMIT = "position_limit"          # Max position in single security
    SECTOR_LIMIT = "sector_limit"              # Max exposure to sector
    PORTFOLIO_LIMIT = "portfolio_limit"        # Max total portfolio value
    LEVERAGE_LIMIT = "leverage_limit"          # Max leverage ratio
    VAR_LIMIT = "var_limit"                    # Value at Risk limit
    CONCENTRATION_LIMIT = "concentration_limit" # Max concentration in single asset
    DAILY_LOSS_LIMIT = "daily_loss_limit"     # Max daily loss
    OVERNIGHT_LIMIT = "overnight_limit"        # Max overnight position
    MARGIN_LIMIT = "margin_limit"              # Margin utilization limit
    CORRELATION_LIMIT = "correlation_limit"    # Max correlated positions


class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = "low"           # <70% of limit
    MEDIUM = "medium"     # 70-85% of limit
    HIGH = "high"         # 85-95% of limit
    CRITICAL = "critical" # >95% of limit
    BREACH = "breach"     # Limit exceeded


class AlertType(Enum):
    """Risk alert types"""
    LIMIT_APPROACHING = "limit_approaching"
    LIMIT_BREACHED = "limit_breached"
    UNUSUAL_ACTIVITY = "unusual_activity"
    MARGIN_CALL = "margin_call"
    REGULATORY_BREACH = "regulatory_breach"
    SYSTEM_ERROR = "system_error"


@dataclass
class RiskLimit:
    """Risk limit configuration"""
    limit_id: str
    client_id: str
    limit_type: RiskLimitType
    limit_value: float
    threshold_warning: float = 0.8    # 80% warning threshold
    threshold_critical: float = 0.95  # 95% critical threshold
    is_hard_limit: bool = True        # Block trades when breached
    currency: str = "INR"
    applicable_symbols: Optional[List[str]] = None
    applicable_sectors: Optional[List[str]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class Position:
    """Client position"""
    client_id: str
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    sector: str
    asset_class: AssetClass
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def notional_value(self) -> float:
        """Calculate notional value"""
        return abs(self.quantity * self.current_price)
    
    @property
    def pnl_percentage(self) -> float:
        """Calculate P&L percentage"""
        if self.market_value == 0:
            return 0.0
        return (self.unrealized_pnl / abs(self.market_value)) * 100


@dataclass
class RiskAlert:
    """Risk management alert"""
    alert_id: str
    client_id: str
    alert_type: AlertType
    risk_level: RiskLevel
    message: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    client_id: str
    portfolio_value: float
    total_exposure: float
    leverage_ratio: float
    var_1day: float
    var_5day: float
    beta: float
    sharpe_ratio: float
    max_drawdown: float
    concentration_risk: float
    sector_exposure: Dict[str, float]
    correlation_matrix: Optional[np.ndarray] = None
    calculated_at: datetime = field(default_factory=datetime.now)


class VolatilityCalculator:
    """Advanced volatility and risk calculations"""
    
    def __init__(self, lookback_days: int = 252):
        self.lookback_days = lookback_days
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=lookback_days))
    
    def update_price(self, symbol: str, price: float, timestamp: datetime):
        """Update price history"""
        self.price_history[symbol].append((price, timestamp))
    
    def calculate_volatility(self, symbol: str, days: int = 30) -> float:
        """Calculate historical volatility"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < days:
            return 0.0
        
        prices = [p[0] for p in list(self.price_history[symbol])[-days:]]
        returns = np.diff(np.log(prices))
        
        if len(returns) == 0:
            return 0.0
        
        daily_vol = np.std(returns)
        return daily_vol * np.sqrt(252)  # Annualized volatility
    
    def calculate_var(self, positions: List[Position], confidence: float = 0.05, days: int = 1) -> float:
        """Calculate Value at Risk using historical simulation"""
        if not positions:
            return 0.0
        
        portfolio_values = []
        min_history = min([len(self.price_history[pos.symbol]) for pos in positions 
                          if pos.symbol in self.price_history])
        
        if min_history < 30:  # Need at least 30 days of history
            return 0.0
        
        # Calculate portfolio returns for each historical day
        for i in range(min_history - 1):
            portfolio_return = 0.0
            
            for position in positions:
                if position.symbol in self.price_history:
                    prices = list(self.price_history[position.symbol])
                    if i + 1 < len(prices):
                        price_return = (prices[i+1][0] - prices[i][0]) / prices[i][0]
                        portfolio_return += (position.market_value / sum(p.market_value for p in positions)) * price_return
            
            portfolio_values.append(portfolio_return)
        
        if not portfolio_values:
            return 0.0
        
        # Calculate VaR at specified confidence level
        var_percentile = np.percentile(portfolio_values, confidence * 100)
        total_portfolio_value = sum(pos.market_value for pos in positions)
        
        return abs(var_percentile * total_portfolio_value * np.sqrt(days))


class InstitutionalRiskManager:
    """Institutional Risk Management System"""
    
    def __init__(self):
        # Risk limits storage
        self.risk_limits: Dict[str, List[RiskLimit]] = defaultdict(list)
        
        # Client positions
        self.positions: Dict[str, Dict[str, Position]] = defaultdict(dict)
        
        # Risk metrics cache
        self.risk_metrics_cache: Dict[str, RiskMetrics] = {}
        
        # Active alerts
        self.active_alerts: Dict[str, List[RiskAlert]] = defaultdict(list)
        
        # Volatility calculator
        self.volatility_calculator = VolatilityCalculator()
        
        # Redis for real-time updates
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
        
        # Risk monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Compliance rules
        self.compliance_rules = self._load_compliance_rules()
        
        logger.info("Institutional Risk Manager initialized")
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load regulatory compliance rules"""
        return {
            "sebi_position_limits": {
                "single_stock_max": 0.05,      # 5% of market cap
                "mutual_fund_max": 0.10,       # 10% of fund size
                "derivative_margin": 0.20       # 20% margin requirement
            },
            "margin_requirements": {
                "equity": 0.20,                # 20% margin for equity
                "derivatives": 0.25,           # 25% margin for derivatives
                "commodity": 0.15              # 15% margin for commodity
            },
            "concentration_limits": {
                "single_security": 0.10,       # 10% max in single security
                "single_sector": 0.25,         # 25% max in single sector
                "single_issuer": 0.15          # 15% max in single issuer
            }
        }
    
    async def add_risk_limit(self, risk_limit: RiskLimit) -> bool:
        """Add risk limit for client"""
        try:
            self.risk_limits[risk_limit.client_id].append(risk_limit)
            
            # Store in Redis for persistence
            await self._store_risk_limit(risk_limit)
            
            logger.info(f"Added risk limit {risk_limit.limit_type.value} for client {risk_limit.client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add risk limit: {e}")
            return False
    
    async def update_position(self, position: Position) -> bool:
        """Update client position"""
        try:
            self.positions[position.client_id][position.symbol] = position
            
            # Update price history for volatility calculations
            self.volatility_calculator.update_price(
                position.symbol, 
                position.current_price,
                position.last_updated
            )
            
            # Store in Redis
            await self._store_position(position)
            
            # Check risk limits
            await self._check_position_limits(position)
            
            logger.debug(f"Updated position {position.symbol} for client {position.client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
            return False
    
    async def validate_order_pre_trade(self, order: Order) -> Tuple[bool, Optional[str]]:
        """Validate order against risk limits before execution"""
        try:
            client_id = order.client_id
            
            # Get current positions
            positions = self.positions.get(client_id, {})
            
            # Calculate new position after order
            new_position = await self._calculate_new_position(order, positions)
            
            # Check all risk limits
            for risk_limit in self.risk_limits.get(client_id, []):
                if not risk_limit.is_active:
                    continue
                
                violation = await self._check_limit_violation(new_position, risk_limit, positions)
                
                if violation and risk_limit.is_hard_limit:
                    error_msg = f"Order rejected: {risk_limit.limit_type.value} limit would be breached"
                    
                    # Generate alert
                    await self._generate_alert(
                        client_id,
                        AlertType.LIMIT_BREACHED,
                        RiskLevel.CRITICAL,
                        error_msg,
                        {"order_id": order.order_id, "limit_type": risk_limit.limit_type.value}
                    )
                    
                    return False, error_msg
            
            # Check compliance rules
            compliance_check = await self._check_compliance_rules(order, positions)
            if not compliance_check[0]:
                return compliance_check
            
            logger.info(f"Order {order.order_id} passed pre-trade risk validation")
            return True, None
            
        except Exception as e:
            error_msg = f"Risk validation error: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    async def calculate_risk_metrics(self, client_id: str) -> Optional[RiskMetrics]:
        """Calculate comprehensive risk metrics for client"""
        try:
            positions = list(self.positions.get(client_id, {}).values())
            
            if not positions:
                return None
            
            # Portfolio value
            portfolio_value = sum(pos.market_value for pos in positions)
            total_exposure = sum(pos.notional_value for pos in positions)
            
            # Leverage ratio
            leverage_ratio = total_exposure / portfolio_value if portfolio_value > 0 else 0
            
            # VaR calculations
            var_1day = self.volatility_calculator.calculate_var(positions, confidence=0.05, days=1)
            var_5day = self.volatility_calculator.calculate_var(positions, confidence=0.05, days=5)
            
            # Sector exposure
            sector_exposure = {}
            for pos in positions:
                sector = pos.sector
                if sector not in sector_exposure:
                    sector_exposure[sector] = 0
                sector_exposure[sector] += pos.market_value
            
            # Normalize sector exposure to percentages
            if portfolio_value > 0:
                sector_exposure = {k: (v / portfolio_value) for k, v in sector_exposure.items()}
            
            # Concentration risk (largest position as % of portfolio)
            concentration_risk = 0
            if portfolio_value > 0:
                largest_position = max(pos.market_value for pos in positions) if positions else 0
                concentration_risk = largest_position / portfolio_value
            
            # Beta calculation (simplified - would need market data)
            beta = 1.0  # Default beta
            
            # Sharpe ratio (simplified calculation)
            sharpe_ratio = 0.0
            if positions:
                returns = [pos.pnl_percentage for pos in positions if pos.pnl_percentage != 0]
                if returns:
                    avg_return = np.mean(returns)
                    return_std = np.std(returns) if len(returns) > 1 else 1
                    sharpe_ratio = avg_return / return_std if return_std > 0 else 0
            
            # Max drawdown calculation
            max_drawdown = 0.0
            for pos in positions:
                if pos.unrealized_pnl < 0:
                    drawdown = abs(pos.unrealized_pnl) / pos.market_value if pos.market_value > 0 else 0
                    max_drawdown = max(max_drawdown, drawdown)
            
            risk_metrics = RiskMetrics(
                client_id=client_id,
                portfolio_value=portfolio_value,
                total_exposure=total_exposure,
                leverage_ratio=leverage_ratio,
                var_1day=var_1day,
                var_5day=var_5day,
                beta=beta,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                concentration_risk=concentration_risk,
                sector_exposure=sector_exposure
            )
            
            # Cache metrics
            self.risk_metrics_cache[client_id] = risk_metrics
            
            # Store in Redis
            await self._store_risk_metrics(risk_metrics)
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {e}")
            return None
    
    async def get_client_alerts(self, client_id: str, active_only: bool = True) -> List[RiskAlert]:
        """Get risk alerts for client"""
        alerts = self.active_alerts.get(client_id, [])
        
        if active_only:
            alerts = [alert for alert in alerts if not alert.is_acknowledged]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge risk alert"""
        try:
            for client_id, alerts in self.active_alerts.items():
                for alert in alerts:
                    if alert.alert_id == alert_id:
                        alert.is_acknowledged = True
                        alert.acknowledged_at = datetime.now()
                        alert.acknowledged_by = acknowledged_by
                        
                        # Update in Redis
                        await self._store_alert(alert)
                        
                        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    async def start_monitoring(self):
        """Start real-time risk monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Risk monitoring started")
    
    async def stop_monitoring(self):
        """Stop risk monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Risk monitoring stopped")
    
    def _monitoring_loop(self):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            try:
                asyncio.run(self._monitor_all_clients())
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Wait longer on error
    
    async def _monitor_all_clients(self):
        """Monitor all clients for risk violations"""
        for client_id in self.positions.keys():
            await self._monitor_client_risk(client_id)
    
    async def _monitor_client_risk(self, client_id: str):
        """Monitor individual client risk"""
        try:
            # Calculate current risk metrics
            risk_metrics = await self.calculate_risk_metrics(client_id)
            
            if not risk_metrics:
                return
            
            # Check all risk limits
            for risk_limit in self.risk_limits.get(client_id, []):
                if not risk_limit.is_active:
                    continue
                
                current_value = await self._get_current_limit_value(risk_limit, risk_metrics)
                utilization = current_value / risk_limit.limit_value if risk_limit.limit_value > 0 else 0
                
                # Generate alerts based on thresholds
                if utilization >= 1.0:  # Breach
                    await self._generate_alert(
                        client_id,
                        AlertType.LIMIT_BREACHED,
                        RiskLevel.BREACH,
                        f"{risk_limit.limit_type.value} limit breached: {utilization:.1%}",
                        {"limit_type": risk_limit.limit_type.value, "utilization": utilization}
                    )
                elif utilization >= risk_limit.threshold_critical:  # Critical
                    await self._generate_alert(
                        client_id,
                        AlertType.LIMIT_APPROACHING,
                        RiskLevel.CRITICAL,
                        f"{risk_limit.limit_type.value} limit critical: {utilization:.1%}",
                        {"limit_type": risk_limit.limit_type.value, "utilization": utilization}
                    )
                elif utilization >= risk_limit.threshold_warning:  # Warning
                    await self._generate_alert(
                        client_id,
                        AlertType.LIMIT_APPROACHING,
                        RiskLevel.HIGH,
                        f"{risk_limit.limit_type.value} limit warning: {utilization:.1%}",
                        {"limit_type": risk_limit.limit_type.value, "utilization": utilization}
                    )
        
        except Exception as e:
            logger.error(f"Client risk monitoring error for {client_id}: {e}")
    
    async def _calculate_new_position(self, order: Order, current_positions: Dict[str, Position]) -> Position:
        """Calculate position after order execution"""
        symbol = order.symbol
        
        if symbol in current_positions:
            current_pos = current_positions[symbol]
            
            if order.side == "BUY":
                new_quantity = current_pos.quantity + order.quantity
            else:  # SELL
                new_quantity = current_pos.quantity - order.quantity
            
            # Calculate new average price
            if new_quantity != 0:
                if order.side == "BUY":
                    total_cost = (current_pos.quantity * current_pos.avg_price + 
                                order.quantity * order.price)
                    new_avg_price = total_cost / (current_pos.quantity + order.quantity)
                else:
                    new_avg_price = current_pos.avg_price
            else:
                new_avg_price = 0
            
            new_position = Position(
                client_id=order.client_id,
                symbol=symbol,
                quantity=new_quantity,
                avg_price=new_avg_price,
                current_price=order.price or current_pos.current_price,
                market_value=new_quantity * (order.price or current_pos.current_price),
                unrealized_pnl=0,  # Will be calculated
                realized_pnl=current_pos.realized_pnl,
                sector=current_pos.sector,
                asset_class=current_pos.asset_class
            )
        else:
            # New position
            new_position = Position(
                client_id=order.client_id,
                symbol=symbol,
                quantity=order.quantity if order.side == "BUY" else -order.quantity,
                avg_price=order.price or 0,
                current_price=order.price or 0,
                market_value=(order.quantity * (order.price or 0)) if order.side == "BUY" else -(order.quantity * (order.price or 0)),
                unrealized_pnl=0,
                realized_pnl=0,
                sector="Unknown",  # Would be looked up from reference data
                asset_class=AssetClass.EQUITY
            )
        
        return new_position
    
    async def _check_limit_violation(self, new_position: Position, risk_limit: RiskLimit, 
                                   current_positions: Dict[str, Position]) -> bool:
        """Check if new position would violate risk limit"""
        
        if risk_limit.limit_type == RiskLimitType.POSITION_LIMIT:
            return abs(new_position.market_value) > risk_limit.limit_value
        
        elif risk_limit.limit_type == RiskLimitType.PORTFOLIO_LIMIT:
            total_value = sum(pos.market_value for pos in current_positions.values())
            total_value += new_position.market_value - current_positions.get(new_position.symbol, Position(
                client_id="", symbol="", quantity=0, avg_price=0, current_price=0,
                market_value=0, unrealized_pnl=0, realized_pnl=0, sector="", asset_class=AssetClass.EQUITY
            )).market_value
            return total_value > risk_limit.limit_value
        
        elif risk_limit.limit_type == RiskLimitType.CONCENTRATION_LIMIT:
            total_portfolio = sum(pos.market_value for pos in current_positions.values())
            total_portfolio += new_position.market_value - current_positions.get(new_position.symbol, Position(
                client_id="", symbol="", quantity=0, avg_price=0, current_price=0,
                market_value=0, unrealized_pnl=0, realized_pnl=0, sector="", asset_class=AssetClass.EQUITY
            )).market_value
            
            if total_portfolio > 0:
                concentration = abs(new_position.market_value) / total_portfolio
                return concentration > risk_limit.limit_value
        
        # Add more limit type checks as needed
        return False
    
    async def _check_compliance_rules(self, order: Order, positions: Dict[str, Position]) -> Tuple[bool, Optional[str]]:
        """Check regulatory compliance rules"""
        try:
            # Example: Check margin requirements
            if order.order_type in [OrderType.MARKET, OrderType.LIMIT]:
                required_margin = order.quantity * (order.price or 0) * self.compliance_rules["margin_requirements"]["equity"]
                
                # In production, check actual margin availability
                # For now, assume sufficient margin
                
            return True, None
            
        except Exception as e:
            return False, f"Compliance check failed: {e}"
    
    async def _get_current_limit_value(self, risk_limit: RiskLimit, risk_metrics: RiskMetrics) -> float:
        """Get current value for a specific limit type"""
        if risk_limit.limit_type == RiskLimitType.PORTFOLIO_LIMIT:
            return risk_metrics.portfolio_value
        elif risk_limit.limit_type == RiskLimitType.LEVERAGE_LIMIT:
            return risk_metrics.leverage_ratio
        elif risk_limit.limit_type == RiskLimitType.VAR_LIMIT:
            return risk_metrics.var_1day
        elif risk_limit.limit_type == RiskLimitType.CONCENTRATION_LIMIT:
            return risk_metrics.concentration_risk
        else:
            return 0.0
    
    async def _generate_alert(self, client_id: str, alert_type: AlertType, 
                            risk_level: RiskLevel, message: str, details: Dict[str, Any]):
        """Generate risk alert"""
        alert = RiskAlert(
            alert_id=str(uuid.uuid4()),
            client_id=client_id,
            alert_type=alert_type,
            risk_level=risk_level,
            message=message,
            details=details
        )
        
        # Store alert
        self.active_alerts[client_id].append(alert)
        await self._store_alert(alert)
        
        # Send notification (WebSocket, email, etc.)
        await self._send_alert_notification(alert)
        
        logger.warning(f"Risk alert generated for {client_id}: {message}")
    
    async def _check_position_limits(self, position: Position):
        """Check position-specific limits after update"""
        client_id = position.client_id
        
        for risk_limit in self.risk_limits.get(client_id, []):
            if risk_limit.limit_type == RiskLimitType.POSITION_LIMIT:
                if (risk_limit.applicable_symbols and 
                    position.symbol in risk_limit.applicable_symbols):
                    
                    utilization = abs(position.market_value) / risk_limit.limit_value
                    
                    if utilization >= risk_limit.threshold_warning:
                        level = RiskLevel.BREACH if utilization >= 1.0 else RiskLevel.HIGH
                        await self._generate_alert(
                            client_id,
                            AlertType.LIMIT_APPROACHING,
                            level,
                            f"Position limit warning for {position.symbol}: {utilization:.1%}",
                            {"symbol": position.symbol, "utilization": utilization}
                        )
    
    async def _store_risk_limit(self, risk_limit: RiskLimit):
        """Store risk limit in Redis"""
        key = f"risk_limit:{risk_limit.client_id}:{risk_limit.limit_id}"
        self.redis_client.setex(key, 86400, json.dumps(asdict(risk_limit), default=str))
    
    async def _store_position(self, position: Position):
        """Store position in Redis"""
        key = f"position:{position.client_id}:{position.symbol}"
        self.redis_client.setex(key, 3600, json.dumps(asdict(position), default=str))
    
    async def _store_risk_metrics(self, risk_metrics: RiskMetrics):
        """Store risk metrics in Redis"""
        key = f"risk_metrics:{risk_metrics.client_id}"
        self.redis_client.setex(key, 300, json.dumps(asdict(risk_metrics), default=str))
    
    async def _store_alert(self, alert: RiskAlert):
        """Store alert in Redis"""
        key = f"alert:{alert.client_id}:{alert.alert_id}"
        self.redis_client.setex(key, 86400, json.dumps(asdict(alert), default=str))
    
    async def _send_alert_notification(self, alert: RiskAlert):
        """Send alert notification via WebSocket/email"""
        # In production, integrate with notification service
        logger.info(f"Alert notification sent: {alert.message}")


# Global risk manager instance
institutional_risk_manager = InstitutionalRiskManager()


async def main():
    """Main function for testing"""
    logger.info("GridWorks Institutional Risk Management System")
    logger.info("=" * 50)
    
    # Example usage
    risk_manager = InstitutionalRiskManager()
    
    # Add sample risk limit
    portfolio_limit = RiskLimit(
        limit_id="LIMIT_001",
        client_id="INST_001",
        limit_type=RiskLimitType.PORTFOLIO_LIMIT,
        limit_value=10000000.0,  # ₹1 Cr
        threshold_warning=0.8,
        threshold_critical=0.95,
        is_hard_limit=True
    )
    
    await risk_manager.add_risk_limit(portfolio_limit)
    
    # Start monitoring
    await risk_manager.start_monitoring()
    
    logger.info("Risk management system operational")


if __name__ == "__main__":
    asyncio.run(main())