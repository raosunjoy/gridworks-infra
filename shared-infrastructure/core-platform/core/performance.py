"""
GridWorks Performance Optimization & Caching System
==================================================
⚡ Sub-100ms API Response Times
🚀 Intelligent Multi-Layer Caching
📈 Performance Analytics & Optimization
💾 Memory & Database Optimization
"""

import asyncio
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import pickle
import gzip
from functools import wraps
from decimal import Decimal

# Performance & Caching imports
import aioredis
import asyncio_throttle
from asyncio import Lock
import psutil
import threading


class CacheType(Enum):
    """Cache types for different use cases"""
    MEMORY = "memory"          # In-memory cache for ultra-fast access
    REDIS = "redis"           # Redis cache for shared data
    DATABASE = "database"     # Database-level caching
    CDN = "cdn"              # Content delivery network cache
    BROWSER = "browser"      # Browser cache headers


class PerformanceMetric(Enum):
    """Performance metrics to track"""
    RESPONSE_TIME = "response_time"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_QUERIES = "database_queries"
    ACTIVE_CONNECTIONS = "active_connections"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    hit_count: int = 0
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Performance analysis report"""
    timestamp: datetime = field(default_factory=datetime.now)
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage_percent: float = 0.0
    cpu_usage_percent: float = 0.0
    active_requests: int = 0
    slowest_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    optimization_recommendations: List[str] = field(default_factory=list)


class GridWorksPerformanceSystem:
    """Comprehensive performance optimization system"""
    
    def __init__(self):
        # Caching layers
        self.memory_cache = {}  # In-memory cache
        self.cache_locks = {}   # Per-key locks for cache operations
        self.redis_client = None
        
        # Performance tracking
        self.request_metrics = []
        self.performance_history = []
        self.active_requests = {}
        
        # Cache statistics
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage": 0
        }
        
        # Configuration
        self.config = {
            "memory_cache_max_size": 1000000,  # 1MB
            "memory_cache_max_entries": 10000,
            "cache_default_ttl": 300,  # 5 minutes
            "performance_metrics_retention": 3600,  # 1 hour
            "response_time_target": 100,  # 100ms target
            "cache_compression_threshold": 1024  # 1KB
        }
        
        # Background tasks
        self.background_tasks = []
        self.is_monitoring = False
    
    async def initialize(self):
        """Initialize the performance system"""
        
        # Initialize Redis connection
        try:
            self.redis_client = await aioredis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=False  # We'll handle encoding manually for binary data
            )
            await self.redis_client.ping()
            print("✅ Redis connection established")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
        
        # Start background monitoring
        self.is_monitoring = True
        self.background_tasks = [
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._cleanup_expired_cache()),
            asyncio.create_task(self._optimize_cache_memory())
        ]
        
        print("🚀 GridWorks Performance System initialized")
    
    async def shutdown(self):
        """Shutdown the performance system"""
        
        self.is_monitoring = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        print("🛑 GridWorks Performance System shutdown")
    
    # Caching Methods
    async def get_cached(self, key: str, cache_type: CacheType = CacheType.MEMORY) -> Optional[Any]:
        """Get value from cache"""
        
        start_time = time.time()
        
        try:
            if cache_type == CacheType.MEMORY:
                result = await self._get_memory_cache(key)
            elif cache_type == CacheType.REDIS:
                result = await self._get_redis_cache(key)
            else:
                result = None
            
            # Update cache statistics
            if result is not None:
                self.cache_stats["hits"] += 1
            else:
                self.cache_stats["misses"] += 1
            
            # Track cache performance
            cache_time = (time.time() - start_time) * 1000
            await self._record_cache_metric("get", cache_time, key, result is not None)
            
            return result
            
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set_cached(self, key: str, value: Any, ttl: Optional[int] = None, 
                        cache_type: CacheType = CacheType.MEMORY, tags: List[str] = None) -> bool:
        """Set value in cache"""
        
        start_time = time.time()
        
        try:
            ttl = ttl or self.config["cache_default_ttl"]
            tags = tags or []
            
            if cache_type == CacheType.MEMORY:
                success = await self._set_memory_cache(key, value, ttl, tags)
            elif cache_type == CacheType.REDIS:
                success = await self._set_redis_cache(key, value, ttl, tags)
            else:
                success = False
            
            # Track cache performance
            cache_time = (time.time() - start_time) * 1000
            await self._record_cache_metric("set", cache_time, key, success)
            
            return success
            
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete_cached(self, key: str, cache_type: CacheType = CacheType.MEMORY) -> bool:
        """Delete value from cache"""
        
        try:
            if cache_type == CacheType.MEMORY:
                return await self._delete_memory_cache(key)
            elif cache_type == CacheType.REDIS:
                return await self._delete_redis_cache(key)
            
            return False
            
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    async def invalidate_cache_by_tags(self, tags: List[str], cache_type: CacheType = CacheType.MEMORY):
        """Invalidate cache entries by tags"""
        
        if cache_type == CacheType.MEMORY:
            keys_to_delete = []
            for key, entry in self.memory_cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                await self._delete_memory_cache(key)
        
        elif cache_type == CacheType.REDIS and self.redis_client:
            # Redis tag-based invalidation would require additional data structures
            # For now, we'll implement a simple pattern-based approach
            for tag in tags:
                pattern = f"tag:{tag}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
    
    # Memory Cache Implementation
    async def _get_memory_cache(self, key: str) -> Optional[Any]:
        """Get from memory cache"""
        
        if key not in self.memory_cache:
            return None
        
        entry = self.memory_cache[key]
        
        # Check expiration
        if entry.expires_at and datetime.now() > entry.expires_at:
            await self._delete_memory_cache(key)
            return None
        
        # Update access metadata
        entry.accessed_at = datetime.now()
        entry.hit_count += 1
        
        return entry.value
    
    async def _set_memory_cache(self, key: str, value: Any, ttl: int, tags: List[str]) -> bool:
        """Set in memory cache"""
        
        # Calculate size
        size_bytes = len(pickle.dumps(value))
        
        # Check if we need to make space
        await self._ensure_memory_cache_capacity(size_bytes)
        
        # Create cache entry
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        
        entry = CacheEntry(
            key=key,
            value=value,
            expires_at=expires_at,
            size_bytes=size_bytes,
            tags=tags
        )
        
        # Acquire lock for this key
        if key not in self.cache_locks:
            self.cache_locks[key] = Lock()
        
        async with self.cache_locks[key]:
            self.memory_cache[key] = entry
            self.cache_stats["memory_usage"] += size_bytes
        
        return True
    
    async def _delete_memory_cache(self, key: str) -> bool:
        """Delete from memory cache"""
        
        if key not in self.memory_cache:
            return False
        
        if key in self.cache_locks:
            async with self.cache_locks[key]:
                entry = self.memory_cache.pop(key, None)
                if entry:
                    self.cache_stats["memory_usage"] -= entry.size_bytes
                    self.cache_stats["evictions"] += 1
                del self.cache_locks[key]
        else:
            entry = self.memory_cache.pop(key, None)
            if entry:
                self.cache_stats["memory_usage"] -= entry.size_bytes
                self.cache_stats["evictions"] += 1
        
        return True
    
    async def _ensure_memory_cache_capacity(self, new_entry_size: int):
        """Ensure memory cache has capacity for new entry"""
        
        max_size = self.config["memory_cache_max_size"]
        max_entries = self.config["memory_cache_max_entries"]
        
        # Check size limit
        while (self.cache_stats["memory_usage"] + new_entry_size > max_size or 
               len(self.memory_cache) >= max_entries):
            
            # Find least recently used entry
            lru_key = None
            lru_time = datetime.now()
            
            for key, entry in self.memory_cache.items():
                if entry.accessed_at < lru_time:
                    lru_time = entry.accessed_at
                    lru_key = key
            
            if lru_key:
                await self._delete_memory_cache(lru_key)
            else:
                break  # No entries to evict
    
    # Redis Cache Implementation
    async def _get_redis_cache(self, key: str) -> Optional[Any]:
        """Get from Redis cache"""
        
        if not self.redis_client:
            return None
        
        try:
            # Check if key exists and get value
            raw_data = await self.redis_client.get(f"cache:{key}")
            
            if raw_data is None:
                return None
            
            # Handle compressed data
            if raw_data.startswith(b"GZIP:"):
                raw_data = gzip.decompress(raw_data[5:])
            
            # Deserialize
            value = pickle.loads(raw_data)
            
            return value
            
        except Exception as e:
            print(f"Redis cache get error: {e}")
            return None
    
    async def _set_redis_cache(self, key: str, value: Any, ttl: int, tags: List[str]) -> bool:
        """Set in Redis cache"""
        
        if not self.redis_client:
            return False
        
        try:
            # Serialize value
            raw_data = pickle.dumps(value)
            
            # Compress if large
            if len(raw_data) > self.config["cache_compression_threshold"]:
                raw_data = b"GZIP:" + gzip.compress(raw_data)
            
            # Set in Redis with TTL
            await self.redis_client.setex(f"cache:{key}", ttl, raw_data)
            
            # Set tags for invalidation
            for tag in tags:
                await self.redis_client.sadd(f"tag:{tag}", key)
                await self.redis_client.expire(f"tag:{tag}", ttl)
            
            return True
            
        except Exception as e:
            print(f"Redis cache set error: {e}")
            return False
    
    async def _delete_redis_cache(self, key: str) -> bool:
        """Delete from Redis cache"""
        
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(f"cache:{key}")
            return result > 0
            
        except Exception as e:
            print(f"Redis cache delete error: {e}")
            return False
    
    # Performance Monitoring
    async def _monitor_performance(self):
        """Monitor system performance continuously"""
        
        while self.is_monitoring:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Calculate cache hit rate
                total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
                hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
                
                # Calculate average response time
                recent_metrics = [m for m in self.request_metrics if m["timestamp"] > time.time() - 300]  # Last 5 minutes
                avg_response_time = sum(m["duration"] for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
                
                # Create performance snapshot
                snapshot = {
                    "timestamp": time.time(),
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory_percent,
                    "cache_hit_rate": hit_rate,
                    "avg_response_time": avg_response_time,
                    "active_requests": len(self.active_requests),
                    "cache_memory_usage": self.cache_stats["memory_usage"],
                    "cache_entries": len(self.memory_cache)
                }
                
                self.performance_history.append(snapshot)
                
                # Keep only recent history
                cutoff_time = time.time() - self.config["performance_metrics_retention"]
                self.performance_history = [h for h in self.performance_history if h["timestamp"] > cutoff_time]
                
                # Check for performance issues
                await self._check_performance_alerts(snapshot)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_cache(self):
        """Cleanup expired cache entries"""
        
        while self.is_monitoring:
            try:
                expired_keys = []
                now = datetime.now()
                
                for key, entry in self.memory_cache.items():
                    if entry.expires_at and now > entry.expires_at:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self._delete_memory_cache(key)
                
                if expired_keys:
                    print(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                print(f"Cache cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _optimize_cache_memory(self):
        """Optimize cache memory usage"""
        
        while self.is_monitoring:
            try:
                # If memory usage is high, optimize
                if self.cache_stats["memory_usage"] > self.config["memory_cache_max_size"] * 0.8:
                    
                    # Find entries that haven't been accessed recently
                    cutoff_time = datetime.now() - timedelta(minutes=30)
                    stale_keys = []
                    
                    for key, entry in self.memory_cache.items():
                        if entry.accessed_at < cutoff_time and entry.hit_count < 5:
                            stale_keys.append(key)
                    
                    # Remove stale entries
                    for key in stale_keys[:100]:  # Limit to 100 at a time
                        await self._delete_memory_cache(key)
                    
                    if stale_keys:
                        print(f"🗂️ Optimized cache: removed {len(stale_keys)} stale entries")
                
                await asyncio.sleep(600)  # Optimize every 10 minutes
                
            except Exception as e:
                print(f"Cache optimization error: {e}")
                await asyncio.sleep(600)
    
    async def _check_performance_alerts(self, snapshot: Dict[str, Any]):
        """Check for performance alerts"""
        
        alerts = []
        
        # High response time alert
        if snapshot["avg_response_time"] > self.config["response_time_target"] * 2:
            alerts.append(f"High response time: {snapshot['avg_response_time']:.0f}ms")
        
        # Low cache hit rate alert
        if snapshot["cache_hit_rate"] < 70:
            alerts.append(f"Low cache hit rate: {snapshot['cache_hit_rate']:.1f}%")
        
        # High memory usage alert
        if snapshot["memory_usage"] > 85:
            alerts.append(f"High memory usage: {snapshot['memory_usage']:.1f}%")
        
        # High CPU usage alert
        if snapshot["cpu_usage"] > 80:
            alerts.append(f"High CPU usage: {snapshot['cpu_usage']:.1f}%")
        
        if alerts:
            print(f"⚠️ Performance alerts: {', '.join(alerts)}")
    
    async def _record_cache_metric(self, operation: str, duration: float, key: str, success: bool):
        """Record cache operation metric"""
        
        metric = {
            "timestamp": time.time(),
            "operation": operation,
            "duration": duration,
            "key": key,
            "success": success
        }
        
        # Keep only recent metrics
        cutoff_time = time.time() - 3600  # 1 hour
        self.request_metrics = [m for m in self.request_metrics if m["timestamp"] > cutoff_time]
        self.request_metrics.append(metric)
    
    # Performance Decorators and Utilities
    def cache_result(self, ttl: int = None, cache_type: CacheType = CacheType.MEMORY, 
                    key_generator: Callable = None, tags: List[str] = None):
        """Decorator to cache function results"""
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
                
                # Try to get from cache
                cached_result = await self.get_cached(cache_key, cache_type)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set_cached(cache_key, result, ttl, cache_type, tags)
                
                return result
            
            return wrapper
        return decorator
    
    def track_performance(self, operation_name: str = None):
        """Decorator to track function performance"""
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request_id = str(uuid.uuid4())
                operation = operation_name or func.__name__
                start_time = time.time()
                
                # Track active request
                self.active_requests[request_id] = {
                    "operation": operation,
                    "start_time": start_time,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Record successful execution
                    duration = (time.time() - start_time) * 1000  # ms
                    
                    metric = {
                        "timestamp": time.time(),
                        "operation": operation,
                        "duration": duration,
                        "success": True,
                        "request_id": request_id
                    }
                    
                    self.request_metrics.append(metric)
                    
                    return result
                    
                except Exception as e:
                    # Record failed execution
                    duration = (time.time() - start_time) * 1000  # ms
                    
                    metric = {
                        "timestamp": time.time(),
                        "operation": operation,
                        "duration": duration,
                        "success": False,
                        "error": str(e),
                        "request_id": request_id
                    }
                    
                    self.request_metrics.append(metric)
                    
                    raise
                    
                finally:
                    # Remove from active requests
                    self.active_requests.pop(request_id, None)
            
            return wrapper
        return decorator
    
    # Public API Methods
    async def get_performance_report(self) -> PerformanceReport:
        """Generate comprehensive performance report"""
        
        report = PerformanceReport()
        
        # Calculate response time metrics
        recent_metrics = [m for m in self.request_metrics if m["timestamp"] > time.time() - 300]  # Last 5 minutes
        
        if recent_metrics:
            response_times = [m["duration"] for m in recent_metrics if m["success"]]
            
            if response_times:
                response_times.sort()
                report.avg_response_time = sum(response_times) / len(response_times)
                
                p95_index = int(len(response_times) * 0.95)
                p99_index = int(len(response_times) * 0.99)
                
                report.p95_response_time = response_times[min(p95_index, len(response_times) - 1)]
                report.p99_response_time = response_times[min(p99_index, len(response_times) - 1)]
        
        # Cache hit rate
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        report.cache_hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # System metrics
        report.memory_usage_percent = psutil.virtual_memory().percent
        report.cpu_usage_percent = psutil.cpu_percent()
        report.active_requests = len(self.active_requests)
        
        # Find slowest endpoints
        operation_times = {}
        for metric in recent_metrics:
            op = metric["operation"]
            if op not in operation_times:
                operation_times[op] = []
            operation_times[op].append(metric["duration"])
        
        slowest_ops = []
        for op, times in operation_times.items():
            avg_time = sum(times) / len(times)
            slowest_ops.append({"operation": op, "avg_time": avg_time, "call_count": len(times)})
        
        slowest_ops.sort(key=lambda x: x["avg_time"], reverse=True)
        report.slowest_endpoints = slowest_ops[:10]
        
        # Generate optimization recommendations
        report.optimization_recommendations = await self._generate_optimization_recommendations(report)
        
        return report
    
    async def _generate_optimization_recommendations(self, report: PerformanceReport) -> List[str]:
        """Generate optimization recommendations based on performance data"""
        
        recommendations = []
        
        # Response time recommendations
        if report.avg_response_time > self.config["response_time_target"]:
            recommendations.append(f"Average response time ({report.avg_response_time:.0f}ms) exceeds target. Consider caching frequently accessed data.")
        
        # Cache recommendations
        if report.cache_hit_rate < 70:
            recommendations.append(f"Cache hit rate ({report.cache_hit_rate:.1f}%) is low. Review cache keys and TTL settings.")
        
        # Memory recommendations
        if report.memory_usage_percent > 80:
            recommendations.append("High memory usage detected. Consider implementing cache eviction policies.")
        
        # Slow endpoint recommendations
        if report.slowest_endpoints:
            slowest = report.slowest_endpoints[0]
            if slowest["avg_time"] > 500:  # 500ms
                recommendations.append(f"Endpoint '{slowest['operation']}' is slow ({slowest['avg_time']:.0f}ms avg). Consider optimization or caching.")
        
        # Database query recommendations
        db_operations = [op for op in report.slowest_endpoints if "db" in op["operation"].lower() or "query" in op["operation"].lower()]
        if db_operations:
            recommendations.append("Database operations detected in slow endpoints. Consider query optimization or connection pooling.")
        
        return recommendations
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "memory_cache": {
                "entries": len(self.memory_cache),
                "memory_usage_bytes": self.cache_stats["memory_usage"],
                "memory_usage_mb": self.cache_stats["memory_usage"] / 1024 / 1024,
                "max_size_mb": self.config["memory_cache_max_size"] / 1024 / 1024,
                "utilization_percent": (self.cache_stats["memory_usage"] / self.config["memory_cache_max_size"]) * 100
            },
            "statistics": {
                "total_hits": self.cache_stats["hits"],
                "total_misses": self.cache_stats["misses"],
                "hit_rate_percent": hit_rate,
                "total_evictions": self.cache_stats["evictions"]
            },
            "redis_available": self.redis_client is not None
        }
    
    async def clear_cache(self, cache_type: CacheType = CacheType.MEMORY):
        """Clear cache"""
        
        if cache_type == CacheType.MEMORY:
            self.memory_cache.clear()
            self.cache_locks.clear()
            self.cache_stats["memory_usage"] = 0
            
        elif cache_type == CacheType.REDIS and self.redis_client:
            # Clear all cache keys
            keys = await self.redis_client.keys("cache:*")
            if keys:
                await self.redis_client.delete(*keys)
        
        print(f"🧹 Cleared {cache_type.value} cache")
    
    async def preload_cache(self, preload_functions: List[Callable]):
        """Preload cache with frequently accessed data"""
        
        print("🔄 Preloading cache...")
        
        preload_tasks = []
        for func in preload_functions:
            if asyncio.iscoroutinefunction(func):
                preload_tasks.append(func())
            else:
                # Wrap sync function
                preload_tasks.append(asyncio.create_task(asyncio.to_thread(func)))
        
        results = await asyncio.gather(*preload_tasks, return_exceptions=True)
        
        successful_preloads = sum(1 for result in results if not isinstance(result, Exception))
        
        print(f"✅ Cache preload completed: {successful_preloads}/{len(preload_functions)} successful")


# Global performance system instance
performance_system = GridWorksPerformanceSystem()


# FastAPI middleware for automatic performance tracking
class PerformanceMiddleware:
    """FastAPI middleware for automatic performance tracking"""
    
    def __init__(self, performance_system: GridWorksPerformanceSystem):
        self.performance = performance_system
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Track request start
        self.performance.active_requests[request_id] = {
            "method": request.method,
            "path": request.url.path,
            "start_time": start_time,
            "client_ip": request.client.host if request.client else "unknown"
        }
        
        try:
            response = await call_next(request)
            
            # Record successful request
            duration = (time.time() - start_time) * 1000
            
            metric = {
                "timestamp": time.time(),
                "operation": f"{request.method} {request.url.path}",
                "duration": duration,
                "success": True,
                "status_code": response.status_code,
                "request_id": request_id
            }
            
            self.performance.request_metrics.append(metric)
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Record failed request
            duration = (time.time() - start_time) * 1000
            
            metric = {
                "timestamp": time.time(),
                "operation": f"{request.method} {request.url.path}",
                "duration": duration,
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
            
            self.performance.request_metrics.append(metric)
            
            raise
            
        finally:
            # Remove from active requests
            self.performance.active_requests.pop(request_id, None)


# Export main classes and functions
__all__ = [
    "GridWorksPerformanceSystem",
    "PerformanceMiddleware",
    "CacheType",
    "PerformanceReport",
    "performance_system"
]