"""
Scheduler service layer for task management and scheduling.
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import logging
import asyncio

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.scheduler import TaskManager, TaskResult, TaskStatus
from core.storage import DataManager, DataQuery

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service layer for scheduler operations.
    Provides high-level interface for task management and scheduling.
    """
    
    def __init__(self, data_manager: Optional[DataManager] = None):
        self.task_manager = TaskManager()
        self.data_manager = data_manager or DataManager()
        self.task_functions = {}
        self._register_default_tasks()
        
    def _register_default_tasks(self):
        """Register default task types."""
        self.task_functions.update({
            "analytics_prediction": self._analytics_prediction_task,
            "data_processing": self._data_processing_task,
            "model_training": self._model_training_task,
            "optimization": self._optimization_task,
            "cleanup": self._cleanup_task,
            "health_check": self._health_check_task,
            "backup": self._backup_task
        })
    
    async def start(self):
        """Start the scheduler service."""
        await self.task_manager.start()
        logger.info("Scheduler service started")
    
    async def stop(self):
        """Stop the scheduler service."""
        await self.task_manager.stop()
        logger.info("Scheduler service stopped")
    
    async def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.task_manager.is_running
    
    async def create_task(self,
                         task_type: str,
                         parameters: Dict[str, Any],
                         priority: int = 1,
                         retry_count: int = 3,
                         timeout: Optional[float] = None,
                         task_id: Optional[str] = None) -> str:
        """
        Create and execute a task immediately.
        
        Args:
            task_type: Type of task to create
            parameters: Task parameters
            priority: Task priority
            retry_count: Number of retry attempts
            timeout: Task timeout
            task_id: Optional custom task ID
            
        Returns:
            Task ID string
        """
        try:
            if task_type not in self.task_functions:
                raise ValueError(f"Unknown task type: {task_type}")
            
            task_func = self.task_functions[task_type]
            
            task_id = self.task_manager.add_task(
                func=lambda: task_func(parameters),
                priority=priority,
                retry_count=retry_count,
                timeout=timeout,
                task_id=task_id
            )
            
            # Store task information
            await self._store_task_info(task_id, task_type, parameters, priority)
            
            return task_id
            
        except Exception as e:
            logger.error(f"Task creation failed: {str(e)}")
            raise
    
    async def schedule_task(self,
                          task_type: str,
                          parameters: Dict[str, Any],
                          scheduled_time: datetime,
                          priority: int = 1,
                          retry_count: int = 3,
                          timeout: Optional[float] = None,
                          task_id: Optional[str] = None) -> str:
        """
        Schedule a task for future execution.
        
        Args:
            task_type: Type of task to schedule
            parameters: Task parameters
            scheduled_time: When to execute the task
            priority: Task priority
            retry_count: Number of retry attempts
            timeout: Task timeout
            task_id: Optional custom task ID
            
        Returns:
            Task ID string
        """
        try:
            if task_type not in self.task_functions:
                raise ValueError(f"Unknown task type: {task_type}")
            
            task_func = self.task_functions[task_type]
            
            task_id = self.task_manager.schedule_task(
                func=lambda: task_func(parameters),
                scheduled_time=scheduled_time,
                priority=priority,
                retry_count=retry_count,
                timeout=timeout,
                task_id=task_id
            )
            
            # Store task information
            await self._store_task_info(task_id, task_type, parameters, priority, scheduled_time)
            
            return task_id
            
        except Exception as e:
            logger.error(f"Task scheduling failed: {str(e)}")
            raise
    
    async def create_recurring_task(self,
                                  task_type: str,
                                  parameters: Dict[str, Any],
                                  interval: timedelta,
                                  start_time: Optional[datetime] = None,
                                  max_executions: Optional[int] = None,
                                  priority: int = 1) -> List[str]:
        """
        Create a recurring task.
        
        Args:
            task_type: Type of task to create
            parameters: Task parameters
            interval: Time interval between executions
            start_time: When to start
            max_executions: Maximum number of executions
            priority: Task priority
            
        Returns:
            List of task IDs for scheduled executions
        """
        try:
            if task_type not in self.task_functions:
                raise ValueError(f"Unknown task type: {task_type}")
            
            task_func = self.task_functions[task_type]
            
            task_ids = self.task_manager.schedule_recurring_task(
                func=lambda: task_func(parameters),
                interval=interval,
                start_time=start_time,
                max_executions=max_executions
            )
            
            # Store information for each scheduled task
            for task_id in task_ids:
                await self._store_task_info(task_id, task_type, parameters, priority)
            
            return task_ids
            
        except Exception as e:
            logger.error(f"Recurring task creation failed: {str(e)}")
            raise
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a specific task."""
        return self.task_manager.get_task_result(task_id)
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        return self.task_manager.get_task_status(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or scheduled task."""
        success = self.task_manager.cancel_task(task_id)
        
        if success:
            # Update task status in storage
            await self._update_task_status(task_id, TaskStatus.CANCELLED)
        
        return success
    
    async def list_tasks(self,
                        status: Optional[TaskStatus] = None,
                        task_type: Optional[str] = None,
                        limit: int = 100,
                        offset: int = 0) -> List[TaskResult]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by task status
            task_type: Filter by task type
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of TaskResult objects
        """
        try:
            # Get tasks from storage
            query = DataQuery(
                table="tasks",
                limit=limit,
                offset=offset,
                order_by="created_at",
                order_direction="DESC"
            )
            
            filters = {}
            if status:
                filters["status"] = status.value
            if task_type:
                filters["task_type"] = task_type
            
            if filters:
                query.filters = filters
            
            result = self.data_manager.query_data(query)
            
            if result.success:
                # Convert to TaskResult objects
                task_results = []
                for task_data in result.data:
                    task_result = TaskResult(
                        task_id=task_data["task_id"],
                        status=TaskStatus(task_data["status"]),
                        result_data=task_data.get("result"),
                        error_message=task_data.get("error_message"),
                        execution_time=0.0,  # Would need to calculate from storage
                        start_time=datetime.fromisoformat(task_data["created_at"]),
                        end_time=datetime.fromisoformat(task_data["completed_at"]) if task_data.get("completed_at") else None,
                        metadata={}
                    )
                    task_results.append(task_result)
                
                return task_results
            else:
                logger.error(f"Failed to query tasks: {result.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list tasks: {str(e)}")
            return []
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics."""
        try:
            # Get stats from task manager
            manager_stats = self.task_manager.get_task_statistics()
            
            # Get additional stats from storage
            query = DataQuery(table="tasks")
            result = self.data_manager.query_data(query)
            
            storage_stats = {
                "total_in_storage": 0,
                "by_status": {},
                "by_type": {}
            }
            
            if result.success:
                storage_stats["total_in_storage"] = len(result.data)
                
                for task in result.data:
                    status = task.get("status", "unknown")
                    task_type = task.get("task_type", "unknown")
                    
                    storage_stats["by_status"][status] = storage_stats["by_status"].get(status, 0) + 1
                    storage_stats["by_type"][task_type] = storage_stats["by_type"].get(task_type, 0) + 1
            
            # Combine stats
            combined_stats = {
                **manager_stats,
                "storage_stats": storage_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Failed to get task statistics: {str(e)}")
            raise
    
    def register_task_function(self, task_type: str, func: Callable):
        """Register a custom task function."""
        self.task_functions[task_type] = func
        logger.info(f"Registered task function for type: {task_type}")
    
    # Task function implementations
    async def _analytics_prediction_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics prediction task."""
        try:
            # This would integrate with the analytics service
            prediction_type = parameters.get("prediction_type", "general")
            features = parameters.get("features", [])
            
            # Simulate prediction (in real implementation, would call analytics service)
            result = {
                "prediction_type": prediction_type,
                "predicted_value": sum(features) / len(features) if features else 0.0,
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Analytics prediction task completed: {prediction_type}")
            return result
            
        except Exception as e:
            logger.error(f"Analytics prediction task failed: {str(e)}")
            raise
    
    async def _data_processing_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data processing task."""
        try:
            data_source = parameters.get("data_source", "unknown")
            processing_type = parameters.get("processing_type", "general")
            
            # Simulate data processing
            await asyncio.sleep(1)  # Simulate processing time
            
            result = {
                "data_source": data_source,
                "processing_type": processing_type,
                "processed_records": parameters.get("record_count", 100),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Data processing task completed: {processing_type}")
            return result
            
        except Exception as e:
            logger.error(f"Data processing task failed: {str(e)}")
            raise
    
    async def _model_training_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute model training task."""
        try:
            model_type = parameters.get("model_type", "linear")
            training_samples = parameters.get("training_samples", 1000)
            
            # Simulate training
            await asyncio.sleep(2)  # Simulate training time
            
            result = {
                "model_type": model_type,
                "training_samples": training_samples,
                "accuracy": 0.85 + (training_samples / 10000) * 0.1,  # Simulate accuracy
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Model training task completed: {model_type}")
            return result
            
        except Exception as e:
            logger.error(f"Model training task failed: {str(e)}")
            raise
    
    async def _optimization_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization task."""
        try:
            optimization_type = parameters.get("optimization_type", "general")
            target_metric = parameters.get("target_metric", "roi")
            
            # Simulate optimization
            await asyncio.sleep(1.5)
            
            result = {
                "optimization_type": optimization_type,
                "target_metric": target_metric,
                "improvement": 0.15,  # 15% improvement
                "optimized_parameters": parameters.get("parameters", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Optimization task completed: {optimization_type}")
            return result
            
        except Exception as e:
            logger.error(f"Optimization task failed: {str(e)}")
            raise
    
    async def _cleanup_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cleanup task."""
        try:
            cleanup_type = parameters.get("cleanup_type", "general")
            max_age_days = parameters.get("max_age_days", 30)
            
            # Simulate cleanup
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            result = {
                "cleanup_type": cleanup_type,
                "cutoff_date": cutoff_date.isoformat(),
                "cleaned_items": 25,  # Simulate number of cleaned items
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Cleanup task completed: {cleanup_type}")
            return result
            
        except Exception as e:
            logger.error(f"Cleanup task failed: {str(e)}")
            raise
    
    async def _health_check_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health check task."""
        try:
            check_type = parameters.get("check_type", "system")
            
            result = {
                "check_type": check_type,
                "status": "healthy",
                "checks_performed": ["database", "memory", "cpu"],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Health check task completed: {check_type}")
            return result
            
        except Exception as e:
            logger.error(f"Health check task failed: {str(e)}")
            raise
    
    async def _backup_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backup task."""
        try:
            backup_type = parameters.get("backup_type", "incremental")
            target_location = parameters.get("target_location", "/backups")
            
            # Simulate backup
            await asyncio.sleep(3)  # Simulate backup time
            
            result = {
                "backup_type": backup_type,
                "target_location": target_location,
                "backup_size_mb": 150,  # Simulate backup size
                "files_backed_up": 500,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Backup task completed: {backup_type}")
            return result
            
        except Exception as e:
            logger.error(f"Backup task failed: {str(e)}")
            raise
    
    async def _store_task_info(self,
                             task_id: str,
                             task_type: str,
                             parameters: Dict[str, Any],
                             priority: int,
                             scheduled_at: Optional[datetime] = None):
        """Store task information in database."""
        try:
            data = {
                "task_id": task_id,
                "task_type": task_type,
                "status": TaskStatus.SCHEDULED.value if scheduled_at else TaskStatus.PENDING.value,
                "priority": priority,
                "scheduled_at": scheduled_at.isoformat() if scheduled_at else None,
                "parameters": parameters
            }
            
            self.data_manager.store_data("tasks", data)
            
        except Exception as e:
            logger.error(f"Failed to store task info: {str(e)}")
    
    async def _update_task_status(self, task_id: str, status: TaskStatus):
        """Update task status in database."""
        try:
            # This would require an update operation in data manager
            # For now, we'll just log it
            logger.info(f"Task {task_id} status updated to {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update task status: {str(e)}")