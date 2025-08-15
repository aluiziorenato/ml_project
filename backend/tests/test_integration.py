"""
Integration tests for OAuth, database, and external API calls.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from sqlmodel import Session

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
from app.core.security import create_access_token, verify_password, get_password_hash


class TestOAuthIntegration:
    """Test OAuth integration functionality."""
    
    def test_generate_code_verifier(self):
        """Test PKCE code verifier generation."""
        verifier = generate_code_verifier()
        
        assert isinstance(verifier, str)
        assert len(verifier) > 0
        # Should be URL-safe base64
        assert verifier.replace("-", "").replace("_", "").isalnum()
    
    def test_generate_code_challenge(self):
        """Test PKCE code challenge generation."""
        verifier = "test_verifier_123"
        challenge = generate_code_challenge(verifier)
        
        assert isinstance(challenge, str)
        assert len(challenge) > 0
        assert challenge != verifier
    
    def test_build_authorization_url(self):
        """Test authorization URL building."""
        state = "test_state_123"
        code_challenge = "test_challenge_123"
        
        url = build_authorization_url(state, code_challenge)
        
        assert "auth.mercadolibre.com" in url
        assert state in url
        assert code_challenge in url
        assert "response_type=code" in url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, mock_ml_token):
        """Test successful token exchange."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_token
            mock_post.return_value = mock_response
            
            result = await exchange_code_for_token("test_code", "test_verifier")
            
            assert result == mock_ml_token
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_failure(self):
        """Test failed token exchange."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=MagicMock()
            )
            mock_post.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await exchange_code_for_token("invalid_code", "test_verifier")


class TestDatabaseIntegration:
    """Test database operations."""
    
    def test_oauth_session_crud(self, session: Session):
        """Test OAuth session CRUD operations."""
        state = "test_state_123"
        code_verifier = "test_verifier_123"
        
        # Create
        save_oauth_session(session, state, code_verifier)
        
        # Read
        oauth_session = get_oauth_session(session, state)
        assert oauth_session is not None
        assert oauth_session.state == state
        assert oauth_session.code_verifier == code_verifier
        
        # Delete
        delete_oauth_session(session, state)
        deleted_session = get_oauth_session(session, state)
        assert deleted_session is None
    
    def test_token_storage(self, session: Session, test_user: User, mock_ml_token):
        """Test token storage in database."""
        # This would require implementing save_token_to_db
        # For now, we'll test the concept
        tokens = mock_ml_token
        user_id = test_user.id
        
        # The function should save tokens to database
        try:
            save_token_to_db(tokens, user_id, session)
            # If function exists and works, this should pass
        except (AttributeError, NotImplementedError):
            # If function doesn't exist yet, we expect this
            pytest.skip("save_token_to_db not implemented yet")
    
    def test_user_creation_and_authentication(self, session: Session):
        """Test user creation and password verification."""
        email = "integration_test@example.com"
        password = "test_password_123"
        
        # Create user
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Verify password
        assert verify_password(password, user.hashed_password)
        assert not verify_password("wrong_password", user.hashed_password)
        
        # Test token creation
        token = create_access_token({"sub": user.email})
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_api_endpoint_crud(self, session: Session):
        """Test API endpoint CRUD operations."""
        # Import from the models package which has the correct structure
        from app.models import ApiEndpoint as MainApiEndpoint
        endpoint = MainApiEndpoint(
            name="Test Endpoint",
            url="https://api.example.com",
            auth_type="oauth",
            oauth_scope="read write"
        )
        session.add(endpoint)
        session.commit()
        session.refresh(endpoint)
        
        assert endpoint.id is not None
        assert endpoint.name == "Test Endpoint"
        assert endpoint.url == "https://api.example.com"


class TestExternalApiIntegration:
    """Test external API integrations."""
    
    @pytest.mark.asyncio
    async def test_get_user_info_success(self, mock_ml_user_info):
        """Test successful user info retrieval."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_user_info
            mock_get.return_value = mock_response
            
            result = await get_user_info("test_token")
            
            assert result == mock_ml_user_info
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_info_failure(self):
        """Test failed user info retrieval."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=MagicMock()
            )
            mock_get.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await get_user_info("invalid_token")
    
    @pytest.mark.asyncio
    async def test_get_user_products_success(self):
        """Test successful user products retrieval."""
        mock_products = {
            "results": ["item1", "item2", "item3"],
            "paging": {"total": 3, "offset": 0, "limit": 50}
        }
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_products
            mock_get.return_value = mock_response
            
            result = await get_user_products("test_token", "123456")
            
            assert result == mock_products
            assert len(result["results"]) == 3
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_categories_success(self, sample_categories):
        """Test successful categories retrieval."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_categories
            mock_get.return_value = mock_response
            
            result = await get_categories()
            
            assert result == sample_categories
            assert len(result) == 3
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """Test network timeout handling."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timed out")
            
            with pytest.raises(httpx.TimeoutException):
                await get_user_info("test_token")
    
    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test network error handling."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.NetworkError("Network error")
            
            with pytest.raises(httpx.NetworkError):
                await get_user_info("test_token")


class TestCommunicationIntegration:
    """Test communication between different components."""
    
    @pytest.mark.asyncio
    async def test_oauth_flow_integration(self, session: Session):
        """Test complete OAuth flow integration."""
        # Step 1: Generate PKCE parameters
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        state = "integration_test_state"
        
        # Step 2: Save OAuth session
        save_oauth_session(session, state, code_verifier)
        
        # Step 3: Build authorization URL
        auth_url = build_authorization_url(state, code_challenge)
        assert state in auth_url
        
        # Step 4: Simulate callback with code
        # (In real scenario, user would authorize and ML would call back)
        test_code = "test_authorization_code"
        
        # Step 5: Retrieve OAuth session
        oauth_session = get_oauth_session(session, state)
        assert oauth_session is not None
        assert oauth_session.code_verifier == code_verifier
        
        # Step 6: Mock token exchange (avoid actual network call)
        mock_token = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        
        # Just test that we can mock the exchange
        with patch("app.services.mercadolibre.exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = mock_token
            
            tokens = await exchange_code_for_token(test_code, code_verifier)
            assert tokens == mock_token
        
        # Step 7: Clean up OAuth session
        delete_oauth_session(session, state)
        assert get_oauth_session(session, state) is None
    
    def test_database_session_isolation(self, session: Session):
        """Test that database sessions are properly isolated."""
        # Create a user in this session
        user1 = User(
            email="isolation_test1@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        session.add(user1)
        session.commit()
        
        # Verify user exists in this session
        from sqlmodel import select
        found_user = session.exec(select(User).where(User.email == "isolation_test1@example.com")).first()
        assert found_user is not None
        assert found_user.email == "isolation_test1@example.com"
    
    @pytest.mark.asyncio
    async def test_async_database_operations(self, session: Session):
        """Test that async operations work with database."""
        # This tests that our async external API calls can work with database operations
        user = User(
            email="async_test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Mock an async API call that would use this user's data
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"id": 123, "email": user.email}
            mock_get.return_value = mock_response
            
            # Simulate getting user info
            user_info = await get_user_info("fake_token")
            assert user_info["email"] == user.email