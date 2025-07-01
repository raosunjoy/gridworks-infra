"""?
GridWorks Performance Monitoring System

Monitors charting platform performance, user interactions, and system metrics.
Provides real-time analytics and alerts for production and beta environments.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import asyncio
import json
import time
import psutil
import aioredis
from contextlib import asynccontextmanager

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.logging import logger
from app.models.performance import PerformanceMetric, UserInteraction, SystemMetric
from app.services.notification import NotificationService

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Pydantic models
class PerformanceMetricRequest(BaseModel):
    metric_name: str
    value: float
    unit: str = Field(default="ms")
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    chart_id: Optional[str] = None
    feature: Optional[str] = None
    timestamp: Optional[datetime] = None

class UserInteractionRequest(BaseModel):
    interaction_type: str
    feature: str
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: str
    timestamp: Optional[datetime] = None

class SystemMetricRequest(BaseModel):
    metric_type: str
    value: float
    unit: str
    component: str
    timestamp: Optional[datetime] = None

class AlertConfigRequest(BaseModel):
    metric_name: str
    threshold: float
    comparison: str = Field(..., regex="^(gt|lt|gte|lte|eq)$")
    window_minutes: int = Field(default=5, ge=1, le=60)
    notification_channels: List[str] = Field(default_factory=list)

# Response models
class PerformanceStatsResponse(BaseModel):
    chart_load_time: Dict[str, float]
    indicator_calculation_time: Dict[str, float]
    websocket_latency: Dict[str, float]
    user_interactions: Dict[str, int]
    error_rate: float
    active_sessions: int

class SystemStatsResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_times: Dict[str, float]


class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self):
        self.redis = None
        self.notification_service = NotificationService()
        self.alert_configs = {}
        self.running = False
        
        # Performance thresholds
        self.thresholds = {
            'chart_load_time': 500,  # ms
            'indicator_calculation': 100,  # ms
            'websocket_latency': 100,  # ms
            'error_rate': 5,  # %
            'memory_usage': 80,  # %
            'cpu_usage': 70  # %
        }
        
        # Metrics cache
        self.metrics_cache = {
            'performance': {},
            'interactions': {},
            'system': {}
        }
    
    async def initialize(self):
        """Initialize monitoring system"""
        try:
            self.redis = await aioredis.from_url("redis://localhost:6379")
            self.running = True
            
            # Start background monitoring tasks
            asyncio.create_task(self.system_metrics_collector())
            asyncio.create_task(self.alert_processor())
            
            logger.info("Performance monitoring system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
    
    async def record_performance_metric(
        self, 
        db: Session, 
        user_id: str, 
        metric: PerformanceMetricRequest
    ) -> PerformanceMetric:
        """Record a performance metric"""
        
        try:
            # Create database record
            perf_metric = PerformanceMetric(
                user_id=user_id,
                metric_name=metric.metric_name,
                value=metric.value,
                unit=metric.unit,
                context=json.dumps(metric.context),
                session_id=metric.session_id,
                chart_id=metric.chart_id,
                feature=metric.feature,
                timestamp=metric.timestamp or datetime.utcnow()
            )
            
            db.add(perf_metric)
            db.commit()
            db.refresh(perf_metric)
            
            # Cache metric for real-time monitoring
            await self._cache_performance_metric(metric)
            
            # Check for alerts
            await self._check_performance_alerts(metric)
            
            return perf_metric
        
        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")
            raise
    
    async def record_user_interaction(
        self, 
        db: Session, 
        user_id: str, 
        interaction: UserInteractionRequest
    ) -> UserInteraction:
        """Record a user interaction"""
        
        try:
            # Create database record
            user_interaction = UserInteraction(
                user_id=user_id,
                interaction_type=interaction.interaction_type,
                feature=interaction.feature,
                duration_ms=interaction.duration_ms,
                success=interaction.success,
                error_message=interaction.error_message,
                context=json.dumps(interaction.context),
                session_id=interaction.session_id,
                timestamp=interaction.timestamp or datetime.utcnow()
            )
            
            db.add(user_interaction)
            db.commit()
            db.refresh(user_interaction)
            
            # Cache for analytics
            await self._cache_user_interaction(interaction)
            
            return user_interaction
        
        except Exception as e:
            logger.error(f"Error recording user interaction: {e}")
            raise
    
    async def _cache_performance_metric(self, metric: PerformanceMetricRequest):
        """Cache performance metric in Redis"""
        
        if not self.redis:
            return
        
        try:
            # Store in time-series format
            key = f"perf:{metric.metric_name}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            
            await self.redis.zadd(
                key,
                {json.dumps({
                    'value': metric.value,
                    'timestamp': time.time(),
                    'context': metric.context
                }): time.time()}
            )
            
            # Set expiration (24 hours)
            await self.redis.expire(key, 86400)
            
            # Update real-time stats
            await self.redis.hset(
                "perf:current",
                metric.metric_name,
                metric.value
            )
        
        except Exception as e:
            logger.error(f"Error caching performance metric: {e}")
    
    async def _cache_user_interaction(self, interaction: UserInteractionRequest):
        """Cache user interaction in Redis"""
        
        if not self.redis:
            return
        
        try:
            # Count interactions by feature
            await self.redis.hincrby(
                "interactions:count",
                f"{interaction.feature}:{interaction.interaction_type}",
                1
            )
            
            # Track errors
            if not interaction.success:
                await self.redis.hincrby(
                    "interactions:errors",
                    interaction.feature,
                    1
                )
        
        except Exception as e:
            logger.error(f"Error caching user interaction: {e}")
    
    async def _check_performance_alerts(self, metric: PerformanceMetricRequest):
        """Check if metric triggers any alerts"""
        
        threshold = self.thresholds.get(metric.metric_name)
        if not threshold:
            return
        
        if metric.metric_name in ['chart_load_time', 'indicator_calculation', 'websocket_latency']:
            if metric.value > threshold:
                await self._trigger_alert(
                    f"High {metric.metric_name.replace('_', ' ')}",
                    f"{metric.metric_name} is {metric.value}{metric.unit}, exceeding threshold of {threshold}{metric.unit}",
                    'warning',
                    metric.context
                )
    
    async def _trigger_alert(
        self, 
        title: str, 
        message: str, 
        severity: str, 
        context: Dict[str, Any]
    ):
        """Trigger performance alert"""
        
        try:
            # Log alert
            logger.warning(f"Performance Alert - {title}: {message}")
            
            # Send notification
            await self.notification_service.send_alert(
                title=title,
                message=message,
                severity=severity,
                context=context,
                channels=['slack', 'email']
            )
        
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def system_metrics_collector(self):
        """Background task to collect system metrics"""
        
        while self.running:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                metrics = {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': (disk.used / disk.total) * 100,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                }
                
                # Cache metrics
                if self.redis:
                    await self.redis.hset(
                        "system:current",
                        mapping=metrics
                    )
                
                # Check system alerts
                if cpu_percent > self.thresholds['cpu_usage']:
                    await self._trigger_alert(
                        "High CPU Usage",
                        f"CPU usage is {cpu_percent}%, exceeding threshold of {self.thresholds['cpu_usage']}%",
                        'warning',
                        {'cpu_percent': cpu_percent}
                    )
                
                if memory.percent > self.thresholds['memory_usage']:
                    await self._trigger_alert(
                        "High Memory Usage",
                        f"Memory usage is {memory.percent}%, exceeding threshold of {self.thresholds['memory_usage']}%",
                        'warning',
                        {'memory_percent': memory.percent}
                    )
                
                await asyncio.sleep(30)  # Collect every 30 seconds
            
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def alert_processor(self):
        """Background task to process alerts"""
        
        while self.running:
            try:
                # Process any pending alerts
                await asyncio.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(60)
    
    async def get_performance_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance statistics"""
        
        if not self.redis:
            return {}
        
        try:
            # Get current metrics
            current_metrics = await self.redis.hgetall("perf:current")
            
            # Get interaction counts
            interactions = await self.redis.hgetall("interactions:count")
            errors = await self.redis.hgetall("interactions:errors")
            
            # Calculate error rate
            total_interactions = sum(int(count) for count in interactions.values())
            total_errors = sum(int(count) for count in errors.values())
            error_rate = (total_errors / total_interactions * 100) if total_interactions > 0 else 0
            
            return {
                'chart_load_time': {
                    'current': float(current_metrics.get('chart_load_time', 0)),
                    'threshold': self.thresholds['chart_load_time']
                },
                'indicator_calculation_time': {
                    'current': float(current_metrics.get('indicator_calculation', 0)),
                    'threshold': self.thresholds['indicator_calculation']
                },
                'websocket_latency': {
                    'current': float(current_metrics.get('websocket_latency', 0)),
                    'threshold': self.thresholds['websocket_latency']
                },
                'user_interactions': dict(interactions),
                'error_rate': round(error_rate, 2),
                'active_sessions': len(await self.redis.keys("session:*"))
            }
        
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        
        if not self.redis:
            return {}
        
        try:
            system_metrics = await self.redis.hgetall("system:current")
            
            return {
                'cpu_usage': float(system_metrics.get('cpu_usage', 0)),
                'memory_usage': float(system_metrics.get('memory_usage', 0)),
                'disk_usage': float(system_metrics.get('disk_usage', 0)),
                'network_io': {
                    'bytes_sent': int(system_metrics.get('network_bytes_sent', 0)),
                    'bytes_recv': int(system_metrics.get('network_bytes_recv', 0))
                },
                'active_connections': 0,  # Would need to implement connection tracking
                'response_times': {}  # Would come from application metrics
            }
        
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}


