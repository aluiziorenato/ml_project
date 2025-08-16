"""
Unit tests for authentication and security modules.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from jose import jwt
from fastapi import HTTPException

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    _create_token
)
from app.auth import (
    verify_password as auth_verify_password,
    get_password_hash as auth_get_password_hash,
    create_access_token as auth_create_access_token,
    get_current_user as auth_get_current_user
)
from app.config import settings
from app.models import User


@pytest.mark.unit
class TestPasswordFunctions:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_password_verification_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_hashing_different_passwords(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_password_hashing_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "same_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Different hashes due to salt, but both verify correctly
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestTokenFunctions:
    """Test JWT token creation and validation."""
    
    def test_create_access_token_basic(self):
        """Test basic access token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload
    
    def test_create_access_token_with_expiration(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + expires_delta
        
        # Allow 1 second tolerance
        assert abs((exp_time - expected_time).total_seconds()) < 1
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "test@example.com"
        
        # Should have longer expiration than access token
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        assert abs((exp_time - expected_time).total_seconds()) < 60  # 1 minute tolerance
    
    def test_create_token_internal(self):
        """Test internal token creation function."""
        data = {"sub": "test@example.com", "role": "user"}
        expires_delta = timedelta(hours=1)
        
        token = _create_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "user"
        assert "exp" in payload
    
    def test_token_expiration_validation(self):
        """Test that expired tokens are rejected."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        expired_token = _create_token(data, expires_delta)
        
        from jose import ExpiredSignatureError
        with pytest.raises(ExpiredSignatureError):
            jwt.decode(expired_token, settings.secret_key, algorithms=[settings.jwt_algorithm])


@pytest.mark.unit
class TestGetCurrentUser:
    """Test user authentication from token."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, session, test_user):
        """Test getting current user with valid token."""
        # Create valid token
        token = create_access_token({"sub": test_user.email})
        
        # Mock session dependency
        user = await get_current_user(token, session)
        
        assert user.email == test_user.email
        assert user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, session):
        """Test getting current user with invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(invalid_token, session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, session):
        """Test getting current user for non-existent user."""
        # Create token for non-existent user
        token = create_access_token({"sub": "nonexistent@example.com"})
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, session)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_token_missing_sub(self, session):
        """Test getting current user with token missing 'sub' claim."""
        # Create token without 'sub' claim
        token = _create_token({"user_id": "123"}, timedelta(minutes=30))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, session)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, session, test_user):
        """Test getting current user with expired token."""
        # Create expired token
        expired_token = _create_token({"sub": test_user.email}, timedelta(seconds=-1))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(expired_token, session)
        
        assert exc_info.value.status_code == 401


@pytest.mark.unit
class TestAuthModuleFunctions:
    """Test functions from app.auth module."""
    
    def test_auth_password_hashing(self):
        """Test password hashing from auth module."""
        password = "test_password_456"
        hashed = auth_get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")
    
    def test_auth_password_verification(self):
        """Test password verification from auth module."""
        password = "test_password_456"
        hashed = auth_get_password_hash(password)
        
        assert auth_verify_password(password, hashed) is True
        assert auth_verify_password("wrong_password", hashed) is False
    
    def test_auth_create_access_token(self):
        """Test access token creation from auth module."""
        data = {"sub": "auth_test@example.com"}
        token = auth_create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "auth_test@example.com"
    
    def test_auth_create_access_token_with_expiration(self):
        """Test access token creation with custom expiration from auth module."""
        data = {"sub": "auth_test@example.com"}
        expires_minutes = 45
        token = auth_create_access_token(data, expires_minutes)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + timedelta(minutes=expires_minutes)
        
        # Allow 1 second tolerance
        assert abs((exp_time - expected_time).total_seconds()) < 1
    
    @pytest.mark.asyncio
    async def test_auth_get_current_user(self, session, test_user):
        """Test getting current user from auth module."""
        token = auth_create_access_token({"sub": test_user.email})
        
        user = await auth_get_current_user(token, session)
        
        assert user.email == test_user.email
        assert user.id == test_user.id


@pytest.mark.unit
class TestSecurityEdgeCases:
    """Test edge cases and error handling in security functions."""
    
    def test_empty_password_hashing(self):
        """Test hashing empty password."""
        empty_password = ""
        hashed = get_password_hash(empty_password)
        
        assert hashed != empty_password
        assert verify_password(empty_password, hashed) is True
    
    def test_unicode_password_handling(self):
        """Test handling of unicode characters in passwords."""
        unicode_password = "пароль123🔒"
        hashed = get_password_hash(unicode_password)
        
        assert verify_password(unicode_password, hashed) is True
        assert verify_password("пароль123🔐", hashed) is False  # Different emoji
    
    def test_very_long_password(self):
        """Test handling of very long passwords."""
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)
        
        assert verify_password(long_password, hashed) is True
        assert verify_password("a" * 999, hashed) is False
    
    def test_token_with_extra_claims(self):
        """Test token creation with additional claims."""
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write"],
            "custom_field": "custom_value"
        }
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
        assert payload["custom_field"] == "custom_value"
    
    @patch('app.core.security.settings')
    def test_token_creation_with_different_settings(self, mock_settings):
        """Test token creation with different settings."""
        mock_settings.secret_key = "different_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 120
        
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, "different_secret_key", algorithms=["HS256"])
        assert payload["sub"] == "test@example.com"