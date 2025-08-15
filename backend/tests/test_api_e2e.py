"""
End-to-end API tests for /login, /categories, /seo/optimize routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import httpx

from app.models import User


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "email": "new_user@example.com",
            "password": "securepassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
    
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,
            "password": "anotherpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_register_invalid_data(self, client: TestClient):
        """Test registration with invalid data."""
        # Missing password
        response = client.post("/api/auth/register", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Invalid email format
        response = client.post("/api/auth/register", json={
            "email": "not.an.email",  # Missing @ and domain
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Empty email
        response = client.post("/api/auth/register", json={
            "email": "",
            "password": "password123"
        })
        assert response.status_code == 422
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Test login with invalid credentials."""
        # Wrong password
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
        
        # Non-existent user
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_missing_data(self, client: TestClient):
        """Test login with missing data."""
        # Missing username
        response = client.post("/api/auth/token", data={"password": "password"})
        assert response.status_code == 422
        
        # Missing password
        response = client.post("/api/auth/token", data={"username": "test@example.com"})
        assert response.status_code == 422
        
        # Empty data
        response = client.post("/api/auth/token", data={})
        assert response.status_code == 422


class TestOAuthEndpoints:
    """Test OAuth endpoints."""
    
    def test_oauth_login_redirect(self, client: TestClient):
        """Test OAuth login redirects to Mercado Libre."""
        response = client.get("/api/oauth/login", follow_redirects=False)
        
        assert response.status_code == 307  # Redirect
        assert "auth.mercadolibre.com" in response.headers["location"]
    
    def test_oauth_login_with_state(self, client: TestClient):
        """Test OAuth login with custom state."""
        state = "custom_state_123"
        response = client.get(f"/api/oauth/login?state={state}", follow_redirects=False)
        
        assert response.status_code == 307
        location = response.headers["location"]
        assert f"state={state}" in location
    
    def test_oauth_callback_missing_params(self, client: TestClient, auth_headers: dict):
        """Test OAuth callback with missing parameters."""
        # Missing code
        response = client.get("/api/oauth/callback?state=test", headers=auth_headers)
        assert response.status_code == 400
        assert "Código ou estado ausente" in response.json()["detail"]
        
        # Missing state
        response = client.get("/api/oauth/callback?code=test", headers=auth_headers)
        assert response.status_code == 400
        assert "Código ou estado ausente" in response.json()["detail"]
    
    def test_oauth_callback_invalid_state(self, client: TestClient, auth_headers: dict):
        """Test OAuth callback with invalid state."""
        response = client.get("/api/oauth/callback?code=test&state=invalid", headers=auth_headers)
        assert response.status_code == 400
        assert "State inválido ou expirado" in response.json()["detail"]


