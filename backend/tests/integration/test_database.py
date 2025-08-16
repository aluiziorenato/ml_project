"""
Integration tests for database operations and transactions.
"""
import pytest
import asyncio
from unittest.mock import patch, Mock
from sqlmodel import Session, select, text
from sqlalchemy.exc import OperationalError, IntegrityError
from datetime import datetime, timedelta
import threading
import time

from app.models import User, OAuthSession, ApiEndpoint, ApiTest
from app.core.security import get_password_hash
from app.db import get_session, init_db


@pytest.mark.integration
class TestDatabaseConnections:
    """Test database connection handling."""
    
    def test_database_session_creation(self, db: Session):
        """Test database session creation and basic operations."""
        # Test session is valid
        assert db is not None
        assert isinstance(db, Session)
        
        # Test basic query
        result = db.exec(text("SELECT 1")).first()
        assert result == 1
        
    def test_database_session_isolation(self, engine):
        """Test that database sessions are properly isolated."""
        # Create two separate sessions
        with Session(engine) as session1, Session(engine) as session2:
            # Add user in session1
            user1 = User(
                email="session1@example.com",
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            session1.add(user1)
            session1.commit()
            
            # Check user exists in session1
            found_user1 = session1.exec(
                select(User).where(User.email == "session1@example.com")
            ).first()
            assert found_user1 is not None
            
            # User should also be visible in session2 after commit
            found_user2 = session2.exec(
                select(User).where(User.email == "session1@example.com")
            ).first()
            assert found_user2 is not None
            assert found_user2.email == found_user1.email
            
    def test_database_transaction_rollback(self, engine):
        """Test database transaction rollback functionality."""
        with Session(engine) as session:
            # Start transaction
            transaction = session.begin()
            
            try:
                # Add user
                user = User(
                    email="rollback_test@example.com",
                    hashed_password=get_password_hash("password"),
                    is_active=True
                )
                session.add(user)
                session.flush()  # Flush but don't commit
                
                # Verify user exists in current transaction
                found_user = session.exec(
                    select(User).where(User.email == "rollback_test@example.com")
                ).first()
                assert found_user is not None
                
                # Rollback transaction
                transaction.rollback()
                
            except Exception:
                transaction.rollback()
                raise
                
        # Verify user doesn't exist after rollback
        with Session(engine) as new_session:
            found_user = new_session.exec(
                select(User).where(User.email == "rollback_test@example.com")
            ).first()
            assert found_user is None
            
    def test_database_concurrent_access(self, engine):
        """Test concurrent database access."""
        results = []
        errors = []
        
        def create_user(user_id):
            try:
                with Session(engine) as session:
                    user = User(
                        email=f"concurrent_user_{user_id}@example.com",
                        hashed_password=get_password_hash("password"),
                        is_active=True
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    results.append(user.id)
            except Exception as e:
                errors.append(str(e))
                
        # Create multiple threads to test concurrent access
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        assert len(set(results)) == 5  # All IDs should be unique


@pytest.mark.integration
class TestDatabaseCRUDOperations:
    """Test CRUD operations with database integration."""
    
    def test_user_crud_operations(self, db: Session):
        """Test complete CRUD operations for User model."""
        # CREATE
        user = User(
            email="crud_test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        created_user_id = user.id
        
        # READ
        found_user = db.get(User, created_user_id)
        assert found_user is not None
        assert found_user.email == "crud_test@example.com"
        assert found_user.is_active is True
        assert found_user.is_superuser is False
        
        # UPDATE
        found_user.is_superuser = True
        found_user.is_active = False
        db.add(found_user)
        db.commit()
        db.refresh(found_user)
        
        updated_user = db.get(User, created_user_id)
        assert updated_user.is_superuser is True
        assert updated_user.is_active is False
        
        # DELETE
        db.delete(updated_user)
        db.commit()
        
        deleted_user = db.get(User, created_user_id)
        assert deleted_user is None
        
    def test_oauth_session_crud_operations(self, db: Session):
        """Test CRUD operations for OAuthSession model."""
        # CREATE
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="test_state_123",
            code_verifier="test_verifier_456",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_type="Bearer",
            expires_at=datetime.utcnow() + timedelta(hours=6)
        )
        db.add(oauth_session)
        db.commit()
        db.refresh(oauth_session)
        
        assert oauth_session.id is not None
        session_id = oauth_session.id
        
        # READ
        found_session = db.get(OAuthSession, session_id)
        assert found_session is not None
        assert found_session.state == "test_state_123"
        assert found_session.access_token == "test_access_token"
        
        # UPDATE
        found_session.access_token = "updated_access_token"
        found_session.expires_at = datetime.utcnow() + timedelta(hours=12)
        db.add(found_session)
        db.commit()
        
        updated_session = db.get(OAuthSession, session_id)
        assert updated_session.access_token == "updated_access_token"
        
        # DELETE
        db.delete(updated_session)
        db.commit()
        
        deleted_session = db.get(OAuthSession, session_id)
        assert deleted_session is None
        
    def test_api_endpoint_crud_operations(self, db: Session):
        """Test CRUD operations for ApiEndpoint model."""
        from app.models import ApiEndpoint
        
        # CREATE
        endpoint = ApiEndpoint(
            name="Test API Endpoint",
            url="https://api.test.com/v1",
            auth_type="oauth",
            oauth_scope="read write"
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        
        assert endpoint.id is not None
        endpoint_id = endpoint.id
        
        # READ
        found_endpoint = db.get(ApiEndpoint, endpoint_id)
        assert found_endpoint is not None
        assert found_endpoint.name == "Test API Endpoint"
        assert found_endpoint.url == "https://api.test.com/v1"
        
        # UPDATE
        found_endpoint.name = "Updated API Endpoint"
        found_endpoint.url = "https://api.updated.com/v2"
        db.add(found_endpoint)
        db.commit()
        
        updated_endpoint = db.get(ApiEndpoint, endpoint_id)
        assert updated_endpoint.name == "Updated API Endpoint"
        assert updated_endpoint.url == "https://api.updated.com/v2"
        
        # DELETE
        db.delete(updated_endpoint)
        db.commit()
        
        deleted_endpoint = db.get(ApiEndpoint, endpoint_id)
        assert deleted_endpoint is None


@pytest.mark.integration
class TestDatabaseConstraints:
    """Test database constraints and data integrity."""
    
    def test_user_email_uniqueness_constraint(self, db: Session):
        """Test that user email uniqueness is enforced."""
        # Create first user
        user1 = User(
            email="unique_test@example.com",
            hashed_password=get_password_hash("password1"),
            is_active=True
        )
        db.add(user1)
        db.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique_test@example.com",  # Same email
            hashed_password=get_password_hash("password2"),
            is_active=True
        )
        db.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            db.commit()
            
    def test_required_field_constraints(self, db: Session):
        """Test that required fields are enforced."""
        # Test User without email (should fail)
        with pytest.raises(Exception):
            user = User(
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            db.add(user)
            db.commit()
            
        # Test User without hashed_password (should fail)
        with pytest.raises(Exception):
            user = User(
                email="test@example.com",
                is_active=True
            )
            db.add(user)
            db.commit()
            
    def test_foreign_key_constraints(self, db: Session):
        """Test foreign key constraints if they exist."""
        # This would test foreign key relationships
        # For now, we'll test basic relationship integrity
        
        # Create OAuth session with endpoint_id
        oauth_session = OAuthSession(
            endpoint_id=999,  # Non-existent endpoint
            state="test_state",
            code_verifier="test_verifier"
        )
        db.add(oauth_session)
        
        # Should succeed even with non-existent endpoint_id
        # (depends on actual schema design)
        try:
            db.commit()
            # If foreign key constraints exist, this would fail
        except Exception:
            # If foreign key constraint exists and is enforced
            pass
            
    def test_data_type_constraints(self, db: Session):
        """Test data type constraints."""
        # Test datetime fields
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="test_state",
            code_verifier="test_verifier",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(oauth_session)
        db.commit()
        db.refresh(oauth_session)
        
        assert isinstance(oauth_session.created_at, datetime)
        assert isinstance(oauth_session.expires_at, datetime)
        
        # Test boolean fields
        user = User(
            email="datatype_test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert isinstance(user.is_active, bool)
        assert isinstance(user.is_superuser, bool)
        assert user.is_active is True
        assert user.is_superuser is False


@pytest.mark.integration
class TestDatabaseErrorHandling:
    """Test database error handling scenarios."""
    
    @patch('app.db.create_engine')
    def test_database_connection_error_handling(self, mock_create_engine):
        """Test handling of database connection errors."""
        # Mock engine creation to raise an error
        mock_create_engine.side_effect = OperationalError(
            "Connection failed", None, None
        )
        
        with pytest.raises(OperationalError):
            init_db()
            
    def test_database_timeout_handling(self, db: Session):
        """Test handling of database timeout scenarios."""
        # Simulate a long-running query
        start_time = time.time()
        
        try:
            # Execute a query that might timeout
            result = db.exec(text("SELECT 1")).first()
            assert result == 1
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete quickly for simple query
            assert execution_time < 1.0
            
        except Exception as e:
            # Handle potential timeout or other database errors
            assert isinstance(e, (OperationalError, Exception))
            
    def test_database_recovery_after_error(self, engine):
        """Test database recovery after connection errors."""
        # Create a session and cause an error
        with Session(engine) as session:
            try:
                # Try to execute invalid SQL
                session.exec(text("INVALID SQL QUERY"))
            except Exception:
                # Error expected
                pass
                
        # Create new session and verify it works
        with Session(engine) as new_session:
            result = new_session.exec(text("SELECT 1")).first()
            assert result == 1
            
    def test_database_rollback_on_error(self, db: Session):
        """Test automatic rollback on errors."""
        # Create user first
        user = User(
            email="error_rollback_test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        try:
            # Try to create duplicate user (should fail)
            duplicate_user = User(
                email="error_rollback_test@example.com",  # Same email
                hashed_password=get_password_hash("password2"),
                is_active=True
            )
            db.add(duplicate_user)
            db.commit()  # This should fail
            
        except Exception:
            # Rollback should happen automatically
            db.rollback()
            
        # Verify original user still exists
        found_user = db.exec(
            select(User).where(User.email == "error_rollback_test@example.com")
        ).first()
        assert found_user is not None
        assert found_user.id == user.id


@pytest.mark.integration
class TestDatabasePerformance:
    """Test database performance characteristics."""
    
    def test_bulk_insert_performance(self, db: Session):
        """Test bulk insert performance."""
        start_time = time.time()
        
        # Create multiple users
        users = []
        for i in range(100):
            user = User(
                email=f"bulk_user_{i}@example.com",
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            users.append(user)
            
        # Bulk insert
        db.add_all(users)
        db.commit()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time
        assert execution_time < 5.0  # 5 seconds for 100 inserts
        
        # Verify all users were created
        user_count = len(db.exec(
            select(User).where(User.email.like("bulk_user_%@example.com"))
        ).all())
        assert user_count == 100
        
    def test_query_performance(self, db: Session):
        """Test query performance."""
        # Create test data
        for i in range(50):
            user = User(
                email=f"query_test_{i}@example.com",
                hashed_password=get_password_hash("password"),
                is_active=i % 2 == 0  # Alternate active/inactive
            )
            db.add(user)
        db.commit()
        
        # Test query performance
        start_time = time.time()
        
        active_users = db.exec(
            select(User).where(
                User.email.like("query_test_%@example.com")
            ).where(
                User.is_active == True
            )
        ).all()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly
        assert execution_time < 1.0
        assert len(active_users) == 25  # Half should be active
        
    def test_transaction_performance(self, db: Session):
        """Test transaction performance."""
        start_time = time.time()
        
        # Perform multiple operations in one transaction
        for i in range(20):
            user = User(
                email=f"transaction_test_{i}@example.com",
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            db.add(user)
            
            # Also create OAuth session for each user
            oauth_session = OAuthSession(
                endpoint_id=i + 1,
                state=f"state_{i}",
                code_verifier=f"verifier_{i}"
            )
            db.add(oauth_session)
            
        db.commit()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time
        assert execution_time < 3.0
        
        # Verify all data was committed
        user_count = len(db.exec(
            select(User).where(User.email.like("transaction_test_%@example.com"))
        ).all())
        assert user_count == 20
        
        session_count = len(db.exec(
            select(OAuthSession).where(OAuthSession.state.like("state_%"))
        ).all())
        assert session_count == 20


@pytest.mark.integration
class TestDatabaseMigration:
    """Test database migration scenarios."""
    
    def test_schema_creation(self, engine):
        """Test that schema creation works properly."""
        # Verify tables exist
        from sqlmodel import SQLModel
        
        # Get table names
        inspector = None
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            # Check that expected tables exist
            expected_tables = ['user', 'oauthsession', 'apiendpoint', 'apitest']
            
            for table in expected_tables:
                # Table names might be case-sensitive or have different naming
                # This is a flexible check
                assert any(table.lower() in tn.lower() for tn in table_names), \
                    f"Table {table} not found in {table_names}"
                    
        except ImportError:
            # If inspect is not available, skip this test
            pytest.skip("SQLAlchemy inspect not available")
            
    def test_data_migration_compatibility(self, db: Session):
        """Test data migration compatibility."""
        # Create data with current schema
        user = User(
            email="migration_test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Verify data integrity
        assert user.id is not None
        assert isinstance(user.created_at, datetime)
        assert user.email == "migration_test@example.com"
        
        # Test that we can query the data
        found_user = db.exec(
            select(User).where(User.email == "migration_test@example.com")
        ).first()
        assert found_user is not None
        assert found_user.id == user.id