"""
API Regression and Snapshot Tests.

These tests create comprehensive regression tests for all REST API endpoints,
including response structure validation and snapshot comparisons.
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from sqlmodel import Session

from app.models import User, ApiEndpoint


class TestAPIRegressionSnapshots:
    """Regression tests with response snapshots for all API endpoints."""
    
    def test_health_endpoint_snapshot(self, client: TestClient):
        """Test health endpoint response structure."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Snapshot test - verify exact response structure
        expected_structure = {"status": str}
        self._validate_response_structure(data, expected_structure)
        assert data["status"] == "ok"
    
    def test_auth_register_endpoint_snapshot(self, client: TestClient):
        """Test user registration endpoint response structure."""
        payload = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Snapshot test - verify response structure
        expected_structure = {
            "id": int,
            "email": str,
            "is_active": bool,
            "is_superuser": bool,
            "created_at": str
        }
        self._validate_response_structure(data, expected_structure)
        assert data["email"] == payload["email"]
        assert data["is_active"] is True
        assert data["is_superuser"] is False
    
    def test_auth_token_endpoint_snapshot(self, client: TestClient, test_user: User):
        """Test token authentication endpoint response structure."""
        form_data = {
            "username": test_user.email,
            "password": "testpassword"
        }
        
        response = client.post("/api/auth/token", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Snapshot test - verify token response structure
        expected_structure = {
            "access_token": str,
            "refresh_token": str,
            "token_type": str
        }
        self._validate_response_structure(data, expected_structure)
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_api_endpoints_list_snapshot(self, client: TestClient, auth_headers: dict):
        """Test API endpoints list response structure."""
        response = client.get("/api/endpoints/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Snapshot test - verify list response structure
        assert isinstance(data, list)
        # Test empty list structure initially
        assert len(data) == 0
    
    def test_api_endpoints_create_snapshot(self, client: TestClient, auth_headers: dict):
        """Test API endpoint creation response structure."""
        payload = {
            "name": "Test API Endpoint",
            "base_url": "https://api.test.com",
            "auth_type": "bearer"
        }
        
        response = client.post("/api/endpoints/", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Snapshot test - verify creation response structure
        expected_structure = {
            "id": int,
            "name": str,
            "url": (str, type(None)),
            "base_url": (str, type(None)),
            "auth_type": (str, type(None)),
            "oauth_scope": (str, type(None)),
            "created_at": str
        }
        self._validate_response_structure(data, expected_structure)
        assert data["name"] == payload["name"]
        assert data["base_url"] == payload["base_url"]
    
    def test_categories_list_snapshot(self, client: TestClient, auth_headers: dict):
        """Test categories list endpoint response structure."""
        with patch("app.services.mercadolibre.get_categories") as mock_get_categories:
            mock_categories = [
                {"id": "MLB1000", "name": "Electronics"},
                {"id": "MLB1001", "name": "Books"}
            ]
            mock_get_categories.return_value = mock_categories
            
            response = client.get("/api/categories/", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            
            # Snapshot test - verify categories response structure
            assert isinstance(data, list)
            for category in data:
                expected_structure = {
                    "id": str,
                    "name": str
                }
                self._validate_response_structure(category, expected_structure)
    
    def test_seo_optimize_endpoint_snapshot(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization endpoint response structure."""
        payload = {
            "text": "Sample product description for SEO optimization",
            "keywords": ["product", "description", "SEO"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Snapshot test - verify SEO response structure
        expected_structure = {
            "original": str,
            "cleaned": str,
            "title": str,
            "meta_description": str,
            "keywords": list,
            "slug": str
        }
        self._validate_response_structure(data, expected_structure)
        assert data["original"] == payload["text"]
        assert isinstance(data["keywords"], list)
    
    def test_oauth_login_endpoint_snapshot(self, client: TestClient):
        """Test OAuth login redirect response."""
        response = client.get("/api/oauth/login")
        
        # Should redirect to authorization URL
        assert response.status_code == 307
        assert "location" in response.headers
        # The redirect URL should contain Mercado Libre authorization
        assert "auth.mercadolibre" in response.headers["location"]
    
    def test_api_endpoints_get_snapshot(self, client: TestClient, auth_headers: dict, session: Session):
        """Test getting specific API endpoint response structure."""
        # First create an endpoint
        test_endpoint = ApiEndpoint(
            name="Test Get Endpoint",
            base_url="https://api.testget.com"
        )
        session.add(test_endpoint)
        session.commit()
        session.refresh(test_endpoint)
        
        response = client.get(f"/api/endpoints/{test_endpoint.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Snapshot test - verify get response structure
        expected_structure = {
            "id": int,
            "name": str,
            "url": (str, type(None)),
            "base_url": (str, type(None)),
            "auth_type": (str, type(None)),
            "oauth_scope": (str, type(None)),
            "created_at": str
        }
        self._validate_response_structure(data, expected_structure)
        assert data["id"] == test_endpoint.id
        assert data["name"] == test_endpoint.name
    
    def test_proxy_endpoint_authentication_snapshot(self, client: TestClient):
        """Test proxy endpoint authentication requirement."""
        payload = {
            "endpoint_id": 1,
            "method": "GET",
            "path": "/test"
        }
        
        response = client.post("/api/proxy/", json=payload)
        
        # Should require authentication
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def _validate_response_structure(self, data: dict, expected_structure: dict):
        """Validate that response data matches expected structure."""
        for key, expected_type in expected_structure.items():
            assert key in data, f"Missing key: {key}"
            
            if isinstance(expected_type, tuple):
                # Multiple allowed types (e.g., str or None)
                assert type(data[key]) in expected_type, f"Key {key} has wrong type: expected {expected_type}, got {type(data[key])}"
            else:
                # Single expected type
                assert isinstance(data[key], expected_type), f"Key {key} has wrong type: expected {expected_type}, got {type(data[key])}"


class TestAPIErrorHandlingRegression:
    """Regression tests for API error handling scenarios."""
    
    def test_invalid_endpoint_404(self, client: TestClient):
        """Test 404 response for non-existent endpoints."""
        response = client.get("/api/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_unauthorized_access_401(self, client: TestClient):
        """Test 401 response for unauthorized access."""
        response = client.get("/api/endpoints/")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_invalid_json_422(self, client: TestClient, auth_headers: dict):
        """Test 422 response for invalid JSON data."""
        # Missing required fields
        payload = {"name": ""}  # Missing required fields
        
        response = client.post("/api/endpoints/", json=payload, headers=auth_headers)
        
        assert response.status_code in [422, 400]  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_get_nonexistent_resource_404(self, client: TestClient, auth_headers: dict):
        """Test 404 response for non-existent resource."""
        response = client.get("/api/endpoints/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestAPIMercadoLibreIntegration:
    """Regression tests for Mercado Libre API integration."""
    
    def test_meli_tokens_endpoint_no_token(self, client: TestClient):
        """Test tokens endpoint when no token exists."""
        response = client.get("/meli/tokens")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No token found" in data["detail"]
    
    def test_meli_user_endpoint_no_token(self, client: TestClient):
        """Test user endpoint when no valid token exists."""
        response = client.get("/meli/user")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_meli_products_endpoint_no_token(self, client: TestClient):
        """Test products endpoint when no valid token exists.""" 
        response = client.get("/meli/products")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestAPIPerformanceRegression:
    """Performance regression tests for API endpoints."""
    
    def test_health_endpoint_performance(self, client: TestClient):
        """Test health endpoint response time."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        # Health endpoint should respond quickly (< 1 second)
        assert end_time - start_time < 1.0
    
    def test_auth_token_performance(self, client: TestClient, test_user: User):
        """Test authentication token generation performance."""
        import time
        
        form_data = {
            "username": test_user.email,
            "password": "testpassword"
        }
        
        start_time = time.time()
        response = client.post("/api/auth/token", data=form_data)
        end_time = time.time()
        
        assert response.status_code == 200
        # Token generation should be reasonably fast (< 2 seconds)
        assert end_time - start_time < 2.0
    
    def test_seo_optimization_performance(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization performance."""
        import time
        
        payload = {
            "text": "This is a longer text for performance testing of the SEO optimization endpoint that should still process reasonably quickly",
            "max_length": 160
        }
        
        start_time = time.time()
        response = client.post("/api/seo/optimize", json=payload, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        # SEO optimization should be reasonably fast (< 3 seconds)
        assert end_time - start_time < 3.0


class TestAPIDataValidationRegression:
    """Regression tests for API data validation."""
    
    def test_seo_optimize_invalid_data_types(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with invalid data types."""
        # Test with invalid max_length type
        payload = {
            "text": "Test text",
            "max_length": "invalid"  # Should be integer
        }
        
        response = client.post("/api/seo/optimize", json=payload, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_auth_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        payload = {
            "email": test_user.email,  # Already exists
            "password": "newpassword"
        }
        
        response = client.post("/api/auth/register", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_api_endpoints_invalid_url_format(self, client: TestClient, auth_headers: dict):
        """Test API endpoint creation with invalid URL format."""
        payload = {
            "name": "Test API",
            "base_url": "not-a-valid-url",  # Invalid URL format
        }
        
        response = client.post("/api/endpoints/", json=payload, headers=auth_headers)
        
        # Should either accept it (since validation may be loose) or reject it
        # We'll check it doesn't cause a server error
        assert response.status_code in [200, 400, 422]