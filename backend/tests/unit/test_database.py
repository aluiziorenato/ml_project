"""
Unit tests for database and startup modules.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from sqlmodel import Session, SQLModel

from app.db import get_session, init_db
from app.startup import create_admin_user
from app.models import User


@pytest.mark.unit
class TestDatabaseModule:
    """Test database module functionality."""
    
    @patch('app.db.create_engine')
    @patch('app.db.SQLModel.metadata.create_all')
    def test_init_db(self, mock_create_all, mock_create_engine):
        """Test database initialization."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        init_db()
        
        mock_create_engine.assert_called_once()
        mock_create_all.assert_called_once_with(mock_engine)
    
    @patch('app.db.create_engine')
    def test_init_db_with_error(self, mock_create_engine):
        """Test database initialization with error."""
        mock_create_engine.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception, match="Database connection error"):
            init_db()
    
    def test_get_session(self):
        """Test get_session generator."""
        sessions = []
        session_gen = get_session()
        
        # Get a few sessions
        for _ in range(3):
            try:
                session = next(session_gen)
                sessions.append(session)
                assert isinstance(session, Session)
            except StopIteration:
                break
        
        # Should have gotten at least one session
        assert len(sessions) > 0
    
    @patch('app.db.Session')
    def test_get_session_with_error(self, mock_session_class):
        """Test get_session with session creation error."""
        mock_session_class.side_effect = Exception("Session creation error")
        
        session_gen = get_session()
        
        with pytest.raises(Exception, match="Session creation error"):
            next(session_gen)
    
    @patch('app.db.Session')
    def test_get_session_cleanup(self, mock_session_class):
        """Test get_session properly closes sessions."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        session_gen = get_session()
        
        # Get session
        session = next(session_gen)
        assert session == mock_session
        
        # Trigger cleanup
        try:
            next(session_gen)
        except StopIteration:
            pass
        
        # Session should be closed
        mock_session.close.assert_called_once()


@pytest.mark.unit
class TestStartupModule:
    """Test startup module functionality."""
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    def test_create_admin_user_new(self, mock_select, mock_get_session):
        """Test creating admin user when none exists."""
        # Mock session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock no existing admin user
        mock_session.exec.return_value.first.return_value = None
        
        # Mock settings
        with patch('app.startup.settings') as mock_settings:
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = "admin_password"
            
            create_admin_user()
            
            # Should create new admin user
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            
            # Verify user data
            added_user = mock_session.add.call_args[0][0]
            assert added_user.email == "admin@test.com"
            assert added_user.is_superuser is True
            assert added_user.is_active is True
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    def test_create_admin_user_exists(self, mock_select, mock_get_session):
        """Test when admin user already exists."""
        # Mock session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock existing admin user
        existing_admin = Mock()
        mock_session.exec.return_value.first.return_value = existing_admin
        
        create_admin_user()
        
        # Should not create new user
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
    
    @patch('app.startup.get_session')
    def test_create_admin_user_no_password(self, mock_get_session):
        """Test admin user creation without password set."""
        # Mock session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock no existing admin user
        mock_session.exec.return_value.first.return_value = None
        
        # Mock settings without password
        with patch('app.startup.settings') as mock_settings:
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = None
            
            create_admin_user()
            
            # Should not create user without password
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    def test_create_admin_user_database_error(self, mock_select, mock_get_session):
        """Test admin user creation with database error."""
        # Mock session with error
        mock_get_session.side_effect = Exception("Database error")
        
        # Should handle error gracefully
        create_admin_user()  # Should not raise exception
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    @patch('app.startup.get_password_hash')
    def test_create_admin_user_password_hashing(self, mock_hash, mock_select, mock_get_session):
        """Test that admin password is properly hashed."""
        # Mock session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock no existing admin user
        mock_session.exec.return_value.first.return_value = None
        
        # Mock password hashing
        mock_hash.return_value = "hashed_password"
        
        # Mock settings
        with patch('app.startup.settings') as mock_settings:
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = "plain_password"
            
            create_admin_user()
            
            # Should hash the password
            mock_hash.assert_called_once_with("plain_password")
            
            # Verify hashed password is used
            added_user = mock_session.add.call_args[0][0]
            assert added_user.hashed_password == "hashed_password"
    
    @patch('app.startup.get_session')
    @patch('app.startup.select')
    def test_create_admin_user_commit_error(self, mock_select, mock_get_session):
        """Test admin user creation with commit error."""
        # Mock session
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock no existing admin user
        mock_session.exec.return_value.first.return_value = None
        
        # Mock commit error
        mock_session.commit.side_effect = Exception("Commit error")
        
        # Mock settings
        with patch('app.startup.settings') as mock_settings:
            mock_settings.admin_email = "admin@test.com"
            mock_settings.admin_password = "admin_password"
            
            # Should handle commit error gracefully
            create_admin_user()  # Should not raise exception


@pytest.mark.unit
class TestModelsIntegration:
    """Test models integration with database operations."""
    
    def test_user_model_database_operations(self, session: Session):
        """Test User model database operations."""
        from app.core.security import get_password_hash
        
        # Create user
        user = User(
            email="db_test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Verify user was saved
        assert user.id is not None
        assert user.email == "db_test@example.com"
        assert user.is_active is True
        
        # Test retrieval
        from sqlmodel import select
        retrieved_user = session.exec(select(User).where(User.email == "db_test@example.com")).first()
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
    
    def test_api_endpoint_model_database_operations(self, session: Session):
        """Test ApiEndpoint model database operations."""
        from app.models import ApiEndpoint
        
        # Create endpoint
        endpoint = ApiEndpoint(
            name="DB Test API",
            url="https://api.dbtest.com",
            auth_type="oauth",
            oauth_scope="read write"
        )
        
        session.add(endpoint)
        session.commit()
        session.refresh(endpoint)
        
        # Verify endpoint was saved
        assert endpoint.id is not None
        assert endpoint.name == "DB Test API"
        assert endpoint.auth_type == "oauth"
        
        # Test retrieval
        from sqlmodel import select
        retrieved_endpoint = session.exec(select(ApiEndpoint).where(ApiEndpoint.name == "DB Test API")).first()
        
        assert retrieved_endpoint is not None
        assert retrieved_endpoint.id == endpoint.id
        assert retrieved_endpoint.url == endpoint.url
    
    def test_oauth_session_model_database_operations(self, session: Session):
        """Test OAuthSession model database operations."""
        from app.models import OAuthSession
        
        # Create OAuth session
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="db_test_state",
            code_verifier="db_test_verifier"
        )
        
        session.add(oauth_session)
        session.commit()
        session.refresh(oauth_session)
        
        # Verify session was saved
        assert oauth_session.id is not None
        assert oauth_session.state == "db_test_state"
        assert oauth_session.code_verifier == "db_test_verifier"
        
        # Test retrieval
        from sqlmodel import select
        retrieved_session = session.exec(select(OAuthSession).where(OAuthSession.state == "db_test_state")).first()
        
        assert retrieved_session is not None
        assert retrieved_session.id == oauth_session.id
    
    def test_api_test_model_database_operations(self, session: Session):
        """Test ApiTest model database operations."""
        from app.models import ApiTest
        
        # Create API test
        api_test = ApiTest(
            name="DB Test Case",
            request_method="GET",
            request_path="/db/test",
            status_code=200,
            response_body='{"test": "success"}'
        )
        
        session.add(api_test)
        session.commit()
        session.refresh(api_test)
        
        # Verify test was saved
        assert api_test.id is not None
        assert api_test.name == "DB Test Case"
        assert api_test.request_method == "GET"
        assert api_test.status_code == 200
        
        # Test retrieval
        from sqlmodel import select
        retrieved_test = session.exec(select(ApiTest).where(ApiTest.name == "DB Test Case")).first()
        
        assert retrieved_test is not None
        assert retrieved_test.id == api_test.id
        assert retrieved_test.response_body == '{"test": "success"}'


@pytest.mark.unit
class TestDatabaseConnectionHandling:
    """Test database connection handling and error scenarios."""
    
    @patch('app.db.settings')
    @patch('app.db.create_engine')
    def test_init_db_with_different_database_urls(self, mock_create_engine, mock_settings):
        """Test init_db with different database URL configurations."""
        # Test SQLite URL
        mock_settings.database_url = "sqlite:///test.db"
        init_db()
        mock_create_engine.assert_called()
        
        # Test PostgreSQL URL
        mock_settings.database_url = "postgresql://user:pass@localhost/db"
        init_db()
        
        # Should have been called twice
        assert mock_create_engine.call_count == 2
    
    @patch('app.db.create_engine')
    def test_init_db_engine_configuration(self, mock_create_engine):
        """Test that init_db configures engine properly."""
        init_db()
        
        # Verify engine was created with correct parameters
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        
        # Should have database URL as first argument
        assert len(call_args[0]) > 0
    
    @patch('app.db.Session')
    def test_get_session_exception_handling(self, mock_session_class):
        """Test get_session handles exceptions during session lifecycle."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock session operation that raises exception
        mock_session.execute.side_effect = Exception("Session operation error")
        
        session_gen = get_session()
        session = next(session_gen)
        
        # Even if session operations fail, cleanup should still happen
        try:
            session.execute("SELECT 1")
        except Exception:
            pass
        
        # Trigger cleanup
        try:
            next(session_gen)
        except StopIteration:
            pass
        
        # Session should still be closed despite the error
        mock_session.close.assert_called_once()


@pytest.mark.unit  
class TestConfigurationIntegration:
    """Test integration between configuration and database/startup modules."""
    
    @patch('app.startup.settings')
    @patch('app.startup.get_session')
    def test_startup_uses_configuration(self, mock_get_session, mock_settings):
        """Test that startup module uses configuration correctly."""
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        # Set specific configuration values
        mock_settings.admin_email = "config@test.com"
        mock_settings.admin_password = "config_password"
        
        create_admin_user()
        
        # Verify configuration was used
        added_user = mock_session.add.call_args[0][0]
        assert added_user.email == "config@test.com"
    
    @patch('app.db.settings')
    def test_database_uses_configuration(self, mock_settings):
        """Test that database module uses configuration correctly."""
        mock_settings.database_url = "sqlite:///config_test.db"
        
        with patch('app.db.create_engine') as mock_create_engine:
            init_db()
            
            # Verify database URL from configuration was used
            mock_create_engine.assert_called_once()
            call_args = mock_create_engine.call_args[0]
            assert "config_test.db" in call_args[0]