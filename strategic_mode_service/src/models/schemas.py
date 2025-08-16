from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class StrategyType(str, Enum):
    """Available strategy types"""
    MAXIMIZE_PROFIT = "maximize_profit"
    SCALE_SALES = "scale_sales"
    PROTECT_MARGIN = "protect_margin"
    AGGRESSIVE_CAMPAIGNS = "aggressive_campaigns"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class ActionStatus(str, Enum):
    """Automation action status"""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"

# Strategic Mode Models
class StrategicModeBase(BaseModel):
    """Base strategic mode model"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    acos_min: Decimal = Field(..., ge=0, le=100)
    acos_max: Decimal = Field(..., ge=0, le=100)
    budget_multiplier: Decimal = Field(..., ge=0.1, le=5.0)
    bid_adjustment: Decimal = Field(..., ge=-100, le=100)
    margin_threshold: Decimal = Field(..., ge=0, le=100)
    automation_rules: Optional[Dict[str, Any]] = None
    alert_thresholds: Optional[Dict[str, Any]] = None

    @validator('acos_max')
    def acos_max_greater_than_min(cls, v, values):
        if 'acos_min' in values and v <= values['acos_min']:
            raise ValueError('acos_max must be greater than acos_min')
        return v

class StrategicModeCreate(StrategicModeBase):
    """Create strategic mode"""
    pass

class StrategicModeUpdate(BaseModel):
    """Update strategic mode"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    acos_min: Optional[Decimal] = Field(None, ge=0, le=100)
    acos_max: Optional[Decimal] = Field(None, ge=0, le=100)
    budget_multiplier: Optional[Decimal] = Field(None, ge=0.1, le=5.0)
    bid_adjustment: Optional[Decimal] = Field(None, ge=-100, le=100)
    margin_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    automation_rules: Optional[Dict[str, Any]] = None
    alert_thresholds: Optional[Dict[str, Any]] = None

class StrategicModeResponse(StrategicModeBase):
    """Strategic mode response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Special Date Models
class SpecialDateBase(BaseModel):
    """Base special date model"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    start_date: date
    end_date: date
    budget_multiplier: Decimal = Field(1.0, ge=0.1, le=5.0)
    acos_adjustment: Decimal = Field(0.0, ge=-50, le=50)
    strategy_override_id: Optional[int] = None
    peak_hours: Optional[List[Dict[str, int]]] = None
    priority_categories: Optional[List[str]] = None
    custom_settings: Optional[Dict[str, Any]] = None
    is_active: bool = True

    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class SpecialDateCreate(SpecialDateBase):
    """Create special date"""
    pass

class SpecialDateUpdate(BaseModel):
    """Update special date"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget_multiplier: Optional[Decimal] = Field(None, ge=0.1, le=5.0)
    acos_adjustment: Optional[Decimal] = Field(None, ge=-50, le=50)
    strategy_override_id: Optional[int] = None
    peak_hours: Optional[List[Dict[str, int]]] = None
    priority_categories: Optional[List[str]] = None
    custom_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class SpecialDateResponse(SpecialDateBase):
    """Special date response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Strategy Configuration Models
class StrategyConfigurationBase(BaseModel):
    """Base strategy configuration model"""
    user_id: int
    active_strategy_id: int
    custom_settings: Optional[Dict[str, Any]] = None
    special_date_overrides: Optional[Dict[str, Any]] = None
    notification_channels: Optional[Dict[str, Any]] = None

class StrategyConfigurationCreate(StrategyConfigurationBase):
    """Create strategy configuration"""
    pass

class StrategyConfigurationUpdate(BaseModel):
    """Update strategy configuration"""
    active_strategy_id: Optional[int] = None
    custom_settings: Optional[Dict[str, Any]] = None
    special_date_overrides: Optional[Dict[str, Any]] = None
    notification_channels: Optional[Dict[str, Any]] = None

class StrategyConfigurationResponse(StrategyConfigurationBase):
    """Strategy configuration response"""
    id: int
    is_active: bool
    last_applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Performance Models
class StrategyPerformanceBase(BaseModel):
    """Base strategy performance model"""
    strategy_id: int
    user_id: int
    date: date
    total_spend: Optional[Decimal] = None
    total_sales: Optional[Decimal] = None
    average_acos: Optional[Decimal] = None
    roi: Optional[Decimal] = None
    profit: Optional[Decimal] = None
    campaigns_count: Optional[int] = None
    active_campaigns: Optional[int] = None
    paused_campaigns: Optional[int] = None
    conversions: Optional[int] = None
    clicks: Optional[int] = None
    impressions: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None

class StrategyPerformanceCreate(StrategyPerformanceBase):
    """Create strategy performance"""
    pass

class StrategyPerformanceResponse(StrategyPerformanceBase):
    """Strategy performance response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Alert Models
class StrategyAlertBase(BaseModel):
    """Base strategy alert model"""
    user_id: int
    strategy_id: Optional[int] = None
    alert_type: str = Field(..., max_length=50)
    severity: AlertSeverity
    title: str = Field(..., max_length=200)
    message: str
    metadata: Optional[Dict[str, Any]] = None

class StrategyAlertCreate(StrategyAlertBase):
    """Create strategy alert"""
    pass

class StrategyAlertResponse(StrategyAlertBase):
    """Strategy alert response"""
    id: int
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Automation Action Models
class AutomationActionBase(BaseModel):
    """Base automation action model"""
    user_id: int
    strategy_id: Optional[int] = None
    action_type: str = Field(..., max_length=50)
    service: str = Field(..., max_length=50)
    campaign_id: Optional[str] = Field(None, max_length=100)
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class AutomationActionCreate(AutomationActionBase):
    """Create automation action"""
    pass

class AutomationActionResponse(AutomationActionBase):
    """Automation action response"""
    id: int
    status: ActionStatus
    error_message: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Strategy Application Models
class StrategyApplicationRequest(BaseModel):
    """Request to apply a strategy"""
    strategy_id: int
    user_id: int
    apply_immediately: bool = True
    scheduled_for: Optional[datetime] = None
    simulate_only: bool = False

class StrategyApplicationResponse(BaseModel):
    """Response for strategy application"""
    success: bool
    message: str
    actions_performed: List[AutomationActionResponse] = []
    alerts_generated: List[StrategyAlertResponse] = []
    estimated_impact: Optional[Dict[str, Any]] = None

# Dashboard Models
class StrategyDashboardData(BaseModel):
    """Dashboard data response"""
    current_strategy: Optional[StrategicModeResponse] = None
    active_special_dates: List[SpecialDateResponse] = []
    recent_alerts: List[StrategyAlertResponse] = []
    recent_actions: List[AutomationActionResponse] = []
    performance_summary: Optional[Dict[str, Any]] = None
    kpis: Dict[str, Any] = {}

# Report Models
class PerformanceReportRequest(BaseModel):
    """Performance report request"""
    user_id: int
    start_date: date
    end_date: date
    strategy_ids: Optional[List[int]] = None
    include_comparison: bool = True

class PerformanceReportResponse(BaseModel):
    """Performance report response"""
    period: Dict[str, date]
    strategies: List[StrategyPerformanceResponse]
    summary: Dict[str, Any]
    comparison: Optional[Dict[str, Any]] = None
    recommendations: List[str] = []