"""
Unit tests for database models.
"""
import pytest
from datetime import datetime
from sqlmodel import Session

from app.models import User, ApiEndpoint, ApiTest, OAuthSession, OAuthToken, MeliToken


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_model_creation(self, session: Session):
        """Test basic user model creation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True,
            is_superuser=False
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
    
    def test_user_model_defaults(self, session: Session):
        """Test user model default values."""
        user = User(
            email="default@example.com",
            hashed_password="password"
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.is_active is True  # Default value
        assert user.is_superuser is False  # Default value
        assert user.created_at is not None
    
    def test_user_email_indexing(self, session: Session):
        """Test that user email is properly indexed."""
        user1 = User(email="user1@example.com", hashed_password="pass1")
        user2 = User(email="user2@example.com", hashed_password="pass2")
        
        session.add(user1)
        session.add(user2)
        session.commit()
        
        # Query by email should work efficiently due to indexing
        found_user = session.query(User).filter(User.email == "user1@example.com").first()
        assert found_user is not None
        assert found_user.email == "user1@example.com"


@pytest.mark.unit
class TestApiEndpointModel:
    """Test ApiEndpoint model functionality."""
    
    def test_api_endpoint_creation(self, session: Session):
        """Test basic API endpoint creation."""
        endpoint = ApiEndpoint(
            name="Test API",
            url="https://api.test.com",
            auth_type="oauth",
            oauth_scope="read write"
        )
        
        session.add(endpoint)
        session.commit()
        session.refresh(endpoint)
        
        assert endpoint.id is not None
        assert endpoint.name == "Test API"
        assert endpoint.url == "https://api.test.com"
        assert endpoint.auth_type == "oauth"
        assert endpoint.oauth_scope == "read write"


@pytest.mark.unit
class TestApiTestModel:
    """Test ApiTest model functionality."""
    
    def test_api_test_creation(self, session: Session):
        """Test basic API test creation."""
        api_test = ApiTest(
            name="Test Case 1",
            request_method="GET",
            request_path="/test",
            status_code=200,
            response_body='{"success": true}'
        )
        
        session.add(api_test)
        session.commit()
        session.refresh(api_test)
        
        assert api_test.id is not None
        assert api_test.name == "Test Case 1"
        assert api_test.request_method == "GET"
        assert api_test.request_path == "/test"
        assert api_test.status_code == 200
        assert api_test.response_body == '{"success": true}'
        assert isinstance(api_test.executed_at, datetime)
    
    def test_api_test_defaults(self, session: Session):
        """Test API test model default values."""
        api_test = ApiTest()
        
        session.add(api_test)
        session.commit()
        session.refresh(api_test)
        
        assert api_test.request_method == "GET"  # Default value
        assert api_test.request_path == "/"  # Default value
        assert api_test.executed_at is not None


@pytest.mark.unit
class TestOAuthSessionModel:
    """Test OAuthSession model functionality."""
    
    def test_oauth_session_creation(self, session: Session):
        """Test basic OAuth session creation."""
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="test_state_123",
            code_verifier="test_verifier_123",
            access_token="test_token",
            refresh_token="test_refresh",
            token_type="Bearer"
        )
        
        session.add(oauth_session)
        session.commit()
        session.refresh(oauth_session)
        
        assert oauth_session.id is not None
        assert oauth_session.endpoint_id == 1
        assert oauth_session.state == "test_state_123"
        assert oauth_session.code_verifier == "test_verifier_123"
        assert oauth_session.access_token == "test_token"
        assert oauth_session.refresh_token == "test_refresh"
        assert oauth_session.token_type == "Bearer"
        assert isinstance(oauth_session.created_at, datetime)


@pytest.mark.unit
class TestOAuthTokenModel:
    """Test OAuthToken model functionality."""
    
    def test_oauth_token_creation(self, session: Session):
        """Test basic OAuth token creation."""
        token = OAuthToken(
            user_id=1,
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="Bearer",
            expires_in=3600
        )
        
        session.add(token)
        session.commit()
        session.refresh(token)
        
        assert token.id is not None
        assert token.user_id == 1
        assert token.access_token == "access_token_123"
        assert token.refresh_token == "refresh_token_123"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600


@pytest.mark.unit
class TestMeliTokenModel:
    """Test MeliToken model functionality."""
    
    def test_meli_token_creation(self, session: Session):
        """Test basic MeliToken creation."""
        meli_token = MeliToken(
            user_id=1,
            access_token="APP_USR-test-token",
            refresh_token="TG-test-refresh",
            expires_in=21600,
            user_ml_id="123456789"
        )
        
        session.add(meli_token)
        session.commit()
        session.refresh(meli_token)
        
        assert meli_token.id is not None
        assert meli_token.user_id == 1
        assert meli_token.access_token == "APP_USR-test-token"
        assert meli_token.refresh_token == "TG-test-refresh"
        assert meli_token.expires_in == 21600
        assert meli_token.user_ml_id == "123456789"


@pytest.mark.unit
class TestModelRelationships:
    """Test model relationships and constraints."""
    
    def test_user_unique_email(self, session: Session):
        """Test that user emails must be unique."""
        user1 = User(email="duplicate@example.com", hashed_password="pass1")
        user2 = User(email="duplicate@example.com", hashed_password="pass2")
        
        session.add(user1)
        session.commit()
        
        session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()
    
    def test_oauth_session_endpoint_relationship(self, session: Session):
        """Test OAuth session endpoint relationship."""
        # Create an endpoint first
        endpoint = ApiEndpoint(
            name="OAuth Test API",
            url="https://oauth.test.com"
        )
        session.add(endpoint)
        session.commit()
        session.refresh(endpoint)
        
        # Create OAuth session linked to endpoint
        oauth_session = OAuthSession(
            endpoint_id=endpoint.id,
            state="test_state",
            code_verifier="test_verifier"
        )
        session.add(oauth_session)
        session.commit()
        session.refresh(oauth_session)
        
        assert oauth_session.endpoint_id == endpoint.id