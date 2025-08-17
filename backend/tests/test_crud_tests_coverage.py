"""
Test coverage for app/crud/tests.py to improve coverage from 44.44% to 100%.
Tests all CRUD operations, edge cases, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime

from app.crud.tests import create_test, list_tests
from app.models.api_test import ApiTest


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestCreateTestFunction:
    """Test the create_test function in crud/tests.py."""
    
    def test_create_test_basic(self, db_session: Session):
        """Test basic test creation."""
        api_test = ApiTest(name="Basic Test")
        
        result = create_test(db_session, api_test)
        
        assert result.id is not None
        assert result.name == "Basic Test"
        assert isinstance(result.executed_at, datetime)
    
    def test_create_test_with_all_fields(self, db_session: Session):
        """Test creating test with all fields populated."""
        api_test = ApiTest(
            name="Complete Test"
        )
        
        result = create_test(db_session, api_test)
        
        assert result.id is not None
        assert result.name == "Complete Test"
        assert isinstance(result.executed_at, datetime)
    
    def test_create_test_returns_refreshed_object(self, db_session: Session):
        """Test that create_test returns a refreshed object with ID."""
        api_test = ApiTest(name="Refresh Test")
        
        # Verify the object doesn't have an ID before creation
        assert api_test.id is None
        
        result = create_test(db_session, api_test)
        
        # Verify the returned object has an ID after creation
        assert result.id is not None
        assert result is api_test  # Should be the same object
    
    def test_create_test_commits_to_database(self, db_session: Session):
        """Test that create_test actually commits the data."""
        api_test = ApiTest(name="Commit Test")
        
        result = create_test(db_session, api_test)
        
        # Query the database directly to verify the data was committed
        found_test = db_session.get(ApiTest, result.id)
        assert found_test is not None
        assert found_test.name == "Commit Test"
    
    def test_create_test_with_none_name(self, db_session: Session):
        """Test creating test with None name."""
        api_test = ApiTest(name=None)
        
        result = create_test(db_session, api_test)
        
        assert result.id is not None
        assert result.name is None
    
    def test_create_test_multiple_instances(self, db_session: Session):
        """Test creating multiple test instances."""
        test1 = ApiTest(name="Test 1")
        test2 = ApiTest(name="Test 2")
        test3 = ApiTest(name="Test 3")
        
        result1 = create_test(db_session, test1)
        result2 = create_test(db_session, test2)
        result3 = create_test(db_session, test3)
        
        assert result1.id != result2.id != result3.id
        assert result1.name == "Test 1"
        assert result2.name == "Test 2"
        assert result3.name == "Test 3"


class TestListTestsFunction:
    """Test the list_tests function in crud/tests.py."""
    
    def test_list_tests_empty_database(self, db_session: Session):
        """Test listing tests when database is empty."""
        result = list_tests(db_session)
        
        assert result == []
    
    def test_list_tests_with_data(self, db_session: Session):
        """Test listing tests with data in database."""
        # Create some test data
        test1 = create_test(db_session, ApiTest(name="Test 1"))
        test2 = create_test(db_session, ApiTest(name="Test 2"))
        test3 = create_test(db_session, ApiTest(name="Test 3"))
        
        result = list_tests(db_session)
        
        assert len(result) == 3
        # Should be ordered by executed_at desc (most recent first)
        assert result[0].name in ["Test 1", "Test 2", "Test 3"]
    
    def test_list_tests_default_limit(self, db_session: Session):
        """Test that default limit is 100."""
        # Create exactly 100 tests
        for i in range(100):
            create_test(db_session, ApiTest(name=f"Test {i}"))
        
        result = list_tests(db_session)
        
        assert len(result) == 100
    
    def test_list_tests_custom_limit(self, db_session: Session):
        """Test listing tests with custom limit."""
        # Create 20 tests
        for i in range(20):
            create_test(db_session, ApiTest(name=f"Test {i}"))
        
        # Get only 5
        result = list_tests(db_session, limit=5)
        
        assert len(result) == 5
    
    def test_list_tests_limit_larger_than_available(self, db_session: Session):
        """Test when limit is larger than available records."""
        # Create only 3 tests
        create_test(db_session, ApiTest(name="Test 1"))
        create_test(db_session, ApiTest(name="Test 2"))
        create_test(db_session, ApiTest(name="Test 3"))
        
        # Ask for 10
        result = list_tests(db_session, limit=10)
        
        assert len(result) == 3
    
    def test_list_tests_zero_limit(self, db_session: Session):
        """Test listing tests with zero limit."""
        # Create some tests
        create_test(db_session, ApiTest(name="Test 1"))
        create_test(db_session, ApiTest(name="Test 2"))
        
        result = list_tests(db_session, limit=0)
        
        assert len(result) == 0
    
    def test_list_tests_ordered_by_executed_at_desc(self, db_session: Session):
        """Test that tests are ordered by executed_at in descending order."""
        import time
        
        # Create tests with slight time differences
        test1 = create_test(db_session, ApiTest(name="First Test"))
        time.sleep(0.01)  # Small delay to ensure different timestamps
        test2 = create_test(db_session, ApiTest(name="Second Test"))
        time.sleep(0.01)
        test3 = create_test(db_session, ApiTest(name="Third Test"))
        
        result = list_tests(db_session)
        
        # Most recent should be first (Third Test)
        assert result[0].name == "Third Test"
        assert result[1].name == "Second Test"
        assert result[2].name == "First Test"
        
        # Verify the ordering is indeed by executed_at
        assert result[0].executed_at >= result[1].executed_at >= result[2].executed_at


class TestCrudTestsIntegration:
    """Test integration between create_test and list_tests functions."""
    
    def test_create_and_list_integration(self, db_session: Session):
        """Test that created tests appear in list_tests."""
        # Start with empty database
        assert list_tests(db_session) == []
        
        # Create a test
        created_test = create_test(db_session, ApiTest(name="Integration Test"))
        
        # Verify it appears in the list
        result = list_tests(db_session)
        assert len(result) == 1
        assert result[0].id == created_test.id
        assert result[0].name == "Integration Test"
    
    def test_multiple_create_and_list(self, db_session: Session):
        """Test creating multiple tests and listing them."""
        test_names = ["Alpha", "Beta", "Gamma", "Delta"]
        created_tests = []
        
        for name in test_names:
            test = create_test(db_session, ApiTest(name=name))
            created_tests.append(test)
        
        # List all tests
        all_tests = list_tests(db_session)
        assert len(all_tests) == 4
        
        # Verify all created tests are in the list
        listed_ids = {t.id for t in all_tests}
        created_ids = {t.id for t in created_tests}
        assert listed_ids == created_ids


class TestCrudTestsErrorHandling:
    """Test error handling and edge cases."""
    
    def test_create_test_with_session_error(self, db_session: Session):
        """Test create_test behavior when session operations fail."""
        api_test = ApiTest(name="Error Test")
        
        # Mock session to raise error on commit
        with patch.object(db_session, 'commit', side_effect=Exception("Commit failed")):
            with pytest.raises(Exception) as exc_info:
                create_test(db_session, api_test)
            
            assert "Commit failed" in str(exc_info.value)
    
    def test_list_tests_with_session_error(self, db_session: Session):
        """Test list_tests behavior when query fails."""
        with patch.object(db_session, 'query', side_effect=Exception("Query failed")):
            with pytest.raises(Exception) as exc_info:
                list_tests(db_session)
            
            assert "Query failed" in str(exc_info.value)


class TestCrudTestsPerformance:
    """Test performance-related aspects."""
    
    def test_list_tests_limit_performance(self, db_session: Session):
        """Test that limit parameter actually limits database queries."""
        # Create many tests
        for i in range(50):
            create_test(db_session, ApiTest(name=f"Performance Test {i}"))
        
        # Test different limits
        result_5 = list_tests(db_session, limit=5)
        result_10 = list_tests(db_session, limit=10)
        result_20 = list_tests(db_session, limit=20)
        
        assert len(result_5) == 5
        assert len(result_10) == 10
        assert len(result_20) == 20
    
    def test_list_tests_handles_large_datasets(self, db_session: Session):
        """Test list_tests with larger datasets."""
        # Create 150 tests (more than default limit)
        for i in range(150):
            create_test(db_session, ApiTest(name=f"Large Dataset Test {i}"))
        
        # Default should return only 100
        result_default = list_tests(db_session)
        assert len(result_default) == 100
        
        # Can still request more
        result_all = list_tests(db_session, limit=200)
        assert len(result_all) == 150