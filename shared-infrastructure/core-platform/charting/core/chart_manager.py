"""
Chart Manager - Central orchestrator for charting platform

Manages multiple charts, layouts, and real-time data feeds.
Provides the main interface for the charting platform.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from enum import Enum

from .chart_engine import ChartEngine, ChartConfig, ChartType, TimeFrame, OHLCV
from ..data_feeds.websocket_manager import WebSocketManager
from ..layouts.layout_manager import LayoutManager
from app.core.logging import logger
from app.core.redis_client import redis_client


class ChartLayout(Enum):
    """Available chart layouts"""
    SINGLE = "single"
    SPLIT_HORIZONTAL = "split_horizontal"
    SPLIT_VERTICAL = "split_vertical"
    GRID_2X2 = "grid_2x2"
    GRID_3X3 = "grid_3x3"
    CUSTOM = "custom"


@dataclass
class ChartSession:
    """User's chart session"""
    user_id: str
    session_id: str
    charts: List[str] = field(default_factory=list)
    layout: ChartLayout = ChartLayout.SINGLE
    active_chart: Optional[str] = None
    watchlist: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class ChartManager:
    """
    Central manager for the charting platform
    Coordinates charts, data feeds, layouts, and user sessions
    """
    
    def __init__(self):
        self.engine = ChartEngine()
        self.websocket_manager = WebSocketManager(self)
        self.layout_manager = LayoutManager()
        
        # User sessions
        self.sessions: Dict[str, ChartSession] = {}
        
        # Symbol subscriptions
        self.symbol_subscribers: Dict[str, Set[str]] = {}  # symbol -> set of session_ids
        
        # Performance monitoring
        self.metrics = {
            "active_charts": 0,
            "active_sessions": 0,
            "data_points_processed": 0,
            "average_render_time": 0
        }
        
        # Background tasks
        self._background_tasks = []
        self._running = False
        
    async def initialize(self):
        """Initialize the chart manager"""
        
        # Start WebSocket manager
        await self.websocket_manager.start()
        
        # Start background tasks
        self._running = True
        self._background_tasks.append(
            asyncio.create_task(self._cleanup_inactive_sessions())
        )
        self._background_tasks.append(
            asyncio.create_task(self._monitor_performance())
        )
        
        logger.info("Chart Manager initialized")
    
    async def create_session(
        self,
        user_id: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new chart session for a user"""
        
        import uuid
        session_id = str(uuid.uuid4())
        
        session = ChartSession(
            user_id=user_id,
            session_id=session_id,
            preferences=preferences or {}
        )
        
        self.sessions[session_id] = session
        self.metrics["active_sessions"] += 1
        
        # Store session in Redis for persistence
        await self._save_session_to_redis(session)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def create_chart(
        self,
        session_id: str,
        symbol: str,
        chart_type: ChartType = ChartType.CANDLESTICK,
        timeframe: TimeFrame = TimeFrame.M5,
        **kwargs
    ) -> str:
        """Create a new chart in a session"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Create chart configuration
        config = ChartConfig(
            symbol=symbol,
            chart_type=chart_type,
            timeframe=timeframe,
            **kwargs
        )
        
        # Create chart ID
        chart_id = f"{session_id}_{symbol}_{timeframe.value}"
        
        # Create chart through engine
        chart = await self.engine.create_chart(chart_id, config)
        
        # Add to session
        session.charts.append(chart_id)
        if not session.active_chart:
            session.active_chart = chart_id
        
        # Subscribe to symbol data
        await self._subscribe_to_symbol(symbol, session_id)
        
        # Update metrics
        self.metrics["active_charts"] += 1
        
        # Update session activity
        session.last_activity = datetime.now()
        
        logger.info(f"Created chart {chart_id} in session {session_id}")
        return chart_id
    
    async def update_chart_data(
        self,
        symbol: str,
        data: Dict[str, Any]
    ):
        """Update charts with new market data"""
        
        # Convert to OHLCV
        ohlcv = OHLCV(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"]
        )
        
        # Update through engine
        await self.engine.update_chart_data(symbol, ohlcv)
        
        # Update metrics
        self.metrics["data_points_processed"] += 1
        
        # Broadcast to WebSocket clients
        await self.websocket_manager.broadcast_data_update(symbol, data)
    
    async def add_indicator(
        self,
        session_id: str,
        chart_id: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> str:
        """Add indicator to a chart"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if chart_id not in self.sessions[session_id].charts:
            raise ValueError(f"Chart {chart_id} not in session")
        
        # Add through engine
        indicator_id = await self.engine.add_indicator(
            chart_id,
            indicator_type,
            params
        )
        
        # Update session activity
        self.sessions[session_id].last_activity = datetime.now()
        
        return indicator_id
    
    async def add_drawing(
        self,
        session_id: str,
        chart_id: str,
        drawing_type: str,
        points: List[Dict[str, float]],
        style: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add drawing to a chart"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if chart_id not in self.sessions[session_id].charts:
            raise ValueError(f"Chart {chart_id} not in session")
        
        # Add through engine
        drawing_id = await self.engine.add_drawing(
            chart_id,
            drawing_type,
            points,
            style
        )
        
        # Update session activity
        self.sessions[session_id].last_activity = datetime.now()
        
        return drawing_id
    
    async def execute_voice_command(
        self,
        session_id: str,
        command: str
    ) -> Dict[str, Any]:
        """Execute voice command on active chart"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        if not session.active_chart:
            return {
                "success": False,
                "message": "No active chart. Please open a chart first."
            }
        
        # Check for chart switching commands
        command_lower = command.lower()
        
        # Symbol switching
        symbols = ["nifty", "banknifty", "reliance", "tcs", "hdfc", "icici", "infy"]
        for symbol in symbols:
            if symbol in command_lower:
                # Switch to or create chart for this symbol
                await self._switch_or_create_chart(session_id, symbol.upper())
                return {
                    "success": True,
                    "action": "chart_switched",
                    "message": f"Switched to {symbol.upper()} chart"
                }
        
        # Timeframe switching
        timeframe_map = {
            "1 minute": TimeFrame.M1,
            "5 minute": TimeFrame.M5,
            "15 minute": TimeFrame.M15,
            "hourly": TimeFrame.H1,
            "daily": TimeFrame.D1,
            "weekly": TimeFrame.W1
        }
        
        for phrase, tf in timeframe_map.items():
            if phrase in command_lower:
                await self._change_timeframe(session_id, session.active_chart, tf)
                return {
                    "success": True,
                    "action": "timeframe_changed",
                    "message": f"Changed to {phrase} timeframe"
                }
        
        # Layout commands
        if "split" in command_lower:
            if "horizontal" in command_lower:
                await self.change_layout(session_id, ChartLayout.SPLIT_HORIZONTAL)
            else:
                await self.change_layout(session_id, ChartLayout.SPLIT_VERTICAL)
            return {
                "success": True,
                "action": "layout_changed",
                "message": "Layout changed"
            }
        
        # Otherwise, pass to active chart
        result = await self.engine.execute_voice_command(
            session.active_chart,
            command
        )
        
        # Update session activity
        session.last_activity = datetime.now()
        
        return result
    
    async def change_layout(
        self,
        session_id: str,
        layout: ChartLayout
    ):
        """Change chart layout for a session"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session.layout = layout
        
        # Apply layout through layout manager
        await self.layout_manager.apply_layout(
            session.charts,
            layout
        )
        
        # Update session activity
        session.last_activity = datetime.now()
        
        # Notify WebSocket clients
        await self.websocket_manager.broadcast_layout_change(
            session_id,
            layout
        )
    
    async def save_chart_template(
        self,
        session_id: str,
        chart_id: str,
        template_name: str
    ) -> str:
        """Save chart configuration as template"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if chart_id not in self.engine.charts:
            raise ValueError(f"Chart {chart_id} not found")
        
        chart = self.engine.charts[chart_id]
        
        # Create template
        template = {
            "name": template_name,
            "chart_type": chart.config.chart_type.value,
            "timeframe": chart.config.timeframe.value,
            "indicators": [
                {
                    "type": ind["type"],
                    "params": ind["params"]
                }
                for ind in chart.indicators.values()
            ],
            "drawings": [
                drawing.to_dict()
                for drawing in chart.drawings.values()
            ],
            "theme": chart.config.theme,
            "created_at": datetime.now().isoformat()
        }
        
        # Save to Redis
        template_id = f"template_{session_id}_{template_name}"
        await redis_client.set(
            f"chart_template:{template_id}",
            json.dumps(template),
            ex=86400 * 30  # 30 days
        )
        
        logger.info(f"Saved chart template {template_id}")
        return template_id
    
    async def apply_template(
        self,
        session_id: str,
        chart_id: str,
        template_id: str
    ):
        """Apply saved template to a chart"""
        
        # Load template from Redis
        template_data = await redis_client.get(f"chart_template:{template_id}")
        if not template_data:
            raise ValueError(f"Template {template_id} not found")
        
        template = json.loads(template_data)
        
        # Apply indicators
        for indicator in template["indicators"]:
            await self.add_indicator(
                session_id,
                chart_id,
                indicator["type"],
                indicator["params"]
            )
        
        # Note: Drawings would need timestamp/price adjustment
        
        logger.info(f"Applied template {template_id} to chart {chart_id}")
    
    async def create_alert(
        self,
        session_id: str,
        chart_id: str,
        condition: Dict[str, Any],
        notification_channels: List[str]
    ) -> str:
        """Create alert on a chart"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if chart_id not in self.sessions[session_id].charts:
            raise ValueError(f"Chart {chart_id} not in session")
        
        # Create through engine
        alert_id = await self.engine.create_alert(
            chart_id,
            condition,
            notification_channels
        )
        
        # Store alert metadata
        alert_data = {
            "alert_id": alert_id,
            "session_id": session_id,
            "chart_id": chart_id,
            "condition": condition,
            "channels": notification_channels,
            "created_at": datetime.now().isoformat()
        }
        
        await redis_client.set(
            f"chart_alert:{alert_id}",
            json.dumps(alert_data),
            ex=86400 * 7  # 7 days
        )
        
        return alert_id
    
    async def share_chart(
        self,
        session_id: str,
        chart_id: str,
        share_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Share chart with social features"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if chart_id not in self.sessions[session_id].charts:
            raise ValueError(f"Chart {chart_id} not in session")
        
        # Generate share data through engine
        share_data = await self.engine.share_chart(
            chart_id,
            share_options
        )
        
        # Store share metadata
        share_id = f"share_{chart_id}_{datetime.now().timestamp()}"
        await redis_client.set(
            f"chart_share:{share_id}",
            json.dumps(share_data),
            ex=86400  # 24 hours
        )
        
        # Generate shareable link
        share_data["share_url"] = f"https://gridworks.ai/charts/shared/{share_id}"
        share_data["whatsapp_url"] = f"https://wa.me/?text=Check%20out%20my%20chart%20analysis%20{share_data['share_url']}"
        
        return share_data
    
    async def get_chart_image(
        self,
        session_id: str,
        chart_id: str,
        width: int = 800,
        height: int = 600
    ) -> bytes:
        """Get chart as image for WhatsApp"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if chart_id not in self.sessions[session_id].charts:
            raise ValueError(f"Chart {chart_id} not in session")
        
        # Generate image through engine
        image_data = await self.engine.get_chart_image(
            chart_id,
            width,
            height,
            "png"
        )
        
        return image_data
    
    async def _subscribe_to_symbol(self, symbol: str, session_id: str):
        """Subscribe session to symbol data"""
        
        if symbol not in self.symbol_subscribers:
            self.symbol_subscribers[symbol] = set()
            
            # Start data feed if first subscriber
            await self.websocket_manager.subscribe_to_symbol(symbol)
        
        self.symbol_subscribers[symbol].add(session_id)
    
    async def _unsubscribe_from_symbol(self, symbol: str, session_id: str):
        """Unsubscribe session from symbol data"""
        
        if symbol in self.symbol_subscribers:
            self.symbol_subscribers[symbol].discard(session_id)
            
            # Stop data feed if no subscribers
            if not self.symbol_subscribers[symbol]:
                await self.websocket_manager.unsubscribe_from_symbol(symbol)
                del self.symbol_subscribers[symbol]
    
    async def _switch_or_create_chart(self, session_id: str, symbol: str):
        """Switch to existing chart or create new one"""
        
        session = self.sessions[session_id]
        
        # Check if chart exists
        for chart_id in session.charts:
            if symbol in chart_id:
                session.active_chart = chart_id
                return
        
        # Create new chart
        chart_id = await self.create_chart(session_id, symbol)
        session.active_chart = chart_id
    
    async def _change_timeframe(
        self,
        session_id: str,
        chart_id: str,
        timeframe: TimeFrame
    ):
        """Change timeframe for a chart"""
        
        # This would recreate the chart with new timeframe
        # For now, just log
        logger.info(f"Changing timeframe for {chart_id} to {timeframe.value}")
    
    async def _save_session_to_redis(self, session: ChartSession):
        """Save session to Redis for persistence"""
        
        session_data = {
            "user_id": session.user_id,
            "session_id": session.session_id,
            "charts": session.charts,
            "layout": session.layout.value,
            "active_chart": session.active_chart,
            "watchlist": session.watchlist,
            "preferences": session.preferences,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
        
        await redis_client.set(
            f"chart_session:{session.session_id}",
            json.dumps(session_data),
            ex=86400  # 24 hours
        )
    
    async def _cleanup_inactive_sessions(self):
        """Background task to cleanup inactive sessions"""
        
        while self._running:
            try:
                current_time = datetime.now()
                inactive_sessions = []
                
                for session_id, session in self.sessions.items():
                    # Remove sessions inactive for more than 1 hour
                    if current_time - session.last_activity > timedelta(hours=1):
                        inactive_sessions.append(session_id)
                
                # Cleanup inactive sessions
                for session_id in inactive_sessions:
                    await self._cleanup_session(session_id)
                
                # Run every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_session(self, session_id: str):
        """Cleanup a session and its resources"""
        
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        # Cleanup charts
        for chart_id in session.charts:
            if chart_id in self.engine.charts:
                await self.engine.charts[chart_id].cleanup()
                del self.engine.charts[chart_id]
        
        # Unsubscribe from symbols
        for symbol in list(self.symbol_subscribers.keys()):
            await self._unsubscribe_from_symbol(symbol, session_id)
        
        # Remove session
        del self.sessions[session_id]
        self.metrics["active_sessions"] -= 1
        self.metrics["active_charts"] -= len(session.charts)
        
        # Remove from Redis
        await redis_client.delete(f"chart_session:{session_id}")
        
        logger.info(f"Cleaned up session {session_id}")
    
    async def _monitor_performance(self):
        """Background task to monitor performance"""
        
        while self._running:
            try:
                # Calculate average render time
                if self.engine.render_times:
                    self.metrics["average_render_time"] = sum(self.engine.render_times) / len(self.engine.render_times)
                    self.engine.render_times = []  # Reset
                
                # Log metrics
                logger.info(f"Chart metrics: {self.metrics}")
                
                # Store in Redis for monitoring
                await redis_client.set(
                    "chart_metrics",
                    json.dumps(self.metrics),
                    ex=300  # 5 minutes
                )
                
                # Run every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Shutdown the chart manager"""
        
        self._running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Cleanup all sessions
        for session_id in list(self.sessions.keys()):
            await self._cleanup_session(session_id)
        
        # Shutdown WebSocket manager
        await self.websocket_manager.stop()
        
        # Cleanup engine
        await self.engine.cleanup()
        
        logger.info("Chart Manager shut down")