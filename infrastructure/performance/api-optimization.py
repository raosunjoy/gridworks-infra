#!/usr/bin/env python3
"""
TradeMate API Performance Optimization
Tier-specific performance tuning for <50ms premium, <100ms shared targets
"""

import asyncio
import aioredis
import time
import json
import logging
from typing import Dict, List, Any, Optional
from functools import wraps, lru_cache
import hashlib
from datetime import datetime, timedelta
import uvloop
import cProfile
import pstats
import io

# Use uvloop for better async performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """API Performance optimization for tier-specific SLA targets"""
    
    def __init__(self, tier: str = 'shared'):
        self.tier = tier
        self.cache_ttl = {
            'shared': 300,  # 5 minutes for shared tier
            'premium': 60   # 1 minute for premium tier (fresher data)
        }
        self.performance_targets = {
            'shared': 0.1,   # 100ms
            'premium': 0.05  # 50ms
        }
        self.redis_pool = None
        self.profiler = cProfile.Profile()
        
    async def initialize(self):
        """Initialize performance optimization components"""
        # Create Redis connection pool for caching
        self.redis_pool = await aioredis.create_redis_pool(
            'redis://localhost:6379',
            minsize=10,
            maxsize=20 if self.tier == 'shared' else 50,  # More connections for premium
            encoding='utf-8'
        )
        logger.info(f"Performance optimizer initialized for {self.tier} tier")
    
    def performance_monitor(self, func):
        """Decorator to monitor function performance"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Start profiling for detailed analysis
            if logger.level == logging.DEBUG:
                self.profiler.enable()
            
            try:
                result = await func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Check against SLA target
                target = self.performance_targets[self.tier]
                if execution_time > target:
                    logger.warning(
                        f"{func.__name__} exceeded {self.tier} tier SLA: "
                        f"{execution_time:.3f}s > {target}s"
                    )
                else:
                    logger.debug(
                        f"{func.__name__} within SLA: {execution_time:.3f}s"
                    )
                
                # Add performance header
                if isinstance(result, dict):
                    result['_performance'] = {
                        'execution_time': execution_time,
                        'tier': self.tier,
                        'sla_met': execution_time <= target
                    }
                
                return result
                
            finally:
                if logger.level == logging.DEBUG:
                    self.profiler.disable()
                    self._print_profiling_stats(func.__name__)
        
        return wrapper
    
    def tier_cache(self, key_prefix: str, expire_override: Optional[int] = None):
        """Tier-specific caching decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(key_prefix, args, kwargs)
                
                # Try to get from cache
                cached_result = await self.redis_pool.get(cache_key)
                if cached_result:
                    logger.debug(f"Cache hit for {cache_key}")
                    return json.loads(cached_result)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                
                # Set cache with tier-specific TTL
                ttl = expire_override or self.cache_ttl[self.tier]
                await self.redis_pool.setex(
                    cache_key,
                    ttl,
                    json.dumps(result)
                )
                
                logger.debug(f"Cached {cache_key} for {ttl}s")
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def _generate_cache_key(prefix: str, args: tuple, kwargs: dict) -> str:
        """Generate consistent cache key from function arguments"""
        # Create a hashable representation of args and kwargs
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_hash = hashlib.md5(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def _print_profiling_stats(self, func_name: str):
        """Print profiling statistics"""
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 time-consuming functions
        logger.debug(f"\nProfiling stats for {func_name}:\n{s.getvalue()}")
    
    async def batch_processor(self, items: List[Any], processor_func, batch_size: int = None):
        """Process items in optimized batches"""
        if batch_size is None:
            batch_size = 50 if self.tier == 'shared' else 100  # Premium can handle larger batches
        
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [processor_func(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            # Small delay between batches for shared tier to prevent overload
            if self.tier == 'shared' and i + batch_size < len(items):
                await asyncio.sleep(0.01)  # 10ms delay
        
        return results
    
    @lru_cache(maxsize=1000)
    def compute_intensive_operation(self, input_data: str) -> str:
        """Example of LRU cached compute-intensive operation"""
        # Simulate expensive computation
        result = hashlib.sha256(input_data.encode()).hexdigest()
        return result
    
    async def parallel_fetch(self, fetch_tasks: List[asyncio.Task], timeout: float = None):
        """Fetch data from multiple sources in parallel with timeout"""
        if timeout is None:
            timeout = 0.08 if self.tier == 'premium' else 0.15  # Stricter timeout for premium
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*fetch_tasks, return_exceptions=True),
                timeout=timeout
            )
            
            # Filter out exceptions
            valid_results = [r for r in results if not isinstance(r, Exception)]
            return valid_results
            
        except asyncio.TimeoutError:
            logger.warning(f"Parallel fetch timeout after {timeout}s")
            # Return partial results
            done, pending = await asyncio.wait(fetch_tasks, timeout=0)
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            return [task.result() for task in done if not task.exception()]


class DatabaseOptimizer:
    """Database query optimization for tier-specific performance"""
    
    def __init__(self, tier: str = 'shared'):
        self.tier = tier
        self.connection_pool_size = {
            'shared': 20,
            'premium': 50
        }
        self.query_timeout = {
            'shared': 0.05,   # 50ms query timeout
            'premium': 0.02   # 20ms query timeout
        }
    
    def optimize_query(self, query: str) -> str:
        """Optimize SQL query for performance"""
        optimized = query
        
        # Add query hints for better performance
        if 'SELECT' in query.upper():
            # Use covering indexes
            if self.tier == 'premium':
                optimized = optimized.replace('SELECT', 'SELECT /*+ INDEX_FFS(t) */', 1)
            
            # Limit result sets
            if 'LIMIT' not in query.upper():
                limit = 100 if self.tier == 'shared' else 1000
                optimized += f' LIMIT {limit}'
        
        return optimized
    
    async def execute_with_timeout(self, connection, query: str, params: tuple = None):
        """Execute query with tier-specific timeout"""
        timeout = self.query_timeout[self.tier]
        
        try:
            # Set statement timeout
            await connection.execute(f"SET statement_timeout = '{int(timeout * 1000)}'")
            
            # Execute query
            if params:
                result = await connection.fetch(query, *params)
            else:
                result = await connection.fetch(query)
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Query timeout after {timeout}s: {query[:100]}...")
            raise
        finally:
            # Reset statement timeout
            await connection.execute("SET statement_timeout = '0'")
    
    def create_materialized_view(self, view_name: str, query: str) -> str:
        """Create materialized view for complex queries"""
        refresh_interval = '5 MINUTES' if self.tier == 'shared' else '1 MINUTE'
        
        return f"""
        CREATE MATERIALIZED VIEW IF NOT EXISTS {view_name}
        WITH (autovacuum_enabled = true)
        AS {query};
        
        CREATE INDEX IF NOT EXISTS idx_{view_name}_created 
        ON {view_name} (created_at DESC);
        
        -- Refresh job
        SELECT cron.schedule('{view_name}_refresh', 
                           'INTERVAL {refresh_interval}', 
                           'REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name}');
        """


class CacheWarmer:
    """Pre-warm cache for frequently accessed data"""
    
    def __init__(self, tier: str = 'shared'):
        self.tier = tier
        self.warmup_queries = {
            'shared': [
                'portfolio_summary',
                'recent_trades',
                'market_overview'
            ],
            'premium': [
                'portfolio_analytics',
                'real_time_positions',
                'market_depth',
                'options_chain',
                'institutional_flow'
            ]
        }
    
    async def warmup_cache(self, redis_pool):
        """Pre-warm cache with frequently accessed data"""
        logger.info(f"Starting cache warmup for {self.tier} tier")
        
        warmup_tasks = []
        for query_type in self.warmup_queries[self.tier]:
            task = self._warmup_query_type(query_type, redis_pool)
            warmup_tasks.append(task)
        
        results = await asyncio.gather(*warmup_tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Cache warmup complete: {success_count}/{len(warmup_tasks)} successful")
    
    async def _warmup_query_type(self, query_type: str, redis_pool):
        """Warm up specific query type"""
        try:
            # Simulate fetching data
            data = await self._fetch_data_for_warmup(query_type)
            
            # Cache the data
            cache_key = f"warmup:{self.tier}:{query_type}"
            ttl = 300 if self.tier == 'shared' else 60
            
            await redis_pool.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
            
            logger.debug(f"Warmed up cache for {query_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to warm up {query_type}: {e}")
            return False
    
    async def _fetch_data_for_warmup(self, query_type: str) -> dict:
        """Fetch data for cache warmup (simulated)"""
        # In real implementation, would fetch from database
        await asyncio.sleep(0.01)  # Simulate DB query
        
        return {
            'query_type': query_type,
            'tier': self.tier,
            'timestamp': datetime.utcnow().isoformat(),
            'data': f'Warmup data for {query_type}'
        }


class ConnectionPoolManager:
    """Manage connection pools for optimal performance"""
    
    def __init__(self, tier: str = 'shared'):
        self.tier = tier
        self.pool_config = {
            'shared': {
                'min_size': 10,
                'max_size': 50,
                'max_queries': 50000,
                'max_inactive_connection_lifetime': 300
            },
            'premium': {
                'min_size': 20,
                'max_size': 100,
                'max_queries': 100000,
                'max_inactive_connection_lifetime': 600
            }
        }
    
    async def create_pool(self, dsn: str):
        """Create optimized connection pool"""
        import asyncpg
        
        config = self.pool_config[self.tier]
        
        pool = await asyncpg.create_pool(
            dsn,
            min_size=config['min_size'],
            max_size=config['max_size'],
            max_queries=config['max_queries'],
            max_inactive_connection_lifetime=config['max_inactive_connection_lifetime'],
            command_timeout=60,
            server_settings={
                'jit': 'off' if self.tier == 'premium' else 'on',  # Disable JIT for premium for consistent latency
                'work_mem': '8MB' if self.tier == 'premium' else '4MB',
                'shared_buffers': '256MB'
            }
        )
        
        logger.info(f"Created {self.tier} tier connection pool with {config['max_size']} max connections")
        return pool


class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'api_latency': [],
            'db_latency': [],
            'cache_hit_rate': 0,
            'concurrent_requests': 0
        }
    
    def record_latency(self, operation: str, latency: float, tier: str):
        """Record operation latency"""
        self.metrics[f'{operation}_latency'].append({
            'value': latency,
            'tier': tier,
            'timestamp': time.time()
        })
        
        # Keep only last 1000 measurements
        if len(self.metrics[f'{operation}_latency']) > 1000:
            self.metrics[f'{operation}_latency'] = self.metrics[f'{operation}_latency'][-1000:]
    
    def get_percentile_latency(self, operation: str, percentile: int = 95) -> Dict[str, float]:
        """Get percentile latency for operation"""
        latencies_by_tier = {'shared': [], 'premium': []}
        
        for measurement in self.metrics.get(f'{operation}_latency', []):
            tier = measurement['tier']
            latencies_by_tier[tier].append(measurement['value'])
        
        results = {}
        for tier, values in latencies_by_tier.items():
            if values:
                sorted_values = sorted(values)
                index = int(len(sorted_values) * (percentile / 100))
                results[tier] = sorted_values[min(index, len(sorted_values) - 1)]
            else:
                results[tier] = 0
        
        return results
    
    def check_sla_compliance(self) -> Dict[str, bool]:
        """Check if current performance meets SLA"""
        p95_latencies = self.get_percentile_latency('api', 95)
        
        return {
            'shared': p95_latencies.get('shared', 0) <= 0.1,  # 100ms
            'premium': p95_latencies.get('premium', 0) <= 0.05  # 50ms
        }


async def main():
    """Example usage of performance optimization"""
    # Initialize optimizers for both tiers
    shared_optimizer = PerformanceOptimizer('shared')
    premium_optimizer = PerformanceOptimizer('premium')
    
    await shared_optimizer.initialize()
    await premium_optimizer.initialize()
    
    # Example optimized API endpoint
    @shared_optimizer.performance_monitor
    @shared_optimizer.tier_cache('portfolio', expire_override=120)
    async def get_portfolio(user_id: str) -> dict:
        # Simulate database query
        await asyncio.sleep(0.05)  # 50ms
        return {
            'user_id': user_id,
            'portfolio_value': 100000,
            'positions': ['RELIANCE', 'TCS', 'INFY']
        }
    
    # Test the optimized function
    result = await get_portfolio('user123')
    print(f"Portfolio result: {result}")
    
    # Cache warmer
    warmer = CacheWarmer('premium')
    await warmer.warmup_cache(premium_optimizer.redis_pool)
    
    # Cleanup
    shared_optimizer.redis_pool.close()
    await shared_optimizer.redis_pool.wait_closed()
    premium_optimizer.redis_pool.close()
    await premium_optimizer.redis_pool.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
