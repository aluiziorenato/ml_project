"""
OAuth integration tests for Mercado Libre authentication.

These tests verify the complete OAuth flow including:
- OAuth URL generation and PKCE
- Token exchange process 
- User information retrieval
- Database storage of tokens
- Integration with PostgreSQL
"""
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from sqlmodel import Session, select

from app.models import User, OAuthSession, OAuthToken
from app.services.mercadolibre import (
    generate_code_verifier,
    generate_code_challenge,
    build_authorization_url,
    exchange_code_for_token,
    get_user_info,
    get_user_products,
    get_categories
)
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from app.crud.oauth_tokens import save_token_to_db


class TestOAuthPKCEFlow:
    """Test OAuth PKCE (Proof Key for Code Exchange) functionality."""
    
    def test_generate_code_verifier(self):
        """Test PKCE code verifier generation."""
        verifier = generate_code_verifier()
        
        assert isinstance(verifier, str)
        assert len(verifier) > 0
        # Should be URL-safe base64
        assert verifier.replace("-", "").replace("_", "").isalnum()
        
        # Test different length
        verifier_128 = generate_code_verifier(128)
        assert len(verifier_128) > len(verifier)
    
    def test_generate_code_challenge(self):
        """Test PKCE code challenge generation."""
        verifier = "test_verifier_123456789"
        challenge = generate_code_challenge(verifier)
        
        assert isinstance(challenge, str)
        assert len(challenge) > 0
        assert challenge != verifier
        # Should be deterministic
        assert challenge == generate_code_challenge(verifier)
    
    def test_build_authorization_url(self):
        """Test authorization URL building with proper parameters."""
        state = "test_state_123"
        code_challenge = "test_challenge_123"
        redirect_uri = "http://localhost:8000/api/oauth/callback"
        
        url = build_authorization_url(state, code_challenge, redirect_uri)
        
        assert "auth.mercadolibre.com" in url
        assert state in url
        assert code_challenge in url
        assert "response_type=code" in url
        assert "code_challenge_method=S256" in url
        # URL will be encoded, so check for the encoded version or decode it
        from urllib.parse import unquote
        assert redirect_uri in unquote(url)


class TestOAuthDatabaseIntegration:
    """Test OAuth integration with PostgreSQL database."""
    
    def test_save_oauth_session(self, pg_session: Session):
        """Test saving OAuth session to database."""
        state = "test_state_session"
        code_verifier = "test_verifier_session"
        endpoint_id = 1
        
        save_oauth_session(
            session=pg_session,
            state=state,
            code_verifier=code_verifier,
            endpoint_id=endpoint_id
        )
        
        # Verify session was saved
        saved_session = get_oauth_session(session=pg_session, state=state)
        assert saved_session is not None
        assert saved_session.state == state
        assert saved_session.code_verifier == code_verifier
        assert saved_session.endpoint_id == endpoint_id
    
    def test_get_oauth_session(self, pg_session: Session, oauth_session_data: OAuthSession):
        """Test retrieving OAuth session from database."""
        retrieved_session = get_oauth_session(
            session=pg_session, 
            state=oauth_session_data.state
        )
        
        assert retrieved_session is not None
        assert retrieved_session.state == oauth_session_data.state
        assert retrieved_session.code_verifier == oauth_session_data.code_verifier
    
    def test_get_oauth_session_not_found(self, pg_session: Session):
        """Test retrieving non-existent OAuth session."""
        session = get_oauth_session(session=pg_session, state="nonexistent")
        assert session is None
    
    def test_delete_oauth_session(self, pg_session: Session, oauth_session_data: OAuthSession):
        """Test deleting OAuth session from database."""
        # Verify session exists
        session = get_oauth_session(pg_session, oauth_session_data.state)
        assert session is not None
        
        # Delete session
        delete_oauth_session(pg_session, oauth_session_data.state)
        
        # Verify session is deleted
        session = get_oauth_session(pg_session, oauth_session_data.state)
        assert session is None
    
    def test_save_token_to_db(self, pg_session: Session, pg_test_user: User, mock_ml_token):
        """Test saving OAuth token to database."""
        token_entry = save_token_to_db(
            tokens=mock_ml_token,
            user_id=pg_test_user.id,
            session=pg_session
        )
        
        assert token_entry is not None
        assert token_entry.access_token == mock_ml_token["access_token"]
        assert token_entry.refresh_token == mock_ml_token["refresh_token"]
        assert token_entry.token_type == mock_ml_token["token_type"]
        assert token_entry.expires_in == mock_ml_token["expires_in"]
        assert token_entry.scope == mock_ml_token["scope"]
        assert token_entry.user_id == pg_test_user.id
        
        # Verify token was saved to database
        saved_token = pg_session.exec(
            select(OAuthToken).where(OAuthToken.user_id == pg_test_user.id)
        ).first()
        assert saved_token is not None
        assert saved_token.access_token == mock_ml_token["access_token"]


class TestOAuthTokenExchange:
    """Test OAuth token exchange with Mercado Libre API."""
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, mock_ml_token):
        """Test successful token exchange."""
        code = "authorization_code_123"
        code_verifier = "test_code_verifier"
        redirect_uri = "http://localhost:8000/api/oauth/callback"
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_token
            mock_post.return_value = mock_response
            
            result = await exchange_code_for_token(code, code_verifier, redirect_uri)
            
            assert result == mock_ml_token
            mock_post.assert_called_once()
            
            # Verify the request was made with correct parameters
            call_args = mock_post.call_args
            assert "code" in call_args.kwargs["data"]
            assert call_args.kwargs["data"]["code"] == code
            assert call_args.kwargs["data"]["code_verifier"] == code_verifier
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_error(self):
        """Test token exchange error handling."""
        code = "invalid_code"
        code_verifier = "test_code_verifier"
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=MagicMock()
            )
            mock_post.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await exchange_code_for_token(code, code_verifier)


