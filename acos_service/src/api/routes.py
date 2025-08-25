"""API routes for ACOS Service."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis

from ..models.acos_models import (
    ACOSRuleCreate, ACOSRuleUpdate, ACOSRuleResponse, ACOSAlertResponse,
    ACOSMetrics, ACOSAnalysis, ACOSRule, ACOSAlert
)
from ..core.acos_engine import ACOSAutomationEngine
from ...campaign_automation_service.src.core.metrics_analyzer import MetricsAnalyzer
from ..utils.config import settings
from ..utils.logger import logger

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
    return {"user_id": "user_123", "username": "demo_user"}

# ACOS engine dependency
def get_acos_engine(db: Session = Depends(get_db)):
    """Get ACOS automation engine."""
    metrics_analyzer = MetricsAnalyzer(db)
    return ACOSAutomationEngine(db, metrics_analyzer)


# ACOS Rules Management
@router.post("/api/acos/rules", response_model=ACOSRuleResponse, tags=["ACOS Rules"])
async def create_acos_rule(
    rule: ACOSRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> ACOSRuleResponse:
    """Create a new ACOS automation rule."""
    try:
        db_rule = ACOSRule(
            name=rule.name,
            description=rule.description,
            threshold_type=rule.threshold_type,
            threshold_value=rule.threshold_value,
            evaluation_period_hours=rule.evaluation_period_hours,
            action_type=rule.action_type,
            action_config=rule.action_config,
            campaign_ids=rule.campaign_ids,
            categories=rule.categories,
            minimum_spend=rule.minimum_spend,
            created_by=current_user["username"]
        )
        
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        
        logger.info(f"ACOS rule created: {db_rule.id}", extra={"user": current_user["username"]})
        
        return ACOSRuleResponse.from_orm(db_rule)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating ACOS rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create ACOS rule")


@router.get("/api/acos/rules", response_model=List[ACOSRuleResponse], tags=["ACOS Rules"])
async def list_acos_rules(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[ACOSRuleResponse]:
    """List ACOS automation rules."""
    try:
        query = db.query(ACOSRule)
        
        if is_active is not None:
            query = query.filter(ACOSRule.is_active == is_active)
        
        if action_type:
            query = query.filter(ACOSRule.action_type == action_type)
        
        rules = query.offset(skip).limit(limit).all()
        
        return [ACOSRuleResponse.from_orm(rule) for rule in rules]
        
    except Exception as e:
        logger.error(f"Error listing ACOS rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to list ACOS rules")


@router.get("/api/acos/rules/{rule_id}", response_model=ACOSRuleResponse, tags=["ACOS Rules"])
async def get_acos_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> ACOSRuleResponse:
    """Get a specific ACOS rule."""
    try:
        rule = db.query(ACOSRule).filter(ACOSRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="ACOS rule not found")
        
        return ACOSRuleResponse.from_orm(rule)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ACOS rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ACOS rule")


@router.put("/api/acos/rules/{rule_id}", response_model=ACOSRuleResponse, tags=["ACOS Rules"])
async def update_acos_rule(
    rule_id: int,
    rule_update: ACOSRuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> ACOSRuleResponse:
    """Update an ACOS rule."""
    try:
        db_rule = db.query(ACOSRule).filter(ACOSRule.id == rule_id).first()
        
        if not db_rule:
            raise HTTPException(status_code=404, detail="ACOS rule not found")
        
        # Update fields that were provided
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        db_rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_rule)
        
        logger.info(f"ACOS rule updated: {rule_id}", extra={"user": current_user["username"]})
        
        return ACOSRuleResponse.from_orm(db_rule)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating ACOS rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update ACOS rule")


@router.delete("/api/acos/rules/{rule_id}", tags=["ACOS Rules"])
async def delete_acos_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an ACOS rule."""
    try:
        db_rule = db.query(ACOSRule).filter(ACOSRule.id == rule_id).first()
        
        if not db_rule:
            raise HTTPException(status_code=404, detail="ACOS rule not found")
        
        db.delete(db_rule)
        db.commit()
        
        logger.info(f"ACOS rule deleted: {rule_id}", extra={"user": current_user["username"]})
        
        return {"message": "ACOS rule deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting ACOS rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete ACOS rule")


