from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import io
import csv
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('learning_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Initialize scheduler
scheduler = AsyncIOScheduler()

app = FastAPI(
    title="Aprendizado Contínuo - Mercado Livre AI",
    description="""
    Sistema avançado de aprendizado contínuo para otimização de campanhas no Mercado Livre.
    
    ## Funcionalidades Avançadas
    
    * **Aprendizado Automático** - Ajustes programados baseados em performance
    * **Notificações Inteligentes** - Alertas automáticos por email e webhook
    * **Auditoria Completa** - Log detalhado de todas as operações e versões
    * **Analytics Preditivo** - Dashboards comparativos com ML
    * **Agendamento Automático** - Retreinamento periódico dos modelos
    * **Detecção de Anomalias** - Identificação automática de padrões inválidos
    
    ## Métricas de Aprendizado
    
    * Precisão de Predições (Click, Conversion, Revenue)
    * Evolução da Performance ao Longo do Tempo
    * Comparação entre Versões de Modelos
    * Análise de Drift de Dados
    * ROI de Otimizações
    """,
    version="2.0.0",
    contact={
        "name": "ML Project - Learning Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Model Updates",
            "description": "Atualização e retreinamento de modelos"
        },
        {
            "name": "Scheduling",
            "description": "Agendamento automático de tarefas"
        },
        {
            "name": "Notifications",
            "description": "Sistema de notificações e alertas"
        },
        {
            "name": "Analytics",
            "description": "Analytics e visualizações comparativas"
        },
        {
            "name": "Audit",
            "description": "Auditoria e versionamento"
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

# In-memory storage for demo purposes (in production, use database)
model_updates = []
learning_history = []
model_versions = {}
scheduled_tasks = {}
notification_config = {
    "email_enabled": True,
    "email_recipients": ["admin@mlproject.com"],
    "webhook_url": None,
    "error_threshold": 0.7  # Trigger alerts when accuracy < 70%
}
audit_log = []

class ModelUpdateRequest(BaseModel):
    campaign_id: str
    actual_clicks: int
    actual_conversions: int
    actual_revenue: float
    predicted_clicks: int
    predicted_conversions: int
    predicted_revenue: float
    notes: str = ""
    model_version: str = "v1.0"

class ModelUpdateResponse(BaseModel):
    update_id: str
    status: str
    accuracy_metrics: Dict[str, float]
    improvement_suggestions: List[str]
    timestamp: str
    model_version: str
    anomaly_detected: bool = False

class ScheduleRequest(BaseModel):
    schedule_name: str
    cron_expression: str  # e.g., "0 2 * * *" for daily at 2 AM
    enabled: bool = True
    target_accuracy_threshold: float = 0.8
    notification_on_completion: bool = True

class NotificationRequest(BaseModel):
    type: str = "email"  # email, webhook, slack
    recipients: List[str]
    subject: str
    message: str
    priority: str = "normal"  # low, normal, high, critical

class ModelVersionInfo(BaseModel):
    version: str
    created_at: str
    accuracy_metrics: Dict[str, float]
    training_data_size: int
    notes: str = ""
    is_active: bool = False

class AuditLogEntry(BaseModel):
    timestamp: str
    action: str
    user: str = "system"
    details: Dict[str, Any]
    model_version: str
    success: bool = True

# Utility Functions
async def log_audit_entry(action: str, details: Dict[str, Any], model_version: str = "v1.0", user: str = "system", success: bool = True):
    """Log audit entry for all system actions"""
    entry = AuditLogEntry(
        timestamp=datetime.now().isoformat(),
        action=action,
        user=user,
        details=details,
        model_version=model_version,
        success=success
    )
    audit_log.append(entry.dict())
    logger.info(f"AUDIT: {action} - {details} - Success: {success}")

async def send_notification(notification: NotificationRequest):
    """Send notifications via email or webhook"""
    try:
        if notification.type == "email" and notification_config["email_enabled"]:
            # Simple email notification (in production, use proper email service)
            logger.info(f"EMAIL NOTIFICATION: {notification.subject} to {notification.recipients}")
            await log_audit_entry(
                action="notification_sent",
                details={"type": "email", "recipients": notification.recipients, "subject": notification.subject},
                success=True
            )
        elif notification.type == "webhook" and notification_config["webhook_url"]:
            # Webhook notification (implement actual HTTP call in production)
            logger.info(f"WEBHOOK NOTIFICATION: {notification.message}")
            await log_audit_entry(
                action="notification_sent", 
                details={"type": "webhook", "message": notification.message},
                success=True
            )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        await log_audit_entry(
            action="notification_failed",
            details={"error": str(e), "notification": notification.dict()},
            success=False
        )

def detect_anomalies(actual_metrics: Dict[str, float], predicted_metrics: Dict[str, float], threshold: float = 0.3) -> bool:
    """Detect anomalies in prediction accuracy"""
    try:
        for metric in actual_metrics:
            if metric in predicted_metrics:
                actual_val = actual_metrics[metric]
                predicted_val = predicted_metrics[metric]
                if predicted_val > 0:
                    deviation = abs(actual_val - predicted_val) / predicted_val
                    if deviation > threshold:
                        logger.warning(f"Anomaly detected in {metric}: {deviation:.2%} deviation")
                        return True
        return False
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return False

async def auto_retrain_model():
    """Automatically retrain model based on recent performance"""
    try:
        logger.info("Starting automatic model retraining...")
        
        # Analyze recent updates for retraining decision
        recent_updates = model_updates[-50:] if len(model_updates) >= 50 else model_updates
        
        if not recent_updates:
            logger.info("No recent updates available for retraining")
            return
        
        # Calculate average accuracy
        avg_accuracy = sum(u["accuracy_metrics"]["overall_accuracy"] for u in recent_updates) / len(recent_updates)
        
        # Create new model version if accuracy is good
        if avg_accuracy > 0.8:
            new_version = f"v{len(model_versions) + 1}.0"
            model_versions[new_version] = ModelVersionInfo(
                version=new_version,
                created_at=datetime.now().isoformat(),
                accuracy_metrics={"overall_accuracy": avg_accuracy},
                training_data_size=len(recent_updates),
                notes=f"Auto-retrained with {len(recent_updates)} samples",
                is_active=True
            ).dict()
            
            # Deactivate old versions
            for version in model_versions:
                if version != new_version:
                    model_versions[version]["is_active"] = False
            
            await log_audit_entry(
                action="model_retrained",
                details={"new_version": new_version, "accuracy": avg_accuracy, "samples": len(recent_updates)},
                model_version=new_version
            )
            
            # Send notification
            await send_notification(NotificationRequest(
                type="email",
                recipients=notification_config["email_recipients"],
                subject="Model Retrained Successfully",
                message=f"New model version {new_version} trained with {avg_accuracy:.1%} accuracy"
            ))
            
        else:
            logger.warning(f"Model accuracy too low for retraining: {avg_accuracy:.1%}")
            
    except Exception as e:
        logger.error(f"Error in auto retraining: {e}")
        await log_audit_entry(
            action="model_retrain_failed",
            details={"error": str(e)},
            success=False
        )

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler and default tasks"""
    scheduler.start()
    
    # Add default retraining schedule (daily at 2 AM)
    scheduler.add_job(
        func=auto_retrain_model,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_retrain",
        name="Daily Model Retraining",
        replace_existing=True
    )
    
    logger.info("Learning service started with automatic scheduling")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    logger.info("Learning service stopped")

class ModelUpdateResponse(BaseModel):
    update_id: str
    status: str
    accuracy_metrics: Dict[str, float]
    improvement_suggestions: List[str]
    timestamp: str
    model_version: str
    anomaly_detected: bool = False

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    with open("static/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "learning_service"}

@app.post("/api/update-model", response_model=ModelUpdateResponse, tags=["Model Updates"])
async def update_model(request: ModelUpdateRequest) -> ModelUpdateResponse:
    """
    Update the model with actual campaign results for continuous learning with advanced features
    """
    logger.info(f"Updating model v{request.model_version} with results from campaign: {request.campaign_id}")
    
    # Generate update ID
    update_id = f"UPD_{len(model_updates) + 1:06d}"
    
    # Calculate accuracy metrics
    click_accuracy = 1 - abs(request.actual_clicks - request.predicted_clicks) / max(request.predicted_clicks, 1)
    conversion_accuracy = 1 - abs(request.actual_conversions - request.predicted_conversions) / max(request.predicted_conversions, 1)
    revenue_accuracy = 1 - abs(request.actual_revenue - request.predicted_revenue) / max(request.predicted_revenue, 1)
    
    # Ensure accuracy is between 0 and 1
    click_accuracy = max(0, min(1, click_accuracy))
    conversion_accuracy = max(0, min(1, conversion_accuracy))
    revenue_accuracy = max(0, min(1, revenue_accuracy))
    
    overall_accuracy = (click_accuracy + conversion_accuracy + revenue_accuracy) / 3
    
    # Detect anomalies
    actual_metrics = {"clicks": request.actual_clicks, "conversions": request.actual_conversions, "revenue": request.actual_revenue}
    predicted_metrics = {"clicks": request.predicted_clicks, "conversions": request.predicted_conversions, "revenue": request.predicted_revenue}
    anomaly_detected = detect_anomalies(actual_metrics, predicted_metrics)
    
    # Generate improvement suggestions based on accuracy
    suggestions = []
    if click_accuracy < 0.8:
        suggestions.append("Improve click prediction models - consider seasonality factors")
    if conversion_accuracy < 0.8:
        suggestions.append("Enhance conversion rate modeling - analyze user behavior patterns")
    if revenue_accuracy < 0.8:
        suggestions.append("Refine revenue forecasting - incorporate market trends")
    if overall_accuracy > 0.9:
        suggestions.append("Excellent prediction accuracy - maintain current model parameters")
    if anomaly_detected:
        suggestions.append("Anomaly detected - investigate data quality and model drift")
    
    # Store the update with enhanced metadata
    update_record = {
        "update_id": update_id,
        "campaign_id": request.campaign_id,
        "timestamp": datetime.now().isoformat(),
        "model_version": request.model_version,
        "actual_metrics": actual_metrics,
        "predicted_metrics": predicted_metrics,
        "accuracy_metrics": {
            "click_accuracy": round(click_accuracy, 3),
            "conversion_accuracy": round(conversion_accuracy, 3),
            "revenue_accuracy": round(revenue_accuracy, 3),
            "overall_accuracy": round(overall_accuracy, 3)
        },
        "anomaly_detected": anomaly_detected,
        "notes": request.notes,
        "improvement_suggestions": suggestions
    }
    
    model_updates.append(update_record)
    learning_history.append({
        "timestamp": datetime.now().isoformat(),
        "accuracy": overall_accuracy,
        "campaign_id": request.campaign_id,
        "model_version": request.model_version,
        "anomaly_detected": anomaly_detected
    })
    
    # Log audit entry
    await log_audit_entry(
        action="model_updated",
        details={
            "campaign_id": request.campaign_id,
            "accuracy": overall_accuracy,
            "anomaly_detected": anomaly_detected
        },
        model_version=request.model_version
    )
    
    # Send notification if accuracy is low or anomaly detected
    if overall_accuracy < notification_config["error_threshold"] or anomaly_detected:
        await send_notification(NotificationRequest(
            type="email",
            recipients=notification_config["email_recipients"],
            subject=f"Model Performance Alert - {request.campaign_id}",
            message=f"Low accuracy detected: {overall_accuracy:.1%}. Anomaly: {anomaly_detected}",
            priority="high" if anomaly_detected else "normal"
        ))
    
    return ModelUpdateResponse(
        update_id=update_id,
        status="success",
        accuracy_metrics={
            "click_accuracy": round(click_accuracy, 3),
            "conversion_accuracy": round(conversion_accuracy, 3),
            "revenue_accuracy": round(revenue_accuracy, 3),
            "overall_accuracy": round(overall_accuracy, 3)
        },
        improvement_suggestions=suggestions,
        timestamp=datetime.now().isoformat(),
        model_version=request.model_version,
        anomaly_detected=anomaly_detected
    )

@app.post("/api/upload-results")
async def upload_results(file: UploadFile = File(...)):
    """
    Upload campaign results from CSV file for batch model updates
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    content = await file.read()
    csv_content = io.StringIO(content.decode('utf-8'))
    
    try:
        csv_reader = csv.DictReader(csv_content)
        updates_processed = 0
        
        for row in csv_reader:
            # Process each row as a model update
            request = ModelUpdateRequest(
                campaign_id=row.get('campaign_id', ''),
                actual_clicks=int(row.get('actual_clicks', 0)),
                actual_conversions=int(row.get('actual_conversions', 0)),
                actual_revenue=float(row.get('actual_revenue', 0)),
                predicted_clicks=int(row.get('predicted_clicks', 0)),
                predicted_conversions=int(row.get('predicted_conversions', 0)),
                predicted_revenue=float(row.get('predicted_revenue', 0)),
                notes=row.get('notes', '')
            )
            
            # Update model with this data
            await update_model(request)
            updates_processed += 1
        
        return {
            "status": "success",
            "message": f"Processed {updates_processed} campaign updates",
            "updates_processed": updates_processed
        }
    
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")

@app.get("/api/learning-history")
async def get_learning_history():
    """Get the learning history for visualization"""
    return {
        "history": learning_history[-50:],  # Return last 50 entries
        "total_updates": len(model_updates),
        "average_accuracy": sum(h["accuracy"] for h in learning_history) / max(len(learning_history), 1)
    }

@app.get("/api/model-performance")
async def get_model_performance():
    """Get current model performance metrics"""
    if not model_updates:
        return {"message": "No model updates available yet"}
    
    recent_updates = model_updates[-10:]  # Last 10 updates
    
    avg_metrics = {
        "click_accuracy": sum(u["accuracy_metrics"]["click_accuracy"] for u in recent_updates) / len(recent_updates),
        "conversion_accuracy": sum(u["accuracy_metrics"]["conversion_accuracy"] for u in recent_updates) / len(recent_updates),
        "revenue_accuracy": sum(u["accuracy_metrics"]["revenue_accuracy"] for u in recent_updates) / len(recent_updates),
        "overall_accuracy": sum(u["accuracy_metrics"]["overall_accuracy"] for u in recent_updates) / len(recent_updates)
    }
    
    return {
        "current_performance": avg_metrics,
        "total_campaigns_analyzed": len(model_updates),
        "last_update": model_updates[-1]["timestamp"] if model_updates else None
    }

@app.post("/api/schedule/create", tags=["Scheduling"])
async def create_schedule(request: ScheduleRequest):
    """
    Create automated schedule for model retraining
    """
    try:
        # Add scheduled job
        scheduler.add_job(
            func=auto_retrain_model,
            trigger=CronTrigger.from_crontab(request.cron_expression),
            id=f"schedule_{request.schedule_name}",
            name=request.schedule_name,
            replace_existing=True
        )
        
        # Store schedule info
        scheduled_tasks[request.schedule_name] = {
            "cron_expression": request.cron_expression,
            "enabled": request.enabled,
            "target_accuracy_threshold": request.target_accuracy_threshold,
            "notification_on_completion": request.notification_on_completion,
            "created_at": datetime.now().isoformat()
        }
        
        await log_audit_entry(
            action="schedule_created",
            details={"schedule_name": request.schedule_name, "cron": request.cron_expression}
        )
        
        return {
            "status": "success",
            "message": f"Schedule '{request.schedule_name}' created successfully",
            "next_run": "calculated_by_scheduler"
        }
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid cron expression: {str(e)}")

@app.get("/api/schedule/list", tags=["Scheduling"])
async def list_schedules():
    """
    List all active schedules
    """
    scheduler_jobs = []
    for job in scheduler.get_jobs():
        scheduler_jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "active_jobs": scheduler_jobs,
        "stored_tasks": scheduled_tasks
    }

@app.delete("/api/schedule/{schedule_name}", tags=["Scheduling"])
async def delete_schedule(schedule_name: str):
    """
    Delete a scheduled task
    """
    try:
        scheduler.remove_job(f"schedule_{schedule_name}")
        if schedule_name in scheduled_tasks:
            del scheduled_tasks[schedule_name]
        
        await log_audit_entry(
            action="schedule_deleted",
            details={"schedule_name": schedule_name}
        )
        
        return {"status": "success", "message": f"Schedule '{schedule_name}' deleted"}
    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        raise HTTPException(status_code=404, detail="Schedule not found")

@app.post("/api/notifications/send", tags=["Notifications"])
async def send_manual_notification(notification: NotificationRequest):
    """
    Send manual notification
    """
    await send_notification(notification)
    return {"status": "success", "message": "Notification sent"}

@app.get("/api/notifications/config", tags=["Notifications"])
async def get_notification_config():
    """
    Get current notification configuration
    """
    return notification_config

@app.put("/api/notifications/config", tags=["Notifications"])
async def update_notification_config(config: dict):
    """
    Update notification configuration
    """
    global notification_config
    notification_config.update(config)
    
    await log_audit_entry(
        action="notification_config_updated",
        details=config
    )
    
    return {"status": "success", "config": notification_config}

@app.get("/api/analytics/comparative", tags=["Analytics"])
async def get_comparative_analytics():
    """
    Get comparative analytics with charts data
    """
    if not model_updates:
        return {"message": "No data available for analytics"}
    
    # Prepare data for charts
    df = pd.DataFrame([{
        "timestamp": u["timestamp"],
        "overall_accuracy": u["accuracy_metrics"]["overall_accuracy"],
        "click_accuracy": u["accuracy_metrics"]["click_accuracy"],
        "conversion_accuracy": u["accuracy_metrics"]["conversion_accuracy"],
        "revenue_accuracy": u["accuracy_metrics"]["revenue_accuracy"],
        "model_version": u.get("model_version", "v1.0"),
        "campaign_id": u["campaign_id"]
    } for u in model_updates])
    
    # Create time series data
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    daily_accuracy = df.groupby("date")["overall_accuracy"].mean().reset_index()
    
    # Model version comparison
    version_accuracy = df.groupby("model_version")["overall_accuracy"].agg(["mean", "count"]).reset_index()
    
    return {
        "time_series": {
            "dates": [str(d) for d in daily_accuracy["date"]],
            "accuracy": daily_accuracy["overall_accuracy"].tolist()
        },
        "model_versions": {
            "versions": version_accuracy["model_version"].tolist(),
            "avg_accuracy": version_accuracy["mean"].tolist(),
            "sample_count": version_accuracy["count"].tolist()
        },
        "recent_performance": {
            "last_30_days_avg": df.tail(30)["overall_accuracy"].mean() if len(df) >= 30 else df["overall_accuracy"].mean(),
            "best_performing_version": version_accuracy.loc[version_accuracy["mean"].idxmax(), "model_version"] if not version_accuracy.empty else "N/A",
            "total_updates": len(model_updates),
            "anomalies_detected": sum(1 for u in model_updates if u.get("anomaly_detected", False))
        }
    }

@app.get("/api/audit/log", tags=["Audit"])
async def get_audit_log(limit: int = 100, action_filter: Optional[str] = None):
    """
    Get audit log entries with optional filtering
    """
    filtered_log = audit_log
    
    if action_filter:
        filtered_log = [entry for entry in audit_log if entry["action"] == action_filter]
    
    return {
        "entries": filtered_log[-limit:],
        "total_entries": len(audit_log),
        "filtered_entries": len(filtered_log)
    }

@app.get("/api/models/versions", tags=["Audit"])
async def get_model_versions():
    """
    Get all model versions and their information
    """
    return {
        "versions": model_versions,
        "active_version": next((v for v, info in model_versions.items() if info["is_active"]), None),
        "total_versions": len(model_versions)
    }

@app.post("/api/models/trigger-retrain", tags=["Model Updates"])
async def trigger_manual_retrain(background_tasks: BackgroundTasks):
    """
    Manually trigger model retraining
    """
    background_tasks.add_task(auto_retrain_model)
    
    await log_audit_entry(
        action="manual_retrain_triggered",
        details={"user": "manual_trigger"}
    )
    
    return {"status": "success", "message": "Model retraining triggered in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)