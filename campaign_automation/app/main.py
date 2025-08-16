from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import asyncio
import httpx
import pandas as pd
import numpy as np
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('logs/campaign_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create directories
Path("logs").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

# Initialize scheduler
scheduler = AsyncIOScheduler()

app = FastAPI(
    title="Automação de Campanhas - Mercado Livre AI",
    description="""
    Sistema avançado de automação de campanhas publicitárias para Mercado Livre com IA.
    
    ## Funcionalidades Principais
    
    * **Ativação/Pausa Inteligente** - Baseado em métricas ACOS, TACOS e margem mínima
    * **Otimização Temporal** - Análise de períodos de conversão (15 dias)
    * **Monitoramento de Concorrência** - Top 20 anúncios patrocinados
    * **Previsão de ACOS** - Predição antes da ativação de campanhas
    * **Validação de Usuário** - Aprovação manual de ações sugeridas
    * **Dashboard Completo** - Métricas e comparativos em tempo real
    * **Aprendizado Contínuo** - Melhoria automática das estratégias
    
    ## Recursos Adicionais
    
    * **Calendário Interativo** - Configuração visual de horários
    * **Integração com Descontos** - Sistema automático ao pausar campanhas
    * **Otimização de Keywords** - Baseada na análise de concorrência
    * **Sistema de Feedback** - Melhoria contínua das sugestões
    * **Monitoramento 24/7** - Logging completo de todas as ações
    """,
    version="1.0.0",
    contact={
        "name": "ML Project - Campaign Automation Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Campaigns",
            "description": "Gestão de campanhas e automação"
        },
        {
            "name": "Monitoring",
            "description": "Monitoramento de métricas e concorrência"
        },
        {
            "name": "Optimization",
            "description": "Otimização temporal e de palavras-chave"
        },
        {
            "name": "Predictions",
            "description": "Previsões de ACOS e performance"
        },
        {
            "name": "Approvals",
            "description": "Sistema de aprovação de ações"
        },
        {
            "name": "Dashboard",
            "description": "Dashboard e visualizações"
        },
        {
            "name": "Calendar",
            "description": "Calendário interativo"
        },
        {
            "name": "Health",
            "description": "Health checks e monitoramento"
        }
    ]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enums for campaign automation
class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    PENDING_APPROVAL = "pending_approval"
    SCHEDULED = "scheduled"

class ActionType(str, Enum):
    ACTIVATE = "activate"
    PAUSE = "pause"
    ADJUST_BID = "adjust_bid"
    OPTIMIZE_KEYWORDS = "optimize_keywords"
    SCHEDULE_CHANGE = "schedule_change"

class MetricType(str, Enum):
    ACOS = "acos"
    TACOS = "tacos"
    MARGIN = "margin"
    CPC = "cpc"
    CTR = "ctr"
    CONVERSION_RATE = "conversion_rate"

# Data Models
class CampaignRule(BaseModel):
    """Rules for campaign automation"""
    rule_id: str = Field(..., description="Unique rule identifier")
    campaign_id: str = Field(..., description="Campaign ID")
    metric_type: MetricType = Field(..., description="Metric to monitor")
    threshold_value: float = Field(..., description="Threshold value for action")
    action_type: ActionType = Field(..., description="Action to take when threshold is met")
    is_active: bool = Field(default=True, description="Whether rule is active")
    created_at: datetime = Field(default_factory=datetime.now)

class CampaignSchedule(BaseModel):
    """Schedule configuration for campaigns"""
    schedule_id: str = Field(..., description="Unique schedule identifier")
    campaign_id: str = Field(..., description="Campaign ID")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    start_hour: int = Field(..., ge=0, le=23, description="Start hour")
    end_hour: int = Field(..., ge=0, le=23, description="End hour")
    is_active: bool = Field(default=True, description="Whether schedule is active")

class CompetitorAd(BaseModel):
    """Competitor advertisement data"""
    ad_id: str = Field(..., description="Advertisement ID")
    product_name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    position: int = Field(..., description="Position in search results")
    keywords: List[str] = Field(..., description="Associated keywords")
    acos_estimate: Optional[float] = Field(None, description="Estimated ACOS")

class CampaignMetrics(BaseModel):
    """Campaign performance metrics"""
    campaign_id: str = Field(..., description="Campaign ID")
    acos: float = Field(..., description="Advertising Cost of Sales")
    tacos: float = Field(..., description="Total Advertising Cost of Sales")
    margin: float = Field(..., description="Profit margin percentage")
    cpc: float = Field(..., description="Cost per click")
    ctr: float = Field(..., description="Click-through rate")
    conversion_rate: float = Field(..., description="Conversion rate")
    impressions: int = Field(..., description="Number of impressions")
    clicks: int = Field(..., description="Number of clicks")
    conversions: int = Field(..., description="Number of conversions")
    spend: float = Field(..., description="Total spend")
    revenue: float = Field(..., description="Total revenue")
    timestamp: datetime = Field(default_factory=datetime.now)

class AutomationAction(BaseModel):
    """Automation action for approval"""
    action_id: str = Field(..., description="Unique action identifier")
    campaign_id: str = Field(..., description="Campaign ID")
    action_type: ActionType = Field(..., description="Type of action")
    reason: str = Field(..., description="Reason for the action")
    suggested_values: Dict[str, Any] = Field(..., description="Suggested parameter changes")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the suggestion")
    requires_approval: bool = Field(default=True, description="Whether action requires user approval")
    status: str = Field(default="pending", description="Action status")
    created_at: datetime = Field(default_factory=datetime.now)

class ACOSPrediction(BaseModel):
    """ACOS prediction before campaign activation"""
    prediction_id: str = Field(..., description="Unique prediction identifier")
    campaign_id: str = Field(..., description="Campaign ID")
    predicted_acos: float = Field(..., description="Predicted ACOS value")
    confidence_interval: Dict[str, float] = Field(..., description="Confidence interval (min/max)")
    factors: List[str] = Field(..., description="Key factors influencing prediction")
    recommendation: str = Field(..., description="Recommendation based on prediction")

# In-memory storage (in production, use database)
campaigns_data: Dict[str, Dict] = {}
automation_rules: Dict[str, CampaignRule] = {}
campaign_schedules: Dict[str, List[CampaignSchedule]] = {}
competitor_data: Dict[str, List[CompetitorAd]] = {}
metrics_history: Dict[str, List[CampaignMetrics]] = {}
pending_actions: Dict[str, AutomationAction] = {}
acos_predictions: Dict[str, ACOSPrediction] = {}

# Service URLs (in production, use service discovery)
SIMULATOR_SERVICE_URL = "http://simulator_service:8001"
LEARNING_SERVICE_URL = "http://learning_service:8002"
OPTIMIZER_SERVICE_URL = "http://optimizer_ai:8003"

async def call_service(url: str, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Helper function to call other services"""
    try:
        async with httpx.AsyncClient() as client:
            full_url = f"{url}{endpoint}"
            if method == "GET":
                response = await client.get(full_url)
            elif method == "POST":
                response = await client.post(full_url, json=data)
            elif method == "PUT":
                response = await client.put(full_url, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Service call failed: {full_url} - {response.status_code}")
                return {}
    except Exception as e:
        logger.error(f"Error calling service {url}{endpoint}: {e}")
        return {}

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Campaign Automation Service...")
    
    # Start the scheduler
    scheduler.start()
    
    # Schedule monitoring tasks
    scheduler.add_job(
        monitor_campaigns,
        IntervalTrigger(minutes=15),
        id="campaign_monitor",
        name="Monitor Campaign Metrics"
    )
    
    scheduler.add_job(
        analyze_competitor_ads,
        IntervalTrigger(hours=2),
        id="competitor_analysis",
        name="Analyze Competitor Advertisements"
    )
    
    scheduler.add_job(
        optimize_time_based_campaigns,
        CronTrigger(hour=0, minute=0),  # Daily at midnight
        id="time_optimization",
        name="Time-based Campaign Optimization"
    )
    
    logger.info("Campaign Automation Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Campaign Automation Service...")
    scheduler.shutdown()

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "campaign_automation",
        "timestamp": datetime.now().isoformat(),
        "scheduler_running": scheduler.running,
        "active_rules": len(automation_rules),
        "pending_actions": len(pending_actions)
    }

# Campaign management endpoints
@app.get("/api/campaigns", tags=["Campaigns"])
async def get_campaigns():
    """Get all campaigns with their current status"""
    return {
        "campaigns": campaigns_data,
        "total": len(campaigns_data)
    }

@app.get("/api/campaigns/{campaign_id}", tags=["Campaigns"])
async def get_campaign(campaign_id: str):
    """Get specific campaign details"""
    if campaign_id not in campaigns_data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_data[campaign_id]
    
    # Get latest metrics
    latest_metrics = None
    if campaign_id in metrics_history and metrics_history[campaign_id]:
        latest_metrics = metrics_history[campaign_id][-1]
    
    # Get active rules
    active_rules = [rule for rule in automation_rules.values() 
                    if rule.campaign_id == campaign_id and rule.is_active]
    
    # Get schedules
    schedules = campaign_schedules.get(campaign_id, [])
    
    return {
        "campaign": campaign,
        "latest_metrics": latest_metrics,
        "active_rules": active_rules,
        "schedules": schedules
    }

@app.post("/api/campaigns/{campaign_id}/rules", tags=["Campaigns"])
async def create_automation_rule(campaign_id: str, rule: CampaignRule):
    """Create automation rule for a campaign"""
    rule.campaign_id = campaign_id
    automation_rules[rule.rule_id] = rule
    
    logger.info(f"Created automation rule {rule.rule_id} for campaign {campaign_id}")
    
    return {
        "message": "Automation rule created successfully",
        "rule": rule
    }

@app.post("/api/campaigns/{campaign_id}/schedule", tags=["Campaigns"])
async def create_campaign_schedule(campaign_id: str, schedule: CampaignSchedule):
    """Create schedule for a campaign"""
    schedule.campaign_id = campaign_id
    
    if campaign_id not in campaign_schedules:
        campaign_schedules[campaign_id] = []
    
    campaign_schedules[campaign_id].append(schedule)
    
    logger.info(f"Created schedule {schedule.schedule_id} for campaign {campaign_id}")
    
    return {
        "message": "Campaign schedule created successfully",
        "schedule": schedule
    }

# Monitoring and metrics endpoints
@app.get("/api/monitoring/metrics/{campaign_id}", tags=["Monitoring"])
async def get_campaign_metrics(campaign_id: str, days: int = 15):
    """Get campaign metrics for the last N days"""
    if campaign_id not in metrics_history:
        return {"metrics": [], "message": "No metrics found"}
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_metrics = [
        metric for metric in metrics_history[campaign_id]
        if metric.timestamp >= cutoff_date
    ]
    
    return {
        "campaign_id": campaign_id,
        "metrics": recent_metrics,
        "count": len(recent_metrics),
        "period_days": days
    }

@app.get("/api/monitoring/competitors", tags=["Monitoring"])
async def get_competitor_analysis():
    """Get top 20 competitor ads analysis"""
    return {
        "competitors": competitor_data,
        "analysis_timestamp": datetime.now().isoformat(),
        "total_tracked": sum(len(ads) for ads in competitor_data.values())
    }

@app.post("/api/monitoring/update-metrics", tags=["Monitoring"])
async def update_campaign_metrics(metrics: CampaignMetrics):
    """Update campaign metrics (typically called by monitoring systems)"""
    campaign_id = metrics.campaign_id
    
    if campaign_id not in metrics_history:
        metrics_history[campaign_id] = []
    
    metrics_history[campaign_id].append(metrics)
    
    # Keep only last 100 metrics to prevent memory issues
    if len(metrics_history[campaign_id]) > 100:
        metrics_history[campaign_id] = metrics_history[campaign_id][-100:]
    
    # Check automation rules
    await check_automation_rules(campaign_id, metrics)
    
    return {
        "message": "Metrics updated successfully",
        "campaign_id": campaign_id
    }

# Prediction endpoints
@app.get("/api/predictions/acos/{campaign_id}", tags=["Predictions"])
async def predict_acos(campaign_id: str):
    """Predict ACOS for campaign before activation"""
    try:
        # Get historical data for prediction
        historical_metrics = metrics_history.get(campaign_id, [])
        
        if len(historical_metrics) < 5:
            # Use simulator service for prediction
            prediction_data = await call_service(
                SIMULATOR_SERVICE_URL,
                f"/api/predict/acos?campaign_id={campaign_id}"
            )
        else:
            # Use internal ML prediction
            prediction_data = await generate_acos_prediction(campaign_id, historical_metrics)
        
        prediction = ACOSPrediction(
            prediction_id=f"pred_{campaign_id}_{int(datetime.now().timestamp())}",
            campaign_id=campaign_id,
            predicted_acos=prediction_data.get("predicted_acos", 0.25),
            confidence_interval={
                "min": prediction_data.get("min_acos", 0.15),
                "max": prediction_data.get("max_acos", 0.35)
            },
            factors=prediction_data.get("factors", ["Historical performance", "Market conditions", "Keyword competitiveness"]),
            recommendation=prediction_data.get("recommendation", "Proceed with caution - monitor closely")
        )
        
        acos_predictions[prediction.prediction_id] = prediction
        
        return prediction
        
    except Exception as e:
        logger.error(f"Error predicting ACOS for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate ACOS prediction")

# Approval system endpoints
@app.get("/api/approvals/pending", tags=["Approvals"])
async def get_pending_approvals():
    """Get all pending actions requiring approval"""
    pending = [action for action in pending_actions.values() 
               if action.status == "pending" and action.requires_approval]
    
    return {
        "pending_actions": pending,
        "count": len(pending)
    }

@app.post("/api/approvals/{action_id}/approve", tags=["Approvals"])
async def approve_action(action_id: str):
    """Approve a pending automation action"""
    if action_id not in pending_actions:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action = pending_actions[action_id]
    action.status = "approved"
    
    # Execute the approved action
    result = await execute_automation_action(action)
    
    logger.info(f"Action {action_id} approved and executed")
    
    return {
        "message": "Action approved and executed",
        "action": action,
        "execution_result": result
    }

@app.post("/api/approvals/{action_id}/reject", tags=["Approvals"])
async def reject_action(action_id: str, reason: str = ""):
    """Reject a pending automation action"""
    if action_id not in pending_actions:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action = pending_actions[action_id]
    action.status = "rejected"
    
    logger.info(f"Action {action_id} rejected. Reason: {reason}")
    
    return {
        "message": "Action rejected",
        "action": action,
        "reason": reason
    }

# Dashboard endpoints
@app.get("/api/dashboard/overview", tags=["Dashboard"])
async def get_dashboard_overview():
    """Get dashboard overview with key metrics"""
    total_campaigns = len(campaigns_data)
    active_campaigns = sum(1 for c in campaigns_data.values() if c.get("status") == "active")
    total_rules = len(automation_rules)
    pending_approvals = len([a for a in pending_actions.values() if a.status == "pending"])
    
    # Calculate average metrics
    recent_metrics = []
    for campaign_metrics in metrics_history.values():
        if campaign_metrics:
            recent_metrics.extend(campaign_metrics[-5:])  # Last 5 metrics per campaign
    
    avg_acos = np.mean([m.acos for m in recent_metrics]) if recent_metrics else 0
    avg_margin = np.mean([m.margin for m in recent_metrics]) if recent_metrics else 0
    
    return {
        "overview": {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_rules": total_rules,
            "pending_approvals": pending_approvals,
            "avg_acos": round(avg_acos, 3),
            "avg_margin": round(avg_margin, 2),
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard/charts/{campaign_id}", tags=["Dashboard"])
async def get_campaign_charts(campaign_id: str, days: int = 15):
    """Get chart data for campaign dashboard"""
    if campaign_id not in metrics_history:
        raise HTTPException(status_code=404, detail="Campaign metrics not found")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_metrics = [
        metric for metric in metrics_history[campaign_id]
        if metric.timestamp >= cutoff_date
    ]
    
    if not recent_metrics:
        return {"message": "No recent metrics found", "charts": {}}
    
    # Prepare chart data
    dates = [m.timestamp.isoformat() for m in recent_metrics]
    acos_values = [m.acos for m in recent_metrics]
    margin_values = [m.margin for m in recent_metrics]
    spend_values = [m.spend for m in recent_metrics]
    revenue_values = [m.revenue for m in recent_metrics]
    
    # Create performance chart
    performance_chart = {
        "data": [
            {
                "x": dates,
                "y": acos_values,
                "name": "ACOS",
                "type": "scatter",
                "mode": "lines+markers"
            },
            {
                "x": dates,
                "y": margin_values,
                "name": "Margin %",
                "type": "scatter",
                "mode": "lines+markers",
                "yaxis": "y2"
            }
        ],
        "layout": {
            "title": "Campaign Performance",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "ACOS"},
            "yaxis2": {"title": "Margin %", "overlaying": "y", "side": "right"}
        }
    }
    
    # Create financial chart
    financial_chart = {
        "data": [
            {
                "x": dates,
                "y": spend_values,
                "name": "Spend",
                "type": "bar"
            },
            {
                "x": dates,
                "y": revenue_values,
                "name": "Revenue",
                "type": "bar"
            }
        ],
        "layout": {
            "title": "Financial Performance",
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Amount ($)"},
            "barmode": "group"
        }
    }
    
    return {
        "campaign_id": campaign_id,
        "charts": {
            "performance": performance_chart,
            "financial": financial_chart
        },
        "period_days": days
    }

# Calendar endpoints
@app.get("/api/calendar/{campaign_id}", tags=["Calendar"])
async def get_campaign_calendar(campaign_id: str):
    """Get campaign schedule calendar"""
    schedules = campaign_schedules.get(campaign_id, [])
    
    # Convert schedules to calendar format
    calendar_events = []
    for schedule in schedules:
        if schedule.is_active:
            calendar_events.append({
                "id": schedule.schedule_id,
                "title": f"Campaign Active",
                "day": schedule.day_of_week,
                "start_hour": schedule.start_hour,
                "end_hour": schedule.end_hour,
                "color": "green" if schedule.is_active else "gray"
            })
    
    return {
        "campaign_id": campaign_id,
        "events": calendar_events,
        "schedule_count": len(schedules)
    }

@app.post("/api/calendar/{campaign_id}/events", tags=["Calendar"])
async def create_calendar_event(campaign_id: str, event_data: Dict[str, Any]):
    """Create new calendar event for campaign"""
    schedule = CampaignSchedule(
        schedule_id=f"schedule_{campaign_id}_{int(datetime.now().timestamp())}",
        campaign_id=campaign_id,
        day_of_week=event_data["day"],
        start_hour=event_data["start_hour"],
        end_hour=event_data["end_hour"]
    )
    
    if campaign_id not in campaign_schedules:
        campaign_schedules[campaign_id] = []
    
    campaign_schedules[campaign_id].append(schedule)
    
    return {
        "message": "Calendar event created successfully",
        "schedule": schedule
    }

# Background tasks and automation logic
async def monitor_campaigns():
    """Background task to monitor campaign metrics and trigger automations"""
    logger.info("Starting campaign monitoring cycle...")
    
    for campaign_id in campaigns_data.keys():
        try:
            # Get latest metrics from monitoring service
            metrics_data = await call_service(
                SIMULATOR_SERVICE_URL,
                f"/api/metrics/{campaign_id}"
            )
            
            if metrics_data:
                # Update metrics
                metrics = CampaignMetrics(
                    campaign_id=campaign_id,
                    **metrics_data
                )
                
                if campaign_id not in metrics_history:
                    metrics_history[campaign_id] = []
                
                metrics_history[campaign_id].append(metrics)
                
                # Check automation rules
                await check_automation_rules(campaign_id, metrics)
        
        except Exception as e:
            logger.error(f"Error monitoring campaign {campaign_id}: {e}")

async def analyze_competitor_ads():
    """Background task to analyze competitor advertisements"""
    logger.info("Starting competitor analysis...")
    
    try:
        # Call competitor intelligence service
        competitor_analysis = await call_service(
            "http://competitor_intelligence:8006",
            "/api/analyze/top-ads?limit=20"
        )
        
        if competitor_analysis:
            # Process competitor data
            for category, ads in competitor_analysis.items():
                competitor_data[category] = [
                    CompetitorAd(**ad) for ad in ads
                ]
        
        logger.info(f"Analyzed competitors in {len(competitor_data)} categories")
    
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")

async def optimize_time_based_campaigns():
    """Background task for time-based campaign optimization"""
    logger.info("Starting time-based optimization...")
    
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    for campaign_id, schedules in campaign_schedules.items():
        for schedule in schedules:
            if not schedule.is_active:
                continue
            
            should_be_active = (
                schedule.day_of_week == current_day and
                schedule.start_hour <= current_hour <= schedule.end_hour
            )
            
            current_status = campaigns_data.get(campaign_id, {}).get("status", "paused")
            
            if should_be_active and current_status == "paused":
                # Suggest activation
                action = AutomationAction(
                    action_id=f"auto_{campaign_id}_{int(datetime.now().timestamp())}",
                    campaign_id=campaign_id,
                    action_type=ActionType.ACTIVATE,
                    reason=f"Scheduled activation for {schedule.day_of_week} at {current_hour}:00",
                    suggested_values={"status": "active"},
                    confidence_score=0.9,
                    requires_approval=False  # Time-based actions can be automatic
                )
                
                pending_actions[action.action_id] = action
                await execute_automation_action(action)
                
            elif not should_be_active and current_status == "active":
                # Suggest pause
                action = AutomationAction(
                    action_id=f"auto_{campaign_id}_{int(datetime.now().timestamp())}",
                    campaign_id=campaign_id,
                    action_type=ActionType.PAUSE,
                    reason=f"Scheduled pause outside active hours",
                    suggested_values={"status": "paused"},
                    confidence_score=0.9,
                    requires_approval=False
                )
                
                pending_actions[action.action_id] = action
                await execute_automation_action(action)

async def check_automation_rules(campaign_id: str, metrics: CampaignMetrics):
    """Check automation rules against campaign metrics"""
    campaign_rules = [rule for rule in automation_rules.values() 
                     if rule.campaign_id == campaign_id and rule.is_active]
    
    for rule in campaign_rules:
        metric_value = getattr(metrics, rule.metric_type.value, 0)
        
        should_trigger = False
        
        # Check threshold conditions
        if rule.metric_type in [MetricType.ACOS, MetricType.TACOS]:
            # For cost metrics, trigger if above threshold
            should_trigger = metric_value > rule.threshold_value
        elif rule.metric_type == MetricType.MARGIN:
            # For margin, trigger if below threshold
            should_trigger = metric_value < rule.threshold_value
        else:
            # For other metrics, trigger if below threshold
            should_trigger = metric_value < rule.threshold_value
        
        if should_trigger:
            # Create automation action
            action = AutomationAction(
                action_id=f"rule_{rule.rule_id}_{int(datetime.now().timestamp())}",
                campaign_id=campaign_id,
                action_type=rule.action_type,
                reason=f"{rule.metric_type.value.upper()} {metric_value} triggered rule threshold {rule.threshold_value}",
                suggested_values=generate_suggested_values(rule, metrics),
                confidence_score=calculate_confidence_score(rule, metrics),
                requires_approval=True
            )
            
            pending_actions[action.action_id] = action
            
            logger.info(f"Rule {rule.rule_id} triggered action {action.action_id} for campaign {campaign_id}")

def generate_suggested_values(rule: CampaignRule, metrics: CampaignMetrics) -> Dict[str, Any]:
    """Generate suggested parameter changes based on rule and metrics"""
    suggested = {}
    
    if rule.action_type == ActionType.PAUSE:
        suggested["status"] = "paused"
        suggested["reason"] = f"High {rule.metric_type.value}: {getattr(metrics, rule.metric_type.value)}"
    
    elif rule.action_type == ActionType.ACTIVATE:
        suggested["status"] = "active"
        suggested["reason"] = f"Good {rule.metric_type.value}: {getattr(metrics, rule.metric_type.value)}"
    
    elif rule.action_type == ActionType.ADJUST_BID:
        current_cpc = metrics.cpc
        if rule.metric_type == MetricType.ACOS and getattr(metrics, rule.metric_type.value) > rule.threshold_value:
            # Reduce bid if ACOS is too high
            suggested["bid_adjustment"] = -0.1  # Reduce by 10%
        else:
            # Increase bid if performance is good
            suggested["bid_adjustment"] = 0.05  # Increase by 5%
    
    return suggested

def calculate_confidence_score(rule: CampaignRule, metrics: CampaignMetrics) -> float:
    """Calculate confidence score for automation action"""
    base_confidence = 0.7
    
    # Increase confidence based on how far from threshold
    metric_value = getattr(metrics, rule.metric_type.value, 0)
    threshold_distance = abs(metric_value - rule.threshold_value) / rule.threshold_value
    
    confidence = min(base_confidence + (threshold_distance * 0.2), 0.95)
    
    return round(confidence, 3)

async def execute_automation_action(action: AutomationAction) -> Dict[str, Any]:
    """Execute an approved automation action"""
    try:
        campaign_id = action.campaign_id
        
        if action.action_type == ActionType.ACTIVATE:
            campaigns_data[campaign_id]["status"] = "active"
            
        elif action.action_type == ActionType.PAUSE:
            campaigns_data[campaign_id]["status"] = "paused"
            
            # Integrate with discount system
            await call_service(
                "http://backend:8000",
                f"/api/campaigns/{campaign_id}/apply-discount",
                "POST",
                {"discount_percentage": 5}  # Apply 5% discount when pausing
            )
        
        elif action.action_type == ActionType.ADJUST_BID:
            bid_adjustment = action.suggested_values.get("bid_adjustment", 0)
            # Call Mercado Livre API to adjust bid
            await call_service(
                "http://backend:8000",
                f"/api/campaigns/{campaign_id}/adjust-bid",
                "POST",
                {"adjustment": bid_adjustment}
            )
        
        action.status = "executed"
        
        logger.info(f"Executed action {action.action_id} for campaign {campaign_id}")
        
        return {"success": True, "message": "Action executed successfully"}
    
    except Exception as e:
        action.status = "failed"
        logger.error(f"Failed to execute action {action.action_id}: {e}")
        return {"success": False, "error": str(e)}

async def generate_acos_prediction(campaign_id: str, historical_metrics: List[CampaignMetrics]) -> Dict[str, Any]:
    """Generate ACOS prediction using internal ML"""
    try:
        # Simple prediction based on historical trends
        recent_acos = [m.acos for m in historical_metrics[-10:]]  # Last 10 metrics
        
        if len(recent_acos) < 3:
            return {
                "predicted_acos": 0.25,
                "min_acos": 0.15,
                "max_acos": 0.35,
                "factors": ["Insufficient historical data"],
                "recommendation": "Start with conservative settings"
            }
        
        # Calculate trend
        trend = np.polyfit(range(len(recent_acos)), recent_acos, 1)[0]
        avg_acos = np.mean(recent_acos)
        
        # Predict next period ACOS
        predicted_acos = avg_acos + trend
        
        # Calculate confidence interval
        std_dev = np.std(recent_acos)
        min_acos = max(0.05, predicted_acos - (1.96 * std_dev))
        max_acos = predicted_acos + (1.96 * std_dev)
        
        # Generate factors
        factors = ["Historical performance trend"]
        if trend > 0.01:
            factors.append("Increasing ACOS trend")
        elif trend < -0.01:
            factors.append("Decreasing ACOS trend")
        else:
            factors.append("Stable ACOS trend")
        
        # Generate recommendation
        if predicted_acos < 0.2:
            recommendation = "Good performance expected - proceed with confidence"
        elif predicted_acos < 0.3:
            recommendation = "Moderate performance expected - monitor closely"
        else:
            recommendation = "High ACOS predicted - consider optimization before activation"
        
        return {
            "predicted_acos": round(predicted_acos, 3),
            "min_acos": round(min_acos, 3),
            "max_acos": round(max_acos, 3),
            "factors": factors,
            "recommendation": recommendation
        }
    
    except Exception as e:
        logger.error(f"Error generating ACOS prediction: {e}")
        return {
            "predicted_acos": 0.25,
            "min_acos": 0.15,
            "max_acos": 0.35,
            "factors": ["Prediction error"],
            "recommendation": "Unable to predict - proceed with caution"
        }

# Initialize some sample data for demonstration
@app.on_event("startup")
async def initialize_sample_data():
    """Initialize sample data for demonstration"""
    # Sample campaigns
    campaigns_data["CAMP_001"] = {
        "id": "CAMP_001",
        "name": "Smartphone Samsung Galaxy",
        "status": "active",
        "budget": 1000.0,
        "created_at": datetime.now().isoformat()
    }
    
    campaigns_data["CAMP_002"] = {
        "id": "CAMP_002", 
        "name": "Notebook Dell Inspiron",
        "status": "paused",
        "budget": 1500.0,
        "created_at": datetime.now().isoformat()
    }
    
    # Sample automation rules
    rule1 = CampaignRule(
        rule_id="RULE_001",
        campaign_id="CAMP_001",
        metric_type=MetricType.ACOS,
        threshold_value=0.25,
        action_type=ActionType.PAUSE
    )
    automation_rules[rule1.rule_id] = rule1
    
    rule2 = CampaignRule(
        rule_id="RULE_002",
        campaign_id="CAMP_002",
        metric_type=MetricType.MARGIN,
        threshold_value=15.0,
        action_type=ActionType.ACTIVATE
    )
    automation_rules[rule2.rule_id] = rule2
    
    # Sample metrics
    sample_metrics = CampaignMetrics(
        campaign_id="CAMP_001",
        acos=0.22,
        tacos=0.18,
        margin=20.5,
        cpc=1.50,
        ctr=0.045,
        conversion_rate=0.032,
        impressions=10000,
        clicks=450,
        conversions=15,
        spend=675.0,
        revenue=3000.0
    )
    
    metrics_history["CAMP_001"] = [sample_metrics]
    
    logger.info("Sample data initialized successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)