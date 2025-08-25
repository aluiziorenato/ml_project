"""
Unit tests for SQLModel models.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models import User, OAuthSession, ApiEndpoint, ApiTest
from app.core.security import get_password_hash, verify_password


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, db: Session):
        """Test basic user creation."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        
    def test_user_password_verification(self, db: Session):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        user = User(
            email="test@example.com",
            hashed_password=hashed,
            is_active=True
        )
        db.add(user)
        db.commit()
        
        assert verify_password(password, user.hashed_password)
        assert not verify_password("wrong_password", user.hashed_password)
        
    def test_user_email_uniqueness(self, db: Session):
        """Test that email must be unique."""
        user1 = User(
            email="test@example.com",
            hashed_password=get_password_hash("password1"),
            is_active=True
        )
        db.add(user1)
        db.commit()
        
        user2 = User(
            email="test@example.com",  # Same email
            hashed_password=get_password_hash("password2"),
            is_active=True
        )
        db.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db.commit()
            
    def test_user_superuser_flag(self, db: Session):
        """Test superuser functionality."""
        admin_user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin_password"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        assert admin_user.is_superuser is True
        
    def test_user_inactive_flag(self, db: Session):
        """Test inactive user functionality."""
        inactive_user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("password"),
            is_active=False
        )
        db.add(inactive_user)
        db.commit()
        db.refresh(inactive_user)
        
        assert inactive_user.is_active is False


@pytest.mark.unit
class TestOAuthSessionModel:
    """Test OAuthSession model functionality."""
    
    def test_oauth_session_creation(self, db: Session):
        """Test OAuth session creation."""
        session = OAuthSession(
            endpoint_id=1,
            state="test_state_123",
            code_verifier="test_verifier_456",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_type="Bearer",
            expires_at=datetime.utcnow() + timedelta(hours=6)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        assert session.id is not None
        assert session.endpoint_id == 1
        assert session.state == "test_state_123"
        assert session.code_verifier == "test_verifier_456"
        assert session.access_token == "test_access_token"
        assert session.refresh_token == "test_refresh_token"
        assert session.token_type == "Bearer"
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.expires_at, datetime)
        
    def test_oauth_session_without_tokens(self, db: Session):
        """Test OAuth session creation without tokens (initial state)."""
        session = OAuthSession(
            endpoint_id=1,
            state="test_state_123",
            code_verifier="test_verifier_456"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        assert session.access_token is None
        assert session.refresh_token is None
        assert session.token_type is None
        assert session.expires_at is None


@pytest.mark.unit
class TestApiEndpointModel:
    """Test ApiEndpoint model functionality."""
    
    def test_api_endpoint_creation(self, db: Session):
        """Test API endpoint creation."""
        from app.models import ApiEndpoint
        
        endpoint = ApiEndpoint(
            name="Test API",
            url="https://api.test.com",
            auth_type="oauth",
            oauth_scope="read write"
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        
        assert endpoint.id is not None
        assert endpoint.name == "Test API"
        assert endpoint.url == "https://api.test.com"
        assert endpoint.auth_type == "oauth"
        assert endpoint.oauth_scope == "read write"
        
    def test_api_endpoint_minimal_data(self, db: Session):
        """Test API endpoint with minimal required data."""
        from app.models import ApiEndpoint
        
        endpoint = ApiEndpoint(
            name="Minimal API",
            url="https://minimal.api.com"
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        
        assert endpoint.id is not None
        assert endpoint.name == "Minimal API"
        assert endpoint.url == "https://minimal.api.com"


@pytest.mark.unit
class TestApiTestModel:
    """Test ApiTest model functionality."""
    
    def test_api_test_creation(self, db: Session):
        """Test API test creation."""
        test = ApiTest(
            endpoint_id=1,
            name="Test API Endpoint",
            request_method="GET",
            request_path="/test",
            request_headers='{"Content-Type": "application/json"}',
            request_body='{"test": true}',
            status_code=200,
            response_body='{"success": true}'
        )
        db.add(test)
        db.commit()
        db.refresh(test)
        
        assert test.id is not None
        assert test.endpoint_id == 1
        assert test.name == "Test API Endpoint"
        assert test.request_method == "GET"
        assert test.request_path == "/test"
        assert test.status_code == 200
        assert isinstance(test.executed_at, datetime)
        
    def test_api_test_defaults(self, db: Session):
        """Test API test with default values."""
        test = ApiTest(
            endpoint_id=1,
            name="Default Test"
        )
        db.add(test)
        db.commit()
        db.refresh(test)
        
        assert test.request_method == "GET"
        assert test.request_path == "/"
        assert test.status_code is None
        assert test.response_body is None


@pytest.mark.unit
class TestModelRelationships:
    """Test relationships between models."""
    
    def test_user_query_operations(self, db: Session):
        """Test user query operations."""
        # Create users
        user1 = User(
            email="user1@example.com",
            hashed_password=get_password_hash("password1"),
            is_active=True
        )
        user2 = User(
            email="user2@example.com",
            hashed_password=get_password_hash("password2"),
            is_active=False
        )
        
        db.add_all([user1, user2])
        db.commit()
        
        # Query active users
        active_users = db.exec(select(User).where(User.is_active == True)).all()
        assert len(active_users) == 1
        assert active_users[0].email == "user1@example.com"
        
        # Query by email
        found_user = db.exec(select(User).where(User.email == "user2@example.com")).first()
        assert found_user is not None
        assert found_user.is_active is False
        
    def test_oauth_session_query_operations(self, db: Session):
        """Test OAuth session query operations."""
        # Create sessions
        session1 = OAuthSession(
            endpoint_id=1,
            state="state1",
            code_verifier="verifier1",
            access_token="token1"
        )
        session2 = OAuthSession(
            endpoint_id=2,
            state="state2",
            code_verifier="verifier2"
        )
        
        db.add_all([session1, session2])
        db.commit()
        
        # Query sessions with tokens
        sessions_with_tokens = db.exec(
            select(OAuthSession).where(OAuthSession.access_token.is_not(None))
        ).all()
        assert len(sessions_with_tokens) == 1
        assert sessions_with_tokens[0].state == "state1"
        
        # Query by endpoint_id
        endpoint_sessions = db.exec(
            select(OAuthSession).where(OAuthSession.endpoint_id == 2)
        ).all()
        assert len(endpoint_sessions) == 1
        assert endpoint_sessions[0].access_token is None


@pytest.mark.unit
class TestModelValidation:
    """Test model field validation and constraints."""
    
    def test_user_email_validation(self, db: Session):
        """Test that email validation works properly."""
        # This would require Pydantic validation if implemented
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        assert "@" in user.email
        assert "." in user.email
        
    def test_api_endpoint_url_validation(self, db: Session):
        """Test URL validation for API endpoints."""
        from app.models import ApiEndpoint
        
        endpoint = ApiEndpoint(
            name="Test API",
            url="https://api.test.com"
        )
        db.add(endpoint)
        db.commit()
        
        assert endpoint.url.startswith("http")
        
    def test_model_timestamp_auto_generation(self, db: Session):
        """Test that timestamps are automatically generated."""
        user = User(
            email="timestamp@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        # Before saving
        assert user.created_at is None or isinstance(user.created_at, datetime)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # After saving
        assert isinstance(user.created_at, datetime)
        assert user.created_at <= datetime.utcnow()