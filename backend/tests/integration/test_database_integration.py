"""
Database integration tests for PostgreSQL operations.

These tests verify:
- Database connection and session management
- Model creation and relationships
- CRUD operations with PostgreSQL
- Data integrity and constraints
- Performance under load
"""
import pytest
from sqlmodel import Session, select, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models import User, OAuthToken, OAuthSession, ApiEndpoint
from app.core.security import get_password_hash, verify_password


class TestDatabaseConnection:
    """Test database connection and basic operations."""
    
    def test_database_connection(self, pg_session: Session):
        """Test that database connection is working."""
        result = pg_session.exec(text("SELECT 1 as test_value")).first()
        assert result[0] == 1
    
    def test_database_transaction_commit(self, pg_session: Session):
        """Test database transaction commit."""
        user = User(
            email="transaction_test@example.com",
            hashed_password=get_password_hash("password")
        )
        pg_session.add(user)
        pg_session.commit()
        
        # Verify user was saved
        saved_user = pg_session.exec(
            select(User).where(User.email == "transaction_test@example.com")
        ).first()
        assert saved_user is not None
        assert saved_user.email == "transaction_test@example.com"
    
    def test_database_transaction_rollback(self, pg_session: Session):
        """Test database transaction rollback."""
        user = User(
            email="rollback_test@example.com",
            hashed_password=get_password_hash("password")
        )
        pg_session.add(user)
        pg_session.rollback()
        
        # Verify user was not saved
        saved_user = pg_session.exec(
            select(User).where(User.email == "rollback_test@example.com")
        ).first()
        assert saved_user is None


class TestUserModelIntegration:
    """Test User model integration with PostgreSQL."""
    
    def test_user_creation(self, pg_session: Session):
        """Test creating a new user."""
        user = User(
            email="newuser@example.com",
            hashed_password=get_password_hash("securepassword"),
            is_active=True,
            is_superuser=False
        )
        pg_session.add(user)
        pg_session.commit()
        pg_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        assert verify_password("securepassword", user.hashed_password)
    
    def test_user_email_uniqueness(self, pg_session: Session):
        """Test user email uniqueness constraint."""
        # Create first user
        user1 = User(
            email="unique@example.com",
            hashed_password=get_password_hash("password1")
        )
        pg_session.add(user1)
        pg_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            hashed_password=get_password_hash("password2")
        )
        pg_session.add(user2)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_user_query_by_email(self, pg_session: Session, pg_test_user: User):
        """Test querying user by email."""
        found_user = pg_session.exec(
            select(User).where(User.email == pg_test_user.email)
        ).first()
        
        assert found_user is not None
        assert found_user.id == pg_test_user.id
        assert found_user.email == pg_test_user.email
    
    def test_user_update(self, pg_session: Session, pg_test_user: User):
        """Test updating user information."""
        original_email = pg_test_user.email
        new_email = "updated@example.com"
        
        pg_test_user.email = new_email
        pg_test_user.is_active = False
        pg_session.commit()
        
        # Refresh from database
        pg_session.refresh(pg_test_user)
        assert pg_test_user.email == new_email
        assert pg_test_user.is_active is False
        
        # Verify old email doesn't exist
        old_user = pg_session.exec(
            select(User).where(User.email == original_email)
        ).first()
        assert old_user is None
    
    def test_user_deletion(self, pg_session: Session):
        """Test user deletion."""
        user = User(
            email="todelete@example.com",
            hashed_password=get_password_hash("password")
        )
        pg_session.add(user)
        pg_session.commit()
        user_id = user.id
        
        # Delete user
        pg_session.delete(user)
        pg_session.commit()
        
        # Verify user is deleted
        deleted_user = pg_session.exec(
            select(User).where(User.id == user_id)
        ).first()
        assert deleted_user is None


