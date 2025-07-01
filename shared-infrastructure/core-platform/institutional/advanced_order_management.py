#!/usr/bin/env python3
"""
GridWorks Advanced Order Management System
=========================================
Institutional-grade order types and execution for HNI clients
"""

import asyncio
import json
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging
from pathlib import Path
import time
import heapq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Advanced institutional order types"""
    # Basic orders
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    
    # Advanced orders
    BRACKET = "bracket"               # OCO with profit target and stop loss
    COVER = "cover"                   # Market order with mandatory stop loss
    ICEBERG = "iceberg"               # Large order broken into smaller pieces
    TWAP = "twap"                     # Time Weighted Average Price
    VWAP = "vwap"                     # Volume Weighted Average Price
    IMPLEMENTATION_SHORTFALL = "is"   # Minimize market impact
    
    # Conditional orders
    IF_TOUCHED = "if_touched"         # Becomes market order when price touched
    ONE_CANCELS_OTHER = "oco"         # Two orders, one execution cancels other
    TRAILING_STOP = "trailing_stop"   # Dynamic stop loss
    
    # Algorithmic orders
    HIDDEN = "hidden"                 # Hide order quantity
    RESERVE = "reserve"               # Show only partial quantity
    DISCRETIONARY = "discretionary"   # Price improvement within range


class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order execution status"""
    PENDING = "pending"               # Order created but not sent
    SUBMITTED = "submitted"           # Order sent to exchange
    ACKNOWLEDGED = "acknowledged"     # Order accepted by exchange
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(Enum):
    """Time in force conditions"""
    DAY = "day"                       # Valid for trading day
    IOC = "ioc"                       # Immediate or Cancel
    FOK = "fok"                       # Fill or Kill
    GTC = "gtc"                       # Good Till Cancelled
    GTD = "gtd"                       # Good Till Date
    ATO = "ato"                       # At The Opening
    ATC = "atc"                       # At The Closing


class ExecutionAlgorithm(Enum):
    """Execution algorithm types"""
    ARRIVAL_PRICE = "arrival_price"   # Target arrival price
    PARTICIPATE = "participate"       # Participation rate strategy
    IMPLEMENT_SHORTFALL = "is"        # Implementation Shortfall
    TARGET_CLOSE = "target_close"     # Target closing price
    PERCENT_VOLUME = "percent_volume" # Percentage of volume


@dataclass
class OrderLeg:
    """Individual leg of a complex order"""
    leg_id: str
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionReport:
    """Order execution report"""
    report_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    filled_quantity: int
    avg_fill_price: float
    commission: float
    timestamp: datetime
    execution_id: str
    venue: str = "NSE"
    
    @property
    def remaining_quantity(self) -> int:
        """Calculate remaining quantity"""
        return self.quantity - self.filled_quantity
    
    @property
    def fill_ratio(self) -> float:
        """Calculate fill ratio"""
        return self.filled_quantity / self.quantity if self.quantity > 0 else 0.0


@dataclass
class AdvancedOrder:
    """Advanced institutional order"""
    order_id: str
    client_id: str
    strategy_id: Optional[str]
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    status: OrderStatus
    
    # Pricing
    price: Optional[float] = None
    stop_price: Optional[float] = None
    discretionary_offset: Optional[float] = None
    
    # Execution parameters
    time_in_force: TimeInForce = TimeInForce.DAY
    algorithm: Optional[ExecutionAlgorithm] = None
    algorithm_params: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced features
    display_quantity: Optional[int] = None  # For iceberg orders
    minimum_quantity: Optional[int] = None  # Minimum fill size
    all_or_none: bool = False
    
    # Order legs (for complex orders)
    legs: List[OrderLeg] = field(default_factory=list)
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Execution tracking
    filled_quantity: int = 0
    avg_fill_price: float = 0.0
    total_commission: float = 0.0
    executions: List[ExecutionReport] = field(default_factory=list)
    
    # Risk and compliance
    risk_checked: bool = False
    compliance_checked: bool = False
    allocation_instructions: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def remaining_quantity(self) -> int:
        """Calculate remaining quantity"""
        return self.quantity - self.filled_quantity
    
    @property
    def is_complete(self) -> bool:
        """Check if order is completely filled"""
        return self.filled_quantity >= self.quantity
    
    @property
    def is_active(self) -> bool:
        """Check if order is active"""
        return self.status in [OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED]


