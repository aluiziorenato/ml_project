"""
Integration tests for database operations and external APIs.
"""
import pytest
from unittest.mock import patch, Mock
import httpx
from sqlmodel import Session, select

from app.models import User, ApiEndpoint, OAuthSession, OAuthToken, MeliToken
from app.crud.endpoints import create_endpoint, get_endpoint, list_endpoints, update_endpoint, delete_endpoint
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from app.crud.oauth_tokens import save_oauth_token, get_oauth_token, delete_oauth_token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.mercadolibre import build_authorization_url, generate_code_verifier, generate_code_challenge


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database operations and CRUD functionality."""
    
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
        # Create
        endpoint_data = ApiEndpoint(
            name="Test Integration Endpoint",
            url="https://api.integration.test.com",
            auth_type="oauth",
            oauth_scope="read write"
        )
        created = create_endpoint(session, endpoint_data)
        
        assert created.id is not None
        assert created.name == "Test Integration Endpoint"
        assert created.url == "https://api.integration.test.com"
        
        # Read
        retrieved = get_endpoint(session, created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
        
        # Update
        update_data = {"name": "Updated Integration Endpoint"}
        updated = update_endpoint(session, created.id, update_data)
        assert updated is not None
        assert updated.name == "Updated Integration Endpoint"
        assert updated.url == "https://api.integration.test.com"  # Unchanged
        
        # List
        all_endpoints = list_endpoints(session)
        assert len(all_endpoints) >= 1
        assert any(ep.id == created.id for ep in all_endpoints)
        
        # Delete
        deleted = delete_endpoint(session, created.id)
        assert deleted is True
        
        # Verify deletion
        deleted_endpoint = get_endpoint(session, created.id)
        assert deleted_endpoint is None
    
    def test_oauth_session_crud(self, session: Session):
        """Test OAuth session CRUD operations."""
        state = "test_integration_state_123"
        code_verifier = "test_integration_verifier_123"
        
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
    
    def test_oauth_token_crud(self, session: Session, test_user: User, mock_ml_token):
        """Test OAuth token CRUD operations."""
        # Create
        save_oauth_token(session, test_user.id, mock_ml_token)
        
        # Read
        stored_token = get_oauth_token(session, test_user.id)
        assert stored_token is not None
        assert stored_token.user_id == test_user.id
        assert stored_token.access_token == mock_ml_token["access_token"]
        assert stored_token.refresh_token == mock_ml_token["refresh_token"]
        
        # Delete
        delete_oauth_token(session, test_user.id)
        deleted_token = get_oauth_token(session, test_user.id)
        assert deleted_token is None
    
    def test_meli_token_storage(self, session: Session, test_user: User, mock_ml_token):
        """Test MeliToken storage in database."""
        meli_token = MeliToken(
            user_id=test_user.id,
            access_token=mock_ml_token["access_token"],
            refresh_token=mock_ml_token["refresh_token"],
            expires_in=mock_ml_token["expires_in"],
            user_ml_id=str(mock_ml_token["user_id"])
        )
        
        session.add(meli_token)
        session.commit()
        session.refresh(meli_token)
        
        # Verify storage
        stored_token = session.exec(
            select(MeliToken).where(MeliToken.user_id == test_user.id)
        ).first()
        
        assert stored_token is not None
        assert stored_token.user_id == test_user.id
        assert stored_token.access_token == mock_ml_token["access_token"]
        assert stored_token.user_ml_id == str(mock_ml_token["user_id"])
    
    def test_database_session_isolation(self, session: Session):
        """Test that database sessions are properly isolated."""
        # Create user in current session
        user1 = User(email="session1@test.com", hashed_password="hash1")
        session.add(user1)
        session.commit()
        
        # Create another session and verify isolation
        from app.db import get_session
        session2 = next(get_session())
        
        try:
            # Should not see uncommitted changes from other sessions
            user_from_session2 = session2.exec(
                select(User).where(User.email == "session1@test.com")
            ).first()
            assert user_from_session2 is not None  # Should see committed data
            
            # Add user in session2 but don't commit
            user2 = User(email="session2@test.com", hashed_password="hash2")
            session2.add(user2)
            
            # Original session should not see uncommitted changes
            user_from_session1 = session.exec(
                select(User).where(User.email == "session2@test.com")
            ).first()
            assert user_from_session1 is None  # Should not see uncommitted data
            
        finally:
            session2.close()


@pytest.mark.integration
class TestExternalAPIIntegration:
    """Test integration with external APIs."""
    
    @pytest.mark.asyncio
    async def test_mercado_libre_oauth_flow_simulation(self, session: Session):
        """Test simulated Mercado Libre OAuth flow."""
        # Step 1: Generate OAuth parameters
        client_id = "test_client_id"
        redirect_uri = "https://test.com/callback"
        state = generate_code_verifier()  # Use as state
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        
        # Step 2: Build authorization URL
        auth_url = build_authorization_url(
            client_id, redirect_uri, state, code_challenge
        )
        
        assert "auth.mercadolibre.com.br" in auth_url
        assert f"client_id={client_id}" in auth_url
        assert f"state={state}" in auth_url
        
        # Step 3: Save OAuth session
        save_oauth_session(session, state, code_verifier)
        
        # Step 4: Simulate callback with authorization code
        auth_code = "test_authorization_code"
        
        # Step 5: Verify OAuth session exists
        oauth_session = get_oauth_session(session, state)
        assert oauth_session is not None
        assert oauth_session.code_verifier == code_verifier
        
        # Step 6: Clean up
        delete_oauth_session(session, state)
    
    @patch('httpx.AsyncClient.post')
    @pytest.mark.asyncio
    async def test_token_exchange_simulation(self, mock_post, mock_ml_token):
        """Test simulated token exchange with Mercado Libre."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ml_token
        mock_post.return_value = mock_response
        
        # Simulate token exchange
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mercadolibre.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                    "code": "test_auth_code",
                    "redirect_uri": "https://test.com/callback",
                    "code_verifier": "test_verifier"
                }
            )
        
        assert response.status_code == 200
        token_data = response.json()
        assert token_data["access_token"] == mock_ml_token["access_token"]
        assert token_data["token_type"] == "Bearer"
    
    @patch('httpx.AsyncClient.get')
    @pytest.mark.asyncio
    async def test_user_info_fetch_simulation(self, mock_get, mock_ml_user_info):
        """Test simulated user info fetch from Mercado Libre."""
        # Mock successful user info response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ml_user_info
        mock_get.return_value = mock_response
        
        # Simulate user info fetch
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.mercadolibre.com/users/me",
                headers={"Authorization": "Bearer test_access_token"}
            )
        
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["id"] == mock_ml_user_info["id"]
        assert user_info["email"] == mock_ml_user_info["email"]
        assert user_info["nickname"] == mock_ml_user_info["nickname"]
    
    @patch('httpx.AsyncClient.get')
    @pytest.mark.asyncio
    async def test_categories_api_simulation(self, mock_get, sample_categories):
        """Test simulated categories API fetch."""
        # Mock categories response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_categories
        mock_get.return_value = mock_response
        
        # Simulate categories fetch
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.mercadolibre.com/sites/MLB/categories")
        
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == len(sample_categories)
        assert categories[0]["id"] == "MLB1132"
        assert categories[0]["name"] == "Telefones e Celulares"