# Initialize performance monitor
perf_monitor = PerformanceMonitor()


# API Endpoints
@router.post("/performance")
async def record_performance(
    metric: PerformanceMetricRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a performance metric"""
    
    try:
        perf_metric = await perf_monitor.record_performance_metric(
            db, user["id"], metric
        )
        
        return {
            "success": True,
            "metric_id": perf_metric.id,
            "message": "Performance metric recorded"
        }
    
    except Exception as e:
        logger.error(f"Performance recording error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction")
async def record_interaction(
    interaction: UserInteractionRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a user interaction"""
    
    try:
        user_interaction = await perf_monitor.record_user_interaction(
            db, user["id"], interaction
        )
        
        return {
            "success": True,
            "interaction_id": user_interaction.id,
            "message": "Interaction recorded"
        }
    
    except Exception as e:
        logger.error(f"Interaction recording error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/performance", response_model=PerformanceStatsResponse)
async def get_performance_stats(
    time_window: int = 60,
    user: Dict = Depends(get_current_user)
):
    """Get performance statistics"""
    
    # Allow all authenticated users to view basic stats
    stats = await perf_monitor.get_performance_stats(time_window)
    
    return PerformanceStatsResponse(**stats)


@router.get("/stats/system", response_model=SystemStatsResponse)
async def get_system_stats(
    user: Dict = Depends(get_current_user)
):
    """Get system statistics (admin only)"""
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = await perf_monitor.get_system_stats()
    
    return SystemStatsResponse(**stats)


@router.get("/dashboard")
async def get_monitoring_dashboard(
    user: Dict = Depends(get_current_user)
):
    """Get comprehensive monitoring dashboard data"""
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        performance_stats = await perf_monitor.get_performance_stats()
        system_stats = await perf_monitor.get_system_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "performance": performance_stats,
            "system": system_stats,
            "alerts": {
                "active_count": 0,  # Would implement alert tracking
                "recent": []
            },
            "health_score": 95  # Would calculate based on all metrics
        }
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@router.get("/health")
async def monitoring_health_check():
    """Health check for monitoring system"""
    
    return {
        "status": "healthy" if perf_monitor.running else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "redis": "connected" if perf_monitor.redis else "disconnected",
            "system_collector": "running" if perf_monitor.running else "stopped",
            "alert_processor": "running" if perf_monitor.running else "stopped"
        }
    }


# Initialize monitoring on startup
@router.on_event("startup")
async def startup_monitoring():
    """Initialize monitoring system"""
    await perf_monitor.initialize()
    logger.info("Performance monitoring system started")


@router.on_event("shutdown")
async def shutdown_monitoring():
    """Shutdown monitoring system"""
    perf_monitor.running = False
    if perf_monitor.redis:
        await perf_monitor.redis.close()
    logger.info("Performance monitoring system stopped")