"""
AI Support Performance Monitoring
Real-time monitoring and SLA tracking for support system
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import redis
from collections import defaultdict, deque

from .models import SupportTier

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    RESOLUTION_RATE = "resolution_rate"
    USER_SATISFACTION = "user_satisfaction"
    ESCALATION_RATE = "escalation_rate"
    QUEUE_WAIT_TIME = "queue_wait_time"
    AGENT_UTILIZATION = "agent_utilization"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    tier: SupportTier
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class SLATarget:
    """SLA target definition"""
    tier: SupportTier
    metric: MetricType
    target_value: float
    measurement_window: int  # seconds
    breach_threshold: float  # percentage of breaches allowed


@dataclass
class SLAStatus:
    """Current SLA compliance status"""
    tier: SupportTier
    metric: MetricType
    target: float
    current_value: float
    compliance_percentage: float
    status: str  # "compliant", "warning", "breach"
    breach_count: int
    last_updated: datetime


class PerformanceMonitor:
    """Real-time performance monitoring for AI support system"""
    
    def __init__(self):
        self.redis = redis.Redis(decode_responses=True)
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.sla_targets = self._load_sla_targets()
        self.current_sla_status = {}
        
        # Start monitoring tasks
        asyncio.create_task(self._start_monitoring())
        
    def _load_sla_targets(self) -> Dict[str, SLATarget]:
        """Load SLA targets for each tier"""
        
        targets = {}
        
        # Response time SLAs
        for tier, target_ms in [
            (SupportTier.LITE, 30000),    # 30 seconds
            (SupportTier.PRO, 15000),     # 15 seconds  
            (SupportTier.ELITE, 10000),   # 10 seconds
            (SupportTier.BLACK, 5000)     # 5 seconds
        ]:
            key = f"{tier.value}_{MetricType.RESPONSE_TIME.value}"
            targets[key] = SLATarget(
                tier=tier,
                metric=MetricType.RESPONSE_TIME,
                target_value=target_ms,
                measurement_window=300,  # 5 minutes
                breach_threshold=5.0     # Max 5% breaches allowed
            )
        
        # Resolution rate SLAs (all tiers should resolve 95% with AI)
        for tier in SupportTier:
            key = f"{tier.value}_{MetricType.RESOLUTION_RATE.value}"
            targets[key] = SLATarget(
                tier=tier,
                metric=MetricType.RESOLUTION_RATE,
                target_value=95.0,       # 95% resolution rate
                measurement_window=3600, # 1 hour
                breach_threshold=2.0     # Max 2% below target
            )
        
        # Queue wait time SLAs  
        for tier, target_ms in [
            (SupportTier.LITE, 7200000),  # 2 hours
            (SupportTier.PRO, 1800000),   # 30 minutes
            (SupportTier.ELITE, 300000),  # 5 minutes
            (SupportTier.BLACK, 60000)    # 1 minute
        ]:
            key = f"{tier.value}_{MetricType.QUEUE_WAIT_TIME.value}"
            targets[key] = SLATarget(
                tier=tier,
                metric=MetricType.QUEUE_WAIT_TIME,
                target_value=target_ms,
                measurement_window=1800, # 30 minutes
                breach_threshold=10.0    # Max 10% breaches allowed
            )
        
        # User satisfaction SLAs
        for tier in SupportTier:
            key = f"{tier.value}_{MetricType.USER_SATISFACTION.value}"
            targets[key] = SLATarget(
                tier=tier,
                metric=MetricType.USER_SATISFACTION,
                target_value=4.0,        # 4.0/5.0 minimum rating
                measurement_window=3600, # 1 hour
                breach_threshold=5.0     # Max 5% below target
            )
        
        return targets
    
    async def record_metric(
        self,
        metric_type: MetricType,
        tier: SupportTier,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric"""
        
        try:
            metric = PerformanceMetric(
                metric_type=metric_type,
                tier=tier,
                value=value,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Add to buffer
            buffer_key = f"{tier.value}_{metric_type.value}"
            self.metrics_buffer[buffer_key].append(metric)
            
            # Store in Redis for persistence
            await self._store_metric(metric)
            
            # Check SLA compliance
            await self._check_sla_compliance(metric)
            
        except Exception as e:
            logger.error(f"Metric recording failed: {e}")
    
    async def _store_metric(self, metric: PerformanceMetric):
        """Store metric in Redis"""
        
        try:
            # Time-series key
            ts_key = f"metrics:{metric.tier.value}:{metric.metric_type.value}"
            
            # Store with timestamp as score for time-based queries
            metric_data = {
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat(),
                "metadata": metric.metadata
            }
            
            timestamp_score = metric.timestamp.timestamp()
            await self.redis.zadd(ts_key, {json.dumps(metric_data): timestamp_score})
            
            # Keep only last 24 hours of data
            cutoff_time = time.time() - 86400
            await self.redis.zremrangebyscore(ts_key, 0, cutoff_time)
            
        except Exception as e:
            logger.error(f"Metric storage failed: {e}")
    
    async def _check_sla_compliance(self, metric: PerformanceMetric):
        """Check if metric breaches SLA"""
        
        try:
            sla_key = f"{metric.tier.value}_{metric.metric_type.value}"
            sla_target = self.sla_targets.get(sla_key)
            
            if not sla_target:
                return
            
            # Get recent metrics for compliance calculation
            recent_metrics = await self._get_recent_metrics(
                metric.tier,
                metric.metric_type,
                sla_target.measurement_window
            )
            
            if not recent_metrics:
                return
            
            # Calculate compliance
            compliance_result = await self._calculate_compliance(recent_metrics, sla_target)
            
            # Update SLA status
            self.current_sla_status[sla_key] = compliance_result
            
            # Check for breaches
            if compliance_result.status in ["warning", "breach"]:
                await self._handle_sla_breach(compliance_result)
                
        except Exception as e:
            logger.error(f"SLA compliance check failed: {e}")
    
    async def _get_recent_metrics(
        self,
        tier: SupportTier,
        metric_type: MetricType,
        window_seconds: int
    ) -> List[PerformanceMetric]:
        """Get recent metrics within time window"""
        
        try:
            ts_key = f"metrics:{tier.value}:{metric_type.value}"
            
            # Get metrics from last window_seconds
            cutoff_time = time.time() - window_seconds
            
            raw_metrics = await self.redis.zrangebyscore(
                ts_key,
                cutoff_time,
                time.time(),
                withscores=True
            )
            
            metrics = []
            for metric_json, timestamp_score in raw_metrics:
                try:
                    metric_data = json.loads(metric_json)
                    metric = PerformanceMetric(
                        metric_type=metric_type,
                        tier=tier,
                        value=metric_data["value"],
                        timestamp=datetime.fromisoformat(metric_data["timestamp"]),
                        metadata=metric_data["metadata"]
                    )
                    metrics.append(metric)
                except Exception as e:
                    logger.warning(f"Failed to parse metric: {e}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Recent metrics retrieval failed: {e}")
            return []
    
    async def _calculate_compliance(
        self,
        metrics: List[PerformanceMetric],
        sla_target: SLATarget
    ) -> SLAStatus:
        """Calculate SLA compliance for metrics"""
        
        if not metrics:
            return SLAStatus(
                tier=sla_target.tier,
                metric=sla_target.metric,
                target=sla_target.target_value,
                current_value=0.0,
                compliance_percentage=0.0,
                status="unknown",
                breach_count=0,
                last_updated=datetime.utcnow()
            )
        
        values = [m.value for m in metrics]
        
        if sla_target.metric in [MetricType.RESPONSE_TIME, MetricType.QUEUE_WAIT_TIME]:
            # For time-based metrics, target is maximum allowed
            compliant_count = sum(1 for v in values if v <= sla_target.target_value)
            current_value = sum(values) / len(values)  # Average
            
        elif sla_target.metric == MetricType.RESOLUTION_RATE:
            # For resolution rate, target is minimum required
            compliant_count = sum(1 for v in values if v >= sla_target.target_value)
            current_value = sum(values) / len(values)  # Average
            
        elif sla_target.metric == MetricType.USER_SATISFACTION:
            # For satisfaction, target is minimum required
            compliant_count = sum(1 for v in values if v >= sla_target.target_value)
            current_value = sum(values) / len(values)  # Average
            
        else:
            # Default: target is minimum required
            compliant_count = sum(1 for v in values if v >= sla_target.target_value)
            current_value = sum(values) / len(values)
        
        compliance_percentage = (compliant_count / len(values)) * 100
        breach_count = len(values) - compliant_count
        
        # Determine status
        if compliance_percentage >= (100 - sla_target.breach_threshold):
            status = "compliant"
        elif compliance_percentage >= (100 - sla_target.breach_threshold * 2):
            status = "warning"
        else:
            status = "breach"
        
        return SLAStatus(
            tier=sla_target.tier,
            metric=sla_target.metric,
            target=sla_target.target_value,
            current_value=current_value,
            compliance_percentage=compliance_percentage,
            status=status,
            breach_count=breach_count,
            last_updated=datetime.utcnow()
        )
    
    async def _handle_sla_breach(self, sla_status: SLAStatus):
        """Handle SLA breach or warning"""
        
        try:
            # Create breach alert
            alert = {
                "type": "sla_breach" if sla_status.status == "breach" else "sla_warning",
                "tier": sla_status.tier.value,
                "metric": sla_status.metric.value,
                "target": sla_status.target,
                "current": sla_status.current_value,
                "compliance": sla_status.compliance_percentage,
                "breach_count": sla_status.breach_count,
                "timestamp": time.time(),
                "severity": self._get_alert_severity(sla_status)
            }
            
            # Store alert
            await self.redis.lpush("sla_alerts", json.dumps(alert))
            
            # Send notifications based on tier
            await self._send_sla_notification(alert)
            
            logger.warning(f"SLA {alert['type']}: {alert}")
            
        except Exception as e:
            logger.error(f"SLA breach handling failed: {e}")
    
    def _get_alert_severity(self, sla_status: SLAStatus) -> str:
        """Determine alert severity"""
        
        if sla_status.tier == SupportTier.BLACK:
            return "critical"
        elif sla_status.tier == SupportTier.ELITE:
            return "high"
        elif sla_status.status == "breach":
            return "medium"
        else:
            return "low"
    
    async def _send_sla_notification(self, alert: Dict[str, Any]):
        """Send SLA breach/warning notification"""
        
        try:
            # Different notification channels based on severity
            if alert["severity"] == "critical":
                # BLACK tier issues - immediate CEO/CTO notification
                await self._send_executive_alert(alert)
                
            elif alert["severity"] == "high":
                # ELITE tier issues - senior management notification
                await self._send_management_alert(alert)
                
            else:
                # Standard team notification
                await self._send_team_alert(alert)
                
        except Exception as e:
            logger.error(f"SLA notification failed: {e}")
    
    async def _send_executive_alert(self, alert: Dict[str, Any]):
        """Send alert to executive team"""
        
        # Would integrate with Slack, email, SMS in production
        logger.critical(f"EXECUTIVE ALERT: BLACK tier SLA breach - {alert}")
    
    async def _send_management_alert(self, alert: Dict[str, Any]):
        """Send alert to management team"""
        
        # Would integrate with management notification system
        logger.error(f"MANAGEMENT ALERT: ELITE tier SLA breach - {alert}")
    
    async def _send_team_alert(self, alert: Dict[str, Any]):
        """Send alert to support team"""
        
        # Would integrate with team chat/notification system
        logger.warning(f"TEAM ALERT: SLA issue - {alert}")
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Generate real-time performance dashboard"""
        
        try:
            dashboard = {
                "timestamp": datetime.utcnow().isoformat(),
                "sla_status": {},
                "tier_performance": {},
                "system_health": await self._get_system_health(),
                "alerts": await self._get_recent_alerts()
            }
            
            # Get SLA status for all tiers
            for tier in SupportTier:
                tier_sla = {}
                
                for metric_type in MetricType:
                    sla_key = f"{tier.value}_{metric_type.value}"
                    sla_status = self.current_sla_status.get(sla_key)
                    
                    if sla_status:
                        tier_sla[metric_type.value] = {
                            "target": sla_status.target,
                            "current": round(sla_status.current_value, 2),
                            "compliance": round(sla_status.compliance_percentage, 1),
                            "status": sla_status.status,
                            "breach_count": sla_status.breach_count
                        }
                
                dashboard["sla_status"][tier.value] = tier_sla
            
            # Get tier performance summaries
            for tier in SupportTier:
                tier_perf = await self._get_tier_performance_summary(tier)
                dashboard["tier_performance"][tier.value] = tier_perf
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return {"error": str(e)}
    
    async def _get_tier_performance_summary(self, tier: SupportTier) -> Dict[str, Any]:
        """Get performance summary for specific tier"""
        
        try:
            # Get metrics from last hour
            recent_metrics = {}
            
            for metric_type in MetricType:
                metrics = await self._get_recent_metrics(tier, metric_type, 3600)
                if metrics:
                    values = [m.value for m in metrics]
                    recent_metrics[metric_type.value] = {
                        "count": len(values),
                        "average": round(sum(values) / len(values), 2),
                        "min": round(min(values), 2),
                        "max": round(max(values), 2),
                        "latest": round(values[-1], 2)
                    }
            
            return recent_metrics
            
        except Exception as e:
            logger.error(f"Tier performance summary failed: {e}")
            return {}
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        
        try:
            # Calculate system-wide metrics
            total_requests = 0
            total_response_time = 0
            escalation_count = 0
            
            for tier in SupportTier:
                # Get recent response times
                response_metrics = await self._get_recent_metrics(
                    tier, MetricType.RESPONSE_TIME, 3600
                )
                
                if response_metrics:
                    total_requests += len(response_metrics)
                    total_response_time += sum(m.value for m in response_metrics)
                
                # Get escalation metrics
                escalation_metrics = await self._get_recent_metrics(
                    tier, MetricType.ESCALATION_RATE, 3600
                )
                
                if escalation_metrics:
                    escalation_count += sum(m.value for m in escalation_metrics)
            
            avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
            
            return {
                "total_requests_hour": total_requests,
                "average_response_time_ms": round(avg_response_time, 2),
                "escalation_rate_percent": round(escalation_count / total_requests * 100, 1) if total_requests > 0 else 0,
                "system_status": "healthy" if avg_response_time < 20000 else "degraded"
            }
            
        except Exception as e:
            logger.error(f"System health calculation failed: {e}")
            return {"system_status": "unknown"}
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent SLA alerts"""
        
        try:
            # Get last 10 alerts
            raw_alerts = await self.redis.lrange("sla_alerts", 0, 9)
            
            alerts = []
            for alert_json in raw_alerts:
                try:
                    alert = json.loads(alert_json)
                    alerts.append(alert)
                except Exception as e:
                    logger.warning(f"Failed to parse alert: {e}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Recent alerts retrieval failed: {e}")
            return []
    
    async def _start_monitoring(self):
        """Start background monitoring tasks"""
        
        try:
            # Start SLA monitoring loop
            asyncio.create_task(self._sla_monitoring_loop())
            
            # Start metrics cleanup loop
            asyncio.create_task(self._cleanup_loop())
            
            logger.info("Performance monitoring started")
            
        except Exception as e:
            logger.error(f"Monitoring startup failed: {e}")
    
    async def _sla_monitoring_loop(self):
        """Continuous SLA monitoring"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Check all SLA targets
                for sla_key, sla_target in self.sla_targets.items():
                    recent_metrics = await self._get_recent_metrics(
                        sla_target.tier,
                        sla_target.metric,
                        sla_target.measurement_window
                    )
                    
                    if recent_metrics:
                        compliance = await self._calculate_compliance(recent_metrics, sla_target)
                        self.current_sla_status[sla_key] = compliance
                        
                        if compliance.status in ["warning", "breach"]:
                            await self._handle_sla_breach(compliance)
                
            except Exception as e:
                logger.error(f"SLA monitoring loop error: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup old metrics and alerts"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Clean up old metrics (keep 24 hours)
                cutoff_time = time.time() - 86400
                
                for tier in SupportTier:
                    for metric_type in MetricType:
                        ts_key = f"metrics:{tier.value}:{metric_type.value}"
                        await self.redis.zremrangebyscore(ts_key, 0, cutoff_time)
                
                # Clean up old alerts (keep 1000 most recent)
                await self.redis.ltrim("sla_alerts", 0, 999)
                
                logger.info("Metrics cleanup completed")
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")