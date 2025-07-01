#!/usr/bin/env python3
"""
TradeMate SLA Validation and Performance Testing
Validates <50ms premium and <100ms shared SLA targets
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SLAValidator:
    """Validate tier-specific SLA compliance"""
    
    def __init__(self):
        self.sla_targets = {
            'shared': 0.1,    # 100ms
            'premium': 0.05   # 50ms
        }
        self.results = {
            'shared': [],
            'premium': []
        }
    
    async def validate_endpoint(self, session: aiohttp.ClientSession, 
                              url: str, tier: str, endpoint: str, 
                              method: str = 'GET', payload: dict = None) -> Dict[str, Any]:
        """Validate single endpoint performance"""
        
        headers = {
            'X-User-Tier': tier.upper(),
            'Content-Type': 'application/json'
        }
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                async with session.get(url + endpoint, headers=headers) as response:
                    response_time = time.time() - start_time
                    status = response.status
            else:
                async with session.post(url + endpoint, headers=headers, 
                                      json=payload or {}) as response:
                    response_time = time.time() - start_time
                    status = response.status
            
            return {
                'endpoint': endpoint,
                'tier': tier,
                'response_time': response_time,
                'status_code': status,
                'success': 200 <= status < 300,
                'sla_met': response_time <= self.sla_targets[tier],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'endpoint': endpoint,
                'tier': tier,
                'response_time': response_time,
                'status_code': 0,
                'success': False,
                'sla_met': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def run_sla_validation(self, shared_url: str, premium_url: str, 
                               iterations: int = 100) -> Dict[str, Any]:
        """Run comprehensive SLA validation tests"""
        
        logger.info(f"Starting SLA validation with {iterations} iterations per tier")
        
        # Test endpoints for each tier
        test_cases = {
            'shared': [
                {'endpoint': '/api/v1/portfolio', 'method': 'GET'},
                {'endpoint': '/api/v1/trades/history', 'method': 'GET'},
                {'endpoint': '/api/v1/market/quotes', 'method': 'GET'},
                {'endpoint': '/api/v1/orders', 'method': 'POST', 
                 'payload': {'symbol': 'RELIANCE', 'quantity': 10, 'order_type': 'MARKET'}}
            ],
            'premium': [
                {'endpoint': '/api/v1/realtime/positions', 'method': 'GET'},
                {'endpoint': '/api/v1/algo/performance', 'method': 'GET'},
                {'endpoint': '/api/v1/market/depth', 'method': 'GET'},
                {'endpoint': '/api/v1/institutional/orders', 'method': 'POST',
                 'payload': {'symbol': 'NIFTY', 'quantity': 100, 'strategy_id': 'algo_1'}}
            ]
        }
        
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # Test shared tier
            logger.info("Testing shared tier endpoints...")
            shared_tasks = []
            for i in range(iterations):
                for test_case in test_cases['shared']:
                    task = self.validate_endpoint(
                        session, shared_url, 'shared',
                        test_case['endpoint'], test_case['method'],
                        test_case.get('payload')
                    )
                    shared_tasks.append(task)
            
            shared_results = await asyncio.gather(*shared_tasks)
            self.results['shared'].extend(shared_results)
            
            # Small delay between tier tests
            await asyncio.sleep(1)
            
            # Test premium tier
            logger.info("Testing premium tier endpoints...")
            premium_tasks = []
            for i in range(iterations):
                for test_case in test_cases['premium']:
                    task = self.validate_endpoint(
                        session, premium_url, 'premium',
                        test_case['endpoint'], test_case['method'],
                        test_case.get('payload')
                    )
                    premium_tasks.append(task)
            
            premium_results = await asyncio.gather(*premium_tasks)
            self.results['premium'].extend(premium_results)
        
        # Analyze results
        return self.analyze_sla_results()
    
    def analyze_sla_results(self) -> Dict[str, Any]:
        """Analyze SLA validation results"""
        
        analysis = {}
        
        for tier in ['shared', 'premium']:
            results = self.results[tier]
            
            if not results:
                analysis[tier] = {'error': 'No results available'}
                continue
            
            # Filter successful requests
            successful = [r for r in results if r['success']]
            response_times = [r['response_time'] for r in successful]
            sla_compliant = [r for r in successful if r['sla_met']]
            
            if response_times:
                analysis[tier] = {
                    'total_requests': len(results),
                    'successful_requests': len(successful),
                    'failed_requests': len(results) - len(successful),
                    'success_rate': len(successful) / len(results) * 100,
                    'sla_target': self.sla_targets[tier],
                    'sla_compliant_requests': len(sla_compliant),
                    'sla_compliance_rate': len(sla_compliant) / len(successful) * 100,
                    'response_times': {
                        'min': min(response_times),
                        'max': max(response_times),
                        'mean': statistics.mean(response_times),
                        'median': statistics.median(response_times),
                        'p95': sorted(response_times)[int(len(response_times) * 0.95)],
                        'p99': sorted(response_times)[int(len(response_times) * 0.99)]
                    },
                    'sla_status': 'PASSED' if len(sla_compliant) / len(successful) >= 0.95 else 'FAILED'
                }
            else:
                analysis[tier] = {'error': 'No successful requests'}
        
        return analysis
    
    def print_sla_report(self, analysis: Dict[str, Any]):
        """Print comprehensive SLA validation report"""
        
        print("\n" + "="*80)
        print("TradeMate SLA Validation Report")
        print("="*80)
        print(f"Test Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        for tier in ['shared', 'premium']:
            tier_data = analysis.get(tier, {})
            
            if 'error' in tier_data:
                print(f"\n❌ {tier.upper()} TIER: {tier_data['error']}")
                continue
            
            print(f"\n📊 {tier.upper()} TIER RESULTS")
            print("-" * 40)
            
            # Request statistics
            print(f"Total Requests: {tier_data['total_requests']:,}")
            print(f"Successful: {tier_data['successful_requests']:,} ({tier_data['success_rate']:.2f}%)")
            print(f"Failed: {tier_data['failed_requests']:,}")
            
            # SLA compliance
            sla_target_ms = tier_data['sla_target'] * 1000
            sla_rate = tier_data['sla_compliance_rate']
            print(f"\nSLA Target: <{sla_target_ms:.0f}ms")
            print(f"SLA Compliant: {tier_data['sla_compliant_requests']:,} ({sla_rate:.2f}%)")
            
            # SLA status
            if tier_data['sla_status'] == 'PASSED':
                print(f"✅ SLA STATUS: PASSED")
            else:
                print(f"❌ SLA STATUS: FAILED")
            
            # Performance metrics
            rt = tier_data['response_times']
            print(f"\nResponse Times (ms):")
            print(f"  Min: {rt['min']*1000:.2f}")
            print(f"  Mean: {rt['mean']*1000:.2f}")
            print(f"  Median: {rt['median']*1000:.2f}")
            print(f"  P95: {rt['p95']*1000:.2f}")
            print(f"  P99: {rt['p99']*1000:.2f}")
            print(f"  Max: {rt['max']*1000:.2f}")
        
        # Overall verdict
        shared_passed = analysis.get('shared', {}).get('sla_status') == 'PASSED'
        premium_passed = analysis.get('premium', {}).get('sla_status') == 'PASSED'
        
        print("\n" + "="*80)
        if shared_passed and premium_passed:
            print("🎉 OVERALL SLA VALIDATION: PASSED")
            print("✅ Both tiers meet their performance targets")
        else:
            print("❌ OVERALL SLA VALIDATION: FAILED")
            if not shared_passed:
                print("❌ Shared tier failed to meet 100ms target")
            if not premium_passed:
                print("❌ Premium tier failed to meet 50ms target")
        print("="*80)


async def main():
    """Main function for SLA validation"""
    
    parser = argparse.ArgumentParser(description='TradeMate SLA Validation')
    parser.add_argument('--shared-url', default='https://api.trademate.ai',
                       help='Shared tier API URL')
    parser.add_argument('--premium-url', default='https://premium.trademate.ai',
                       help='Premium tier API URL')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of iterations per endpoint')
    parser.add_argument('--output', help='Output file for results (JSON)')
    
    args = parser.parse_args()
    
    # Run SLA validation
    validator = SLAValidator()
    analysis = await validator.run_sla_validation(
        args.shared_url, args.premium_url, args.iterations
    )
    
    # Print report
    validator.print_sla_report(analysis)
    
    # Save results if output specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        logger.info(f"Results saved to {args.output}")
    
    # Return exit code based on SLA compliance
    shared_passed = analysis.get('shared', {}).get('sla_status') == 'PASSED'
    premium_passed = analysis.get('premium', {}).get('sla_status') == 'PASSED'
    
    return 0 if shared_passed and premium_passed else 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)