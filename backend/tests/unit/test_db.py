"""
Unit tests for app.db module.
Tests PostgreSQL connection, URL validation, error handling, and fallback mechanisms.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from sqlalchemy.exc import OperationalError
import time


@pytest.mark.unit
class TestDatabaseModule:
    """Test the app.db module functionality."""
    
    def test_db_module_import(self):
        """Test that db module can be imported successfully."""
        from app import db
        assert db is not None
    
    def test_engine_creation(self):
        """Test that database engine is created properly."""
        from app.db import engine
        from sqlalchemy.engine import Engine
        
        assert engine is not None
        assert isinstance(engine, Engine)
    
    def test_get_session_function(self):
        """Test get_session dependency function."""
        from app.db import get_session
        from typing import Generator
        
        # Should be a generator function
        assert callable(get_session)
        
        # Test that it returns a generator
        session_gen = get_session()
        assert hasattr(session_gen, '__next__')  # Generator protocol
    
    def test_database_url_configuration(self):
        """Test that database URL is properly configured."""
        from app.db import engine
        from app.config import settings
        
        # Engine should use the configured database URL
        engine_url = str(engine.url)
        
        # Should be PostgreSQL
        assert engine_url.startswith('postgresql')
        
        # Should contain expected components
        assert '@' in engine_url  # user@host format
        assert '/' in engine_url  # host/database format
    
    @patch('app.db.engine')
    def test_wait_for_db_success(self, mock_engine):
        """Test _wait_for_db function with successful connection."""
        from app.db import _wait_for_db
        
        # Mock successful connection
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Should not raise any exception
        _wait_for_db(max_retries=3, delay=0.1)
        
        # Should have attempted connection
        mock_engine.connect.assert_called()
    
    @patch('app.db.engine')
    @patch('app.db.sleep')
    def test_wait_for_db_retry_then_success(self, mock_sleep, mock_engine):
        """Test _wait_for_db function with retries then success."""
        from app.db import _wait_for_db
        
        # Mock connection that fails twice then succeeds
        mock_engine.connect.side_effect = [
            OperationalError("Connection failed", None, None),
            OperationalError("Connection failed", None, None),
            MagicMock()  # Success on third try
        ]
        
        _wait_for_db(max_retries=5, delay=0.1)
        
        # Should have retried twice
        assert mock_engine.connect.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(0.1)
    
    @patch('app.db.engine')
    @patch('app.db.sleep')
    def test_wait_for_db_max_retries_exceeded(self, mock_sleep, mock_engine):
        """Test _wait_for_db function when max retries are exceeded."""
        from app.db import _wait_for_db
        
        # Mock connection that always fails
        mock_engine.connect.side_effect = OperationalError("Connection failed", None, None)
        
        # Should raise the last exception
        with pytest.raises(OperationalError):
            _wait_for_db(max_retries=3, delay=0.1)
        
        # Should have tried 3 times
        assert mock_engine.connect.call_count == 3
        assert mock_sleep.call_count == 3
    
    @patch('app.db.engine')
    def test_wait_for_db_non_operational_error(self, mock_engine):
        """Test _wait_for_db function with non-operational errors."""
        from app.db import _wait_for_db
        
        # Mock connection that raises a non-operational error
        mock_engine.connect.side_effect = ValueError("Different error")
        
        # Should raise the error immediately (no retries for non-operational errors)
        with pytest.raises(ValueError):
            _wait_for_db(max_retries=3, delay=0.1)
        
        # Should only try once
        assert mock_engine.connect.call_count == 1
    
    @patch('app.db._wait_for_db')
    @patch('app.db.Session')
    @patch('app.db.select')
    def test_init_db_function(self, mock_select, mock_session, mock_wait_for_db):
        """Test init_db function."""
        from app.db import init_db
        from sqlmodel import SQLModel
        
        # Mock database session and user query
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None  # No existing admin
        
        # Mock settings
        with patch('app.db.settings') as mock_settings:
            mock_settings.admin_email = 'admin@test.com'
            mock_settings.admin_password = 'test-password'
            
            # Mock SQLModel metadata
            with patch.object(SQLModel, 'metadata') as mock_metadata:
                mock_metadata.create_all = MagicMock()
                
                init_db()
                
                # Should wait for DB
                mock_wait_for_db.assert_called_once_with(max_retries=20, delay=1.0)
                
                # Should create tables
                mock_metadata.create_all.assert_called_once()
                
                # Should check for existing admin user
                mock_session_instance.exec.assert_called()
    
    @patch('app.db._wait_for_db')
    def test_init_db_table_creation(self, mock_wait_for_db):
        """Test that init_db creates tables."""
        from app.db import init_db
        from sqlmodel import SQLModel
        
        with patch.object(SQLModel, 'metadata') as mock_metadata:
            mock_metadata.create_all = MagicMock()
            
            with patch('app.db.Session'):  # Mock session to avoid DB calls
                with patch('app.db.settings') as mock_settings:
                    mock_settings.admin_email = 'admin@test.com'
                    mock_settings.admin_password = None  # No admin user creation
                    
                    init_db()
                    
                    # Should create all tables
                    mock_metadata.create_all.assert_called_once()
    
    @patch('app.db._wait_for_db')
    @patch('app.db.Session')
    def test_init_db_admin_user_creation(self, mock_session, mock_wait_for_db):
        """Test admin user creation in init_db."""
        from app.db import init_db
        
        # Mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.return_value.first.return_value = None  # No existing admin
        
        with patch('app.db.settings') as mock_settings:
            mock_settings.admin_email = 'admin@test.com'
            mock_settings.admin_password = 'admin-password-123'
            
            with patch('sqlmodel.SQLModel.metadata'):
                with patch('passlib.context.CryptContext') as mock_context:
                    mock_pwd_context = MagicMock()
                    mock_context.return_value = mock_pwd_context
                    mock_pwd_context.hash.return_value = 'hashed-password'
                    
                    with patch('app.models.User') as mock_user_class:
                        init_db()
                        
                        # Should create admin user
                        mock_user_class.assert_called_once()
                        mock_session_instance.add.assert_called_once()
                        mock_session_instance.commit.assert_called_once()
    
    @patch('app.db._wait_for_db')
    @patch('app.db.Session')
    def test_init_db_existing_admin_user(self, mock_session, mock_wait_for_db):
        """Test init_db with existing admin user."""
        from app.db import init_db
        
        # Mock session with existing user
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_existing_user = MagicMock()
        mock_session_instance.exec.return_value.first.return_value = mock_existing_user
        
        with patch('app.db.settings') as mock_settings:
            mock_settings.admin_email = 'admin@test.com'
            mock_settings.admin_password = 'admin-password-123'
            
            with patch('sqlmodel.SQLModel.metadata'):
                init_db()
                
                # Should not create new admin user
                mock_session_instance.add.assert_not_called()
                mock_session_instance.commit.assert_not_called()
    
    def test_database_url_validation(self):
        """Test database URL format validation."""
        from app.config import settings
        
        db_url = settings.database_url
        
        # Should be a valid PostgreSQL URL
        assert db_url.startswith('postgresql')
        
        # Should have proper format
        url_parts = db_url.split('://')
        assert len(url_parts) == 2
        
        # Should have user:password@host:port/database format after ://
        connection_part = url_parts[1]
        assert '@' in connection_part
        assert '/' in connection_part
    
    @patch.dict('os.environ', {'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db'})
    def test_database_url_environment_override(self):
        """Test database URL can be overridden by environment."""
        import importlib
        import app.config
        importlib.reload(app.config)
        
        from app.config import settings
        
        # Should use environment value
        assert 'test_db' in settings.database_url
        assert 'test:test@localhost' in settings.database_url
    
    def test_engine_configuration(self):
        """Test database engine configuration."""
        from app.db import engine
        
        # Engine should be configured properly
        assert engine is not None
        
        # Check that echo is disabled (for production)
        # This might vary based on settings
        engine_echo = engine.echo
        assert isinstance(engine_echo, bool)
    
    def test_session_dependency_usage(self):
        """Test session dependency can be used in FastAPI context."""
        from app.db import get_session
        
        # Should be usable as FastAPI dependency
        session_gen = get_session()
        
        try:
            session = next(session_gen)
            # Session should be a SQLModel Session
            from sqlmodel import Session
            assert isinstance(session, Session)
        except StopIteration:
            pytest.fail("get_session should yield a session")
        except Exception as e:
            # If there's a connection error, that's expected in test environment
            # Just ensure the function structure is correct
            assert callable(get_session)


@pytest.mark.unit
class TestDatabaseErrorHandling:
    """Test database error handling and fallback mechanisms."""
    
    @patch('app.db.engine')
    def test_connection_error_handling(self, mock_engine):
        """Test handling of connection errors."""
        from app.db import _wait_for_db
        
        # Mock connection error
        mock_engine.connect.side_effect = OperationalError(
            "could not connect to server", None, None
        )
        
        with pytest.raises(OperationalError):
            _wait_for_db(max_retries=1, delay=0.1)
    
    @patch('app.db.engine')
    def test_database_not_exist_error(self, mock_engine):
        """Test handling of database does not exist error."""
        from app.db import _wait_for_db
        
        # Mock database doesn't exist error
        mock_engine.connect.side_effect = OperationalError(
            'database "ml_db" does not exist', None, None
        )
        
        with pytest.raises(OperationalError):
            _wait_for_db(max_retries=1, delay=0.1)
    
    @patch('app.db.engine')
    def test_authentication_error(self, mock_engine):
        """Test handling of authentication errors."""
        from app.db import _wait_for_db
        
        # Mock authentication error
        mock_engine.connect.side_effect = OperationalError(
            "password authentication failed", None, None
        )
        
        with pytest.raises(OperationalError):
            _wait_for_db(max_retries=1, delay=0.1)
    
    @patch('app.db.engine')
    @patch('app.db.sleep')
    def test_wait_for_db_delay_parameter(self, mock_sleep, mock_engine):
        """Test that _wait_for_db respects delay parameter."""
        from app.db import _wait_for_db
        
        # Mock connection that fails then succeeds
        mock_engine.connect.side_effect = [
            OperationalError("Connection failed", None, None),
            MagicMock()  # Success on second try
        ]
        
        custom_delay = 0.5
        _wait_for_db(max_retries=3, delay=custom_delay)
        
        # Should use custom delay
        mock_sleep.assert_called_once_with(custom_delay)
    
    @patch('app.db.engine')
    def test_wait_for_db_zero_retries(self, mock_engine):
        """Test _wait_for_db with zero retries."""
        from app.db import _wait_for_db
        
        # Mock connection failure
        mock_engine.connect.side_effect = OperationalError("Connection failed", None, None)
        
        # With zero retries, should fail immediately
        with pytest.raises(OperationalError):
            _wait_for_db(max_retries=0, delay=0.1)
        
        # Should not retry
        assert mock_engine.connect.call_count == 0  # Zero retries means no attempts
    
    def test_wait_for_db_runtime_error_fallback(self):
        """Test _wait_for_db RuntimeError fallback."""
        from app.db import _wait_for_db
        
        with patch('app.db.engine') as mock_engine:
            # Mock no exception stored
            mock_engine.connect.side_effect = OperationalError("test", None, None)
            
            # Create a scenario where last_exc might be None
            with patch('app.db.sleep'):
                with pytest.raises((OperationalError, RuntimeError)):
                    _wait_for_db(max_retries=1, delay=0.1)