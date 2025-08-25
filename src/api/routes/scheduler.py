"""
Scheduler API routes for task management and scheduling.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ...core.scheduler import TaskManager, TaskResult, TaskStatus
from ...services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


# Pydantic models for request/response
class TaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 1
    retry_count: int = 3
    timeout: Optional[float] = None


class ScheduledTaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]
    scheduled_time: datetime
    priority: int = 1
    retry_count: int = 3
    timeout: Optional[float] = None


class RecurringTaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]
    interval_seconds: int
    start_time: Optional[datetime] = None
    max_executions: Optional[int] = None
    priority: int = 1


def get_scheduler_service() -> SchedulerService:
    """Dependency to get scheduler service instance."""
    return SchedulerService()


@router.post("/tasks", response_model=Dict[str, Any])
async def create_task(
    request: TaskRequest,
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Create and execute a new task immediately.
    """
    try:
        task_id = await service.create_task(
            task_type=request.task_type,
            parameters=request.parameters,
            priority=request.priority,
            retry_count=request.retry_count,
            timeout=request.timeout
        )
        
        return {
            "task_id": task_id,
            "status": "created",
            "task_type": request.task_type,
            "priority": request.priority,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")


@router.post("/tasks/schedule", response_model=Dict[str, Any])
async def schedule_task(
    request: ScheduledTaskRequest,
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Schedule a task for future execution.
    """
    try:
        task_id = await service.schedule_task(
            task_type=request.task_type,
            parameters=request.parameters,
            scheduled_time=request.scheduled_time,
            priority=request.priority,
            retry_count=request.retry_count,
            timeout=request.timeout
        )
        
        return {
            "task_id": task_id,
            "status": "scheduled",
            "task_type": request.task_type,
            "scheduled_time": request.scheduled_time.isoformat(),
            "priority": request.priority,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task scheduling failed: {str(e)}")


@router.post("/tasks/recurring", response_model=Dict[str, Any])
async def create_recurring_task(
    request: RecurringTaskRequest,
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Create a recurring task.
    """
    try:
        task_ids = await service.create_recurring_task(
            task_type=request.task_type,
            parameters=request.parameters,
            interval=timedelta(seconds=request.interval_seconds),
            start_time=request.start_time,
            max_executions=request.max_executions,
            priority=request.priority
        )
        
        return {
            "task_ids": task_ids,
            "status": "scheduled",
            "task_type": request.task_type,
            "interval_seconds": request.interval_seconds,
            "executions_scheduled": len(task_ids),
            "start_time": (request.start_time or datetime.now()).isoformat(),
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recurring task creation failed: {str(e)}")


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_status(
    task_id: str,
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Get the status and result of a specific task.
    """
    try:
        result = await service.get_task_result(task_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": result.task_id,
            "status": result.status.value,
            "result_data": result.result_data,
            "error_message": result.error_message,
            "execution_time": result.execution_time,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "metadata": result.metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.delete("/tasks/{task_id}", response_model=Dict[str, Any])
async def cancel_task(
    task_id: str,
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Cancel a pending or scheduled task.
    """
    try:
        success = await service.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Task cannot be cancelled")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task cancellation failed: {str(e)}")


@router.get("/tasks", response_model=Dict[str, Any])
async def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    List tasks with optional filtering.
    """
    try:
        tasks = await service.list_tasks(
            status=TaskStatus(status) if status else None,
            task_type=task_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "tasks": [
                {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "result_data": task.result_data,
                    "execution_time": task.execution_time,
                    "start_time": task.start_time.isoformat(),
                    "end_time": task.end_time.isoformat() if task.end_time else None,
                    "metadata": task.metadata
                }
                for task in tasks
            ],
            "count": len(tasks),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_task_statistics(
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Get task execution statistics.
    """
    try:
        stats = await service.get_task_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/start", response_model=Dict[str, str])
async def start_scheduler(
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, str]:
    """
    Start the task scheduler.
    """
    try:
        await service.start()
        return {
            "status": "started",
            "message": "Task scheduler started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/stop", response_model=Dict[str, str])
async def stop_scheduler(
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, str]:
    """
    Stop the task scheduler.
    """
    try:
        await service.stop()
        return {
            "status": "stopped",
            "message": "Task scheduler stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


@router.get("/health", response_model=Dict[str, str])
async def health_check(
    service: SchedulerService = Depends(get_scheduler_service)
) -> Dict[str, str]:
    """
    Health check endpoint for scheduler service.
    """
    try:
        is_running = await service.is_running()
        return {
            "status": "healthy" if is_running else "stopped",
            "service": "scheduler",
            "running": str(is_running),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "scheduler",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }