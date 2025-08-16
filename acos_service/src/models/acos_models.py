"""ACOS (Advertising Cost of Sales) data models and automation rules."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ACOSActionType(str, Enum):
    """ACOS automation action types."""
    PAUSE_CAMPAIGN = "pause_campaign"
    ADJUST_BID = "adjust_bid"
    ADJUST_BUDGET = "adjust_budget"
    SEND_ALERT = "send_alert"
    OPTIMIZE_KEYWORDS = "optimize_keywords"


class ACOSAlertSeverity(str, Enum):
    """ACOS alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ACOSThresholdType(str, Enum):
    """ACOS threshold types."""
    MAXIMUM = "maximum"  # Trigger when ACOS exceeds threshold
    MINIMUM = "minimum"  # Trigger when ACOS falls below threshold


# SQLAlchemy Models
class ACOSRule(Base):
    """ACOS automation rule database model."""
    __tablename__ = "acos_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Threshold configuration
    threshold_type = Column(String(50))  # maximum, minimum
    threshold_value = Column(Float)  # ACOS percentage
    evaluation_period_hours = Column(Integer, default=24)  # Hours to evaluate
    
    # Action configuration
    action_type = Column(String(50))
    action_config = Column(JSON)  # Additional action parameters
    
    # Targeting
    campaign_ids = Column(JSON)  # Specific campaigns, null = all campaigns
    categories = Column(JSON)  # Product categories
    minimum_spend = Column(Float, default=0.0)  # Minimum spend to trigger rule
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    executions = relationship("ACOSRuleExecution", back_populates="rule")


class ACOSRuleExecution(Base):
    """ACOS rule execution log."""
    __tablename__ = "acos_rule_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("acos_rules.id"))
    campaign_id = Column(Integer)
    
    # Execution details
    triggered_acos = Column(Float)
    threshold_value = Column(Float)
    action_taken = Column(String(50))
    action_result = Column(JSON)
    
    # Status
    status = Column(String(50))  # success, failed, skipped
    error_message = Column(Text, nullable=True)
    
    # Metadata
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rule = relationship("ACOSRule", back_populates="executions")


class ACOSAlert(Base):
    """ACOS alert database model."""
    __tablename__ = "acos_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer)
    rule_id = Column(Integer, ForeignKey("acos_rules.id"), nullable=True)
    
    # Alert details
    alert_type = Column(String(50))
    severity = Column(String(50))
    title = Column(String(255))
    message = Column(Text)
    
    # ACOS data
    current_acos = Column(Float)
    threshold_acos = Column(Float)
    period_hours = Column(Integer)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Recommendations
    recommended_actions = Column(JSON)


# Pydantic Models
class ACOSRuleBase(BaseModel):
    """Base ACOS rule model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    threshold_type: ACOSThresholdType
    threshold_value: float = Field(..., ge=0, le=1000)
    evaluation_period_hours: int = Field(24, ge=1, le=168)
    action_type: ACOSActionType
    action_config: Optional[Dict[str, Any]] = None
    campaign_ids: Optional[List[int]] = None
    categories: Optional[List[str]] = None
    minimum_spend: float = Field(0.0, ge=0)


class ACOSRuleCreate(ACOSRuleBase):
    """ACOS rule creation model."""
    pass


class ACOSRuleUpdate(BaseModel):
    """ACOS rule update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    threshold_value: Optional[float] = Field(None, ge=0, le=1000)
    evaluation_period_hours: Optional[int] = Field(None, ge=1, le=168)
    action_config: Optional[Dict[str, Any]] = None
    campaign_ids: Optional[List[int]] = None
    categories: Optional[List[str]] = None
    minimum_spend: Optional[float] = Field(None, ge=0)


class ACOSRuleResponse(ACOSRuleBase):
    """ACOS rule response model."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class ACOSAlertCreate(BaseModel):
    """ACOS alert creation model."""
    campaign_id: int
    alert_type: str
    severity: ACOSAlertSeverity
    title: str
    message: str
    current_acos: float
    threshold_acos: Optional[float] = None
    period_hours: int = 24
    recommended_actions: Optional[List[str]] = None


class ACOSAlertResponse(BaseModel):
    """ACOS alert response model."""
    id: int
    campaign_id: int
    rule_id: Optional[int]
    alert_type: str
    severity: ACOSAlertSeverity
    title: str
    message: str
    current_acos: float
    threshold_acos: Optional[float]
    period_hours: int
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    created_at: datetime
    recommended_actions: Optional[List[str]]
    
    class Config:
        from_attributes = True


class ACOSMetrics(BaseModel):
    """ACOS metrics summary."""
    campaign_id: int
    current_acos: float
    acos_trend: str  # "increasing", "decreasing", "stable"
    period_hours: int
    total_spend: float
    total_revenue: float
    recommendations: List[str]


class ACOSAnalysis(BaseModel):
    """ACOS analysis result."""
    campaign_id: int
    current_acos: float
    target_acos: Optional[float]
    performance_status: str  # "good", "warning", "critical"
    trend_analysis: Dict[str, Any]
    optimization_suggestions: List[str]
    projected_impact: Dict[str, float]