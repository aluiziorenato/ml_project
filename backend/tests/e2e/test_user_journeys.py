"""
End-to-end tests for complete user journeys and API workflows.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from sqlmodel import Session, select

from app.models import User, ApiEndpoint, OAuthToken, MeliToken


@pytest.mark.e2e
class TestCompleteUserJourneys:
    """Test complete user journeys from registration to API usage."""
    
    def test_user_registration_to_api_usage_journey(self, client: TestClient):
        """Test complete user journey from registration to authenticated API usage."""
        # Step 1: User Registration
        registration_data = {
            "email": "journey_user@example.com",
            "password": "secure_password_123"
        }
        
        register_response = client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code == 201
        register_data = register_response.json()
        assert register_data["email"] == registration_data["email"]
        assert "id" in register_data
        
        # Step 2: User Login
        login_data = {
            "username": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = client.post("/api/auth/token", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Step 3: Use API with authentication
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test SEO optimization endpoint
        seo_request = {
            "text": "Premium wireless headphones with excellent sound quality and long battery life",
            "keywords": ["wireless", "headphones", "premium"],
            "max_length": 160
        }
        
        seo_response = client.post("/api/seo/optimize", json=seo_request, headers=auth_headers)
        assert seo_response.status_code == 200
        seo_data = seo_response.json()
        assert "optimized_text" in seo_data
        assert "meta_description" in seo_data
        assert "keywords" in seo_data
        
        # Test categories endpoint
        categories_response = client.get("/api/categories/", headers=auth_headers)
        assert categories_response.status_code == 200
        categories_data = categories_response.json()
        assert isinstance(categories_data, list)
        
        # Test specific category details
        if categories_data:
            category_id = categories_data[0]["id"]
            category_details_response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
            assert category_details_response.status_code == 200
    
    def test_oauth_integration_journey(self, client: TestClient, session: Session):
        """Test complete OAuth integration journey."""
        # Step 1: Create authenticated user
        user_data = {
            "email": "oauth_journey@example.com",
            "password": "oauth_password_123"
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
        
        # Step 2: Initiate OAuth flow
        oauth_login_response = client.get("/api/oauth/login", headers=auth_headers, follow_redirects=False)
        assert oauth_login_response.status_code == 307  # Redirect to ML
        
        redirect_url = oauth_login_response.headers["location"]
        assert "auth.mercadolibre.com.br" in redirect_url
        assert "client_id=" in redirect_url
        assert "state=" in redirect_url
        assert "code_challenge=" in redirect_url
        
        # Extract state from redirect URL
        import urllib.parse as urlparse
        parsed_url = urlparse.urlparse(redirect_url)
        query_params = urlparse.parse_qs(parsed_url.query)
        state = query_params["state"][0]
        
        # Step 3: Simulate OAuth callback (would normally come from ML)
        callback_params = {
            "code": "test_authorization_code",
            "state": state
        }
        
        with patch('httpx.AsyncClient.post') as mock_post, \
             patch('httpx.AsyncClient.get') as mock_get:
            
            # Mock token exchange response
            mock_token_response = Mock()
            mock_token_response.status_code = 200
            mock_token_response.json.return_value = {
                "access_token": "APP_USR-oauth-journey-token",
                "token_type": "Bearer",
                "expires_in": 21600,
                "refresh_token": "TG-oauth-journey-refresh",
                "user_id": "oauth_journey_ml_id"
            }
            mock_post.return_value = mock_token_response
            
            # Mock user info response
            mock_user_response = Mock()
            mock_user_response.status_code = 200
            mock_user_response.json.return_value = {
                "id": 987654321,
                "email": "oauth_journey@example.com",
                "nickname": "OAUTH_JOURNEY_USER",
                "country_id": "BR"
            }
            mock_get.return_value = mock_user_response
            
            # Process callback
            callback_response = client.get(
                f"/api/oauth/callback?code={callback_params['code']}&state={callback_params['state']}",
                headers=auth_headers
            )
            
            assert callback_response.status_code == 200
            callback_data = callback_response.json()
            assert "access_token" in callback_data
            assert callback_data["token_type"] == "Bearer"
    
    def test_api_endpoint_management_journey(self, client: TestClient):
        """Test complete API endpoint management journey."""
        # Step 1: Create user and authenticate
        user_data = {
            "email": "endpoint_manager@example.com",
            "password": "endpoint_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 2: Create new endpoint
        endpoint_data = {
            "name": "Test API Endpoint",
            "url": "https://api.test-endpoint.com",
            "auth_type": "oauth",
            "oauth_scope": "read write"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        assert create_response.status_code == 201
        created_endpoint = create_response.json()
        assert created_endpoint["name"] == endpoint_data["name"]
        assert created_endpoint["url"] == endpoint_data["url"]
        endpoint_id = created_endpoint["id"]
        
        # Step 3: List all endpoints
        list_response = client.get("/api/endpoints/", headers=auth_headers)
        assert list_response.status_code == 200
        endpoints_list = list_response.json()
        assert len(endpoints_list) >= 1
        assert any(ep["id"] == endpoint_id for ep in endpoints_list)
        
        # Step 4: Get specific endpoint
        get_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert get_response.status_code == 200
        endpoint_details = get_response.json()
        assert endpoint_details["id"] == endpoint_id
        assert endpoint_details["name"] == endpoint_data["name"]
        
        # Step 5: Update endpoint
        update_data = {
            "name": "Updated Test API Endpoint",
            "url": "https://api.updated-endpoint.com"
        }
        
        update_response = client.put(f"/api/endpoints/{endpoint_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200
        updated_endpoint = update_response.json()
        assert updated_endpoint["name"] == update_data["name"]
        assert updated_endpoint["url"] == update_data["url"]
        
        # Step 6: Delete endpoint
        delete_response = client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["deleted"] is True
        
        # Step 7: Verify deletion
        get_deleted_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert get_deleted_response.status_code == 404


@pytest.mark.e2e
class TestAPILifecycleTesting:
    """Test complete API lifecycle including CRUD operations."""
    
    def test_api_test_lifecycle(self, client: TestClient):
        """Test complete API test lifecycle."""
        # Setup: Create user and authenticate
        user_data = {
            "email": "api_tester@example.com",
            "password": "tester_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 1: Create API endpoint for testing
        endpoint_data = {
            "name": "Test Target API",
            "url": "https://jsonplaceholder.typicode.com",
            "auth_type": "none"
        }
        
        endpoint_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = endpoint_response.json()["id"]
        
        # Step 2: Create API test
        test_data = {
            "endpoint_id": endpoint_id,
            "name": "Get Posts Test",
            "request_method": "GET",
            "request_path": "/posts/1",
            "expected_status": 200
        }
        
        test_response = client.post("/api/tests/", json=test_data, headers=auth_headers)
        assert test_response.status_code == 201
        created_test = test_response.json()
        test_id = created_test["id"]
        
        # Step 3: Execute API test
        execute_response = client.post(f"/api/tests/{test_id}/execute", headers=auth_headers)
        assert execute_response.status_code == 200
        execution_result = execute_response.json()
        assert "status_code" in execution_result
        assert "response_time" in execution_result
        
        # Step 4: Get test results
        results_response = client.get(f"/api/tests/{test_id}/results", headers=auth_headers)
        assert results_response.status_code == 200
        results = results_response.json()
        assert "executions" in results
        
        # Step 5: Clean up
        client.delete(f"/api/tests/{test_id}", headers=auth_headers)
        client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
    
    def test_proxy_api_functionality(self, client: TestClient):
        """Test proxy API functionality for external API calls."""
        # Setup authentication
        user_data = {
            "email": "proxy_user@example.com",
            "password": "proxy_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Create endpoint for proxying
        endpoint_data = {
            "name": "Proxy Test API",
            "url": "https://httpbin.org",
            "auth_type": "none"
        }
        
        endpoint_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = endpoint_response.json()["id"]
        
        # Test proxy functionality
        proxy_data = {
            "endpoint_id": endpoint_id,
            "method": "GET",
            "path": "/get"
        }
        
        with patch('httpx.AsyncClient.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.json.return_value = {"origin": "127.0.0.1", "url": "https://httpbin.org/get"}
            mock_request.return_value = mock_response
            
            proxy_response = client.post("/api/proxy", json=proxy_data, headers=auth_headers)
            
        assert proxy_response.status_code == 200
        proxy_result = proxy_response.json()
        assert "status_code" in proxy_result
        assert "headers" in proxy_result
        assert "body" in proxy_result


@pytest.mark.e2e
class TestAuthenticationFlows:
    """Test various authentication flows end-to-end."""
    
    def test_registration_validation_flow(self, client: TestClient):
        """Test user registration with various validation scenarios."""
        # Test successful registration
        valid_data = {
            "email": "valid_user@example.com",
            "password": "valid_password_123"
        }
        
        response = client.post("/api/auth/register", json=valid_data)
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["email"] == valid_data["email"]
        assert "password" not in user_data  # Password should not be returned
        
        # Test duplicate email registration
        duplicate_response = client.post("/api/auth/register", json=valid_data)
        assert duplicate_response.status_code == 400
        error_data = duplicate_response.json()
        assert "already registered" in error_data["detail"].lower()
        
        # Test invalid email format
        invalid_email_data = {
            "email": "invalid_email_format",
            "password": "valid_password_123"
        }
        
        invalid_response = client.post("/api/auth/register", json=invalid_email_data)
        assert invalid_response.status_code == 422  # Validation error
        
        # Test weak password
        weak_password_data = {
            "email": "weak_password@example.com",
            "password": "123"
        }
        
        weak_response = client.post("/api/auth/register", json=weak_password_data)
        # Note: Depending on validation rules, this might be 400 or 422
        assert weak_response.status_code in [400, 422]
    
    def test_login_scenarios_flow(self, client: TestClient):
        """Test various login scenarios."""
        # Setup: Register a user
        user_data = {
            "email": "login_test@example.com",
            "password": "login_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        
        # Test successful login
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        success_response = client.post("/api/auth/token", data=login_data)
        assert success_response.status_code == 200
        token_data = success_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Test invalid password
        invalid_password_data = {
            "username": user_data["email"],
            "password": "wrong_password"
        }
        
        invalid_response = client.post("/api/auth/token", data=invalid_password_data)
        assert invalid_response.status_code == 401
        
        # Test non-existent user
        nonexistent_data = {
            "username": "nonexistent@example.com",
            "password": "any_password"
        }
        
        nonexistent_response = client.post("/api/auth/token", data=nonexistent_data)
        assert nonexistent_response.status_code == 401
        
        # Test missing credentials
        missing_response = client.post("/api/auth/token", data={})
        assert missing_response.status_code == 422  # Validation error
    
    def test_token_validation_flow(self, client: TestClient):
        """Test token validation in protected endpoints."""
        # Step 1: Create user and get token
        user_data = {
            "email": "token_validation@example.com",
            "password": "token_password_123"
        }
        
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        
        token_data = login_response.json()
        valid_token = token_data["access_token"]
        
        # Step 2: Test access with valid token
        valid_headers = {"Authorization": f"Bearer {valid_token}"}
        valid_response = client.get("/api/categories/", headers=valid_headers)
        assert valid_response.status_code == 200
        
        # Step 3: Test access without token
        no_token_response = client.get("/api/categories/")
        assert no_token_response.status_code == 401
        
        # Step 4: Test access with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        invalid_response = client.get("/api/categories/", headers=invalid_headers)
        assert invalid_response.status_code == 401
        
        # Step 5: Test access with malformed authorization header
        malformed_headers = {"Authorization": "Invalid format"}
        malformed_response = client.get("/api/categories/", headers=malformed_headers)
        assert malformed_response.status_code == 401


@pytest.mark.e2e
class TestErrorHandlingFlows:
    """Test error handling across different endpoints and scenarios."""
    
    def test_validation_error_consistency(self, client: TestClient, auth_headers: dict):
        """Test that validation errors are consistent across endpoints."""
        validation_test_cases = [
            # SEO endpoint validation
            ("/api/seo/optimize", "POST", {"keywords": ["test"]}, 422),  # Missing text
            ("/api/seo/optimize", "POST", {"text": ""}, 422),  # Empty text
            
            # Auth endpoint validation
            ("/api/auth/register", "POST", {"email": "invalid-email"}, 422),  # Invalid email
            ("/api/auth/token", "POST", {"username": "test"}, 422),  # Missing password
        ]
        
        for endpoint, method, invalid_data, expected_status in validation_test_cases:
            if endpoint.startswith("/api/seo/") or endpoint.startswith("/api/categories/"):
                headers = auth_headers
            else:
                headers = {}
            
            if method == "POST":
                if endpoint == "/api/auth/token":
                    response = client.post(endpoint, data=invalid_data, headers=headers)
                else:
                    response = client.post(endpoint, json=invalid_data, headers=headers)
            
            assert response.status_code == expected_status
            assert "detail" in response.json()
    
    def test_error_response_format_consistency(self, client: TestClient):
        """Test that error responses have consistent format."""
        # Test 404 errors
        not_found_response = client.get("/api/nonexistent/endpoint")
        assert not_found_response.status_code == 404
        not_found_data = not_found_response.json()
        assert "detail" in not_found_data
        
        # Test 401 errors
        unauthorized_response = client.get("/api/categories/")
        assert unauthorized_response.status_code == 401
        unauthorized_data = unauthorized_response.json()
        assert "detail" in unauthorized_data
        
        # Test 422 validation errors
        validation_response = client.post("/api/auth/register", json={"invalid": "data"})
        assert validation_response.status_code == 422
        validation_data = validation_response.json()
        assert "detail" in validation_data
    
    def test_rate_limiting_simulation(self, client: TestClient, auth_headers: dict):
        """Test simulated rate limiting behavior."""
        # Make multiple rapid requests to the same endpoint
        endpoint = "/api/categories/"
        
        responses = []
        for i in range(10):  # Make 10 rapid requests
            response = client.get(endpoint, headers=auth_headers)
            responses.append(response)
        
        # All requests should succeed (no rate limiting implemented yet)
        # But this test validates the endpoint can handle rapid requests
        for response in responses:
            assert response.status_code == 200
    
    def test_large_payload_handling(self, client: TestClient, auth_headers: dict):
        """Test handling of large payloads."""
        # Test SEO optimization with very large text
        large_text = "word " * 10000  # Very large text
        large_payload = {
            "text": large_text,
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=large_payload, headers=auth_headers)
        # Should handle large payloads gracefully
        assert response.status_code in [200, 413]  # Success or payload too large
        
        if response.status_code == 200:
            data = response.json()
            assert "optimized_text" in data
            assert len(data["optimized_text"]["meta_description"]) <= 160