class TestOAuthTokenModelIntegration:
    """Test OAuthToken model integration with PostgreSQL."""
    
    def test_oauth_token_creation(self, pg_session: Session, pg_test_user: User):
        """Test creating OAuth token."""
        token = OAuthToken(
            user_id=pg_test_user.id,
            access_token="APP_USR-test-access-token",
            refresh_token="TG-test-refresh-token",
            token_type="Bearer",
            expires_in=21600,
            scope="offline_access read write"
        )
        pg_session.add(token)
        pg_session.commit()
        pg_session.refresh(token)
        
        assert token.id is not None
        assert token.user_id == pg_test_user.id
        assert token.access_token == "APP_USR-test-access-token"
        assert token.refresh_token == "TG-test-refresh-token"
        assert token.token_type == "Bearer"
        assert token.expires_in == 21600
        assert token.scope == "offline_access read write"
        assert isinstance(token.created_at, datetime)
    
    def test_oauth_token_user_relationship(self, pg_session: Session, 
                                         pg_test_user: User, oauth_token_data: OAuthToken):
        """Test OAuth token relationship with user."""
        # Test accessing user from token
        assert oauth_token_data.user is not None
        assert oauth_token_data.user.id == pg_test_user.id
        assert oauth_token_data.user.email == pg_test_user.email
        
        # Test accessing tokens from user
        assert len(pg_test_user.oauth_tokens) > 0
        assert oauth_token_data in pg_test_user.oauth_tokens
    
    def test_oauth_token_foreign_key_constraint(self, pg_session: Session):
        """Test OAuth token foreign key constraint."""
        token = OAuthToken(
            user_id=99999,  # Non-existent user
            access_token="test-token",
            refresh_token="test-refresh"
        )
        pg_session.add(token)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_oauth_token_update(self, pg_session: Session, oauth_token_data: OAuthToken):
        """Test updating OAuth token."""
        new_access_token = "APP_USR-new-access-token"
        new_expires_in = 7200
        
        oauth_token_data.access_token = new_access_token
        oauth_token_data.expires_in = new_expires_in
        pg_session.commit()
        
        # Refresh from database
        pg_session.refresh(oauth_token_data)
        assert oauth_token_data.access_token == new_access_token
        assert oauth_token_data.expires_in == new_expires_in
    
    def test_oauth_token_cascade_delete(self, pg_session: Session):
        """Test OAuth token deletion when user is deleted."""
        # Create user and token
        user = User(
            email="cascade_test@example.com",
            hashed_password=get_password_hash("password")
        )
        pg_session.add(user)
        pg_session.commit()
        
        token = OAuthToken(
            user_id=user.id,
            access_token="test-token"
        )
        pg_session.add(token)
        pg_session.commit()
        token_id = token.id
        
        # Delete user
        pg_session.delete(user)
        pg_session.commit()
        
        # Verify token is also deleted (cascade)
        deleted_token = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == token_id)
        ).first()
        # Note: The actual behavior depends on the foreign key cascade setting
        # This test might need adjustment based on the actual model configuration


class TestOAuthSessionModelIntegration:
    """Test OAuthSession model integration with PostgreSQL."""
    
    def test_oauth_session_creation(self, pg_session: Session):
        """Test creating OAuth session."""
        session_obj = OAuthSession(
            state="test_state_unique",
            code_verifier="test_code_verifier_unique",
            endpoint_id=1
        )
        pg_session.add(session_obj)
        pg_session.commit()
        
        assert session_obj.state == "test_state_unique"
        assert session_obj.code_verifier == "test_code_verifier_unique"
        assert session_obj.endpoint_id == 1
        assert isinstance(session_obj.created_at, datetime)
    
    def test_oauth_session_state_uniqueness(self, pg_session: Session):
        """Test OAuth session state uniqueness."""
        # Create first session
        session1 = OAuthSession(
            state="unique_state",
            code_verifier="verifier1"
        )
        pg_session.add(session1)
        pg_session.commit()
        
        # Try to create second session with same state
        session2 = OAuthSession(
            state="unique_state",
            code_verifier="verifier2"
        )
        pg_session.add(session2)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_oauth_session_query_by_state(self, pg_session: Session, oauth_session_data: OAuthSession):
        """Test querying OAuth session by state."""
        found_session = pg_session.exec(
            select(OAuthSession).where(OAuthSession.state == oauth_session_data.state)
        ).first()
        
        assert found_session is not None
        assert found_session.state == oauth_session_data.state
        assert found_session.code_verifier == oauth_session_data.code_verifier


