#!/usr/bin/env python3
"""
GridWorks Institutional API Trading Interface
===========================================
RESTful + WebSocket APIs for institutional client integration
"""

import asyncio
import json
import uuid
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging
from pathlib import Path
import time
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import websockets
import redis

from .advanced_order_management import (
    AdvancedOrderManager, OrderType, OrderStatus, Order, 
    ExecutionReport, OrderPriority
)
from .hni_portfolio_management import (
    HNIPortfolioManager, PortfolioType, RiskProfile, 
    Portfolio, PortfolioAnalytics
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClientType(Enum):
    """API client types"""
    INSTITUTIONAL = "institutional"
    HNI = "hni"
    HEDGE_FUND = "hedge_fund"
    PROPRIETARY = "proprietary"
    RETAIL_PRO = "retail_pro"


class PermissionLevel(Enum):
    """API permission levels"""
    READ_ONLY = "read_only"
    TRADE_ENABLED = "trade_enabled"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    FULL_ACCESS = "full_access"


@dataclass
class APIClient:
    """Institutional API client configuration"""
    client_id: str
    client_name: str
    client_type: APIClientType
    permission_level: PermissionLevel
    api_key: str
    secret_key: str
    rate_limit: int = 1000  # requests per minute
    max_order_value: float = 10000000.0  # ₹1 Cr max per order
    max_portfolio_value: float = 100000000.0  # ₹10 Cr max portfolio
    allowed_order_types: List[OrderType] = field(default_factory=list)
    webhook_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


# Pydantic models for API requests/responses
class OrderRequest(BaseModel):
    """API order request model"""
    symbol: str
    order_type: str
    side: str  # "BUY" or "SELL"
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"  # DAY, GTC, IOC, FOK
    client_order_id: Optional[str] = None
    
    # Advanced order parameters
    display_quantity: Optional[int] = None  # For iceberg orders
    execution_time: Optional[int] = None    # For TWAP/VWAP in minutes
    discretionary_amount: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "order_type": "LIMIT",
                "side": "BUY",
                "quantity": 100,
                "price": 2450.50,
                "time_in_force": "DAY"
            }
        }


class OrderResponse(BaseModel):
    """API order response model"""
    order_id: str
    client_order_id: Optional[str]
    symbol: str
    status: str
    filled_quantity: int
    remaining_quantity: int
    avg_fill_price: Optional[float]
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "order_id": "ORD_12345678",
                "client_order_id": "CLIENT_001",
                "symbol": "RELIANCE",
                "status": "NEW",
                "filled_quantity": 0,
                "remaining_quantity": 100,
                "avg_fill_price": None,
                "timestamp": "2025-06-28T10:30:00Z"
            }
        }


class PortfolioRequest(BaseModel):
    """Portfolio management API request"""
    portfolio_name: str
    portfolio_type: str
    risk_profile: str
    target_allocation: Dict[str, float]
    investment_amount: float
    rebalancing_frequency: str = "QUARTERLY"
    
    class Config:
        schema_extra = {
            "example": {
                "portfolio_name": "Conservative Growth",
                "portfolio_type": "BALANCED",
                "risk_profile": "MODERATE",
                "target_allocation": {
                    "EQUITY": 0.6,
                    "DEBT": 0.3,
                    "CASH": 0.1
                },
                "investment_amount": 5000000.0,
                "rebalancing_frequency": "QUARTERLY"
            }
        }