# ACOS Metrics and Analysis
@router.get("/api/acos/campaigns/{campaign_id}/metrics", response_model=ACOSMetrics, tags=["ACOS Metrics"])
async def get_campaign_acos_metrics(
    campaign_id: int,
    period_hours: int = Query(24, ge=1, le=168, description="Analysis period in hours"),
    acos_engine: ACOSAutomationEngine = Depends(get_acos_engine),
    current_user = Depends(get_current_user)
) -> ACOSMetrics:
    """Get ACOS metrics for a specific campaign."""
    try:
        current_acos = await acos_engine._calculate_campaign_acos(campaign_id, period_hours)
        previous_acos = await acos_engine._calculate_campaign_acos(
            campaign_id, 
            period_hours * 2
        )
        
        # Determine trend
        trend = "stable"
        if current_acos and previous_acos:
            if current_acos > previous_acos * 1.1:
                trend = "increasing"
            elif current_acos < previous_acos * 0.9:
                trend = "decreasing"
        
        # Get spend and revenue
        total_spend = await acos_engine._get_campaign_spend(campaign_id, period_hours)
        
        # Calculate revenue (reverse engineering from ACOS)
        total_revenue = 0.0
        if current_acos and current_acos > 0:
            total_revenue = (total_spend / current_acos) * 100
        
        # Generate recommendations
        recommendations = []
        if current_acos and current_acos > 25:
            recommendations.extend([
                "Consider reducing bid amounts",
                "Review keyword performance",
                "Optimize product listings"
            ])
        
        return ACOSMetrics(
            campaign_id=campaign_id,
            current_acos=current_acos or 0.0,
            acos_trend=trend,
            period_hours=period_hours,
            total_spend=total_spend,
            total_revenue=total_revenue,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error getting ACOS metrics for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ACOS metrics")


@router.get("/api/acos/campaigns/{campaign_id}/analysis", response_model=ACOSAnalysis, tags=["ACOS Analysis"])
async def analyze_campaign_acos(
    campaign_id: int,
    period_hours: int = Query(168, ge=24, le=720, description="Analysis period in hours"),
    acos_engine: ACOSAutomationEngine = Depends(get_acos_engine),
    current_user = Depends(get_current_user)
) -> ACOSAnalysis:
    """Get detailed ACOS analysis for a campaign."""
    try:
        analysis = await acos_engine.analyze_campaign_acos(campaign_id, period_hours)
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing ACOS for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze ACOS")


# ACOS Alerts
@router.get("/api/acos/alerts", response_model=List[ACOSAlertResponse], tags=["ACOS Alerts"])
async def list_acos_alerts(
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[ACOSAlertResponse]:
    """List ACOS alerts."""
    try:
        query = db.query(ACOSAlert).order_by(ACOSAlert.created_at.desc())
        
        if campaign_id:
            query = query.filter(ACOSAlert.campaign_id == campaign_id)
        
        if severity:
            query = query.filter(ACOSAlert.severity == severity)
        
        if is_resolved is not None:
            query = query.filter(ACOSAlert.is_resolved == is_resolved)
        
        alerts = query.offset(skip).limit(limit).all()
        
        return [ACOSAlertResponse.from_orm(alert) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error listing ACOS alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to list ACOS alerts")


@router.post("/api/acos/alerts/{alert_id}/resolve", tags=["ACOS Alerts"])
async def resolve_acos_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resolve an ACOS alert."""
    try:
        alert = db.query(ACOSAlert).filter(ACOSAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="ACOS alert not found")
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_user["username"]
        
        db.commit()
        
        logger.info(f"ACOS alert resolved: {alert_id}", extra={"user": current_user["username"]})
        
        return {"message": "ACOS alert resolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error resolving ACOS alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve ACOS alert")


# ACOS Automation
@router.post("/api/acos/automation/evaluate", tags=["ACOS Automation"])
async def evaluate_acos_rules(
    background_tasks: BackgroundTasks,
    acos_engine: ACOSAutomationEngine = Depends(get_acos_engine),
    current_user = Depends(get_current_user)
):
    """Trigger ACOS rules evaluation."""
    try:
        # Run evaluation in background
        background_tasks.add_task(acos_engine.evaluate_all_rules)
        
        logger.info("ACOS rules evaluation triggered", extra={"user": current_user["username"]})
        
        return {"message": "ACOS rules evaluation started"}
        
    except Exception as e:
        logger.error(f"Error triggering ACOS evaluation: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger ACOS evaluation")


@router.get("/api/acos/automation/status", tags=["ACOS Automation"])
async def get_automation_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get ACOS automation status and recent activity."""
    try:
        # Get recent rule executions
        recent_executions = db.query(ACOSRuleExecution).order_by(
            ACOSRuleExecution.executed_at.desc()
        ).limit(10).all()
        
        # Get unresolved alerts count
        unresolved_alerts = db.query(ACOSAlert).filter(
            ACOSAlert.is_resolved == False
        ).count()
        
        # Get active rules count
        active_rules = db.query(ACOSRule).filter(ACOSRule.is_active == True).count()
        
        return {
            "active_rules": active_rules,
            "unresolved_alerts": unresolved_alerts,
            "recent_executions": [
                {
                    "rule_id": ex.rule_id,
                    "campaign_id": ex.campaign_id,
                    "action": ex.action_taken,
                    "status": ex.status,
                    "executed_at": ex.executed_at,
                    "acos": ex.triggered_acos
                }
                for ex in recent_executions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting automation status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get automation status")


# Health Check
@router.get("/api/acos/health", tags=["Health"])
async def health_check():
    """ACOS service health check."""
    return {
        "status": "healthy",
        "service": "ACOS Service",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }