"""
Data Manager module for data storage and retrieval operations.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import os
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DataQuery:
    """Represents a data query operation."""
    table: str
    filters: Dict[str, Any] = None
    fields: List[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    order_by: Optional[str] = None
    order_direction: str = "ASC"


@dataclass
class DataResult:
    """Result of a data operation."""
    success: bool
    data: Optional[Any] = None
    row_count: int = 0
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None


class DataManager:
    """
    Data manager for storing and retrieving ML project data.
    Supports both file-based and database storage.
    """
    
    def __init__(self, 
                 storage_type: str = "sqlite",
                 connection_string: Optional[str] = None,
                 data_directory: str = "./data"):
        self.storage_type = storage_type
        self.connection_string = connection_string
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        # Initialize storage
        if storage_type == "sqlite":
            self.db_path = self.data_directory / "ml_project.db"
            self._init_sqlite()
        elif storage_type == "file":
            self.json_dir = self.data_directory / "json_storage"
            self.json_dir.mkdir(exist_ok=True)
        
        logger.info(f"DataManager initialized with {storage_type} storage")
    
    def _init_sqlite(self):
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create campaigns table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        type TEXT,
                        status TEXT,
                        budget REAL,
                        start_date TEXT,
                        end_date TEXT,
                        parameters TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create predictions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prediction_id TEXT UNIQUE NOT NULL,
                        campaign_id TEXT,
                        model_type TEXT,
                        predicted_value REAL,
                        confidence_score REAL,
                        feature_importance TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Create optimizations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimizations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        optimization_id TEXT UNIQUE NOT NULL,
                        campaign_id TEXT,
                        optimization_type TEXT,
                        parameters TEXT,
                        expected_improvement REAL,
                        confidence_score REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Create tasks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT UNIQUE NOT NULL,
                        task_type TEXT,
                        status TEXT,
                        priority INTEGER,
                        scheduled_at TEXT,
                        started_at TEXT,
                        completed_at TEXT,
                        result TEXT,
                        error_message TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create performance_metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_id TEXT UNIQUE NOT NULL,
                        campaign_id TEXT,
                        metric_type TEXT,
                        value REAL,
                        timestamp TEXT,
                        metadata TEXT
                    )
                """)
                
                conn.commit()
                logger.info("SQLite database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {str(e)}")
            raise
    
    def store_data(self, 
                   table: str, 
                   data: Dict[str, Any], 
                   upsert: bool = False) -> DataResult:
        """
        Store data in the specified table.
        
        Args:
            table: Table name
            data: Data to store
            upsert: Whether to update if record exists
            
        Returns:
            DataResult with operation status
        """
        start_time = datetime.now()
        
        try:
            if self.storage_type == "sqlite":
                return self._store_sqlite(table, data, upsert)
            elif self.storage_type == "file":
                return self._store_file(table, data, upsert)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to store data: {str(e)}")
            return DataResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _store_sqlite(self, table: str, data: Dict[str, Any], upsert: bool) -> DataResult:
        """Store data in SQLite database."""
        start_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add timestamp if not present
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
            if 'updated_at' not in data:
                data['updated_at'] = datetime.now().isoformat()
            
            # Convert complex objects to JSON strings
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    processed_data[key] = json.dumps(value)
                else:
                    processed_data[key] = value
            
            # Build SQL query
            columns = list(processed_data.keys())
            placeholders = ['?' * len(columns)]
            values = list(processed_data.values())
            
            if upsert:
                # Use INSERT OR REPLACE for SQLite
                sql = f"""
                    INSERT OR REPLACE INTO {table} 
                    ({', '.join(columns)}) 
                    VALUES ({', '.join(['?'] * len(columns))})
                """
            else:
                sql = f"""
                    INSERT INTO {table} 
                    ({', '.join(columns)}) 
                    VALUES ({', '.join(['?'] * len(columns))})
                """
            
            cursor.execute(sql, values)
            row_count = cursor.rowcount
            conn.commit()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataResult(
            success=True,
            row_count=row_count,
            execution_time=execution_time,
            metadata={"table": table, "operation": "insert"}
        )
    
    def _store_file(self, table: str, data: Dict[str, Any], upsert: bool) -> DataResult:
        """Store data in JSON file."""
        start_time = datetime.now()
        
        file_path = self.json_dir / f"{table}.json"
        
        # Load existing data
        existing_data = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        
        # Add timestamp and ID if not present
        if 'id' not in data:
            data['id'] = len(existing_data) + 1
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()
        
        # Handle upsert
        if upsert and 'id' in data:
            # Find and update existing record
            for i, record in enumerate(existing_data):
                if record.get('id') == data['id']:
                    existing_data[i] = data
                    break
            else:
                existing_data.append(data)
        else:
            existing_data.append(data)
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2, default=str)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataResult(
            success=True,
            row_count=1,
            execution_time=execution_time,
            metadata={"table": table, "operation": "file_store"}
        )
    
    def query_data(self, query: DataQuery) -> DataResult:
        """
        Query data from storage.
        
        Args:
            query: DataQuery object with query parameters
            
        Returns:
            DataResult with query results
        """
        start_time = datetime.now()
        
        try:
            if self.storage_type == "sqlite":
                return self._query_sqlite(query)
            elif self.storage_type == "file":
                return self._query_file(query)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to query data: {str(e)}")
            return DataResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _query_sqlite(self, query: DataQuery) -> DataResult:
        """Query data from SQLite database."""
        start_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            # Build SQL query
            fields = ', '.join(query.fields) if query.fields else '*'
            sql = f"SELECT {fields} FROM {query.table}"
            params = []
            
            # Add WHERE clause
            if query.filters:
                where_conditions = []
                for key, value in query.filters.items():
                    where_conditions.append(f"{key} = ?")
                    params.append(value)
                sql += f" WHERE {' AND '.join(where_conditions)}"
            
            # Add ORDER BY
            if query.order_by:
                sql += f" ORDER BY {query.order_by} {query.order_direction}"
            
            # Add LIMIT and OFFSET
            if query.limit:
                sql += f" LIMIT {query.limit}"
                if query.offset:
                    sql += f" OFFSET {query.offset}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries and parse JSON fields
            result_data = []
            for row in rows:
                row_dict = dict(row)
                
                # Try to parse JSON fields
                for key, value in row_dict.items():
                    if isinstance(value, str) and value.startswith(('{', '[')):
                        try:
                            row_dict[key] = json.loads(value)
                        except json.JSONDecodeError:
                            pass  # Keep as string if not valid JSON
                
                result_data.append(row_dict)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataResult(
            success=True,
            data=result_data,
            row_count=len(result_data),
            execution_time=execution_time,
            metadata={"table": query.table, "operation": "query"}
        )
    
    def _query_file(self, query: DataQuery) -> DataResult:
        """Query data from JSON file."""
        start_time = datetime.now()
        
        file_path = self.json_dir / f"{query.table}.json"
        
        if not file_path.exists():
            return DataResult(
                success=True,
                data=[],
                row_count=0,
                execution_time=0.0,
                metadata={"table": query.table, "operation": "file_query"}
            )
        
        with open(file_path, 'r') as f:
            all_data = json.load(f)
        
        # Apply filters
        filtered_data = all_data
        if query.filters:
            filtered_data = [
                record for record in all_data
                if all(
                    record.get(key) == value 
                    for key, value in query.filters.items()
                )
            ]
        
        # Apply ordering
        if query.order_by:
            reverse = query.order_direction.upper() == "DESC"
            filtered_data.sort(
                key=lambda x: x.get(query.order_by, 0),
                reverse=reverse
            )
        
        # Apply pagination
        if query.offset:
            filtered_data = filtered_data[query.offset:]
        if query.limit:
            filtered_data = filtered_data[:query.limit]
        
        # Select fields
        if query.fields:
            filtered_data = [
                {field: record.get(field) for field in query.fields}
                for record in filtered_data
            ]
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataResult(
            success=True,
            data=filtered_data,
            row_count=len(filtered_data),
            execution_time=execution_time,
            metadata={"table": query.table, "operation": "file_query"}
        )
    
    def delete_data(self, table: str, filters: Dict[str, Any]) -> DataResult:
        """
        Delete data from storage.
        
        Args:
            table: Table name
            filters: Filters for records to delete
            
        Returns:
            DataResult with operation status
        """
        start_time = datetime.now()
        
        try:
            if self.storage_type == "sqlite":
                return self._delete_sqlite(table, filters)
            elif self.storage_type == "file":
                return self._delete_file(table, filters)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to delete data: {str(e)}")
            return DataResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _delete_sqlite(self, table: str, filters: Dict[str, Any]) -> DataResult:
        """Delete data from SQLite database."""
        start_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            for key, value in filters.items():
                where_conditions.append(f"{key} = ?")
                params.append(value)
            
            sql = f"DELETE FROM {table} WHERE {' AND '.join(where_conditions)}"
            cursor.execute(sql, params)
            row_count = cursor.rowcount
            conn.commit()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataResult(
            success=True,
            row_count=row_count,
            execution_time=execution_time,
            metadata={"table": table, "operation": "delete"}
        )
    
    def _delete_file(self, table: str, filters: Dict[str, Any]) -> DataResult:
        """Delete data from JSON file."""
        start_time = datetime.now()
        
        file_path = self.json_dir / f"{table}.json"
        
        if not file_path.exists():
            return DataResult(
                success=True,
                row_count=0,
                execution_time=0.0,
                metadata={"table": table, "operation": "file_delete"}
            )
        
        with open(file_path, 'r') as f:
            all_data = json.load(f)
        
        # Filter out records to delete
        original_count = len(all_data)
        remaining_data = [
            record for record in all_data
            if not all(
                record.get(key) == value 
                for key, value in filters.items()
            )
        ]
        
        deleted_count = original_count - len(remaining_data)
        
        # Save remaining data
        with open(file_path, 'w') as f:
            json.dump(remaining_data, f, indent=2, default=str)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataResult(
            success=True,
            row_count=deleted_count,
            execution_time=execution_time,
            metadata={"table": table, "operation": "file_delete"}
        )
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the storage system."""
        info = {
            "storage_type": self.storage_type,
            "data_directory": str(self.data_directory)
        }
        
        if self.storage_type == "sqlite":
            info["database_path"] = str(self.db_path)
            info["database_size"] = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            # Get table information
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    info["tables"] = tables
            except Exception as e:
                info["error"] = str(e)
                
        elif self.storage_type == "file":
            info["json_directory"] = str(self.json_dir)
            info["files"] = [f.name for f in self.json_dir.glob("*.json")]
        
        return info