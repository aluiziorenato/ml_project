"""
Unit tests for API routers.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json


@pytest.mark.unit
class TestAuthRouter:
    """Test authentication router endpoints."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "email": "router_test@example.com",
            "password": "router_password_123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email."""
        user_data = {
            "email": "duplicate_router@example.com",
            "password": "password123"
        }
        
        # Register first time
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to register again
        response2 = client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_login_success(self, client: TestClient):
        """Test successful login."""
        # Register user first
        user_data = {
            "email": "login_test@example.com",
            "password": "login_password_123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Login
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields."""
        # Missing password
        response1 = client.post("/api/auth/token", data={"username": "test@example.com"})
        assert response1.status_code == 422
        
        # Missing username
        response2 = client.post("/api/auth/token", data={"password": "password"})
        assert response2.status_code == 422


@pytest.mark.unit
class TestSEORouter:
    """Test SEO router endpoints."""
    
    def test_optimize_success(self, client: TestClient, auth_headers: dict):
        """Test successful SEO optimization."""
        request_data = {
            "text": "Router test product description for SEO optimization",
            "keywords": ["router", "test", "seo"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "optimized_text" in data
        
        optimized = data["optimized_text"]
        assert "original" in optimized
        assert "cleaned" in optimized
        assert "title" in optimized
        assert "meta_description" in optimized
        assert "keywords" in optimized
        assert "slug" in optimized
    
    def test_optimize_unauthorized(self, client: TestClient):
        """Test SEO optimization without authentication."""
        request_data = {
            "text": "Unauthorized test",
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data)
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_optimize_invalid_token(self, client: TestClient):
        """Test SEO optimization with invalid token."""
        request_data = {
            "text": "Invalid token test",
            "max_length": 160
        }
        
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/seo/optimize", json=request_data, headers=headers)
        
        assert response.status_code == 401
    
    def test_optimize_missing_text(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with missing text."""
        request_data = {
            "keywords": ["test"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_optimize_empty_text(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with empty text."""
        request_data = {
            "text": "",
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_optimize_invalid_max_length(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with invalid max_length."""
        request_data = {
            "text": "Valid text",
            "max_length": -1
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 400
    
    @patch('app.services.seo.optimize_text')
    def test_optimize_service_error(self, mock_optimize, client: TestClient, auth_headers: dict):
        """Test SEO optimization with service error."""
        mock_optimize.side_effect = Exception("Service error")
        
        request_data = {
            "text": "Service error test",
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 500
        assert "detail" in response.json()


@pytest.mark.unit
class TestCategoriesRouter:
    """Test categories router endpoints."""
    
    @patch('httpx.AsyncClient.get')
    def test_list_categories_success(self, mock_get, client: TestClient, auth_headers: dict):
        """Test successful categories listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "MLB1132", "name": "Telefones e Celulares"},
            {"id": "MLB1144", "name": "Eletrodomésticos"}
        ]
        mock_get.return_value = mock_response
        
        response = client.get("/api/categories/", headers=auth_headers)
        
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) == 2
        assert categories[0]["id"] == "MLB1132"
    
    def test_list_categories_unauthorized(self, client: TestClient):
        """Test categories listing without authentication."""
        response = client.get("/api/categories/")
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    @patch('httpx.AsyncClient.get')
    def test_get_category_success(self, mock_get, client: TestClient, auth_headers: dict):
        """Test successful category details retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "MLB1132",
            "name": "Telefones e Celulares",
            "settings": {
                "listing_allowed": True,
                "has_picture": True
            }
        }
        mock_get.return_value = mock_response
        
        response = client.get("/api/categories/MLB1132", headers=auth_headers)
        
        assert response.status_code == 200
        category = response.json()
        assert category["id"] == "MLB1132"
        assert category["name"] == "Telefones e Celulares"
        assert "settings" in category
    
    @patch('httpx.AsyncClient.get')
    def test_get_category_not_found(self, mock_get, client: TestClient, auth_headers: dict):
        """Test category details with invalid category ID."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Category not found"}
        mock_get.return_value = mock_response
        
        response = client.get("/api/categories/INVALID", headers=auth_headers)
        
        assert response.status_code == 404
    
    @patch('httpx.AsyncClient.get')
    def test_categories_external_api_error(self, mock_get, client: TestClient, auth_headers: dict):
        """Test categories with external API error."""
        mock_get.side_effect = Exception("External API error")
        
        response = client.get("/api/categories/", headers=auth_headers)
        
        assert response.status_code >= 400
        assert "detail" in response.json()


@pytest.mark.unit
class TestOAuthRouter:
    """Test OAuth router endpoints."""
    
    def test_oauth_login_redirect(self, client: TestClient, auth_headers: dict):
        """Test OAuth login redirects properly."""
        response = client.get("/api/oauth/login", headers=auth_headers, follow_redirects=False)
        
        assert response.status_code == 307
        assert "location" in response.headers
        
        location = response.headers["location"]
        assert "auth.mercadolibre.com.br" in location
        assert "client_id=" in location
        assert "state=" in location
        assert "code_challenge=" in location
    
    def test_oauth_login_with_state(self, client: TestClient, auth_headers: dict):
        """Test OAuth login with custom state parameter."""
        state = "custom_state_123"
        response = client.get(f"/api/oauth/login?state={state}", headers=auth_headers, follow_redirects=False)
        
        assert response.status_code == 307
        location = response.headers["location"]
        assert f"state={state}" in location
    
    def test_oauth_login_unauthorized(self, client: TestClient):
        """Test OAuth login without authentication."""
        response = client.get("/api/oauth/login")
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_oauth_callback_missing_params(self, client: TestClient, auth_headers: dict):
        """Test OAuth callback with missing parameters."""
        # Missing code parameter
        response1 = client.get("/api/oauth/callback?state=test", headers=auth_headers)
        assert response1.status_code == 400
        assert "detail" in response1.json()
        
        # Missing state parameter
        response2 = client.get("/api/oauth/callback?code=test", headers=auth_headers)
        assert response2.status_code == 400
        assert "detail" in response2.json()
    
    def test_oauth_callback_invalid_state(self, client: TestClient, auth_headers: dict):
        """Test OAuth callback with invalid state."""
        response = client.get("/api/oauth/callback?code=test&state=invalid", headers=auth_headers)
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.get')
    def test_oauth_callback_success(self, mock_get, mock_post, client: TestClient, auth_headers: dict, mock_ml_token, mock_ml_user_info):
        """Test successful OAuth callback."""
        # First, initiate OAuth to get state
        oauth_response = client.get("/api/oauth/login", headers=auth_headers, follow_redirects=False)
        location = oauth_response.headers["location"]
        
        # Extract state from URL
        import urllib.parse as urlparse
        parsed_url = urlparse.urlparse(location)
        query_params = urlparse.parse_qs(parsed_url.query)
        state = query_params["state"][0]
        
        # Mock token exchange
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = mock_ml_token
        mock_post.return_value = mock_token_response
        
        # Mock user info
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = mock_ml_user_info
        mock_get.return_value = mock_user_response
        
        # Process callback
        response = client.get(f"/api/oauth/callback?code=test_code&state={state}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


@pytest.mark.unit
class TestApiEndpointsRouter:
    """Test API endpoints router."""
    
    def test_create_endpoint(self, client: TestClient, auth_headers: dict):
        """Test endpoint creation."""
        endpoint_data = {
            "name": "Router Test API",
            "url": "https://api.routertest.com",
            "auth_type": "oauth"
        }
        
        response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == endpoint_data["name"]
        assert data["url"] == endpoint_data["url"]
        assert "id" in data
    
    def test_create_endpoint_validation_error(self, client: TestClient, auth_headers: dict):
        """Test endpoint creation with validation errors."""
        # Missing name
        invalid_data1 = {"url": "https://api.test.com"}
        response1 = client.post("/api/endpoints/", json=invalid_data1, headers=auth_headers)
        assert response1.status_code == 422
        
        # Missing URL
        invalid_data2 = {"name": "Test API"}
        response2 = client.post("/api/endpoints/", json=invalid_data2, headers=auth_headers)
        assert response2.status_code == 422
    
    def test_list_endpoints(self, client: TestClient, auth_headers: dict):
        """Test listing endpoints."""
        # Create an endpoint first
        endpoint_data = {
            "name": "List Test API",
            "url": "https://api.listtest.com"
        }
        client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        
        # List endpoints
        response = client.get("/api/endpoints/", headers=auth_headers)
        
        assert response.status_code == 200
        endpoints = response.json()
        assert isinstance(endpoints, list)
        assert len(endpoints) >= 1
    
    def test_get_endpoint(self, client: TestClient, auth_headers: dict):
        """Test getting specific endpoint."""
        # Create endpoint first
        endpoint_data = {
            "name": "Get Test API",
            "url": "https://api.gettest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = create_response.json()["id"]
        
        # Get endpoint
        response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == endpoint_id
        assert data["name"] == endpoint_data["name"]
    
    def test_get_endpoint_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent endpoint."""
        response = client.get("/api/endpoints/999999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_update_endpoint(self, client: TestClient, auth_headers: dict):
        """Test updating endpoint."""
        # Create endpoint first
        endpoint_data = {
            "name": "Update Test API",
            "url": "https://api.updatetest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = create_response.json()["id"]
        
        # Update endpoint
        update_data = {
            "name": "Updated Test API",
            "url": "https://api.updated.com"
        }
        
        response = client.put(f"/api/endpoints/{endpoint_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["url"] == update_data["url"]
    
    def test_update_endpoint_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent endpoint."""
        update_data = {"name": "Non-existent"}
        
        response = client.put("/api/endpoints/999999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_delete_endpoint(self, client: TestClient, auth_headers: dict):
        """Test deleting endpoint."""
        # Create endpoint first
        endpoint_data = {
            "name": "Delete Test API",
            "url": "https://api.deletetest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = create_response.json()["id"]
        
        # Delete endpoint
        response = client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
    
    def test_delete_endpoint_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent endpoint."""
        response = client.delete("/api/endpoints/999999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_endpoints_unauthorized(self, client: TestClient):
        """Test endpoints access without authentication."""
        # All endpoints operations should require authentication
        endpoints = [
            ("/api/endpoints/", "GET"),
            ("/api/endpoints/", "POST"),
            ("/api/endpoints/1", "GET"),
            ("/api/endpoints/1", "PUT"),
            ("/api/endpoints/1", "DELETE"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={"name": "Test", "url": "https://test.com"})
            elif method == "PUT":
                response = client.put(endpoint, json={"name": "Updated"})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code == 401, f"{method} {endpoint} should require authentication"


@pytest.mark.unit
class TestProxyRouter:
    """Test proxy router endpoints."""
    
    @patch('httpx.AsyncClient.request')
    def test_proxy_request_success(self, mock_request, client: TestClient, auth_headers: dict):
        """Test successful proxy request."""
        # Create endpoint first
        endpoint_data = {
            "name": "Proxy Test API",
            "url": "https://api.proxytest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = create_response.json()["id"]
        
        # Mock external API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response
        
        # Make proxy request
        proxy_data = {
            "endpoint_id": endpoint_id,
            "method": "GET",
            "path": "/test"
        }
        
        response = client.post("/api/proxy", json=proxy_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "status_code" in data
        assert "headers" in data
        assert "body" in data
    
    def test_proxy_request_unauthorized(self, client: TestClient):
        """Test proxy request without authentication."""
        proxy_data = {
            "endpoint_id": 1,
            "method": "GET",
            "path": "/test"
        }
        
        response = client.post("/api/proxy", json=proxy_data)
        
        assert response.status_code == 401
    
    def test_proxy_request_invalid_endpoint(self, client: TestClient, auth_headers: dict):
        """Test proxy request with invalid endpoint ID."""
        proxy_data = {
            "endpoint_id": 999999,
            "method": "GET",
            "path": "/test"
        }
        
        response = client.post("/api/proxy", json=proxy_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    @patch('httpx.AsyncClient.request')
    def test_proxy_request_external_error(self, mock_request, client: TestClient, auth_headers: dict):
        """Test proxy request with external API error."""
        # Create endpoint first
        endpoint_data = {
            "name": "Error Proxy Test API",
            "url": "https://api.errorproxytest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        endpoint_id = create_response.json()["id"]
        
        # Mock external API error
        mock_request.side_effect = Exception("External API error")
        
        # Make proxy request
        proxy_data = {
            "endpoint_id": endpoint_id,
            "method": "GET",
            "path": "/error"
        }
        
        response = client.post("/api/proxy", json=proxy_data, headers=auth_headers)
        
        assert response.status_code >= 400
        assert "detail" in response.json()


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health endpoint."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_health_check_methods(self, client: TestClient):
        """Test health endpoint only accepts GET."""
        # POST should not be allowed
        response_post = client.post("/health", json={})
        assert response_post.status_code in [404, 405]
        
        # PUT should not be allowed
        response_put = client.put("/health", json={})
        assert response_put.status_code in [404, 405]
        
        # DELETE should not be allowed
        response_delete = client.delete("/health")
        assert response_delete.status_code in [404, 405]