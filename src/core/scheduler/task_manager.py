"""
Task Manager module for scheduling and executing ML tasks.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    status: TaskStatus
    result_data: Optional[Any]
    error_message: Optional[str]
    execution_time: float
    start_time: datetime
    end_time: Optional[datetime]
    metadata: Dict[str, Any]


class Task:
    """Represents a schedulable task."""
    
    def __init__(self, 
                 task_id: str,
                 func: Callable,
                 args: tuple = (),
                 kwargs: Dict[str, Any] = None,
                 priority: int = 1,
                 retry_count: int = 3,
                 timeout: Optional[float] = None):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.retry_count = retry_count
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.scheduled_at = None
        self.attempts = 0
        self.metadata = {}


class TaskManager:
    """
    Task manager for scheduling and executing ML tasks.
    Supports both immediate and scheduled execution.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}  # task_id -> Task
        self.results = {}  # task_id -> TaskResult
        self.scheduled_tasks = []  # List of (datetime, task_id) for scheduled tasks
        self.running_tasks = set()
        self.is_running = False
        
    async def start(self):
        """Start the task manager."""
        self.is_running = True
        logger.info("Task manager started")
        
        # Start background scheduler
        asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        """Stop the task manager."""
        self.is_running = False
        self.executor.shutdown(wait=True)
        logger.info("Task manager stopped")
    
    def add_task(self, 
                 func: Callable,
                 args: tuple = (),
                 kwargs: Dict[str, Any] = None,
                 priority: int = 1,
                 retry_count: int = 3,
                 timeout: Optional[float] = None,
                 task_id: Optional[str] = None) -> str:
        """
        Add a task for immediate execution.
        
        Args:
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority (higher = more priority)
            retry_count: Number of retry attempts
            timeout: Task timeout in seconds
            task_id: Optional custom task ID
            
        Returns:
            Task ID string
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
            
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            retry_count=retry_count,
            timeout=timeout
        )
        
        self.tasks[task_id] = task
        logger.info(f"Added task {task_id} for immediate execution")
        
        # Execute immediately if manager is running
        if self.is_running:
            asyncio.create_task(self._execute_task(task_id))
            
        return task_id
    
    def schedule_task(self,
                     func: Callable,
                     scheduled_time: datetime,
                     args: tuple = (),
                     kwargs: Dict[str, Any] = None,
                     priority: int = 1,
                     retry_count: int = 3,
                     timeout: Optional[float] = None,
                     task_id: Optional[str] = None) -> str:
        """
        Schedule a task for future execution.
        
        Args:
            func: Function to execute
            scheduled_time: When to execute the task
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority
            retry_count: Number of retry attempts
            timeout: Task timeout in seconds
            task_id: Optional custom task ID
            
        Returns:
            Task ID string
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
            
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            retry_count=retry_count,
            timeout=timeout
        )
        
        task.scheduled_at = scheduled_time
        task.status = TaskStatus.SCHEDULED
        
        self.tasks[task_id] = task
        self.scheduled_tasks.append((scheduled_time, task_id))
        self.scheduled_tasks.sort(key=lambda x: x[0])  # Sort by time
        
        logger.info(f"Scheduled task {task_id} for {scheduled_time}")
        return task_id
    
    def schedule_recurring_task(self,
                              func: Callable,
                              interval: timedelta,
                              args: tuple = (),
                              kwargs: Dict[str, Any] = None,
                              start_time: Optional[datetime] = None,
                              max_executions: Optional[int] = None) -> List[str]:
        """
        Schedule a recurring task.
        
        Args:
            func: Function to execute
            interval: Time interval between executions
            args: Function arguments
            kwargs: Function keyword arguments
            start_time: When to start (default: now)
            max_executions: Maximum number of executions
            
        Returns:
            List of task IDs for scheduled executions
        """
        if start_time is None:
            start_time = datetime.now() + timedelta(seconds=1)
            
        task_ids = []
        current_time = start_time
        
        executions = 0
        while max_executions is None or executions < max_executions:
            if max_executions and executions >= max_executions:
                break
                
            task_id = self.schedule_task(
                func=func,
                scheduled_time=current_time,
                args=args,
                kwargs=kwargs
            )
            task_ids.append(task_id)
            
            current_time += interval
            executions += 1
            
            # Prevent infinite scheduling for very short intervals
            if executions > 1000:
                logger.warning("Stopping recurring task scheduling after 1000 executions")
                break
        
        logger.info(f"Scheduled {len(task_ids)} recurring executions")
        return task_ids
    
    async def _scheduler_loop(self):
        """Background loop to execute scheduled tasks."""
        while self.is_running:
            try:
                await self._check_scheduled_tasks()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _check_scheduled_tasks(self):
        """Check and execute scheduled tasks that are due."""
        now = datetime.now()
        due_tasks = []
        
        # Find tasks that are due
        while (self.scheduled_tasks and 
               self.scheduled_tasks[0][0] <= now):
            scheduled_time, task_id = self.scheduled_tasks.pop(0)
            due_tasks.append(task_id)
        
        # Execute due tasks
        for task_id in due_tasks:
            if task_id in self.tasks:
                asyncio.create_task(self._execute_task(task_id))
    
    async def _execute_task(self, task_id: str) -> TaskResult:
        """Execute a task."""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return None
            
        task = self.tasks[task_id]
        
        if task_id in self.running_tasks:
            logger.warning(f"Task {task_id} is already running")
            return self.results.get(task_id)
        
        self.running_tasks.add(task_id)
        task.status = TaskStatus.RUNNING
        start_time = datetime.now()
        
        try:
            task.attempts += 1
            logger.info(f"Executing task {task_id} (attempt {task.attempts})")
            
            # Execute the task in thread pool
            loop = asyncio.get_event_loop()
            
            if task.timeout:
                result_data = await asyncio.wait_for(
                    loop.run_in_executor(
                        self.executor,
                        lambda: task.func(*task.args, **task.kwargs)
                    ),
                    timeout=task.timeout
                )
            else:
                result_data = await loop.run_in_executor(
                    self.executor,
                    lambda: task.func(*task.args, **task.kwargs)
                )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            task.status = TaskStatus.COMPLETED
            
            result = TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                result_data=result_data,
                error_message=None,
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time,
                metadata={
                    "attempts": task.attempts,
                    "priority": task.priority
                }
            )
            
            self.results[task_id] = result
            logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task {task_id} timed out after {task.timeout}s"
            logger.error(error_msg)
            task.status = TaskStatus.FAILED
            
            result = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                result_data=None,
                error_message=error_msg,
                execution_time=(datetime.now() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.now(),
                metadata={"attempts": task.attempts, "timeout": True}
            )
            
        except Exception as e:
            error_msg = f"Task {task_id} failed: {str(e)}"
            logger.error(error_msg)
            
            # Retry if attempts remaining
            if task.attempts < task.retry_count:
                logger.info(f"Retrying task {task_id} ({task.attempts}/{task.retry_count})")
                task.status = TaskStatus.PENDING
                self.running_tasks.discard(task_id)
                
                # Schedule retry with delay
                await asyncio.sleep(2 ** task.attempts)  # Exponential backoff
                return await self._execute_task(task_id)
            else:
                task.status = TaskStatus.FAILED
                
                result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    result_data=None,
                    error_message=error_msg,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    start_time=start_time,
                    end_time=datetime.now(),
                    metadata={"attempts": task.attempts, "max_retries_exceeded": True}
                )
        
        finally:
            self.running_tasks.discard(task_id)
            
        if task_id not in self.results:
            self.results[task_id] = result
            
        return result
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a task."""
        return self.results.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or scheduled task."""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        
        if task.status in [TaskStatus.PENDING, TaskStatus.SCHEDULED]:
            task.status = TaskStatus.CANCELLED
            
            # Remove from scheduled tasks if it's there
            self.scheduled_tasks = [
                (time, tid) for time, tid in self.scheduled_tasks 
                if tid != task_id
            ]
            
            logger.info(f"Cancelled task {task_id}")
            return True
        
        logger.warning(f"Cannot cancel task {task_id} with status {task.status}")
        return False
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about task execution."""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        running_tasks = len(self.running_tasks)
        scheduled_tasks = len(self.scheduled_tasks)
        
        avg_execution_time = 0
        if self.results:
            total_time = sum(r.execution_time for r in self.results.values())
            avg_execution_time = total_time / len(self.results)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "scheduled_tasks": scheduled_tasks,
            "success_rate": completed_tasks / max(1, total_tasks),
            "average_execution_time": avg_execution_time
        }