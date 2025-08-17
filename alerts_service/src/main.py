from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
import logging
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/ml_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Prometheus metrics
alerts_counter = Counter('alerts_triggered_total', 'Total alerts triggered', ['alert_type', 'severity'])
notifications_counter = Counter('notifications_sent_total', 'Total notifications sent', ['channel'])

# Database Models
class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String)
    description = Column(Text)
    metric = Column(String)  # acos, markup_margin, campaign_spend, etc.
    condition = Column(String)  # >, <, >=, <=, ==, !=
    threshold = Column(Float)
    severity = Column(String)  # low, medium, high, critical
    enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON)  # email, webhook, card, sms
    notification_config = Column(JSON)  # specific config for each channel
    cooldown_minutes = Column(Integer, default=60)  # Prevent spam
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)

class AlertEvent(Base):
    __tablename__ = "alert_events"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_rule_id = Column(Integer, index=True)
    user_id = Column(String, index=True)
    metric = Column(String)
    actual_value = Column(Float)
    threshold = Column(Float)
    severity = Column(String)
    message = Column(Text)
    acknowledged = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    campaign_id = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_event_id = Column(Integer, index=True)
    channel = Column(String)  # email, webhook, card, sms
    status = Column(String)  # sent, failed, pending
    recipient = Column(String)
    message = Column(Text)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class AlertRuleCreate(BaseModel):
    user_id: str
    name: str
    description: str
    metric: str
    condition: str
    threshold: float
    severity: str
    notification_channels: List[str]
    notification_config: Dict[str, Any]
    cooldown_minutes: int = 60

class AlertRuleResponse(BaseModel):
    id: int
    user_id: str
    name: str
    description: str
    metric: str
    condition: str
    threshold: float
    severity: str
    enabled: bool
    notification_channels: List[str]
    notification_config: Dict[str, Any]
    cooldown_minutes: int
    created_at: datetime
    last_triggered: Optional[datetime]

class AlertEventCreate(BaseModel):
    alert_rule_id: int
    user_id: str
    metric: str
    actual_value: float
    threshold: float
    severity: str
    message: str
    campaign_id: Optional[str] = None
    product_id: Optional[str] = None

class AlertEventResponse(BaseModel):
    id: int
    alert_rule_id: int
    user_id: str
    metric: str
    actual_value: float
    threshold: float
    severity: str
    message: str
    acknowledged: bool
    resolved: bool
    campaign_id: Optional[str]
    product_id: Optional[str]
    created_at: datetime

class MetricCheck(BaseModel):
    user_id: str
    metric: str
    value: float
    campaign_id: Optional[str] = None
    product_id: Optional[str] = None

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Alerts Service", 
    description="Sistema de alertas personalizados para campanhas e métricas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "alerts"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Alert Rules endpoints
@app.post("/alert-rules", response_model=AlertRuleResponse)
async def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Criar nova regra de alerta"""
    try:
        db_rule = AlertRule(**rule.dict())
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        
        logger.info(f"Alert rule created: {rule.name} for user {rule.user_id}")
        return db_rule
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        raise HTTPException(status_code=500, detail="Error creating alert rule")

@app.get("/alert-rules/{user_id}", response_model=List[AlertRuleResponse])
async def get_user_alert_rules(user_id: str, db: Session = Depends(get_db)):
    """Buscar regras de alerta do usuário"""
    rules = db.query(AlertRule).filter(AlertRule.user_id == user_id).all()
    return rules

@app.put("/alert-rules/{rule_id}/toggle")
async def toggle_alert_rule(rule_id: int, enabled: bool, db: Session = Depends(get_db)):
    """Ativar/desativar regra de alerta"""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    rule.enabled = enabled
    db.commit()
    return {"message": f"Alert rule {'enabled' if enabled else 'disabled'}"}

@app.delete("/alert-rules/{rule_id}")
async def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Deletar regra de alerta"""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Alert rule deleted"}

