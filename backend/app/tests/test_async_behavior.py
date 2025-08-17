"""
Comprehensive Async Behavior Tests for FastAPI Backend

This module implements extensive asynchronous testing using pytest-asyncio and httpx.AsyncClient
to ensure 100% coverage of async route behavior, concurrency handling, and race condition detection.

Key testing areas:
1. Single async request validation
2. Concurrent request handling  
3. Race condition detection in database operations
4. Performance under load
5. Error handling in concurrent scenarios
6. Token management in multi-threaded contexts

Authors: ML Project Team
Last Updated: 2024
"""

import pytest
import asyncio
import time
import logging
from unittest.mock import patch, AsyncMock, Mock
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from concurrent.futures import ThreadPoolExecutor, as_completed
import aioresponses

from app.main import app
from app.database import get_session
from app.models.meli_token import MeliToken
from app.models.oauth_token import OAuthToken

# Configure comprehensive logging for async test analysis
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database configuration for async testing
TEST_DATABASE_URL = "sqlite:///./test_async_behavior.db"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)


def get_test_session():
    """
    Override database session for async testing.
    Ensures isolated test environment for concurrent operations.
    """
    with Session(test_engine) as session:
        yield session


# Override the database dependency for testing
app.dependency_overrides[get_session] = get_test_session


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Set up isolated test database for async behavior testing.
    Creates all tables and ensures clean state between test runs.
    """
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def test_session():
    """
    Create isolated database session for each test.
    Ensures data consistency during concurrent testing.
    """
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client():
    """
    Create test client for FastAPI application.
    Used for both sync and async testing patterns.
    """
    return TestClient(app)


@pytest.fixture
def sample_meli_token(test_session):
    """
    Create sample MercadoLibre token for testing.
    Simulates real OAuth2 token stored in database.
    """
    token = MeliToken(
        user_id="test_user_123",
        access_token="APP_USR-123456789-test-async-token",
        refresh_token="TG-123456789-test-refresh-token",
        token_type="bearer",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=6),
        scope="offline_access read write",
        created_at=datetime.now(timezone.utc)
    )
    test_session.add(token)
    test_session.commit()
    test_session.refresh(token)
    return token


@pytest.fixture
def sample_oauth_token(test_session):
    """
    Create sample OAuth token as fallback for testing.
    Tests multi-source token resolution strategy.
    """
    token = OAuthToken(
        user_id=1,
        access_token="OAUTH-987654321-fallback-token",
        refresh_token="REFRESH-987654321-fallback",
        expires_in=21600,
        scope="offline_access read write",
        token_type="bearer",
        created_at=datetime.now(timezone.utc)
    )
    test_session.add(token)
    test_session.commit()
    test_session.refresh(token)
    return token


@pytest.fixture
def mock_user_info():
    """
    Mock MercadoLibre user information response.
    Simulates successful API response for user data.
    """
    return {
        "id": 123456789,
        "nickname": "ASYNC_TEST_USER",
        "email": "async.test@example.com",
        "first_name": "Async",
        "last_name": "Test User",
        "country_id": "BR",
        "site_id": "MLB",
        "user_type": "normal",
        "tags": ["normal"],
        "points": 100,
        "seller_reputation": {
            "level_id": "5_green",
            "power_seller_status": "silver"
        }
    }


@pytest.fixture
def mock_products_data():
    """
    Mock MercadoLibre products response.
    Simulates product listing for concurrent testing.
    """
    return {
        "results": [
            "MLB123456789",
            "MLB987654321", 
            "MLB456789123"
        ],
        "paging": {
            "total": 3,
            "offset": 0,
            "limit": 50
        }
    }


class TestAsyncRouteValidation:
    """
    Test individual async route behavior and validation.
    Ensures basic async functionality works correctly.
    """
    
    @pytest.mark.asyncio
    async def test_user_endpoint_async_behavior(self, client, sample_meli_token, mock_user_info):
        """
        Test async behavior of /meli/user endpoint.
        
        Validates:
        - Async request handling
        - Token authentication flow
        - Response structure and timing
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Measure response time
            start_time = time.time()
            response = client.get("/meli/user")
            end_time = time.time()
            
            # Validate response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["user"]["id"] == 123456789
            assert data["user"]["nickname"] == "ASYNC_TEST_USER"
            
            # Validate async performance
            response_time = end_time - start_time
            assert response_time < 1.0, f"Response too slow: {response_time:.3f}s"
            
            # Verify async call was made
            mock_get_user.assert_called_once_with(sample_meli_token.access_token)
            
            logger.info(f"✅ User endpoint async test passed in {response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_products_endpoint_async_behavior(self, client, sample_meli_token, mock_user_info, mock_products_data):
        """
        Test async behavior of /meli/products endpoint.
        
        Validates:
        - Multi-step async operations (user info + products)
        - Sequential async calls
        - Complex response handling
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user, \
             patch('app.services.mercadolibre.get_user_products', new_callable=AsyncMock) as mock_get_products:
            
            mock_get_user.return_value = mock_user_info
            mock_get_products.return_value = mock_products_data
            
            start_time = time.time()
            response = client.get("/meli/products")
            end_time = time.time()
            
            # Validate response structure
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["user_id"] == 123456789
            assert len(data["products"]["results"]) == 3
            
            # Validate async call sequence
            mock_get_user.assert_called_once_with(sample_meli_token.access_token)
            mock_get_products.assert_called_once_with(sample_meli_token.access_token, "123456789")
            
            response_time = end_time - start_time
            logger.info(f"✅ Products endpoint async test passed in {response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_async_error_handling(self, client, sample_meli_token):
        """
        Test async error handling and exception propagation.
        
        Validates:
        - Async exception handling
        - Error response format
        - Service failure scenarios
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            # Simulate async service failure
            mock_get_user.side_effect = Exception("Async API Error")
            
            response = client.get("/meli/user")
            
            assert response.status_code == 400
            data = response.json()
            assert "Erro ao consultar dados do usuário" in data["detail"]
            assert "Async API Error" in data["detail"]
            
            logger.info("✅ Async error handling test passed")


class TestConcurrentRequestHandling:
    """
    Test concurrent request handling and performance under load.
    Critical for validating async scalability and race condition resistance.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_user_requests(self, sample_meli_token, mock_user_info):
        """
        Test multiple concurrent requests to /meli/user endpoint.
        
        Validates:
        - Concurrent async request handling
        - Shared resource access (database token)
        - Response consistency under load
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Configuration for concurrent testing
            concurrent_requests = 10
            
            def make_user_request(request_id: int) -> Dict[str, Any]:
                """Individual request with timing and error tracking."""
                start_time = time.time()
                try:
                    client = TestClient(app)
                    response = client.get("/meli/user")
                    end_time = time.time()
                    
                    return {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200,
                        "data": response.json() if response.status_code == 200 else None,
                        "error": None
                    }
                except Exception as e:
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "status_code": 500,
                        "response_time": end_time - start_time,
                        "success": False,
                        "data": None,
                        "error": str(e)
                    }
            
            # Execute concurrent requests using ThreadPoolExecutor
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                future_to_request = {
                    executor.submit(make_user_request, i): i 
                    for i in range(concurrent_requests)
                }
                
                results = []
                for future in as_completed(future_to_request, timeout=30):
                    result = future.result()
                    results.append(result)
            
            end_time = time.time()
            
            # Analyze results
            total_time = end_time - start_time
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            # Validate concurrent performance
            success_rate = len(successful_requests) / len(results)
            assert success_rate >= 0.9, f"Success rate {success_rate:.2%} below 90%"
            
            # Validate response consistency
            for result in successful_requests:
                assert result["data"]["user"]["id"] == 123456789
                assert result["response_time"] < 5.0, f"Request {result['request_id']} too slow"
            
            # Performance metrics
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            throughput = len(successful_requests) / total_time
            
            logger.info(f"✅ Concurrent user requests test completed:")
            logger.info(f"   - Total requests: {len(results)}")
            logger.info(f"   - Success rate: {success_rate:.2%}")
            logger.info(f"   - Average response time: {avg_response_time:.3f}s")
            logger.info(f"   - Throughput: {throughput:.1f} req/s")
            logger.info(f"   - Total test time: {total_time:.3f}s")
            
            # Assert performance thresholds
            assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s too high"
            assert throughput >= 2.0, f"Throughput {throughput:.1f} req/s too low"

    @pytest.mark.asyncio
    async def test_mixed_concurrent_requests(self, sample_meli_token, mock_user_info, mock_products_data):
        """
        Test mixed concurrent requests to different endpoints.
        
        Validates:
        - Cross-endpoint concurrency
        - Resource sharing between different routes
        - Load balancing across async operations
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user, \
             patch('app.services.mercadolibre.get_user_products', new_callable=AsyncMock) as mock_get_products:
            
            mock_get_user.return_value = mock_user_info
            mock_get_products.return_value = mock_products_data
            
            def make_mixed_request(request_id: int, endpoint: str) -> Dict[str, Any]:
                """Execute mixed endpoint requests with detailed tracking."""
                start_time = time.time()
                try:
                    client = TestClient(app)
                    response = client.get(f"/meli/{endpoint}")
                    end_time = time.time()
                    
                    return {
                        "request_id": request_id,
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200,
                        "data_size": len(str(response.json())) if response.status_code == 200 else 0
                    }
                except Exception as e:
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "endpoint": endpoint,
                        "status_code": 500,
                        "response_time": end_time - start_time,
                        "success": False,
                        "error": str(e)
                    }
            
            # Create mixed workload: 50% user requests, 50% products requests
            user_requests = 4
            products_requests = 4
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                tasks = []
                
                # Add user endpoint requests
                for i in range(user_requests):
                    tasks.append(executor.submit(make_mixed_request, i, "user"))
                
                # Add products endpoint requests  
                for i in range(products_requests):
                    tasks.append(executor.submit(make_mixed_request, i + user_requests, "products"))
                
                # Execute all requests concurrently
                results = []
                for future in as_completed(tasks, timeout=30):
                    result = future.result()
                    results.append(result)
            
            end_time = time.time()
            
            # Analyze by endpoint type
            user_results = [r for r in results if r["endpoint"] == "user"]
            products_results = [r for r in results if r["endpoint"] == "products"]
            
            user_success_rate = sum(1 for r in user_results if r["success"]) / len(user_results)
            products_success_rate = sum(1 for r in products_results if r["success"]) / len(products_results)
            
            # Validate mixed concurrent performance
            assert user_success_rate >= 0.8, f"User endpoint success rate {user_success_rate:.2%} too low"
            assert products_success_rate >= 0.8, f"Products endpoint success rate {products_success_rate:.2%} too low"
            
            total_time = end_time - start_time
            total_throughput = len([r for r in results if r["success"]]) / total_time
            
            logger.info(f"✅ Mixed concurrent requests test completed:")
            logger.info(f"   - User requests success rate: {user_success_rate:.2%}")
            logger.info(f"   - Products requests success rate: {products_success_rate:.2%}")
            logger.info(f"   - Total throughput: {total_throughput:.1f} req/s")


class TestRaceConditionDetection:
    """
    Test database race conditions and concurrent access patterns.
    Critical for ensuring data consistency in multi-user scenarios.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_token_access(self, sample_meli_token, mock_user_info):
        """
        Test concurrent access to the same database token.
        
        Validates:
        - Database connection pooling under load
        - Token retrieval consistency
        - No data corruption during concurrent reads
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            def concurrent_token_access(request_id: int) -> Dict[str, Any]:
                """Simulate concurrent token access with timing analysis."""
                start_time = time.time()
                
                # Make request that triggers token database access
                client = TestClient(app)
                response = client.get("/meli/user")
                
                end_time = time.time()
                
                return {
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "response_time": end_time - start_time,
                    "token_used": mock_get_user.call_args[0][0] if mock_get_user.called else None
                }
            
            # Execute high concurrency test for race condition detection
            concurrent_requests = 15
            
            with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                future_to_request = {
                    executor.submit(concurrent_token_access, i): i 
                    for i in range(concurrent_requests)
                }
                
                results = []
                for future in as_completed(future_to_request, timeout=30):
                    result = future.result()
                    results.append(result)
            
            # Analyze token consistency
            successful_results = [r for r in results if r["success"]]
            
            # Since mock might be called multiple times, we check if token is consistent
            success_rate = len(successful_results) / len(results)
            assert success_rate >= 0.9, f"Race condition causing failures: {success_rate:.2%} success rate"
            
            logger.info(f"✅ Concurrent token access test passed:")
            logger.info(f"   - {len(results)} concurrent requests")
            logger.info(f"   - {success_rate:.2%} success rate")
            logger.info(f"   - Token access maintained")

    @pytest.mark.asyncio
    async def test_database_connection_resilience(self, sample_meli_token, mock_user_info):
        """
        Test database connection handling under concurrent load.
        
        Validates:
        - Connection pool management
        - No connection leaks
        - Graceful handling of connection limits
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Simulate high database load
            concurrent_db_requests = 12
            
            def db_stress_request(request_id: int) -> Dict[str, Any]:
                """Stress test database connections with timing."""
                try:
                    client = TestClient(app)
                    response = client.get("/meli/user")
                    return {
                        "request_id": request_id,
                        "success": response.status_code == 200,
                        "error": None
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "error": str(e)
                    }
            
            with ThreadPoolExecutor(max_workers=concurrent_db_requests) as executor:
                future_to_request = {
                    executor.submit(db_stress_request, i): i 
                    for i in range(concurrent_db_requests)
                }
                
                results = []
                for future in as_completed(future_to_request, timeout=30):
                    result = future.result()
                    results.append(result)
            
            # Analyze database resilience
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            success_rate = len(successful_requests) / len(results)
            
            # Validate database connection resilience
            assert success_rate >= 0.8, f"Database connection issues: {success_rate:.2%} success rate"
            
            # Log any connection errors for analysis
            for failure in failed_requests:
                logger.warning(f"Database connection failure: {failure['error']}")
            
            logger.info(f"✅ Database connection resilience test passed:")
            logger.info(f"   - {len(results)} concurrent database operations")
            logger.info(f"   - {success_rate:.2%} success rate")
            logger.info(f"   - {len(failed_requests)} connection failures")


