"""
Performance tests for response times and benchmarking.
"""
import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from sqlmodel import Session


@pytest.mark.performance
class TestResponseTimeBenchmarks:
    """Test response time benchmarks for all endpoints."""
    
    def test_health_endpoint_response_time(self, client: TestClient, benchmark):
        """Benchmark health endpoint response time."""
        def make_health_request():
            return client.get("/health")
        
        result = benchmark(make_health_request)
        assert result.status_code == 200
        
        # Verify benchmark statistics
        stats = benchmark.stats.stats
        assert stats.mean < 0.1  # 100ms maximum average
        assert stats.max < 0.5   # 500ms maximum single request
        
    def test_seo_optimization_response_time(self, client: TestClient, auth_headers: dict, benchmark):
        """Benchmark SEO optimization endpoint response time."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        seo_data = {
            "text": "High-quality wireless bluetooth headphones with excellent sound quality and noise cancellation",
            "max_length": 160,
            "keywords": ["bluetooth", "headphones", "wireless", "quality"]
        }
        
        def make_seo_request():
            return client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
        
        result = benchmark(make_seo_request)
        assert result.status_code == 200
        
        # SEO optimization might be more complex
        stats = benchmark.stats.stats
        assert stats.mean < 0.5  # 500ms maximum average
        assert stats.max < 2.0   # 2 seconds maximum single request
        
    def test_categories_endpoint_response_time(self, client: TestClient, auth_headers: dict, benchmark):
        """Benchmark categories endpoint response time."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        def make_categories_request():
            return client.get("/api/categories/", headers=auth_headers)
        
        result = benchmark(make_categories_request)
        assert result.status_code == 200
        
        stats = benchmark.stats.stats
        assert stats.mean < 0.3  # 300ms maximum average
        assert stats.max < 1.0   # 1 second maximum single request
        
    def test_authentication_response_time(self, client: TestClient, db: Session, benchmark):
        """Benchmark authentication endpoint response time."""
        from app.models import User
        from app.core.security import get_password_hash
        
        # Create test user
        user = User(
            email="perf_test@example.com",
            hashed_password=get_password_hash("PerfTestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        login_data = {
            "username": "perf_test@example.com",
            "password": "PerfTestPassword123!"
        }
        
        def make_auth_request():
            return client.post("/api/auth/token", data=login_data)
        
        result = benchmark(make_auth_request)
        assert result.status_code == 200
        
        # Authentication might involve password hashing
        stats = benchmark.stats.stats
        assert stats.mean < 1.0  # 1 second maximum average
        assert stats.max < 3.0   # 3 seconds maximum single request
        
    def test_oauth_initiation_response_time(self, client: TestClient, benchmark):
        """Benchmark OAuth initiation response time."""
        def make_oauth_request():
            return client.get("/oauth/login")
        
        result = benchmark(make_oauth_request)
        assert result.status_code in [200, 302]
        
        stats = benchmark.stats.stats
        assert stats.mean < 0.2  # 200ms maximum average
        assert stats.max < 1.0   # 1 second maximum single request


@pytest.mark.performance
class TestConcurrentRequestPerformance:
    """Test concurrent request handling performance."""
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, client: TestClient):
        """Test concurrent health check requests."""
        async def make_request():
            # Convert sync client to async operation
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Make 50 concurrent requests
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        successful_requests = [r for r in results if r["status_code"] == 200]
        response_times = [r["response_time"] for r in successful_requests]
        
        # Performance assertions
        assert len(successful_requests) == 50  # All should succeed
        assert max(response_times) < 2.0  # No request should take more than 2 seconds
        assert sum(response_times) / len(response_times) < 0.5  # Average under 500ms
        
    @pytest.mark.asyncio
    async def test_concurrent_seo_optimization(self, client: TestClient, auth_headers: dict):
        """Test concurrent SEO optimization requests."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        async def make_seo_request(request_id):
            seo_data = {
                "text": f"Product description {request_id} for performance testing with various features and benefits",
                "max_length": 160
            }
            
            start_time = time.time()
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Make 20 concurrent SEO requests
        tasks = [make_seo_request(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        # Performance assertions
        assert len(successful_requests) >= 18  # At least 90% should succeed
        if response_times:
            assert max(response_times) < 5.0  # No request should take more than 5 seconds
            assert sum(response_times) / len(response_times) < 2.0  # Average under 2 seconds
            
    def test_concurrent_authentication_requests(self, client: TestClient, db: Session):
        """Test concurrent authentication requests."""
        from app.models import User
        from app.core.security import get_password_hash
        import threading
        import queue
        
        # Create test user
        user = User(
            email="concurrent_auth@example.com",
            hashed_password=get_password_hash("ConcurrentPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        results = queue.Queue()
        
        def authenticate(worker_id):
            login_data = {
                "username": "concurrent_auth@example.com",
                "password": "ConcurrentPassword123!"
            }
            
            start_time = time.time()
            response = client.post("/api/auth/token", data=login_data)
            end_time = time.time()
            
            results.put({
                "worker_id": worker_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            })
        
        # Start 10 concurrent authentication requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=authenticate, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join()
            
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
            
        # Analyze results
        successful_requests = [r for r in all_results if r["success"]]
        response_times = [r["response_time"] for r in all_results]
        
        # Performance assertions
        assert len(all_results) == 10
        assert len(successful_requests) >= 8  # At least 80% should succeed
        assert max(response_times) < 5.0  # No request should take more than 5 seconds


@pytest.mark.performance
class TestMemoryUsageMonitoring:
    """Test memory usage during various operations."""
    
    def test_memory_usage_during_seo_operations(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test memory usage during SEO operations."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        initial_memory = memory_monitor['initial']
        process = memory_monitor['process']
        
        # Perform multiple SEO operations
        for i in range(100):
            seo_data = {
                "text": f"Memory test product description {i} with detailed features and specifications",
                "max_length": 160
            }
            
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            assert response.status_code == 200
            
            # Check memory periodically
            if i % 20 == 0:
                current_memory = process.memory_info().rss
                memory_increase = (current_memory - initial_memory) / 1024 / 1024  # MB
                
                # Memory should not increase excessively
                assert memory_increase < 50  # Less than 50MB increase during operations
                
        # Final memory check
        final_memory = process.memory_info().rss
        total_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Total memory increase should be reasonable
        assert total_increase < 100  # Less than 100MB total increase
        
    def test_memory_usage_during_concurrent_operations(self, client: TestClient, memory_monitor):
        """Test memory usage during concurrent operations."""
        import threading
        
        initial_memory = memory_monitor['initial']
        process = memory_monitor['process']
        
        def worker(worker_id, num_requests):
            for i in range(num_requests):
                response = client.get("/health")
                assert response.status_code == 200
                
        # Start multiple workers
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker, args=(worker_id, 50))
            threads.append(thread)
            thread.start()
            
        # Monitor memory during execution
        max_memory_increase = 0
        
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout per thread
            
            current_memory = process.memory_info().rss
            memory_increase = (current_memory - initial_memory) / 1024 / 1024  # MB
            max_memory_increase = max(max_memory_increase, memory_increase)
            
        # Memory usage should be reasonable during concurrent operations
        assert max_memory_increase < 200  # Less than 200MB increase
        
    def test_memory_cleanup_after_operations(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test memory cleanup after operations complete."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        initial_memory = memory_monitor['initial']
        process = memory_monitor['process']
        
        # Perform intensive operations
        for i in range(50):
            seo_data = {
                "text": "Large text content for memory cleanup testing " * 10,  # Larger text
                "max_length": 300
            }
            
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            assert response.status_code == 200
            
        # Memory after operations
        peak_memory = process.memory_info().rss
        peak_increase = (peak_memory - initial_memory) / 1024 / 1024  # MB
        
        # Wait a bit for potential cleanup
        import time
        time.sleep(2)
        
        # Check if memory was cleaned up
        final_memory = process.memory_info().rss
        final_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory should not have increased too much and should be somewhat stable
        assert peak_increase < 150  # Peak should be reasonable
        assert final_increase <= peak_increase + 10  # Final should not be much higher than peak


@pytest.mark.performance
class TestConnectionPoolingPerformance:
    """Test connection pooling performance."""
    
    def test_database_connection_performance(self, client: TestClient, db: Session):
        """Test database connection performance."""
        from sqlmodel import text
        
        # Test multiple database operations
        start_time = time.time()
        
        for i in range(100):
            result = db.exec(text("SELECT 1")).first()
            assert result == 1
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 100 simple queries quickly
        assert total_time < 5.0  # Under 5 seconds for 100 queries
        average_time = total_time / 100
        assert average_time < 0.05  # Under 50ms per query on average
        
    def test_concurrent_database_connections(self, engine):
        """Test concurrent database connections."""
        from sqlmodel import Session, text
        import threading
        import queue
        
        results = queue.Queue()
        
        def database_worker(worker_id, num_operations):
            try:
                with Session(engine) as session:
                    start_time = time.time()
                    
                    for i in range(num_operations):
                        result = session.exec(text("SELECT 1")).first()
                        assert result == 1
                        
                    end_time = time.time()
                    
                    results.put({
                        "worker_id": worker_id,
                        "success": True,
                        "time": end_time - start_time,
                        "operations": num_operations
                    })
                    
            except Exception as e:
                results.put({
                    "worker_id": worker_id,
                    "success": False,
                    "error": str(e)
                })
                
        # Start multiple database workers
        threads = []
        num_workers = 5
        operations_per_worker = 20
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=database_worker, 
                args=(worker_id, operations_per_worker)
            )
            threads.append(thread)
            thread.start()
            
        # Wait for all workers
        for thread in threads:
            thread.join()
            
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
            
        # Analyze results
        successful_workers = [r for r in all_results if r.get("success", False)]
        
        # Performance assertions
        assert len(all_results) == num_workers
        assert len(successful_workers) == num_workers  # All should succeed
        
        # Check timing
        for result in successful_workers:
            operations_time = result["time"]
            operations_count = result["operations"]
            avg_time_per_operation = operations_time / operations_count
            
            assert avg_time_per_operation < 0.1  # Under 100ms per operation
            assert operations_time < 10.0  # Under 10 seconds total per worker


@pytest.mark.performance
class TestLoadTestingScenarios:
    """Test various load testing scenarios."""
    
    def test_sustained_load_performance(self, client: TestClient):
        """Test performance under sustained load."""
        duration = 30  # 30 seconds
        start_time = time.time()
        
        request_count = 0
        successful_requests = 0
        response_times = []
        
        while time.time() - start_time < duration:
            request_start = time.time()
            response = client.get("/health")
            request_end = time.time()
            
            request_count += 1
            if response.status_code == 200:
                successful_requests += 1
                
            response_times.append(request_end - request_start)
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.01)  # 10ms delay
            
        # Calculate metrics
        success_rate = successful_requests / request_count
        average_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        requests_per_second = request_count / duration
        
        # Performance assertions
        assert success_rate >= 0.95  # At least 95% success rate
        assert average_response_time < 0.5  # Average under 500ms
        assert max_response_time < 2.0  # Max under 2 seconds
        assert requests_per_second >= 10  # At least 10 requests per second
        
    def test_burst_load_performance(self, client: TestClient):
        """Test performance under burst load."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def burst_worker(worker_id, requests_per_burst):
            worker_results = []
            
            for i in range(requests_per_burst):
                start_time = time.time()
                response = client.get("/health")
                end_time = time.time()
                
                worker_results.append({
                    "request_id": i,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                })
                
            results.put({
                "worker_id": worker_id,
                "results": worker_results
            })
            
        # Create burst load with multiple workers
        threads = []
        num_workers = 10
        requests_per_burst = 20
        
        burst_start = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=burst_worker,
                args=(worker_id, requests_per_burst)
            )
            threads.append(thread)
            thread.start()
            
        # Wait for burst to complete
        for thread in threads:
            thread.join()
            
        burst_end = time.time()
        burst_duration = burst_end - burst_start
        
        # Collect all results
        all_request_results = []
        while not results.empty():
            worker_result = results.get()
            all_request_results.extend(worker_result["results"])
            
        # Analyze burst performance
        total_requests = len(all_request_results)
        successful_requests = [r for r in all_request_results if r["success"]]
        response_times = [r["response_time"] for r in all_request_results]
        
        success_rate = len(successful_requests) / total_requests
        average_response_time = sum(response_times) / len(response_times)
        burst_throughput = total_requests / burst_duration
        
        # Performance assertions for burst load
        assert success_rate >= 0.8  # At least 80% success rate under burst
        assert average_response_time < 2.0  # Average under 2 seconds during burst
        assert burst_throughput >= 5  # At least 5 requests per second during burst
        assert burst_duration < 60  # Burst should complete within 60 seconds
        
    def test_gradual_load_increase_performance(self, client: TestClient):
        """Test performance with gradually increasing load."""
        load_levels = [1, 2, 5, 10, 15]  # Requests per second
        results_by_load = {}
        
        for load_level in load_levels:
            request_interval = 1.0 / load_level  # Seconds between requests
            test_duration = 10  # 10 seconds per load level
            
            start_time = time.time()
            load_results = []
            
            while time.time() - start_time < test_duration:
                request_start = time.time()
                response = client.get("/health")
                request_end = time.time()
                
                load_results.append({
                    "status_code": response.status_code,
                    "response_time": request_end - request_start,
                    "success": response.status_code == 200
                })
                
                # Wait for next request interval
                elapsed = time.time() - request_start
                if elapsed < request_interval:
                    time.sleep(request_interval - elapsed)
                    
            # Analyze results for this load level
            successful_requests = [r for r in load_results if r["success"]]
            success_rate = len(successful_requests) / len(load_results)
            avg_response_time = sum(r["response_time"] for r in load_results) / len(load_results)
            
            results_by_load[load_level] = {
                "success_rate": success_rate,
                "average_response_time": avg_response_time,
                "total_requests": len(load_results)
            }
            
        # Analyze degradation across load levels
        for load_level, results in results_by_load.items():
            # All load levels should maintain reasonable performance
            assert results["success_rate"] >= 0.9  # At least 90% success
            assert results["average_response_time"] < 1.0  # Under 1 second average
            
        # Check that performance doesn't degrade too much with increased load
        baseline_response_time = results_by_load[1]["average_response_time"]
        highest_load_response_time = results_by_load[15]["average_response_time"]
        
        # Response time shouldn't increase by more than 5x under highest load
        assert highest_load_response_time < baseline_response_time * 5