# Alert Events endpoints
@app.get("/alert-events/{user_id}", response_model=List[AlertEventResponse])
async def get_user_alert_events(
    user_id: str, 
    skip: int = 0, 
    limit: int = 50,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Buscar eventos de alerta do usuário"""
    query = db.query(AlertEvent).filter(AlertEvent.user_id == user_id)
    
    if severity:
        query = query.filter(AlertEvent.severity == severity)
    if resolved is not None:
        query = query.filter(AlertEvent.resolved == resolved)
    
    events = query.order_by(AlertEvent.created_at.desc()).offset(skip).limit(limit).all()
    return events

@app.put("/alert-events/{event_id}/acknowledge")
async def acknowledge_alert(event_id: int, db: Session = Depends(get_db)):
    """Marcar alerta como reconhecido"""
    event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Alert event not found")
    
    event.acknowledged = True
    event.acknowledged_at = datetime.utcnow()
    db.commit()
    return {"message": "Alert acknowledged"}

@app.put("/alert-events/{event_id}/resolve")
async def resolve_alert(event_id: int, db: Session = Depends(get_db)):
    """Marcar alerta como resolvido"""
    event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Alert event not found")
    
    event.resolved = True
    event.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Alert resolved"}

# Metric checking endpoint
@app.post("/check-metrics")
async def check_metrics(
    metrics: List[MetricCheck], 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Verificar métricas contra regras de alerta"""
    triggered_alerts = []
    
    for metric_check in metrics:
        # Get active alert rules for this user and metric
        rules = db.query(AlertRule).filter(
            AlertRule.user_id == metric_check.user_id,
            AlertRule.metric == metric_check.metric,
            AlertRule.enabled == True
        ).all()
        
        for rule in rules:
            # Check if rule should trigger
            should_trigger = False
            actual_value = metric_check.value
            threshold = rule.threshold
            
            if rule.condition == ">" and actual_value > threshold:
                should_trigger = True
            elif rule.condition == "<" and actual_value < threshold:
                should_trigger = True
            elif rule.condition == ">=" and actual_value >= threshold:
                should_trigger = True
            elif rule.condition == "<=" and actual_value <= threshold:
                should_trigger = True
            elif rule.condition == "==" and actual_value == threshold:
                should_trigger = True
            elif rule.condition == "!=" and actual_value != threshold:
                should_trigger = True
            
            if should_trigger:
                # Check cooldown
                if rule.last_triggered:
                    time_since_last = datetime.utcnow() - rule.last_triggered
                    if time_since_last.total_seconds() < rule.cooldown_minutes * 60:
                        continue  # Still in cooldown
                
                # Create alert event
                alert_event = AlertEvent(
                    alert_rule_id=rule.id,
                    user_id=metric_check.user_id,
                    metric=metric_check.metric,
                    actual_value=actual_value,
                    threshold=threshold,
                    severity=rule.severity,
                    message=f"Alerta: {rule.name} - {metric_check.metric} {rule.condition} {threshold} (valor atual: {actual_value})",
                    campaign_id=metric_check.campaign_id,
                    product_id=metric_check.product_id
                )
                
                db.add(alert_event)
                
                # Update last triggered
                rule.last_triggered = datetime.utcnow()
                
                # Send notifications in background
                background_tasks.add_task(
                    send_notifications, 
                    alert_event.id, 
                    rule.notification_channels, 
                    rule.notification_config,
                    alert_event.message
                )
                
                # Update metrics
                alerts_counter.labels(
                    alert_type=metric_check.metric, 
                    severity=rule.severity
                ).inc()
                
                triggered_alerts.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "metric": metric_check.metric,
                    "actual_value": actual_value,
                    "threshold": threshold,
                    "severity": rule.severity
                })
    
    db.commit()
    
    return {
        "message": f"Checked {len(metrics)} metrics",
        "triggered_alerts": len(triggered_alerts),
        "alerts": triggered_alerts
    }

# Notification functions
async def send_notifications(event_id: int, channels: List[str], config: Dict[str, Any], message: str):
    """Enviar notificações por diferentes canais"""
    db = SessionLocal()
    
    try:
        for channel in channels:
            if channel == "email":
                await send_email_notification(event_id, config.get("email", {}), message, db)
            elif channel == "webhook":
                await send_webhook_notification(event_id, config.get("webhook", {}), message, db)
            elif channel == "card":
                await send_card_notification(event_id, config.get("card", {}), message, db)
    except Exception as e:
        logger.error(f"Error sending notifications: {e}")
    finally:
        db.close()

