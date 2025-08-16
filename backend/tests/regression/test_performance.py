"""
Performance regression tests for monitoring API response times and throughput.
"""
import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


@pytest.mark.regression
class TestPerformanceBaselines:
    """Test performance baselines for critical API endpoints."""
    
    def test_health_endpoint_response_time(self, client: TestClient):
        """Test health endpoint response time baseline."""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Health endpoint should respond within 100ms
        assert response_time < 0.1, f"Health endpoint too slow: {response_time:.3f}s"
    
    def test_authentication_response_time(self, client: TestClient):
        """Test authentication endpoint response time baseline."""
        # Register user first
        user_data = {
            "email": "perf_test_auth@example.com",
            "password": "perf_password_123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Test login performance
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        start_time = time.time()
        response = client.post("/api/auth/token", data=login_data)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Authentication should complete within 1 second
        assert response_time < 1.0, f"Authentication too slow: {response_time:.3f}s"
    
    def test_seo_optimization_response_time(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization endpoint response time baseline."""
        request_data = {
            "text": "Performance test for SEO optimization endpoint with medium length text that requires processing",
            "keywords": ["performance", "test", "seo"],
            "max_length": 160
        }
        
        start_time = time.time()
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # SEO optimization should complete within 2 seconds
        assert response_time < 2.0, f"SEO optimization too slow: {response_time:.3f}s"
    
    def test_categories_list_response_time(self, client: TestClient, auth_headers: dict):
        """Test categories list endpoint response time baseline."""
        start_time = time.time()
        response = client.get("/api/categories/", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Categories list should load within 3 seconds
        assert response_time < 3.0, f"Categories list too slow: {response_time:.3f}s"
    
    def test_category_details_response_time(self, client: TestClient, auth_headers: dict):
        """Test category details endpoint response time baseline."""
        start_time = time.time()
        response = client.get("/api/categories/MLB1132", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Category details should load within 3 seconds
        assert response_time < 3.0, f"Category details too slow: {response_time:.3f}s"


@pytest.mark.regression
class TestThroughputBaselines:
    """Test API throughput and concurrent request handling."""
    
    def test_concurrent_health_checks(self, client: TestClient):
        """Test handling of concurrent health check requests."""
        num_requests = 10
        start_time = time.time()
        
        responses = []
        for _ in range(num_requests):
            response = client.get("/health")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should handle 10 concurrent requests within 1 second
        assert total_time < 1.0, f"Concurrent health checks too slow: {total_time:.3f}s"
        
        # Calculate requests per second
        rps = num_requests / total_time
        assert rps > 10, f"Health endpoint RPS too low: {rps:.1f}"
    
    def test_concurrent_seo_optimizations(self, client: TestClient, auth_headers: dict):
        """Test handling of concurrent SEO optimization requests."""
        request_data = {
            "text": "Concurrent test text for SEO optimization",
            "max_length": 160
        }
        
        num_requests = 5
        start_time = time.time()
        
        responses = []
        for i in range(num_requests):
            # Vary the text slightly for each request
            data = request_data.copy()
            data["text"] = f"{request_data['text']} request {i}"
            
            response = client.post("/api/seo/optimize", json=data, headers=auth_headers)
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should handle 5 SEO requests within 10 seconds
        assert total_time < 10.0, f"Concurrent SEO optimization too slow: {total_time:.3f}s"
    
    def test_authentication_throughput(self, client: TestClient):
        """Test authentication endpoint throughput."""
        # Register multiple users for testing
        users = []
        for i in range(3):
            user_data = {
                "email": f"throughput_user_{i}@example.com",
                "password": f"password_{i}_123"
            }
            client.post("/api/auth/register", json=user_data)
            users.append(user_data)
        
        # Test concurrent logins
        start_time = time.time()
        
        responses = []
        for user in users:
            login_data = {
                "username": user["email"],
                "password": user["password"]
            }
            response = client.post("/api/auth/token", data=login_data)
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All logins should succeed
        for response in responses:
            assert response.status_code == 200
            assert "access_token" in response.json()
        
        # Should handle 3 logins within 3 seconds
        assert total_time < 3.0, f"Authentication throughput too slow: {total_time:.3f}s"


@pytest.mark.regression
class TestMemoryUsageBaselines:
    """Test memory usage patterns for regression detection."""
    
    def test_large_text_seo_optimization(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with large text input."""
        # Create large text (10KB)
        large_text = "Large text content for memory testing. " * 250
        
        request_data = {
            "text": large_text,
            "keywords": ["large", "text", "memory", "test"],
            "max_length": 160
        }
        
        start_time = time.time()
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should handle large text within reasonable time
        assert response_time < 5.0, f"Large text SEO optimization too slow: {response_time:.3f}s"
        
        # Verify response structure is still correct
        data = response.json()
        assert "optimized_text" in data
        optimized = data["optimized_text"]
        assert len(optimized["meta_description"]) <= 160
    
    def test_multiple_keyword_processing(self, client: TestClient, auth_headers: dict):
        """Test processing with many keywords."""
        # Create request with many keywords
        many_keywords = [f"keyword_{i}" for i in range(50)]
        
        request_data = {
            "text": "Testing SEO optimization with many keywords to ensure memory efficiency",
            "keywords": many_keywords,
            "max_length": 160
        }
        
        start_time = time.time()
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should handle many keywords efficiently
        assert response_time < 3.0, f"Many keywords processing too slow: {response_time:.3f}s"
    
    def test_sequential_requests_memory_stability(self, client: TestClient, auth_headers: dict):
        """Test memory stability across sequential requests."""
        request_data = {
            "text": "Sequential request testing for memory stability and leak detection",
            "keywords": ["sequential", "memory", "stability"],
            "max_length": 160
        }
        
        response_times = []
        
        # Make 10 sequential requests
        for i in range(10):
            start_time = time.time()
            response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Response times should remain stable (no significant increase)
        # indicating no memory leaks
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Maximum response time should not be more than 3x average
        assert max_time < avg_time * 3, f"Response time degradation detected: avg={avg_time:.3f}s, max={max_time:.3f}s"
        
        # All response times should be reasonable
        for rt in response_times:
            assert rt < 5.0, f"Individual request too slow: {rt:.3f}s"


@pytest.mark.regression
class TestDatabasePerformanceBaselines:
    """Test database operation performance baselines."""
    
    def test_user_registration_performance(self, client: TestClient):
        """Test user registration database performance."""
        user_data = {
            "email": "db_perf_test@example.com",
            "password": "db_perf_password_123"
        }
        
        start_time = time.time()
        response = client.post("/api/auth/register", json=user_data)
        end_time = time.time()
        
        assert response.status_code == 201
        response_time = end_time - start_time
        
        # User registration should complete quickly
        assert response_time < 2.0, f"User registration too slow: {response_time:.3f}s"
    
    def test_endpoint_crud_performance(self, client: TestClient, auth_headers: dict):
        """Test API endpoint CRUD operations performance."""
        endpoint_data = {
            "name": "Performance Test API",
            "url": "https://api.performance-test.com",
            "auth_type": "oauth"
        }
        
        # Test CREATE performance
        start_time = time.time()
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        create_time = time.time() - start_time
        
        assert create_response.status_code == 201
        assert create_time < 1.0, f"Endpoint creation too slow: {create_time:.3f}s"
        
        endpoint_id = create_response.json()["id"]
        
        # Test READ performance
        start_time = time.time()
        get_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        read_time = time.time() - start_time
        
        assert get_response.status_code == 200
        assert read_time < 0.5, f"Endpoint read too slow: {read_time:.3f}s"
        
        # Test UPDATE performance
        update_data = {"name": "Updated Performance Test API"}
        start_time = time.time()
        update_response = client.put(f"/api/endpoints/{endpoint_id}", json=update_data, headers=auth_headers)
        update_time = time.time() - start_time
        
        assert update_response.status_code == 200
        assert update_time < 1.0, f"Endpoint update too slow: {update_time:.3f}s"
        
        # Test DELETE performance
        start_time = time.time()
        delete_response = client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        delete_time = time.time() - start_time
        
        assert delete_response.status_code == 200
        assert delete_time < 1.0, f"Endpoint deletion too slow: {delete_time:.3f}s"
    
    def test_bulk_operations_performance(self, client: TestClient, auth_headers: dict):
        """Test performance of bulk database operations."""
        # Create multiple endpoints
        endpoints = []
        create_start = time.time()
        
        for i in range(5):
            endpoint_data = {
                "name": f"Bulk Test API {i}",
                "url": f"https://api.bulk-test-{i}.com",
                "auth_type": "oauth"
            }
            
            response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
            assert response.status_code == 201
            endpoints.append(response.json()["id"])
        
        create_time = time.time() - create_start
        
        # Should create 5 endpoints within 5 seconds
        assert create_time < 5.0, f"Bulk endpoint creation too slow: {create_time:.3f}s"
        
        # List all endpoints
        list_start = time.time()
        list_response = client.get("/api/endpoints/", headers=auth_headers)
        list_time = time.time() - list_start
        
        assert list_response.status_code == 200
        assert list_time < 1.0, f"Endpoint listing too slow: {list_time:.3f}s"
        
        # Clean up
        delete_start = time.time()
        for endpoint_id in endpoints:
            delete_response = client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
            assert delete_response.status_code == 200
        
        delete_time = time.time() - delete_start
        
        # Should delete 5 endpoints within 5 seconds
        assert delete_time < 5.0, f"Bulk endpoint deletion too slow: {delete_time:.3f}s"


@pytest.mark.regression
class TestResourceUtilizationBaselines:
    """Test resource utilization patterns for regression detection."""
    
    def test_oauth_flow_performance(self, client: TestClient, auth_headers: dict):
        """Test OAuth flow performance baseline."""
        start_time = time.time()
        
        # Initiate OAuth login
        oauth_response = client.get("/api/oauth/login", headers=auth_headers, follow_redirects=False)
        
        oauth_time = time.time() - start_time
        
        assert oauth_response.status_code == 307
        assert oauth_time < 1.0, f"OAuth initiation too slow: {oauth_time:.3f}s"
        
        # Extract state from redirect URL
        redirect_url = oauth_response.headers["location"]
        assert "auth.mercadolibre.com.br" in redirect_url
        assert "state=" in redirect_url
        assert "code_challenge=" in redirect_url
    
    def test_error_handling_performance(self, client: TestClient, auth_headers: dict):
        """Test that error responses are still fast."""
        error_tests = [
            # 404 errors
            ("/api/nonexistent/endpoint", "GET", None),
            # 422 validation errors
            ("/api/seo/optimize", "POST", {"invalid": "data"}),
            # 401 unauthorized (without headers)
            ("/api/categories/", "GET", None),
        ]
        
        for endpoint, method, data in error_tests:
            start_time = time.time()
            
            if method == "GET":
                if endpoint == "/api/categories/":
                    # Test without auth headers for 401
                    response = client.get(endpoint)
                else:
                    response = client.get(endpoint, headers=auth_headers)
            elif method == "POST":
                response = client.post(endpoint, json=data, headers=auth_headers)
            
            error_time = time.time() - start_time
            
            # Error responses should still be fast
            assert error_time < 1.0, f"Error response too slow for {endpoint}: {error_time:.3f}s"
            
            # Should return appropriate error status
            assert response.status_code >= 400
    
    def test_concurrent_different_endpoints(self, client: TestClient, auth_headers: dict):
        """Test concurrent access to different endpoints."""
        start_time = time.time()
        
        responses = []
        
        # Make concurrent requests to different endpoints
        endpoints = [
            ("/health", "GET", None),
            ("/api/categories/", "GET", None),
            ("/api/seo/optimize", "POST", {"text": "Concurrent test text"}),
        ]
        
        for endpoint, method, data in endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers if endpoint != "/health" else None)
            elif method == "POST":
                response = client.post(endpoint, json=data, headers=auth_headers)
            
            responses.append(response)
        
        total_time = time.time() - start_time
        
        # All responses should succeed
        expected_status = [200, 200, 200]
        for i, response in enumerate(responses):
            assert response.status_code == expected_status[i]
        
        # Should handle all requests within reasonable time
        assert total_time < 5.0, f"Concurrent different endpoints too slow: {total_time:.3f}s"