@pytest.mark.integration
class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    def test_transaction_rollback(self, session: Session):
        """Test transaction rollback on error."""
        initial_count = len(session.exec(select(User)).all())
        
        try:
            # Start transaction
            user = User(email="rollback_test@example.com", hashed_password="hash")
            session.add(user)
            
            # Simulate error condition
            raise Exception("Simulated error")
            
        except Exception:
            # Rollback should happen automatically
            session.rollback()
        
        # Verify no data was committed
        final_count = len(session.exec(select(User)).all())
        assert final_count == initial_count
        
        # Verify user was not saved
        rollback_user = session.exec(
            select(User).where(User.email == "rollback_test@example.com")
        ).first()
        assert rollback_user is None
    
    def test_transaction_commit(self, session: Session):
        """Test successful transaction commit."""
        initial_count = len(session.exec(select(User)).all())
        
        # Create and commit user
        user = User(email="commit_test@example.com", hashed_password="hash")
        session.add(user)
        session.commit()
        
        # Verify data was committed
        final_count = len(session.exec(select(User)).all())
        assert final_count == initial_count + 1
        
        # Verify user was saved
        commit_user = session.exec(
            select(User).where(User.email == "commit_test@example.com")
        ).first()
        assert commit_user is not None
        assert commit_user.email == "commit_test@example.com"
    
    def test_concurrent_access_simulation(self, engine):
        """Test simulated concurrent database access."""
        from sqlmodel import Session
        
        # Create two separate sessions to simulate concurrent access
        session1 = Session(engine)
        session2 = Session(engine)
        
        try:
            # Session 1: Create user
            user1 = User(email="concurrent1@example.com", hashed_password="hash1")
            session1.add(user1)
            session1.commit()
            
            # Session 2: Try to read the user
            user_from_session2 = session2.exec(
                select(User).where(User.email == "concurrent1@example.com")
            ).first()
            
            assert user_from_session2 is not None
            assert user_from_session2.email == "concurrent1@example.com"
            
            # Session 2: Update user
            user_from_session2.is_active = False
            session2.add(user_from_session2)
            session2.commit()
            
            # Session 1: Read updated user
            session1.refresh(user1)
            assert user1.is_active is False
            
        finally:
            session1.close()
            session2.close()


