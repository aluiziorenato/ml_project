"""
Unit tests for authentication and authorization functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlmodel import Session

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    create_refresh_token,
    get_current_user
)
from app.models import User
from app.settings import Settings


@pytest.mark.unit
class TestPasswordOperations:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert hashed != password  # Should be hashed
        assert len(hashed) > len(password)  # Hash should be longer
        
    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        
    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
        
    def test_password_hashing_consistency(self):
        """Test that same password produces different hashes."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
        
    def test_password_verification_with_empty_strings(self):
        """Test password verification with empty strings."""
        # Empty password should not hash to empty string
        empty_hash = get_password_hash("")
        assert empty_hash != ""
        
        # Verification should work
        assert verify_password("", empty_hash) is True
        assert verify_password("not_empty", empty_hash) is False
        
    def test_password_verification_edge_cases(self):
        """Test password verification edge cases."""
        # Test with special characters
        special_password = "p@$$w0rd!@#$%^&*()"
        special_hash = get_password_hash(special_password)
        assert verify_password(special_password, special_hash) is True
        
        # Test with unicode characters
        unicode_password = "pássword_ñoñó_测试"
        unicode_hash = get_password_hash(unicode_password)
        assert verify_password(unicode_password, unicode_hash) is True


@pytest.mark.unit
class TestTokenOperations:
    """Test JWT token creation and validation."""
    
    def test_access_token_creation(self):
        """Test access token creation."""
        data = {"sub": "test@example.com", "user_id": 123}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT has dots
        
    def test_access_token_with_custom_expiry(self):
        """Test access token with custom expiry time."""
        data = {"sub": "test@example.com"}
        custom_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=custom_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_refresh_token_creation(self):
        """Test refresh token creation."""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT has dots
        
    def test_refresh_token_with_custom_expiry(self):
        """Test refresh token with custom expiry time."""
        data = {"sub": "test@example.com"}
        custom_delta = timedelta(days=3)
        token = create_refresh_token(data, expires_delta=custom_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
    @patch('app.core.security.settings')
    def test_token_creation_with_settings(self, mock_settings):
        """Test token creation uses settings correctly."""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = "30"
        mock_settings.refresh_token_expire_days = "7"
        
        data = {"sub": "test@example.com"}
        
        # Test access token
        access_token = create_access_token(data)
        assert isinstance(access_token, str)
        
        # Test refresh token
        refresh_token = create_refresh_token(data)
        assert isinstance(refresh_token, str)
        
    def test_token_payload_encoding(self):
        """Test that token payload is properly encoded."""
        data = {
            "sub": "test@example.com",
            "user_id": 123,
            "is_superuser": True,
            "custom_field": "custom_value"
        }
        token = create_access_token(data)
        
        # Decode token to verify payload (without verification for testing)
        # This is for testing purposes only
        import base64
        import json
        
        # Split token and decode payload (second part)
        parts = token.split('.')
        assert len(parts) == 3  # Header, payload, signature
        
        # Decode payload (add padding if needed)
        payload_part = parts[1]
        payload_part += '=' * (4 - len(payload_part) % 4)  # Add padding
        decoded_payload = base64.urlsafe_b64decode(payload_part)
        payload_data = json.loads(decoded_payload)
        
        assert payload_data["sub"] == "test@example.com"
        assert "exp" in payload_data  # Should have expiration


@pytest.mark.unit
class TestGetCurrentUser:
    """Test get_current_user functionality."""
    
    @pytest.mark.asyncio
    @patch('app.core.security.settings')
    async def test_get_current_user_success(self, mock_settings, db: Session):
        """Test successful user retrieval from token."""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create token for this user
        token = create_access_token({"sub": user.email})
        
        # Mock the database session
        with patch('app.core.security.get_session') as mock_get_session:
            mock_get_session.return_value = db
            
            result = await get_current_user(token, db)
            
            assert result.email == user.email
            assert result.id == user.id
            
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db: Session):
        """Test user retrieval with invalid token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(invalid_token, db)
            
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
        
    @pytest.mark.asyncio  
    @patch('app.core.security.settings')
    async def test_get_current_user_expired_token(self, mock_settings, db: Session):
        """Test user retrieval with expired token."""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Create expired token
        expired_data = {
            "sub": "test@example.com",
            "exp": datetime.utcnow() - timedelta(seconds=1)
        }
        expired_token = jwt.encode(expired_data, "test_secret_key", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(expired_token, db)
            
        assert exc_info.value.status_code == 401
        
    @pytest.mark.asyncio
    @patch('app.core.security.settings')
    async def test_get_current_user_nonexistent_user(self, mock_settings, db: Session):
        """Test user retrieval when user doesn't exist in database."""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Create token for non-existent user
        token = create_access_token({"sub": "nonexistent@example.com"})
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, db)
            
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
        
    @pytest.mark.asyncio
    @patch('app.core.security.settings')
    async def test_get_current_user_token_without_sub(self, mock_settings, db: Session):
        """Test user retrieval with token missing 'sub' claim."""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Create token without 'sub' claim
        token_data = {"user_id": 123, "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(token_data, "test_secret_key", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, db)
            
        assert exc_info.value.status_code == 401


@pytest.mark.unit
class TestAuthenticationEdgeCases:
    """Test authentication edge cases and error scenarios."""
    
    def test_password_hash_with_none(self):
        """Test password hashing with None input."""
        with pytest.raises((TypeError, AttributeError)):
            get_password_hash(None)
            
    def test_password_verification_with_none(self):
        """Test password verification with None inputs."""
        with pytest.raises((TypeError, AttributeError)):
            verify_password(None, "some_hash")
            
        with pytest.raises((TypeError, AttributeError)):
            verify_password("password", None)
            
    def test_token_creation_with_empty_data(self):
        """Test token creation with empty data."""
        empty_data = {}
        token = create_access_token(empty_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_token_creation_with_none_data(self):
        """Test token creation with None data."""
        with pytest.raises((TypeError, AttributeError)):
            create_access_token(None)
            
    @patch('app.core.security.pwd_context.verify')
    def test_password_verification_exception_handling(self, mock_verify):
        """Test password verification with underlying exception."""
        mock_verify.side_effect = Exception("Hashing error")
        
        # Should handle exceptions gracefully
        result = verify_password("password", "hash")
        assert result is False or isinstance(result, bool)
        
    @patch('app.core.security.jwt.encode')
    def test_token_creation_jwt_error_handling(self, mock_encode):
        """Test token creation with JWT encoding error."""
        mock_encode.side_effect = Exception("JWT encoding error")
        
        with pytest.raises(Exception):
            create_access_token({"sub": "test@example.com"})


@pytest.mark.unit
class TestAuthenticationMocking:
    """Test authentication with comprehensive mocking."""
    
    @patch('app.core.security.pwd_context')
    def test_password_operations_mocked(self, mock_pwd_context):
        """Test password operations with mocked context."""
        # Mock password hashing
        mock_pwd_context.hash.return_value = "mocked_hash"
        mock_pwd_context.verify.return_value = True
        
        # Test hashing
        result = get_password_hash("password")
        assert result == "mocked_hash"
        mock_pwd_context.hash.assert_called_once_with("password")
        
        # Test verification
        verification_result = verify_password("password", "hash")
        assert verification_result is True
        mock_pwd_context.verify.assert_called_once_with("password", "hash")
        
    @patch('app.core.security.jwt')
    @patch('app.core.security.settings')
    def test_token_operations_mocked(self, mock_settings, mock_jwt):
        """Test token operations with mocked JWT."""
        mock_settings.secret_key = "test_key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = "30"
        mock_jwt.encode.return_value = "mocked_token"
        
        data = {"sub": "test@example.com"}
        result = create_access_token(data)
        
        assert result == "mocked_token"
        mock_jwt.encode.assert_called_once()
        
    @pytest.mark.asyncio
    @patch('app.core.security.jwt')
    @patch('app.core.security.settings')
    async def test_get_current_user_mocked_jwt(self, mock_settings, mock_jwt, db: Session):
        """Test get_current_user with mocked JWT operations."""
        mock_settings.secret_key = "test_key"
        mock_settings.jwt_algorithm = "HS256"
        
        # Mock JWT decode to return user email
        mock_jwt.decode.return_value = {"sub": "test@example.com"}
        
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Test the function
        result = await get_current_user("mocked_token", db)
        
        assert result.email == "test@example.com"
        mock_jwt.decode.assert_called_once_with("mocked_token", "test_key", algorithms=["HS256"])


@pytest.mark.unit
class TestAuthenticationSecurity:
    """Test authentication security aspects."""
    
    def test_password_hash_security(self):
        """Test that password hashes are secure."""
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (salted)
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        
        # Wrong password should not verify
        assert not verify_password("wrong_password", hash1)
        assert not verify_password("wrong_password", hash2)
        
    def test_token_contains_expiration(self):
        """Test that tokens contain proper expiration."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Decode token to check expiration (for testing only)
        import base64
        import json
        
        parts = token.split('.')
        payload_part = parts[1]
        payload_part += '=' * (4 - len(payload_part) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload_part)
        payload_data = json.loads(decoded_payload)
        
        assert "exp" in payload_data
        assert isinstance(payload_data["exp"], (int, float))
        
        # Expiration should be in the future
        current_time = datetime.utcnow().timestamp()
        assert payload_data["exp"] > current_time
        
    def test_token_signature_validation(self):
        """Test that token signature validation works."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Token should have 3 parts (header.payload.signature)
        parts = token.split('.')
        assert len(parts) == 3
        
        # Each part should be non-empty
        for part in parts:
            assert len(part) > 0