class TestMercadoLibreAPIIntegration:
    """Test integration with Mercado Libre API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_user_info_success(self, mock_ml_user_info):
        """Test successful user info retrieval."""
        access_token = "APP_USR-test-token"
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_user_info
            mock_get.return_value = mock_response
            
            result = await get_user_info(access_token)
            
            assert result == mock_ml_user_info
            assert result["id"] == 123456789
            assert result["nickname"] == "TEST_USER"
            assert result["email"] == "test@example.com"
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert f"Bearer {access_token}" in call_args.kwargs["headers"]["Authorization"]
    
    @pytest.mark.asyncio
    async def test_get_user_products_success(self, mock_ml_products):
        """Test successful user products retrieval."""
        access_token = "APP_USR-test-token"
        user_id = "123456789"
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_products
            mock_get.return_value = mock_response
            
            result = await get_user_products(access_token, user_id)
            
            assert result == mock_ml_products
            assert len(result["results"]) == 3
            assert result["paging"]["total"] == 3
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert f"Bearer {access_token}" in call_args.kwargs["headers"]["Authorization"]
            assert user_id in call_args.args[0]  # URL should contain user_id
    
    @pytest.mark.asyncio
    async def test_get_categories_success(self, mock_ml_categories):
        """Test successful categories retrieval."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_categories
            mock_get.return_value = mock_response
            
            result = await get_categories()
            
            assert result == mock_ml_categories
            assert len(result) == 5
            assert result[0]["id"] == "MLB1132"
            assert result[0]["name"] == "Telefones e Celulares"
            
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_info_unauthorized(self):
        """Test user info retrieval with invalid token."""
        access_token = "invalid_token"
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=MagicMock()
            )
            mock_get.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await get_user_info(access_token)


class TestOAuthEndpointsIntegration:
    """Test OAuth endpoints with PostgreSQL integration."""
    
    def test_oauth_login_redirect(self, pg_client):
        """Test OAuth login endpoint returns proper redirect."""
        response = pg_client.get("/api/oauth/login")
        
        assert response.status_code == 307  # Redirect
        
        # Check if the redirect URL is to Mercado Libre
        redirect_url = response.headers.get("location")
        assert redirect_url is not None
        assert "auth.mercadolibre.com" in redirect_url
        assert "response_type=code" in redirect_url
        assert "code_challenge" in redirect_url
    
    def test_oauth_login_with_custom_state(self, pg_client, pg_session: Session):
        """Test OAuth login with custom state parameter."""
        custom_state = "custom_test_state"
        response = pg_client.get(f"/api/oauth/login?state={custom_state}")
        
        assert response.status_code == 307
        
        # Verify state was saved in database
        saved_session = get_oauth_session(pg_session, custom_state)
        assert saved_session is not None
        assert saved_session.state == custom_state
    
    def test_oauth_callback_missing_params(self, pg_client):
        """Test OAuth callback with missing parameters."""
        response = pg_client.get("/api/oauth/callback")
        assert response.status_code == 400
    
    def test_oauth_callback_invalid_state(self, pg_client, pg_auth_headers):
        """Test OAuth callback with invalid state."""
        response = pg_client.get(
            "/api/oauth/callback?code=test_code&state=invalid_state",
            headers=pg_auth_headers
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_oauth_callback_success(self, pg_client, pg_session: Session, 
                                        pg_test_user: User, pg_auth_headers, 
                                        oauth_session_data: OAuthSession, mock_ml_token):
        """Test successful OAuth callback flow."""
        with patch("app.services.mercadolibre.exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = mock_ml_token
            
            response = pg_client.get(
                f"/api/oauth/callback?code=test_code&state={oauth_session_data.state}",
                headers=pg_auth_headers
            )
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "ok"
            assert "tokens" in response_data
            
            # Verify token was saved to database
            saved_token = pg_session.exec(
                select(OAuthToken).where(OAuthToken.user_id == pg_test_user.id)
            ).first()
            assert saved_token is not None
            assert saved_token.access_token == mock_ml_token["access_token"]
            
            # Verify OAuth session was deleted
            session = get_oauth_session(pg_session, oauth_session_data.state)
            assert session is None


class TestOAuthRefreshToken:
    """Test OAuth refresh token functionality."""
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, mock_ml_token):
        """Test successful token refresh."""
        refresh_token = "TG-test-refresh-token"
        
        # Import the refresh function
        from app.services.mercadolibre import refresh_access_token
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_token
            mock_post.return_value = mock_response
            
            result = await refresh_access_token(refresh_token)
            
            assert result == mock_ml_token
            mock_post.assert_called_once()
            
            # Verify the request was made with correct parameters
            call_args = mock_post.call_args
            assert "refresh_token" in call_args.kwargs["data"]
            assert call_args.kwargs["data"]["refresh_token"] == refresh_token
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_error(self):
        """Test refresh token error handling."""
        refresh_token = "invalid_refresh_token"
        
        from app.services.mercadolibre import refresh_access_token
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=MagicMock()
            )
            mock_post.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await refresh_access_token(refresh_token)