#!/usr/bin/env python3
"""
TradeMate SLA Exporter
Custom Prometheus exporter for tracking tier-specific SLA compliance
"""

import time
import logging
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import requests
import threading
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeMateNinja:
    """SLA Monitoring and Metrics Collection for TradeMate"""
    
    def __init__(self):
        # SLA Compliance Metrics
        self.shared_sla_compliance = Gauge(
            'trademate_shared_sla_compliance',
            'Shared tier SLA compliance percentage (target: 99%)',
            ['metric_type']
        )
        
        self.premium_sla_compliance = Gauge(
            'trademate_premium_sla_compliance', 
            'Premium tier SLA compliance percentage (target: 99.99%)',
            ['metric_type']
        )
        
        # Response Time SLA Tracking
        self.shared_response_time_sla = Gauge(
            'trademate_shared_response_time_sla_seconds',
            'Shared tier response time SLA threshold (100ms)',
        )
        
        self.premium_response_time_sla = Gauge(
            'trademate_premium_response_time_sla_seconds',
            'Premium tier response time SLA threshold (50ms)',
        )
        
        # SLA Breach Counters
        self.sla_breaches = Counter(
            'trademate_sla_breaches_total',
            'Total SLA breaches by tier and type',
            ['tier', 'breach_type']
        )
        
        # Business Metrics
        self.active_users = Gauge(
            'trademate_active_users',
            'Number of active users by tier',
            ['tier']
        )
        
        self.revenue_per_hour = Gauge(
            'trademate_revenue_per_hour_inr',
            'Revenue per hour in INR by tier',
            ['tier']
        )
        
        self.trades_per_second = Gauge(
            'trademate_trades_per_second',
            'Trading frequency by tier',
            ['tier']
        )
        
        # Cost Optimization Metrics
        self.infrastructure_cost = Gauge(
            'trademate_infrastructure_cost_inr_per_hour',
            'Infrastructure cost per hour by tier',
            ['tier']
        )
        
        self.cost_per_user = Gauge(
            'trademate_cost_per_user_inr',
            'Cost per user by tier',
            ['tier']
        )
        
        # Availability Tracking
        self.uptime_percentage = Gauge(
            'trademate_uptime_percentage',
            'Service uptime percentage by tier',
            ['tier']
        )
        
        # Error Budget Metrics
        self.error_budget_remaining = Gauge(
            'trademate_error_budget_remaining_percentage',
            'Remaining error budget percentage',
            ['tier']
        )
        
        # Initialize SLA thresholds
        self.shared_response_time_sla.set(0.1)  # 100ms
        self.premium_response_time_sla.set(0.05)  # 50ms
        
        # Prometheus endpoints
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')
        self.endpoints = {
            'shared': os.getenv('SHARED_API_URL', 'https://api.trademate.ai'),
            'premium': os.getenv('PREMIUM_API_URL', 'https://premium.trademate.ai')
        }
        
    def calculate_sla_compliance(self, tier: str, hours: int = 24) -> dict:
        """Calculate SLA compliance for the last N hours"""
        try:
            # Query Prometheus for metrics
            queries = {
                'availability': f'avg_over_time(up{{tier="{tier}"}}[{hours}h])',
                'response_time': f'histogram_quantile(0.95, avg_over_time(http_request_duration_seconds_bucket{{tier="{tier}"}}[{hours}h]))',
                'error_rate': f'avg_over_time(rate(http_requests_total{{status=~"5..",tier="{tier}"}}[5m])[{hours}h:1m]) / avg_over_time(rate(http_requests_total{{tier="{tier}"}}[5m])[{hours}h:1m])'
            }
            
            results = {}
            for metric, query in queries.items():
                response = requests.get(
                    f'{self.prometheus_url}/api/v1/query',
                    params={'query': query},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['data']['result']:
                        value = float(data['data']['result'][0]['value'][1])
                        results[metric] = value
                    else:
                        results[metric] = 0.0
                else:
                    logger.error(f"Failed to query {metric} for {tier}: {response.status_code}")
                    results[metric] = 0.0
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating SLA compliance for {tier}: {e}")
            return {'availability': 0.0, 'response_time': 1.0, 'error_rate': 1.0}
    
    def check_endpoint_health(self, tier: str, url: str) -> dict:
        """Check endpoint health and response time"""
        try:
            start_time = time.time()
            response = requests.get(f'{url}/health', timeout=5)
            response_time = time.time() - start_time
            
            return {
                'available': response.status_code == 200,
                'response_time': response_time,
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Health check failed for {tier} ({url}): {e}")
            return {
                'available': False,
                'response_time': 5.0,  # Timeout
                'status_code': 0
            }
    
    def update_business_metrics(self):
        """Update business and revenue metrics"""
        try:
            # Simulated business metrics (replace with actual data sources)
            business_data = {
                'lite': {'users': 750000, 'revenue_per_hour': 8333, 'trades_per_sec': 50},
                'pro': {'users': 200000, 'revenue_per_hour': 16667, 'trades_per_sec': 30},
                'elite': {'users': 45000, 'revenue_per_hour': 41667, 'trades_per_sec': 25},
                'black': {'users': 5000, 'revenue_per_hour': 83333, 'trades_per_sec': 15}
            }
            
            for tier, data in business_data.items():
                self.active_users.labels(tier=tier).set(data['users'])
                self.revenue_per_hour.labels(tier=tier).set(data['revenue_per_hour'])
                self.trades_per_second.labels(tier=tier).set(data['trades_per_sec'])
            
            # Cost metrics (INR per hour)
            cost_data = {
                'shared': {'cost_per_hour': 166667, 'users': 950000},  # ₹40L/month
                'premium': {'cost_per_hour': 250000, 'users': 50000}   # ₹60L/month
            }
            
            for tier, data in cost_data.items():
                self.infrastructure_cost.labels(tier=tier).set(data['cost_per_hour'])
                cost_per_user = data['cost_per_hour'] / data['users'] if data['users'] > 0 else 0
                self.cost_per_user.labels(tier=tier).set(cost_per_user)
                
        except Exception as e:
            logger.error(f"Error updating business metrics: {e}")
    
    def monitor_sla_compliance(self):
        """Main monitoring loop for SLA compliance"""
        while True:
            try:
                # Check both tiers
                for tier in ['shared', 'premium']:
                    # Get SLA metrics
                    sla_data = self.calculate_sla_compliance(tier)
                    
                    # Calculate compliance percentages
                    availability_compliance = sla_data['availability'] * 100
                    
                    # Response time compliance (percentage of requests under SLA)
                    sla_threshold = 0.1 if tier == 'shared' else 0.05
                    response_time_compliance = 100 if sla_data['response_time'] <= sla_threshold else 0
                    
                    # Error rate compliance
                    max_error_rate = 0.05 if tier == 'shared' else 0.01
                    error_rate_compliance = 100 if sla_data['error_rate'] <= max_error_rate else 0
                    
                    # Update metrics
                    if tier == 'shared':
                        self.shared_sla_compliance.labels(metric_type='availability').set(availability_compliance)
                        self.shared_sla_compliance.labels(metric_type='response_time').set(response_time_compliance)
                        self.shared_sla_compliance.labels(metric_type='error_rate').set(error_rate_compliance)
                        target_sla = 99.0
                    else:
                        self.premium_sla_compliance.labels(metric_type='availability').set(availability_compliance)
                        self.premium_sla_compliance.labels(metric_type='response_time').set(response_time_compliance)
                        self.premium_sla_compliance.labels(metric_type='error_rate').set(error_rate_compliance)
                        target_sla = 99.99
                    
                    # Track SLA breaches
                    if availability_compliance < target_sla:
                        self.sla_breaches.labels(tier=tier, breach_type='availability').inc()
                    
                    if response_time_compliance < 100:
                        self.sla_breaches.labels(tier=tier, breach_type='response_time').inc()
                    
                    if error_rate_compliance < 100:
                        self.sla_breaches.labels(tier=tier, breach_type='error_rate').inc()
                    
                    # Update uptime
                    self.uptime_percentage.labels(tier=tier).set(availability_compliance)
                    
                    # Calculate error budget remaining
                    if tier == 'shared':
                        error_budget = max(0, 100 - (100 - availability_compliance) * 100)
                    else:
                        error_budget = max(0, 100 - (100 - availability_compliance) * 10000)
                    
                    self.error_budget_remaining.labels(tier=tier).set(error_budget)
                    
                    logger.info(f"{tier.upper()} SLA - Availability: {availability_compliance:.2f}%, Response Time: {response_time_compliance:.2f}%, Error Rate: {error_rate_compliance:.2f}%")
                
                # Update business metrics
                self.update_business_metrics()
                
                # Health checks
                for tier, url in self.endpoints.items():
                    health = self.check_endpoint_health(tier, url)
                    logger.info(f"{tier.upper()} Health - Available: {health['available']}, Response Time: {health['response_time']:.3f}s")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)

def main():
    """Main function to start the SLA exporter"""
    logger.info("Starting TradeMate SLA Exporter")
    
    # Start metrics server
    metrics_port = int(os.getenv('METRICS_PORT', 9090))
    start_http_server(metrics_port)
    logger.info(f"Metrics server started on port {metrics_port}")
    
    # Initialize and start monitoring
    monitor = TradeMateNinja()
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor.monitor_sla_compliance)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    logger.info("SLA monitoring started")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down SLA exporter")

if __name__ == '__main__':
    main()
