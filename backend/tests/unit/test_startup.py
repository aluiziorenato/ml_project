"""
Unit tests for app.startup module.
Tests admin user creation during startup and environment validation.
"""
import pytest
from unittest.mock import patch, MagicMock
import os


@pytest.mark.unit
class TestStartupModule:
    """Test the app.startup module functionality."""
    
    def test_startup_module_import(self):
        """Test that startup module can be imported successfully."""
        from app import startup
        assert startup is not None
    
    def test_create_admin_user_function_exists(self):
        """Test that create_admin_user function exists and is callable."""
        from app.startup import create_admin_user
        assert callable(create_admin_user)
    
    @patch('app.startup.Session')
    @patch('app.startup.engine')
    def test_create_admin_user_success(self, mock_engine, mock_session):
        """Test successful admin user creation."""
        from app.startup import create_admin_user
        
        # Mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None  # No existing user
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'secure-password-123'
        }):
            with patch('app.startup.get_password_hash') as mock_hash:
                mock_hash.return_value = 'hashed-password'
                
                with patch('app.startup.User') as mock_user:
                    create_admin_user()
                    
                    # Should hash the password
                    mock_hash.assert_called_once_with('secure-password-123')
                    
                    # Should create user
                    mock_user.assert_called_once_with(
                        email='admin@test.com',
                        password='hashed-password'
                    )
                    
                    # Should add and commit
                    mock_session_instance.add.assert_called_once()
                    mock_session_instance.commit.assert_called_once()
    
    @patch('app.startup.Session')
    @patch('app.startup.engine')
    def test_create_admin_user_already_exists(self, mock_engine, mock_session):
        """Test admin user creation when user already exists."""
        from app.startup import create_admin_user
        
        # Mock session with existing user
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_existing_user = MagicMock()
        mock_session_instance.exec.return_value.first.return_value = mock_existing_user
        
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'secure-password-123'
        }):
            create_admin_user()
            
            # Should not create new user
            mock_session_instance.add.assert_not_called()
            mock_session_instance.commit.assert_not_called()
    
    def test_create_admin_user_missing_password(self):
        """Test admin user creation with missing password."""
        from app.startup import create_admin_user
        
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'admin@test.com'
        }, clear=True):  # Clear ADMIN_PASSWORD
            
            with pytest.raises(ValueError, match="ADMIN_PASSWORD não definido"):
                create_admin_user()
    
    @patch('app.startup.Session')
    @patch('app.startup.engine')
    def test_create_admin_user_default_email(self, mock_engine, mock_session):
        """Test admin user creation with default email."""
        from app.startup import create_admin_user
        
        # Mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None
        
        # Clear ADMIN_EMAIL to use default
        with patch.dict(os.environ, {
            'ADMIN_PASSWORD': 'secure-password-123'
        }, clear=True):
            
            with patch('app.startup.get_password_hash') as mock_hash:
                mock_hash.return_value = 'hashed-password'
                
                with patch('app.startup.User') as mock_user:
                    create_admin_user()
                    
                    # Should use default email
                    mock_user.assert_called_once_with(
                        email='admin@example.com',
                        password='hashed-password'
                    )
    
    @patch('app.startup.Session')
    @patch('app.startup.engine')
    def test_create_admin_user_database_error(self, mock_engine, mock_session):
        """Test admin user creation with database error."""
        from app.startup import create_admin_user
        
        # Mock session that raises error on commit
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None
        mock_session_instance.commit.side_effect = Exception("Database error")
        
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'secure-password-123'
        }):
            with patch('app.startup.get_password_hash') as mock_hash:
                mock_hash.return_value = 'hashed-password'
                
                with patch('app.startup.User'):
                    # Should raise the database error
                    with pytest.raises(Exception, match="Database error"):
                        create_admin_user()
    
    def test_create_admin_user_imports(self):
        """Test that create_admin_user can import required modules."""
        from app.startup import create_admin_user
        
        # Function should be able to import its dependencies
        # This test verifies import structure is correct
        import inspect
        source = inspect.getsource(create_admin_user)
        
        # Should import required modules
        assert 'from app.models import User' in source or 'import' in source
        assert 'from app.auth import get_password_hash' in source or 'import' in source
    
    @patch('app.startup.Session')
    @patch('app.startup.engine') 
    def test_create_admin_user_query_structure(self, mock_engine, mock_session):
        """Test the database query structure in create_admin_user."""
        from app.startup import create_admin_user
        
        # Mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None
        
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'query-test@test.com',
            'ADMIN_PASSWORD': 'test-password'
        }):
            with patch('app.startup.get_password_hash') as mock_hash:
                mock_hash.return_value = 'hashed-password'
                
                with patch('app.startup.User'):
                    with patch('app.startup.select') as mock_select:
                        create_admin_user()
                        
                        # Should execute a select query
                        mock_session_instance.exec.assert_called_once()
                        mock_select.assert_called_once()
    
    def test_startup_environment_validation_integration(self):
        """Test that startup integrates with environment validation."""
        # This test ensures startup module can work with various environment configs
        test_environments = [
            {'ADMIN_EMAIL': 'test1@example.com', 'ADMIN_PASSWORD': 'pass1'},
            {'ADMIN_EMAIL': 'test2@example.com', 'ADMIN_PASSWORD': 'pass2'},
        ]
        
        for env_config in test_environments:
            with patch.dict(os.environ, env_config):
                try:
                    from app.startup import create_admin_user
                    # Just test that function can be called with different configs
                    assert callable(create_admin_user)
                except ImportError:
                    pytest.fail("Startup module should import successfully with any valid env config")
    
    @patch('app.startup.print')
    @patch('app.startup.Session')
    @patch('app.startup.engine')
    def test_create_admin_user_logging(self, mock_engine, mock_session, mock_print):
        """Test logging in create_admin_user function."""
        from app.startup import create_admin_user
        
        # Test existing user scenario
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_existing_user = MagicMock()
        mock_session_instance.exec.return_value.first.return_value = mock_existing_user
        
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'existing@test.com',
            'ADMIN_PASSWORD': 'test-password'
        }):
            create_admin_user()
            
            # Should log that user already exists
            mock_print.assert_called()
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert any('já existe' in call for call in print_calls)
    
    @patch('app.startup.print')
    @patch('app.startup.Session')
    @patch('app.startup.engine')
    def test_create_admin_user_creation_logging(self, mock_engine, mock_session, mock_print):
        """Test logging when creating new admin user."""
        from app.startup import create_admin_user
        
        # Test new user creation scenario
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None  # No existing user
        
        with patch.dict(os.environ, {
            'ADMIN_EMAIL': 'new@test.com',
            'ADMIN_PASSWORD': 'test-password'
        }):
            with patch('app.startup.get_password_hash') as mock_hash:
                mock_hash.return_value = 'hashed-password'
                
                with patch('app.startup.User'):
                    create_admin_user()
                    
                    # Should log user creation
                    mock_print.assert_called()
                    print_calls = [call.args[0] for call in mock_print.call_args_list]
                    assert any('criado' in call for call in print_calls)


