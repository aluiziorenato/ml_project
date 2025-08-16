"""API routes for Campaign Automation Service."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis

from ..models.campaign_models import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStatus,
    MetricsSummary, ABTestCreate, ABTestResponse, CompetitorAnalysis
)
from ..core.campaign_manager import CampaignManager
from ..core.metrics_analyzer import MetricsAnalyzer
from ..core.competitor_monitor import CompetitorMonitor
from ..services.ai_integration import AIIntegrationService
from ..services.scheduler import SchedulerService, TaskType, TaskPriority
from ..utils.config import settings
from ..utils.logger import logger, log_error


# Security
security = HTTPBearer(auto_error=False)

# Router instance
router = APIRouter()

# Database dependency (placeholder - would be implemented with actual DB session)
def get_db():
    """Get database session."""
    # This would return actual SQLAlchemy session in production
    pass

# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # In production, this would validate JWT token
    # For now, return mock user
    return {"user_id": "user_123", "username": "demo_user"}

# Redis dependency
def get_redis():
    """Get Redis client."""
    return redis.from_url(settings.redis_url)


# Campaign Management Routes
@router.post("/campaigns", response_model=CampaignResponse, tags=["Campaigns"])
async def create_campaign(
    campaign: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign."""
    try:
        manager = CampaignManager(db)
        result = await manager.create_campaign(campaign, current_user["user_id"])
        
        # Schedule initial optimization task
        scheduler = SchedulerService()
        await scheduler.schedule_task(
            task_type=TaskType.CAMPAIGN_OPTIMIZATION,
            campaign_id=result.id,
            parameters={"optimization_type": "initial_setup"},
            schedule_time=datetime.utcnow() + timedelta(minutes=5)
        )
        
        return result
    except Exception as e:
        log_error(e, {"action": "create_campaign", "user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", response_model=List[CampaignResponse], tags=["Campaigns"])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[CampaignStatus] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List campaigns with optional filters."""
    try:
        manager = CampaignManager(db)
        return await manager.list_campaigns(
            skip=skip, 
            limit=limit, 
            status=status, 
            user_id=current_user["user_id"]
        )
    except Exception as e:
        log_error(e, {"action": "list_campaigns", "user_id": current_user["user_id"]})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["Campaigns"])
async def get_campaign(
    campaign_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign by ID."""
    try:
        manager = CampaignManager(db)
        campaign = await manager.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "get_campaign", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["Campaigns"])
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update campaign."""
    try:
        manager = CampaignManager(db)
        campaign = await manager.update_campaign(
            campaign_id, campaign_update, current_user["user_id"]
        )
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "update_campaign", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/activate", response_model=CampaignResponse, tags=["Campaigns"])
async def activate_campaign(
    campaign_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a campaign."""
    try:
        manager = CampaignManager(db)
        campaign = await manager.activate_campaign(campaign_id, current_user["user_id"])
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Schedule ongoing optimization tasks
        scheduler = SchedulerService()
        await scheduler.schedule_task(
            task_type=TaskType.PERFORMANCE_ANALYSIS,
            campaign_id=campaign_id,
            parameters={"period": "daily"},
            schedule_time=datetime.utcnow() + timedelta(hours=24),
            recurring=True,
            recurring_interval=timedelta(days=1)
        )
        
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "activate_campaign", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/pause", response_model=CampaignResponse, tags=["Campaigns"])
async def pause_campaign(
    campaign_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause a campaign."""
    try:
        manager = CampaignManager(db)
        campaign = await manager.pause_campaign(campaign_id, current_user["user_id"])
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "pause_campaign", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


# Metrics and Analytics Routes
@router.get("/campaigns/{campaign_id}/metrics", response_model=MetricsSummary, tags=["Analytics"])
async def get_campaign_metrics(
    campaign_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign performance metrics."""
    try:
        manager = CampaignManager(db)
        metrics = await manager.get_campaign_performance(campaign_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "get_campaign_metrics", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/metrics/hourly", tags=["Analytics"])
async def get_hourly_metrics(
    campaign_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hourly metrics breakdown."""
    try:
        analyzer = MetricsAnalyzer(db)
        return await analyzer.get_hourly_metrics(campaign_id, start_date, end_date)
    except Exception as e:
        log_error(e, {"action": "get_hourly_metrics", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/metrics/daily", tags=["Analytics"])
async def get_daily_metrics(
    campaign_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily aggregated metrics."""
    try:
        analyzer = MetricsAnalyzer(db)
        return await analyzer.get_daily_aggregated_metrics(campaign_id, start_date, end_date)
    except Exception as e:
        log_error(e, {"action": "get_daily_metrics", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/analysis/trends", tags=["Analytics"])
async def analyze_performance_trends(
    campaign_id: int,
    days: int = Query(7, ge=1, le=90),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze performance trends."""
    try:
        analyzer = MetricsAnalyzer(db)
        return await analyzer.analyze_performance_trends(campaign_id, days)
    except Exception as e:
        log_error(e, {"action": "analyze_performance_trends", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/analysis/benchmark", tags=["Analytics"])
async def get_benchmark_comparison(
    campaign_id: int,
    category: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare campaign performance against benchmarks."""
    try:
        analyzer = MetricsAnalyzer(db)
        return await analyzer.get_benchmark_comparison(campaign_id, category)
    except Exception as e:
        log_error(e, {"action": "get_benchmark_comparison", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


# AI Optimization Routes
@router.post("/campaigns/{campaign_id}/optimize/copy", tags=["AI Optimization"])
async def optimize_campaign_copy(
    campaign_id: int,
    copy_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize campaign copy using AI."""
    try:
        ai_service = AIIntegrationService()
        return await ai_service.optimize_campaign_copy(
            campaign_id=campaign_id,
            current_copy=copy_data.get("text", ""),
            target_audience=copy_data.get("target_audience", {}),
            category=copy_data.get("category", "general")
        )
    except Exception as e:
        log_error(e, {"action": "optimize_campaign_copy", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/predict", tags=["AI Optimization"])
async def predict_campaign_performance(
    campaign_id: int,
    prediction_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict campaign performance using ML models."""
    try:
        ai_service = AIIntegrationService()
        return await ai_service.predict_campaign_performance(
            campaign_data=prediction_data,
            historical_data=prediction_data.get("historical_data")
        )
    except Exception as e:
        log_error(e, {"action": "predict_campaign_performance", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/optimize/bidding", tags=["AI Optimization"])
async def optimize_bidding_strategy(
    campaign_id: int,
    optimization_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize bidding strategy based on performance."""
    try:
        ai_service = AIIntegrationService()
        return await ai_service.optimize_bidding_strategy(
            campaign_id=campaign_id,
            current_performance=optimization_data.get("current_performance", {}),
            optimization_goal=optimization_data.get("optimization_goal", "conversions")
        )
    except Exception as e:
        log_error(e, {"action": "optimize_bidding_strategy", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


# A/B Testing Routes
@router.post("/campaigns/{campaign_id}/ab-tests", response_model=ABTestResponse, tags=["A/B Testing"])
async def create_ab_test(
    campaign_id: int,
    ab_test: ABTestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new A/B test for a campaign."""
    try:
        # This would be implemented with actual A/B test creation logic
        # For now, return a mock response
        return ABTestResponse(
            id=123,
            campaign_id=campaign_id,
            name=ab_test.name,
            description=ab_test.description,
            test_type=ab_test.test_type,
            variants=ab_test.variants,
            status="running",
            statistical_significance=False,
            winning_variant=None,
            created_at=datetime.utcnow()
        )
    except Exception as e:
        log_error(e, {"action": "create_ab_test", "campaign_id": campaign_id})
        raise HTTPException(status_code=500, detail=str(e))


# Competitor Analysis Routes
@router.post("/competitor/analyze", response_model=CompetitorAnalysis, tags=["Competitor Analysis"])
async def analyze_competitor(
    competitor_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a specific competitor."""
    try:
        monitor = CompetitorMonitor(db)
        return await monitor.analyze_competitor(
            competitor_name=competitor_data["competitor_name"],
            category=competitor_data["category"],
            keywords=competitor_data.get("keywords", [])
        )
    except Exception as e:
        log_error(e, {"action": "analyze_competitor"})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitor/category/{category}", tags=["Competitor Analysis"])
async def monitor_category_competitors(
    category: str,
    max_competitors: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Monitor competitors in a specific category."""
    try:
        monitor = CompetitorMonitor(db)
        return await monitor.monitor_category_competitors(category, max_competitors)
    except Exception as e:
        log_error(e, {"action": "monitor_category_competitors", "category": category})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitor/keywords/analyze", tags=["Competitor Analysis"])
async def analyze_keyword_competition(
    keyword_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze keyword competition landscape."""
    try:
        monitor = CompetitorMonitor(db)
        return await monitor.get_keyword_competition_analysis(
            keywords=keyword_data["keywords"],
            category=keyword_data["category"]
        )
    except Exception as e:
        log_error(e, {"action": "analyze_keyword_competition"})
        raise HTTPException(status_code=500, detail=str(e))


# Automation and Scheduling Routes
@router.post("/automation/schedule", tags=["Automation"])
async def schedule_automation_task(
    task_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Schedule an automation task."""
    try:
        scheduler = SchedulerService()
        
        task_type = TaskType(task_data["task_type"])
        schedule_time = datetime.fromisoformat(task_data["schedule_time"]) if "schedule_time" in task_data else None
        priority = TaskPriority(task_data.get("priority", "medium"))
        
        task_id = await scheduler.schedule_task(
            task_type=task_type,
            campaign_id=task_data.get("campaign_id"),
            parameters=task_data.get("parameters", {}),
            schedule_time=schedule_time,
            priority=priority,
            recurring=task_data.get("recurring", False),
            recurring_interval=timedelta(seconds=task_data["recurring_interval"]) if "recurring_interval" in task_data else None
        )
        
        return {"task_id": task_id, "status": "scheduled"}
    except Exception as e:
        log_error(e, {"action": "schedule_automation_task"})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/automation/tasks/{task_id}", tags=["Automation"])
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of an automation task."""
    try:
        scheduler = SchedulerService()
        task_status = await scheduler.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task_status
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "get_task_status", "task_id": task_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/automation/tasks/{task_id}", tags=["Automation"])
async def cancel_automation_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a pending automation task."""
    try:
        scheduler = SchedulerService()
        success = await scheduler.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
        
        return {"message": "Task cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"action": "cancel_automation_task", "task_id": task_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/automation/stats", tags=["Automation"])
async def get_automation_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get automation scheduler statistics."""
    try:
        scheduler = SchedulerService()
        return await scheduler.get_scheduler_stats()
    except Exception as e:
        log_error(e, {"action": "get_automation_stats"})
        raise HTTPException(status_code=500, detail=str(e))


# Health and Status Routes
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_client = get_redis()
        redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "campaign_automation_service",
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "redis": "healthy",
                "scheduler": "healthy"
            }
        }
    except Exception as e:
        log_error(e, {"action": "health_check"})
        return {
            "status": "unhealthy",
            "service": "campaign_automation_service",
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/info", tags=["Health"])
async def service_info():
    """Get service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "Campaign Automation Service for Mercado Livre ML Integration",
        "features": [
            "Campaign Management",
            "Performance Analytics",
            "AI-Powered Optimization", 
            "Competitor Monitoring",
            "A/B Testing",
            "Automated Scheduling"
        ],
        "endpoints": {
            "campaigns": "/campaigns",
            "analytics": "/campaigns/{id}/metrics",
            "optimization": "/campaigns/{id}/optimize",
            "competitor_analysis": "/competitor",
            "automation": "/automation"
        }
    }