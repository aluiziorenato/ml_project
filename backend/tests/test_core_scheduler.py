"""
Unit tests for core scheduler modules.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.scheduler.task_manager import TaskManager, Task, TaskResult, TaskStatus


class TestTaskManager:
    """Test cases for TaskManager class."""
    
    def test_init(self):
        """Test task manager initialization."""
        manager = TaskManager(max_workers=2)
        assert manager.max_workers == 2
        assert not manager.is_running
        assert manager.tasks == {}
        assert manager.results == {}
        assert manager.scheduled_tasks == []
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping task manager."""
        manager = TaskManager()
        
        # Start manager
        await manager.start()
        assert manager.is_running is True
        
        # Stop manager
        await manager.stop()
        assert manager.is_running is False
    
    def test_add_task(self):
        """Test adding immediate execution task."""
        manager = TaskManager()
        
        def test_func():
            return "test_result"
        
        task_id = manager.add_task(
            func=test_func,
            args=(1, 2),
            kwargs={"key": "value"},
            priority=2,
            retry_count=5,
            timeout=30.0
        )
        
        assert isinstance(task_id, str)
        assert task_id in manager.tasks
        
        task = manager.tasks[task_id]
        assert task.func == test_func
        assert task.args == (1, 2)
        assert task.kwargs == {"key": "value"}
        assert task.priority == 2
        assert task.retry_count == 5
        assert task.timeout == 30.0
        assert task.status == TaskStatus.PENDING
    
    def test_schedule_task(self):
        """Test scheduling task for future execution."""
        manager = TaskManager()
        
        def test_func():
            return "scheduled_result"
        
        future_time = datetime.now() + timedelta(hours=1)
        task_id = manager.schedule_task(
            func=test_func,
            scheduled_time=future_time,
            priority=3
        )
        
        assert task_id in manager.tasks
        assert task_id in [tid for _, tid in manager.scheduled_tasks]
        
        task = manager.tasks[task_id]
        assert task.scheduled_at == future_time
        assert task.status == TaskStatus.SCHEDULED
        assert task.priority == 3
    
    def test_cancel_task_pending(self):
        """Test cancelling pending task."""
        manager = TaskManager()
        
        def test_func():
            return "test"
        
        task_id = manager.add_task(func=test_func)
        success = manager.cancel_task(task_id)
        
        assert success is True
        assert manager.tasks[task_id].status == TaskStatus.CANCELLED
    
    def test_get_task_statistics(self):
        """Test getting task statistics."""
        manager = TaskManager()
        
        def test_func():
            return "test"
        
        # Add some tasks
        task1 = manager.add_task(func=test_func)
        task2 = manager.add_task(func=test_func)
        
        # Set different statuses
        manager.tasks[task1].status = TaskStatus.COMPLETED
        manager.tasks[task2].status = TaskStatus.FAILED
        
        stats = manager.get_task_statistics()
        
        assert stats["total_tasks"] == 2
        assert stats["completed_tasks"] == 1
        assert stats["failed_tasks"] == 1
    
    def test_task_class(self):
        """Test Task class."""
        def test_func():
            return "test"
        
        task = Task(
            task_id="test_123",
            func=test_func,
            args=(1, 2),
            kwargs={"key": "value"},
            priority=2,
            retry_count=3,
            timeout=30.0
        )
        
        assert task.task_id == "test_123"
        assert task.func == test_func
        assert task.args == (1, 2)
        assert task.kwargs == {"key": "value"}
        assert task.priority == 2
        assert task.retry_count == 3
        assert task.timeout == 30.0
        assert task.status == TaskStatus.PENDING
        assert task.attempts == 0
        assert isinstance(task.created_at, datetime)
    
    def test_task_status_enum(self):
        """Test TaskStatus enum."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.SCHEDULED.value == "scheduled"