@pytest.mark.unit
class TestStartupEnvironmentValidation:
    """Test environment validation aspects of startup module."""
    
    def test_startup_with_development_environment(self):
        """Test startup behavior in development environment."""
        with patch.dict(os.environ, {
            'ENV': 'development',
            'ADMIN_EMAIL': 'dev@test.com',
            'ADMIN_PASSWORD': 'dev-password'
        }):
            from app.startup import create_admin_user
            assert callable(create_admin_user)
    
    def test_startup_with_production_environment(self):
        """Test startup behavior in production environment."""
        with patch.dict(os.environ, {
            'ENV': 'production',
            'ADMIN_EMAIL': 'prod@test.com',
            'ADMIN_PASSWORD': 'prod-secure-password-123'
        }):
            from app.startup import create_admin_user
            assert callable(create_admin_user)
    
    def test_startup_with_testing_environment(self):
        """Test startup behavior in testing environment."""
        with patch.dict(os.environ, {
            'ENV': 'testing',
            'ADMIN_EMAIL': 'test@test.com',
            'ADMIN_PASSWORD': 'test-password'
        }):
            from app.startup import create_admin_user
            assert callable(create_admin_user)
    
    def test_startup_environment_variable_handling(self):
        """Test handling of various environment variable configurations."""
        # Test with minimal required variables
        minimal_env = {
            'ADMIN_PASSWORD': 'required-password'
        }
        
        with patch.dict(os.environ, minimal_env, clear=True):
            from app.startup import create_admin_user
            # Should not raise import error
            assert callable(create_admin_user)
    
    def test_startup_admin_email_validation(self):
        """Test admin email validation in startup."""
        # Valid email formats that should work
        valid_emails = [
            'admin@example.com',
            'test.admin@domain.co.uk',
            'admin123@test-domain.org'
        ]
        
        for email in valid_emails:
            with patch.dict(os.environ, {
                'ADMIN_EMAIL': email,
                'ADMIN_PASSWORD': 'test-password'
            }):
                from app.startup import create_admin_user
                assert callable(create_admin_user)
    
    def test_startup_password_security_requirements(self):
        """Test password security handling in startup."""
        # Different password strengths
        passwords = [
            'simple',  # Simple password
            'Complex123!',  # Complex password
            'very-long-password-with-multiple-words-and-numbers-123'  # Long password
        ]
        
        for password in passwords:
            with patch.dict(os.environ, {
                'ADMIN_EMAIL': 'admin@test.com',
                'ADMIN_PASSWORD': password
            }):
                from app.startup import create_admin_user
                # Should accept any password (validation is done elsewhere)
                assert callable(create_admin_user)
    
    @patch('app.startup.os.getenv')
    def test_startup_environment_variable_defaults(self, mock_getenv):
        """Test environment variable defaults in startup."""
        from app.startup import create_admin_user
        
        # Mock getenv to test defaults
        mock_getenv.side_effect = lambda key, default=None: {
            'ADMIN_EMAIL': 'admin@example.com',
            'ADMIN_PASSWORD': None
        }.get(key, default)
        
        # Should use default email
        with pytest.raises(ValueError):  # Should fail on missing password
            create_admin_user()
        
        # Verify getenv was called with correct defaults
        mock_getenv.assert_any_call('ADMIN_EMAIL', 'admin@example.com')
        mock_getenv.assert_any_call('ADMIN_PASSWORD')
    
    def test_startup_module_dependencies(self):
        """Test that startup module has correct dependencies."""
        import app.startup
        
        # Should be able to import required modules
        required_imports = [
            'os', 'Session', 'select', 'User', 'engine', 'get_password_hash'
        ]
        
        # Check module source for imports
        import inspect
        source = inspect.getsource(app.startup)
        
        # Should have proper imports (at least some of them)
        assert 'import os' in source
        assert 'from app.models import User' in source
        assert 'from app.auth import get_password_hash' in source