class OrderValidator:
    """Advanced order validation for institutional clients"""
    
    def __init__(self):
        """Initialize order validator"""
        self.validation_rules = {}
        self.market_hours = {
            'pre_open': ('09:00', '09:15'),
            'normal': ('09:15', '15:30'),
            'closing': ('15:30', '16:00')
        }
    
    async def validate_order(self, order: AdvancedOrder) -> Tuple[bool, List[str]]:
        """Comprehensive order validation"""
        errors = []
        
        # Basic validation
        if not await self._validate_basic_parameters(order, errors):
            return False, errors
        
        # Market hours validation
        if not await self._validate_market_hours(order, errors):
            return False, errors
        
        # Order type specific validation
        if not await self._validate_order_type(order, errors):
            return False, errors
        
        # Risk validation
        if not await self._validate_risk_limits(order, errors):
            return False, errors
        
        # Compliance validation
        if not await self._validate_compliance(order, errors):
            return False, errors
        
        return len(errors) == 0, errors
    
    async def _validate_basic_parameters(self, order: AdvancedOrder, errors: List[str]) -> bool:
        """Validate basic order parameters"""
        if order.quantity <= 0:
            errors.append("Order quantity must be positive")
        
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and not order.price:
            errors.append("Limit orders require a price")
        
        if order.order_type in [OrderType.STOP_LOSS, OrderType.STOP_LIMIT, OrderType.TRAILING_STOP] and not order.stop_price:
            errors.append("Stop orders require a stop price")
        
        if order.display_quantity and order.display_quantity > order.quantity:
            errors.append("Display quantity cannot exceed order quantity")
        
        return len(errors) == 0
    
    async def _validate_market_hours(self, order: AdvancedOrder, errors: List[str]) -> bool:
        """Validate market hours for order types"""
        current_time = datetime.now().time()
        
        # ATO orders only during pre-open
        if order.time_in_force == TimeInForce.ATO:
            pre_open_start = datetime.strptime(self.market_hours['pre_open'][0], '%H:%M').time()
            pre_open_end = datetime.strptime(self.market_hours['pre_open'][1], '%H:%M').time()
            
            if not (pre_open_start <= current_time <= pre_open_end):
                errors.append("ATO orders can only be placed during pre-open session")
        
        # Market orders during market hours
        if order.order_type == OrderType.MARKET:
            market_start = datetime.strptime(self.market_hours['normal'][0], '%H:%M').time()
            market_end = datetime.strptime(self.market_hours['normal'][1], '%H:%M').time()
            
            if not (market_start <= current_time <= market_end):
                errors.append("Market orders can only be placed during market hours")
        
        return len(errors) == 0
    
    async def _validate_order_type(self, order: AdvancedOrder, errors: List[str]) -> bool:
        """Validate order type specific requirements"""
        
        if order.order_type == OrderType.BRACKET:
            if len(order.legs) != 3:
                errors.append("Bracket orders require exactly 3 legs")
        
        elif order.order_type == OrderType.ICEBERG:
            if not order.display_quantity:
                errors.append("Iceberg orders require display quantity")
            if order.display_quantity >= order.quantity:
                errors.append("Iceberg display quantity must be less than total quantity")
        
        elif order.order_type == OrderType.TWAP:
            if 'duration' not in order.algorithm_params:
                errors.append("TWAP orders require duration parameter")
        
        elif order.order_type == OrderType.VWAP:
            if 'participation_rate' not in order.algorithm_params:
                errors.append("VWAP orders require participation rate parameter")
        
        return len(errors) == 0
    
    async def _validate_risk_limits(self, order: AdvancedOrder, errors: List[str]) -> bool:
        """Validate against risk limits"""
        # Simplified risk validation (expand based on requirements)
        
        # Position size limits
        max_position_value = 10000000  # ₹1 crore
        if order.price and (order.quantity * order.price) > max_position_value:
            errors.append(f"Order value exceeds maximum position limit of ₹{max_position_value:,}")
        
        # Single order quantity limits
        max_quantity = 100000
        if order.quantity > max_quantity:
            errors.append(f"Order quantity exceeds maximum limit of {max_quantity:,}")
        
        return len(errors) == 0
    
    async def _validate_compliance(self, order: AdvancedOrder, errors: List[str]) -> bool:
        """Validate compliance requirements"""
        # Mock compliance checks (implement actual compliance logic)
        
        # Check if client is authorized for order type
        restricted_order_types = [OrderType.TWAP, OrderType.VWAP, OrderType.IMPLEMENTATION_SHORTFALL]
        if order.order_type in restricted_order_types:
            # In production, check client permissions
            logger.info(f"Advanced order type {order.order_type.value} requires special authorization")
        
        return len(errors) == 0


