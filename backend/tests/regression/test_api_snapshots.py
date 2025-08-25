"""
API snapshot regression tests using pytest-regressions.

These tests capture API response snapshots to detect unintended changes
in API behavior over time.
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.models import User


class TestAPISnapshots:
    """Test API response snapshots for regression detection."""
    
    def test_health_endpoint_snapshot(self, client: TestClient, data_regression):
        """Test health endpoint response snapshot."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data_regression.check(response.json())

    def test_seo_optimize_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO optimization endpoint response snapshot."""
        request_data = {
            "text": "This is a sample product description for testing SEO optimization. It contains multiple words and should be optimized for search engines.",
            "keywords": ["product", "testing", "optimization"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Check the response structure
        response_data = response.json()
        data_regression.check(response_data)

    def test_categories_list_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test categories list endpoint response snapshot."""
        response = client.get("/api/categories/", headers=auth_headers)
        assert response.status_code == 200
        
        response_data = response.json()
        # Verify it's a list with expected structure
        assert isinstance(response_data, list)
        assert len(response_data) > 0
        
        data_regression.check(response_data)

    def test_category_details_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test category details endpoint response snapshot."""
        category_id = "MLB1132"
        response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
        assert response.status_code == 200
        
        response_data = response.json()
        # Verify basic structure
        assert "id" in response_data
        assert "name" in response_data
        assert "settings" in response_data
        
        data_regression.check(response_data)

    def test_auth_register_response_structure_snapshot(self, client: TestClient, data_regression):
        """Test user registration response structure snapshot."""
        user_data = {
            "email": "snapshot_test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
        response_data = response.json()
        # Only check email since that's what the endpoint returns
        snapshot_data = {
            "email": response_data["email"]
        }
        
        data_regression.check(snapshot_data)

    def test_auth_token_response_structure_snapshot(self, client: TestClient, data_regression):
        """Test token endpoint response structure snapshot."""
        # First register a user
        user_data = {
            "email": "token_test@example.com", 
            "password": "testpassword123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Then get token
        login_data = {
            "username": "token_test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        
        response_data = response.json()
        # Check structure without the actual token values
        snapshot_data = {
            "access_token_type": type(response_data["access_token"]).__name__,
            "token_type": response_data["token_type"],
            "has_access_token": bool(response_data.get("access_token"))
        }
        
        data_regression.check(snapshot_data)

    def test_seo_optimize_minimal_request_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO optimization with minimal request parameters."""
        request_data = {
            "text": "Short text"
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data_regression.check(response.json())

    def test_seo_optimize_with_keywords_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO optimization with specific keywords."""
        request_data = {
            "text": "Electronics and technology products for modern consumers",
            "keywords": ["electronics", "technology", "modern"],
            "max_length": 120
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data_regression.check(response.json())

    def test_error_response_snapshots(self, client: TestClient, data_regression):
        """Test error response structure snapshots."""
        # Test unauthorized access
        response = client.get("/api/categories/")
        assert response.status_code == 401
        
        error_data = response.json()
        data_regression.check(error_data)

    def test_seo_validation_error_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO endpoint validation error response."""
        # Send invalid data (empty text)
        request_data = {
            "text": "",
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 400
        
        data_regression.check(response.json())

    def test_oauth_login_redirect_snapshot(self, client: TestClient, data_regression):
        """Test OAuth login redirect response structure."""
        # OAuth login might not be available or might require specific setup
        # Let's test a simpler approach or skip this test for now
        response = client.get("/api/oauth/login")
        
        if response.status_code == 200:
            response_data = response.json()
            # Extract just the structure info, not the actual URLs which contain dynamic state
            snapshot_data = {
                "has_authorization_url": "authorization_url" in response_data,
                "has_state": "state" in response_data,
                "url_contains_redirect": "redirect_uri" in response_data.get("authorization_url", ""),
                "url_contains_state": "state=" in response_data.get("authorization_url", "")
            }
            data_regression.check(snapshot_data)
        else:
            # If OAuth is not properly configured, just test the error structure
            snapshot_data = {
                "status_code": response.status_code,
                "has_detail": "detail" in response.json() if response.content else False
            }
            data_regression.check(snapshot_data)


class TestAPIResponseValidation:
    """Additional validation tests for API responses."""
    
    def test_seo_response_completeness(self, client: TestClient, auth_headers: dict):
        """Validate SEO response contains all expected fields."""
        request_data = {
            "text": "Product description for validation test",
            "keywords": ["product", "validation"],
            "max_length": 150
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        expected_fields = ["original", "cleaned", "title", "meta_description", "keywords", "slug"]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            assert data[field] is not None, f"Field {field} is None"

    def test_categories_response_structure(self, client: TestClient, auth_headers: dict):
        """Validate categories response structure."""
        response = client.get("/api/categories/", headers=auth_headers)
        assert response.status_code == 200
        
        categories = response.json()
        assert isinstance(categories, list)
        
        for category in categories[:3]:  # Check first 3 categories
            assert "id" in category
            assert "name" in category
            assert isinstance(category["id"], str)
            assert isinstance(category["name"], str)

    def test_category_details_response_structure(self, client: TestClient, auth_headers: dict):
        """Validate category details response structure."""
        response = client.get("/api/categories/MLB1132", headers=auth_headers)
        assert response.status_code == 200
        
        category = response.json()
        expected_fields = ["id", "name", "path_from_root", "settings"]
        
        for field in expected_fields:
            assert field in category, f"Missing field: {field}"