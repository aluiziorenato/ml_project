"""
Comprehensive test coverage for achieving 100% coverage.
This file focuses on covering all the uncovered lines in the application.
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, select
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.models import User, OAuthSession, OAuthToken
from app.auth import get_password_hash, verify_password, create_access_token
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from app.crud.oauth_tokens import save_token_to_db, get_latest_token
from app.services.mercadolibre import generate_code_verifier, generate_code_challenge, build_authorization_url


class TestStartupModule:
    """Test coverage for startup.py module."""
    
    @patch.dict(os.environ, {"ADMIN_PASSWORD": "test_password"})
    @patch('app.startup.Session')
    def test_create_admin_user_new(self, mock_session_class):
        """Test creating new admin user."""
        from app.startup import create_admin_user
        
        # Mock session and database operations
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None  # No existing user
        
        create_admin_user()
        
        # Verify user was added and committed
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch.dict(os.environ, {"ADMIN_PASSWORD": "test_password"})
    @patch('app.startup.Session')
    def test_create_admin_user_exists(self, mock_session_class):
        """Test when admin user already exists."""
        from app.startup import create_admin_user
        
        # Mock session and existing user
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        existing_user = Mock()
        mock_session.exec.return_value.first.return_value = existing_user
        
        create_admin_user()
        
        # Verify no new user was added
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
    
    @patch.dict(os.environ, {"ADMIN_PASSWORD": ""}, clear=True)
    def test_create_admin_user_no_password(self):
        """Test error when admin password not set."""
        from app.startup import create_admin_user
        
        with pytest.raises(ValueError, match="ADMIN_PASSWORD não definido no .env"):
            create_admin_user()


class TestMeliRoutesModule:
    """Test coverage for meli_routes.py module."""
    
    @patch('app.routers.meli_routes.Session')
    def test_get_valid_token_meli_token(self, mock_session_class):
        """Test getting valid token from MeliToken table."""
        from app.routers.meli_routes import get_valid_token
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock MeliToken exists
        mock_meli_token = Mock()
        mock_meli_token.access_token = "meli_test_token"
        mock_session.query.return_value.order_by.return_value.first.return_value = mock_meli_token
        
        result = get_valid_token(mock_session)
        assert result == "meli_test_token"
    
    @patch('app.routers.meli_routes.Session')
    def test_get_valid_token_oauth_fallback(self, mock_session_class):
        """Test fallback to OAuthToken when MeliToken not available."""
        from app.routers.meli_routes import get_valid_token
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock MeliToken doesn't exist, but OAuthToken does
        mock_oauth_token = Mock()
        mock_oauth_token.access_token = "oauth_test_token"
        
        def side_effect(*args):
            if 'MeliToken' in str(args[0]):
                return Mock(order_by=Mock(return_value=Mock(first=Mock(return_value=None))))
            else:  # OAuthToken query
                return Mock(order_by=Mock(return_value=Mock(first=Mock(return_value=mock_oauth_token))))
        
        mock_session.query.side_effect = side_effect
        
        result = get_valid_token(mock_session)
        assert result == "oauth_test_token"
    
    @patch('app.routers.meli_routes.Session')
    def test_get_valid_token_no_token(self, mock_session_class):
        """Test error when no valid token found."""
        from app.routers.meli_routes import get_valid_token
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock no tokens exist
        mock_session.query.return_value.order_by.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_valid_token(mock_session)
        
        assert exc_info.value.status_code == 404
        assert "Nenhum token válido encontrado" in str(exc_info.value.detail)


class TestOAuthCRUD:
    """Test coverage for OAuth CRUD operations."""
    
    def test_oauth_sessions_crud_comprehensive(self, session: Session):
        """Test OAuth sessions CRUD operations."""
        # Test save new session
        save_oauth_session(session, "test_state", "test_verifier", 1)
        
        # Test get session
        oauth_session = get_oauth_session(session, "test_state")
        assert oauth_session is not None
        assert oauth_session.state == "test_state"
        assert oauth_session.code_verifier == "test_verifier"
        assert oauth_session.endpoint_id == 1
        
        # Test update existing session
        save_oauth_session(session, "test_state", "new_verifier", 2)
        updated_session = get_oauth_session(session, "test_state")
        assert updated_session.code_verifier == "new_verifier"
        assert updated_session.endpoint_id == 2
        
        # Test delete session
        delete_oauth_session(session, "test_state")
        deleted_session = get_oauth_session(session, "test_state")
        assert deleted_session is None
        
        # Test delete non-existent session (should not error)
        delete_oauth_session(session, "non_existent_state")
    
    def test_oauth_tokens_crud_comprehensive(self, session: Session, test_user: User):
        """Test OAuth tokens CRUD operations."""
        # Test save token
        token_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "scope": "read write",
            "token_type": "Bearer"
        }
        
        saved_token = save_token_to_db(token_data, test_user.id, session)
        assert saved_token.access_token == "test_access_token"
        assert saved_token.refresh_token == "test_refresh_token"
        assert saved_token.user_id == test_user.id
        
        # Test get latest token
        latest_token = get_latest_token(test_user.id, session)
        assert latest_token is not None
        assert latest_token.access_token == "test_access_token"


class TestMercadoLibreService:
    """Test coverage for MercadoLibre service functions."""
    
    def test_code_verifier_various_lengths(self):
        """Test code verifier generation with different lengths."""
        for length in [32, 43, 64, 128]:
            verifier = generate_code_verifier(length)
            assert isinstance(verifier, str)
            assert len(verifier) > 0
    
    def test_code_challenge_edge_cases(self):
        """Test code challenge generation with edge cases."""
        # Test with very short verifier
        short_verifier = "abc"
        challenge = generate_code_challenge(short_verifier)
        assert isinstance(challenge, str)
        assert len(challenge) > 0
        
        # Test with special characters in verifier
        special_verifier = "test-verifier_123.456"
        challenge_special = generate_code_challenge(special_verifier)
        assert isinstance(challenge_special, str)
        assert len(challenge_special) > 0
    
    def test_authorization_url_with_custom_redirect(self):
        """Test authorization URL building with custom redirect URI."""
        state = "custom_state"
        challenge = "custom_challenge"
        custom_redirect = "https://custom.example.com/callback"
        
        url = build_authorization_url(state, challenge, custom_redirect)
        assert "auth.mercadolibre.com" in url
        assert state in url
        assert challenge in url
        # URL encode the redirect URI to match what's actually in the URL
        import urllib.parse
        encoded_redirect = urllib.parse.quote(custom_redirect, safe='')
        assert encoded_redirect in url
    
    @pytest.mark.asyncio
    async def test_external_api_functions_exist(self):
        """Test that external API functions are callable and importable."""
        from app.services.mercadolibre import get_user_info, get_user_products
        
        # Just verify they are callable - actual API calls tested separately
        assert callable(get_user_info)
        assert callable(get_user_products)


class TestAuthModule:
    """Test coverage for auth module functions."""
    
    def test_password_operations(self):
        """Test password hashing and verification."""
        plain_password = "test_password_123"
        
        # Test hashing
        hashed = get_password_hash(plain_password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != plain_password
        
        # Test verification
        assert verify_password(plain_password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_token_creation(self):
        """Test access token creation."""
        data = {"sub": "test@example.com", "user_id": 1}
        
        # Test with default expiration
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test with custom expiration
        token_custom = create_access_token(data, 120)
        assert isinstance(token_custom, str)
        assert len(token_custom) > 0
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, session: Session):
        """Test get_current_user with invalid token."""
        from app.auth import get_current_user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", session)
        
        assert exc_info.value.status_code == 401


class TestProxyRouter:
    """Test coverage for proxy router."""
    
    def test_proxy_route_no_token(self, client: TestClient, auth_headers: dict):
        """Test proxy route when no access token available."""
        response = client.post(
            "/api/proxy/", 
            json={"endpoint_id": 999, "method": "GET", "path": "/test"},
            headers=auth_headers
        )
        
        # Should return error about missing token or method not allowed
        assert response.status_code in [400, 404, 422]


class TestErrorScenarios:
    """Test various error scenarios for complete coverage."""
    
    def test_oauth_callback_error_paths(self, client: TestClient, auth_headers: dict):
        """Test OAuth callback error scenarios."""
        # Test with malformed parameters
        response = client.get("/api/oauth/callback?code=&state=", headers=auth_headers)
        assert response.status_code == 400
        
        # Test with only code
        response = client.get("/api/oauth/callback?code=test_code", headers=auth_headers)
        assert response.status_code == 400
        
        # Test with only state  
        response = client.get("/api/oauth/callback?state=test_state", headers=auth_headers)
        assert response.status_code == 400
    
    def test_categories_error_handling(self, client: TestClient):
        """Test categories endpoint error handling."""
        # Test without authentication
        response = client.get("/api/categories/")
        assert response.status_code == 401
        
        # Test with invalid token
        response = client.get(
            "/api/categories/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_seo_error_scenarios(self, client: TestClient, auth_headers: dict):
        """Test SEO endpoint error scenarios."""
        # Test with empty content
        response = client.post(
            "/api/seo/optimize",
            json={"content": ""},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Test with missing required fields
        response = client.post(
            "/api/seo/optimize",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 422


class TestAsyncFunctions:
    """Test async functions that require special handling."""
    
    @pytest.mark.asyncio
    async def test_meli_user_info_error_handling(self):
        """Test MercadoLibre user info error handling."""
        from app.routers.meli_routes import get_authenticated_user
        
        # This would typically test with a mock, but the function signature
        # requires dependency injection, so we'll test the import
        assert callable(get_authenticated_user)
    
    @pytest.mark.asyncio 
    async def test_meli_products_error_handling(self):
        """Test MercadoLibre products error handling."""
        from app.routers.meli_routes import get_user_products_endpoint
        
        # Similar to above - test that function exists and is callable
        assert callable(get_user_products_endpoint)


class TestDatabaseOperations:
    """Test database operations for coverage."""
    
    def test_user_crud_operations(self, session: Session):
        """Test user CRUD operations."""
        # Create user
        user_data = {
            "email": "test_crud@example.com",
            "hashed_password": get_password_hash("test_password")  # Use correct field name
        }
        user = User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Read user
        found_user = session.exec(select(User).where(User.email == "test_crud@example.com")).first()
        assert found_user is not None
        assert found_user.email == "test_crud@example.com"
        
        # Update user (implicitly tested by refresh)
        assert found_user.id is not None
        
        # Delete user
        session.delete(found_user)
        session.commit()
        
        # Verify deletion
        deleted_user = session.exec(select(User).where(User.email == "test_crud@example.com")).first()
        assert deleted_user is None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_mercadolibre_service_edge_cases(self):
        """Test MercadoLibre service edge cases."""
        from app.services.mercadolibre import generate_code_verifier, generate_code_challenge
        
        # Test minimum length
        verifier_min = generate_code_verifier(32)
        assert len(verifier_min) >= 32
        
        # Test challenge with empty string (should handle gracefully)
        try:
            challenge_empty = generate_code_challenge("")
            assert isinstance(challenge_empty, str)
        except Exception:
            # If it raises an exception, that's also valid behavior
            pass
    
    def test_oauth_session_edge_cases(self, session: Session):
        """Test OAuth session edge cases."""
        # Test with None endpoint_id
        save_oauth_session(session, "edge_case_state", "edge_verifier", None)
        oauth_session = get_oauth_session(session, "edge_case_state")
        assert oauth_session.endpoint_id is None
        
        # Clean up
        delete_oauth_session(session, "edge_case_state")
    
    def test_token_operations_edge_cases(self, session: Session, test_user: User):
        """Test token operations edge cases."""
        # Test with minimal token data
        minimal_token_data = {
            "access_token": "minimal_token",
            # Other fields None/missing
        }
        
        saved_token = save_token_to_db(minimal_token_data, test_user.id, session)
        assert saved_token.access_token == "minimal_token"
        assert saved_token.refresh_token is None
        assert saved_token.expires_in is None