class TestCategoriesEndpoints:
    """Test categories endpoints."""
    
    def test_get_categories_success(self, client: TestClient, auth_headers: dict):
        """Test successful categories retrieval."""
        response = client.get("/api/categories/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of first category
        category = data[0]
        assert "id" in category
        assert "name" in category
        assert isinstance(category["id"], str)
        assert isinstance(category["name"], str)
    
    def test_get_categories_unauthorized(self, client: TestClient):
        """Test categories endpoint without authentication."""
        response = client.get("/api/categories/")
        
        assert response.status_code == 401
    
    def test_get_categories_invalid_token(self, client: TestClient):
        """Test categories endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/categories/", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_category_details_success(self, client: TestClient, auth_headers: dict):
        """Test successful category details retrieval."""
        category_id = "MLB1132"
        response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert "name" in data
        assert "path_from_root" in data
        assert "settings" in data
        
        # Check path_from_root structure
        assert isinstance(data["path_from_root"], list)
        if data["path_from_root"]:
            path_item = data["path_from_root"][0]
            assert "id" in path_item
            assert "name" in path_item
    
    def test_get_category_details_unauthorized(self, client: TestClient):
        """Test category details endpoint without authentication."""
        response = client.get("/api/categories/MLB1132")
        
        assert response.status_code == 401
    
    def test_get_category_details_various_ids(self, client: TestClient, auth_headers: dict):
        """Test category details with various category IDs."""
        category_ids = ["MLB1132", "MLB1144", "MLB1196", "INVALID_ID"]
        
        for category_id in category_ids:
            response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
            
            # All should return 200 with our mock implementation
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == category_id


class TestSEOEndpoints:
    """Test SEO optimization endpoints."""
    
    def test_seo_optimize_success(self, client: TestClient, auth_headers: dict, sample_seo_text: str):
        """Test successful SEO optimization."""
        request_data = {
            "text": sample_seo_text,
            "keywords": ["product", "description", "SEO"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = ["original", "cleaned", "title", "meta_description", "keywords", "slug"]
        for field in required_fields:
            assert field in data
        
        # Check data types and constraints
        assert data["original"] == sample_seo_text
        assert isinstance(data["cleaned"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["meta_description"], str)
        assert isinstance(data["keywords"], list)
        assert isinstance(data["slug"], str)
        
        # Check length constraints
        assert len(data["title"]) <= 60
        assert len(data["meta_description"]) <= 160
        assert len(data["keywords"]) <= 8
        assert len(data["slug"]) <= 50
    
    def test_seo_optimize_minimal_request(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with minimal request data."""
        request_data = {
            "text": "Simple test text for optimization"
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original"] == request_data["text"]
    
    def test_seo_optimize_custom_max_length(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with custom max_length."""
        long_text = "This is a very long text that should be truncated according to the custom maximum length parameter specified in the request."
        request_data = {
            "text": long_text,
            "max_length": 50
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["meta_description"]) <= 50
    
    def test_seo_optimize_with_keywords(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with custom keywords."""
        request_data = {
            "text": "Smartphone with amazing camera and long battery life",
            "keywords": ["smartphone", "camera", "battery", "device"],  # Changed to use keywords that are in text
            "max_length": 120
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that some keywords are present in the result
        result_keywords_lower = [k.lower() for k in data["keywords"]]
        text_lower = data["cleaned"].lower()
        
        # At least one of the suggested keywords should be found
        found_keywords = 0
        for keyword in request_data["keywords"]:
            if keyword.lower() in result_keywords_lower or keyword.lower() in text_lower:
                found_keywords += 1
        
        assert found_keywords >= 3  # At least 3 of the 4 keywords should be found
    
    def test_seo_optimize_unauthorized(self, client: TestClient):
        """Test SEO optimization without authentication."""
        request_data = {
            "text": "Test text"
        }
        
        response = client.post("/api/seo/optimize", json=request_data)
        
        assert response.status_code == 401
    
    def test_seo_optimize_invalid_token(self, client: TestClient):
        """Test SEO optimization with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        request_data = {
            "text": "Test text"
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=headers)
        
        assert response.status_code == 401
    
    def test_seo_optimize_empty_text(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with empty text."""
        request_data = {
            "text": ""
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Text must be a non-empty string" in response.json()["detail"]
    
    def test_seo_optimize_invalid_max_length(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with invalid max_length."""
        request_data = {
            "text": "Test text",
            "max_length": 0
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "max_length must be positive" in response.json()["detail"]
        
        # Test negative max_length
        request_data["max_length"] = -1
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "max_length must be positive" in response.json()["detail"]
    
    def test_seo_optimize_missing_text(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with missing text field."""
        request_data = {
            "keywords": ["test"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_seo_optimize_invalid_keywords_type(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with invalid keywords type."""
        request_data = {
            "text": "Test text",
            "keywords": "not a list",  # Should be a list
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestEndToEndFlows:
    """Test complete end-to-end flows."""
    
    def test_complete_user_journey(self, client: TestClient):
        """Test complete user journey from registration to API usage."""
        # Step 1: Register user
        user_data = {
            "email": "journey_test@example.com",
            "password": "securepassword123"
        }
        
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Step 2: Login
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/auth/token", data=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 3: Use authenticated endpoints
        # Test categories
        categories_response = client.get("/api/categories/", headers=auth_headers)
        assert categories_response.status_code == 200
        
        # Test SEO optimization
        seo_request = {
            "text": "Amazing product with great features and excellent quality"
        }
        seo_response = client.post("/api/seo/optimize", json=seo_request, headers=auth_headers)
        assert seo_response.status_code == 200
        
        # Test category details
        category_response = client.get("/api/categories/MLB1132", headers=auth_headers)
        assert category_response.status_code == 200
    
    def test_error_handling_consistency(self, client: TestClient, auth_headers: dict):
        """Test that error handling is consistent across endpoints."""
        # Test unauthorized access (401)
        unauthorized_endpoints = [
            ("/api/categories/", "GET"),
            ("/api/categories/MLB1132", "GET"),
            ("/api/seo/optimize", "POST")
        ]
        
        for endpoint, method in unauthorized_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={"text": "test"})
            
            assert response.status_code == 401
            assert "detail" in response.json()
        
        # Test validation errors (422)
        validation_test_cases = [
            ("/api/auth/register", "POST", {"email": "invalid-email"}),
            ("/api/auth/token", "POST", {"username": "test"}),  # Missing password
            ("/api/seo/optimize", "POST", {"keywords": ["test"]}),  # Missing text
        ]
        
        for endpoint, method, invalid_data in validation_test_cases:
            if endpoint.startswith("/api/seo/"):
                headers = auth_headers
            else:
                headers = {}
            
            if method == "POST":
                if endpoint == "/api/auth/token":
                    response = client.post(endpoint, data=invalid_data, headers=headers)
                else:
                    response = client.post(endpoint, json=invalid_data, headers=headers)
            
            # Should be either 422 (validation) or 401 (auth) or 400 (bad request)
            assert response.status_code in [400, 401, 422]
            assert "detail" in response.json()