"""
Test coverage for app/models.py to achieve 100% coverage.
Tests model creation, validation, field types, and database operations.
"""

import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from app.models import User, OAuthSession, ApiTest


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, db_session: Session):
        """Test creating a User instance."""
        user = User(
            email="test@example.com",
            hashed_password="hashedpassword123",
            is_active=True,
            is_superuser=False
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashedpassword123"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
    
    def test_user_defaults(self, db_session: Session):
        """Test User model default values."""
        user = User(
            email="default@example.com",
            hashed_password="password"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test default values
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
    
    def test_user_superuser_creation(self, db_session: Session):
        """Test creating a superuser."""
        superuser = User(
            email="admin@example.com",
            hashed_password="adminpassword",
            is_active=True,
            is_superuser=True
        )
        
        db_session.add(superuser)
        db_session.commit()
        db_session.refresh(superuser)
        
        assert superuser.is_superuser is True
        assert superuser.is_active is True
    
    def test_user_inactive_creation(self, db_session: Session):
        """Test creating an inactive user."""
        inactive_user = User(
            email="inactive@example.com",
            hashed_password="password",
            is_active=False
        )
        
        db_session.add(inactive_user)
        db_session.commit()
        db_session.refresh(inactive_user)
        
        assert inactive_user.is_active is False
        assert inactive_user.is_superuser is False


class TestOAuthSessionModel:
    """Test OAuthSession model functionality."""
    
    def test_oauth_session_creation(self, db_session: Session):
        """Test creating an OAuthSession instance."""
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="test_state_123",
            code_verifier="test_code_verifier",
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="bearer",
            expires_at=datetime.now()
        )
        
        db_session.add(oauth_session)
        db_session.commit()
        db_session.refresh(oauth_session)
        
        assert oauth_session.id is not None
        assert oauth_session.endpoint_id == 1
        assert oauth_session.state == "test_state_123"
        assert oauth_session.code_verifier == "test_code_verifier"
        assert oauth_session.access_token == "access_token_123"
        assert oauth_session.refresh_token == "refresh_token_123"
        assert oauth_session.token_type == "bearer"
        assert isinstance(oauth_session.created_at, datetime)
        assert isinstance(oauth_session.expires_at, datetime)
    
    def test_oauth_session_minimal_creation(self, db_session: Session):
        """Test creating an OAuthSession with minimal required fields."""
        oauth_session = OAuthSession(
            endpoint_id=2,
            state="minimal_state",
            code_verifier="minimal_verifier"
        )
        
        db_session.add(oauth_session)
        db_session.commit()
        db_session.refresh(oauth_session)
        
        assert oauth_session.endpoint_id == 2
        assert oauth_session.state == "minimal_state"
        assert oauth_session.code_verifier == "minimal_verifier"
        assert oauth_session.access_token is None
        assert oauth_session.refresh_token is None
        assert oauth_session.token_type is None
        assert oauth_session.expires_at is None
        assert isinstance(oauth_session.created_at, datetime)
    
    def test_oauth_session_with_tokens(self, db_session: Session):
        """Test OAuth session with complete token information."""
        expires_at = datetime.now()
        oauth_session = OAuthSession(
            endpoint_id=3,
            state="full_state",
            code_verifier="full_verifier",
            access_token="full_access_token",
            refresh_token="full_refresh_token",
            token_type="Bearer",
            expires_at=expires_at
        )
        
        db_session.add(oauth_session)
        db_session.commit()
        db_session.refresh(oauth_session)
        
        assert oauth_session.access_token == "full_access_token"
        assert oauth_session.refresh_token == "full_refresh_token"
        assert oauth_session.token_type == "Bearer"
        assert oauth_session.expires_at == expires_at


class TestApiTestModel:
    """Test ApiTest model functionality."""
    
    def test_api_test_creation(self, db_session: Session):
        """Test creating an ApiTest instance."""
        api_test = ApiTest(
            endpoint_id=1,
            name="Test API Endpoint",
            request_method="POST",
            request_path="/api/test",
            request_headers='{"Content-Type": "application/json"}',
            request_body='{"key": "value"}',
            status_code=200,
            response_body='{"result": "success"}'
        )
        
        db_session.add(api_test)
        db_session.commit()
        db_session.refresh(api_test)
        
        assert api_test.id is not None
        assert api_test.endpoint_id == 1
        assert api_test.name == "Test API Endpoint"
        assert api_test.request_method == "POST"
        assert api_test.request_path == "/api/test"
        assert api_test.request_headers == '{"Content-Type": "application/json"}'
        assert api_test.request_body == '{"key": "value"}'
        assert api_test.status_code == 200
        assert api_test.response_body == '{"result": "success"}'
        assert isinstance(api_test.executed_at, datetime)
    
    def test_api_test_defaults(self, db_session: Session):
        """Test ApiTest model default values."""
        api_test = ApiTest()
        
        db_session.add(api_test)
        db_session.commit()
        db_session.refresh(api_test)
        
        # Test default values
        assert api_test.endpoint_id is None
        assert api_test.name is None
        assert api_test.request_method == "GET"
        assert api_test.request_path == "/"
        assert api_test.request_headers is None
        assert api_test.request_body is None
        assert api_test.status_code is None
        assert api_test.response_body is None
        assert isinstance(api_test.executed_at, datetime)
    
    def test_api_test_with_endpoint_id(self, db_session: Session):
        """Test ApiTest with endpoint_id."""
        api_test = ApiTest(
            endpoint_id=99,
            name="Endpoint Test",
            request_method="PUT",
            request_path="/api/endpoint/99"
        )
        
        db_session.add(api_test)
        db_session.commit()
        db_session.refresh(api_test)
        
        assert api_test.endpoint_id == 99
        assert api_test.name == "Endpoint Test"
        assert api_test.request_method == "PUT"
        assert api_test.request_path == "/api/endpoint/99"
    
    def test_api_test_different_methods(self, db_session: Session):
        """Test ApiTest with different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            api_test = ApiTest(
                name=f"Test {method}",
                request_method=method,
                request_path=f"/api/{method.lower()}"
            )
            
            db_session.add(api_test)
            db_session.commit()
            db_session.refresh(api_test)
            
            assert api_test.request_method == method
            assert api_test.request_path == f"/api/{method.lower()}"
    
    def test_api_test_status_codes(self, db_session: Session):
        """Test ApiTest with various status codes."""
        status_codes = [200, 201, 400, 401, 404, 500]
        
        for status_code in status_codes:
            api_test = ApiTest(
                name=f"Test Status {status_code}",
                status_code=status_code
            )
            
            db_session.add(api_test)
            db_session.commit()
            db_session.refresh(api_test)
            
            assert api_test.status_code == status_code


class TestModelsIntegration:
    """Test integration between different models."""
    
    def test_multiple_models_creation(self, db_session: Session):
        """Test creating multiple model instances in the same session."""
        # Create a user
        user = User(
            email="integration@example.com",
            hashed_password="password"
        )
        db_session.add(user)
        db_session.flush()  # Get the ID without committing
        
        # Create an OAuth session
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="integration_state",
            code_verifier="integration_verifier"
        )
        db_session.add(oauth_session)
        db_session.flush()
        
        # Create an API test
        api_test = ApiTest(
            endpoint_id=oauth_session.endpoint_id,
            name="Integration Test"
        )
        db_session.add(api_test)
        
        db_session.commit()
        
        # Verify all models were created
        assert user.id is not None
        assert oauth_session.id is not None
        assert api_test.id is not None
        assert api_test.endpoint_id == oauth_session.endpoint_id
    
    def test_model_field_types(self, db_session: Session):
        """Test that all model fields have correct types."""
        # Test User model field types
        user = User(email="type@example.com", hashed_password="password")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert isinstance(user.id, int)
        assert isinstance(user.email, str)
        assert isinstance(user.hashed_password, str)
        assert isinstance(user.is_active, bool)
        assert isinstance(user.is_superuser, bool)
        assert isinstance(user.created_at, datetime)
        
        # Test OAuthSession field types
        oauth = OAuthSession(endpoint_id=1, state="test", code_verifier="test")
        db_session.add(oauth)
        db_session.commit()
        db_session.refresh(oauth)
        
        assert isinstance(oauth.id, int)
        assert isinstance(oauth.endpoint_id, int)
        assert isinstance(oauth.state, str)
        assert isinstance(oauth.code_verifier, str)
        assert isinstance(oauth.created_at, datetime)
        
        # Test ApiTest field types
        api_test = ApiTest()
        db_session.add(api_test)
        db_session.commit()
        db_session.refresh(api_test)
        
        assert isinstance(api_test.id, int)
        assert isinstance(api_test.request_method, str)
        assert isinstance(api_test.request_path, str)
        assert isinstance(api_test.executed_at, datetime)