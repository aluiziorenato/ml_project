"""
Test coverage for app/routers/proxy.py to improve coverage from 61.54% to 100%.
Tests proxy functionality, authentication, error handling, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel

from app.main import app
from app.models.oauth_session import OAuthSession


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {"id": 1, "email": "test@example.com"}


class TestProxyRouter:
    """Test proxy router functionality."""
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_success(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test successful proxy call."""
        # Setup mocks
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session with access token
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_access_token"
        mock_oauth.endpoint_id = 1
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        # Mock successful API response
        mock_proxy_api.return_value = {"status": "success", "data": "test_data"}
        
        response = client.post(
            "/api/proxy/",
            json={
                "endpoint_id": 1,
                "method": "GET",
                "path": "/test/endpoint"
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {"status": "success", "data": "test_data"}
        
        # Verify proxy_api_request was called with correct parameters
        mock_proxy_api.assert_called_once_with(
            "valid_access_token",
            "GET", 
            "/test/endpoint",
            base_url="https://api.mercadolibre.com",
            headers=None,
            json_body=None
        )
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_no_oauth_session(self, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call when OAuth session is not found."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock no OAuth session found
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = None
        mock_session.exec.return_value = mock_exec_result
        
        response = client.post(
            "/api/proxy/",
            json={
                "endpoint_id": 999,
                "method": "GET",
                "path": "/test"
            }
        )
        
        assert response.status_code == 400
        assert "No access token available for endpoint" in response.json()["detail"]
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_no_access_token(self, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call when OAuth session exists but has no access token."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session without access token
        mock_oauth = Mock()
        mock_oauth.access_token = None
        mock_oauth.endpoint_id = 1
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        response = client.post(
            "/api/proxy/",
            json={
                "endpoint_id": 1,
                "method": "GET", 
                "path": "/test"
            }
        )
        
        assert response.status_code == 400
        assert "No access token available for endpoint" in response.json()["detail"]
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_empty_access_token(self, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call when OAuth session has empty access token."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session with empty access token
        mock_oauth = Mock()
        mock_oauth.access_token = ""
        mock_oauth.endpoint_id = 1
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        response = client.post(
            "/api/proxy/",
            json={
                "endpoint_id": 1,
                "method": "POST",
                "path": "/test"
            }
        )
        
        assert response.status_code == 400
        assert "No access token available for endpoint" in response.json()["detail"]
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_with_json_body(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with JSON body data."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_token"
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        # Mock API response
        mock_proxy_api.return_value = {"created": "success"}
        
        test_json_body = {"name": "test", "value": 123}
        
        response = client.post(
            "/api/proxy/",
            json={
                "endpoint_id": 1,
                "method": "POST",
                "path": "/api/create",
                "json_body": test_json_body
            }
        )
        
        assert response.status_code == 200
        
        # Verify json_body was passed correctly
        mock_proxy_api.assert_called_once_with(
            "valid_token",
            "POST",
            "/api/create", 
            base_url="https://api.mercadolibre.com",
            headers=None,
            json_body=test_json_body
        )
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_different_methods(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with different HTTP methods."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_token"
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        mock_proxy_api.return_value = {"result": "ok"}
        
        # Test different HTTP methods
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            response = client.post(
                "/api/proxy/",
                json={
                    "endpoint_id": 1,
                    "method": method,
                    "path": f"/api/{method.lower()}"
                }
            )
            
            assert response.status_code == 200
            
            # Verify method was passed correctly
            mock_proxy_api.assert_called_with(
                "valid_token",
                method,
                f"/api/{method.lower()}",
                base_url="https://api.mercadolibre.com",
                headers=None,
                json_body=None
            )
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_default_values(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with default values."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_token"
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        mock_proxy_api.return_value = {"default": "response"}
        
        # Test with only required endpoint_id
        response = client.post(
            "/api/proxy/",
            json={"endpoint_id": 1}
        )
        
        assert response.status_code == 200
        
        # Verify default values were used
        mock_proxy_api.assert_called_once_with(
            "valid_token",
            "GET",  # default method
            "/",    # default path
            base_url="https://api.mercadolibre.com",
            headers=None,
            json_body=None  # default json_body
        )
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_api_error(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call when underlying API request fails."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_token"
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        # Mock API request failure
        mock_proxy_api.side_effect = Exception("API request failed")
        
        with pytest.raises(Exception) as exc_info:
            response = client.post(
                "/api/proxy/",
                json={
                    "endpoint_id": 1,
                    "method": "GET",
                    "path": "/failing/endpoint"
                }
            )
        
        assert "API request failed" in str(exc_info.value)


class TestProxyRouterAuthentication:
    """Test authentication aspects of proxy router."""
    
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_unauthenticated(self, mock_get_session, client: TestClient):
        """Test proxy call without authentication."""
        # Don't mock get_current_user to simulate unauthenticated request
        response = client.post(
            "/api/proxy/",
            json={"endpoint_id": 1}
        )
        
        # Should get authentication error
        assert response.status_code in [401, 422]  # Depends on auth implementation
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_authenticated_user(self, mock_get_session, mock_get_current_user, client: TestClient):
        """Test that authenticated user is required."""
        mock_get_current_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock no OAuth session to focus on auth
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = None
        mock_session.exec.return_value = mock_exec_result
        
        response = client.post(
            "/api/proxy/",
            json={"endpoint_id": 1}
        )
        
        # Should pass authentication but fail on OAuth
        assert response.status_code == 400
        assert "No access token available" in response.json()["detail"]


class TestProxyRouterEdgeCases:
    """Test edge cases and error scenarios."""
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_invalid_endpoint_id(self, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with invalid endpoint ID."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock database error for invalid endpoint_id
        mock_session.exec.side_effect = Exception("Invalid endpoint_id")
        
        with pytest.raises(Exception):
            response = client.post(
                "/api/proxy/",
                json={"endpoint_id": -1}
            )
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    async def test_proxy_call_database_error(self, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with database error."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock database error
        mock_session.exec.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            response = client.post(
                "/api/proxy/",
                json={"endpoint_id": 1}
            )
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_large_json_body(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with large JSON body."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_token"
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        mock_proxy_api.return_value = {"processed": True}
        
        # Create large JSON body
        large_json_body = {
            "data": ["item" + str(i) for i in range(1000)],
            "metadata": {"size": 1000, "type": "test"}
        }
        
        response = client.post(
            "/api/proxy/",
            json={
                "endpoint_id": 1,
                "method": "POST",
                "path": "/api/bulk",
                "json_body": large_json_body
            }
        )
        
        assert response.status_code == 200
        
        # Verify large body was passed correctly
        mock_proxy_api.assert_called_once_with(
            "valid_token",
            "POST",
            "/api/bulk",
            base_url="https://api.mercadolibre.com",
            headers=None,
            json_body=large_json_body
        )


class TestProxyRouterParams:
    """Test parameter validation and handling."""
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_missing_endpoint_id(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call without required endpoint_id."""
        mock_get_current_user.return_value = {"id": 1}
        
        response = client.post(
            "/api/proxy/",
            json={
                "method": "GET",
                "path": "/test"
                # Missing endpoint_id
            }
        )
        
        # Should get validation error
        assert response.status_code == 422
    
    @patch('app.routers.proxy.get_current_user')
    @patch('app.routers.proxy.get_session')
    @patch('app.routers.proxy.proxy_api_request')
    async def test_proxy_call_custom_paths(self, mock_proxy_api, mock_get_session, mock_get_current_user, client: TestClient):
        """Test proxy call with various custom paths."""
        mock_get_current_user.return_value = {"id": 1}
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock OAuth session
        mock_oauth = Mock()
        mock_oauth.access_token = "valid_token"
        
        mock_exec_result = Mock()
        mock_exec_result.first.return_value = mock_oauth
        mock_session.exec.return_value = mock_exec_result
        
        mock_proxy_api.return_value = {"result": "ok"}
        
        test_paths = [
            "/api/users/123",
            "/v1/products/search",
            "/categories/electronics",
            "/orders?status=active",
            "/"
        ]
        
        for path in test_paths:
            response = client.post(
                "/api/proxy/",
                json={
                    "endpoint_id": 1,
                    "method": "GET",
                    "path": path
                }
            )
            
            assert response.status_code == 200
            
            # Verify path was passed correctly
            mock_proxy_api.assert_called_with(
                "valid_token",
                "GET",
                path,
                base_url="https://api.mercadolibre.com",
                headers=None,
                json_body=None
            )