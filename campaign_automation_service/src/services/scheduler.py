"""Scheduler service for automated campaign tasks."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import redis
import json
from celery import Celery

from ..utils.config import settings
from ..utils.logger import logger, log_error, log_task


class TaskType(str, Enum):
    """Task type enumeration."""
    CAMPAIGN_OPTIMIZATION = "campaign_optimization"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    COMPETITOR_MONITORING = "competitor_monitoring"
    AB_TEST_ANALYSIS = "ab_test_analysis"
    BUDGET_ADJUSTMENT = "budget_adjustment"
    KEYWORD_RESEARCH = "keyword_research"
    REPORT_GENERATION = "report_generation"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Scheduled task data structure."""
    id: str
    task_type: TaskType
    priority: TaskPriority
    campaign_id: Optional[int]
    parameters: Dict[str, Any]
    schedule_time: datetime
    recurring: bool = False
    recurring_interval: Optional[timedelta] = None
    retry_count: int = 3
    timeout: int = 300  # 5 minutes default
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


# Initialize Celery
celery_app = Celery(
    "campaign_automation",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=500,  # 8 minutes 20 seconds
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


class SchedulerService:
    """Campaign automation scheduler service."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.tasks_key = "campaign_automation:scheduled_tasks"
        self.running_tasks_key = "campaign_automation:running_tasks"
        self.completed_tasks_key = "campaign_automation:completed_tasks"
        self.is_running = False
    
    async def schedule_task(
        self,
        task_type: TaskType,
        campaign_id: Optional[int],
        parameters: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        recurring: bool = False,
        recurring_interval: Optional[timedelta] = None
    ) -> str:
        """Schedule a new task."""
        try:
            task_id = f"{task_type.value}_{campaign_id}_{int(datetime.utcnow().timestamp())}"
            
            if schedule_time is None:
                schedule_time = datetime.utcnow()
            
            task = ScheduledTask(
                id=task_id,
                task_type=task_type,
                priority=priority,
                campaign_id=campaign_id,
                parameters=parameters,
                schedule_time=schedule_time,
                recurring=recurring,
                recurring_interval=recurring_interval
            )
            
            # Store task in Redis
            task_data = {
                "id": task.id,
                "task_type": task.task_type.value,
                "priority": task.priority.value,
                "campaign_id": task.campaign_id,
                "parameters": task.parameters,
                "schedule_time": task.schedule_time.isoformat(),
                "recurring": task.recurring,
                "recurring_interval": task.recurring_interval.total_seconds() if task.recurring_interval else None,
                "retry_count": task.retry_count,
                "timeout": task.timeout,
                "created_at": task.created_at.isoformat(),
                "status": TaskStatus.PENDING.value
            }
            
            self.redis_client.hset(self.tasks_key, task_id, json.dumps(task_data))
            
            logger.info(
                "Task scheduled",
                task_id=task_id,
                task_type=task_type.value,
                campaign_id=campaign_id,
                schedule_time=schedule_time.isoformat()
            )
            
            return task_id
            
        except Exception as e:
            log_error(e, {"action": "schedule_task", "task_type": task_type.value})
            raise
    
    async def start_scheduler(self):
        """Start the task scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        logger.info("Scheduler started")
        
        try:
            while self.is_running:
                await self._process_pending_tasks()
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            log_error(e, {"action": "start_scheduler"})
            self.is_running = False
    
    async def stop_scheduler(self):
        """Stop the task scheduler."""
        self.is_running = False
        logger.info("Scheduler stopped")
    
    async def _process_pending_tasks(self):
        """Process pending tasks that are ready to run."""
        try:
            # Get all pending tasks
            all_tasks = self.redis_client.hgetall(self.tasks_key)
            current_time = datetime.utcnow()
            
            for task_id, task_data_json in all_tasks.items():
                task_data = json.loads(task_data_json)
                
                if task_data["status"] != TaskStatus.PENDING.value:
                    continue
                
                schedule_time = datetime.fromisoformat(task_data["schedule_time"])
                
                # Check if task is ready to run
                if schedule_time <= current_time:
                    await self._execute_task(task_id.decode(), task_data)
                    
        except Exception as e:
            log_error(e, {"action": "process_pending_tasks"})
    
    async def _execute_task(self, task_id: str, task_data: Dict[str, Any]):
        """Execute a scheduled task."""
        try:
            log_task(task_id, task_data["task_type"], "starting")
            
            # Update task status to running
            task_data["status"] = TaskStatus.RUNNING.value
            task_data["started_at"] = datetime.utcnow().isoformat()
            self.redis_client.hset(self.tasks_key, task_id, json.dumps(task_data))
            self.redis_client.hset(self.running_tasks_key, task_id, json.dumps(task_data))
            
            # Execute task based on type
            task_type = TaskType(task_data["task_type"])
            result = await self._dispatch_task(task_type, task_data)
            
            # Update task status to completed
            task_data["status"] = TaskStatus.COMPLETED.value
            task_data["completed_at"] = datetime.utcnow().isoformat()
            task_data["result"] = result
            
            log_task(task_id, task_data["task_type"], "completed")
            
            # Handle recurring tasks
            if task_data["recurring"] and task_data["recurring_interval"]:
                await self._schedule_next_occurrence(task_data)
            
            # Move to completed tasks
            self.redis_client.hset(self.completed_tasks_key, task_id, json.dumps(task_data))
            self.redis_client.hdel(self.tasks_key, task_id)
            self.redis_client.hdel(self.running_tasks_key, task_id)
            
        except Exception as e:
            # Mark task as failed
            task_data["status"] = TaskStatus.FAILED.value
            task_data["error"] = str(e)
            task_data["failed_at"] = datetime.utcnow().isoformat()
            
            self.redis_client.hset(self.tasks_key, task_id, json.dumps(task_data))
            self.redis_client.hdel(self.running_tasks_key, task_id)
            
            log_task(task_id, task_data["task_type"], "failed", error=str(e))
            log_error(e, {"action": "execute_task", "task_id": task_id})
    
    async def _dispatch_task(self, task_type: TaskType, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch task to appropriate handler."""
        handlers = {
            TaskType.CAMPAIGN_OPTIMIZATION: self._handle_campaign_optimization,
            TaskType.PERFORMANCE_ANALYSIS: self._handle_performance_analysis,
            TaskType.COMPETITOR_MONITORING: self._handle_competitor_monitoring,
            TaskType.AB_TEST_ANALYSIS: self._handle_ab_test_analysis,
            TaskType.BUDGET_ADJUSTMENT: self._handle_budget_adjustment,
            TaskType.KEYWORD_RESEARCH: self._handle_keyword_research,
            TaskType.REPORT_GENERATION: self._handle_report_generation
        }
        
        handler = handlers.get(task_type)
        if not handler:
            raise ValueError(f"No handler for task type: {task_type}")
        
        return await handler(task_data)
    
    async def _handle_campaign_optimization(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle campaign optimization task."""
        # This would integrate with the AI services
        campaign_id = task_data["campaign_id"]
        parameters = task_data["parameters"]
        
        # Simulate optimization process
        await asyncio.sleep(2)  # Simulate processing time
        
        return {
            "optimization_type": parameters.get("optimization_type", "general"),
            "improvements_applied": ["keyword_optimization", "bid_adjustment", "copy_enhancement"],
            "estimated_improvement": 15.5,  # percentage
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_performance_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance analysis task."""
        campaign_id = task_data["campaign_id"]
        parameters = task_data["parameters"]
        
        # Simulate analysis
        await asyncio.sleep(1)
        
        return {
            "analysis_period": parameters.get("period", "7_days"),
            "metrics_analyzed": ["ctr", "cpc", "roas", "conversions"],
            "insights_generated": 8,
            "recommendations_count": 5,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_competitor_monitoring(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle competitor monitoring task."""
        parameters = task_data["parameters"]
        
        # Simulate monitoring
        await asyncio.sleep(3)
        
        return {
            "competitors_monitored": parameters.get("competitors", []),
            "category": parameters.get("category", "general"),
            "threats_detected": 2,
            "opportunities_found": 4,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_ab_test_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A/B test analysis task."""
        campaign_id = task_data["campaign_id"]
        parameters = task_data["parameters"]
        
        # Simulate A/B test analysis
        await asyncio.sleep(1)
        
        return {
            "test_id": parameters.get("test_id"),
            "statistical_significance": True,
            "winning_variant": "variant_b",
            "confidence_level": 95.8,
            "improvement": 12.3,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_budget_adjustment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle budget adjustment task."""
        campaign_id = task_data["campaign_id"]
        parameters = task_data["parameters"]
        
        # Simulate budget adjustment
        await asyncio.sleep(1)
        
        return {
            "adjustment_type": parameters.get("adjustment_type", "performance_based"),
            "old_budget": parameters.get("current_budget", 0),
            "new_budget": parameters.get("current_budget", 0) * 1.1,  # 10% increase
            "reason": "Performance exceeding targets",
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_keyword_research(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle keyword research task."""
        campaign_id = task_data["campaign_id"]
        parameters = task_data["parameters"]
        
        # Simulate keyword research
        await asyncio.sleep(2)
        
        return {
            "category": parameters.get("category", "general"),
            "keywords_found": 45,
            "high_opportunity_keywords": 12,
            "low_competition_keywords": 18,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_report_generation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report generation task."""
        campaign_id = task_data["campaign_id"]
        parameters = task_data["parameters"]
        
        # Simulate report generation
        await asyncio.sleep(1)
        
        return {
            "report_type": parameters.get("report_type", "performance"),
            "period": parameters.get("period", "weekly"),
            "campaigns_included": 1 if campaign_id else parameters.get("campaign_count", 0),
            "report_url": f"/reports/{task_data['id']}.pdf",
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _schedule_next_occurrence(self, task_data: Dict[str, Any]):
        """Schedule the next occurrence of a recurring task."""
        try:
            if not task_data["recurring"] or not task_data["recurring_interval"]:
                return
            
            interval_seconds = task_data["recurring_interval"]
            next_run_time = datetime.fromisoformat(task_data["schedule_time"]) + timedelta(seconds=interval_seconds)
            
            # Create new task for next occurrence
            new_task_id = f"{task_data['task_type']}_{task_data['campaign_id']}_{int(next_run_time.timestamp())}"
            
            new_task_data = task_data.copy()
            new_task_data["id"] = new_task_id
            new_task_data["schedule_time"] = next_run_time.isoformat()
            new_task_data["status"] = TaskStatus.PENDING.value
            new_task_data["created_at"] = datetime.utcnow().isoformat()
            
            # Remove execution metadata
            for key in ["started_at", "completed_at", "result", "error", "failed_at"]:
                new_task_data.pop(key, None)
            
            self.redis_client.hset(self.tasks_key, new_task_id, json.dumps(new_task_data))
            
            logger.info(
                "Recurring task scheduled",
                task_id=new_task_id,
                next_run_time=next_run_time.isoformat()
            )
            
        except Exception as e:
            log_error(e, {"action": "schedule_next_occurrence", "task_id": task_data["id"]})
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        try:
            # Check in pending tasks
            task_data = self.redis_client.hget(self.tasks_key, task_id)
            if task_data:
                return json.loads(task_data)
            
            # Check in running tasks
            task_data = self.redis_client.hget(self.running_tasks_key, task_id)
            if task_data:
                return json.loads(task_data)
            
            # Check in completed tasks
            task_data = self.redis_client.hget(self.completed_tasks_key, task_id)
            if task_data:
                return json.loads(task_data)
            
            return None
            
        except Exception as e:
            log_error(e, {"action": "get_task_status", "task_id": task_id})
            return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        try:
            task_data = self.redis_client.hget(self.tasks_key, task_id)
            if not task_data:
                return False
            
            task_dict = json.loads(task_data)
            if task_dict["status"] != TaskStatus.PENDING.value:
                return False
            
            task_dict["status"] = TaskStatus.CANCELLED.value
            task_dict["cancelled_at"] = datetime.utcnow().isoformat()
            
            self.redis_client.hset(self.completed_tasks_key, task_id, json.dumps(task_dict))
            self.redis_client.hdel(self.tasks_key, task_id)
            
            logger.info("Task cancelled", task_id=task_id)
            return True
            
        except Exception as e:
            log_error(e, {"action": "cancel_task", "task_id": task_id})
            return False
    
    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        try:
            pending_count = self.redis_client.hlen(self.tasks_key)
            running_count = self.redis_client.hlen(self.running_tasks_key)
            completed_count = self.redis_client.hlen(self.completed_tasks_key)
            
            return {
                "is_running": self.is_running,
                "pending_tasks": pending_count,
                "running_tasks": running_count,
                "completed_tasks": completed_count,
                "total_tasks": pending_count + running_count + completed_count,
                "stats_retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log_error(e, {"action": "get_scheduler_stats"})
            return {
                "error": str(e),
                "stats_retrieved_at": datetime.utcnow().isoformat()
            }


# Global scheduler instance
scheduler = SchedulerService()