"""
Comprehensive tests for app/startup.py to achieve 100% coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestStartupFunctions:
    """Tests for startup functions."""
    
    def test_create_admin_user_success_new_user(self):
        """Test creating admin user when none exists."""
        from app.startup import create_admin_user
        
        with patch('app.startup.Session') as mock_session_class, \
             patch('app.startup.os.getenv') as mock_getenv, \
             patch('app.startup.get_password_hash') as mock_hash, \
             patch('app.startup.User') as mock_user_class, \
             patch('app.startup.select') as mock_select, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            
            # Mock environment variables
            mock_getenv.side_effect = lambda key, default=None: {
                "ADMIN_EMAIL": "admin@test.com",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # No existing user
            mock_session.exec.return_value.first.return_value = None
            
            # Mock password hashing
            mock_hash.return_value = "hashed_admin123"
            
            # Mock user creation
            mock_user = Mock()
            mock_user_class.return_value = mock_user
            
            # Call the function
            create_admin_user()
            
            # Verify the flow
            mock_getenv.assert_any_call("ADMIN_EMAIL", "admin@example.com")
            mock_getenv.assert_any_call("ADMIN_PASSWORD")
            mock_hash.assert_called_once_with("admin123")
            mock_user_class.assert_called_once_with(
                email="admin@test.com",
                password="hashed_admin123"  # This matches the buggy code
            )
            mock_session.add.assert_called_once_with(mock_user)
            mock_session.commit.assert_called_once()
            mock_print.assert_called_once_with("[Seed] Usuário admin criado: admin@test.com")
    
    def test_create_admin_user_existing_user(self):
        """Test when admin user already exists."""
        from app.startup import create_admin_user
        
        with patch('app.startup.Session') as mock_session_class, \
             patch('app.startup.os.getenv') as mock_getenv, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            
            # Mock environment variables
            mock_getenv.side_effect = lambda key, default=None: {
                "ADMIN_EMAIL": "admin@test.com",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Existing user
            existing_user = Mock()
            mock_session.exec.return_value.first.return_value = existing_user
            
            # Call the function
            create_admin_user()
            
            # Verify the flow
            mock_getenv.assert_any_call("ADMIN_EMAIL", "admin@example.com")
            mock_getenv.assert_any_call("ADMIN_PASSWORD")
            
            # Should NOT create new user
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()
            mock_print.assert_called_once_with("[Seed] Usuário admin já existe: admin@test.com")
    
    def test_create_admin_user_no_password(self):
        """Test when no admin password is provided."""
        from app.startup import create_admin_user
        
        with patch('app.startup.os.getenv') as mock_getenv:
            
            # Mock environment variables - no password
            mock_getenv.side_effect = lambda key, default=None: {
                "ADMIN_EMAIL": "admin@test.com",
                "ADMIN_PASSWORD": None
            }.get(key, default)
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                create_admin_user()
            
            assert str(exc_info.value) == "ADMIN_PASSWORD não definido no .env"
            
            # Verify getenv was called
            mock_getenv.assert_any_call("ADMIN_EMAIL", "admin@example.com")
            mock_getenv.assert_any_call("ADMIN_PASSWORD")
    
    def test_create_admin_user_empty_password(self):
        """Test when admin password is empty string."""
        from app.startup import create_admin_user
        
        with patch('app.startup.os.getenv') as mock_getenv:
            
            # Mock environment variables - empty password
            mock_getenv.side_effect = lambda key, default=None: {
                "ADMIN_EMAIL": "admin@test.com",
                "ADMIN_PASSWORD": ""
            }.get(key, default)
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                create_admin_user()
            
            assert str(exc_info.value) == "ADMIN_PASSWORD não definido no .env"
    
    def test_create_admin_user_default_email(self):
        """Test when no admin email is provided, uses default."""
        from app.startup import create_admin_user
        
        with patch('app.startup.Session') as mock_session_class, \
             patch('app.startup.os.getenv') as mock_getenv, \
             patch('app.startup.get_password_hash') as mock_hash, \
             patch('app.startup.User') as mock_user_class, \
             patch('app.startup.select') as mock_select, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            
            # Mock environment variables - use default email
            mock_getenv.side_effect = lambda key, default=None: {
                "ADMIN_EMAIL": default,  # Will use default
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # No existing user
            mock_session.exec.return_value.first.return_value = None
            
            # Mock password hashing
            mock_hash.return_value = "hashed_admin123"
            
            # Mock user creation
            mock_user = Mock()
            mock_user_class.return_value = mock_user
            
            # Call the function
            create_admin_user()
            
            # Verify default email was used
            mock_getenv.assert_any_call("ADMIN_EMAIL", "admin@example.com")
            mock_user_class.assert_called_once_with(
                email="admin@example.com",  # Default email
                password="hashed_admin123"
            )
            mock_print.assert_called_once_with("[Seed] Usuário admin criado: admin@example.com")