"""
GridWorks B2B Services - Performance and Load Tests
Comprehensive performance testing for all service components
"""

import pytest
import pytest_asyncio
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import json

from ...main import app
from ...config import settings


class TestAPIPerformance:
    """Performance tests for API endpoints."""
    
    @pytest.mark.asyncio
    async def test_ai_support_response_time_requirements(self, test_client: AsyncClient, override_service_dependencies):
        """Test AI support API response time requirements."""
        
        # Performance requirements by tier
        tier_requirements = {
            "growth": {"max_response_time": 5000, "target_response_time": 3000},      # 5s max, 3s target
            "enterprise": {"max_response_time": 3000, "target_response_time": 2000}, # 3s max, 2s target  
            "quantum": {"max_response_time": 1500, "target_response_time": 1000}     # 1.5s max, 1s target
        }
        
        for tier, requirements in tier_requirements.items():
            request_data = {
                "user_message": "What are the key factors affecting stock market volatility?",
                "language": "en",
                "user_context": {
                    "user_id": f"perf_test_user_{tier}",
                    "client_tier": tier
                },
                "conversation_history": [],
                "channel": "api"
            }
            
            # Measure response time over multiple requests
            response_times = []
            for i in range(10):
                start_time = time.time()
                
                response = await test_client.post(
                    "/api/v1/ai-services/support/query",
                    json=request_data
                )
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                assert response.status_code == 200
                response_times.append(response_time_ms)
            
            # Analyze performance metrics
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            max_response_time = max(response_times)
            
            # Assert performance requirements
            assert avg_response_time <= requirements["target_response_time"], \
                f"{tier} tier average response time {avg_response_time:.0f}ms exceeds target {requirements['target_response_time']}ms"
            
            assert p95_response_time <= requirements["max_response_time"], \
                f"{tier} tier P95 response time {p95_response_time:.0f}ms exceeds maximum {requirements['max_response_time']}ms"
            
            assert max_response_time <= requirements["max_response_time"] * 1.5, \
                f"{tier} tier maximum response time {max_response_time:.0f}ms exceeds acceptable limit"
    
    @pytest.mark.asyncio
    async def test_concurrent_user_load(self, test_client: AsyncClient, override_service_dependencies):
        """Test system performance under concurrent user load."""
        
        async def simulate_user_session(user_id: int, requests_per_user: int = 5):
            """Simulate a complete user session with multiple API calls."""
            session_results = []
            
            for request_num in range(requests_per_user):
                # Vary request types to simulate realistic usage
                if request_num % 3 == 0:
                    # AI Support request
                    request_data = {
                        "user_message": f"User {user_id} request {request_num}: Explain portfolio diversification",
                        "language": "en",
                        "user_context": {"user_id": f"load_user_{user_id}"},
                        "conversation_history": [],
                        "channel": "api"
                    }
                    endpoint = "/api/v1/ai-services/support/query"
                    
                elif request_num % 3 == 1:
                    # Intelligence analysis request
                    request_data = {
                        "intelligence_type": "morning_pulse",
                        "market_region": "india",
                        "user_context": {"user_id": f"load_user_{user_id}"}
                    }
                    endpoint = "/api/v1/ai-services/intelligence/analyze"
                    
                else:
                    # Profile/status request
                    request_data = None
                    endpoint = "/api/v1/partners/profile"
                
                start_time = time.time()
                
                if request_data:
                    response = await test_client.post(endpoint, json=request_data)
                else:
                    response = await test_client.get(endpoint)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                session_results.append({
                    "user_id": user_id,
                    "request_num": request_num,
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "success": response.status_code == 200
                })
                
                # Small delay between requests to simulate human behavior
                await asyncio.sleep(0.1)
            
            return session_results
        
        # Test different concurrent user loads
        load_scenarios = [
            {"concurrent_users": 50, "description": "Normal load"},
            {"concurrent_users": 100, "description": "High load"},
            {"concurrent_users": 200, "description": "Peak load"}
        ]
        
        for scenario in load_scenarios:
            concurrent_users = scenario["concurrent_users"]
            
            # Execute concurrent user sessions
            start_time = time.time()
            
            tasks = [simulate_user_session(user_id) for user_id in range(concurrent_users)]
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Flatten results and analyze
            flat_results = []
            for user_results in all_results:
                if isinstance(user_results, list):
                    flat_results.extend(user_results)
            
            # Calculate performance metrics
            successful_requests = [r for r in flat_results if r["success"]]
            failed_requests = [r for r in flat_results if not r["success"]]
            
            success_rate = len(successful_requests) / len(flat_results) if flat_results else 0
            avg_response_time = statistics.mean([r["response_time_ms"] for r in successful_requests]) if successful_requests else 0
            p95_response_time = statistics.quantiles([r["response_time_ms"] for r in successful_requests], n=20)[18] if len(successful_requests) >= 20 else 0
            
            requests_per_second = len(flat_results) / total_duration
            
            # Performance assertions
            assert success_rate >= 0.95, f"{scenario['description']}: Success rate {success_rate:.2%} below 95% minimum"
            assert avg_response_time <= 5000, f"{scenario['description']}: Average response time {avg_response_time:.0f}ms exceeds 5 second limit"
            assert p95_response_time <= 10000, f"{scenario['description']}: P95 response time {p95_response_time:.0f}ms exceeds 10 second limit"
            
            # Log performance results
            print(f"\n{scenario['description']} ({concurrent_users} users):")
            print(f"  Total requests: {len(flat_results)}")
            print(f"  Success rate: {success_rate:.2%}")
            print(f"  Average response time: {avg_response_time:.0f}ms")
            print(f"  P95 response time: {p95_response_time:.0f}ms")
            print(f"  Requests per second: {requests_per_second:.1f}")
            print(f"  Failed requests: {len(failed_requests)}")
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, test_client: AsyncClient, override_service_dependencies):
        """Test memory usage and leak detection under sustained load."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate sustained load for memory testing
        async def memory_stress_test():
            request_data = {
                "user_message": "Analyze the correlation between cryptocurrency prices and traditional stock markets",
                "language": "en",
                "user_context": {"user_id": "memory_test_user"},
                "conversation_history": [],
                "channel": "api"
            }
            
            tasks = []
            for i in range(100):  # 100 concurrent requests
                task = test_client.post("/api/v1/ai-services/support/query", json=request_data)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return len([r for r in responses if not isinstance(r, Exception)])
        
        # Run multiple rounds of stress testing
        memory_measurements = [initial_memory]
        
        for round_num in range(5):
            successful_requests = await memory_stress_test()
            
            # Measure memory after each round
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_measurements.append(current_memory)
            
            # Force garbage collection
            import gc
            gc.collect()
            
            print(f"Round {round_num + 1}: {successful_requests} successful requests, Memory: {current_memory:.1f}MB")
            
            # Small delay between rounds
            await asyncio.sleep(1)
        
        final_memory = memory_measurements[-1]
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_measurements)
        
        # Memory usage assertions
        assert memory_increase <= 100, f"Memory increased by {memory_increase:.1f}MB, indicating potential memory leak"
        assert max_memory <= initial_memory + 200, f"Peak memory usage {max_memory:.1f}MB exceeds acceptable limit"
        
        print(f"\nMemory Usage Analysis:")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(f"  Final memory: {final_memory:.1f}MB")
        print(f"  Memory increase: {memory_increase:.1f}MB")
        print(f"  Peak memory: {max_memory:.1f}MB")
    
    @pytest.mark.asyncio
    async def test_database_performance(self, test_client: AsyncClient, test_db_session):
        """Test database query performance under load."""
        
        async def database_intensive_operation():
            """Simulate database-intensive operations."""
            # Create test data
            from ...database.models import EnterpriseClient, User, APIKey
            
            # Multiple database operations
            operations = [
                # Client lookup
                lambda: test_db_session.query(EnterpriseClient).filter_by(is_active=True).first(),
                # User search
                lambda: test_db_session.query(User).filter_by(is_active=True).all(),
                # API key validation
                lambda: test_db_session.query(APIKey).filter_by(is_active=True).count(),
            ]
            
            start_time = time.time()
            
            for operation in operations:
                try:
                    operation()
                except Exception as e:
                    pass  # Handle any database exceptions
            
            end_time = time.time()
            return (end_time - start_time) * 1000  # ms
        
        # Test database performance under concurrent load
        concurrent_operations = 50
        tasks = [database_intensive_operation() for _ in range(concurrent_operations)]
        
        start_time = time.time()
        operation_times = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Filter out exceptions and calculate metrics
        valid_times = [t for t in operation_times if isinstance(t, (int, float))]
        
        if valid_times:
            avg_db_time = statistics.mean(valid_times)
            max_db_time = max(valid_times)
            p95_db_time = statistics.quantiles(valid_times, n=20)[18] if len(valid_times) >= 20 else max_db_time
            
            # Database performance assertions
            assert avg_db_time <= 100, f"Average database operation time {avg_db_time:.0f}ms exceeds 100ms limit"
            assert p95_db_time <= 500, f"P95 database operation time {p95_db_time:.0f}ms exceeds 500ms limit"
            assert max_db_time <= 1000, f"Maximum database operation time {max_db_time:.0f}ms exceeds 1 second limit"
            
            print(f"\nDatabase Performance Analysis:")
            print(f"  Concurrent operations: {concurrent_operations}")
            print(f"  Successful operations: {len(valid_times)}")
            print(f"  Average operation time: {avg_db_time:.0f}ms")
            print(f"  P95 operation time: {p95_db_time:.0f}ms")
            print(f"  Maximum operation time: {max_db_time:.0f}ms")


class TestCachePerformance:
    """Performance tests for caching mechanisms."""
    
    @pytest.mark.asyncio
    async def test_redis_cache_performance(self, test_client: AsyncClient, mock_redis):
        """Test Redis cache performance and hit rates."""
        
        # Configure cache for testing
        cache_test_data = [
            {"key": "market_data:nifty_50", "value": json.dumps({"price": 21500, "change": 0.8})},
            {"key": "ai_response:hash_123", "value": json.dumps({"response": "Cached AI response"})},
            {"key": "user_profile:user_456", "value": json.dumps({"name": "Test User", "tier": "enterprise"})}
        ]
        
        # Populate cache
        for item in cache_test_data:
            mock_redis.set(item["key"], item["value"])
        
        # Test cache read performance
        cache_read_times = []
        
        for _ in range(1000):  # 1000 cache reads
            start_time = time.time()
            
            # Simulate cache lookup
            for item in cache_test_data:
                result = mock_redis.get(item["key"])
                assert result is not None
            
            end_time = time.time()
            cache_read_times.append((end_time - start_time) * 1000)  # ms
        
        avg_cache_read_time = statistics.mean(cache_read_times)
        max_cache_read_time = max(cache_read_times)
        
        # Cache performance assertions
        assert avg_cache_read_time <= 1, f"Average cache read time {avg_cache_read_time:.2f}ms exceeds 1ms limit"
        assert max_cache_read_time <= 5, f"Maximum cache read time {max_cache_read_time:.2f}ms exceeds 5ms limit"
        
        # Test cache write performance
        cache_write_times = []
        
        for i in range(100):  # 100 cache writes
            start_time = time.time()
            
            mock_redis.set(f"perf_test_key_{i}", json.dumps({"data": f"test_data_{i}"}))
            
            end_time = time.time()
            cache_write_times.append((end_time - start_time) * 1000)  # ms
        
        avg_cache_write_time = statistics.mean(cache_write_times)
        max_cache_write_time = max(cache_write_times)
        
        # Cache write performance assertions
        assert avg_cache_write_time <= 2, f"Average cache write time {avg_cache_write_time:.2f}ms exceeds 2ms limit"
        assert max_cache_write_time <= 10, f"Maximum cache write time {max_cache_write_time:.2f}ms exceeds 10ms limit"
        
        print(f"\nCache Performance Analysis:")
        print(f"  Average read time: {avg_cache_read_time:.2f}ms")
        print(f"  Maximum read time: {max_cache_read_time:.2f}ms")
        print(f"  Average write time: {avg_cache_write_time:.2f}ms")
        print(f"  Maximum write time: {max_cache_write_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_cache_hit_ratio_optimization(self, test_client: AsyncClient, override_service_dependencies):
        """Test cache hit ratio for frequently accessed data."""
        
        # Simulate realistic API usage patterns
        frequent_requests = [
            {
                "user_message": "What is NIFTY 50?",
                "language": "en",
                "user_context": {"user_id": "frequent_user_1"},
                "conversation_history": [],
                "channel": "api"
            },
            {
                "user_message": "Explain mutual funds",
                "language": "en", 
                "user_context": {"user_id": "frequent_user_2"},
                "conversation_history": [],
                "channel": "api"
            },
            {
                "user_message": "What are derivatives?",
                "language": "en",
                "user_context": {"user_id": "frequent_user_3"},
                "conversation_history": [],
                "channel": "api"
            }
        ]
        
        # Track cache hit/miss for repeated requests
        cache_hits = 0
        cache_misses = 0
        
        # Make requests multiple times to test caching
        for round_num in range(5):
            for request_data in frequent_requests:
                start_time = time.time()
                
                response = await test_client.post(
                    "/api/v1/ai-services/support/query",
                    json=request_data
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                assert response.status_code == 200
                result = response.json()
                
                # Determine if response was cached (faster response time indicates cache hit)
                if response_time < 100:  # Cache hits should be under 100ms
                    cache_hits += 1
                else:
                    cache_misses += 1
        
        total_requests = cache_hits + cache_misses
        cache_hit_ratio = cache_hits / total_requests if total_requests > 0 else 0
        
        # Cache efficiency assertions
        assert cache_hit_ratio >= 0.6, f"Cache hit ratio {cache_hit_ratio:.2%} below 60% minimum for repeated requests"
        
        print(f"\nCache Hit Ratio Analysis:")
        print(f"  Total requests: {total_requests}")
        print(f"  Cache hits: {cache_hits}")
        print(f"  Cache misses: {cache_misses}")
        print(f"  Hit ratio: {cache_hit_ratio:.2%}")


class TestScalabilityLimits:
    """Tests for system scalability and breaking points."""
    
    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self, test_client: AsyncClient, test_api_key):
        """Test rate limiting enforcement under high load."""
        
        # Configure rate limit for testing (low limit to trigger quickly)
        api_key_headers = {"X-API-Key": test_api_key._test_key_value}
        
        # Mock rate limit to 10 requests per minute for testing
        with patch('...middleware.security.RateLimitMiddleware._get_rate_limit') as mock_rate_limit:
            mock_rate_limit.return_value = (10, 60)  # 10 requests per 60 seconds
            
            # Make requests up to rate limit
            responses = []
            rate_limited_responses = []
            
            for i in range(15):  # Try to exceed rate limit
                response = await test_client.get(
                    "/api/v1/partners/services/available",
                    headers=api_key_headers
                )
                
                if response.status_code == 200:
                    responses.append(response)
                elif response.status_code == 429:  # Rate limited
                    rate_limited_responses.append(response)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            # Verify rate limiting worked
            assert len(responses) <= 10, f"Rate limiting failed: {len(responses)} requests succeeded when limit is 10"
            assert len(rate_limited_responses) >= 5, f"Expected rate limiting to trigger for excess requests"
            
            # Check rate limit headers
            if responses:
                last_response = responses[-1]
                assert "X-RateLimit-Limit" in last_response.headers
                assert "X-RateLimit-Remaining" in last_response.headers
                assert "X-RateLimit-Reset" in last_response.headers
    
    @pytest.mark.asyncio 
    async def test_connection_pool_limits(self, test_client: AsyncClient):
        """Test database connection pool behavior under high concurrent load."""
        
        async def database_connection_test():
            """Test that simulates database connection usage."""
            try:
                response = await test_client.get("/api/v1/partners/profile")
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Test with connection pool size limits
        concurrent_connections = 100  # Exceed typical connection pool size
        
        start_time = time.time()
        tasks = [database_connection_test() for _ in range(concurrent_connections)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze connection handling
        successful_connections = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_connections = [r for r in results if not (isinstance(r, dict) and r.get("success"))]
        
        success_rate = len(successful_connections) / concurrent_connections
        total_time = end_time - start_time
        
        # Connection pool assertions
        assert success_rate >= 0.9, f"Connection pool handling: {success_rate:.2%} success rate below 90%"
        assert total_time <= 30, f"Connection pool exhaustion: {total_time:.1f}s total time exceeds 30s limit"
        
        print(f"\nConnection Pool Analysis:")
        print(f"  Concurrent connections attempted: {concurrent_connections}")
        print(f"  Successful connections: {len(successful_connections)}")
        print(f"  Failed connections: {len(failed_connections)}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Total execution time: {total_time:.1f}s")
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_under_load(self, test_client: AsyncClient, override_service_dependencies):
        """Test proper resource cleanup under sustained load."""
        import gc
        import threading
        
        # Get baseline metrics
        initial_thread_count = threading.active_count()
        gc.collect()
        initial_object_count = len(gc.get_objects())
        
        async def resource_intensive_operation():
            """Operation that creates and should clean up resources."""
            request_data = {
                "user_message": "Perform complex financial analysis with multiple data sources",
                "language": "en",
                "user_context": {"user_id": "resource_test_user"},
                "conversation_history": [
                    {"role": "user", "content": f"Previous context {i}"} 
                    for i in range(10)  # Large conversation history
                ],
                "channel": "api"
            }
            
            response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json=request_data
            )
            
            return response.status_code == 200
        
        # Run sustained operations
        operations_per_batch = 20
        batches = 5
        
        for batch_num in range(batches):
            # Execute batch of operations
            tasks = [resource_intensive_operation() for _ in range(operations_per_batch)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Force cleanup
            gc.collect()
            await asyncio.sleep(0.5)  # Allow cleanup time
            
            # Monitor resource usage
            current_thread_count = threading.active_count()
            current_object_count = len(gc.get_objects())
            
            print(f"Batch {batch_num + 1}: Threads: {current_thread_count}, Objects: {current_object_count}")
        
        # Final resource check
        final_thread_count = threading.active_count()
        final_object_count = len(gc.get_objects())
        
        thread_increase = final_thread_count - initial_thread_count
        object_increase = final_object_count - initial_object_count
        
        # Resource cleanup assertions
        assert thread_increase <= 5, f"Thread leak detected: {thread_increase} threads not cleaned up"
        assert object_increase <= initial_object_count * 0.1, f"Memory leak detected: {object_increase} objects not cleaned up"
        
        print(f"\nResource Cleanup Analysis:")
        print(f"  Initial threads: {initial_thread_count}")
        print(f"  Final threads: {final_thread_count}")
        print(f"  Thread increase: {thread_increase}")
        print(f"  Initial objects: {initial_object_count}")
        print(f"  Final objects: {final_object_count}")
        print(f"  Object increase: {object_increase}")


class TestPerformanceRegressionDetection:
    """Tests for detecting performance regressions."""
    
    @pytest.mark.asyncio
    async def test_baseline_performance_benchmarks(self, test_client: AsyncClient, override_service_dependencies):
        """Establish and verify baseline performance benchmarks."""
        
        # Define performance benchmarks for different operations
        benchmarks = {
            "ai_support_query": {
                "endpoint": "/api/v1/ai-services/support/query",
                "method": "POST",
                "data": {
                    "user_message": "What is the current market outlook for Indian equities?",
                    "language": "en",
                    "user_context": {"user_id": "benchmark_user"},
                    "conversation_history": [],
                    "channel": "api"
                },
                "target_response_time_ms": 2000,
                "max_response_time_ms": 5000
            },
            "intelligence_analysis": {
                "endpoint": "/api/v1/ai-services/intelligence/analyze",
                "method": "POST", 
                "data": {
                    "intelligence_type": "morning_pulse",
                    "market_region": "india",
                    "user_context": {"user_id": "benchmark_user"}
                },
                "target_response_time_ms": 3000,
                "max_response_time_ms": 8000
            },
            "profile_retrieval": {
                "endpoint": "/api/v1/partners/profile",
                "method": "GET",
                "data": None,
                "target_response_time_ms": 100,
                "max_response_time_ms": 500
            }
        }
        
        performance_results = {}
        
        for test_name, benchmark in benchmarks.items():
            # Execute multiple requests to get stable metrics
            response_times = []
            
            for _ in range(20):  # 20 samples for statistical significance
                start_time = time.time()
                
                if benchmark["method"] == "POST":
                    response = await test_client.post(benchmark["endpoint"], json=benchmark["data"])
                else:
                    response = await test_client.get(benchmark["endpoint"])
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                assert response.status_code == 200, f"Benchmark {test_name} failed with status {response.status_code}"
                response_times.append(response_time_ms)
            
            # Calculate performance metrics
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            max_response_time = max(response_times)
            
            performance_results[test_name] = {
                "average_ms": avg_response_time,
                "median_ms": median_response_time,
                "p95_ms": p95_response_time,
                "max_ms": max_response_time,
                "target_ms": benchmark["target_response_time_ms"],
                "max_allowed_ms": benchmark["max_response_time_ms"]
            }
            
            # Verify against benchmarks
            assert avg_response_time <= benchmark["target_response_time_ms"], \
                f"{test_name}: Average response time {avg_response_time:.0f}ms exceeds target {benchmark['target_response_time_ms']}ms"
            
            assert p95_response_time <= benchmark["max_response_time_ms"], \
                f"{test_name}: P95 response time {p95_response_time:.0f}ms exceeds maximum {benchmark['max_response_time_ms']}ms"
        
        # Log performance baseline
        print("\nPerformance Baseline Results:")
        for test_name, results in performance_results.items():
            print(f"  {test_name}:")
            print(f"    Average: {results['average_ms']:.0f}ms (target: {results['target_ms']}ms)")
            print(f"    P95: {results['p95_ms']:.0f}ms (max: {results['max_allowed_ms']}ms)")
            print(f"    Maximum: {results['max_ms']:.0f}ms")
        
        return performance_results
    
    @pytest.mark.asyncio
    async def test_performance_under_different_loads(self, test_client: AsyncClient, override_service_dependencies):
        """Test how performance degrades under increasing load."""
        
        load_levels = [1, 5, 10, 25, 50]  # Concurrent users
        performance_degradation = {}
        
        for load_level in load_levels:
            async def load_test_request():
                request_data = {
                    "user_message": "Analyze the impact of Federal Reserve policy on emerging markets",
                    "language": "en",
                    "user_context": {"user_id": f"load_test_user_{load_level}"},
                    "conversation_history": [],
                    "channel": "api"
                }
                
                start_time = time.time()
                response = await test_client.post("/api/v1/ai-services/support/query", json=request_data)
                end_time = time.time()
                
                return {
                    "success": response.status_code == 200,
                    "response_time_ms": (end_time - start_time) * 1000
                }
            
            # Execute concurrent requests
            tasks = [load_test_request() for _ in range(load_level)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            valid_results = [r for r in results if isinstance(r, dict) and r["success"]]
            
            if valid_results:
                avg_response_time = statistics.mean([r["response_time_ms"] for r in valid_results])
                success_rate = len(valid_results) / load_level
                
                performance_degradation[load_level] = {
                    "avg_response_time_ms": avg_response_time,
                    "success_rate": success_rate,
                    "successful_requests": len(valid_results)
                }
        
        # Analyze performance degradation
        baseline_performance = performance_degradation[1]["avg_response_time_ms"]
        
        for load_level, metrics in performance_degradation.items():
            degradation_factor = metrics["avg_response_time_ms"] / baseline_performance
            
            # Performance degradation should be reasonable
            if load_level <= 10:
                assert degradation_factor <= 2.0, f"Load {load_level}: Performance degraded by {degradation_factor:.1f}x (>2x limit)"
            elif load_level <= 50:
                assert degradation_factor <= 5.0, f"Load {load_level}: Performance degraded by {degradation_factor:.1f}x (>5x limit)"
            
            assert metrics["success_rate"] >= 0.95, f"Load {load_level}: Success rate {metrics['success_rate']:.2%} below 95%"
        
        print("\nPerformance Degradation Analysis:")
        for load_level, metrics in performance_degradation.items():
            degradation = metrics["avg_response_time_ms"] / baseline_performance
            print(f"  {load_level} concurrent users:")
            print(f"    Average response time: {metrics['avg_response_time_ms']:.0f}ms")
            print(f"    Performance degradation: {degradation:.1f}x")
            print(f"    Success rate: {metrics['success_rate']:.2%}")
        
        return performance_degradation