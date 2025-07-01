#!/usr/bin/env python3
"""
TradeMate Load Testing and Performance Validation
Validate <50ms premium and <100ms shared SLA targets
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import random
import logging
from dataclasses import dataclass
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    tier: str
    target_rps: int  # Requests per second
    duration_seconds: int
    concurrent_users: int
    ramp_up_seconds: int
    endpoints: List[Dict[str, Any]]
    sla_target_ms: float

class LoadTester:
    """Load testing framework for TradeMate API"""
    
    def __init__(self, base_url: str, tier: str = 'shared'):
        self.base_url = base_url
        self.tier = tier
        self.results = {
            'requests': [],
            'errors': [],
            'summary': {}
        }
        
        # Load test configurations
        self.configs = {
            'shared': LoadTestConfig(
                tier='shared',
                target_rps=1000,
                duration_seconds=300,  # 5 minutes
                concurrent_users=100,
                ramp_up_seconds=30,
                endpoints=[
                    {'path': '/api/v1/portfolio', 'method': 'GET', 'weight': 30},
                    {'path': '/api/v1/trades/history', 'method': 'GET', 'weight': 20},
                    {'path': '/api/v1/market/quotes', 'method': 'GET', 'weight': 25},
                    {'path': '/api/v1/whatsapp/process', 'method': 'POST', 'weight': 15},
                    {'path': '/api/v1/orders', 'method': 'POST', 'weight': 10}
                ],
                sla_target_ms=100
            ),
            'premium': LoadTestConfig(
                tier='premium',
                target_rps=500,
                duration_seconds=300,  # 5 minutes
                concurrent_users=50,
                ramp_up_seconds=20,
                endpoints=[
                    {'path': '/api/v1/realtime/positions', 'method': 'GET', 'weight': 35},
                    {'path': '/api/v1/algo/execute', 'method': 'POST', 'weight': 20},
                    {'path': '/api/v1/market/depth', 'method': 'GET', 'weight': 20},
                    {'path': '/api/v1/institutional/orders', 'method': 'POST', 'weight': 15},
                    {'path': '/api/v1/options/chain', 'method': 'GET', 'weight': 10}
                ],
                sla_target_ms=50
            )
        }
    
    def generate_test_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test data for endpoint"""
        if endpoint['method'] == 'GET':
            # GET request parameters
            if 'portfolio' in endpoint['path']:
                return {'params': {'user_id': f'user_{random.randint(1, 10000)}'}}
            elif 'quotes' in endpoint['path']:
                symbols = random.sample(['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICI'], 3)
                return {'params': {'symbols': ','.join(symbols)}}
            elif 'history' in endpoint['path']:
                return {'params': {'page': random.randint(1, 10), 'limit': 50}}
            else:
                return {}
        
        elif endpoint['method'] == 'POST':
            # POST request body
            if 'orders' in endpoint['path']:
                return {
                    'json': {
                        'symbol': random.choice(['RELIANCE', 'TCS', 'INFY']),
                        'quantity': random.randint(1, 100),
                        'order_type': random.choice(['MARKET', 'LIMIT']),
                        'side': random.choice(['BUY', 'SELL'])
                    }
                }
            elif 'whatsapp' in endpoint['path']:
                return {
                    'json': {
                        'message': random.choice([
                            'Buy 10 shares of Reliance',
                            'Show my portfolio',
                            'What is the price of TCS?'
                        ]),
                        'phone': f'+9198{random.randint(10000000, 99999999)}'
                    }
                }
            elif 'algo' in endpoint['path']:
                return {
                    'json': {
                        'strategy_id': f'strat_{random.randint(1, 50)}',
                        'parameters': {
                            'symbol': random.choice(['NIFTY', 'BANKNIFTY']),
                            'quantity': random.randint(10, 100)
                        }
                    }
                }
            else:
                return {'json': {}}
        
        return {}
    
    async def execute_request(self, session: aiohttp.ClientSession, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single request and measure performance"""
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']
        test_data = self.generate_test_data(endpoint)
        
        headers = {
            'X-User-Tier': self.tier.upper(),
            'Authorization': f'Bearer test_token_{self.tier}'
        }
        
        start_time = time.time()
        
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                **test_data,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                result = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'endpoint': endpoint['path'],
                    'method': method,
                    'status_code': response.status,
                    'response_time_ms': response_time,
                    'tier': self.tier,
                    'success': 200 <= response.status < 300
                }
                
                return result
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': endpoint['path'],
                'method': method,
                'status_code': 0,
                'response_time_ms': response_time,
                'tier': self.tier,
                'success': False,
                'error': str(e)
            }
    
    async def run_load_test(self) -> Dict[str, Any]:
        """Run load test for the configured tier"""
        config = self.configs[self.tier]
        logger.info(f"Starting load test for {self.tier} tier")
        logger.info(f"Target: {config.target_rps} RPS, Duration: {config.duration_seconds}s")
        
        # Calculate endpoint weights
        total_weight = sum(e['weight'] for e in config.endpoints)
        endpoint_probabilities = [e['weight'] / total_weight for e in config.endpoints]
        
        # Create session with connection pool
        connector = aiohttp.TCPConnector(
            limit=config.concurrent_users,
            limit_per_host=config.concurrent_users
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Ramp up phase
            logger.info(f"Ramping up over {config.ramp_up_seconds} seconds...")
            
            current_rps = 0
            ramp_up_increment = config.target_rps / config.ramp_up_seconds
            
            start_time = time.time()
            
            while time.time() - start_time < config.duration_seconds:
                loop_start = time.time()
                
                # Calculate current RPS (ramp up)
                elapsed = time.time() - start_time
                if elapsed < config.ramp_up_seconds:
                    current_rps = min(ramp_up_increment * elapsed, config.target_rps)
                else:
                    current_rps = config.target_rps
                
                # Generate requests for this second
                requests_this_second = int(current_rps)
                tasks = []
                
                for _ in range(requests_this_second):
                    # Select endpoint based on weights
                    endpoint = np.random.choice(config.endpoints, p=endpoint_probabilities)
                    task = self.execute_request(session, endpoint)
                    tasks.append(task)
                
                # Execute requests concurrently
                if tasks:
                    results = await asyncio.gather(*tasks)
                    self.results['requests'].extend(results)
                
                # Sleep to maintain RPS
                loop_duration = time.time() - loop_start
                if loop_duration < 1.0:
                    await asyncio.sleep(1.0 - loop_duration)
                
                # Progress update
                if int(elapsed) % 10 == 0:
                    logger.info(f"Progress: {int(elapsed)}s, Current RPS: {int(current_rps)}")
        
        # Analyze results
        self.analyze_results(config)
        
        return self.results
    
    def analyze_results(self, config: LoadTestConfig):
        """Analyze load test results"""
        requests = self.results['requests']
        
        if not requests:
            logger.error("No requests completed")
            return
        
        # Filter successful requests
        successful_requests = [r for r in requests if r['success']]
        failed_requests = [r for r in requests if not r['success']]
        
        # Calculate metrics
        response_times = [r['response_time_ms'] for r in successful_requests]
        
        if response_times:
            metrics = {
                'total_requests': len(requests),
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': (len(successful_requests) / len(requests)) * 100,
                'response_time_ms': {
                    'min': min(response_times),
                    'max': max(response_times),
                    'mean': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'p95': np.percentile(response_times, 95),
                    'p99': np.percentile(response_times, 99)
                },
                'sla_compliance': {
                    'target_ms': config.sla_target_ms,
                    'requests_within_sla': sum(1 for rt in response_times if rt <= config.sla_target_ms),
                    'sla_percentage': (sum(1 for rt in response_times if rt <= config.sla_target_ms) / len(response_times)) * 100
                }
            }
            
            # Calculate throughput
            duration = (requests[-1]['timestamp'] - requests[0]['timestamp'])
            # Convert ISO timestamp to seconds
            start_ts = datetime.fromisoformat(requests[0]['timestamp'].replace('Z', '+00:00'))
            end_ts = datetime.fromisoformat(requests[-1]['timestamp'].replace('Z', '+00:00'))
            duration_seconds = (end_ts - start_ts).total_seconds()
            
            metrics['throughput'] = {
                'actual_rps': len(requests) / duration_seconds if duration_seconds > 0 else 0,
                'successful_rps': len(successful_requests) / duration_seconds if duration_seconds > 0 else 0
            }
            
            # Endpoint-specific metrics
            endpoint_metrics = {}
            for endpoint in config.endpoints:
                endpoint_requests = [r for r in successful_requests if r['endpoint'] == endpoint['path']]
                if endpoint_requests:
                    endpoint_times = [r['response_time_ms'] for r in endpoint_requests]
                    endpoint_metrics[endpoint['path']] = {
                        'count': len(endpoint_requests),
                        'mean_ms': statistics.mean(endpoint_times),
                        'p95_ms': np.percentile(endpoint_times, 95)
                    }
            
            metrics['endpoint_metrics'] = endpoint_metrics
            
            # Store summary
            self.results['summary'] = metrics
            
            # Print results
            self.print_results(metrics)
            
            # Generate visualizations
            self.generate_charts(response_times, config)
    
    def print_results(self, metrics: Dict[str, Any]):
        """Print load test results"""
        print(f"\n{'='*60}")
        print(f"Load Test Results - {self.tier.upper()} Tier")
        print(f"{'='*60}\n")
        
        print(f"Total Requests: {metrics['total_requests']:,}")
        print(f"Successful: {metrics['successful_requests']:,} ({metrics['success_rate']:.2f}%)")
        print(f"Failed: {metrics['failed_requests']:,}")
        print(f"\nThroughput:")
        print(f"  Actual RPS: {metrics['throughput']['actual_rps']:.2f}")
        print(f"  Successful RPS: {metrics['throughput']['successful_rps']:.2f}")
        
        print(f"\nResponse Times (ms):")
        rt = metrics['response_time_ms']
        print(f"  Min: {rt['min']:.2f}")
        print(f"  Mean: {rt['mean']:.2f}")
        print(f"  Median: {rt['median']:.2f}")
        print(f"  P95: {rt['p95']:.2f}")
        print(f"  P99: {rt['p99']:.2f}")
        print(f"  Max: {rt['max']:.2f}")
        
        print(f"\nSLA Compliance:")
        sla = metrics['sla_compliance']
        print(f"  Target: <{sla['target_ms']}ms")
        print(f"  Requests within SLA: {sla['requests_within_sla']:,} ({sla['sla_percentage']:.2f}%)")
        
        # SLA verdict
        if sla['sla_percentage'] >= 95:
            print(f"  ✅ SLA PASSED")
        else:
            print(f"  ❌ SLA FAILED")
        
        print(f"\nEndpoint Performance:")
        for endpoint, stats in metrics['endpoint_metrics'].items():
            print(f"  {endpoint}:")
            print(f"    Requests: {stats['count']:,}")
            print(f"    Mean: {stats['mean_ms']:.2f}ms")
            print(f"    P95: {stats['p95_ms']:.2f}ms")
    
    def generate_charts(self, response_times: List[float], config: LoadTestConfig):
        """Generate performance visualization charts"""
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Load Test Results - {self.tier.upper()} Tier', fontsize=16)
        
        # Response time distribution
        ax1 = axes[0, 0]
        ax1.hist(response_times, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(x=config.sla_target_ms, color='red', linestyle='--', linewidth=2, label=f'SLA Target ({config.sla_target_ms}ms)')
        ax1.set_xlabel('Response Time (ms)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Response Time Distribution')
        ax1.legend()
        
        # Response time over time
        ax2 = axes[0, 1]
        requests = self.results['requests']
        timestamps = [i for i in range(len(requests))]
        times = [r['response_time_ms'] for r in requests if r['success']]
        
        # Downsample if too many points
        if len(times) > 1000:
            sample_indices = np.linspace(0, len(times)-1, 1000, dtype=int)
            times = [times[i] for i in sample_indices]
            timestamps = [timestamps[i] for i in sample_indices]
        
        ax2.plot(timestamps, times, alpha=0.5)
        ax2.axhline(y=config.sla_target_ms, color='red', linestyle='--', linewidth=2, label=f'SLA Target')
        ax2.set_xlabel('Request Number')
        ax2.set_ylabel('Response Time (ms)')
        ax2.set_title('Response Time Over Time')
        ax2.legend()
        
        # Percentile chart
        ax3 = axes[1, 0]
        percentiles = [50, 75, 90, 95, 99]
        values = [np.percentile(response_times, p) for p in percentiles]
        
        bars = ax3.bar([f'P{p}' for p in percentiles], values, color='green', alpha=0.7)
        ax3.axhline(y=config.sla_target_ms, color='red', linestyle='--', linewidth=2, label=f'SLA Target')
        
        # Color bars red if they exceed SLA
        for bar, value in zip(bars, values):
            if value > config.sla_target_ms:
                bar.set_color('red')
        
        ax3.set_ylabel('Response Time (ms)')
        ax3.set_title('Response Time Percentiles')
        ax3.legend()
        
        # Success rate over time
        ax4 = axes[1, 1]
        
        # Calculate success rate in windows
        window_size = max(len(requests) // 50, 1)
        success_rates = []
        
        for i in range(0, len(requests), window_size):
            window = requests[i:i+window_size]
            if window:
                success_rate = sum(1 for r in window if r['success']) / len(window) * 100
                success_rates.append(success_rate)
        
        ax4.plot(success_rates, marker='o')
        ax4.axhline(y=99, color='green', linestyle='--', linewidth=2, label='Target (99%)')
        ax4.set_xlabel('Time Window')
        ax4.set_ylabel('Success Rate (%)')
        ax4.set_title('Success Rate Over Time')
        ax4.set_ylim(90, 101)
        ax4.legend()
        
        plt.tight_layout()
        
        # Save chart
        filename = f'load_test_results_{self.tier}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=150)
        logger.info(f"Performance charts saved to {filename}")
        
        # Don't display in non-interactive environments
        # plt.show()


async def main():
    """Run load tests for both tiers"""
    # Test shared tier
    shared_tester = LoadTester('https://api.trademate.ai', 'shared')
    logger.info("\n" + "="*60)
    logger.info("Starting SHARED TIER load test")
    logger.info("="*60)
    shared_results = await shared_tester.run_load_test()
    
    # Wait between tests
    logger.info("\nWaiting 60 seconds before premium tier test...")
    await asyncio.sleep(60)
    
    # Test premium tier
    premium_tester = LoadTester('https://premium.trademate.ai', 'premium')
    logger.info("\n" + "="*60)
    logger.info("Starting PREMIUM TIER load test")
    logger.info("="*60)
    premium_results = await premium_tester.run_load_test()
    
    # Final summary
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    
    shared_sla = shared_results['summary']['sla_compliance']['sla_percentage']
    premium_sla = premium_results['summary']['sla_compliance']['sla_percentage']
    
    print(f"\nShared Tier:")
    print(f"  SLA Target: <100ms")
    print(f"  SLA Compliance: {shared_sla:.2f}%")
    print(f"  Status: {'✅ PASSED' if shared_sla >= 95 else '❌ FAILED'}")
    
    print(f"\nPremium Tier:")
    print(f"  SLA Target: <50ms")
    print(f"  SLA Compliance: {premium_sla:.2f}%")
    print(f"  Status: {'✅ PASSED' if premium_sla >= 95 else '❌ FAILED'}")
    
    # Overall verdict
    if shared_sla >= 95 and premium_sla >= 95:
        print(f"\n🎉 OVERALL: ALL SLA TARGETS MET!")
        return 0
    else:
        print(f"\n❌ OVERALL: SLA TARGETS NOT MET")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
