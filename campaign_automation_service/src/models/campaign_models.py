"""Campaign automation data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

Base = declarative_base()


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    """Campaign type enumeration."""
    SPONSORED_ADS = "sponsored_ads"
    PRODUCT_ADS = "product_ads"
    DISPLAY_ADS = "display_ads"
    RETARGETING = "retargeting"


class OptimizationGoal(str, Enum):
    """Optimization goal enumeration."""
    CONVERSIONS = "conversions"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    ROI = "roi"
    REVENUE = "revenue"


# SQLAlchemy Models
class Campaign(Base):
    """Campaign database model."""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    status = Column(String(50), default=CampaignStatus.DRAFT)
    campaign_type = Column(String(50))
    optimization_goal = Column(String(50))
    
    # Budget and bidding
    daily_budget = Column(Float)
    total_budget = Column(Float)
    max_cpc = Column(Float)
    target_cpa = Column(Float)
    
    # Targeting
    target_audience = Column(JSON)
    keywords = Column(JSON)
    categories = Column(JSON)
    locations = Column(JSON)
    
    # Schedule
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    metrics = relationship("CampaignMetric", back_populates="campaign")
    experiments = relationship("ABTest", back_populates="campaign")


class CampaignMetric(Base):
    """Campaign metrics database model."""
    __tablename__ = "campaign_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    # Time period
    date = Column(DateTime)
    hour = Column(Integer)
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Derived metrics
    ctr = Column(Float, default=0.0)  # Click Through Rate
    cpc = Column(Float, default=0.0)  # Cost Per Click
    cpa = Column(Float, default=0.0)  # Cost Per Acquisition
    roas = Column(Float, default=0.0)  # Return on Ad Spend
    roi = Column(Float, default=0.0)  # Return on Investment
    acos = Column(Float, default=0.0)  # Advertising Cost of Sales
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="metrics")


class ABTest(Base):
    """A/B test database model."""
    __tablename__ = "ab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    name = Column(String(255))
    description = Column(Text)
    
    # Test configuration
    test_type = Column(String(50))  # ad_copy, keywords, bidding, etc.
    variants = Column(JSON)  # List of test variants
    traffic_split = Column(JSON)  # Traffic allocation per variant
    
    # Status and results
    status = Column(String(50), default="running")
    confidence_level = Column(Float, default=0.95)
    statistical_significance = Column(Boolean, default=False)
    winning_variant = Column(String(255))
    
    # Schedule
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="experiments")


class CompetitorData(Base):
    """Competitor monitoring data model."""
    __tablename__ = "competitor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String(255), index=True)
    category = Column(String(255))
    
    # Competitive metrics
    estimated_budget = Column(Float)
    keyword_overlap = Column(JSON)
    ad_positions = Column(JSON)
    pricing_data = Column(JSON)
    
    # Analysis results
    threat_level = Column(String(50))  # low, medium, high
    opportunity_score = Column(Float)
    recommendations = Column(JSON)
    
    # Metadata
    monitored_date = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String(255))


# Pydantic Models for API
class CampaignBase(BaseModel):
    """Base campaign model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: CampaignType
    optimization_goal: OptimizationGoal
    daily_budget: float = Field(..., gt=0)
    total_budget: Optional[float] = Field(None, gt=0)
    max_cpc: Optional[float] = Field(None, gt=0)
    target_cpa: Optional[float] = Field(None, gt=0)
    target_audience: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    """Campaign creation model."""
    pass


class CampaignUpdate(BaseModel):
    """Campaign update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    daily_budget: Optional[float] = Field(None, gt=0)
    max_cpc: Optional[float] = Field(None, gt=0)
    target_audience: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None


class CampaignResponse(CampaignBase):
    """Campaign response model."""
    id: int
    status: CampaignStatus
    impressions: int
    clicks: int
    conversions: int
    cost: float
    revenue: float
    created_at: datetime
    updated_at: datetime
    
    # Calculated metrics
    ctr: Optional[float] = None
    cpc: Optional[float] = None
    roas: Optional[float] = None
    roi: Optional[float] = None
    acos: Optional[float] = None
    
    class Config:
        from_attributes = True


class MetricsSummary(BaseModel):
    """Campaign metrics summary."""
    campaign_id: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_cost: float
    total_revenue: float
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    roas: float
    roi: float
    acos: float


class ABTestCreate(BaseModel):
    """A/B test creation model."""
    campaign_id: int
    name: str
    description: Optional[str] = None
    test_type: str
    variants: List[Dict[str, Any]]
    traffic_split: Dict[str, float]
    confidence_level: float = 0.95
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ABTestResponse(BaseModel):
    """A/B test response model."""
    id: int
    campaign_id: int
    name: str
    description: Optional[str]
    test_type: str
    variants: List[Dict[str, Any]]
    status: str
    statistical_significance: bool
    winning_variant: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompetitorAnalysis(BaseModel):
    """Competitor analysis model."""
    competitor_name: str
    category: str
    estimated_budget: Optional[float]
    keyword_overlap: Dict[str, Any]
    threat_level: str
    opportunity_score: float
    recommendations: List[str]
    monitored_date: datetime