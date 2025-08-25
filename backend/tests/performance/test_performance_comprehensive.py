"""
Performance tests for critical endpoints and workflows.
This addresses point 4 of the PR #42 checklist: "Testes de performance dos principais endpoints e fluxos"
"""
import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import threading
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.performance
class TestEndpointPerformance:
    """Test performance of critical API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_health_endpoint_performance(self, client):
        """Test health endpoint response time."""
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            # Health endpoint should be fast (< 100ms)
            assert avg_response_time < 100, f"Average response time {avg_response_time:.2f}ms exceeds 100ms"
            assert max_response_time < 200, f"Max response time {max_response_time:.2f}ms exceeds 200ms"
    
    def test_seo_optimization_performance(self, client, auth_headers):
        """Test SEO optimization endpoint performance."""
        seo_data = {
            "text": "High-quality wireless bluetooth headphones with active noise cancellation technology and superior sound quality for music lovers and professionals who demand the best audio experience available in the market today.",
            "keywords": ["wireless", "bluetooth", "headphones", "noise cancellation", "audio"],
            "max_length": 160
        }
        
        response_times = []
        
        for i in range(5):
            start_time = time.time()
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)
            elif response.status_code == 404:
                pytest.skip("SEO optimization endpoint not implemented")
                
        if response_times:
            avg_response_time = statistics.mean(response_times)
            
            # SEO optimization should complete within reasonable time (< 500ms)
            assert avg_response_time < 500, f"SEO optimization too slow: {avg_response_time:.2f}ms"
    
    def test_database_query_performance(self, client, auth_headers):
        """Test database query performance."""
        # Test endpoints that likely involve database queries
        db_endpoints = [
            "/api/user/profile",
            "/api/campaigns/list",
            "/api/products/list",
            "/api/analytics/overview"
        ]
        
        for endpoint in db_endpoints:
            response_times = []
            
            for i in range(3):
                start_time = time.time()
                response = client.get(endpoint, headers=auth_headers)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time) * 1000
                    response_times.append(response_time)
                elif response.status_code == 404:
                    break  # Endpoint not implemented
                    
            if response_times:
                avg_response_time = statistics.mean(response_times)
                
                # Database queries should be reasonably fast (< 1000ms)
                assert avg_response_time < 1000, f"{endpoint} database query too slow: {avg_response_time:.2f}ms"

@pytest.mark.performance
class TestConcurrencyPerformance:
    """Test performance under concurrent load."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_concurrent_health_checks(self, client):
        """Test health endpoint under concurrent load."""
        num_requests = 20
        max_workers = 10
        
        def make_request():
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000
            }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["status_code"] == 200]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            # Under concurrent load, response times should still be reasonable
            assert avg_response_time < 200, f"Concurrent average response time {avg_response_time:.2f}ms too high"
            assert max_response_time < 500, f"Concurrent max response time {max_response_time:.2f}ms too high"
            
            # Success rate should be high
            success_rate = len(successful_requests) / num_requests
            assert success_rate > 0.9, f"Success rate {success_rate:.2%} too low under concurrent load"
    
    def test_concurrent_seo_optimization(self, client, auth_headers):
        """Test SEO optimization under concurrent load."""
        seo_data = {
            "text": f"Product description for performance testing item with unique content",
            "keywords": ["test", "performance", "product"],
            "max_length": 120
        }
        
        num_requests = 10
        max_workers = 5
        
        def make_seo_request(request_id):
            test_data = {**seo_data, "text": f"{seo_data['text']} {request_id}"}
            start_time = time.time()
            response = client.post("/api/seo/optimize", json=test_data, headers=auth_headers)
            end_time = time.time()
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000
            }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_seo_request, i) for i in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["status_code"] == 200]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            
            # SEO optimization under load should still be reasonable
            assert avg_response_time < 1000, f"Concurrent SEO optimization too slow: {avg_response_time:.2f}ms"
            
        elif any(r["status_code"] == 404 for r in results):
            pytest.skip("SEO optimization endpoint not implemented")

@pytest.mark.performance
class TestMemoryPerformance:
    """Test memory usage and memory leaks."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_memory_usage_under_load(self, client, auth_headers):
        """Test memory usage under sustained load."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Make sustained requests
        for i in range(50):
            response = client.get("/health")
            
            # Also test endpoints that might use more memory
            if i % 10 == 0:
                seo_data = {
                    "text": "Large product description " * 100,  # Large text
                    "keywords": ["test"] * 50,  # Many keywords
                    "max_length": 300
                }
                client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Memory increase should be reasonable (< 50MB for this test)
        assert memory_increase_mb < 50, f"Memory increase {memory_increase_mb:.2f}MB too high"
    
    def test_large_payload_handling(self, client, auth_headers):
        """Test handling of large payloads."""
        # Test with large text payload
        large_seo_data = {
            "text": "A" * 10000,  # 10KB text
            "keywords": ["keyword"] * 100,  # Many keywords
            "max_length": 500
        }
        
        start_time = time.time()
        response = client.post("/api/seo/optimize", json=large_seo_data, headers=auth_headers)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000
            
            # Should handle large payloads reasonably fast (< 2 seconds)
            assert response_time < 2000, f"Large payload processing too slow: {response_time:.2f}ms"
            
        elif response.status_code == 413:
            # Payload too large - this is acceptable
            pass
        elif response.status_code == 404:
            pytest.skip("SEO optimization endpoint not implemented")