class ExecutionEngine:
    """Advanced order execution engine"""
    
    def __init__(self):
        """Initialize execution engine"""
        self.active_orders = {}
        self.execution_queue = []
        self.market_data_cache = {}
        self.execution_algorithms = {}
        
        # Initialize execution algorithms
        self._initialize_algorithms()
    
    def _initialize_algorithms(self):
        """Initialize execution algorithms"""
        self.execution_algorithms = {
            ExecutionAlgorithm.TWAP: self._execute_twap,
            ExecutionAlgorithm.VWAP: self._execute_vwap,
            ExecutionAlgorithm.IMPLEMENT_SHORTFALL: self._execute_implementation_shortfall,
            ExecutionAlgorithm.PARTICIPATE: self._execute_participation,
        }
    
    async def submit_order(self, order: AdvancedOrder) -> bool:
        """Submit order for execution"""
        try:
            # Validate order
            validator = OrderValidator()
            is_valid, errors = await validator.validate_order(order)
            
            if not is_valid:
                logger.error(f"Order validation failed: {errors}")
                order.status = OrderStatus.REJECTED
                return False
            
            # Update order status
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now()
            
            # Add to active orders
            self.active_orders[order.order_id] = order
            
            # Route to appropriate execution handler
            await self._route_order(order)
            
            logger.info(f"Order {order.order_id} submitted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting order {order.order_id}: {e}")
            order.status = OrderStatus.REJECTED
            return False
    
    async def _route_order(self, order: AdvancedOrder):
        """Route order to appropriate execution handler"""
        
        if order.order_type == OrderType.MARKET:
            await self._execute_market_order(order)
        
        elif order.order_type == OrderType.LIMIT:
            await self._execute_limit_order(order)
        
        elif order.order_type == OrderType.BRACKET:
            await self._execute_bracket_order(order)
        
        elif order.order_type == OrderType.ICEBERG:
            await self._execute_iceberg_order(order)
        
        elif order.order_type in [OrderType.TWAP, OrderType.VWAP]:
            await self._execute_algorithmic_order(order)
        
        else:
            # Default to limit order execution
            await self._execute_limit_order(order)
    
    async def _execute_market_order(self, order: AdvancedOrder):
        """Execute market order"""
        # Simulate immediate execution
        current_price = await self._get_current_price(order.symbol)
        
        # Simulate market impact
        impact = self._calculate_market_impact(order.quantity, order.symbol)
        execution_price = current_price * (1 + impact if order.side == OrderSide.BUY else 1 - impact)
        
        # Create execution report
        execution = ExecutionReport(
            report_id=str(uuid.uuid4()),
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            filled_quantity=order.quantity,
            avg_fill_price=execution_price,
            commission=self._calculate_commission(order.quantity, execution_price),
            timestamp=datetime.now(),
            execution_id=str(uuid.uuid4())
        )
        
        # Update order
        order.filled_quantity = order.quantity
        order.avg_fill_price = execution_price
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        order.executions.append(execution)
        
        logger.info(f"Market order {order.order_id} executed at ₹{execution_price:.2f}")
    
    async def _execute_limit_order(self, order: AdvancedOrder):
        """Execute limit order"""
        # Simulate limit order logic
        current_price = await self._get_current_price(order.symbol)
        
        # Check if order can be filled immediately
        can_fill = (
            (order.side == OrderSide.BUY and current_price <= order.price) or
            (order.side == OrderSide.SELL and current_price >= order.price)
        )
        
        if can_fill:
            # Immediate fill
            execution_price = order.price
            
            execution = ExecutionReport(
                report_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                filled_quantity=order.quantity,
                avg_fill_price=execution_price,
                commission=self._calculate_commission(order.quantity, execution_price),
                timestamp=datetime.now(),
                execution_id=str(uuid.uuid4())
            )
            
            order.filled_quantity = order.quantity
            order.avg_fill_price = execution_price
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now()
            order.executions.append(execution)
            
            logger.info(f"Limit order {order.order_id} filled at ₹{execution_price:.2f}")
        else:
            # Order remains pending
            order.status = OrderStatus.ACKNOWLEDGED
            logger.info(f"Limit order {order.order_id} pending at ₹{order.price:.2f}")
    
    async def _execute_bracket_order(self, order: AdvancedOrder):
        """Execute bracket order (OCO with target and stop)"""
        if len(order.legs) != 3:
            logger.error(f"Bracket order {order.order_id} requires 3 legs")
            order.status = OrderStatus.REJECTED
            return
        
        # First leg is the main order
        main_leg = order.legs[0]
        
        # Execute main order first
        await self._execute_market_order(order)
        
        if order.status == OrderStatus.FILLED:
            # Create target and stop orders
            target_leg = order.legs[1]  # Profit target
            stop_leg = order.legs[2]    # Stop loss
            
            # In production, submit both orders to exchange
            logger.info(f"Bracket order {order.order_id} main leg filled, target and stop orders active")
    
    async def _execute_iceberg_order(self, order: AdvancedOrder):
        """Execute iceberg order"""
        display_qty = order.display_quantity or min(order.quantity // 10, 1000)
        remaining_qty = order.quantity
        
        while remaining_qty > 0 and order.status == OrderStatus.ACKNOWLEDGED:
            # Create child order for display quantity
            child_qty = min(display_qty, remaining_qty)
            
            # Simulate partial execution
            current_price = await self._get_current_price(order.symbol)
            execution_price = current_price
            
            execution = ExecutionReport(
                report_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=child_qty,
                filled_quantity=child_qty,
                avg_fill_price=execution_price,
                commission=self._calculate_commission(child_qty, execution_price),
                timestamp=datetime.now(),
                execution_id=str(uuid.uuid4())
            )
            
            order.filled_quantity += child_qty
            order.executions.append(execution)
            remaining_qty -= child_qty
            
            # Update average fill price
            total_value = sum(e.filled_quantity * e.avg_fill_price for e in order.executions)
            order.avg_fill_price = total_value / order.filled_quantity
            
            if remaining_qty == 0:
                order.status = OrderStatus.FILLED
                order.filled_at = datetime.now()
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
            
            # Wait before next slice (simulated)
            await asyncio.sleep(0.1)
        
        logger.info(f"Iceberg order {order.order_id} completed with {len(order.executions)} executions")
    
    async def _execute_algorithmic_order(self, order: AdvancedOrder):
        """Execute algorithmic order (TWAP/VWAP)"""
        if order.algorithm in self.execution_algorithms:
            await self.execution_algorithms[order.algorithm](order)
        else:
            logger.error(f"Unknown algorithm: {order.algorithm}")
            order.status = OrderStatus.REJECTED
    
    async def _execute_twap(self, order: AdvancedOrder):
        """Execute Time Weighted Average Price order"""
        duration_minutes = order.algorithm_params.get('duration', 60)  # Default 1 hour
        slice_interval = order.algorithm_params.get('slice_interval', 5)  # 5 minutes
        
        total_slices = duration_minutes // slice_interval
        quantity_per_slice = order.quantity // total_slices
        remaining_quantity = order.quantity
        
        logger.info(f"TWAP order {order.order_id}: {total_slices} slices over {duration_minutes} minutes")
        
        for slice_num in range(total_slices):
            if remaining_quantity <= 0:
                break
            
            slice_qty = min(quantity_per_slice, remaining_quantity)
            if slice_num == total_slices - 1:  # Last slice gets remaining
                slice_qty = remaining_quantity
            
            # Execute slice
            current_price = await self._get_current_price(order.symbol)
            execution_price = current_price
            
            execution = ExecutionReport(
                report_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=slice_qty,
                filled_quantity=slice_qty,
                avg_fill_price=execution_price,
                commission=self._calculate_commission(slice_qty, execution_price),
                timestamp=datetime.now(),
                execution_id=str(uuid.uuid4())
            )
            
            order.filled_quantity += slice_qty
            order.executions.append(execution)
            remaining_quantity -= slice_qty
            
            # Update average fill price
            total_value = sum(e.filled_quantity * e.avg_fill_price for e in order.executions)
            order.avg_fill_price = total_value / order.filled_quantity
            
            if remaining_quantity == 0:
                order.status = OrderStatus.FILLED
                order.filled_at = datetime.now()
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
            
            # Wait for next slice
            if slice_num < total_slices - 1:
                await asyncio.sleep(slice_interval * 60)  # Convert to seconds
        
        logger.info(f"TWAP order {order.order_id} completed with avg price ₹{order.avg_fill_price:.2f}")
    
    async def _execute_vwap(self, order: AdvancedOrder):
        """Execute Volume Weighted Average Price order"""
        participation_rate = order.algorithm_params.get('participation_rate', 0.1)  # 10%
        duration_minutes = order.algorithm_params.get('duration', 60)
        
        # Simulate VWAP execution
        slices = 12  # Execute every 5 minutes for 1 hour
        quantity_per_slice = order.quantity // slices
        remaining_quantity = order.quantity
        
        logger.info(f"VWAP order {order.order_id}: {participation_rate:.1%} participation rate")
        
        for slice_num in range(slices):
            if remaining_quantity <= 0:
                break
            
            # Simulate volume-based sizing
            market_volume = await self._get_market_volume(order.symbol)
            max_slice_qty = int(market_volume * participation_rate)
            slice_qty = min(quantity_per_slice, max_slice_qty, remaining_quantity)
            
            if slice_num == slices - 1:  # Last slice
                slice_qty = remaining_quantity
            
            # Execute slice
            current_price = await self._get_current_price(order.symbol)
            vwap_price = await self._get_vwap_price(order.symbol)
            execution_price = (current_price + vwap_price) / 2  # Simplified VWAP targeting
            
            execution = ExecutionReport(
                report_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=slice_qty,
                filled_quantity=slice_qty,
                avg_fill_price=execution_price,
                commission=self._calculate_commission(slice_qty, execution_price),
                timestamp=datetime.now(),
                execution_id=str(uuid.uuid4())
            )
            
            order.filled_quantity += slice_qty
            order.executions.append(execution)
            remaining_quantity -= slice_qty
            
            # Update average fill price
            total_value = sum(e.filled_quantity * e.avg_fill_price for e in order.executions)
            order.avg_fill_price = total_value / order.filled_quantity
            
            if remaining_quantity == 0:
                order.status = OrderStatus.FILLED
                order.filled_at = datetime.now()
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
            
            # Wait for next slice
            if slice_num < slices - 1:
                await asyncio.sleep(5 * 60)  # 5 minutes
        
        logger.info(f"VWAP order {order.order_id} completed with avg price ₹{order.avg_fill_price:.2f}")
    
    async def _execute_implementation_shortfall(self, order: AdvancedOrder):
        """Execute Implementation Shortfall algorithm"""
        # Simplified IS algorithm
        aggression = order.algorithm_params.get('aggression', 0.5)  # 0 = passive, 1 = aggressive
        
        # More aggressive = faster execution, higher market impact
        slices = max(1, int(10 * (1 - aggression)))  # 1-10 slices
        quantity_per_slice = order.quantity // slices
        remaining_quantity = order.quantity
        
        logger.info(f"Implementation Shortfall order {order.order_id}: {slices} slices, aggression {aggression}")
        
        for slice_num in range(slices):
            if remaining_quantity <= 0:
                break
            
            slice_qty = min(quantity_per_slice, remaining_quantity)
            if slice_num == slices - 1:
                slice_qty = remaining_quantity
            
            # Calculate market impact based on aggression
            current_price = await self._get_current_price(order.symbol)
            impact = self._calculate_market_impact(slice_qty, order.symbol) * aggression
            execution_price = current_price * (1 + impact if order.side == OrderSide.BUY else 1 - impact)
            
            execution = ExecutionReport(
                report_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=slice_qty,
                filled_quantity=slice_qty,
                avg_fill_price=execution_price,
                commission=self._calculate_commission(slice_qty, execution_price),
                timestamp=datetime.now(),
                execution_id=str(uuid.uuid4())
            )
            
            order.filled_quantity += slice_qty
            order.executions.append(execution)
            remaining_quantity -= slice_qty
            
            # Update average fill price
            total_value = sum(e.filled_quantity * e.avg_fill_price for e in order.executions)
            order.avg_fill_price = total_value / order.filled_quantity
            
            if remaining_quantity == 0:
                order.status = OrderStatus.FILLED
                order.filled_at = datetime.now()
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
            
            # Dynamic wait time based on aggression
            wait_time = (1 - aggression) * 60  # 0-60 seconds
            if slice_num < slices - 1:
                await asyncio.sleep(wait_time)
        
        logger.info(f"IS order {order.order_id} completed with avg price ₹{order.avg_fill_price:.2f}")
    
    async def _execute_participation(self, order: AdvancedOrder):
        """Execute participation rate strategy"""
        participation_rate = order.algorithm_params.get('participation_rate', 0.2)  # 20%
        max_participation = order.algorithm_params.get('max_participation', 0.3)   # 30%
        
        # Simulate participation-based execution
        remaining_quantity = order.quantity
        
        while remaining_quantity > 0:
            market_volume = await self._get_market_volume(order.symbol)
            target_qty = int(market_volume * participation_rate)
            slice_qty = min(target_qty, remaining_quantity)
            
            if slice_qty == 0:
                await asyncio.sleep(30)  # Wait for more volume
                continue
            
            # Execute slice
            current_price = await self._get_current_price(order.symbol)
            execution_price = current_price
            
            execution = ExecutionReport(
                report_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=slice_qty,
                filled_quantity=slice_qty,
                avg_fill_price=execution_price,
                commission=self._calculate_commission(slice_qty, execution_price),
                timestamp=datetime.now(),
                execution_id=str(uuid.uuid4())
            )
            
            order.filled_quantity += slice_qty
            order.executions.append(execution)
            remaining_quantity -= slice_qty
            
            # Update average fill price
            total_value = sum(e.filled_quantity * e.avg_fill_price for e in order.executions)
            order.avg_fill_price = total_value / order.filled_quantity
            
            if remaining_quantity == 0:
                order.status = OrderStatus.FILLED
                order.filled_at = datetime.now()
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
            
            # Wait based on market conditions
            await asyncio.sleep(30)  # 30 seconds between checks
        
        logger.info(f"Participation order {order.order_id} completed")
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an active order"""
        if order_id not in self.active_orders:
            return False
        
        order = self.active_orders[order_id]
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now()
        
        logger.info(f"Order {order_id} cancelled")
        return True
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current market price (mock implementation)"""
        # In production, integrate with real market data feed
        base_prices = {
            'RELIANCE': 2420.0,
            'TCS': 3680.0,
            'HDFC': 1580.0,
            'INFY': 1420.0,
            'ITC': 310.0
        }
        
        base_price = base_prices.get(symbol, 1000.0)
        # Add some random variation
        variation = np.random.normal(0, 0.002)  # 0.2% standard deviation
        return base_price * (1 + variation)
    
    async def _get_market_volume(self, symbol: str) -> int:
        """Get current market volume (mock implementation)"""
        # Mock volume data
        base_volumes = {
            'RELIANCE': 5000,
            'TCS': 3000,
            'HDFC': 4000,
            'INFY': 3500,
            'ITC': 8000
        }
        
        base_volume = base_volumes.get(symbol, 2000)
        return int(base_volume * (0.5 + np.random.random()))
    
    async def _get_vwap_price(self, symbol: str) -> float:
        """Get VWAP price (mock implementation)"""
        current_price = await self._get_current_price(symbol)
        # VWAP typically close to current price
        return current_price * (1 + np.random.normal(0, 0.001))
    
    def _calculate_market_impact(self, quantity: int, symbol: str) -> float:
        """Calculate market impact for order"""
        # Simplified market impact model
        avg_daily_volume = 1000000  # Mock average daily volume
        participation_rate = quantity / avg_daily_volume
        
        # Square root impact model
        impact = 0.01 * np.sqrt(participation_rate)  # 1% impact for 100% participation
        return min(impact, 0.05)  # Cap at 5%
    
    def _calculate_commission(self, quantity: int, price: float) -> float:
        """Calculate trading commission"""
        trade_value = quantity * price
        
        # Institutional rates (lower than retail)
        brokerage = min(trade_value * 0.0001, 20.0)  # 1 bps or ₹20, whichever is lower
        
        # Exchange charges
        exchange_charges = trade_value * 0.0000345
        
        # GST
        gst = (brokerage + exchange_charges) * 0.18
        
        return brokerage + exchange_charges + gst


# Example usage and testing
async def main():
    """Example usage of advanced order management"""
    
    # Initialize execution engine
    engine = ExecutionEngine()
    
    print("=== Advanced Order Management System Demo ===")
    
    # 1. Market Order
    market_order = AdvancedOrder(
        order_id=str(uuid.uuid4()),
        client_id="INST001",
        symbol="RELIANCE",
        side=OrderSide.BUY,
        quantity=1000,
        order_type=OrderType.MARKET,
        status=OrderStatus.PENDING
    )
    
    print(f"\n1. Submitting Market Order for {market_order.quantity} {market_order.symbol}")
    await engine.submit_order(market_order)
    print(f"   Status: {market_order.status.value}")
    if market_order.status == OrderStatus.FILLED:
        print(f"   Filled at: ₹{market_order.avg_fill_price:.2f}")
    
    # 2. Iceberg Order
    iceberg_order = AdvancedOrder(
        order_id=str(uuid.uuid4()),
        client_id="INST001",
        symbol="TCS",
        side=OrderSide.BUY,
        quantity=5000,
        order_type=OrderType.ICEBERG,
        status=OrderStatus.PENDING,
        display_quantity=500
    )
    
    print(f"\n2. Submitting Iceberg Order for {iceberg_order.quantity} {iceberg_order.symbol}")
    print(f"   Display Quantity: {iceberg_order.display_quantity}")
    await engine.submit_order(iceberg_order)
    print(f"   Status: {iceberg_order.status.value}")
    print(f"   Executions: {len(iceberg_order.executions)}")
    if iceberg_order.avg_fill_price > 0:
        print(f"   Average Fill Price: ₹{iceberg_order.avg_fill_price:.2f}")
    
    # 3. TWAP Order
    twap_order = AdvancedOrder(
        order_id=str(uuid.uuid4()),
        client_id="INST001",
        symbol="HDFC",
        side=OrderSide.SELL,
        quantity=2000,
        order_type=OrderType.TWAP,
        status=OrderStatus.PENDING,
        algorithm=ExecutionAlgorithm.TWAP,
        algorithm_params={'duration': 20, 'slice_interval': 5}  # 20 minutes, 5-minute slices
    )
    
    print(f"\n3. Submitting TWAP Order for {twap_order.quantity} {twap_order.symbol}")
    print(f"   Duration: {twap_order.algorithm_params['duration']} minutes")
    await engine.submit_order(twap_order)
    print(f"   Status: {twap_order.status.value}")
    print(f"   Executions: {len(twap_order.executions)}")
    if twap_order.avg_fill_price > 0:
        print(f"   Average Fill Price: ₹{twap_order.avg_fill_price:.2f}")
    
    # 4. VWAP Order
    vwap_order = AdvancedOrder(
        order_id=str(uuid.uuid4()),
        client_id="INST002",
        symbol="INFY",
        side=OrderSide.BUY,
        quantity=3000,
        order_type=OrderType.VWAP,
        status=OrderStatus.PENDING,
        algorithm=ExecutionAlgorithm.VWAP,
        algorithm_params={'participation_rate': 0.15, 'duration': 30}
    )
    
    print(f"\n4. Submitting VWAP Order for {vwap_order.quantity} {vwap_order.symbol}")
    print(f"   Participation Rate: {vwap_order.algorithm_params['participation_rate']:.1%}")
    await engine.submit_order(vwap_order)
    print(f"   Status: {vwap_order.status.value}")
    print(f"   Executions: {len(vwap_order.executions)}")
    if vwap_order.avg_fill_price > 0:
        print(f"   Average Fill Price: ₹{vwap_order.avg_fill_price:.2f}")
    
    print(f"\n=== Order Management Demo Complete ===")
    print(f"Active Orders: {len(engine.active_orders)}")


if __name__ == "__main__":
    asyncio.run(main())