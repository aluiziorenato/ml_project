"""
Performance tests for concurrent load and memory usage monitoring.
"""
import pytest
import time
import asyncio
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from sqlmodel import Session
import psutil
import gc


@pytest.mark.performance
class TestConcurrentLoadPerformance:
    """Test performance under concurrent load scenarios."""
    
    def test_concurrent_health_check_load(self, client: TestClient):
        """Test concurrent health check requests under load."""
        num_workers = 20
        requests_per_worker = 50
        timeout_seconds = 60
        
        results = queue.Queue()
        
        def worker(worker_id):
            worker_results = []
            
            for i in range(requests_per_worker):
                start_time = time.time()
                
                try:
                    response = client.get("/health")
                    end_time = time.time()
                    
                    worker_results.append({
                        "worker_id": worker_id,
                        "request_id": i,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    worker_results.append({
                        "worker_id": worker_id,
                        "request_id": i,
                        "error": str(e),
                        "response_time": end_time - start_time,
                        "success": False
                    })
                    
            results.put(worker_results)
            
        # Start all workers
        threads = []
        test_start_time = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
            
        # Wait for all workers to complete
        for thread in threads:
            thread.join(timeout=timeout_seconds)
            
        test_end_time = time.time()
        total_test_time = test_end_time - test_start_time
        
        # Collect all results
        all_results = []
        while not results.empty():
            worker_results = results.get()
            all_results.extend(worker_results)
            
        # Analyze performance
        total_requests = len(all_results)
        successful_requests = [r for r in all_results if r.get("success", False)]
        failed_requests = [r for r in all_results if not r.get("success", False)]
        
        response_times = [r["response_time"] for r in successful_requests]
        
        # Performance metrics
        success_rate = len(successful_requests) / total_requests
        average_response_time = sum(response_times) / len(response_times) if response_times else float('inf')
        max_response_time = max(response_times) if response_times else float('inf')
        min_response_time = min(response_times) if response_times else 0
        throughput = total_requests / total_test_time
        
        # Performance assertions
        assert total_requests == num_workers * requests_per_worker
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95%"
        assert average_response_time < 1.0, f"Average response time {average_response_time:.3f}s above 1s"
        assert max_response_time < 5.0, f"Max response time {max_response_time:.3f}s above 5s"
        assert throughput >= 50, f"Throughput {throughput:.1f} req/s below 50 req/s"
        assert total_test_time < timeout_seconds, f"Test took {total_test_time:.1f}s, exceeding {timeout_seconds}s"
        
    def test_mixed_endpoint_concurrent_load(self, client: TestClient, auth_headers: dict):
        """Test concurrent load across multiple endpoints."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        endpoints = [
            {"method": "GET", "url": "/health", "data": None, "headers": None, "weight": 0.4},
            {"method": "GET", "url": "/api/categories/", "data": None, "headers": auth_headers, "weight": 0.3},
            {"method": "POST", "url": "/api/seo/optimize", 
             "data": {"text": "Mixed load test product description", "max_length": 160}, 
             "headers": auth_headers, "weight": 0.3}
        ]
        
        num_workers = 15
        requests_per_worker = 30
        results = queue.Queue()
        
        def mixed_worker(worker_id):
            import random
            worker_results = []
            
            for i in range(requests_per_worker):
                # Select endpoint based on weight
                endpoint = random.choices(
                    endpoints, 
                    weights=[e["weight"] for e in endpoints]
                )[0]
                
                start_time = time.time()
                
                try:
                    if endpoint["method"] == "GET":
                        response = client.get(endpoint["url"], headers=endpoint["headers"])
                    else:
                        response = client.post(
                            endpoint["url"], 
                            json=endpoint["data"], 
                            headers=endpoint["headers"]
                        )
                        
                    end_time = time.time()
                    
                    worker_results.append({
                        "worker_id": worker_id,
                        "request_id": i,
                        "endpoint": endpoint["url"],
                        "method": endpoint["method"],
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    worker_results.append({
                        "worker_id": worker_id,
                        "request_id": i,
                        "endpoint": endpoint["url"],
                        "method": endpoint["method"],
                        "error": str(e),
                        "response_time": end_time - start_time,
                        "success": False
                    })
                    
            results.put(worker_results)
            
        # Execute mixed load test
        threads = []
        test_start_time = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=mixed_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join(timeout=120)  # 2 minute timeout
            
        test_end_time = time.time()
        total_test_time = test_end_time - test_start_time
        
        # Collect and analyze results
        all_results = []
        while not results.empty():
            worker_results = results.get()
            all_results.extend(worker_results)
            
        # Group results by endpoint
        results_by_endpoint = {}
        for result in all_results:
            endpoint = result["endpoint"]
            if endpoint not in results_by_endpoint:
                results_by_endpoint[endpoint] = []
            results_by_endpoint[endpoint].append(result)
            
        # Analyze performance by endpoint
        for endpoint, endpoint_results in results_by_endpoint.items():
            successful_requests = [r for r in endpoint_results if r.get("success", False)]
            success_rate = len(successful_requests) / len(endpoint_results)
            
            if successful_requests:
                response_times = [r["response_time"] for r in successful_requests]
                avg_response_time = sum(response_times) / len(response_times)
                
                # Endpoint-specific performance requirements
                if endpoint == "/health":
                    assert success_rate >= 0.98, f"Health endpoint success rate {success_rate:.2%} below 98%"
                    assert avg_response_time < 0.5, f"Health endpoint avg response time {avg_response_time:.3f}s above 0.5s"
                elif endpoint == "/api/categories/":
                    assert success_rate >= 0.95, f"Categories endpoint success rate {success_rate:.2%} below 95%"
                    assert avg_response_time < 1.0, f"Categories endpoint avg response time {avg_response_time:.3f}s above 1s"
                elif endpoint == "/api/seo/optimize":
                    assert success_rate >= 0.90, f"SEO endpoint success rate {success_rate:.2%} below 90%"
                    assert avg_response_time < 2.0, f"SEO endpoint avg response time {avg_response_time:.3f}s above 2s"
                    
    def test_thread_pool_executor_performance(self, client: TestClient):
        """Test performance using ThreadPoolExecutor for concurrent requests."""
        max_workers = 10
        total_requests = 100
        
        def make_request(request_id):
            start_time = time.time()
            
            try:
                response = client.get("/health")
                end_time = time.time()
                
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
                
            except Exception as e:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "error": str(e),
                    "response_time": end_time - start_time,
                    "success": False
                }
                
        # Execute requests using ThreadPoolExecutor
        test_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_request = {
                executor.submit(make_request, i): i 
                for i in range(total_requests)
            }
            
            results = []
            for future in as_completed(future_to_request, timeout=60):
                result = future.result()
                results.append(result)
                
        test_end_time = time.time()
        total_test_time = test_end_time - test_start_time
        
        # Analyze results
        successful_requests = [r for r in results if r.get("success", False)]
        success_rate = len(successful_requests) / len(results)
        
        response_times = [r["response_time"] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else float('inf')
        throughput = total_requests / total_test_time
        
        # Performance assertions
        assert len(results) == total_requests
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95%"
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s above 1s"
        assert throughput >= 20, f"Throughput {throughput:.1f} req/s below 20 req/s"
        assert total_test_time < 30, f"Test took {total_test_time:.1f}s, exceeding 30s"


@pytest.mark.performance
class TestMemoryUsageMonitoring:
    """Test memory usage monitoring during concurrent operations."""
    
    def test_memory_usage_during_concurrent_requests(self, client: TestClient, memory_monitor):
        """Test memory usage during concurrent request processing."""
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        memory_samples = []
        results = queue.Queue()
        
        def memory_monitor_worker():
            """Monitor memory usage during test execution."""
            start_time = time.time()
            while time.time() - start_time < 60:  # Monitor for 60 seconds
                current_memory = process.memory_info().rss
                memory_samples.append({
                    "timestamp": time.time(),
                    "memory_rss": current_memory,
                    "memory_increase_mb": (current_memory - initial_memory) / 1024 / 1024
                })
                time.sleep(0.5)  # Sample every 500ms
                
        def request_worker(worker_id, num_requests):
            """Generate concurrent requests."""
            for i in range(num_requests):
                try:
                    response = client.get("/health")
                    results.put({
                        "worker_id": worker_id,
                        "request_id": i,
                        "status_code": response.status_code,
                        "success": response.status_code == 200
                    })
                except Exception as e:
                    results.put({
                        "worker_id": worker_id,
                        "request_id": i,
                        "error": str(e),
                        "success": False
                    })
                    
                # Small delay to avoid overwhelming
                time.sleep(0.01)
                
        # Start memory monitoring
        monitor_thread = threading.Thread(target=memory_monitor_worker)
        monitor_thread.start()
        
        # Start request workers
        num_workers = 8
        requests_per_worker = 50
        request_threads = []
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=request_worker, args=(worker_id, requests_per_worker))
            request_threads.append(thread)
            thread.start()
            
        # Wait for request workers to complete
        for thread in request_threads:
            thread.join()
            
        # Stop memory monitoring
        monitor_thread.join(timeout=5)
        
        # Collect request results
        request_results = []
        while not results.empty():
            request_results.append(results.get())
            
        # Analyze memory usage
        if memory_samples:
            max_memory_increase = max(sample["memory_increase_mb"] for sample in memory_samples)
            avg_memory_increase = sum(sample["memory_increase_mb"] for sample in memory_samples) / len(memory_samples)
            final_memory_increase = memory_samples[-1]["memory_increase_mb"]
            
            # Memory usage assertions
            assert max_memory_increase < 200, f"Peak memory increase {max_memory_increase:.1f}MB exceeds 200MB"
            assert avg_memory_increase < 100, f"Average memory increase {avg_memory_increase:.1f}MB exceeds 100MB"
            assert final_memory_increase < 150, f"Final memory increase {final_memory_increase:.1f}MB exceeds 150MB"
            
        # Request performance assertions
        successful_requests = [r for r in request_results if r.get("success", False)]
        success_rate = len(successful_requests) / len(request_results)
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95% during memory monitoring"
        
    def test_memory_leak_detection(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test for potential memory leaks during repeated operations."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        # Perform multiple cycles of operations
        cycle_memory_data = []
        
        for cycle in range(5):  # 5 cycles
            cycle_start_memory = process.memory_info().rss
            
            # Perform operations in this cycle
            for i in range(50):
                seo_data = {
                    "text": f"Memory leak test cycle {cycle} request {i} with detailed product description",
                    "max_length": 160
                }
                
                response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
                assert response.status_code == 200
                
            # Force garbage collection
            gc.collect()
            
            # Measure memory after cycle
            cycle_end_memory = process.memory_info().rss
            cycle_memory_increase = (cycle_end_memory - initial_memory) / 1024 / 1024  # MB
            
            cycle_memory_data.append({
                "cycle": cycle,
                "memory_increase_mb": cycle_memory_increase,
                "cycle_start_memory": cycle_start_memory,
                "cycle_end_memory": cycle_end_memory
            })
            
            # Small pause between cycles
            time.sleep(1)
            
        # Analyze memory leak patterns
        memory_increases = [data["memory_increase_mb"] for data in cycle_memory_data]
        
        # Check for consistent memory growth (potential leak)
        if len(memory_increases) >= 3:
            # Calculate trend
            first_half_avg = sum(memory_increases[:2]) / 2
            second_half_avg = sum(memory_increases[-2:]) / 2
            growth_rate = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0
            
            # Memory should not grow consistently across cycles
            assert growth_rate < 0.5, f"Memory growth rate {growth_rate:.2%} indicates potential leak"
            
        # Final memory should be reasonable
        final_memory_increase = memory_increases[-1]
        assert final_memory_increase < 300, f"Final memory increase {final_memory_increase:.1f}MB too high"
        
    def test_garbage_collection_effectiveness(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test garbage collection effectiveness during operations."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        process = memory_monitor['process']
        initial_memory = memory_monitor['initial']
        
        # Phase 1: Generate load to increase memory usage
        for i in range(100):
            seo_data = {
                "text": f"GC test iteration {i} with extensive product description and features " * 5,
                "max_length": 300
            }
            
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            assert response.status_code == 200
            
        # Measure memory after load
        before_gc_memory = process.memory_info().rss
        before_gc_increase = (before_gc_memory - initial_memory) / 1024 / 1024  # MB
        
        # Phase 2: Force garbage collection
        gc.collect()
        time.sleep(1)  # Allow time for cleanup
        
        # Measure memory after GC
        after_gc_memory = process.memory_info().rss
        after_gc_increase = (after_gc_memory - initial_memory) / 1024 / 1024  # MB
        
        # Calculate GC effectiveness
        memory_freed = (before_gc_memory - after_gc_memory) / 1024 / 1024  # MB
        gc_effectiveness = memory_freed / before_gc_increase if before_gc_increase > 0 else 0
        
        # Assertions about garbage collection
        assert before_gc_increase > 0, "No memory increase detected during load phase"
        assert memory_freed >= 0, f"Memory increased {-memory_freed:.1f}MB after GC"
        assert after_gc_increase < before_gc_increase * 1.1, "GC had minimal effect on memory usage"
        
        # Memory should not be excessively high even after operations
        assert after_gc_increase < 400, f"Memory after GC {after_gc_increase:.1f}MB still too high"


@pytest.mark.performance
class TestConnectionPoolingPerformance:
    """Test connection pooling performance under concurrent load."""
    
    def test_database_connection_pool_under_load(self, engine):
        """Test database connection pool performance under concurrent load."""
        from sqlmodel import Session, text
        
        num_workers = 15
        operations_per_worker = 30
        results = queue.Queue()
        
        def database_worker(worker_id):
            worker_results = []
            
            for i in range(operations_per_worker):
                start_time = time.time()
                
                try:
                    with Session(engine) as session:
                        # Perform a simple database operation
                        result = session.exec(text("SELECT 1 as test_value")).first()
                        assert result == 1
                        
                        end_time = time.time()
                        
                        worker_results.append({
                            "worker_id": worker_id,
                            "operation_id": i,
                            "response_time": end_time - start_time,
                            "success": True
                        })
                        
                except Exception as e:
                    end_time = time.time()
                    worker_results.append({
                        "worker_id": worker_id,
                        "operation_id": i,
                        "response_time": end_time - start_time,
                        "error": str(e),
                        "success": False
                    })
                    
            results.put(worker_results)
            
        # Execute concurrent database operations
        threads = []
        test_start_time = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=database_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join(timeout=60)
            
        test_end_time = time.time()
        total_test_time = test_end_time - test_start_time
        
        # Collect results
        all_results = []
        while not results.empty():
            worker_results = results.get()
            all_results.extend(worker_results)
            
        # Analyze connection pool performance
        successful_operations = [r for r in all_results if r.get("success", False)]
        success_rate = len(successful_operations) / len(all_results)
        
        response_times = [r["response_time"] for r in successful_operations]
        avg_response_time = sum(response_times) / len(response_times) if response_times else float('inf')
        max_response_time = max(response_times) if response_times else float('inf')
        
        operations_per_second = len(all_results) / total_test_time
        
        # Performance assertions
        assert success_rate >= 0.95, f"DB operation success rate {success_rate:.2%} below 95%"
        assert avg_response_time < 0.1, f"Average DB response time {avg_response_time:.3f}s above 100ms"
        assert max_response_time < 1.0, f"Max DB response time {max_response_time:.3f}s above 1s"
        assert operations_per_second >= 50, f"DB throughput {operations_per_second:.1f} ops/s below 50"
        assert total_test_time < 30, f"DB test took {total_test_time:.1f}s, exceeding 30s"
        
    def test_http_client_connection_reuse(self, client: TestClient):
        """Test HTTP client connection reuse performance."""
        num_requests = 200
        results = []
        
        # Measure performance over many requests to test connection reuse
        start_time = time.time()
        
        for i in range(num_requests):
            request_start = time.time()
            response = client.get("/health")
            request_end = time.time()
            
            results.append({
                "request_id": i,
                "status_code": response.status_code,
                "response_time": request_end - request_start,
                "success": response.status_code == 200
            })
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze connection reuse performance
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results)
        
        response_times = [r["response_time"] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times)
        
        # Check for connection reuse efficiency
        # Later requests should not be significantly slower (indicating good connection reuse)
        first_quarter_times = response_times[:len(response_times)//4]
        last_quarter_times = response_times[-len(response_times)//4:]
        
        first_quarter_avg = sum(first_quarter_times) / len(first_quarter_times)
        last_quarter_avg = sum(last_quarter_times) / len(last_quarter_times)
        
        performance_degradation = (last_quarter_avg - first_quarter_avg) / first_quarter_avg
        
        # Performance assertions
        assert success_rate >= 0.98, f"Success rate {success_rate:.2%} below 98%"
        assert avg_response_time < 0.5, f"Average response time {avg_response_time:.3f}s above 0.5s"
        assert performance_degradation < 0.5, f"Performance degraded {performance_degradation:.2%} over time"
        assert total_time < 60, f"Total test time {total_time:.1f}s exceeding 60s"
        
        # Connection reuse should keep response times consistent
        response_time_std = (sum((t - avg_response_time) ** 2 for t in response_times) / len(response_times)) ** 0.5
        assert response_time_std < avg_response_time, f"High response time variance indicates poor connection reuse"