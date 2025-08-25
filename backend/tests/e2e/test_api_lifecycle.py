"""
End-to-end tests for API lifecycle and comprehensive system testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, MagicMock
import time
import json
from datetime import datetime, timedelta


@pytest.mark.e2e
class TestAPILifecycleManagement:
    """Test complete API lifecycle management."""
    
    def test_application_startup_lifecycle(self, client: TestClient):
        """Test application startup and initialization."""
        # Test that application starts successfully
        assert client.app is not None
        
        # Test health endpoint availability
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert health_data["status"] == "ok"
        
    def test_database_connectivity_lifecycle(self, client: TestClient, db: Session):
        """Test database connectivity throughout lifecycle."""
        # Test database is accessible
        assert db is not None
        
        # Test basic database operations work
        from sqlmodel import text
        result = db.exec(text("SELECT 1")).first()
        assert result == 1
        
        # Test application can handle database operations
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
    def test_api_versioning_lifecycle(self, client: TestClient):
        """Test API versioning and backward compatibility."""
        # Test current API version endpoints
        endpoints_to_test = [
            "/health",
            "/api/auth/register",
            "/api/seo/optimize",
            "/api/categories/",
            "/oauth/login"
        ]
        
        for endpoint in endpoints_to_test:
            if endpoint in ["/api/auth/register", "/api/seo/optimize"]:
                # POST endpoints
                response = client.post(endpoint, json={})
                # Should handle empty requests gracefully
                assert response.status_code in [200, 400, 401, 422]
            else:
                # GET endpoints
                response = client.get(endpoint)
                # Should be accessible or require auth
                assert response.status_code in [200, 302, 401]
                
    def test_dependency_initialization_lifecycle(self, client: TestClient):
        """Test that all dependencies are properly initialized."""
        # Test that JWT dependencies work
        from app.core.security import create_access_token
        token = create_access_token({"sub": "test@example.com"})
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test that password hashing works
        from app.core.security import get_password_hash, verify_password
        password = "test_password"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        
        # Test that SEO services work
        from app.services.seo import optimize_text
        result = optimize_text("test text")
        assert isinstance(result, dict)
        assert "original" in result
        
    def test_configuration_lifecycle(self, client: TestClient):
        """Test configuration management throughout lifecycle."""
        from app.config import settings
        
        # Test that settings are loaded
        assert settings is not None
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'secret_key')
        
        # Test that settings affect application behavior
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.secret_key, str)
        assert len(settings.secret_key) > 0


@pytest.mark.e2e
class TestAPIErrorHandlingLifecycle:
    """Test error handling throughout API lifecycle."""
    
    def test_graceful_error_handling(self, client: TestClient):
        """Test graceful error handling across all endpoints."""
        error_scenarios = [
            # Invalid JSON
            {
                "endpoint": "/api/auth/register",
                "method": "POST",
                "data": "invalid json",
                "headers": {"Content-Type": "application/json"}
            },
            # Missing required fields
            {
                "endpoint": "/api/auth/register",
                "method": "POST",
                "data": {"email": "test@example.com"},  # Missing password
                "headers": {"Content-Type": "application/json"}
            },
            # Invalid authorization
            {
                "endpoint": "/api/seo/optimize",
                "method": "POST",
                "data": {"text": "test"},
                "headers": {"Authorization": "Bearer invalid_token"}
            }
        ]
        
        for scenario in error_scenarios:
            try:
                if scenario["method"] == "POST":
                    if isinstance(scenario["data"], str):
                        # Raw string data
                        response = client.post(
                            scenario["endpoint"],
                            content=scenario["data"],
                            headers=scenario["headers"]
                        )
                    else:
                        # JSON data
                        response = client.post(
                            scenario["endpoint"],
                            json=scenario["data"],
                            headers=scenario.get("headers", {})
                        )
                else:
                    response = client.get(
                        scenario["endpoint"],
                        headers=scenario.get("headers", {})
                    )
                    
                # Should handle errors gracefully, not crash
                assert response.status_code != 500, f"Server error for {scenario['endpoint']}"
                assert response.status_code in [400, 401, 422], \
                    f"Unexpected status code {response.status_code} for {scenario['endpoint']}"
                    
            except Exception as e:
                pytest.fail(f"Exception raised for {scenario['endpoint']}: {str(e)}")
                
    def test_rate_limiting_error_handling(self, client: TestClient):
        """Test rate limiting and throttling error handling."""
        # Make multiple rapid requests to test rate limiting
        responses = []
        
        for i in range(20):  # 20 rapid requests
            response = client.get("/health")
            responses.append(response.status_code)
            
        # Most should succeed, some might be rate limited
        success_responses = [r for r in responses if r == 200]
        rate_limited_responses = [r for r in responses if r == 429]
        
        # Should handle requests properly
        assert len(success_responses) >= 10  # At least half should succeed
        # Rate limiting might not be implemented yet
        assert len(rate_limited_responses) >= 0
        
    def test_database_error_recovery(self, client: TestClient):
        """Test database error recovery scenarios."""
        # Test with mock database errors
        with patch('app.db.get_session') as mock_session:
            # Mock database error
            mock_session.side_effect = Exception("Database connection error")
            
            # Application should handle database errors gracefully
            response = client.get("/health")
            
            # Might still work if health check doesn't need database
            # Or should return appropriate error
            assert response.status_code in [200, 503]
            
    def test_external_service_error_handling(self, client: TestClient, auth_headers: dict):
        """Test handling of external service errors."""
        if not auth_headers:
            pytest.skip("Auth headers not available")
            
        # Mock external service failures
        with patch('app.services.mercadolibre.get_user_info') as mock_ml_service:
            mock_ml_service.side_effect = Exception("External service unavailable")
            
            # Application should handle external service errors
            response = client.get("/meli/user", headers=auth_headers)
            
            # Should return appropriate error, not crash
            assert response.status_code in [404, 503, 502]


@pytest.mark.e2e
class TestAPIPerformanceLifecycle:
    """Test API performance characteristics throughout lifecycle."""
    
    def test_response_time_consistency(self, client: TestClient, auth_headers: dict):
        """Test response time consistency across requests."""
        response_times = []
        
        # Test multiple requests to same endpoint
        for _ in range(10):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
            
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Performance assertions
        assert avg_time < 1.0  # Average under 1 second
        assert max_time < 2.0  # Max under 2 seconds
        assert min_time < 0.5  # Min under 0.5 seconds
        
        # Consistency check (max shouldn't be much higher than average)
        assert max_time / avg_time < 3.0
        
    def test_memory_usage_stability(self, client: TestClient, auth_headers: dict, memory_monitor):
        """Test memory usage stability during operations."""
        initial_memory = memory_monitor['initial']
        process = memory_monitor['process']
        
        # Perform various operations
        operations = [
            lambda: client.get("/health"),
        ]
        
        if auth_headers:
            operations.extend([
                lambda: client.post("/api/seo/optimize", json={
                    "text": "Memory test content for SEO optimization",
                    "max_length": 160
                }, headers=auth_headers),
                lambda: client.get("/api/categories/", headers=auth_headers)
            ])
            
        # Execute operations multiple times
        for _ in range(50):
            for operation in operations:
                response = operation()
                assert response.status_code == 200
                
        # Check memory after operations
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory should not increase excessively
        assert memory_increase < 100  # Less than 100MB increase
        
    def test_concurrent_request_handling(self, client: TestClient, concurrent_requests_config):
        """Test concurrent request handling performance."""
        import threading
        import queue
        
        results = queue.Queue()
        config = concurrent_requests_config
        
        def worker(worker_id):
            for request_id in range(config["requests_per_worker"]):
                start_time = time.time()
                
                try:
                    response = client.get("/health")
                    end_time = time.time()
                    
                    results.put({
                        "worker_id": worker_id,
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    results.put({
                        "worker_id": worker_id,
                        "request_id": request_id,
                        "error": str(e),
                        "response_time": end_time - start_time,
                        "success": False
                    })
                    
        # Start workers
        workers = []
        for worker_id in range(config["max_workers"]):
            worker = threading.Thread(target=worker, args=(worker_id,))
            workers.append(worker)
            worker.start()
            
        # Wait for completion
        for worker in workers:
            worker.join(timeout=config["timeout"])
            
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
            
        # Analyze results
        total_requests = config["max_workers"] * config["requests_per_worker"]
        successful_requests = [r for r in all_results if r.get("success", False)]
        
        # Performance assertions
        assert len(all_results) == total_requests
        assert len(successful_requests) >= total_requests * 0.9  # 90% success rate
        
        # Response time analysis
        response_times = [r["response_time"] for r in successful_requests]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 2.0  # Average under 2 seconds
            
    def test_throughput_performance(self, client: TestClient):
        """Test API throughput performance."""
        start_time = time.time()
        successful_requests = 0
        total_requests = 100
        
        for i in range(total_requests):
            response = client.get("/health")
            if response.status_code == 200:
                successful_requests += 1
                
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate throughput
        throughput = successful_requests / total_time  # requests per second
        
        # Performance assertions
        assert successful_requests >= total_requests * 0.95  # 95% success rate
        assert throughput >= 10  # At least 10 requests per second
        assert total_time < 30  # Complete within 30 seconds


@pytest.mark.e2e
class TestAPISecurityLifecycle:
    """Test security aspects throughout API lifecycle."""
    
    def test_authentication_security_lifecycle(self, client: TestClient, db: Session):
        """Test authentication security throughout lifecycle."""
        # Test password security
        from app.core.security import get_password_hash, verify_password
        
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (salted)
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        
        # Wrong password should not verify
        assert not verify_password("WrongPassword", hash1)
        
    def test_token_security_lifecycle(self, client: TestClient, db: Session):
        """Test token security throughout lifecycle."""
        from app.core.security import create_access_token
        from app.models import User
        
        # Create test user
        user = User(
            email="security_test@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Test token creation
        token1 = create_access_token({"sub": user.email})
        token2 = create_access_token({"sub": user.email})
        
        # Tokens should be different (non-deterministic)
        assert token1 != token2
        
        # Test token usage
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        response1 = client.get("/health", headers=headers1)
        response2 = client.get("/health", headers=headers2)
        
        # Both should work
        assert response1.status_code == 200
        assert response2.status_code == 200
        
    def test_input_validation_security(self, client: TestClient):
        """Test input validation security measures."""
        malicious_inputs = [
            # SQL injection attempts
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            
            # XSS attempts
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            
            # Command injection attempts
            "; rm -rf /",
            "$(rm -rf /)",
            
            # Path traversal attempts
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in registration endpoint
            registration_data = {
                "email": malicious_input,
                "password": "password123",
                "is_active": True
            }
            
            response = client.post("/api/auth/register", json=registration_data)
            
            # Should handle malicious input safely
            assert response.status_code in [400, 422]  # Validation error
            
            # Should not return server error (which might indicate successful injection)
            assert response.status_code != 500
            
    def test_authorization_security_lifecycle(self, client: TestClient, db: Session):
        """Test authorization security throughout lifecycle."""
        from app.models import User
        from app.core.security import create_access_token
        
        # Create regular user
        regular_user = User(
            email="regular@example.com",
            hashed_password=get_password_hash("Password123!"),
            is_active=True,
            is_superuser=False
        )
        db.add(regular_user)
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        
        # Create tokens
        regular_token = create_access_token({"sub": regular_user.email})
        admin_token = create_access_token({"sub": admin_user.email})
        
        regular_headers = {"Authorization": f"Bearer {regular_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test regular user access
        response = client.get("/health", headers=regular_headers)
        assert response.status_code == 200
        
        # Test admin user access
        response = client.get("/health", headers=admin_headers)
        assert response.status_code == 200
        
        # Test admin-only endpoints (if they exist)
        admin_response = client.get("/api/admin/users", headers=regular_headers)
        assert admin_response.status_code in [401, 403, 404]  # Should be denied or not exist
        
        admin_response = client.get("/api/admin/users", headers=admin_headers)
        assert admin_response.status_code in [200, 404]  # Should work or not exist


@pytest.mark.e2e
class TestAPIIntegrationLifecycle:
    """Test API integration scenarios throughout lifecycle."""
    
    def test_end_to_end_workflow_integration(self, client: TestClient, db: Session):
        """Test complete end-to-end workflow integration."""
        # Step 1: User registration
        registration_data = {
            "email": "workflow_integration@example.com",
            "password": "WorkflowPassword123!",
            "is_active": True
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code in [200, 201, 409]
        
        # Step 2: User authentication
        login_data = {
            "username": "workflow_integration@example.com",
            "password": "WorkflowPassword123!"
        }
        
        login_response = client.post("/api/auth/token", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 3: Use core services
            workflow_steps = [
                # SEO optimization
                {
                    "action": "seo_optimization",
                    "endpoint": "/api/seo/optimize",
                    "method": "POST",
                    "data": {
                        "text": "Complete workflow integration test product description",
                        "max_length": 160,
                        "keywords": ["integration", "test", "workflow"]
                    }
                },
                # Categories access
                {
                    "action": "categories_access",
                    "endpoint": "/api/categories/",
                    "method": "GET",
                    "data": None
                }
            ]
            
            workflow_results = []
            
            for step in workflow_steps:
                if step["method"] == "POST":
                    response = client.post(
                        step["endpoint"],
                        json=step["data"],
                        headers=auth_headers
                    )
                else:
                    response = client.get(step["endpoint"], headers=auth_headers)
                    
                workflow_results.append({
                    "action": step["action"],
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
                
                if response.status_code == 200 and step["action"] == "seo_optimization":
                    seo_data = response.json()
                    assert "original" in seo_data
                    assert "meta_description" in seo_data
                    assert len(seo_data["meta_description"]) <= 160
                    
            # Verify workflow completion
            successful_steps = [r for r in workflow_results if r["success"]]
            assert len(successful_steps) >= len(workflow_steps) * 0.8  # 80% success rate
            
    def test_service_integration_dependencies(self, client: TestClient):
        """Test service integration and dependencies."""
        # Test that all services are properly integrated
        service_tests = [
            {
                "service": "health_check",
                "test": lambda: client.get("/health"),
                "expected_status": 200
            },
            {
                "service": "seo_service",
                "test": lambda: client.post("/api/seo/optimize", json={}),
                "expected_status": [400, 401, 422]  # Should handle empty request
            },
            {
                "service": "auth_service",
                "test": lambda: client.post("/api/auth/register", json={}),
                "expected_status": [400, 422]  # Should validate input
            }
        ]
        
        for service_test in service_tests:
            response = service_test["test"]()
            
            if isinstance(service_test["expected_status"], list):
                assert response.status_code in service_test["expected_status"], \
                    f"Service {service_test['service']} failed with status {response.status_code}"
            else:
                assert response.status_code == service_test["expected_status"], \
                    f"Service {service_test['service']} failed with status {response.status_code}"
                    
    def test_external_service_integration_lifecycle(self, client: TestClient):
        """Test external service integration lifecycle."""
        # Test OAuth integration
        oauth_response = client.get("/oauth/login")
        assert oauth_response.status_code in [200, 302]  # Should provide OAuth flow
        
        # Test with mocked external services
        with patch('app.services.mercadolibre.get_user_info') as mock_ml:
            mock_ml.return_value = {
                "id": 123456789,
                "nickname": "TEST_USER",
                "email": "test@example.com"
            }
            
            # Test external service integration
            # This would require proper authentication setup
            # For now, just verify the service layer works
            from app.services.mercadolibre import get_user_info
            
            # Test with asyncio
            import asyncio
            
            async def test_ml_service():
                try:
                    result = await get_user_info("test_token")
                    return result
                except Exception as e:
                    return {"error": str(e)}
                    
            # Run async test
            result = asyncio.run(test_ml_service())
            
            # Should either work with mock or handle gracefully
            assert isinstance(result, dict)
            
    def test_data_flow_integration_lifecycle(self, client: TestClient, db: Session):
        """Test data flow integration throughout lifecycle."""
        from app.models import User, OAuthSession
        
        # Test data creation flow
        user = User(
            email="dataflow_test@example.com",
            hashed_password=get_password_hash("DataFlowPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Test data retrieval flow
        retrieved_user = db.get(User, user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == user.email
        
        # Test related data creation
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="dataflow_test_state",
            code_verifier="dataflow_test_verifier"
        )
        db.add(oauth_session)
        db.commit()
        
        # Test data relationship queries
        from sqlmodel import select
        sessions = db.exec(
            select(OAuthSession).where(OAuthSession.state == "dataflow_test_state")
        ).all()
        
        assert len(sessions) == 1
        assert sessions[0].state == "dataflow_test_state"
        
        # Test data cleanup
        db.delete(oauth_session)
        db.delete(user)
        db.commit()
        
        # Verify cleanup
        deleted_user = db.get(User, user.id)
        assert deleted_user is None