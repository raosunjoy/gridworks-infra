"""
GridWorks Admin Dashboard
Comprehensive admin interface for monitoring, billing, tickets, and system performance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from app.ai_support.models import SupportTier
from app.billing.subscription_manager import SubscriptionManager, SubscriptionStatus
from app.ai_support.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class AdminRole(Enum):
    """Admin user roles"""
    SUPER_ADMIN = "super_admin"
    BILLING_ADMIN = "billing_admin"
    SUPPORT_ADMIN = "support_admin"
    ANALYTICS_ADMIN = "analytics_admin"
    READ_ONLY = "read_only"


@dataclass
class AdminUser:
    """Admin user structure"""
    user_id: str
    name: str
    email: str
    role: AdminRole
    permissions: List[str]
    last_login: datetime


class GridWorksAdminDashboard:
    """
    Comprehensive admin dashboard for GridWorks platform
    
    Features:
    - Real-time system monitoring
    - Subscription and billing management
    - Support ticket management
    - User tier analytics
    - Performance monitoring
    - Financial reporting
    - Alert management
    """
    
    def __init__(self):
        self.app = FastAPI(title="GridWorks Admin Dashboard")
        self.templates = Jinja2Templates(directory="app/admin/templates")
        
        # Initialize managers
        self.subscription_manager = SubscriptionManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")
        
        # Setup routes
        self._setup_routes()
        
        logger.info("GridWorks Admin Dashboard initialized")
    
    def _setup_routes(self):
        """Setup admin dashboard routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def admin_dashboard(request: Request):
            """Main admin dashboard"""
            
            # Get real-time metrics
            metrics = await self._get_dashboard_metrics()
            
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "metrics": metrics,
                "page_title": "GridWorks Admin Dashboard"
            })
        
        @self.app.get("/api/metrics/realtime")
        async def get_realtime_metrics():
            """Get real-time system metrics"""
            
            return await self._get_realtime_metrics()
        
        @self.app.get("/api/billing/overview")
        async def get_billing_overview():
            """Get billing overview and analytics"""
            
            return await self._get_billing_overview()
        
        @self.app.get("/api/support/tickets")
        async def get_support_tickets():
            """Get support ticket analytics"""
            
            return await self._get_support_ticket_analytics()
        
        @self.app.get("/api/users/analytics")
        async def get_user_analytics():
            """Get user tier analytics"""
            
            return await self._get_user_tier_analytics()
        
        @self.app.get("/api/performance/system")
        async def get_system_performance():
            """Get system performance metrics"""
            
            return await self._get_system_performance_metrics()
        
        @self.app.post("/api/billing/subscription/{subscription_id}/cancel")
        async def cancel_subscription(subscription_id: str):
            """Cancel a subscription"""
            
            return await self._cancel_subscription(subscription_id)
        
        @self.app.post("/api/support/ticket/{ticket_id}/escalate")
        async def escalate_ticket(ticket_id: str):
            """Escalate support ticket"""
            
            return await self._escalate_support_ticket(ticket_id)
        
        @self.app.get("/billing", response_class=HTMLResponse)
        async def billing_dashboard(request: Request):
            """Billing management dashboard"""
            
            billing_data = await self._get_comprehensive_billing_data()
            
            return self.templates.TemplateResponse("billing.html", {
                "request": request,
                "billing_data": billing_data,
                "page_title": "Billing Management"
            })
        
        @self.app.get("/support", response_class=HTMLResponse)
        async def support_dashboard(request: Request):
            """Support ticket management dashboard"""
            
            support_data = await self._get_comprehensive_support_data()
            
            return self.templates.TemplateResponse("support.html", {
                "request": request,
                "support_data": support_data,
                "page_title": "Support Management"
            })
        
        @self.app.get("/analytics", response_class=HTMLResponse)
        async def analytics_dashboard(request: Request):
            """Analytics and reporting dashboard"""
            
            analytics_data = await self._get_comprehensive_analytics()
            
            return self.templates.TemplateResponse("analytics.html", {
                "request": request,
                "analytics_data": analytics_data,
                "page_title": "Analytics & Reporting"
            })
    
    async def _get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get main dashboard metrics"""
        
        return {
            "system_health": await self._get_system_health(),
            "user_stats": await self._get_user_statistics(),
            "revenue_stats": await self._get_revenue_statistics(),
            "support_stats": await self._get_support_statistics(),
            "performance_stats": await self._get_performance_statistics()
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        
        return {
            "status": "healthy",
            "uptime": "99.98%",
            "api_response_time": "45ms",
            "active_users": 47652,
            "total_trades_today": 125430,
            "revenue_today": 2847650,  # In paise
            "alerts": [
                {
                    "level": "warning",
                    "message": "Elite tier response time slightly elevated (8.2s vs 5s target)",
                    "timestamp": datetime.now() - timedelta(minutes=15)
                }
            ]
        }
    
    async def _get_user_statistics(self) -> Dict[str, Any]:
        """Get user tier statistics"""
        
        return {
            "total_users": 52847,
            "by_tier": {
                "LITE": {"count": 44920, "percentage": 85.0, "growth_7d": "+12.3%"},
                "PRO": {"count": 6890, "percentage": 13.0, "growth_7d": "+8.7%"},
                "ELITE": {"count": 987, "percentage": 1.87, "growth_7d": "+15.2%"},
                "BLACK": {"count": 50, "percentage": 0.09, "growth_7d": "+25.0%"}
            },
            "new_signups_today": 1247,
            "tier_upgrades_today": 89,
            "churn_rate_monthly": 2.3
        }
    
    async def _get_revenue_statistics(self) -> Dict[str, Any]:
        """Get revenue statistics"""
        
        return {
            "today": {
                "total": 2847650,  # ₹28,476.50
                "subscriptions": 1950000,  # ₹19,500
                "per_trade_fees": 897650  # ₹8,976.50
            },
            "monthly": {
                "total": 67854300,  # ₹6,78,543
                "subscriptions": 45870000,  # ₹4,58,700
                "per_trade_fees": 21984300  # ₹2,19,843
            },
            "by_tier": {
                "LITE": {"revenue": 8975400, "users": 44920, "arpu": 200},
                "PRO": {"revenue": 34560000, "users": 6890, "arpu": 5015},
                "ELITE": {"revenue": 19740000, "users": 987, "arpu": 20000},
                "BLACK": {"revenue": 4578900, "users": 50, "arpu": 91578}
            },
            "growth_metrics": {
                "month_over_month": "+23.5%",
                "quarter_over_quarter": "+67.8%",
                "annual_run_rate": "₹8.14 Cr"
            }
        }
    
    async def _get_support_statistics(self) -> Dict[str, Any]:
        """Get support ticket statistics"""
        
        return {
            "tickets_today": 892,
            "resolved_today": 856,
            "resolution_rate": "95.9%",
            "by_tier": {
                "BLACK": {"tickets": 3, "avg_response": "45s", "satisfaction": "99.3%"},
                "ELITE": {"tickets": 28, "avg_response": "4.2min", "satisfaction": "97.8%"},
                "PRO": {"tickets": 156, "avg_response": "12.5min", "satisfaction": "94.5%"},
                "LITE": {"tickets": 705, "avg_response": "28.3min", "satisfaction": "91.2%"}
            },
            "escalated_tickets": 23,
            "ai_resolution_rate": "78.5%",
            "human_escalation_rate": "21.5%"
        }
    
    async def _get_billing_overview(self) -> Dict[str, Any]:
        """Get comprehensive billing overview"""
        
        return {
            "active_subscriptions": {
                "total": 7927,
                "by_tier": {
                    "PRO": {"count": 6890, "mrr": 6890 * 99},
                    "ELITE": {"count": 987, "mrr": 987 * 2999},
                    "BLACK": {"count": 50, "mrr": 50 * 15000}
                }
            },
            "billing_issues": {
                "failed_payments": 23,
                "payment_retries": 45,
                "account_suspensions": 7,
                "refund_requests": 12
            },
            "revenue_breakdown": {
                "subscription_revenue": 4587000,
                "per_trade_revenue": 2198430,
                "setup_fees": 125000,
                "partner_commissions": 567800
            },
            "payment_methods": {
                "upi": {"percentage": 78.5, "success_rate": "99.2%"},
                "credit_card": {"percentage": 15.3, "success_rate": "97.8%"},
                "net_banking": {"percentage": 6.2, "success_rate": "98.9%"}
            }
        }
    
    async def _get_support_ticket_analytics(self) -> Dict[str, Any]:
        """Get detailed support ticket analytics"""
        
        return {
            "ticket_volume": {
                "last_24h": 892,
                "last_7d": 6453,
                "last_30d": 28765,
                "trend": "+5.2% vs last month"
            },
            "ticket_categories": {
                "trading_issues": {"count": 267, "percentage": 29.9},
                "payment_problems": {"count": 156, "percentage": 17.5},
                "account_access": {"count": 134, "percentage": 15.0},
                "feature_requests": {"count": 98, "percentage": 11.0},
                "technical_support": {"count": 89, "percentage": 10.0},
                "billing_queries": {"count": 67, "percentage": 7.5},
                "other": {"count": 81, "percentage": 9.1}
            },
            "resolution_metrics": {
                "avg_first_response": "8.3 minutes",
                "avg_resolution_time": "2.1 hours",
                "first_contact_resolution": "78.5%",
                "customer_satisfaction": "94.2%"
            },
            "agent_performance": [
                {"name": "Priya Sharma", "tickets_resolved": 156, "satisfaction": "98.2%", "avg_time": "1.8h"},
                {"name": "Rajesh Kumar", "tickets_resolved": 134, "satisfaction": "96.7%", "avg_time": "2.2h"},
                {"name": "Anita Singh", "tickets_resolved": 128, "satisfaction": "97.1%", "avg_time": "1.9h"}
            ]
        }
    
    async def _get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed system performance metrics"""
        
        return {
            "api_performance": {
                "avg_response_time": "45ms",
                "95th_percentile": "89ms",
                "99th_percentile": "145ms",
                "error_rate": "0.02%",
                "requests_per_second": 1250
            },
            "database_performance": {
                "query_time_avg": "12ms",
                "slow_queries": 3,
                "connection_pool": "78% utilized",
                "cache_hit_rate": "94.5%"
            },
            "infrastructure": {
                "cpu_usage": "67%",
                "memory_usage": "72%",
                "disk_usage": "45%",
                "network_throughput": "450 Mbps"
            },
            "tier_specific_sla": {
                "BLACK": {"target": "<5s", "actual": "2.8s", "compliance": "99.8%"},
                "ELITE": {"target": "<10s", "actual": "8.2s", "compliance": "97.3%"},
                "PRO": {"target": "<15s", "actual": "12.5s", "compliance": "98.9%"},
                "LITE": {"target": "<30s", "actual": "28.3s", "compliance": "96.7%"}
            }
        }
    
    async def _get_user_tier_analytics(self) -> Dict[str, Any]:
        """Get detailed user tier analytics"""
        
        return {
            "tier_distribution": {
                "LITE": {"users": 44920, "revenue_share": "13.2%", "avg_trades_month": 8},
                "PRO": {"users": 6890, "revenue_share": "50.9%", "avg_trades_month": 45},
                "ELITE": {"users": 987, "revenue_share": "29.1%", "avg_trades_month": 128},
                "BLACK": {"users": 50, "revenue_share": "6.8%", "avg_trades_month": 245}
            },
            "upgrade_funnel": {
                "LITE_to_PRO": {"rate": "12.3%", "conversion_time": "45 days avg"},
                "PRO_to_ELITE": {"rate": "8.7%", "conversion_time": "78 days avg"},
                "ELITE_to_BLACK": {"rate": "2.1%", "conversion_time": "156 days avg"}
            },
            "engagement_metrics": {
                "daily_active_users": "67.8%",
                "weekly_active_users": "84.2%",
                "monthly_active_users": "91.5%",
                "avg_session_duration": "12.5 minutes"
            },
            "geographic_distribution": {
                "mumbai": "28.5%",
                "delhi": "18.7%",
                "bangalore": "15.2%",
                "hyderabad": "8.9%",
                "pune": "7.3%",
                "other": "21.4%"
            }
        }
    
    async def _cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        
        try:
            # Implementation would integrate with Stripe
            # stripe.Subscription.delete(subscription_id)
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "cancelled_at": datetime.now().isoformat(),
                "refund_amount": 0
            }
            
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _escalate_support_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Escalate support ticket to higher tier"""
        
        try:
            # Implementation would integrate with support system
            return {
                "success": True,
                "ticket_id": ticket_id,
                "escalated_to": "senior_support",
                "escalated_at": datetime.now().isoformat(),
                "estimated_response": "15 minutes"
            }
            
        except Exception as e:
            logger.error(f"Ticket escalation failed: {e}")
            return {"success": False, "error": str(e)}


# Dashboard HTML Templates
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow">
            <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <h1 class="text-3xl font-bold text-gray-900">GridWorks Admin Dashboard</h1>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            
            <!-- Stats Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                
                <!-- Total Users -->
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                                    <span class="text-white font-bold">👥</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                                    <dd class="text-lg font-medium text-gray-900">{{ metrics.user_stats.total_users | default(0) }}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Today's Revenue -->
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                                    <span class="text-white font-bold">💰</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Today's Revenue</dt>
                                    <dd class="text-lg font-medium text-gray-900">₹{{ (metrics.revenue_stats.today.total / 100) | round(0) }}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- System Health -->
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-{{ 'green' if metrics.system_health.status == 'healthy' else 'red' }}-500 rounded-md flex items-center justify-center">
                                    <span class="text-white font-bold">⚡</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">System Health</dt>
                                    <dd class="text-lg font-medium text-gray-900">{{ metrics.system_health.uptime }}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Support Tickets -->
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                                    <span class="text-white font-bold">🎫</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Support Tickets</dt>
                                    <dd class="text-lg font-medium text-gray-900">{{ metrics.support_stats.tickets_today }}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                
            </div>

            <!-- Tier Distribution Chart -->
            <div class="bg-white shadow rounded-lg mb-8">
                <div class="px-4 py-5 sm:p-6">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">User Tier Distribution</h3>
                    <canvas id="tierChart" width="400" height="200"></canvas>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="bg-white shadow rounded-lg">
                <div class="px-4 py-5 sm:p-6">
                    <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                            View Billing
                        </button>
                        <button class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                            Support Tickets
                        </button>
                        <button class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
                            User Analytics
                        </button>
                        <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                            System Alerts
                        </button>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <script>
        // Tier Distribution Chart
        const ctx = document.getElementById('tierChart').getContext('2d');
        const tierChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['LITE', 'PRO', 'ELITE', 'BLACK'],
                datasets: [{
                    data: [
                        {{ metrics.user_stats.by_tier.LITE.count | default(0) }},
                        {{ metrics.user_stats.by_tier.PRO.count | default(0) }},
                        {{ metrics.user_stats.by_tier.ELITE.count | default(0) }},
                        {{ metrics.user_stats.by_tier.BLACK.count | default(0) }}
                    ],
                    backgroundColor: [
                        '#10B981', // Green for LITE
                        '#3B82F6', // Blue for PRO  
                        '#8B5CF6', // Purple for ELITE
                        '#1F2937'  // Dark for BLACK
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>
"""


# Demo usage
async def demo_admin_dashboard():
    """Demonstrate admin dashboard"""
    
    print("🎛️ GridWorks Admin Dashboard Demo")
    print("=" * 50)
    
    admin = GridWorksAdminDashboard()
    
    # Get dashboard metrics
    metrics = await admin._get_dashboard_metrics()
    
    print("📊 System Overview:")
    print(f"Total Users: {metrics['user_stats']['total_users']:,}")
    print(f"Today's Revenue: ₹{metrics['revenue_stats']['today']['total']/100:,.0f}")
    print(f"System Health: {metrics['system_health']['status']}")
    print(f"Support Tickets: {metrics['support_stats']['tickets_today']}")
    
    print("\n💰 Revenue by Tier:")
    for tier, data in metrics['revenue_stats']['by_tier'].items():
        print(f"{tier}: {data['users']:,} users, ₹{data['revenue']/100:,.0f} revenue")
    
    print("\n🎫 Support Performance:")
    for tier, data in metrics['support_stats']['by_tier'].items():
        print(f"{tier}: {data['tickets']} tickets, {data['avg_response']} avg response")


if __name__ == "__main__":
    asyncio.run(demo_admin_dashboard())