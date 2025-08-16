"""
Comprehensive regression tests for API snapshots and performance monitoring.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


@pytest.mark.regression
class TestAPISnapshots:
    """Test API response snapshots for regression detection."""
    
    def test_health_endpoint_snapshot(self, client: TestClient, data_regression):
        """Test health endpoint response structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data_regression.check(response.json())
    
    def test_auth_register_response_structure_snapshot(self, client: TestClient, data_regression):
        """Test user registration response structure."""
        user_data = {
            "email": "snapshot_user@example.com",
            "password": "snapshot_password_123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
        response_data = response.json()
        # Remove dynamic fields for snapshot consistency
        response_data.pop("id", None)
        response_data.pop("created_at", None)
        
        data_regression.check(response_data)
    
    def test_auth_token_response_structure_snapshot(self, client: TestClient, data_regression):
        """Test token generation response structure."""
        # First register a user
        user_data = {
            "email": "token_snapshot@example.com",
            "password": "token_password_123"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Login to get token
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/token", data=login_data)
        assert response.status_code == 200
        
        response_data = response.json()
        # Replace actual token with placeholder for consistent snapshots
        if "access_token" in response_data:
            response_data["access_token"] = "PLACEHOLDER_ACCESS_TOKEN"
        
        data_regression.check(response_data)
    
    def test_seo_optimize_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO optimization response structure."""
        request_data = {
            "text": "Premium wireless headphones with noise cancellation technology",
            "keywords": ["wireless", "headphones", "premium"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data_regression.check(response.json())
    
    def test_seo_optimize_minimal_request_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO optimization with minimal request data."""
        request_data = {
            "text": "Simple product description"
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data_regression.check(response.json())
    
    def test_seo_optimize_with_keywords_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO optimization with specific keywords."""
        request_data = {
            "text": "Professional camera equipment for photography enthusiasts and professionals",
            "keywords": ["camera", "photography", "professional", "equipment"],
            "max_length": 140
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data_regression.check(response.json())
    
    def test_categories_list_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test categories list response structure."""
        response = client.get("/api/categories/", headers=auth_headers)
        assert response.status_code == 200
        
        response_data = response.json()
        # Verify it's a list with expected structure
        assert isinstance(response_data, list)
        
        data_regression.check(response_data)
    
    def test_category_details_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test category details response structure."""
        category_id = "MLB1132"
        response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
        assert response.status_code == 200
        
        response_data = response.json()
        # Verify basic structure
        assert "id" in response_data
        assert "name" in response_data
        
        data_regression.check(response_data)
    
    def test_oauth_login_redirect_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test OAuth login redirect response structure."""
        response = client.get("/api/oauth/login", headers=auth_headers, follow_redirects=False)
        assert response.status_code == 307
        
        # Capture redirect information
        redirect_data = {
            "status_code": response.status_code,
            "location_contains": {
                "auth_mercadolibre": "auth.mercadolibre.com.br" in response.headers.get("location", ""),
                "client_id_present": "client_id=" in response.headers.get("location", ""),
                "state_present": "state=" in response.headers.get("location", ""),
                "code_challenge_present": "code_challenge=" in response.headers.get("location", "")
            }
        }
        
        data_regression.check(redirect_data)
    
    def test_error_response_snapshots(self, client: TestClient, auth_headers: dict, data_regression):
        """Test error response structures for consistency."""
        error_responses = {}
        
        # 404 Not Found
        not_found_response = client.get("/api/nonexistent/endpoint", headers=auth_headers)
        error_responses["404_not_found"] = {
            "status_code": not_found_response.status_code,
            "response_structure": list(not_found_response.json().keys())
        }
        
        # 401 Unauthorized
        unauthorized_response = client.get("/api/categories/")
        error_responses["401_unauthorized"] = {
            "status_code": unauthorized_response.status_code,
            "response_structure": list(unauthorized_response.json().keys())
        }
        
        # 422 Validation Error
        validation_response = client.post("/api/seo/optimize", json={"invalid": "data"}, headers=auth_headers)
        error_responses["422_validation"] = {
            "status_code": validation_response.status_code,
            "response_structure": list(validation_response.json().keys())
        }
        
        data_regression.check(error_responses)
    
    def test_seo_validation_error_snapshot(self, client: TestClient, auth_headers: dict, data_regression):
        """Test SEO validation error response structure."""
        # Missing required 'text' field
        invalid_request = {"keywords": ["test"]}
        
        response = client.post("/api/seo/optimize", json=invalid_request, headers=auth_headers)
        assert response.status_code == 422
        
        # Normalize validation error details for consistent snapshots
        response_data = response.json()
        if "detail" in response_data and isinstance(response_data["detail"], list):
            # Sort validation errors for consistent ordering
            response_data["detail"] = sorted(response_data["detail"], key=lambda x: x.get("loc", []))
        
        data_regression.check(response_data)


@pytest.mark.regression
class TestAPIResponseValidation:
    """Test API response validation and structure consistency."""
    
    def test_seo_response_completeness(self, client: TestClient, auth_headers: dict):
        """Test that SEO responses contain all expected fields."""
        request_data = {
            "text": "Complete response test text for SEO optimization",
            "keywords": ["complete", "response", "test"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        response_data = response.json()
        required_fields = ["optimized_text"]
        
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"
        
        # Validate optimized_text structure
        if "optimized_text" in response_data:
            optimized = response_data["optimized_text"]
            seo_fields = ["original", "cleaned", "title", "meta_description", "keywords", "slug"]
            
            for seo_field in seo_fields:
                assert seo_field in optimized, f"Missing SEO field: {seo_field}"
    
    def test_categories_response_structure(self, client: TestClient, auth_headers: dict):
        """Test categories response structure consistency."""
        response = client.get("/api/categories/", headers=auth_headers)
        assert response.status_code == 200
        
        categories = response.json()
        assert isinstance(categories, list), "Categories response should be a list"
        
        for category in categories[:3]:  # Check first 3 categories
            assert "id" in category, "Category should have 'id' field"
            assert "name" in category, "Category should have 'name' field"
            assert isinstance(category["id"], str), "Category ID should be string"
            assert isinstance(category["name"], str), "Category name should be string"
    
    def test_category_details_response_structure(self, client: TestClient, auth_headers: dict):
        """Test category details response structure consistency."""
        response = client.get("/api/categories/MLB1132", headers=auth_headers)
        assert response.status_code == 200
        
        category = response.json()
        required_fields = ["id", "name"]
        
        for field in required_fields:
            assert field in category, f"Category details should have '{field}' field"
        
        assert isinstance(category["id"], str), "Category ID should be string"
        assert isinstance(category["name"], str), "Category name should be string"
    
    def test_auth_response_security(self, client: TestClient):
        """Test that authentication responses don't leak sensitive information."""
        user_data = {
            "email": "security_test@example.com",
            "password": "security_password_123"
        }
        
        # Test registration response
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        register_data = register_response.json()
        
        # Should not contain password or hashed_password
        assert "password" not in register_data
        assert "hashed_password" not in register_data
        
        # Should contain safe fields
        assert "email" in register_data
        assert "id" in register_data
        
        # Test login response
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        
        # Should contain token information
        assert "access_token" in token_data
        assert "token_type" in token_data
        
        # Should not contain sensitive user information
        assert "password" not in token_data
        assert "hashed_password" not in token_data


@pytest.mark.regression
class TestPerformanceRegression:
    """Test performance benchmarks to detect performance regressions."""
    
    @pytest.mark.benchmark(group="seo")
    def test_seo_optimization_performance(self, client: TestClient, auth_headers: dict, benchmark):
        """Benchmark SEO optimization performance."""
        request_data = {
            "text": "Performance benchmark test for SEO optimization with multiple keywords and long text content that should be processed efficiently",
            "keywords": ["performance", "benchmark", "seo", "optimization"],
            "max_length": 160
        }
        
        def seo_request():
            response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
            assert response.status_code == 200
            return response.json()
        
        result = benchmark(seo_request)
        
        # Validate benchmark result structure
        assert "optimized_text" in result
    
    @pytest.mark.benchmark(group="auth")
    def test_authentication_performance(self, client: TestClient, benchmark):
        """Benchmark authentication performance."""
        user_data = {
            "email": "perf_auth@example.com",
            "password": "perf_password_123"
        }
        
        # Register user first
        client.post("/api/auth/register", json=user_data)
        
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        def auth_request():
            response = client.post("/api/auth/token", data=login_data)
            assert response.status_code == 200
            return response.json()
        
        result = benchmark(auth_request)
        
        # Validate benchmark result
        assert "access_token" in result
    
    @pytest.mark.benchmark(group="categories")
    def test_categories_api_performance(self, client: TestClient, auth_headers: dict, benchmark):
        """Benchmark categories API performance."""
        def categories_request():
            response = client.get("/api/categories/", headers=auth_headers)
            assert response.status_code == 200
            return response.json()
        
        result = benchmark(categories_request)
        
        # Validate benchmark result
        assert isinstance(result, list)


@pytest.mark.regression
class TestDataConsistencyRegression:
    """Test data consistency and integrity over time."""
    
    def test_user_data_consistency(self, client: TestClient, session):
        """Test user data remains consistent across operations."""
        user_data = {
            "email": "consistency_test@example.com",
            "password": "consistency_password_123"
        }
        
        # Register user
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        user_id = register_response.json()["id"]
        
        # Verify user in database
        from sqlmodel import select
        from app.models import User
        
        db_user = session.exec(select(User).where(User.id == user_id)).first()
        assert db_user is not None
        assert db_user.email == user_data["email"]
        assert db_user.is_active is True  # Default value
        
        # Login and verify token works
        login_response = client.post("/api/auth/token", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        
        # Use token to access protected endpoint
        protected_response = client.get("/api/categories/", headers=auth_headers)
        assert protected_response.status_code == 200
    
    def test_endpoint_data_consistency(self, client: TestClient, auth_headers: dict, session):
        """Test endpoint data remains consistent across CRUD operations."""
        endpoint_data = {
            "name": "Consistency Test API",
            "url": "https://api.consistency-test.com",
            "auth_type": "oauth",
            "oauth_scope": "read write"
        }
        
        # Create endpoint
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        assert create_response.status_code == 201
        
        created_endpoint = create_response.json()
        endpoint_id = created_endpoint["id"]
        
        # Verify in database
        from sqlmodel import select
        from app.models import ApiEndpoint
        
        db_endpoint = session.exec(select(ApiEndpoint).where(ApiEndpoint.id == endpoint_id)).first()
        assert db_endpoint is not None
        assert db_endpoint.name == endpoint_data["name"]
        assert db_endpoint.url == endpoint_data["url"]
        
        # Update endpoint
        update_data = {"name": "Updated Consistency Test API"}
        update_response = client.put(f"/api/endpoints/{endpoint_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # Verify update in database
        session.refresh(db_endpoint)
        assert db_endpoint.name == update_data["name"]
        assert db_endpoint.url == endpoint_data["url"]  # Should remain unchanged
        
        # Verify via API
        get_response = client.get(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        api_endpoint = get_response.json()
        assert api_endpoint["name"] == update_data["name"]
        assert api_endpoint["url"] == endpoint_data["url"]
        
        # Clean up
        delete_response = client.delete(f"/api/endpoints/{endpoint_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        # Verify deletion
        deleted_endpoint = session.exec(select(ApiEndpoint).where(ApiEndpoint.id == endpoint_id)).first()
        assert deleted_endpoint is None