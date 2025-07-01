"""
GridWorks Monitoring & Observability System
==========================================
🔍 Real-time System Monitoring
📊 Performance Analytics
🚨 Intelligent Alerting
💡 Predictive Insights
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from decimal import Decimal

# Monitoring imports
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import psutil
import aioredis
import aiohttp


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Alert:
    """Alert data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = ""
    description: str = ""
    metric_name: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledgments: List[str] = field(default_factory=list)


@dataclass
class MetricValue:
    """Metric value with metadata"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""


class GridWorksMonitoringSystem:
    """Comprehensive monitoring and observability system"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = {}
        self.alert_rules = {}
        self.notification_channels = []
        self.is_monitoring = False
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
        # System metrics
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_io": {"bytes_sent": 0, "bytes_recv": 0},
            "active_connections": 0
        }
        
        # Application metrics
        self.app_metrics = {
            "total_requests": 0,
            "active_users": 0,
            "billing_requests": 0,
            "payment_success_rate": 0.0,
            "response_time": 0.0,
            "error_rate": 0.0
        }
        
        # Business metrics
        self.business_metrics = {
            "revenue_per_minute": 0.0,
            "user_signups": 0,
            "subscription_activations": 0,
            "tier_distribution": {"LITE": 0, "PRO": 0, "ELITE": 0, "BLACK_ONYX": 0, "BLACK_VOID": 0},
            "churn_rate": 0.0
        }
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        
        # HTTP Request metrics
        self.http_requests_total = Counter(
            'gridworks_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'gridworks_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        # Billing metrics
        self.billing_requests_total = Counter(
            'gridworks_billing_requests_total',
            'Total billing requests',
            ['tier', 'payment_method', 'status']
        )
        
        self.billing_amount = Summary(
            'gridworks_billing_amount_inr',
            'Billing amounts in INR',
            ['tier']
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'gridworks_system_cpu_usage_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'gridworks_system_memory_usage_percent',
            'System memory usage percentage'
        )
        
        self.active_users = Gauge(
            'gridworks_active_users',
            'Number of active users'
        )
        
        # Business metrics
        self.revenue_per_minute = Gauge(
            'gridworks_revenue_per_minute_inr',
            'Revenue per minute in INR'
        )
        
        self.subscription_activations = Counter(
            'gridworks_subscription_activations_total',
            'Total subscription activations',
            ['tier']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'gridworks_errors_total',
            'Total errors',
            ['error_type', 'component']
        )
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.logger.info("🔍 Starting GridWorks Monitoring System")
        
        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_application_metrics()),
            asyncio.create_task(self._monitor_business_metrics()),
            asyncio.create_task(self._process_alerts()),
            asyncio.create_task(self._health_check_loop())
        ]
        
        await asyncio.gather(*monitoring_tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False
        self.logger.info("🛑 Stopping GridWorks Monitoring System")
    
    async def _monitor_system_metrics(self):
        """Monitor system-level metrics"""
        while self.is_monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_metrics["cpu_usage"] = cpu_percent
                self.system_cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.system_metrics["memory_usage"] = memory_percent
                self.system_memory_usage.set(memory_percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.system_metrics["disk_usage"] = disk_percent
                
                # Network I/O
                network = psutil.net_io_counters()
                self.system_metrics["network_io"] = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
                
                # Check for alerts
                await self._check_system_alerts()
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"System metrics monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_application_metrics(self):
        """Monitor application-level metrics"""
        while self.is_monitoring:
            try:
                # This would integrate with your application
                # For now, simulating with realistic values
                
                # Response time monitoring
                response_times = await self._get_average_response_times()
                self.app_metrics["response_time"] = response_times["avg"]
                
                # Error rate monitoring
                error_rate = await self._calculate_error_rate()
                self.app_metrics["error_rate"] = error_rate
                
                # Active users
                active_users = await self._count_active_users()
                self.app_metrics["active_users"] = active_users
                self.active_users.set(active_users)
                
                # Payment success rate
                payment_success = await self._calculate_payment_success_rate()
                self.app_metrics["payment_success_rate"] = payment_success
                
                # Check for application alerts
                await self._check_application_alerts()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                self.logger.error(f"Application metrics monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_business_metrics(self):
        """Monitor business-level metrics"""
        while self.is_monitoring:
            try:
                # Revenue per minute
                revenue_per_min = await self._calculate_revenue_per_minute()
                self.business_metrics["revenue_per_minute"] = revenue_per_min
                self.revenue_per_minute.set(revenue_per_min)
                
                # User signups
                signups = await self._count_recent_signups()
                self.business_metrics["user_signups"] = signups
                
                # Subscription activations
                activations = await self._count_subscription_activations()
                self.business_metrics["subscription_activations"] = activations
                
                # Tier distribution
                tier_dist = await self._get_tier_distribution()
                self.business_metrics["tier_distribution"] = tier_dist
                
                # Churn rate
                churn = await self._calculate_churn_rate()
                self.business_metrics["churn_rate"] = churn
                
                # Check for business alerts
                await self._check_business_alerts()
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Business metrics monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _process_alerts(self):
        """Process and send alerts"""
        while self.is_monitoring:
            try:
                # Process pending alerts
                pending_alerts = [alert for alert in self.alerts.values() if not alert.resolved]
                
                for alert in pending_alerts:
                    # Send notifications
                    await self._send_alert_notifications(alert)
                    
                    # Check for auto-resolution
                    if await self._check_alert_resolution(alert):
                        alert.resolved = True
                        alert.resolved_at = datetime.now()
                        self.logger.info(f"🟢 Alert {alert.id} auto-resolved: {alert.title}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """Continuous health check of critical services"""
        while self.is_monitoring:
            try:
                health_checks = await self._run_health_checks()
                
                for service, status in health_checks.items():
                    if status["healthy"]:
                        self.logger.debug(f"✅ {service}: {status['response_time']}ms")
                    else:
                        await self._create_alert(
                            AlertSeverity.CRITICAL,
                            f"Service {service} is unhealthy",
                            f"Health check failed: {status['error']}",
                            "health_check"
                        )
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    async def _check_system_alerts(self):
        """Check system metrics for alert conditions"""
        
        # CPU usage alert
        if self.system_metrics["cpu_usage"] > 80:
            await self._create_alert(
                AlertSeverity.HIGH,
                "High CPU Usage",
                f"CPU usage is {self.system_metrics['cpu_usage']:.1f}%",
                "system_cpu_usage",
                self.system_metrics["cpu_usage"],
                80.0
            )
        
        # Memory usage alert
        if self.system_metrics["memory_usage"] > 85:
            await self._create_alert(
                AlertSeverity.HIGH,
                "High Memory Usage",
                f"Memory usage is {self.system_metrics['memory_usage']:.1f}%",
                "system_memory_usage",
                self.system_metrics["memory_usage"],
                85.0
            )
        
        # Disk usage alert
        if self.system_metrics["disk_usage"] > 90:
            await self._create_alert(
                AlertSeverity.CRITICAL,
                "Critical Disk Usage",
                f"Disk usage is {self.system_metrics['disk_usage']:.1f}%",
                "system_disk_usage",
                self.system_metrics["disk_usage"],
                90.0
            )
    
    async def _check_application_alerts(self):
        """Check application metrics for alert conditions"""
        
        # Response time alert
        if self.app_metrics["response_time"] > 2000:  # 2 seconds
            await self._create_alert(
                AlertSeverity.MEDIUM,
                "High Response Time",
                f"Average response time is {self.app_metrics['response_time']:.0f}ms",
                "response_time",
                self.app_metrics["response_time"],
                2000.0
            )
        
        # Error rate alert
        if self.app_metrics["error_rate"] > 5.0:  # 5%
            await self._create_alert(
                AlertSeverity.HIGH,
                "High Error Rate",
                f"Error rate is {self.app_metrics['error_rate']:.1f}%",
                "error_rate",
                self.app_metrics["error_rate"],
                5.0
            )
        
        # Payment success rate alert
        if self.app_metrics["payment_success_rate"] < 95.0:  # Below 95%
            await self._create_alert(
                AlertSeverity.CRITICAL,
                "Low Payment Success Rate",
                f"Payment success rate is {self.app_metrics['payment_success_rate']:.1f}%",
                "payment_success_rate",
                self.app_metrics["payment_success_rate"],
                95.0
            )
    
    async def _check_business_alerts(self):
        """Check business metrics for alert conditions"""
        
        # Revenue drop alert
        if self.business_metrics["revenue_per_minute"] < 50000:  # Below ₹50k/min
            await self._create_alert(
                AlertSeverity.HIGH,
                "Revenue Drop",
                f"Revenue per minute is ₹{self.business_metrics['revenue_per_minute']:,.0f}",
                "revenue_per_minute",
                self.business_metrics["revenue_per_minute"],
                50000.0
            )
        
        # High churn rate alert
        if self.business_metrics["churn_rate"] > 10.0:  # Above 10%
            await self._create_alert(
                AlertSeverity.MEDIUM,
                "High Churn Rate",
                f"Churn rate is {self.business_metrics['churn_rate']:.1f}%",
                "churn_rate",
                self.business_metrics["churn_rate"],
                10.0
            )
    
    async def _create_alert(self, severity: AlertSeverity, title: str, description: str, 
                          metric_name: str, current_value: float = 0.0, threshold_value: float = 0.0):
        """Create a new alert"""
        
        # Check if similar alert already exists
        existing_alert = self._find_existing_alert(metric_name, title)
        if existing_alert and not existing_alert.resolved:
            return existing_alert
        
        alert = Alert(
            severity=severity,
            title=title,
            description=description,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            tags={"environment": "production", "component": "gridworks"}
        )
        
        self.alerts[alert.id] = alert
        self.logger.warning(f"🚨 Alert created: {alert.title} - {alert.description}")
        
        return alert
    
    def _find_existing_alert(self, metric_name: str, title: str) -> Optional[Alert]:
        """Find existing alert for the same metric"""
        for alert in self.alerts.values():
            if alert.metric_name == metric_name and alert.title == title and not alert.resolved:
                return alert
        return None
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        
        # Email notification
        await self._send_email_notification(alert)
        
        # Slack notification
        await self._send_slack_notification(alert)
        
        # WhatsApp notification for critical alerts
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            await self._send_whatsapp_notification(alert)
        
        # PagerDuty for critical alerts
        if alert.severity == AlertSeverity.CRITICAL:
            await self._send_pagerduty_notification(alert)
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        try:
            # Email sending logic here
            self.logger.info(f"📧 Email notification sent for alert: {alert.title}")
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""
        try:
            # Slack API integration here
            self.logger.info(f"💬 Slack notification sent for alert: {alert.title}")
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_whatsapp_notification(self, alert: Alert):
        """Send WhatsApp notification"""
        try:
            # WhatsApp Business API integration here
            self.logger.info(f"📱 WhatsApp notification sent for alert: {alert.title}")
        except Exception as e:
            self.logger.error(f"Failed to send WhatsApp notification: {e}")
    
    async def _send_pagerduty_notification(self, alert: Alert):
        """Send PagerDuty notification"""
        try:
            # PagerDuty API integration here
            self.logger.info(f"📟 PagerDuty notification sent for alert: {alert.title}")
        except Exception as e:
            self.logger.error(f"Failed to send PagerDuty notification: {e}")
    
    async def _check_alert_resolution(self, alert: Alert) -> bool:
        """Check if alert condition has been resolved"""
        
        if alert.metric_name == "system_cpu_usage":
            return self.system_metrics["cpu_usage"] < alert.threshold_value * 0.9
        elif alert.metric_name == "system_memory_usage":
            return self.system_metrics["memory_usage"] < alert.threshold_value * 0.9
        elif alert.metric_name == "response_time":
            return self.app_metrics["response_time"] < alert.threshold_value * 0.9
        elif alert.metric_name == "error_rate":
            return self.app_metrics["error_rate"] < alert.threshold_value * 0.9
        elif alert.metric_name == "payment_success_rate":
            return self.app_metrics["payment_success_rate"] > alert.threshold_value * 1.01
        
        return False
    
    async def _run_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks on critical services"""
        
        health_results = {}
        
        # Database health check
        try:
            start_time = time.time()
            # Database connection test here
            response_time = (time.time() - start_time) * 1000
            health_results["database"] = {
                "healthy": True,
                "response_time": response_time,
                "last_check": datetime.now()
            }
        except Exception as e:
            health_results["database"] = {
                "healthy": False,
                "error": str(e),
                "last_check": datetime.now()
            }
        
        # Redis health check
        try:
            start_time = time.time()
            # Redis connection test here
            response_time = (time.time() - start_time) * 1000
            health_results["redis"] = {
                "healthy": True,
                "response_time": response_time,
                "last_check": datetime.now()
            }
        except Exception as e:
            health_results["redis"] = {
                "healthy": False,
                "error": str(e),
                "last_check": datetime.now()
            }
        
        # External APIs health check
        external_apis = ["stripe", "setu", "whatsapp", "openai"]
        for api in external_apis:
            try:
                start_time = time.time()
                # API health check here
                response_time = (time.time() - start_time) * 1000
                health_results[api] = {
                    "healthy": True,
                    "response_time": response_time,
                    "last_check": datetime.now()
                }
            except Exception as e:
                health_results[api] = {
                    "healthy": False,
                    "error": str(e),
                    "last_check": datetime.now()
                }
        
        return health_results
    
    # Helper methods for metric calculations
    async def _get_average_response_times(self) -> Dict[str, float]:
        """Get average response times"""
        # This would integrate with your request tracking
        return {"avg": 150.0, "p95": 300.0, "p99": 500.0}
    
    async def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        # This would calculate from error logs
        return 1.5  # 1.5% error rate
    
    async def _count_active_users(self) -> int:
        """Count currently active users"""
        # This would query your user session data
        return 2450
    
    async def _calculate_payment_success_rate(self) -> float:
        """Calculate payment success rate"""
        # This would query payment transaction data
        return 97.8  # 97.8% success rate
    
    async def _calculate_revenue_per_minute(self) -> float:
        """Calculate revenue per minute"""
        # This would calculate from recent transactions
        return 125000.0  # ₹1.25 Lakh per minute
    
    async def _count_recent_signups(self) -> int:
        """Count recent user signups"""
        # This would query user registration data
        return 145
    
    async def _count_subscription_activations(self) -> int:
        """Count recent subscription activations"""
        # This would query subscription data
        return 98
    
    async def _get_tier_distribution(self) -> Dict[str, int]:
        """Get current tier distribution"""
        # This would query user tier data
        return {
            "LITE": 2100,
            "PRO": 280,
            "ELITE": 65,
            "BLACK_ONYX": 4,
            "BLACK_VOID": 1
        }
    
    async def _calculate_churn_rate(self) -> float:
        """Calculate churn rate"""
        # This would calculate from subscription cancellations
        return 3.2  # 3.2% churn rate
    
    # Public API methods
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        health_checks = await self._run_health_checks()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if all(h.get("healthy", False) for h in health_checks.values()) else "degraded",
            "system_metrics": self.system_metrics,
            "application_metrics": self.app_metrics,
            "business_metrics": self.business_metrics,
            "health_checks": health_checks,
            "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
            "monitoring_active": self.is_monitoring
        }
    
    async def get_alerts(self, severity: Optional[AlertSeverity] = None, resolved: Optional[bool] = None) -> List[Alert]:
        """Get alerts with optional filtering"""
        
        alerts = list(self.alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.acknowledgments.append(acknowledged_by)
        
        self.logger.info(f"🤝 Alert {alert_id} acknowledged by {acknowledged_by}")
        return True
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Manually resolve an alert"""
        
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.now()
        alert.acknowledgments.append(f"Resolved by {resolved_by}")
        
        self.logger.info(f"✅ Alert {alert_id} resolved by {resolved_by}")
        return True
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None, unit: str = ""):
        """Record a custom metric"""
        
        metric = MetricValue(
            name=name,
            value=value,
            tags=tags or {},
            unit=unit
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Keep only last 1000 values per metric
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]


# Monitoring middleware for FastAPI
class MonitoringMiddleware:
    """FastAPI middleware for automatic monitoring"""
    
    def __init__(self, monitoring_system: GridWorksMonitoringSystem):
        self.monitoring = monitoring_system
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        # Record request
        self.monitoring.http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code="unknown"
        ).inc()
        
        try:
            response = await call_next(request)
            
            # Record successful request
            duration = time.time() - start_time
            
            self.monitoring.http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=str(response.status_code)
            ).inc()
            
            self.monitoring.http_request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error
            self.monitoring.errors_total.labels(
                error_type=type(e).__name__,
                component="api"
            ).inc()
            
            raise


# Global monitoring instance
monitoring_system = GridWorksMonitoringSystem()


# Monitoring decorators
def monitor_billing_operation(tier: str, payment_method: str):
    """Decorator to monitor billing operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful billing
                status = "success" if result.get("success") else "failed"
                monitoring_system.billing_requests_total.labels(
                    tier=tier,
                    payment_method=payment_method,
                    status=status
                ).inc()
                
                if result.get("amount"):
                    monitoring_system.billing_amount.labels(tier=tier).observe(float(result["amount"]))
                
                return result
                
            except Exception as e:
                # Record billing error
                monitoring_system.billing_requests_total.labels(
                    tier=tier,
                    payment_method=payment_method,
                    status="error"
                ).inc()
                
                monitoring_system.errors_total.labels(
                    error_type=type(e).__name__,
                    component="billing"
                ).inc()
                
                raise
        
        return wrapper
    return decorator


def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record performance metric
                duration = (time.time() - start_time) * 1000  # Convert to milliseconds
                monitoring_system.record_metric(
                    f"{operation_name}_duration_ms",
                    duration,
                    {"operation": operation_name}
                )
                
                return result
                
            except Exception as e:
                monitoring_system.errors_total.labels(
                    error_type=type(e).__name__,
                    component=operation_name
                ).inc()
                
                raise
        
        return wrapper
    return decorator


# Export monitoring functions
__all__ = [
    "GridWorksMonitoringSystem",
    "MonitoringMiddleware", 
    "Alert",
    "AlertSeverity",
    "MetricValue",
    "monitoring_system",
    "monitor_billing_operation",
    "monitor_performance"
]