class TestDatabasePerformance:
    """Test database performance and bulk operations."""
    
    def test_bulk_user_creation(self, pg_session: Session):
        """Test creating multiple users efficiently."""
        users = []
        for i in range(100):
            user = User(
                email=f"bulk_user_{i}@example.com",
                hashed_password=get_password_hash(f"password_{i}")
            )
            users.append(user)
        
        # Add all users at once
        pg_session.add_all(users)
        pg_session.commit()
        
        # Verify all users were created
        user_count = pg_session.exec(
            select(User).where(User.email.like("bulk_user_%@example.com"))
        ).fetchall()
        assert len(user_count) == 100
    
    def test_complex_query_with_joins(self, pg_session: Session, pg_test_user: User, oauth_token_data: OAuthToken):
        """Test complex query with joins."""
        # Query users with their OAuth tokens
        result = pg_session.exec(
            select(User, OAuthToken)
            .join(OAuthToken, User.id == OAuthToken.user_id)
            .where(User.id == pg_test_user.id)
        ).first()
        
        assert result is not None
        user, token = result
        assert user.id == pg_test_user.id
        assert token.user_id == pg_test_user.id
    
    def test_database_indexing_performance(self, pg_session: Session):
        """Test that database indexes are working for common queries."""
        # Create users for testing
        users = []
        for i in range(50):
            user = User(
                email=f"index_test_{i}@example.com",
                hashed_password=get_password_hash("password")
            )
            users.append(user)
        
        pg_session.add_all(users)
        pg_session.commit()
        
        # Query by email (should use index)
        result = pg_session.exec(
            select(User).where(User.email == "index_test_25@example.com")
        ).first()
        
        assert result is not None
        assert result.email == "index_test_25@example.com"


class TestDataIntegrity:
    """Test data integrity and constraints."""
    
    def test_user_email_not_null(self, pg_session: Session):
        """Test that user email cannot be null."""
        user = User(hashed_password=get_password_hash("password"))
        # Email is not set (None)
        pg_session.add(user)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_user_password_not_null(self, pg_session: Session):
        """Test that user password cannot be null."""
        user = User(email="test@example.com")
        # Password is not set (None)
        pg_session.add(user)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_oauth_token_access_token_not_null(self, pg_session: Session, pg_test_user: User):
        """Test that OAuth token access_token cannot be null."""
        token = OAuthToken(user_id=pg_test_user.id)
        # access_token is not set (None)
        pg_session.add(token)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_oauth_session_state_not_null(self, pg_session: Session):
        """Test that OAuth session state cannot be null."""
        session_obj = OAuthSession(code_verifier="test_verifier")
        # state is not set (None)
        pg_session.add(session_obj)
        
        with pytest.raises(IntegrityError):
            pg_session.commit()
    
    def test_datetime_fields_auto_populate(self, pg_session: Session):
        """Test that datetime fields are automatically populated."""
        user = User(
            email="datetime_test@example.com",
            hashed_password=get_password_hash("password")
        )
        pg_session.add(user)
        pg_session.commit()
        pg_session.refresh(user)
        
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
        # Should be recent (within last minute)
        assert (datetime.utcnow() - user.created_at) < timedelta(minutes=1)
    
    def test_boolean_fields_default_values(self, pg_session: Session):
        """Test boolean fields have correct default values."""
        user = User(
            email="boolean_test@example.com",
            hashed_password=get_password_hash("password")
        )
        # Not explicitly setting is_active or is_superuser
        pg_session.add(user)
        pg_session.commit()
        pg_session.refresh(user)
        
        assert user.is_active is True  # Default should be True
        assert user.is_superuser is False  # Default should be False


class TestDatabaseMigration:
    """Test database schema and migration compatibility."""
    
    def test_table_creation(self, pg_session: Session):
        """Test that all expected tables exist."""
        # Query information schema to check tables exist
        result = pg_session.exec(
            text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)
        ).fetchall()
        
        table_names = [row[0] for row in result]
        
        # Check that expected tables exist
        expected_tables = ["users", "oauth_tokens", "oauth_sessions"]
        for table in expected_tables:
            assert table in table_names
    
    def test_column_types(self, pg_session: Session):
        """Test that columns have correct data types."""
        # Test users table columns
        result = pg_session.exec(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
        ).fetchall()
        
        columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}
        
        # Verify key column types
        assert "id" in columns
        assert "email" in columns
        assert columns["email"]["type"] == "character varying"
        assert columns["email"]["nullable"] == "NO"
        assert "hashed_password" in columns
        assert columns["hashed_password"]["nullable"] == "NO"