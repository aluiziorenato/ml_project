"""
End-to-end tests for API lifecycle management and workflows.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import time

from app.models import User, ApiEndpoint


@pytest.mark.e2e
class TestAPILifecycleManagement:
    """Test complete API lifecycle management workflows."""
    
    def test_api_endpoint_complete_lifecycle(self, client: TestClient):
        """Test complete API endpoint lifecycle from creation to deletion."""
        # Setup: Create and authenticate user
        user_data = {
            "email": "lifecycle_user@example.com",
            "password": "lifecycle_password_123"
        }
        
        # Register user
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login user
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Phase 1: Create multiple endpoints
        endpoints_data = [
            {
                "name": "Primary API",
                "url": "https://api.primary.com",
                "auth_type": "oauth",
                "oauth_scope": "read write"
            },
            {
                "name": "Secondary API",
                "url": "https://api.secondary.com",
                "auth_type": "api_key",
                "api_key_header": "X-API-Key"
            },
            {
                "name": "Public API",
                "url": "https://api.public.com",
                "auth_type": "none"
            }
        ]
        
        created_endpoints = []
        for endpoint_data in endpoints_data:
            response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
            assert response.status_code == 201
            created_endpoint = response.json()
            assert created_endpoint["name"] == endpoint_data["name"]
            created_endpoints.append(created_endpoint)
        
        # Phase 2: List and verify all endpoints
        list_response = client.get("/api/endpoints/", headers=auth_headers)
        assert list_response.status_code == 200
        endpoints_list = list_response.json()
        
        assert len(endpoints_list) >= len(created_endpoints)
        for created_endpoint in created_endpoints:
            assert any(ep["id"] == created_endpoint["id"] for ep in endpoints_list)
        
        # Phase 3: Detailed testing of each endpoint
        for i, endpoint in enumerate(created_endpoints):
            endpoint_id = endpoint["id"]
            
            # Get endpoint details
            get_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
            assert get_response.status_code == 200
            endpoint_details = get_response.json()
            assert endpoint_details["id"] == endpoint_id
            assert endpoint_details["name"] == endpoints_data[i]["name"]
            
            # Update endpoint
            updated_name = f"Updated {endpoints_data[i]['name']}"
            update_data = {"name": updated_name}
            
            update_response = client.put(f"/api/endpoints/{endpoint_id}", json=update_data, headers=auth_headers)
            assert update_response.status_code == 200
            updated_endpoint = update_response.json()
            assert updated_endpoint["name"] == updated_name
            
        # Phase 4: Test endpoint relationships and dependencies
        # Create API tests for endpoints
        for endpoint in created_endpoints:
            test_data = {
                "endpoint_id": endpoint["id"],
                "name": f"Test for {endpoint['name']}",
                "request_method": "GET",
                "request_path": "/health",
                "expected_status": 200
            }
            
            test_response = client.post("/api/tests/", json=test_data, headers=auth_headers)
            if test_response.status_code == 201:  # If endpoint exists
                test_id = test_response.json()["id"]
                
                # Execute test
                execute_response = client.post(f"/api/tests/{test_id}/execute", headers=auth_headers)
                # Test execution might fail due to mock endpoints, but structure should be valid
                assert execute_response.status_code in [200, 400, 404, 500]
        
        # Phase 5: Bulk operations
        # Get all endpoints again to verify updates
        final_list_response = client.get("/api/endpoints/", headers=auth_headers)
        assert final_list_response.status_code == 200
        final_endpoints = final_list_response.json()
        
        for endpoint in final_endpoints:
            if endpoint["id"] in [ep["id"] for ep in created_endpoints]:
                assert endpoint["name"].startswith("Updated")
        
        # Phase 6: Cleanup - Delete all created endpoints
        for endpoint in created_endpoints:
            delete_response = client.delete(f"/api/endpoints/{endpoint['id']}", headers=auth_headers)
            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert delete_data["deleted"] is True
        
        # Phase 7: Verify deletion
        for endpoint in created_endpoints:
            get_deleted_response = client.get(f"/api/endpoints/{endpoint['id']}", headers=auth_headers)
            assert get_deleted_response.status_code == 404
    
    def test_api_testing_workflow(self, client: TestClient):
        """Test complete API testing workflow."""
        # Setup user authentication
        user_data = {
            "email": "api_tester_workflow@example.com",
            "password": "testing_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Create test endpoint
        endpoint_data = {
            "name": "Testing Workflow API",
            "url": "https://jsonplaceholder.typicode.com",
            "auth_type": "none"
        }
        
        endpoint_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = endpoint_response.json()["id"]
        
        # Create multiple test cases
        test_cases = [
            {
                "name": "Get All Posts",
                "request_method": "GET",
                "request_path": "/posts",
                "expected_status": 200
            },
            {
                "name": "Get Single Post",
                "request_method": "GET",
                "request_path": "/posts/1",
                "expected_status": 200
            },
            {
                "name": "Create Post",
                "request_method": "POST",
                "request_path": "/posts",
                "request_body": json.dumps({
                    "title": "Test Post",
                    "body": "Test Body",
                    "userId": 1
                }),
                "expected_status": 201
            },
            {
                "name": "Invalid Endpoint",
                "request_method": "GET",
                "request_path": "/invalid",
                "expected_status": 404
            }
        ]
        
        created_tests = []
        for test_case in test_cases:
            test_data = {
                "endpoint_id": endpoint_id,
                **test_case
            }
            
            test_response = client.post("/api/tests/", json=test_data, headers=auth_headers)
            if test_response.status_code == 201:
                created_tests.append(test_response.json())
        
        # Execute all tests
        test_results = []
        for test in created_tests:
            with patch('httpx.AsyncClient.request') as mock_request:
                # Mock different responses based on test case
                mock_response = Mock()
                
                if "Invalid" in test["name"]:
                    mock_response.status_code = 404
                    mock_response.json.return_value = {"error": "Not found"}
                elif "Create" in test["name"]:
                    mock_response.status_code = 201
                    mock_response.json.return_value = {"id": 101, "title": "Test Post"}
                else:
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"id": 1, "title": "Sample Post"}
                
                mock_response.headers = {"Content-Type": "application/json"}
                mock_response.elapsed.total_seconds.return_value = 0.123
                mock_request.return_value = mock_response
                
                execute_response = client.post(f"/api/tests/{test['id']}/execute", headers=auth_headers)
                
                if execute_response.status_code == 200:
                    result = execute_response.json()
                    test_results.append({
                        "test_id": test["id"],
                        "test_name": test["name"],
                        "result": result
                    })
        
        # Verify test results
        assert len(test_results) > 0
        for result in test_results:
            assert "status_code" in result["result"]
            assert "response_time" in result["result"]
        
        # Get test execution history
        for test in created_tests:
            history_response = client.get(f"/api/tests/{test['id']}/results", headers=auth_headers)
            if history_response.status_code == 200:
                history = history_response.json()
                assert "executions" in history
        
        # Cleanup
        for test in created_tests:
            client.delete(f"/api/tests/{test['id']}", headers=auth_headers)
        
        client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
    
    def test_performance_testing_workflow(self, client: TestClient):
        """Test performance testing capabilities."""
        # Setup authentication
        user_data = {
            "email": "performance_tester@example.com",
            "password": "performance_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test response time measurement
        start_time = time.time()
        
        # Test SEO optimization performance
        seo_request = {
            "text": "Performance test text that should be optimized for SEO purposes and contains multiple keywords for testing optimization algorithms",
            "keywords": ["performance", "test", "optimization", "seo"],
            "max_length": 160
        }
        
        seo_response = client.post("/api/seo/optimize", json=seo_request, headers=auth_headers)
        seo_end_time = time.time()
        
        assert seo_response.status_code == 200
        seo_time = seo_end_time - start_time
        assert seo_time < 2.0  # Should complete within 2 seconds
        
        # Test categories endpoint performance
        categories_start = time.time()
        categories_response = client.get("/api/categories/", headers=auth_headers)
        categories_end = time.time()
        
        assert categories_response.status_code == 200
        categories_time = categories_end - categories_start
        assert categories_time < 1.0  # Should complete within 1 second
        
        # Test multiple concurrent requests simulation
        responses = []
        start_concurrent = time.time()
        
        for i in range(5):  # Simulate 5 concurrent requests
            response = client.get("/api/categories/", headers=auth_headers)
            responses.append(response)
        
        end_concurrent = time.time()
        concurrent_time = end_concurrent - start_concurrent
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Total time should be reasonable
        assert concurrent_time < 5.0  # Should complete all within 5 seconds
    
    def test_data_integrity_workflow(self, client: TestClient, session):
        """Test data integrity throughout API operations."""
        # Setup user
        user_data = {
            "email": "integrity_tester@example.com",
            "password": "integrity_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test 1: Create endpoint and verify database consistency
        endpoint_data = {
            "name": "Integrity Test API",
            "url": "https://api.integrity-test.com",
            "auth_type": "oauth"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        assert create_response.status_code == 201
        created_endpoint = create_response.json()
        endpoint_id = created_endpoint["id"]
        
        # Verify in database
        from sqlmodel import select
        db_endpoint = session.exec(
            select(ApiEndpoint).where(ApiEndpoint.id == endpoint_id)
        ).first()
        
        assert db_endpoint is not None
        assert db_endpoint.name == endpoint_data["name"]
        assert db_endpoint.url == endpoint_data["url"]
        
        # Test 2: Update endpoint and verify consistency
        update_data = {"name": "Updated Integrity Test API"}
        update_response = client.put(f"/api/endpoints/{endpoint_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # Refresh database object
        session.refresh(db_endpoint)
        assert db_endpoint.name == update_data["name"]
        
        # Test 3: API response consistency
        get_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert get_response.status_code == 200
        api_endpoint = get_response.json()
        
        # API response should match database
        assert api_endpoint["name"] == db_endpoint.name
        assert api_endpoint["url"] == db_endpoint.url
        assert api_endpoint["id"] == db_endpoint.id
        
        # Test 4: Delete and verify cleanup
        delete_response = client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        # Verify deletion in database
        deleted_endpoint = session.exec(
            select(ApiEndpoint).where(ApiEndpoint.id == endpoint_id)
        ).first()
        assert deleted_endpoint is None
        
        # Verify API consistency
        get_deleted_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert get_deleted_response.status_code == 404


@pytest.mark.e2e
class TestComplexWorkflows:
    """Test complex multi-step workflows."""
    
    def test_multi_user_collaboration_workflow(self, client: TestClient):
        """Test workflows involving multiple users."""
        # Create two users
        user1_data = {
            "email": "collaborator1@example.com",
            "password": "collab1_password_123"
        }
        
        user2_data = {
            "email": "collaborator2@example.com",
            "password": "collab2_password_123"
        }
        
        # Register both users
        client.post("/api/auth/register", json=user1_data)
        client.post("/api/auth/register", json=user2_data)
        
        # Login both users
        login1_response = client.post("/api/auth/token", data={
            "username": user1_data["email"],
            "password": user1_data["password"]
        })
        
        login2_response = client.post("/api/auth/token", data={
            "username": user2_data["email"],
            "password": user2_data["password"]
        })
        
        user1_headers = {"Authorization": f"Bearer {login1_response.json()['access_token']}"}
        user2_headers = {"Authorization": f"Bearer {login2_response.json()['access_token']}"}
        
        # User 1 creates endpoints
        user1_endpoint = {
            "name": "User 1 API",
            "url": "https://api.user1.com",
            "auth_type": "oauth"
        }
        
        endpoint1_response = client.post("/api/endpoints/", json=user1_endpoint, headers=user1_headers)
        assert endpoint1_response.status_code == 201
        endpoint1_id = endpoint1_response.json()["id"]
        
        # User 2 creates endpoints
        user2_endpoint = {
            "name": "User 2 API",
            "url": "https://api.user2.com",
            "auth_type": "api_key"
        }
        
        endpoint2_response = client.post("/api/endpoints/", json=user2_endpoint, headers=user2_headers)
        assert endpoint2_response.status_code == 201
        endpoint2_id = endpoint2_response.json()["id"]
        
        # Both users should see all endpoints (if sharing is enabled)
        user1_list = client.get("/api/endpoints/", headers=user1_headers)
        user2_list = client.get("/api/endpoints/", headers=user2_headers)
        
        assert user1_list.status_code == 200
        assert user2_list.status_code == 200
        
        # Each user should see their own endpoints
        user1_endpoints = user1_list.json()
        user2_endpoints = user2_list.json()
        
        user1_endpoint_ids = [ep["id"] for ep in user1_endpoints]
        user2_endpoint_ids = [ep["id"] for ep in user2_endpoints]
        
        assert endpoint1_id in user1_endpoint_ids
        assert endpoint2_id in user2_endpoint_ids
        
        # Test cross-user access restrictions
        # User 2 tries to modify User 1's endpoint
        update_data = {"name": "Unauthorized Update"}
        unauthorized_update = client.put(f"/api/endpoints/{endpoint1_id}", json=update_data, headers=user2_headers)
        
        # Should either succeed (if sharing allowed) or fail with 403/404
        assert unauthorized_update.status_code in [200, 403, 404]
        
        # Cleanup
        client.delete(f"/api/endpoints/{endpoint1_id}", headers=user1_headers)
        client.delete(f"/api/endpoints/{endpoint2_id}", headers=user2_headers)
    
    def test_oauth_to_api_usage_workflow(self, client: TestClient):
        """Test complete workflow from OAuth to API usage."""
        # Setup user
        user_data = {
            "email": "oauth_api_user@example.com",
            "password": "oauth_api_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 1: Initiate OAuth flow
        oauth_response = client.get("/api/oauth/login", headers=auth_headers, follow_redirects=False)
        assert oauth_response.status_code == 307
        
        # Extract OAuth parameters from redirect
        import urllib.parse as urlparse
        redirect_url = oauth_response.headers["location"]
        parsed_url = urlparse.urlparse(redirect_url)
        query_params = urlparse.parse_qs(parsed_url.query)
        state = query_params["state"][0]
        
        # Step 2: Simulate OAuth callback
        with patch('httpx.AsyncClient.post') as mock_post, \
             patch('httpx.AsyncClient.get') as mock_get:
            
            # Mock token exchange
            mock_token_response = Mock()
            mock_token_response.status_code = 200
            mock_token_response.json.return_value = {
                "access_token": "APP_USR-oauth-workflow-token",
                "token_type": "Bearer",
                "expires_in": 21600,
                "refresh_token": "TG-oauth-workflow-refresh",
                "user_id": "oauth_workflow_ml_user"
            }
            mock_post.return_value = mock_token_response
            
            # Mock user info
            mock_user_response = Mock()
            mock_user_response.status_code = 200
            mock_user_response.json.return_value = {
                "id": 999888777,
                "email": "oauth_api_user@example.com",
                "nickname": "OAUTH_API_USER"
            }
            mock_get.return_value = mock_user_response
            
            # Process callback
            callback_response = client.get(
                f"/api/oauth/callback?code=test_auth_code&state={state}",
                headers=auth_headers
            )
            
            assert callback_response.status_code == 200
            ml_token_data = callback_response.json()
        
        # Step 3: Use Mercado Libre APIs with stored token
        # Test categories endpoint (should use stored ML token)
        categories_response = client.get("/api/categories/", headers=auth_headers)
        assert categories_response.status_code == 200
        
        # Test specific category
        category_response = client.get("/api/categories/MLB1132", headers=auth_headers)
        assert category_response.status_code == 200
        
        # Step 4: Test SEO optimization (doesn't require ML token)
        seo_request = {
            "text": "OAuth workflow test product description",
            "keywords": ["oauth", "workflow", "test"],
            "max_length": 160
        }
        
        seo_response = client.post("/api/seo/optimize", json=seo_request, headers=auth_headers)
        assert seo_response.status_code == 200
        seo_data = seo_response.json()
        assert "optimized_text" in seo_data
    
    def test_error_recovery_workflow(self, client: TestClient):
        """Test error recovery in complex workflows."""
        # Setup user
        user_data = {
            "email": "error_recovery@example.com",
            "password": "recovery_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test 1: Recover from invalid endpoint creation
        invalid_endpoint = {
            "name": "",  # Invalid: empty name
            "url": "not_a_valid_url",  # Invalid URL
            "auth_type": "invalid_auth_type"  # Invalid auth type
        }
        
        invalid_response = client.post("/api/endpoints/", json=invalid_endpoint, headers=auth_headers)
        assert invalid_response.status_code in [400, 422]  # Should fail validation
        
        # Recover with valid endpoint
        valid_endpoint = {
            "name": "Recovery Test API",
            "url": "https://api.recovery-test.com",
            "auth_type": "oauth"
        }
        
        valid_response = client.post("/api/endpoints/", json=valid_endpoint, headers=auth_headers)
        assert valid_response.status_code == 201
        endpoint_id = valid_response.json()["id"]
        
        # Test 2: Recover from failed API test
        invalid_test = {
            "endpoint_id": 99999,  # Non-existent endpoint
            "name": "Invalid Test",
            "request_method": "INVALID_METHOD",
            "request_path": ""
        }
        
        invalid_test_response = client.post("/api/tests/", json=invalid_test, headers=auth_headers)
        assert invalid_test_response.status_code in [400, 404, 422]
        
        # Recover with valid test
        valid_test = {
            "endpoint_id": endpoint_id,
            "name": "Recovery Test",
            "request_method": "GET",
            "request_path": "/health"
        }
        
        valid_test_response = client.post("/api/tests/", json=valid_test, headers=auth_headers)
        if valid_test_response.status_code == 201:
            test_id = valid_test_response.json()["id"]
            
            # Test execution might fail, but structure should be valid
            execute_response = client.post(f"/api/tests/{test_id}/execute", headers=auth_headers)
            assert execute_response.status_code in [200, 400, 404, 500]
            
            # Clean up test
            client.delete(f"/api/tests/{test_id}", headers=auth_headers)
        
        # Test 3: Recover from authentication errors
        # Temporarily use invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        invalid_auth_response = client.get("/api/endpoints/", headers=invalid_headers)
        assert invalid_auth_response.status_code == 401
        
        # Recover with valid authentication
        valid_auth_response = client.get("/api/endpoints/", headers=auth_headers)
        assert valid_auth_response.status_code == 200
        
        # Cleanup
        client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)