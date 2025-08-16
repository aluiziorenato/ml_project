from datetime import datetime, time
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, JSON
from pydantic import BaseModel


class CampaignStatus(str, Enum):
    """Status enum for discount campaigns"""
    ACTIVE = "active"
    PAUSED = "paused"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"
    DRAFT = "draft"


class ScheduleStatus(str, Enum):
    """Status enum for schedule entries"""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"


class DayOfWeek(str, Enum):
    """Days of the week enum"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class DiscountCampaign(SQLModel, table=True):
    """Model for discount campaigns"""
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: str = Field(index=True)
    item_id: str = Field(index=True)
    campaign_name: str
    discount_percentage: float = Field(ge=0, le=100)
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    
    # Scheduling information
    start_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    end_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    
    # Metrics
    total_clicks: int = Field(default=0)
    total_impressions: int = Field(default=0)
    total_conversions: int = Field(default=0)
    total_sales_amount: float = Field(default=0.0)
    
    # Relationships
    schedules: List["CampaignSchedule"] = Relationship(back_populates="campaign")
    metrics: List["CampaignMetric"] = Relationship(back_populates="campaign")


class CampaignSchedule(SQLModel, table=True):
    """Model for campaign scheduling rules"""
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="discountcampaign.id")
    
    # Schedule configuration
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    action: str = Field(description="activate or pause")
    
    # Execution tracking
    status: ScheduleStatus = Field(default=ScheduleStatus.PENDING)
    last_executed: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    next_execution: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    
    # Relationship
    campaign: DiscountCampaign = Relationship(back_populates="schedules")


class CampaignMetric(SQLModel, table=True):
    """Model for storing campaign metrics"""
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="discountcampaign.id")
    
    # Metrics data
    clicks: int = Field(default=0)
    impressions: int = Field(default=0)
    conversions: int = Field(default=0)
    conversion_rate: float = Field(default=0.0)
    sales_amount: float = Field(default=0.0)
    
    # Additional metrics from ML API
    engagement_score: Optional[float] = Field(default=None)
    performance_index: Optional[float] = Field(default=None)
    
    # Timestamp
    recorded_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    period_start: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    period_end: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    
    # Relationship
    campaign: DiscountCampaign = Relationship(back_populates="metrics")


class ItemSuggestion(SQLModel, table=True):
    """Model for storing item suggestions for discount campaigns"""
    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: str = Field(index=True)
    item_id: str = Field(index=True)
    
    # Item information
    title: str
    image_url: Optional[str] = Field(default=None)
    current_price: float
    category_id: str
    
    # Engagement metrics
    recent_clicks: int = Field(default=0)
    recent_impressions: int = Field(default=0)
    recent_views: int = Field(default=0)
    
    # Suggestion scoring
    potential_score: float = Field(description="AI-calculated potential for discount campaign")
    engagement_trend: float = Field(description="Trend in engagement metrics")
    
    # Suggestion metadata
    suggested_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    is_active: bool = Field(default=True)


class PerformancePrediction(SQLModel, table=True):
    """Model for storing performance predictions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="discountcampaign.id")
    
    # Prediction data
    predicted_clicks: int
    predicted_impressions: int
    predicted_conversions: int
    predicted_sales: float
    confidence_score: float = Field(ge=0, le=1)
    
    # Prediction period
    prediction_period_days: int
    prediction_date: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    
    # Model information
    model_version: str
    features_used: Optional[dict] = Field(default=None, sa_column=Column(JSON))


# Pydantic models for API requests/responses

class CampaignCreate(BaseModel):
    """Schema for creating a discount campaign"""
    item_id: str
    campaign_name: str
    discount_percentage: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    """Schema for updating a discount campaign"""
    campaign_name: Optional[str] = None
    discount_percentage: Optional[float] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ScheduleCreate(BaseModel):
    """Schema for creating a campaign schedule"""
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    action: str


class ScheduleUpdate(BaseModel):
    """Schema for updating a campaign schedule"""
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    action: Optional[str] = None


class SuggestionResponse(BaseModel):
    """Schema for item suggestion response"""
    item_id: str
    title: str
    image_url: Optional[str]
    current_price: float
    recent_clicks: int
    potential_score: float
    engagement_trend: float


class MetricsResponse(BaseModel):
    """Schema for campaign metrics response"""
    campaign_id: int
    clicks: int
    impressions: int
    conversions: int
    conversion_rate: float
    sales_amount: float
    period_start: datetime
    period_end: datetime


class PredictionResponse(BaseModel):
    """Schema for performance prediction response"""
    campaign_id: int
    predicted_clicks: int
    predicted_impressions: int
    predicted_conversions: int
    predicted_sales: float
    confidence_score: float
    prediction_period_days: int