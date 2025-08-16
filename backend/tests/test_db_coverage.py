"""
Comprehensive tests for app/db.py to achieve 100% coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from sqlalchemy.exc import OperationalError
from time import sleep


class MockContextManager:
    """Mock context manager for testing."""
    def __init__(self, mock_obj):
        self.mock_obj = mock_obj
    
    def __enter__(self):
        return self.mock_obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class TestDbFunctions:
    """Tests for database functions."""
    
    def test_get_session_success(self):
        """Test successful session creation and cleanup."""
        from app.db import get_session
        
        with patch('app.db.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            
            # Use the generator
            session_gen = get_session()
            session = next(session_gen)
            
            assert session == mock_session
            
            # Close the generator to trigger cleanup
            try:
                next(session_gen)
            except StopIteration:
                pass
    
    def test_wait_for_db_success_immediate(self):
        """Test _wait_for_db when connection succeeds immediately."""
        from app.db import _wait_for_db
        
        with patch('app.db.engine') as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_engine.connect.return_value.__exit__.return_value = None
            
            # Should complete without error
            _wait_for_db(max_retries=5, delay=0.1)
            
            # Verify connection was attempted
            mock_engine.connect.assert_called_once()
            mock_conn.execute.assert_called_once()
    
    def test_wait_for_db_success_after_retries(self):
        """Test _wait_for_db when connection succeeds after some retries."""
        from app.db import _wait_for_db
        
        with patch('app.db.engine') as mock_engine, \
             patch('app.db.sleep') as mock_sleep:
            
            mock_conn = Mock()
            
            # First two calls fail, third succeeds
            call_count = 0
            def mock_connect():
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    raise OperationalError("Connection failed", None, None)
                else:
                    # Return a successful connection context manager
                    return MockContextManager(mock_conn)
            
            mock_engine.connect.side_effect = mock_connect
            
            _wait_for_db(max_retries=5, delay=0.1)
            
            # Should have tried 3 times (2 failures + 1 success)
            assert mock_engine.connect.call_count == 3
            # Should have slept twice (after each failure)
            assert mock_sleep.call_count == 2
            mock_sleep.assert_has_calls([call(0.1), call(0.1)])
    
    def test_wait_for_db_max_retries_exceeded(self):
        """Test _wait_for_db when max retries is exceeded."""
        from app.db import _wait_for_db
        
        with patch('app.db.engine') as mock_engine, \
             patch('app.db.sleep') as mock_sleep:
            
            # All attempts fail
            test_exception = OperationalError("Connection failed", None, None)
            mock_engine.connect.side_effect = [test_exception] * 3
            
            with pytest.raises(OperationalError) as exc_info:
                _wait_for_db(max_retries=3, delay=0.1)
            
            # Should re-raise the last exception
            assert exc_info.value == test_exception
            assert mock_engine.connect.call_count == 3
            assert mock_sleep.call_count == 3
    
    def test_wait_for_db_runtime_error_fallback(self):
        """Test _wait_for_db when no exception was stored."""
        from app.db import _wait_for_db
        
        with patch('app.db.engine') as mock_engine, \
             patch('app.db.sleep') as mock_sleep:
            
            # Mock to not store any exception (edge case)
            mock_engine.connect.side_effect = Exception("Some other error")
            
            with pytest.raises(Exception):
                _wait_for_db(max_retries=1, delay=0.1)
    
    def test_init_db_success_no_existing_admin(self):
        """Test init_db when no admin user exists and admin password is provided."""
        from app.db import init_db
        
        # We'll use a more targeted test that just exercises the missing lines
        # by creating a test that covers the user creation path
        with patch('app.db._wait_for_db') as mock_wait, \
             patch('app.db.SQLModel') as mock_sqlmodel, \
             patch('app.db.Session') as mock_session_constructor:
            
            # Mock the context manager behavior
            mock_session = Mock()
            mock_session_constructor.return_value.__enter__.return_value = mock_session
            mock_session_constructor.return_value.__exit__.return_value = None
            
            # Mock the query result - no existing user
            mock_session.exec.return_value.first.return_value = None
            
            # Mock settings to have password (to trigger creation path)
            with patch('app.db.settings') as mock_settings:
                mock_settings.admin_email = "test@test.com"
                mock_settings.admin_password = "testpass"
                
                # Call init_db - this should exercise lines 54-60
                init_db()
                
                # Verify the basic flow happened
                mock_wait.assert_called_once()
                mock_sqlmodel.metadata.create_all.assert_called_once()
                # The session should have been used for queries and operations
                assert mock_session.exec.called
                assert mock_session.add.called
                assert mock_session.commit.called
    
    def test_init_db_existing_admin_user(self):
        """Test init_db when admin user already exists."""
        from app.db import init_db
        
        with patch('app.db._wait_for_db') as mock_wait, \
             patch('app.db.SQLModel') as mock_sqlmodel, \
             patch('app.db.Session') as mock_session_class, \
             patch('app.db.settings') as mock_settings, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            
            # Admin user already exists
            existing_user = Mock()
            mock_session.exec.return_value.first.return_value = existing_user
            
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = "admin123"
            
            # Call the function
            init_db()
            
            # Verify the flow
            mock_wait.assert_called_once_with(max_retries=20, delay=1.0)
            mock_sqlmodel.metadata.create_all.assert_called_once()
            
            # Should NOT create new user
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()
            mock_print.assert_not_called()
    
    def test_init_db_no_admin_password(self):
        """Test init_db when no admin password is provided."""
        from app.db import init_db
        
        with patch('app.db._wait_for_db') as mock_wait, \
             patch('app.db.SQLModel') as mock_sqlmodel, \
             patch('app.db.Session') as mock_session_class, \
             patch('app.db.settings') as mock_settings, \
             patch('builtins.print') as mock_print:
            
            # Setup mocks
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            mock_session.exec.return_value.first.return_value = None  # No existing admin
            
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = None  # No password provided
            
            # Call the function
            init_db()
            
            # Verify the flow
            mock_wait.assert_called_once_with(max_retries=20, delay=1.0)
            mock_sqlmodel.metadata.create_all.assert_called_once()
            
            # Should NOT create new user because no password
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()
            mock_print.assert_not_called()
    
    def test_init_db_empty_admin_password(self):
        """Test init_db when admin password is empty string."""
        from app.db import init_db
        
        with patch('app.db._wait_for_db') as mock_wait, \
             patch('app.db.SQLModel') as mock_sqlmodel, \
             patch('app.db.Session') as mock_session_class, \
             patch('app.db.settings') as mock_settings:
            
            # Setup mocks
            mock_session = Mock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session_class.return_value.__exit__.return_value = None
            mock_session.exec.return_value.first.return_value = None  # No existing admin
            
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = ""  # Empty password
            
            # Call the function
            init_db()
            
            # Verify the flow
            mock_wait.assert_called_once_with(max_retries=20, delay=1.0)
            mock_sqlmodel.metadata.create_all.assert_called_once()
            
            # Should NOT create new user because empty password evaluates to False
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()