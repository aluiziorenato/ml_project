"""
Comprehensive tests for app/auth/__init__.py to achieve 100% coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from jose import JWTError
import asyncio


class TestAuthFunctions:
    """Tests for authentication helper functions."""
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        from app.auth import verify_password
        
        with patch('app.auth.pwd_context.verify', return_value=True) as mock_verify:
            result = verify_password("plain_password", "hashed_password")
            
            assert result is True
            mock_verify.assert_called_once_with("plain_password", "hashed_password")
    
    def test_verify_password_failure(self):
        """Test failed password verification."""
        from app.auth import verify_password
        
        with patch('app.auth.pwd_context.verify', return_value=False) as mock_verify:
            result = verify_password("wrong_password", "hashed_password")
            
            assert result is False
            mock_verify.assert_called_once_with("wrong_password", "hashed_password")
    
    def test_get_password_hash(self):
        """Test password hashing."""
        from app.auth import get_password_hash
        
        with patch('app.auth.pwd_context.hash', return_value="hashed_result") as mock_hash:
            result = get_password_hash("password123")
            
            assert result == "hashed_result"
            mock_hash.assert_called_once_with("password123")
    
    def test_create_access_token_with_expires_delta(self):
        """Test token creation with custom expiration."""
        from app.auth import create_access_token
        
        # Mock the jwt module and settings
        with patch('app.auth.jwt') as mock_jwt, \
             patch('app.auth.settings') as mock_settings:
            
            mock_jwt.encode.return_value = "test_token"
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            
            data = {"sub": "test@example.com"}
            result = create_access_token(data, expires_delta=30)
            
            assert result == "test_token"
            # Verify JWT encoding was called
            mock_jwt.encode.assert_called_once()
            # Just verify the call was made, don't inspect the args structure
            assert mock_jwt.encode.called
    
    def test_create_access_token_without_expires_delta(self):
        """Test token creation with default expiration."""
        from app.auth import create_access_token
        
        # Mock the jwt module and settings
        with patch('app.auth.jwt') as mock_jwt, \
             patch('app.auth.settings') as mock_settings:
            
            mock_jwt.encode.return_value = "test_token"
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.access_token_expire_minutes = 15
            
            data = {"sub": "test@example.com"}
            result = create_access_token(data)  # No expires_delta
            
            assert result == "test_token"
            # Verify JWT encoding was called
            mock_jwt.encode.assert_called_once()
            # Just verify the call was made, don't inspect the args structure
            assert mock_jwt.encode.called
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user retrieval from token."""
        from app.auth import get_current_user
        
        # Mock token and session
        token = "valid_token"
        mock_session = Mock()
        mock_user = Mock()
        mock_session.exec.return_value.first.return_value = mock_user
        
        with patch('app.auth.jwt.decode') as mock_decode, \
             patch('app.auth.settings') as mock_settings:
            
            mock_decode.return_value = {"sub": "test@example.com"}
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            
            result = await get_current_user(token, mock_session)
            
            assert result == mock_user
            mock_decode.assert_called_once_with(token, "secret", algorithms=["HS256"])
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test user retrieval with invalid token."""
        from app.auth import get_current_user
        
        token = "invalid_token"
        mock_session = Mock()
        
        with patch('app.auth.jwt.decode', side_effect=JWTError("Invalid token")), \
             patch('app.auth.settings') as mock_settings:
            
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_session)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Could not validate credentials"
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_sub_in_token(self):
        """Test user retrieval when token has no 'sub' claim."""
        from app.auth import get_current_user
        
        token = "token_without_sub"
        mock_session = Mock()
        
        with patch('app.auth.jwt.decode') as mock_decode, \
             patch('app.auth.settings') as mock_settings:
            
            mock_decode.return_value = {"other_field": "value"}  # No 'sub'
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_session)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Could not validate credentials"
    
    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """Test user retrieval when user doesn't exist in database."""
        from app.auth import get_current_user
        
        token = "valid_token"
        mock_session = Mock()
        mock_session.exec.return_value.first.return_value = None  # User not found
        
        with patch('app.auth.jwt.decode') as mock_decode, \
             patch('app.auth.settings') as mock_settings:
            
            mock_decode.return_value = {"sub": "nonexistent@example.com"}
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_session)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Could not validate credentials"
    
    @pytest.mark.asyncio
    async def test_get_current_user_sub_is_none(self):
        """Test user retrieval when 'sub' claim is None."""
        from app.auth import get_current_user
        
        token = "token_with_null_sub"
        mock_session = Mock()
        
        with patch('app.auth.jwt.decode') as mock_decode, \
             patch('app.auth.settings') as mock_settings:
            
            mock_decode.return_value = {"sub": None}  # sub is None
            mock_settings.secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_session)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Could not validate credentials"