@pytest.mark.integration
class TestServiceIntegration:
    """Test integration between different services."""
    
    def test_complete_oauth_workflow(self, session: Session):
        """Test complete OAuth workflow integration."""
        # Generate OAuth parameters
        state = generate_code_verifier()
        code_verifier = generate_code_verifier()
        
        # Save OAuth session
        save_oauth_session(session, state, code_verifier)
        
        # Simulate authorization callback
        stored_session = get_oauth_session(session, state)
        assert stored_session is not None
        assert stored_session.code_verifier == code_verifier
        
        # Simulate token storage after successful exchange
        test_user = User(email="oauth_workflow@example.com", hashed_password="hash")
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        
        mock_token = {
            "access_token": "APP_USR-workflow-token",
            "token_type": "Bearer",
            "expires_in": 21600,
            "refresh_token": "TG-workflow-refresh",
            "user_id": "workflow_user_123"
        }
        
        save_oauth_token(session, test_user.id, mock_token)
        
        # Verify complete workflow
        stored_token = get_oauth_token(session, test_user.id)
        assert stored_token is not None
        assert stored_token.access_token == mock_token["access_token"]
        
        # Clean up
        delete_oauth_session(session, state)
        delete_oauth_token(session, test_user.id)
    
    def test_user_and_token_relationship(self, session: Session):
        """Test relationship between users and their tokens."""
        # Create user
        user = User(email="token_relationship@example.com", hashed_password="hash")
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create multiple tokens for the user
        oauth_token = OAuthToken(
            user_id=user.id,
            access_token="oauth_access_token",
            refresh_token="oauth_refresh_token",
            token_type="Bearer",
            expires_in=3600
        )
        
        meli_token = MeliToken(
            user_id=user.id,
            access_token="meli_access_token",
            refresh_token="meli_refresh_token",
            expires_in=21600,
            user_ml_id="meli_user_123"
        )
        
        session.add(oauth_token)
        session.add(meli_token)
        session.commit()
        
        # Verify relationships
        user_oauth_tokens = session.exec(
            select(OAuthToken).where(OAuthToken.user_id == user.id)
        ).all()
        user_meli_tokens = session.exec(
            select(MeliToken).where(MeliToken.user_id == user.id)
        ).all()
        
        assert len(user_oauth_tokens) == 1
        assert len(user_meli_tokens) == 1
        assert user_oauth_tokens[0].user_id == user.id
        assert user_meli_tokens[0].user_id == user.id