class MarketDataFeed(BaseModel):
    """Real-time market data feed"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None


class InstitutionalAPIInterface:
    """Institutional API Trading Interface"""
    
    def __init__(self):
        self.app = FastAPI(
            title="GridWorks Institutional API",
            description="Enterprise-grade trading API for institutional clients",
            version="2.0.0"
        )
        
        # Initialize components
        self.order_manager = AdvancedOrderManager()
        self.portfolio_manager = HNIPortfolioManager()
        
        # Redis for rate limiting and session management
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # Active WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # API clients registry
        self.api_clients: Dict[str, APIClient] = {}
        
        # Security
        self.security = HTTPBearer()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        logger.info("Institutional API Interface initialized")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://institutional.gridworks.ai"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """API health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now(),
                "version": "2.0.0",
                "services": {
                    "order_management": "active",
                    "portfolio_management": "active",
                    "market_data": "active"
                }
            }
        
        @self.app.post("/auth/token")
        async def get_access_token(credentials: dict):
            """Generate JWT access token"""
            api_key = credentials.get("api_key")
            secret_key = credentials.get("secret_key")
            
            client = await self._authenticate_client(api_key, secret_key)
            if not client:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Generate JWT token
            payload = {
                "client_id": client.client_id,
                "client_type": client.client_type.value,
                "permission_level": client.permission_level.value,
                "exp": datetime.now() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, secret_key, algorithm="HS256")
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 86400,  # 24 hours
                "client_id": client.client_id,
                "permissions": client.permission_level.value
            }
        
        @self.app.post("/orders", response_model=OrderResponse)
        async def place_order(
            order_request: OrderRequest,
            client = Depends(self._get_current_client)
        ):
            """Place institutional order"""
            
            # Validate permissions
            if client.permission_level == PermissionLevel.READ_ONLY:
                raise HTTPException(status_code=403, detail="Trading not permitted")
            
            # Rate limiting check
            if not await self._check_rate_limit(client.client_id):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Validate order
            await self._validate_order(order_request, client)
            
            # Create order
            order = Order(
                order_id=str(uuid.uuid4()),
                client_id=client.client_id,
                symbol=order_request.symbol,
                order_type=OrderType(order_request.order_type.lower()),
                side=order_request.side,
                quantity=order_request.quantity,
                price=order_request.price,
                stop_price=order_request.stop_price,
                time_in_force=order_request.time_in_force,
                client_order_id=order_request.client_order_id,
                display_quantity=order_request.display_quantity,
                execution_time=order_request.execution_time,
                discretionary_amount=order_request.discretionary_amount
            )
            
            # Submit order
            result = await self.order_manager.place_order(order)
            
            # Send WebSocket notification
            await self._notify_order_update(client.client_id, result)
            
            return OrderResponse(
                order_id=result.order_id,
                client_order_id=result.client_order_id,
                symbol=result.symbol,
                status=result.status.value,
                filled_quantity=result.filled_quantity,
                remaining_quantity=result.remaining_quantity,
                avg_fill_price=result.avg_fill_price,
                timestamp=result.timestamp
            )
        
        @self.app.get("/orders/{order_id}")
        async def get_order_status(
            order_id: str,
            client = Depends(self._get_current_client)
        ):
            """Get order status"""
            order = await self.order_manager.get_order(order_id)
            
            if not order or order.client_id != client.client_id:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return {
                "order_id": order.order_id,
                "status": order.status.value,
                "filled_quantity": order.filled_quantity,
                "remaining_quantity": order.remaining_quantity,
                "avg_fill_price": order.avg_fill_price,
                "timestamp": order.timestamp,
                "executions": [asdict(exec) for exec in order.executions]
            }
        
        @self.app.delete("/orders/{order_id}")
        async def cancel_order(
            order_id: str,
            client = Depends(self._get_current_client)
        ):
            """Cancel order"""
            if client.permission_level == PermissionLevel.READ_ONLY:
                raise HTTPException(status_code=403, detail="Order cancellation not permitted")
            
            result = await self.order_manager.cancel_order(order_id, client.client_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="Order not found or cannot be cancelled")
            
            return {"message": "Order cancelled successfully", "order_id": order_id}
        
        @self.app.get("/orders")
        async def get_orders(
            client = Depends(self._get_current_client),
            status: Optional[str] = None,
            symbol: Optional[str] = None,
            limit: int = 100
        ):
            """Get client orders"""
            orders = await self.order_manager.get_client_orders(
                client.client_id, status, symbol, limit
            )
            
            return {
                "orders": [
                    {
                        "order_id": order.order_id,
                        "symbol": order.symbol,
                        "order_type": order.order_type.value,
                        "side": order.side,
                        "quantity": order.quantity,
                        "status": order.status.value,
                        "filled_quantity": order.filled_quantity,
                        "avg_fill_price": order.avg_fill_price,
                        "timestamp": order.timestamp
                    }
                    for order in orders
                ],
                "total": len(orders)
            }
        
        @self.app.post("/portfolios", response_model=dict)
        async def create_portfolio(
            portfolio_request: PortfolioRequest,
            client = Depends(self._get_current_client)
        ):
            """Create HNI portfolio"""
            
            if client.permission_level not in [PermissionLevel.PORTFOLIO_MANAGEMENT, PermissionLevel.FULL_ACCESS]:
                raise HTTPException(status_code=403, detail="Portfolio management not permitted")
            
            # Create portfolio
            portfolio = Portfolio(
                portfolio_id=str(uuid.uuid4()),
                client_id=client.client_id,
                name=portfolio_request.portfolio_name,
                portfolio_type=PortfolioType(portfolio_request.portfolio_type.lower()),
                risk_profile=RiskProfile(portfolio_request.risk_profile.lower()),
                target_allocation=portfolio_request.target_allocation,
                investment_amount=portfolio_request.investment_amount,
                rebalancing_frequency=portfolio_request.rebalancing_frequency
            )
            
            result = await self.portfolio_manager.create_portfolio(portfolio)
            
            return {
                "portfolio_id": result.portfolio_id,
                "name": result.name,
                "status": "created",
                "investment_amount": result.investment_amount,
                "target_allocation": result.target_allocation,
                "created_at": result.created_at
            }
        
        @self.app.get("/portfolios/{portfolio_id}/analytics")
        async def get_portfolio_analytics(
            portfolio_id: str,
            client = Depends(self._get_current_client)
        ):
            """Get portfolio analytics"""
            analytics = await self.portfolio_manager.get_portfolio_analytics(
                portfolio_id, client.client_id
            )
            
            if not analytics:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            return asdict(analytics)
        
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            
            # Authenticate WebSocket connection
            try:
                auth_data = await websocket.receive_json()
                client = await self._authenticate_websocket(auth_data, client_id)
                
                if not client:
                    await websocket.close(code=4001, reason="Authentication failed")
                    return
                
                # Store connection
                self.active_connections[client_id] = websocket
                
                logger.info(f"WebSocket connected: {client_id}")
                
                # Send connection confirmation
                await websocket.send_json({
                    "type": "connection",
                    "status": "connected",
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Keep connection alive and handle messages
                while True:
                    try:
                        message = await websocket.receive_json()
                        await self._handle_websocket_message(client, message)
                    except Exception as e:
                        logger.error(f"WebSocket error for {client_id}: {e}")
                        break
                        
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                await websocket.close(code=4000, reason="Connection error")
            
            finally:
                # Clean up connection
                if client_id in self.active_connections:
                    del self.active_connections[client_id]
                logger.info(f"WebSocket disconnected: {client_id}")
    
    async def _authenticate_client(self, api_key: str, secret_key: str) -> Optional[APIClient]:
        """Authenticate API client"""
        # In production, this would query a secure database
        # For now, using a mock implementation
        
        client_hash = hashlib.sha256(f"{api_key}:{secret_key}".encode()).hexdigest()
        
        # Mock client for demonstration
        if api_key == "INST_API_KEY_001":
            return APIClient(
                client_id="INST_001",
                client_name="Institutional Client Alpha",
                client_type=APIClientType.INSTITUTIONAL,
                permission_level=PermissionLevel.FULL_ACCESS,
                api_key=api_key,
                secret_key=secret_key,
                rate_limit=2000,
                max_order_value=50000000.0,  # ₹5 Cr
                allowed_order_types=[OrderType.MARKET, OrderType.LIMIT, OrderType.TWAP, OrderType.VWAP]
            )
        
        return None
    
    async def _get_current_client(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """Get current authenticated client from JWT token"""
        try:
            # Decode JWT token
            payload = jwt.decode(credentials.credentials, verify=False)  # In production, use proper secret
            client_id = payload.get("client_id")
            
            # Get client from registry
            client = self.api_clients.get(client_id)
            if not client:
                # Mock for demonstration
                client = APIClient(
                    client_id=client_id,
                    client_name="Test Client",
                    client_type=APIClientType.INSTITUTIONAL,
                    permission_level=PermissionLevel.FULL_ACCESS,
                    api_key="test_key",
                    secret_key="test_secret"
                )
            
            return client
            
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check API rate limiting"""
        key = f"rate_limit:{client_id}"
        current_minute = int(time.time() / 60)
        
        # Get current request count
        requests = self.redis_client.get(f"{key}:{current_minute}")
        
        if requests and int(requests) >= 1000:  # 1000 requests per minute limit
            return False
        
        # Increment counter
        pipe = self.redis_client.pipeline()
        pipe.incr(f"{key}:{current_minute}")
        pipe.expire(f"{key}:{current_minute}", 60)
        pipe.execute()
        
        return True
    
    async def _validate_order(self, order_request: OrderRequest, client: APIClient):
        """Validate order request"""
        
        # Check order value limits
        order_value = order_request.quantity * (order_request.price or 0)
        if order_value > client.max_order_value:
            raise HTTPException(
                status_code=400, 
                detail=f"Order value exceeds limit of ₹{client.max_order_value:,.2f}"
            )
        
        # Check allowed order types
        order_type = OrderType(order_request.order_type.lower())
        if client.allowed_order_types and order_type not in client.allowed_order_types:
            raise HTTPException(
                status_code=400,
                detail=f"Order type {order_type.value} not permitted for this client"
            )
        
        # Additional validations...
        if order_request.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        if order_request.price and order_request.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be positive")
    
    async def _notify_order_update(self, client_id: str, order_result):
        """Send order update via WebSocket"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json({
                    "type": "order_update",
                    "order_id": order_result.order_id,
                    "status": order_result.status.value,
                    "filled_quantity": order_result.filled_quantity,
                    "avg_fill_price": order_result.avg_fill_price,
                    "timestamp": order_result.timestamp.isoformat()
                })
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {e}")
    
    async def _authenticate_websocket(self, auth_data: dict, client_id: str) -> Optional[APIClient]:
        """Authenticate WebSocket connection"""
        # Simple token-based authentication for WebSocket
        token = auth_data.get("token")
        
        if not token:
            return None
        
        try:
            # Decode and validate token
            payload = jwt.decode(token, verify=False)
            if payload.get("client_id") == client_id:
                return await self._get_client_by_id(client_id)
        except:
            pass
        
        return None
    
    async def _get_client_by_id(self, client_id: str) -> Optional[APIClient]:
        """Get client by ID"""
        # Mock implementation
        return APIClient(
            client_id=client_id,
            client_name="WebSocket Client",
            client_type=APIClientType.INSTITUTIONAL,
            permission_level=PermissionLevel.FULL_ACCESS,
            api_key="ws_key",
            secret_key="ws_secret"
        )
    
    async def _handle_websocket_message(self, client: APIClient, message: dict):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")
        
        if message_type == "subscribe_market_data":
            symbols = message.get("symbols", [])
            # Subscribe to market data for symbols
            await self._subscribe_market_data(client.client_id, symbols)
        
        elif message_type == "ping":
            # Send pong response
            websocket = self.active_connections[client.client_id]
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _subscribe_market_data(self, client_id: str, symbols: List[str]):
        """Subscribe client to market data feed"""
        # In production, this would connect to actual market data feeds
        logger.info(f"Client {client_id} subscribed to market data: {symbols}")
        
        # Mock market data simulation
        websocket = self.active_connections[client_id]
        for symbol in symbols:
            await websocket.send_json({
                "type": "market_data",
                "symbol": symbol,
                "price": 2450.50,  # Mock price
                "volume": 1000,
                "timestamp": datetime.now().isoformat(),
                "bid": 2449.50,
                "ask": 2451.50,
                "bid_size": 500,
                "ask_size": 300
            })
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the API server"""
        import uvicorn
        
        logger.info(f"Starting Institutional API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


# Global API instance
institutional_api = InstitutionalAPIInterface()


async def main():
    """Main function for testing"""
    logger.info("GridWorks Institutional API Trading Interface")
    logger.info("=" * 50)
    
    # Start API server
    institutional_api.start_server()


if __name__ == "__main__":
    asyncio.run(main())