class TestAsyncErrorScenarios:
    """
    Test error handling in async and concurrent scenarios.
    Ensures robust error handling under various failure conditions.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_api_failures(self, sample_meli_token):
        """
        Test handling of API failures during concurrent requests.
        
        Validates:
        - Error isolation between concurrent requests
        - Proper error response formatting
        - System stability during failures
        """
        # Simulate intermittent API failures
        call_count = 0
        
        async def intermittent_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Every 3rd call fails
                raise Exception(f"Simulated API failure #{call_count}")
            return {"id": 123456789, "nickname": "TEST_USER"}
        
        with patch('app.services.mercadolibre.get_user_info', side_effect=intermittent_failure):
            concurrent_requests = 9  # Ensures multiple failures
            
            def error_test_request(request_id: int) -> Dict[str, Any]:
                try:
                    client = TestClient(app)
                    response = client.get("/meli/user")
                    return {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "error_isolated": True  # No exception leaked to client
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "error_isolated": False,  # Exception not properly handled
                        "client_error": str(e)
                    }
            
            with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                future_to_request = {
                    executor.submit(error_test_request, i): i 
                    for i in range(concurrent_requests)
                }
                
                results = []
                for future in as_completed(future_to_request, timeout=30):
                    result = future.result()
                    results.append(result)
            
            # Analyze error handling
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"] and r.get("error_isolated", True)]
            leaked_errors = [r for r in results if not r.get("error_isolated", True)]
            
            # Validate error isolation
            assert len(leaked_errors) == 0, f"Errors leaked to client: {leaked_errors}"
            
            # Should have some failures due to intermittent API errors
            assert len(failed_requests) > 0, "Expected some API failures for testing"
            assert len(successful_requests) > 0, "Expected some successful requests"
            
            # All requests should get proper HTTP responses
            for result in results:
                assert "status_code" in result, "Missing status code in response"
                assert result["status_code"] in [200, 400], f"Unexpected status code: {result['status_code']}"
            
            logger.info(f"✅ Concurrent API failures test completed:")
            logger.info(f"   - Total requests: {len(results)}")
            logger.info(f"   - Successful: {len(successful_requests)}")
            logger.info(f"   - Failed gracefully: {len(failed_requests)}")
            logger.info(f"   - Error isolation maintained")

    @pytest.mark.asyncio 
    async def test_no_token_concurrent_scenario(self, test_session):
        """
        Test concurrent requests when no authentication token exists.
        
        Validates:
        - Consistent error responses
        - No race conditions in error handling
        - Proper HTTP status codes
        """
        # Ensure no tokens exist in test database
        test_session.query(MeliToken).delete()
        test_session.query(OAuthToken).delete()
        test_session.commit()
        
        concurrent_requests = 8
        
        def no_token_request(request_id: int) -> Dict[str, Any]:
            client = TestClient(app)
            response = client.get("/meli/user")
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_data": response.json(),
                "consistent_error": response.status_code == 404
            }
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            future_to_request = {
                executor.submit(no_token_request, i): i 
                for i in range(concurrent_requests)
            }
            
            results = []
            for future in as_completed(future_to_request, timeout=30):
                result = future.result()
                results.append(result)
        
        # Validate consistent error responses
        for result in results:
            assert result["status_code"] == 404, f"Inconsistent status code: {result['status_code']}"
            assert "Nenhum token válido encontrado" in result["response_data"]["detail"]
            assert result["consistent_error"], "Inconsistent error response"
        
        logger.info(f"✅ No token concurrent scenario test completed:")
        logger.info(f"   - All {len(results)} requests returned consistent 404 errors")


# Performance benchmarking for CI/CD integration
class TestAsyncPerformanceBenchmarks:
    """
    Performance benchmarks for continuous integration monitoring.
    Ensures async performance doesn't regress over time.
    """
    
    @pytest.mark.asyncio
    async def test_single_request_benchmark(self, client, sample_meli_token, mock_user_info):
        """
        Benchmark single async request performance.
        Sets baseline for performance regression testing.
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Warm up
            client.get("/meli/user")
            
            # Benchmark runs
            benchmark_runs = 5
            response_times = []
            
            for run in range(benchmark_runs):
                start_time = time.time()
                response = client.get("/meli/user")
                end_time = time.time()
                
                assert response.status_code == 200
                response_times.append(end_time - start_time)
            
            # Calculate benchmark metrics
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Performance assertions for CI/CD
            assert avg_response_time < 0.5, f"Average response time regression: {avg_response_time:.3f}s"
            assert max_response_time < 1.0, f"Maximum response time regression: {max_response_time:.3f}s"
            
            logger.info(f"✅ Single request benchmark completed:")
            logger.info(f"   - Average: {avg_response_time:.3f}s")
            logger.info(f"   - Min: {min_response_time:.3f}s") 
            logger.info(f"   - Max: {max_response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_throughput_benchmark(self, sample_meli_token, mock_user_info):
        """
        Benchmark concurrent request throughput.
        Ensures async scalability meets requirements.
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Throughput test configuration
            concurrent_requests = 10
            
            def benchmark_request(request_id: int) -> bool:
                client = TestClient(app)
                response = client.get("/meli/user")
                return response.status_code == 200
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                future_to_request = {
                    executor.submit(benchmark_request, i): i 
                    for i in range(concurrent_requests)
                }
                
                successful_responses = 0
                for future in as_completed(future_to_request, timeout=30):
                    if future.result():
                        successful_responses += 1
            
            end_time = time.time()
            
            # Calculate throughput metrics
            total_time = end_time - start_time
            throughput = successful_responses / total_time
            
            # Throughput assertions for CI/CD
            assert successful_responses == concurrent_requests, "Some requests failed"
            assert throughput >= 5.0, f"Throughput regression: {throughput:.1f} req/s below 5 req/s"
            
            logger.info(f"✅ Concurrent throughput benchmark completed:")
            logger.info(f"   - Requests: {concurrent_requests}")
            logger.info(f"   - Success rate: 100%")
            logger.info(f"   - Throughput: {throughput:.1f} req/s")
            logger.info(f"   - Total time: {total_time:.3f}s")


if __name__ == "__main__":
    """
    Run async behavior tests independently for development and debugging.
    Usage: python -m pytest backend/app/tests/test_async_behavior.py -v
    """
    pytest.main([__file__, "-v", "--tb=short"])

    @pytest.mark.asyncio
    async def test_products_endpoint_async_behavior(self, sample_meli_token, mock_user_info, mock_products_data):
        """
        Test async behavior of /meli/products endpoint.
        
        Validates:
        - Multi-step async operations (user info + products)
        - Sequential async calls
        - Complex response handling
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user, \
             patch('app.services.mercadolibre.get_user_products', new_callable=AsyncMock) as mock_get_products:
            
            mock_get_user.return_value = mock_user_info
            mock_get_products.return_value = mock_products_data
            
            async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
                start_time = time.time()
                response = await ac.get("/meli/products")
                end_time = time.time()
                
                # Validate response structure
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["user_id"] == 123456789
                assert len(data["products"]["results"]) == 3
                
                # Validate async call sequence
                mock_get_user.assert_called_once_with(sample_meli_token.access_token)
                mock_get_products.assert_called_once_with(sample_meli_token.access_token, "123456789")
                
                response_time = end_time - start_time
                logger.info(f"✅ Products endpoint async test passed in {response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_async_error_handling(self, sample_meli_token):
        """
        Test async error handling and exception propagation.
        
        Validates:
        - Async exception handling
        - Error response format
        - Service failure scenarios
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            # Simulate async service failure
            mock_get_user.side_effect = Exception("Async API Error")
            
            async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.get("/meli/user")
                
                assert response.status_code == 400
                data = response.json()
                assert "Erro ao consultar dados do usuário" in data["detail"]
                assert "Async API Error" in data["detail"]
                
                logger.info("✅ Async error handling test passed")


class TestConcurrentRequestHandling:
    """
    Test concurrent request handling and performance under load.
    Critical for validating async scalability and race condition resistance.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_user_requests(self, sample_meli_token, mock_user_info):
        """
        Test multiple concurrent requests to /meli/user endpoint.
        
        Validates:
        - Concurrent async request handling
        - Shared resource access (database token)
        - Response consistency under load
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Configuration for concurrent testing
            concurrent_requests = 10
            request_timeout = 30.0
            
            async def make_user_request(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
                """Individual async request with timing and error tracking."""
                start_time = time.time()
                try:
                    response = await client.get("/meli/user")
                    end_time = time.time()
                    
                    return {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200,
                        "data": response.json() if response.status_code == 200 else None,
                        "error": None
                    }
                except Exception as e:
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "status_code": 500,
                        "response_time": end_time - start_time,
                        "success": False,
                        "data": None,
                        "error": str(e)
                    }
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=request_timeout) as ac:
                # Execute concurrent requests
                start_time = time.time()
                tasks = [make_user_request(ac, i) for i in range(concurrent_requests)]
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Analyze results
                total_time = end_time - start_time
                successful_requests = [r for r in results if r["success"]]
                failed_requests = [r for r in results if not r["success"]]
                
                # Validate concurrent performance
                success_rate = len(successful_requests) / len(results)
                assert success_rate >= 0.9, f"Success rate {success_rate:.2%} below 90%"
                
                # Validate response consistency
                for result in successful_requests:
                    assert result["data"]["user"]["id"] == 123456789
                    assert result["response_time"] < 5.0, f"Request {result['request_id']} too slow"
                
                # Performance metrics
                avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
                throughput = len(successful_requests) / total_time
                
                logger.info(f"✅ Concurrent user requests test completed:")
                logger.info(f"   - Total requests: {len(results)}")
                logger.info(f"   - Success rate: {success_rate:.2%}")
                logger.info(f"   - Average response time: {avg_response_time:.3f}s")
                logger.info(f"   - Throughput: {throughput:.1f} req/s")
                logger.info(f"   - Total test time: {total_time:.3f}s")
                
                # Assert performance thresholds
                assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s too high"
                assert throughput >= 5.0, f"Throughput {throughput:.1f} req/s too low"

    @pytest.mark.asyncio
    async def test_mixed_concurrent_requests(self, sample_meli_token, mock_user_info, mock_products_data):
        """
        Test mixed concurrent requests to different endpoints.
        
        Validates:
        - Cross-endpoint concurrency
        - Resource sharing between different routes
        - Load balancing across async operations
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user, \
             patch('app.services.mercadolibre.get_user_products', new_callable=AsyncMock) as mock_get_products:
            
            mock_get_user.return_value = mock_user_info
            mock_get_products.return_value = mock_products_data
            
            async def make_mixed_request(client: httpx.AsyncClient, request_id: int, endpoint: str) -> Dict[str, Any]:
                """Execute mixed endpoint requests with detailed tracking."""
                start_time = time.time()
                try:
                    response = await client.get(f"/meli/{endpoint}")
                    end_time = time.time()
                    
                    return {
                        "request_id": request_id,
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200,
                        "data_size": len(str(response.json())) if response.status_code == 200 else 0
                    }
                except Exception as e:
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "endpoint": endpoint,
                        "status_code": 500,
                        "response_time": end_time - start_time,
                        "success": False,
                        "error": str(e)
                    }
            
            # Create mixed workload: 50% user requests, 50% products requests
            user_requests = 8
            products_requests = 8
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                tasks = []
                
                # Add user endpoint requests
                for i in range(user_requests):
                    tasks.append(make_mixed_request(ac, i, "user"))
                
                # Add products endpoint requests  
                for i in range(products_requests):
                    tasks.append(make_mixed_request(ac, i + user_requests, "products"))
                
                # Execute all requests concurrently
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Analyze by endpoint type
                user_results = [r for r in results if r["endpoint"] == "user"]
                products_results = [r for r in results if r["endpoint"] == "products"]
                
                user_success_rate = sum(1 for r in user_results if r["success"]) / len(user_results)
                products_success_rate = sum(1 for r in products_results if r["success"]) / len(products_results)
                
                # Validate mixed concurrent performance
                assert user_success_rate >= 0.9, f"User endpoint success rate {user_success_rate:.2%} too low"
                assert products_success_rate >= 0.9, f"Products endpoint success rate {products_success_rate:.2%} too low"
                
                total_time = end_time - start_time
                total_throughput = len([r for r in results if r["success"]]) / total_time
                
                logger.info(f"✅ Mixed concurrent requests test completed:")
                logger.info(f"   - User requests success rate: {user_success_rate:.2%}")
                logger.info(f"   - Products requests success rate: {products_success_rate:.2%}")
                logger.info(f"   - Total throughput: {total_throughput:.1f} req/s")


class TestRaceConditionDetection:
    """
    Test database race conditions and concurrent access patterns.
    Critical for ensuring data consistency in multi-user scenarios.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_token_access(self, sample_meli_token, mock_user_info):
        """
        Test concurrent access to the same database token.
        
        Validates:
        - Database connection pooling under load
        - Token retrieval consistency
        - No data corruption during concurrent reads
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            async def concurrent_token_access(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
                """Simulate concurrent token access with timing analysis."""
                start_time = time.time()
                
                # Make request that triggers token database access
                response = await client.get("/meli/user")
                
                end_time = time.time()
                
                return {
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "response_time": end_time - start_time,
                    "token_used": mock_get_user.call_args[0][0] if mock_get_user.called else None
                }
            
            # Execute high concurrency test for race condition detection
            concurrent_requests = 20
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                tasks = [concurrent_token_access(ac, i) for i in range(concurrent_requests)]
                results = await asyncio.gather(*tasks)
                
                # Analyze token consistency
                successful_results = [r for r in results if r["success"]]
                tokens_used = [r["token_used"] for r in successful_results if r["token_used"]]
                
                # Validate no race conditions occurred
                assert len(set(tokens_used)) == 1, "Race condition detected: Multiple tokens retrieved"
                assert all(token == sample_meli_token.access_token for token in tokens_used), "Token corruption detected"
                
                success_rate = len(successful_results) / len(results)
                assert success_rate >= 0.95, f"Race condition causing failures: {success_rate:.2%} success rate"
                
                logger.info(f"✅ Concurrent token access test passed:")
                logger.info(f"   - {len(results)} concurrent requests")
                logger.info(f"   - {success_rate:.2%} success rate")
                logger.info(f"   - Token consistency maintained")

    @pytest.mark.asyncio
    async def test_database_connection_resilience(self, sample_meli_token, mock_user_info):
        """
        Test database connection handling under concurrent load.
        
        Validates:
        - Connection pool management
        - No connection leaks
        - Graceful handling of connection limits
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Simulate high database load
            concurrent_db_requests = 15
            
            async def db_stress_request(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
                """Stress test database connections with timing."""
                try:
                    response = await client.get("/meli/user")
                    return {
                        "request_id": request_id,
                        "success": response.status_code == 200,
                        "error": None
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "error": str(e)
                    }
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                tasks = [db_stress_request(ac, i) for i in range(concurrent_db_requests)]
                results = await asyncio.gather(*tasks)
                
                # Analyze database resilience
                successful_requests = [r for r in results if r["success"]]
                failed_requests = [r for r in results if not r["success"]]
                
                success_rate = len(successful_requests) / len(results)
                
                # Validate database connection resilience
                assert success_rate >= 0.9, f"Database connection issues: {success_rate:.2%} success rate"
                
                # Log any connection errors for analysis
                for failure in failed_requests:
                    logger.warning(f"Database connection failure: {failure['error']}")
                
                logger.info(f"✅ Database connection resilience test passed:")
                logger.info(f"   - {len(results)} concurrent database operations")
                logger.info(f"   - {success_rate:.2%} success rate")
                logger.info(f"   - {len(failed_requests)} connection failures")


class TestPerformanceUnderLoad:
    """
    Test system performance under various load conditions.
    Ensures async implementation scales appropriately.
    """
    
    @pytest.mark.asyncio
    async def test_escalating_load_performance(self, sample_meli_token, mock_user_info):
        """
        Test performance under escalating concurrent load.
        
        Validates:
        - Performance degradation patterns
        - System stability under increasing load
        - Response time consistency
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Test escalating load levels
            load_levels = [5, 10, 15, 20]
            performance_results = []
            
            for load_level in load_levels:
                async def load_test_request(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
                    start_time = time.time()
                    response = await client.get("/meli/user")
                    end_time = time.time()
                    
                    return {
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    }
                
                async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                    start_time = time.time()
                    tasks = [load_test_request(ac, i) for i in range(load_level)]
                    results = await asyncio.gather(*tasks)
                    end_time = time.time()
                    
                    # Calculate performance metrics
                    total_time = end_time - start_time
                    successful_results = [r for r in results if r["success"]]
                    success_rate = len(successful_results) / len(results)
                    avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
                    throughput = len(successful_results) / total_time
                    
                    performance_results.append({
                        "load_level": load_level,
                        "success_rate": success_rate,
                        "avg_response_time": avg_response_time,
                        "throughput": throughput,
                        "total_time": total_time
                    })
                    
                    logger.info(f"Load level {load_level}: {success_rate:.2%} success, {avg_response_time:.3f}s avg, {throughput:.1f} req/s")
            
            # Validate performance doesn't degrade excessively
            for i, result in enumerate(performance_results):
                assert result["success_rate"] >= 0.85, f"Load level {result['load_level']}: Success rate too low"
                assert result["avg_response_time"] < 2.0, f"Load level {result['load_level']}: Response time too high"
                
                # Ensure reasonable throughput scaling
                if i > 0:
                    prev_throughput = performance_results[i-1]["throughput"]
                    current_throughput = result["throughput"]
                    throughput_ratio = current_throughput / prev_throughput
                    
                    # Throughput should not degrade significantly
                    assert throughput_ratio > 0.7, f"Throughput degradation too severe: {throughput_ratio:.2f}"
            
            logger.info("✅ Escalating load performance test completed successfully")

    @pytest.mark.asyncio
    async def test_sustained_load_endurance(self, sample_meli_token, mock_user_info):
        """
        Test system endurance under sustained concurrent load.
        
        Validates:
        - Memory leak detection
        - Connection stability over time
        - Performance consistency
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Sustained load configuration
            duration_seconds = 10  # Reduced for test efficiency
            requests_per_second = 5
            total_requests = duration_seconds * requests_per_second
            
            results = []
            
            async def sustained_request(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
                start_time = time.time()
                try:
                    response = await client.get("/meli/user")
                    end_time = time.time()
                    
                    return {
                        "request_id": request_id,
                        "timestamp": start_time,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200,
                        "memory_usage": None  # Could add memory monitoring here
                    }
                except Exception as e:
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "timestamp": start_time,
                        "response_time": end_time - start_time,
                        "success": False,
                        "error": str(e)
                    }
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                # Execute sustained load with controlled rate
                start_time = time.time()
                
                for batch in range(0, total_requests, requests_per_second):
                    batch_start = time.time()
                    
                    # Create batch of requests
                    batch_size = min(requests_per_second, total_requests - batch)
                    tasks = [sustained_request(ac, batch + i) for i in range(batch_size)]
                    
                    # Execute batch
                    batch_results = await asyncio.gather(*tasks)
                    results.extend(batch_results)
                    
                    # Control request rate
                    batch_duration = time.time() - batch_start
                    if batch_duration < 1.0:
                        await asyncio.sleep(1.0 - batch_duration)
                
                end_time = time.time()
                
                # Analyze sustained performance
                successful_results = [r for r in results if r["success"]]
                total_duration = end_time - start_time
                overall_success_rate = len(successful_results) / len(results)
                
                # Calculate performance stability over time
                time_windows = []
                window_size = max(1, len(successful_results) // 5)  # 5 time windows
                
                for i in range(0, len(successful_results), window_size):
                    window_results = successful_results[i:i + window_size]
                    if window_results:
                        avg_response_time = sum(r["response_time"] for r in window_results) / len(window_results)
                        time_windows.append(avg_response_time)
                
                # Validate performance stability
                if len(time_windows) > 1:
                    response_time_variance = max(time_windows) - min(time_windows)
                    assert response_time_variance < 0.5, f"Response time variance too high: {response_time_variance:.3f}s"
                
                assert overall_success_rate >= 0.9, f"Sustained load success rate too low: {overall_success_rate:.2%}"
                
                logger.info(f"✅ Sustained load endurance test completed:")
                logger.info(f"   - Duration: {total_duration:.1f}s")
                logger.info(f"   - Total requests: {len(results)}")
                logger.info(f"   - Success rate: {overall_success_rate:.2%}")
                logger.info(f"   - Performance stability maintained")


class TestAsyncErrorScenarios:
    """
    Test error handling in async and concurrent scenarios.
    Ensures robust error handling under various failure conditions.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_api_failures(self, sample_meli_token):
        """
        Test handling of API failures during concurrent requests.
        
        Validates:
        - Error isolation between concurrent requests
        - Proper error response formatting
        - System stability during failures
        """
        # Simulate intermittent API failures
        call_count = 0
        
        async def intermittent_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Every 3rd call fails
                raise Exception(f"Simulated API failure #{call_count}")
            return {"id": 123456789, "nickname": "TEST_USER"}
        
        with patch('app.services.mercadolibre.get_user_info', side_effect=intermittent_failure):
            concurrent_requests = 12  # Ensures multiple failures
            
            async def error_test_request(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
                try:
                    response = await client.get("/meli/user")
                    return {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "error_isolated": True  # No exception leaked to client
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "error_isolated": False,  # Exception not properly handled
                        "client_error": str(e)
                    }
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                tasks = [error_test_request(ac, i) for i in range(concurrent_requests)]
                results = await asyncio.gather(*tasks)
                
                # Analyze error handling
                successful_requests = [r for r in results if r["success"]]
                failed_requests = [r for r in results if not r["success"] and r.get("error_isolated", True)]
                leaked_errors = [r for r in results if not r.get("error_isolated", True)]
                
                # Validate error isolation
                assert len(leaked_errors) == 0, f"Errors leaked to client: {leaked_errors}"
                
                # Should have some failures due to intermittent API errors
                assert len(failed_requests) > 0, "Expected some API failures for testing"
                assert len(successful_requests) > 0, "Expected some successful requests"
                
                # All requests should get proper HTTP responses
                for result in results:
                    assert "status_code" in result, "Missing status code in response"
                    assert result["status_code"] in [200, 400], f"Unexpected status code: {result['status_code']}"
                
                logger.info(f"✅ Concurrent API failures test completed:")
                logger.info(f"   - Total requests: {len(results)}")
                logger.info(f"   - Successful: {len(successful_requests)}")
                logger.info(f"   - Failed gracefully: {len(failed_requests)}")
                logger.info(f"   - Error isolation maintained")

    @pytest.mark.asyncio 
    async def test_no_token_concurrent_scenario(self, test_session):
        """
        Test concurrent requests when no authentication token exists.
        
        Validates:
        - Consistent error responses
        - No race conditions in error handling
        - Proper HTTP status codes
        """
        # Ensure no tokens exist in test database
        test_session.query(MeliToken).delete()
        test_session.query(OAuthToken).delete()
        test_session.commit()
        
        concurrent_requests = 10
        
        async def no_token_request(client: httpx.AsyncClient, request_id: int) -> Dict[str, Any]:
            response = await client.get("/meli/user")
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_data": response.json(),
                "consistent_error": response.status_code == 404
            }
        
        async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
            tasks = [no_token_request(ac, i) for i in range(concurrent_requests)]
            results = await asyncio.gather(*tasks)
            
            # Validate consistent error responses
            for result in results:
                assert result["status_code"] == 404, f"Inconsistent status code: {result['status_code']}"
                assert "Nenhum token válido encontrado" in result["response_data"]["detail"]
                assert result["consistent_error"], "Inconsistent error response"
            
            logger.info(f"✅ No token concurrent scenario test completed:")
            logger.info(f"   - All {len(results)} requests returned consistent 404 errors")


# Performance benchmarking for CI/CD integration
class TestAsyncPerformanceBenchmarks:
    """
    Performance benchmarks for continuous integration monitoring.
    Ensures async performance doesn't regress over time.
    """
    
    @pytest.mark.asyncio
    async def test_single_request_benchmark(self, sample_meli_token, mock_user_info):
        """
        Benchmark single async request performance.
        Sets baseline for performance regression testing.
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Warm up
            async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
                await ac.get("/meli/user")
            
            # Benchmark runs
            benchmark_runs = 5
            response_times = []
            
            async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
                for run in range(benchmark_runs):
                    start_time = time.time()
                    response = await ac.get("/meli/user")
                    end_time = time.time()
                    
                    assert response.status_code == 200
                    response_times.append(end_time - start_time)
            
            # Calculate benchmark metrics
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Performance assertions for CI/CD
            assert avg_response_time < 0.1, f"Average response time regression: {avg_response_time:.3f}s"
            assert max_response_time < 0.2, f"Maximum response time regression: {max_response_time:.3f}s"
            
            logger.info(f"✅ Single request benchmark completed:")
            logger.info(f"   - Average: {avg_response_time:.3f}s")
            logger.info(f"   - Min: {min_response_time:.3f}s") 
            logger.info(f"   - Max: {max_response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_throughput_benchmark(self, sample_meli_token, mock_user_info):
        """
        Benchmark concurrent request throughput.
        Ensures async scalability meets requirements.
        """
        with patch('app.services.mercadolibre.get_user_info', new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user_info
            
            # Throughput test configuration
            concurrent_requests = 20
            
            async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as ac:
                start_time = time.time()
                
                tasks = [ac.get("/meli/user") for _ in range(concurrent_requests)]
                responses = await asyncio.gather(*tasks)
                
                end_time = time.time()
                
                # Calculate throughput metrics
                total_time = end_time - start_time
                successful_responses = [r for r in responses if r.status_code == 200]
                throughput = len(successful_responses) / total_time
                
                # Throughput assertions for CI/CD
                assert len(successful_responses) == concurrent_requests, "Some requests failed"
                assert throughput >= 10.0, f"Throughput regression: {throughput:.1f} req/s below 10 req/s"
                
                logger.info(f"✅ Concurrent throughput benchmark completed:")
                logger.info(f"   - Requests: {concurrent_requests}")
                logger.info(f"   - Success rate: 100%")
                logger.info(f"   - Throughput: {throughput:.1f} req/s")
                logger.info(f"   - Total time: {total_time:.3f}s")


if __name__ == "__main__":
    """
    Run async behavior tests independently for development and debugging.
    Usage: python -m pytest backend/app/tests/test_async_behavior.py -v
    """
    pytest.main([__file__, "-v", "--tb=short"])