async def send_email_notification(event_id: int, email_config: Dict, message: str, db: Session):
    """Enviar notificação por email"""
    try:
        to_email = email_config.get("recipient")
        if not to_email:
            return
        
        smtp_server = os.getenv("SMTP_SERVER", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        msg = MimeMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = "ML Project - Alerta de Sistema"
        
        body = f"""
        <html>
        <body>
            <h2>Alerta do Sistema ML Project</h2>
            <p>{message}</p>
            <p>Verifique o dashboard para mais detalhes.</p>
            <hr>
            <p><small>Este é um alerta automático do sistema.</small></p>
        </body>
        </html>
        """
        
        msg.attach(MimeText(body, "html"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        
        server.send_message(msg)
        server.quit()
        
        # Log notification
        log = NotificationLog(
            alert_event_id=event_id,
            channel="email",
            status="sent",
            recipient=to_email,
            message=message
        )
        db.add(log)
        db.commit()
        
        notifications_counter.labels(channel="email").inc()
        logger.info(f"Email notification sent to {to_email}")
        
    except Exception as e:
        # Log error
        log = NotificationLog(
            alert_event_id=event_id,
            channel="email",
            status="failed",
            recipient=email_config.get("recipient", "unknown"),
            message=message,
            error_message=str(e)
        )
        db.add(log)
        db.commit()
        logger.error(f"Failed to send email notification: {e}")

async def send_webhook_notification(event_id: int, webhook_config: Dict, message: str, db: Session):
    """Enviar notificação via webhook"""
    try:
        webhook_url = webhook_config.get("url")
        if not webhook_url:
            return
        
        payload = {
            "event_id": event_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "ml_project_alerts"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        # Log notification
        log = NotificationLog(
            alert_event_id=event_id,
            channel="webhook",
            status="sent",
            recipient=webhook_url,
            message=message
        )
        db.add(log)
        db.commit()
        
        notifications_counter.labels(channel="webhook").inc()
        logger.info(f"Webhook notification sent to {webhook_url}")
        
    except Exception as e:
        # Log error
        log = NotificationLog(
            alert_event_id=event_id,
            channel="webhook",
            status="failed",
            recipient=webhook_config.get("url", "unknown"),
            message=message,
            error_message=str(e)
        )
        db.add(log)
        db.commit()
        logger.error(f"Failed to send webhook notification: {e}")

async def send_card_notification(event_id: int, card_config: Dict, message: str, db: Session):
    """Enviar notificação por card animado (via websocket ou API)"""
    try:
        # This would integrate with the frontend notification system
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        payload = {
            "type": "alert",
            "event_id": event_id,
            "message": message,
            "severity": card_config.get("severity", "medium"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to frontend notification endpoint
        response = requests.post(f"{frontend_url}/api/notifications", json=payload, timeout=10)
        
        # Log notification
        log = NotificationLog(
            alert_event_id=event_id,
            channel="card",
            status="sent",
            recipient="frontend_notifications",
            message=message
        )
        db.add(log)
        db.commit()
        
        notifications_counter.labels(channel="card").inc()
        logger.info(f"Card notification sent to frontend")
        
    except Exception as e:
        # Log error
        log = NotificationLog(
            alert_event_id=event_id,
            channel="card",
            status="failed",
            recipient="frontend_notifications",
            message=message,
            error_message=str(e)
        )
        db.add(log)
        db.commit()
        logger.error(f"Failed to send card notification: {e}")

# Predefined alert templates
@app.post("/alert-rules/templates/acos-high")
async def create_acos_alert(user_id: str, threshold: float = 15.0, db: Session = Depends(get_db)):
    """Criar alerta para ACOS alto"""
    rule = AlertRuleCreate(
        user_id=user_id,
        name="ACOS Alto",
        description="Alerta quando ACOS ultrapassa o limite seguro",
        metric="acos",
        condition=">",
        threshold=threshold,
        severity="high",
        notification_channels=["email", "card"],
        notification_config={
            "email": {"recipient": f"user_{user_id}@company.com"},
            "card": {"severity": "high"}
        }
    )
    return await create_alert_rule(rule, db)

@app.post("/alert-rules/templates/markup-margin-low")
async def create_markup_margin_alert(user_id: str, threshold: float = 10.0, db: Session = Depends(get_db)):
    """Criar alerta para margem de markup baixa"""
    rule = AlertRuleCreate(
        user_id=user_id,
        name="Margem de Markup Baixa",
        description="Alerta quando margem de markup está abaixo do limite seguro",
        metric="markup_margin",
        condition="<",
        threshold=threshold,
        severity="medium",
        notification_channels=["email", "card"],
        notification_config={
            "email": {"recipient": f"user_{user_id}@company.com"},
            "card": {"severity": "medium"}
        }
    )
    return await create_alert_rule(rule, db)

@app.post("/alert-rules/templates/campaign-spend-high")
async def create_campaign_spend_alert(user_id: str, threshold: float = 1000.0, db: Session = Depends(get_db)):
    """Criar alerta para gasto alto em campanha"""
    rule = AlertRuleCreate(
        user_id=user_id,
        name="Gasto Alto em Campanha",
        description="Alerta quando gasto da campanha ultrapassa o limite",
        metric="campaign_spend",
        condition=">",
        threshold=threshold,
        severity="critical",
        notification_channels=["email", "card", "webhook"],
        notification_config={
            "email": {"recipient": f"user_{user_id}@company.com"},
            "card": {"severity": "critical"},
            "webhook": {"url": "http://webhook.company.com/alerts"}
        }
    )
    return await create_alert_rule(rule, db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)