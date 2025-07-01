"""
WebSocket Manager for Real-time Chart Data

Handles real-time market data streaming for charts
with support for multiple symbols and timeframes.
"""

import asyncio
import json
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime, timedelta
import websockets
from websockets.server import WebSocketServerProtocol
import aiohttp
from collections import defaultdict
import numpy as np

from app.core.logging import logger
from app.core.config import settings


class DataAggregator:
    """Aggregates tick data into different timeframes"""
    
    def __init__(self):
        self.tick_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.candle_data: Dict[str, Dict[str, Any]] = {}  # symbol_timeframe -> current candle
        
    def add_tick(self, symbol: str, tick: Dict[str, Any]):
        """Add a tick and aggregate into candles"""
        
        self.tick_buffer[symbol].append(tick)
        
        # Update all timeframe candles
        for timeframe in ["1m", "5m", "15m", "30m", "1h", "1d"]:
            candle_key = f"{symbol}_{timeframe}"
            
            if candle_key not in self.candle_data:
                self.candle_data[candle_key] = self._create_new_candle(tick)
            else:
                self._update_candle(self.candle_data[candle_key], tick)
            
            # Check if candle is complete
            if self._is_candle_complete(self.candle_data[candle_key], timeframe):
                # Emit completed candle
                completed_candle = self.candle_data[candle_key].copy()
                self.candle_data[candle_key] = self._create_new_candle(tick)
                return completed_candle, timeframe
        
        return None, None
    
    def _create_new_candle(self, tick: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new candle from tick"""
        
        return {
            "timestamp": tick["timestamp"],
            "open": tick["price"],
            "high": tick["price"],
            "low": tick["price"],
            "close": tick["price"],
            "volume": tick.get("volume", 0),
            "tick_count": 1
        }
    
    def _update_candle(self, candle: Dict[str, Any], tick: Dict[str, Any]):
        """Update candle with new tick"""
        
        candle["high"] = max(candle["high"], tick["price"])
        candle["low"] = min(candle["low"], tick["price"])
        candle["close"] = tick["price"]
        candle["volume"] += tick.get("volume", 0)
        candle["tick_count"] += 1
    
    def _is_candle_complete(self, candle: Dict[str, Any], timeframe: str) -> bool:
        """Check if candle period is complete"""
        
        # Parse timeframe
        duration_map = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "1d": 86400
        }
        
        duration = duration_map.get(timeframe, 60)
        
        # Check if current time has passed candle period
        candle_time = datetime.fromisoformat(candle["timestamp"])
        current_time = datetime.now()
        
        return (current_time - candle_time).total_seconds() >= duration


class WebSocketManager:
    """
    Manages WebSocket connections for real-time chart data
    Handles both client connections and market data sources
    """
    
    def __init__(self, chart_manager):
        self.chart_manager = chart_manager
        
        # Client connections
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.client_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # client_id -> symbols
        
        # Market data connections
        self.market_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.symbol_subscriptions: Set[str] = set()
        
        # Data processing
        self.aggregator = DataAggregator()
        self.data_handlers: Dict[str, Callable] = {}
        
        # Server
        self.server = None
        self.server_task = None
        self._running = False
        
        # Performance
        self.message_count = 0
        self.last_message_time = datetime.now()
        
    async def start(self):
        """Start WebSocket server and connections"""
        
        self._running = True
        
        # Start WebSocket server for clients
        self.server = await websockets.serve(
            self.handle_client,
            "localhost",
            8765,
            compression=None  # Disable compression for lower latency
        )
        
        # Start market data connections
        await self._connect_to_market_data()
        
        logger.info("WebSocket Manager started on port 8765")
    
    async def stop(self):
        """Stop WebSocket server and connections"""
        
        self._running = False
        
        # Close client connections
        for client in list(self.clients.values()):
            await client.close()
        
        # Close market connections
        for conn in self.market_connections.values():
            await conn.close()
        
        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("WebSocket Manager stopped")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client WebSocket connection"""
        
        client_id = f"client_{id(websocket)}"
        self.clients[client_id] = websocket
        
        logger.info(f"Client {client_id} connected")
        
        try:
            async for message in websocket:
                await self._process_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Cleanup
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
    
    async def _process_client_message(self, client_id: str, message: str):
        """Process message from client"""
        
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "subscribe":
                await self._handle_subscribe(client_id, data)
            elif action == "unsubscribe":
                await self._handle_unsubscribe(client_id, data)
            elif action == "ping":
                await self._handle_ping(client_id)
            else:
                logger.warning(f"Unknown action from {client_id}: {action}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {client_id}: {message}")
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
    
    async def _handle_subscribe(self, client_id: str, data: Dict[str, Any]):
        """Handle subscribe request"""
        
        symbols = data.get("symbols", [])
        
        for symbol in symbols:
            self.client_subscriptions[client_id].add(symbol)
            
            # Subscribe to market data if needed
            if symbol not in self.symbol_subscriptions:
                await self.subscribe_to_symbol(symbol)
        
        # Send confirmation
        if client_id in self.clients:
            await self.clients[client_id].send(json.dumps({
                "type": "subscribe_confirm",
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def _handle_unsubscribe(self, client_id: str, data: Dict[str, Any]):
        """Handle unsubscribe request"""
        
        symbols = data.get("symbols", [])
        
        for symbol in symbols:
            self.client_subscriptions[client_id].discard(symbol)
        
        # Send confirmation
        if client_id in self.clients:
            await self.clients[client_id].send(json.dumps({
                "type": "unsubscribe_confirm",
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def _handle_ping(self, client_id: str):
        """Handle ping request"""
        
        if client_id in self.clients:
            await self.clients[client_id].send(json.dumps({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }))
    
    async def subscribe_to_symbol(self, symbol: str):
        """Subscribe to market data for a symbol"""
        
        if symbol in self.symbol_subscriptions:
            return
        
        self.symbol_subscriptions.add(symbol)
        
        # Send subscription to market data provider
        # This would connect to actual market data feed
        # For now, start simulated data
        asyncio.create_task(self._simulate_market_data(symbol))
        
        logger.info(f"Subscribed to market data for {symbol}")
    
    async def unsubscribe_from_symbol(self, symbol: str):
        """Unsubscribe from market data for a symbol"""
        
        if symbol not in self.symbol_subscriptions:
            return
        
        self.symbol_subscriptions.remove(symbol)
        
        # Send unsubscribe to market data provider
        logger.info(f"Unsubscribed from market data for {symbol}")
    
    async def broadcast_data_update(self, symbol: str, data: Dict[str, Any]):
        """Broadcast data update to subscribed clients"""
        
        # Find clients subscribed to this symbol
        interested_clients = [
            client_id for client_id, symbols in self.client_subscriptions.items()
            if symbol in symbols
        ]
        
        if not interested_clients:
            return
        
        # Prepare message
        message = json.dumps({
            "type": "data_update",
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send to all interested clients
        disconnected_clients = []
        
        for client_id in interested_clients:
            if client_id in self.clients:
                try:
                    await self.clients[client_id].send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.append(client_id)
                except Exception as e:
                    logger.error(f"Error sending to {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
        
        # Update metrics
        self.message_count += len(interested_clients) - len(disconnected_clients)
    
    async def broadcast_layout_change(self, session_id: str, layout: Any):
        """Broadcast layout change to clients"""
        
        # Find clients in this session
        # For now, broadcast to all clients
        message = json.dumps({
            "type": "layout_change",
            "session_id": session_id,
            "layout": layout.value if hasattr(layout, "value") else str(layout),
            "timestamp": datetime.now().isoformat()
        })
        
        for client_id, client in list(self.clients.items()):
            try:
                await client.send(message)
            except Exception as e:
                logger.error(f"Error broadcasting layout change to {client_id}: {e}")
    
    async def _connect_to_market_data(self):
        """Connect to market data providers"""
        
        # In production, this would connect to real market data feeds
        # For now, we'll simulate connections
        
        # Example: Connect to NSE data feed
        # self.market_connections["nse"] = await websockets.connect("wss://nse-feed.example.com")
        
        logger.info("Connected to market data providers")
    
    async def _simulate_market_data(self, symbol: str):
        """Simulate market data for testing"""
        
        # Initial price
        base_prices = {
            "NIFTY": 20000,
            "BANKNIFTY": 45000,
            "RELIANCE": 2500,
            "TCS": 3500,
            "HDFC": 1600,
            "ICICI": 950,
            "INFY": 1400
        }
        
        base_price = base_prices.get(symbol, 1000)
        last_price = base_price
        
        while symbol in self.symbol_subscriptions and self._running:
            try:
                # Generate random tick
                change = np.random.normal(0, 0.001)  # 0.1% volatility
                last_price *= (1 + change)
                
                # Create tick data
                tick = {
                    "symbol": symbol,
                    "price": round(last_price, 2),
                    "volume": np.random.randint(100, 1000),
                    "timestamp": datetime.now().isoformat(),
                    "bid": round(last_price * 0.9995, 2),
                    "ask": round(last_price * 1.0005, 2)
                }
                
                # Process tick through aggregator
                candle, timeframe = self.aggregator.add_tick(symbol, tick)
                
                # Broadcast tick data
                await self.broadcast_data_update(symbol, {
                    "type": "tick",
                    **tick
                })
                
                # If candle completed, update charts
                if candle:
                    candle_data = {
                        "type": "candle",
                        "timeframe": timeframe,
                        **candle
                    }
                    
                    # Update chart manager
                    await self.chart_manager.update_chart_data(symbol, candle)
                    
                    # Broadcast candle update
                    await self.broadcast_data_update(symbol, candle_data)
                
                # Simulate market hours (9:15 AM - 3:30 PM IST)
                current_time = datetime.now()
                market_open = current_time.replace(hour=9, minute=15, second=0)
                market_close = current_time.replace(hour=15, minute=30, second=0)
                
                if current_time < market_open or current_time > market_close:
                    # Outside market hours, slow down updates
                    await asyncio.sleep(5)
                else:
                    # During market hours, fast updates
                    await asyncio.sleep(0.1)  # 10 updates per second
                    
            except Exception as e:
                logger.error(f"Error simulating data for {symbol}: {e}")
                await asyncio.sleep(1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get WebSocket metrics"""
        
        current_time = datetime.now()
        time_diff = (current_time - self.last_message_time).total_seconds()
        
        messages_per_second = self.message_count / time_diff if time_diff > 0 else 0
        
        metrics = {
            "connected_clients": len(self.clients),
            "active_subscriptions": len(self.symbol_subscriptions),
            "messages_sent": self.message_count,
            "messages_per_second": round(messages_per_second, 2),
            "client_subscriptions": {
                client_id: list(symbols)
                for client_id, symbols in self.client_subscriptions.items()
            }
        }
        
        # Reset counters
        self.message_count = 0
        self.last_message_time = current_time
        
        return metrics