@pytest.mark.performance
class TestThroughputPerformance:
    """Test system throughput and capacity."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_requests_per_second(self, client):
        """Test requests per second capacity."""
        num_requests = 100
        duration_seconds = 10
        
        start_time = time.time()
        completed_requests = 0
        successful_requests = 0
        
        def make_requests():
            nonlocal completed_requests, successful_requests
            
            while time.time() - start_time < duration_seconds:
                response = client.get("/health")
                completed_requests += 1
                
                if response.status_code == 200:
                    successful_requests += 1
                    
                time.sleep(0.01)  # Small delay to prevent overwhelming
        
        # Run requests in multiple threads
        threads = []
        for i in range(5):  # 5 concurrent threads
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        actual_duration = time.time() - start_time
        requests_per_second = completed_requests / actual_duration
        success_rate = successful_requests / completed_requests if completed_requests > 0 else 0
        
        # Should handle reasonable throughput
        assert requests_per_second > 10, f"Throughput too low: {requests_per_second:.2f} req/sec"
        assert success_rate > 0.95, f"Success rate too low: {success_rate:.2%}"
    
    def test_sustained_load_performance(self, client, auth_headers):
        """Test performance under sustained load."""
        duration_seconds = 30
        request_interval = 0.1  # 10 requests per second
        
        start_time = time.time()
        response_times = []
        error_count = 0
        
        while time.time() - start_time < duration_seconds:
            request_start = time.time()
            response = client.get("/health")
            request_end = time.time()
            
            response_time = (request_end - request_start) * 1000
            response_times.append(response_time)
            
            if response.status_code != 200:
                error_count += 1
            
            # Maintain request interval
            elapsed = time.time() - request_start
            if elapsed < request_interval:
                time.sleep(request_interval - elapsed)
        
        # Analyze sustained performance
        if response_times:
            avg_response_time = statistics.mean(response_times)
            response_time_95th = sorted(response_times)[int(len(response_times) * 0.95)]
            error_rate = error_count / len(response_times)
            
            # Performance should remain stable under sustained load
            assert avg_response_time < 100, f"Sustained load average response time {avg_response_time:.2f}ms too high"
            assert response_time_95th < 200, f"95th percentile response time {response_time_95th:.2f}ms too high"
            assert error_rate < 0.05, f"Error rate {error_rate:.2%} too high under sustained load"

@pytest.mark.performance
class TestSpecializedPerformance:
    """Test performance of specialized operations."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_search_performance(self, client, auth_headers):
        """Test search operation performance."""
        search_queries = [
            "wireless headphones",
            "smartphone samsung",
            "laptop gaming",
            "camera professional",
            "monitor 4k"
        ]
        
        response_times = []
        
        for query in search_queries:
            search_data = {"query": query, "limit": 20}
            
            start_time = time.time()
            response = client.post("/api/search", json=search_data, headers=auth_headers)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)
            elif response.status_code == 404:
                pytest.skip("Search endpoint not implemented")
                
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            # Search should be fast
            assert avg_response_time < 300, f"Search average response time {avg_response_time:.2f}ms too slow"
            assert max_response_time < 500, f"Search max response time {max_response_time:.2f}ms too slow"
    
    def test_report_generation_performance(self, client, auth_headers):
        """Test report generation performance."""
        report_data = {
            "type": "performance_summary",
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            },
            "metrics": ["sales", "traffic", "conversions"],
            "format": "json"
        }
        
        start_time = time.time()
        response = client.post("/api/analytics/reports", json=report_data, headers=auth_headers)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000
            
            # Report generation should complete within reasonable time
            assert response_time < 5000, f"Report generation too slow: {response_time:.2f}ms"
            
            # Check if report contains expected data
            report = response.json()
            assert "data" in report or "results" in report
            
        elif response.status_code == 404:
            pytest.skip("Analytics reports endpoint not implemented")
    
    def test_bulk_operations_performance(self, client, auth_headers):
        """Test bulk operations performance."""
        # Test bulk product updates
        bulk_data = {
            "operations": [
                {"action": "update", "product_id": f"PROD_{i}", "data": {"price": 99.99 + i}}
                for i in range(10)
            ]
        }
        
        start_time = time.time()
        response = client.post("/api/products/bulk", json=bulk_data, headers=auth_headers)
        end_time = time.time()
        
        if response.status_code in [200, 202]:
            response_time = (end_time - start_time) * 1000
            
            # Bulk operations should be efficient
            items_per_second = len(bulk_data["operations"]) / (response_time / 1000)
            assert items_per_second > 5, f"Bulk operations too slow: {items_per_second:.2f} items/sec"
            
        elif response.status_code == 404:
            pytest.skip("Bulk operations endpoint not implemented")

@pytest.mark.benchmark
def test_seo_optimization_benchmark(benchmark):
    """Benchmark SEO optimization function directly."""
    from app.services.seo import optimize_text
    
    text = "High-quality wireless bluetooth headphones with active noise cancellation"
    keywords = ["wireless", "bluetooth", "headphones", "noise cancellation"]
    
    # Benchmark the function
    result = benchmark(optimize_text, text, keywords, 160)
    
    # Verify result is correct
    assert "original" in result
    assert "title" in result
    assert "meta_description" in result
    assert result["original"] == text