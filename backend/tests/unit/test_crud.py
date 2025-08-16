"""
Unit tests for CRUD operations.
"""
import pytest
from sqlmodel import Session
from unittest.mock import Mock, patch

from app.crud.endpoints import create_endpoint, get_endpoint, list_endpoints, update_endpoint, delete_endpoint
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from app.crud.oauth_tokens import save_token_to_db, get_latest_token
from app.crud.tests import create_test, list_tests
from app.models import ApiEndpoint, User, OAuthSession, OAuthToken, ApiTest


@pytest.mark.unit
class TestEndpointsCRUD:
    """Test endpoints CRUD operations."""
    
    def test_create_endpoint(self, session: Session):
        """Test endpoint creation."""
        endpoint_data = ApiEndpoint(
            name="Test Endpoint",
            url="https://api.test.com",
            auth_type="oauth",
            oauth_scope="read write"
        )
        
        created = create_endpoint(session, endpoint_data)
        
        assert created.id is not None
        assert created.name == "Test Endpoint"
        assert created.url == "https://api.test.com"
        assert created.auth_type == "oauth"
        assert created.oauth_scope == "read write"
    
    def test_get_endpoint(self, session: Session):
        """Test endpoint retrieval."""
        # Create endpoint first
        endpoint_data = ApiEndpoint(
            name="Get Test Endpoint",
            url="https://api.gettest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Retrieve it
        retrieved = get_endpoint(session, created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Get Test Endpoint"
    
    def test_get_endpoint_not_found(self, session: Session):
        """Test endpoint retrieval with non-existent ID."""
        retrieved = get_endpoint(session, 999999)
        assert retrieved is None
    
    def test_list_endpoints(self, session: Session):
        """Test listing all endpoints."""
        # Create multiple endpoints
        endpoints_data = [
            ApiEndpoint(name="List Test 1", url="https://api1.test.com"),
            ApiEndpoint(name="List Test 2", url="https://api2.test.com"),
        ]
        
        created_endpoints = []
        for endpoint_data in endpoints_data:
            created = create_endpoint(session, endpoint_data)
            created_endpoints.append(created)
        
        # List all endpoints
        all_endpoints = list_endpoints(session)
        
        assert len(all_endpoints) >= 2
        created_ids = [ep.id for ep in created_endpoints]
        retrieved_ids = [ep.id for ep in all_endpoints]
        
        for created_id in created_ids:
            assert created_id in retrieved_ids
    
    def test_update_endpoint(self, session: Session):
        """Test endpoint update."""
        # Create endpoint
        endpoint_data = ApiEndpoint(
            name="Update Test",
            url="https://api.updatetest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Update it
        update_data = {"name": "Updated Test", "url": "https://api.updated.com"}
        updated = update_endpoint(session, created.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated Test"
        assert updated.url == "https://api.updated.com"
    
    def test_update_endpoint_not_found(self, session: Session):
        """Test endpoint update with non-existent ID."""
        update_data = {"name": "Non-existent"}
        updated = update_endpoint(session, 999999, update_data)
        assert updated is None
    
    def test_delete_endpoint(self, session: Session):
        """Test endpoint deletion."""
        # Create endpoint
        endpoint_data = ApiEndpoint(
            name="Delete Test",
            url="https://api.deletetest.com"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Delete it
        deleted = delete_endpoint(session, created.id)
        assert deleted is True
        
        # Verify deletion
        retrieved = get_endpoint(session, created.id)
        assert retrieved is None
    
    def test_delete_endpoint_not_found(self, session: Session):
        """Test endpoint deletion with non-existent ID."""
        deleted = delete_endpoint(session, 999999)
        assert deleted is False


@pytest.mark.unit
class TestOAuthSessionsCRUD:
    """Test OAuth sessions CRUD operations."""
    
    def test_save_oauth_session(self, session: Session):
        """Test saving OAuth session."""
        state = "test_state_123"
        code_verifier = "test_verifier_123"
        
        save_oauth_session(session, state, code_verifier)
        
        # Verify saved
        oauth_session = get_oauth_session(session, state)
        assert oauth_session is not None
        assert oauth_session.state == state
        assert oauth_session.code_verifier == code_verifier
    
    def test_get_oauth_session(self, session: Session):
        """Test retrieving OAuth session."""
        state = "get_test_state"
        code_verifier = "get_test_verifier"
        
        # Save first
        save_oauth_session(session, state, code_verifier)
        
        # Retrieve
        retrieved = get_oauth_session(session, state)
        assert retrieved is not None
        assert retrieved.state == state
        assert retrieved.code_verifier == code_verifier
    
    def test_get_oauth_session_not_found(self, session: Session):
        """Test retrieving non-existent OAuth session."""
        retrieved = get_oauth_session(session, "non_existent_state")
        assert retrieved is None
    
    def test_delete_oauth_session(self, session: Session):
        """Test deleting OAuth session."""
        state = "delete_test_state"
        code_verifier = "delete_test_verifier"
        
        # Save first
        save_oauth_session(session, state, code_verifier)
        
        # Delete
        delete_oauth_session(session, state)
        
        # Verify deletion
        retrieved = get_oauth_session(session, state)
        assert retrieved is None
    
    def test_delete_oauth_session_not_found(self, session: Session):
        """Test deleting non-existent OAuth session."""
        # Should not raise error
        delete_oauth_session(session, "non_existent_state")


@pytest.mark.unit
class TestOAuthTokensCRUD:
    """Test OAuth tokens CRUD operations."""
    
    def test_save_token_to_db(self, session: Session, test_user: User, mock_ml_token):
        """Test saving OAuth token."""
        saved_token = save_token_to_db(mock_ml_token, test_user.id, session)
        
        # Verify saved
        assert saved_token is not None
        assert saved_token.user_id == test_user.id
        assert saved_token.access_token == mock_ml_token["access_token"]
    
    def test_get_latest_token(self, session: Session, test_user: User, mock_ml_token):
        """Test retrieving latest OAuth token."""
        # Save first
        save_token_to_db(mock_ml_token, test_user.id, session)
        
        # Retrieve
        retrieved = get_latest_token(test_user.id, session)
        assert retrieved is not None
        assert retrieved.user_id == test_user.id
        assert retrieved.access_token == mock_ml_token["access_token"]
        assert retrieved.refresh_token == mock_ml_token["refresh_token"]
    
    def test_get_latest_token_not_found(self, session: Session):
        """Test retrieving non-existent OAuth token."""
        retrieved = get_latest_token(999999, session)
        assert retrieved is None
    
    def test_get_latest_token_multiple(self, session: Session, test_user: User, mock_ml_token):
        """Test getting latest token when multiple exist."""
        # Save first token
        save_token_to_db(mock_ml_token, test_user.id, session)
        
        # Save second token
        new_token = mock_ml_token.copy()
        new_token["access_token"] = "NEW_TOKEN"
        save_token_to_db(new_token, test_user.id, session)
        
        # Should get the latest one
        retrieved = get_latest_token(test_user.id, session)
        assert retrieved.access_token == "NEW_TOKEN"


@pytest.mark.unit
class TestTestsCRUD:
    """Test API tests CRUD operations."""
    
    def test_create_test(self, session: Session):
        """Test creating test."""
        api_test = ApiTest(
            name="Test Case",
            request_method="GET",
            request_path="/test",
            status_code=200,
            response_body='{"success": true}'
        )
        
        saved = create_test(session, api_test)
        
        assert saved.id is not None
        assert saved.name == "Test Case"
        assert saved.request_method == "GET"
        assert saved.status_code == 200
    
    def test_list_tests(self, session: Session):
        """Test listing tests."""
        # Create multiple tests
        test_cases = [
            ApiTest(name="List Test 1", request_method="GET", request_path="/1"),
            ApiTest(name="List Test 2", request_method="POST", request_path="/2"),
        ]
        
        saved_tests = []
        for test_data in test_cases:
            saved = create_test(session, test_data)
            saved_tests.append(saved)
        
        # List all
        all_tests = list_tests(session)
        
        assert len(all_tests) >= 2
        saved_ids = [test.id for test in saved_tests]
        retrieved_ids = [test.id for test in all_tests]
        
        for saved_id in saved_ids:
            assert saved_id in retrieved_ids
    
    def test_list_tests_with_limit(self, session: Session):
        """Test listing tests with limit."""
        # Create multiple tests
        for i in range(5):
            api_test = ApiTest(name=f"Limit Test {i}", request_method="GET", request_path=f"/{i}")
            create_test(session, api_test)
        
        # List with limit
        limited_tests = list_tests(session, limit=3)
        
        assert len(limited_tests) <= 3


@pytest.mark.unit
class TestCRUDErrorHandling:
    """Test CRUD error handling and edge cases."""
    
    def test_create_endpoint_with_duplicate_name(self, session: Session):
        """Test creating endpoints with same name (should be allowed)."""
        endpoint_data = ApiEndpoint(
            name="Duplicate Name",
            url="https://api1.test.com"
        )
        created1 = create_endpoint(session, endpoint_data)
        
        # Create another with same name but different URL
        endpoint_data2 = ApiEndpoint(
            name="Duplicate Name",
            url="https://api2.test.com"
        )
        created2 = create_endpoint(session, endpoint_data2)
        
        assert created1.id != created2.id
        assert created1.name == created2.name
        assert created1.url != created2.url
    
    def test_update_endpoint_partial(self, session: Session):
        """Test partial endpoint update."""
        # Create endpoint
        endpoint_data = ApiEndpoint(
            name="Partial Update Test",
            url="https://api.partialtest.com",
            auth_type="oauth"
        )
        created = create_endpoint(session, endpoint_data)
        
        # Update only name
        update_data = {"name": "Updated Name Only"}
        updated = update_endpoint(session, created.id, update_data)
        
        assert updated.name == "Updated Name Only"
        assert updated.url == "https://api.partialtest.com"  # Unchanged
        assert updated.auth_type == "oauth"  # Unchanged
    
    def test_oauth_session_state_collision(self, session: Session):
        """Test handling OAuth session state collisions."""
        state = "collision_test_state"
        
        # Save first session
        save_oauth_session(session, state, "verifier1")
        
        # Save second session with same state (should overwrite)
        save_oauth_session(session, state, "verifier2")
        
        # Should have the latest verifier
        retrieved = get_oauth_session(session, state)
        assert retrieved.code_verifier == "verifier2"
    
    def test_oauth_token_user_collision(self, session: Session, test_user: User, mock_ml_token):
        """Test handling OAuth token user collisions."""
        # Save first token
        save_token_to_db(mock_ml_token, test_user.id, session)
        
        # Save second token for same user (should create new entry)
        new_token = mock_ml_token.copy()
        new_token["access_token"] = "NEW_TOKEN"
        save_token_to_db(new_token, test_user.id, session)
        
        # Should have the latest token
        retrieved = get_latest_token(test_user.id, session)
        assert retrieved.access_token == "NEW_TOKEN"
    
    def test_create_test_minimal_data(self, session: Session):
        """Test creating test with minimal data."""
        minimal_test = ApiTest(name="Minimal Test")
        
        saved = create_test(session, minimal_test)
        
        assert saved.id is not None
        assert saved.name == "Minimal Test"
        assert saved.request_method == "GET"  # Default value
        assert saved.request_path == "/"  # Default value
    
    @patch('sqlmodel.Session.add')
    def test_create_endpoint_database_error(self, mock_add, session: Session):
        """Test create endpoint with database error."""
        mock_add.side_effect = Exception("Database error")
        
        endpoint_data = ApiEndpoint(
            name="Error Test",
            url="https://api.errortest.com"
        )
        
        with pytest.raises(Exception, match="Database error"):
            create_endpoint(session, endpoint_data)
    
    @patch('sqlmodel.Session.exec')
    def test_get_endpoint_database_error(self, mock_exec, session: Session):
        """Test get endpoint with database error."""
        mock_exec.side_effect = Exception("Database query error")
        
        with pytest.raises(Exception, match="Database query error"):
            get_endpoint(session, 1)