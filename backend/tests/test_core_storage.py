"""
Unit tests for core storage modules.
"""

import pytest
import tempfile
import shutil
from datetime import datetime
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.storage.data_manager import DataManager, DataQuery, DataResult


class TestDataManager:
    """Test cases for DataManager class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_file_storage(self):
        """Test file storage initialization."""
        manager = DataManager(storage_type="file", data_directory=self.temp_dir)
        assert manager.storage_type == "file"
        assert str(manager.data_directory) == self.temp_dir
    
    def test_init_sqlite_storage(self):
        """Test SQLite storage initialization."""
        manager = DataManager(storage_type="sqlite", data_directory=self.temp_dir)
        assert manager.storage_type == "sqlite"
        assert manager.db_path.exists()
    
    def test_store_data_file(self):
        """Test storing data in file storage."""
        manager = DataManager(storage_type="file", data_directory=self.temp_dir)
        
        test_data = {
            "test_id": "test_123",
            "value": 42.0,
            "timestamp": datetime.now().isoformat()
        }
        
        result = manager.store_data("test_table", test_data)
        
        assert result.success is True
        assert result.row_count == 1
    
    def test_query_data_file(self):
        """Test querying data from file storage."""
        manager = DataManager(storage_type="file", data_directory=self.temp_dir)
        
        # Store test data first
        test_data = {
            "test_id": "test_123",
            "value": 42.0
        }
        manager.store_data("test_table", test_data)
        
        # Query the data
        query = DataQuery(table="test_table")
        result = manager.query_data(query)
        
        assert result.success is True
        assert len(result.data) > 0
        assert result.data[0]["value"] == 42.0
    
    def test_query_data_with_filters(self):
        """Test querying data with filters."""
        manager = DataManager(storage_type="file", data_directory=self.temp_dir)
        
        # Store multiple test records
        test_data1 = {"test_id": "test_123", "category": "A", "value": 10}
        test_data2 = {"test_id": "test_456", "category": "B", "value": 20}
        
        manager.store_data("test_table", test_data1)
        manager.store_data("test_table", test_data2)
        
        # Query with filter
        query = DataQuery(table="test_table", filters={"category": "A"})
        result = manager.query_data(query)
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["category"] == "A"
    
    def test_delete_data_file(self):
        """Test deleting data from file storage."""
        manager = DataManager(storage_type="file", data_directory=self.temp_dir)
        
        # Store test data first
        test_data = {"test_id": "test_123", "value": 42.0}
        manager.store_data("test_table", test_data)
        
        # Delete the data
        result = manager.delete_data("test_table", {"test_id": "test_123"})
        
        assert result.success is True
        assert result.row_count == 1
        
        # Verify deletion
        query = DataQuery(table="test_table", filters={"test_id": "test_123"})
        query_result = manager.query_data(query)
        assert len(query_result.data) == 0
    
    def test_store_data_sqlite(self):
        """Test storing data in SQLite storage."""
        manager = DataManager(storage_type="sqlite", data_directory=self.temp_dir)
        
        test_data = {
            "campaign_id": "test_campaign_001",
            "name": "Test Campaign",
            "budget": 5000,
            "status": "active"
        }
        
        result = manager.store_data("campaigns", test_data)
        
        assert result.success is True
        assert result.row_count > 0
    
    def test_query_data_sqlite(self):
        """Test querying data from SQLite storage."""
        manager = DataManager(storage_type="sqlite", data_directory=self.temp_dir)
        
        # Store test data first
        test_data = {
            "campaign_id": "test_campaign_001",
            "name": "Test Campaign",
            "budget": 5000
        }
        manager.store_data("campaigns", test_data)
        
        # Query the data
        query = DataQuery(table="campaigns", filters={"campaign_id": "test_campaign_001"})
        result = manager.query_data(query)
        
        assert result.success is True
        assert len(result.data) > 0
        assert result.data[0]["name"] == "Test Campaign"
    
    def test_get_storage_info(self):
        """Test getting storage information."""
        manager = DataManager(storage_type="file", data_directory=self.temp_dir)
        
        info = manager.get_storage_info()
        
        assert info["storage_type"] == "file"
        assert "data_directory" in info
        assert "files" in info
    
    def test_data_query_class(self):
        """Test DataQuery class."""
        query = DataQuery(
            table="test_table",
            filters={"status": "active"},
            fields=["id", "name"],
            limit=10,
            offset=5,
            order_by="created_at",
            order_direction="DESC"
        )
        
        assert query.table == "test_table"
        assert query.filters == {"status": "active"}
        assert query.fields == ["id", "name"]
        assert query.limit == 10
        assert query.offset == 5
        assert query.order_by == "created_at"
        assert query.order_direction == "DESC"
    
    def test_data_result_class(self):
        """Test DataResult class."""
        result = DataResult(
            success=True,
            data={"test": "data"},
            row_count=1,
            error_message=None,
            execution_time=0.5,
            metadata={"source": "test"}
        )
        
        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.row_count == 1
        assert result.error_message is None
        assert result.execution_time == 0.5
        assert result.metadata == {"source": "test"}