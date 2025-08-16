"""
Comprehensive tests for app/auth/token.py to achieve 100% coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
import sqlalchemy.exc


class TestTokenAuthentication:
    """Tests for token authentication endpoint."""
    
    def test_login_for_access_token_success(self):
        """Test successful login with valid credentials."""
        from app.auth.token import login_for_access_token
        
        # Mock form data
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "test@example.com"
        form_data.password = "testpassword"
        
        # Mock session and user
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_session.exec.return_value.first.return_value = mock_user
        
        # Mock password verification and token creation
        with patch('app.auth.token.verify_password', return_value=True) as mock_verify, \
             patch('app.auth.token.create_access_token', return_value="test_token") as mock_create_token:
            
            result = login_for_access_token(form_data, mock_session)
            
            # Verify results
            assert result == {"access_token": "test_token", "token_type": "bearer"}
            mock_verify.assert_called_once_with("testpassword", "hashed_password")
            mock_create_token.assert_called_once_with(data={"sub": "test@example.com"})
    
    def test_login_for_access_token_user_not_found(self):
        """Test login failure when user doesn't exist."""
        from app.auth.token import login_for_access_token
        
        # Mock form data
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "nonexistent@example.com"
        form_data.password = "testpassword"
        
        # Mock session returning no user
        mock_session = Mock(spec=Session)
        mock_session.exec.return_value.first.return_value = None
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            login_for_access_token(form_data, mock_session)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Incorrect username or password"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_login_for_access_token_wrong_password(self):
        """Test login failure with wrong password."""
        from app.auth.token import login_for_access_token
        
        # Mock form data
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "test@example.com"
        form_data.password = "wrongpassword"
        
        # Mock session and user
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_session.exec.return_value.first.return_value = mock_user
        
        # Mock password verification to return False
        with patch('app.auth.token.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                login_for_access_token(form_data, mock_session)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Incorrect username or password"
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_login_for_access_token_user_exists_but_no_password_match(self):
        """Test when user exists but password verification fails."""
        from app.auth.token import login_for_access_token
        
        # Mock form data
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "test@example.com"
        form_data.password = "testpassword"
        
        # Mock session and user
        mock_session = Mock(spec=Session)
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_session.exec.return_value.first.return_value = mock_user
        
        # Mock verify_password to return False (wrong password)
        with patch('app.auth.token.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                login_for_access_token(form_data, mock_session)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Incorrect username or password"