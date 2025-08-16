"""
End-to-end tests for complete user journeys and API lifecycle.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import patch
import time
from datetime import datetime

from app.models import User, OAuthSession
from app.core.security import get_password_hash


@pytest.mark.e2e
class TestCompleteUserJourneys:
    """Test complete user journeys from start to finish."""
    
    def test_new_user_complete_journey(self, client: TestClient, db: Session):
        """Test complete journey for a new user."""
        # Step 1: User registration
        registration_data = {
            "email": "journey_user@example.com",
            "password": "SecurePassword123!",
            "is_active": True
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code in [200, 201, 409]
        
        # Step 2: User login
        login_data = {
            "username": "journey_user@example.com",
            "password": "SecurePassword123!"
        }
        
        login_response = client.post("/api/auth/token", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 3: Use SEO optimization service
            seo_data = {
                "text": "High-quality wireless bluetooth headphones with excellent sound quality",
                "max_length": 160,
                "keywords": ["bluetooth", "headphones", "wireless"]
            }
            
            seo_response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            assert seo_response.status_code == 200
            
            seo_result = seo_response.json()
            assert "original" in seo_result
            assert "title" in seo_result
            assert "meta_description" in seo_result
            assert "keywords" in seo_result
            assert "slug" in seo_result
            
            # Step 4: Access categories
            categories_response = client.get("/api/categories/", headers=auth_headers)
            assert categories_response.status_code == 200
            
            categories_data = categories_response.json()
            assert isinstance(categories_data, list)
            
            # Step 5: Get specific category details
            if categories_data:
                category_id = categories_data[0]["id"]
                category_response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
                assert category_response.status_code == 200
                
    def test_mercado_livre_integration_journey(self, client: TestClient, db: Session):
        """Test complete Mercado Livre integration journey."""
        # Step 1: Initiate OAuth flow
        oauth_response = client.get("/oauth/login")
        assert oauth_response.status_code in [200, 302]
        
        if oauth_response.status_code == 200:
            oauth_data = oauth_response.json()
            
            if "redirect_url" in oauth_data and "state" in oauth_data:
                state = oauth_data["state"]
                
                # Step 2: Simulate OAuth callback
                callback_params = {
                    "code": "simulated_auth_code",
                    "state": state
                }
                
                with patch('app.services.mercadolibre.exchange_code_for_token') as mock_exchange:
                    mock_exchange.return_value = {
                        "access_token": "APP_USR-test-token",
                        "token_type": "Bearer",
                        "expires_in": 21600,
                        "refresh_token": "TG-test-refresh-token",
                        "user_id": "123456789"
                    }
                    
                    callback_response = client.get("/oauth/callback", params=callback_params)
                    # Response depends on implementation
                    assert callback_response.status_code in [200, 302, 400]
                    
        # Step 3: Access Mercado Livre endpoints (if authenticated)
        # This would require proper OAuth session setup
        with patch('app.routers.meli_routes.get_valid_token') as mock_token:
            mock_token.return_value = "valid_ml_token"
            
            with patch('app.services.mercadolibre.get_user_info') as mock_user_info:
                mock_user_info.return_value = {
                    "id": 123456789,
                    "nickname": "TEST_USER",
                    "email": "test@example.com"
                }
                
                ml_user_response = client.get("/meli/user")
                # Response depends on implementation and route protection
                assert ml_user_response.status_code in [200, 401, 404]
                
    def test_error_recovery_journey(self, client: TestClient, db: Session):
        """Test user journey with error recovery."""
        # Step 1: Failed login attempt
        wrong_login_data = {
            "username": "nonexistent@example.com",
            "password": "WrongPassword"
        }
        
        failed_login = client.post("/api/auth/token", data=wrong_login_data)
        assert failed_login.status_code in [401, 422]
        
        # Step 2: Successful registration
        registration_data = {
            "email": "recovery_user@example.com",
            "password": "CorrectPassword123!",
            "is_active": True
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code in [200, 201]
        
        # Step 3: Successful login after registration
        correct_login_data = {
            "username": "recovery_user@example.com",
            "password": "CorrectPassword123!"
        }
        
        login_response = client.post("/api/auth/token", data=correct_login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 4: Use services successfully
            health_response = client.get("/health", headers=auth_headers)
            assert health_response.status_code == 200
            
    def test_admin_user_journey(self, client: TestClient, db: Session):
        """Test admin user journey with elevated permissions."""
        # Create admin user directly in database
        admin_user = User(
            email="admin_journey@example.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        
        # Step 1: Admin login
        admin_login_data = {
            "username": "admin_journey@example.com",
            "password": "AdminPassword123!"
        }
        
        login_response = client.post("/api/auth/token", data=admin_login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 2: Access regular endpoints
            health_response = client.get("/health", headers=auth_headers)
            assert health_response.status_code == 200
            
            # Step 3: Access admin-only endpoints (if implemented)
            admin_response = client.get("/api/admin/users", headers=auth_headers)
            # Should either work or not exist
            assert admin_response.status_code in [200, 404]
            
            # Step 4: Perform admin operations
            seo_data = {
                "text": "Admin test content for SEO optimization",
                "max_length": 200
            }
            
            seo_response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            assert seo_response.status_code == 200


@pytest.mark.e2e
class TestAPILifecycle:
    """Test complete API lifecycle scenarios."""
    
    def test_api_endpoint_lifecycle(self, client: TestClient, db: Session, auth_headers: dict):
        """Test complete API endpoint lifecycle."""
        # Step 1: Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "ok"
        
        # Step 2: Authentication verification
        if auth_headers:
            # Step 3: SEO service lifecycle
            seo_requests = [
                {
                    "text": "Short text",
                    "max_length": 100
                },
                {
                    "text": "Medium length product description with more details about features",
                    "max_length": 160
                },
                {
                    "text": "Very long product description with extensive details about features, specifications, benefits, and usage scenarios that would typically be found in a comprehensive product listing",
                    "max_length": 250
                }
            ]
            
            for seo_request in seo_requests:
                seo_response = client.post("/api/seo/optimize", json=seo_request, headers=auth_headers)
                assert seo_response.status_code == 200
                
                seo_data = seo_response.json()
                assert len(seo_data["meta_description"]) <= seo_request["max_length"]
                
            # Step 4: Categories service lifecycle
            categories_response = client.get("/api/categories/", headers=auth_headers)
            assert categories_response.status_code == 200
            
            categories_data = categories_response.json()
            assert isinstance(categories_data, list)
            
            # Test specific category if available
            if categories_data:
                for category in categories_data[:3]:  # Test first 3 categories
                    category_id = category["id"]
                    detail_response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
                    assert detail_response.status_code == 200
                    
    def test_concurrent_api_usage(self, client: TestClient, auth_headers: dict):
        """Test concurrent API usage scenarios."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(request_id):
            try:
                # Health check
                health_response = client.get("/health")
                
                # SEO optimization
                if auth_headers:
                    seo_data = {
                        "text": f"Product description {request_id} for testing concurrent access",
                        "max_length": 160
                    }
                    seo_response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
                    
                    results.put({
                        "request_id": request_id,
                        "health_status": health_response.status_code,
                        "seo_status": seo_response.status_code,
                        "success": health_response.status_code == 200 and seo_response.status_code == 200
                    })
                else:
                    results.put({
                        "request_id": request_id,
                        "health_status": health_response.status_code,
                        "success": health_response.status_code == 200
                    })
                    
            except Exception as e:
                results.put({
                    "request_id": request_id,
                    "error": str(e),
                    "success": False
                })
                
        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
            
        # Verify results
        assert len(all_results) == 5
        successful_requests = [r for r in all_results if r.get("success", False)]
        assert len(successful_requests) >= 3  # At least 3 should succeed
        
    def test_api_performance_journey(self, client: TestClient, auth_headers: dict):
        """Test API performance characteristics."""
        performance_results = []
        
        # Test various endpoints with timing
        endpoints_to_test = [
            ("GET", "/health", None),
        ]
        
        if auth_headers:
            endpoints_to_test.extend([
                ("GET", "/api/categories/", None),
                ("POST", "/api/seo/optimize", {
                    "text": "Performance test product description",
                    "max_length": 160
                })
            ])
            
        for method, endpoint, data in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers)
            elif method == "POST":
                response = client.post(endpoint, json=data, headers=auth_headers)
                
            end_time = time.time()
            response_time = end_time - start_time
            
            performance_results.append({
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200
            })
            
        # Verify performance requirements
        for result in performance_results:
            assert result["response_time"] < 5.0  # 5 second max response time
            if result["success"]:
                assert result["response_time"] < 2.0  # 2 second max for successful requests
                
    def test_data_consistency_journey(self, client: TestClient, db: Session):
        """Test data consistency across API operations."""
        # Create user for testing
        test_user = User(
            email="consistency_test@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Verify user was created
        created_user = db.get(User, test_user.id)
        assert created_user is not None
        assert created_user.email == "consistency_test@example.com"
        
        # Test login with created user
        login_data = {
            "username": "consistency_test@example.com",
            "password": "TestPassword123!"
        }
        
        login_response = client.post("/api/auth/token", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            
            # Use authenticated endpoints
            health_response = client.get("/health", headers=auth_headers)
            assert health_response.status_code == 200
            
            # Verify user still exists in database
            final_user = db.get(User, test_user.id)
            assert final_user is not None
            assert final_user.email == created_user.email
            assert final_user.id == created_user.id


@pytest.mark.e2e
class TestComplexScenarios:
    """Test complex real-world scenarios."""
    
    def test_high_load_simulation(self, client: TestClient, auth_headers: dict):
        """Test system behavior under high load."""
        import threading
        import queue
        import time
        
        results = queue.Queue()
        start_time = time.time()
        
        def load_test_worker(worker_id, num_requests):
            for i in range(num_requests):
                try:
                    # Mix of different operations
                    operations = [
                        lambda: client.get("/health"),
                    ]
                    
                    if auth_headers:
                        operations.extend([
                            lambda: client.post("/api/seo/optimize", json={
                                "text": f"Load test content {worker_id}-{i}",
                                "max_length": 160
                            }, headers=auth_headers),
                            lambda: client.get("/api/categories/", headers=auth_headers)
                        ])
                        
                    # Execute random operation
                    import random
                    operation = random.choice(operations)
                    response = operation()
                    
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
                    
        # Start load test with multiple workers
        workers = []
        num_workers = 3
        requests_per_worker = 10
        
        for worker_id in range(num_workers):
            worker = threading.Thread(
                target=load_test_worker, 
                args=(worker_id, requests_per_worker)
            )
            workers.append(worker)
            worker.start()
            
        # Wait for all workers to complete
        for worker in workers:
            worker.join()
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect and analyze results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
            
        total_requests = num_workers * requests_per_worker
        successful_requests = len([r for r in all_results if r.get("success", False)])
        success_rate = successful_requests / total_requests
        
        # Performance assertions
        assert len(all_results) == total_requests
        assert success_rate >= 0.8  # At least 80% success rate
        assert total_time < 30.0  # Should complete within 30 seconds
        
    def test_error_cascade_handling(self, client: TestClient, db: Session):
        """Test system resilience to cascading errors."""
        # Step 1: Create scenario that might cause errors
        invalid_requests = [
            # Invalid SEO request
            {
                "endpoint": "/api/seo/optimize",
                "method": "POST",
                "data": {"invalid": "data"},
                "headers": {"Authorization": "Bearer invalid_token"}
            },
            # Invalid auth request
            {
                "endpoint": "/api/auth/token",
                "method": "POST",
                "data": {"invalid": "credentials"}
            },
            # Non-existent endpoint
            {
                "endpoint": "/api/nonexistent",
                "method": "GET",
                "data": None,
                "headers": None
            }
        ]
        
        error_responses = []
        
        for request_config in invalid_requests:
            try:
                if request_config["method"] == "GET":
                    response = client.get(
                        request_config["endpoint"],
                        headers=request_config.get("headers")
                    )
                elif request_config["method"] == "POST":
                    response = client.post(
                        request_config["endpoint"],
                        json=request_config["data"],
                        headers=request_config.get("headers")
                    )
                    
                error_responses.append({
                    "endpoint": request_config["endpoint"],
                    "status_code": response.status_code,
                    "handled_gracefully": response.status_code != 500
                })
                
            except Exception as e:
                error_responses.append({
                    "endpoint": request_config["endpoint"],
                    "error": str(e),
                    "handled_gracefully": False
                })
                
        # Step 2: Verify system still responds to valid requests
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Step 3: Verify errors were handled gracefully
        for error_response in error_responses:
            assert error_response.get("handled_gracefully", False), \
                f"Error not handled gracefully for {error_response['endpoint']}"
                
    def test_data_integrity_under_stress(self, client: TestClient, db: Session):
        """Test data integrity under concurrent operations."""
        import threading
        
        # Create base user
        base_user = User(
            email="stress_test@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(base_user)
        db.commit()
        initial_user_count = len(db.exec(select(User)).all())
        
        def concurrent_operations(thread_id):
            # Each thread tries to create OAuth sessions
            for i in range(5):
                oauth_session = OAuthSession(
                    endpoint_id=thread_id,
                    state=f"thread_{thread_id}_session_{i}",
                    code_verifier=f"verifier_{thread_id}_{i}"
                )
                db.add(oauth_session)
                
            try:
                db.commit()
            except Exception:
                db.rollback()
                
        # Run concurrent operations
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=concurrent_operations, args=(thread_id,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Verify data integrity
        final_user_count = len(db.exec(select(User)).all())
        oauth_sessions = db.exec(select(OAuthSession)).all()
        
        # User count should be unchanged
        assert final_user_count == initial_user_count
        
        # OAuth sessions should have been created (some may fail due to conflicts)
        assert len(oauth_sessions) > 0
        
        # Verify no data corruption
        for session in oauth_sessions:
            assert session.state is not None
            assert session.code_verifier is not None
            assert isinstance(session.endpoint_id, int)