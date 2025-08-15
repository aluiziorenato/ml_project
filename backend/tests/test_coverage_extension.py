"""
Additional tests to achieve 100% coverage.
"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, Mock
from sqlmodel import Session, select

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
            base_url="https://api.test.com",
            auth_type="bearer",
            oauth_scope="read"
        )
        
        created = create_endpoint(session, endpoint_data)
        assert created.id is not None
        assert created.name == "Test API"
        assert created.base_url == "https://api.test.com"
    
    def test_get_endpoint_success(self, session: Session):
        """Test successful endpoint retrieval."""
        # Create an endpoint first
        endpoint_data = ApiEndpoint(
            name="Get Test API",
            base_url="https://api.gettest.com"
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
                base_url=f"https://api.listtest{i}.com"
            )
            create_endpoint(session, endpoint_data)
        
        endpoints = list_endpoints(session)
        assert len(endpoints) >= 3
    
    def test_update_endpoint_success(self, session: Session):
        """Test successful endpoint update."""
        # Create an endpoint first
        endpoint_data = ApiEndpoint(
            name="Update Test API",
            base_url="https://api.updatetest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Update it
        update_data = {"name": "Updated API", "base_url": "https://api.updated.com"}
        updated = update_endpoint(session, created.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated API"
        assert updated.base_url == "https://api.updated.com"
    
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
            base_url="https://api.deletetest.com"
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
            "base_url": "https://api.routetest.com",
            "auth_type": "oauth",
            "oauth_scope": "read write"
        }
        
        response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Route Test API"
        assert data["base_url"] == "https://api.routetest.com"
    
    def test_endpoint_get_route(self, client: TestClient, auth_headers: dict):
        """Test endpoint retrieval route."""
        # Create an endpoint first
        endpoint_data = {
            "name": "Get Route Test API",
            "base_url": "https://api.getroutetest.com"
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
            "base_url": "https://api.updateroutetest.com"
        }
        
        create_response = client.post("/api/endpoints/", json=endpoint_data, headers=auth_headers)
        created_endpoint = create_response.json()
        
        # Update it
        update_data = {
            "name": "Updated Route API",
            "base_url": "https://api.updatedroute.com"
        }
        
        response = client.put(f"/api/endpoints/{created_endpoint['id']}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Route API"
        assert data["base_url"] == "https://api.updatedroute.com"
    
    def test_endpoint_update_route_not_found(self, client: TestClient, auth_headers: dict):
        """Test endpoint update route with non-existent ID."""
        update_data = {
            "name": "Non-existent API",
            "base_url": "https://api.nonexistent.com"
        }
        
        response = client.put("/api/endpoints/999999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_endpoint_delete_route(self, client: TestClient, auth_headers: dict):
        """Test endpoint deletion route."""
        # Create an endpoint first
        endpoint_data = {
            "name": "Delete Route Test API",
            "base_url": "https://api.deleteroutetest.com"
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
    
    @patch.dict(os.environ, {'ADMIN_EMAIL': 'test@admin.com', 'ADMIN_PASSWORD': 'testpass123'})
    def test_create_admin_user_new(self, session: Session):
        """Test creating admin user when none exists."""
        from app.startup import create_admin_user
        import os
        
        # Ensure no admin exists first
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        existing = session.exec(select(User).where(User.email == admin_email)).first()
        if existing:
            session.delete(existing)
            session.commit()
        
        # Call the function with mocked engine using our test session
        with patch('app.startup.engine') as mock_engine:
            mock_engine.__enter__ = Mock(return_value=session)
            mock_engine.__exit__ = Mock(return_value=None)
            
            # Mock Session to return our test session
            with patch('app.startup.Session') as mock_session_class:
                mock_session_class.return_value.__enter__.return_value = session
                mock_session_class.return_value.__exit__.return_value = None
                
                create_admin_user()
        
        # Verify admin user was created
        created_admin = session.exec(select(User).where(User.email == admin_email)).first()
        assert created_admin is not None
        assert created_admin.email == admin_email
    
    @patch.dict(os.environ, {'ADMIN_EMAIL': 'existing@admin.com', 'ADMIN_PASSWORD': 'testpass123'})
    def test_create_admin_user_exists(self, session: Session):
        """Test when admin user already exists."""
        from app.startup import create_admin_user
        from app.auth import get_password_hash
        import os
        
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        
        # Create an existing admin first
        existing_admin = User(
            email=admin_email, 
            hashed_password=get_password_hash("oldpass"),
            is_superuser=True
        )
        session.add(existing_admin)
        session.commit()
        
        # Call the function with mocked engine
        with patch('app.startup.engine') as mock_engine:
            mock_engine.__enter__ = Mock(return_value=session)
            mock_engine.__exit__ = Mock(return_value=None)
            
            with patch('app.startup.Session') as mock_session_class:
                mock_session_class.return_value.__enter__.return_value = session
                mock_session_class.return_value.__exit__.return_value = None
                
                create_admin_user()
        
        # Verify only one admin exists (no duplicates created)
        admins = session.exec(select(User).where(User.email == admin_email)).all()
        assert len(admins) == 1


class TestProxyRouter:
    """Test proxy router functionality."""
    
    def test_proxy_route_unauthorized(self, client: TestClient):
        """Test proxy route without authentication."""
        response = client.post("/api/proxy/", json={
            "endpoint_id": 1,
            "method": "GET",
            "path": "/test"
        })
        
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
        
        with patch("app.routers.seo.optimize_text") as mock_optimize:
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
            
            # The route fails because of the exception in logging
            assert response.status_code == 500