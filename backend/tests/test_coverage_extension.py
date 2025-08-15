"""
Additional tests to achieve 100% coverage.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlmodel import Session

from app.models import User, ApiEndpoint
from app.crud.endpoints import create_endpoint, get_endpoint, list_endpoints, update_endpoint, delete_endpoint
from app.routers.api_endpoints import router
from app.routers.api_tests import router as api_tests_router
from app.routers.proxy import router as proxy_router
from app.startup import create_admin_user
from app import main


class TestCRUDEndpoints:
    """Test CRUD operations for endpoints."""
    
    def test_create_endpoint_success(self, session: Session):
        """Test successful endpoint creation."""
        endpoint_data = ApiEndpoint(
            name="Test API",
            url="https://api.test.com"
        )
        
        created = create_endpoint(session, endpoint_data)
        assert created.id is not None
        assert created.name == "Test API"
        assert created.url == "https://api.test.com"
    
    def test_get_endpoint_success(self, session: Session):
        """Test successful endpoint retrieval."""
        # Create an endpoint first
        endpoint_data = ApiEndpoint(
            name="Get Test API",
            url="https://api.gettest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Retrieve it
        retrieved = get_endpoint(session, created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Get Test API"
    
    def test_get_endpoint_not_found(self, session: Session):
        """Test endpoint retrieval with non-existent ID."""
        retrieved = get_endpoint(session, 999999)
        assert retrieved is None
    
    def test_list_endpoints(self, session: Session):
        """Test listing all endpoints."""
        # Create multiple endpoints
        for i in range(3):
            endpoint_data = ApiEndpoint(
                name=f"List Test API {i}",
                url=f"https://api.listtest{i}.com"
            )
            create_endpoint(session, endpoint_data)
        
        endpoints = list_endpoints(session)
        assert len(endpoints) >= 3
    
    def test_update_endpoint_success(self, session: Session):
        """Test successful endpoint update."""
        # Create an endpoint first
        endpoint_data = ApiEndpoint(
            name="Update Test API",
            url="https://api.updatetest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Update it
        update_data = {"name": "Updated API", "url": "https://api.updated.com"}
        updated = update_endpoint(session, created.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated API"
        assert updated.url == "https://api.updated.com"
    
    def test_update_endpoint_not_found(self, session: Session):
        """Test endpoint update with non-existent ID."""
        update_data = {"name": "Non-existent"}
        updated = update_endpoint(session, 999999, update_data)
        assert updated is None
    
    def test_delete_endpoint_success(self, session: Session):
        """Test successful endpoint deletion."""
        # Create an endpoint first
        endpoint_data = ApiEndpoint(
            name="Delete Test API",
            url="https://api.deletetest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Delete it
        deleted = delete_endpoint(session, created.id)
        assert deleted is True
        
        # Verify it's gone
        retrieved = get_endpoint(session, created.id)
        assert retrieved is None
    
    def test_delete_endpoint_not_found(self, session: Session):
        """Test endpoint deletion with non-existent ID."""
        deleted = delete_endpoint(session, 999999)
        assert deleted is False


class TestApiEndpointsRouter:
    """Test the API endpoints router."""
    
    def test_endpoint_create_route(self, client: TestClient, auth_headers: dict):
        """Test endpoint creation route."""
        endpoint_data = {
            "name": "Route Test API",
            "url": "https://api.routetest.com",
            "auth_type": "oauth",
            "oauth_scope": "read write"
        }
        
        response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Route Test API"
        assert data["url"] == "https://api.routetest.com"
    
    def test_endpoint_get_route(self, client: TestClient, auth_headers: dict):
        """Test endpoint retrieval route."""
        # Create an endpoint first
        endpoint_data = {
            "name": "Get Route Test API",
            "url": "https://api.getroutetest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        created_endpoint = create_response.json()
        
        # Get it
        response = client.get(f"/api/endpoints/{created_endpoint['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_endpoint["id"]
        assert data["name"] == "Get Route Test API"
    
    def test_endpoint_get_route_not_found(self, client: TestClient, auth_headers: dict):
        """Test endpoint retrieval route with non-existent ID."""
        response = client.get("/api/endpoints/999999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_endpoint_update_route(self, client: TestClient, auth_headers: dict):
        """Test endpoint update route."""
        # Create an endpoint first
        endpoint_data = {
            "name": "Update Route Test API",
            "url": "https://api.updateroutetest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        created_endpoint = create_response.json()
        
        # Update it
        update_data = {
            "name": "Updated Route API",
            "url": "https://api.updatedroute.com"
        }
        
        response = client.put(f"/api/endpoints/{created_endpoint['id']}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Route API"
        assert data["url"] == "https://api.updatedroute.com"
    
    def test_endpoint_update_route_not_found(self, client: TestClient, auth_headers: dict):
        """Test endpoint update route with non-existent ID."""
        update_data = {
            "name": "Non-existent API",
            "url": "https://api.nonexistent.com"
        }
        
        response = client.put("/api/endpoints/999999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_endpoint_delete_route(self, client: TestClient, auth_headers: dict):
        """Test endpoint deletion route."""
        # Create an endpoint first
        endpoint_data = {
            "name": "Delete Route Test API",
            "url": "https://api.deleteroutetest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        created_endpoint = create_response.json()
        
        # Delete it
        response = client.delete(f"/api/endpoints/{created_endpoint['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
    
    def test_endpoint_delete_route_not_found(self, client: TestClient, auth_headers: dict):
        """Test endpoint deletion route with non-existent ID."""
        response = client.delete("/api/endpoints/999999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_endpoints_list_route(self, client: TestClient, auth_headers: dict):
        """Test endpoints list route."""
        response = client.get("/api/endpoints/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestStartupFunctions:
    """Test startup functions."""
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    def test_create_admin_user_new(self, mock_select, mock_get_session):
        """Test creating admin user when none exists."""
        # Mock session and user query
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None  # No existing admin
        
        # Call the function
        create_admin_user()
        
        # Verify admin user was created
        assert mock_session.add.called
        assert mock_session.commit.called
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    def test_create_admin_user_exists(self, mock_select, mock_get_session):
        """Test when admin user already exists."""
        # Mock session and user query
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock existing admin user
        mock_admin = MagicMock()
        mock_session.exec.return_value.first.return_value = mock_admin
        
        # Call the function
        create_admin_user()
        
        # Verify no new user was created
        assert not mock_session.add.called


class TestProxyRouter:
    """Test proxy router functionality."""
    
    def test_proxy_route_unauthorized(self, client: TestClient):
        """Test proxy route without authentication."""
        response = client.get("/proxy/test")
        
        assert response.status_code == 401


class TestApiTestsRouter:
    """Test API tests router functionality."""
    
    def test_api_tests_route_unauthorized(self, client: TestClient):
        """Test API tests route without authentication."""
        response = client.get("/api/tests/")
        
        assert response.status_code == 401


class TestMainApplication:
    """Test main application setup."""
    
    def test_health_endpoint_basic(self, client: TestClient):
        """Test basic health endpoint functionality."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_application_startup(self):
        """Test that the application can be instantiated."""
        app = main.app
        assert app is not None
        assert hasattr(app, 'routes')
        
        # Check that our routes are registered
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        expected_paths = ['/health', '/api/auth/register', '/api/auth/token', '/api/seo/optimize', '/api/categories/']
        
        for expected_path in expected_paths:
            assert any(expected_path in path for path in route_paths), f"Route {expected_path} not found"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_seo_optimize_server_error(self, client: TestClient, auth_headers: dict):
        """Test SEO optimization with server error simulation."""
        request_data = {
            "text": "Test text",
            "max_length": 160
        }
        
        with patch("app.services.seo.optimize_text") as mock_optimize:
            mock_optimize.side_effect = Exception("Unexpected error")
            
            response = client.post("/api/seo/optimize", json=request_data, headers=auth_headers)
            
            assert response.status_code == 500
            assert "Internal server error" in response.json()["detail"]
    
    def test_categories_server_error(self, client: TestClient, auth_headers: dict):
        """Test categories endpoint with server error simulation."""
        with patch("app.routers.categories.logger") as mock_logger:
            # Simulate an exception in the categories route
            mock_logger.info.side_effect = Exception("Unexpected error")
            
            response = client.get("/api/categories/", headers=auth_headers)
            
            # The route should still work since the exception is in logging
            assert response.status_code == 200