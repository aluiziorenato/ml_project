"""
Tests for previously untested modules to achieve higher coverage.
"""
import pytest
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import patch, Mock

from app.models import User
from app.models.api_test import ApiTest
from app.auth.token import router as token_router
from app.crud.tests import create_test, list_tests
from app.auth import verify_password, get_password_hash, create_access_token


class TestAuthToken:
    """Test auth token module (app/auth/token.py)."""
    
    def test_login_for_access_token_success(self, client: TestClient, test_user: User):
        """Test successful login with correct credentials."""
        form_data = {
            "username": test_user.email,
            "password": "testpassword"  # This matches the test_user fixture
        }
        
        response = client.post("/api/auth/token", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_for_access_token_invalid_username(self, client: TestClient):
        """Test login with invalid username."""
        form_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = client.post("/api/auth/token", data=form_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"
    
    def test_login_for_access_token_invalid_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password."""
        form_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/token", data=form_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"
    
    def test_login_for_access_token_missing_data(self, client: TestClient):
        """Test login with missing form data."""
        response = client.post("/api/auth/token", data={})
        
        assert response.status_code == 422  # Validation error


class TestModelsLegacy:
    """Test legacy models from app/models.py."""
    
    def test_user_model_creation(self):
        """Test User model creation and fields."""
        from app.models import User as LegacyUser
        
        user = LegacyUser(
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False
        )
        
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
    
    def test_api_endpoint_model_creation(self):
        """Test ApiEndpoint model creation and fields."""
        from app.models import ApiEndpoint as LegacyApiEndpoint
        
        endpoint = LegacyApiEndpoint(
            name="Test API",
            base_url="https://api.test.com",
            auth_type="bearer",
            oauth_scope="read"
        )
        
        assert endpoint.name == "Test API"
        assert endpoint.base_url == "https://api.test.com"
        assert endpoint.auth_type == "bearer"
        assert endpoint.oauth_scope == "read"
        assert isinstance(endpoint.created_at, datetime)
    
    def test_oauth_session_model_creation(self):
        """Test OAuthSession model creation and fields."""
        from app.models import OAuthSession as LegacyOAuthSession
        
        session = LegacyOAuthSession(
            state="test_state",
            code_verifier="test_verifier",
            endpoint_id=1
        )
        
        assert session.state == "test_state"
        assert session.code_verifier == "test_verifier"
        assert session.endpoint_id == 1
        assert isinstance(session.created_at, datetime)
    
    def test_api_test_model_creation(self):
        """Test ApiTest model creation and fields."""
        from app.models import ApiTest as LegacyApiTest
        
        test = LegacyApiTest(
            name="Test API Call"
        )
        
        assert test.name == "Test API Call"


class TestCrudTests:
    """Test CRUD operations for tests (app/crud/tests.py)."""
    
    def test_create_test_success(self, session: Session):
        """Test successful test creation."""
        test_data = ApiTest(
            name="Test API Call"
        )
        
        created_test = create_test(session, test_data)
        
        assert created_test.id is not None
        assert created_test.name == "Test API Call"
    
    def test_list_tests_default_limit(self, session: Session):
        """Test listing tests with default limit."""
        # Create multiple tests
        for i in range(3):
            test = ApiTest(
                name=f"Test {i}"
            )
            create_test(session, test)
        
        tests = list_tests(session)
        
        assert len(tests) == 3
    
    def test_list_tests_custom_limit(self, session: Session):
        """Test listing tests with custom limit."""
        # Create multiple tests
        for i in range(5):
            test = ApiTest(
                name=f"Test {i}"
            )
            create_test(session, test)
        
        tests = list_tests(session, limit=3)
        
        assert len(tests) == 3
    
    def test_list_tests_empty_database(self, session: Session):
        """Test listing tests when database is empty."""
        tests = list_tests(session)
        
        assert tests == []


class TestAuthHelpers:
    """Test auth helper functions that might have missing coverage."""
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        plain_password = "testpassword123"
        hashed_password = get_password_hash(plain_password)
        
        result = verify_password(plain_password, hashed_password)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        plain_password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(plain_password)
        
        result = verify_password(wrong_password, hashed_password)
        
        assert result is False
    
    def test_create_access_token_no_expiry(self):
        """Test access token creation without custom expiry."""
        test_data = {"sub": "test@example.com"}
        
        token = create_access_token(test_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # Token should contain JWT structure (3 parts separated by dots)
        assert len(token.split('.')) == 3
    
    def test_create_access_token_custom_expiry(self):
        """Test access token creation with custom expiry."""
        test_data = {"sub": "test@example.com"}
        custom_expiry = 60  # 60 minutes
        
        token = create_access_token(test_data, expires_delta=custom_expiry)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert len(token.split('.')) == 3


class TestDatabaseFunctions:
    """Test database helper functions with missing coverage."""
    
    def test_db_init_functionality(self):
        """Test database initialization functionality."""
        from app.db import _wait_for_db, init_db
        
        # Test wait_for_db with mock
        with patch('app.db.engine') as mock_engine:
            mock_engine.connect.return_value.__enter__.return_value.execute.return_value = None
            
            # Should not raise exception
            _wait_for_db(max_retries=1, delay=0.1)
    
    @patch.dict(os.environ, {'ADMIN_EMAIL': 'test-admin@example.com', 'ADMIN_PASSWORD': 'test123'})
    def test_db_init_with_admin_creation(self):
        """Test database initialization with admin user creation."""
        from app.db import init_db
        
        with patch('app.db._wait_for_db'), \
             patch('app.db.SQLModel') as mock_sqlmodel, \
             patch('app.db.Session') as mock_session_class:
            
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.exec.return_value.first.return_value = None  # No existing admin
            
            init_db()
            
            # Verify SQLModel.metadata.create_all was called
            mock_sqlmodel.metadata.create_all.assert_called_once()
            # Verify admin user creation was attempted
            assert mock_session.add.called
            assert mock_session.commit.called