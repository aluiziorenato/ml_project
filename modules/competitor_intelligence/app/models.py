"""Database models for competitor intelligence module."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

Base = declarative_base()


class CompetitorProfile(Base):
    """Competitor profile information."""
    __tablename__ = "competitor_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(100), index=True, nullable=False)
    website = Column(String(500))
    estimated_budget = Column(Float, default=0.0)
    market_share = Column(Float, default=0.0)
    threat_level = Column(String(20), default="low")  # low, medium, high
    status = Column(String(20), default="active")  # active, inactive, monitoring
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CompetitorProduct(Base):
    """Competitor product information."""
    __tablename__ = "competitor_products"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String(255), index=True, nullable=False)
    product_id = Column(String(100), index=True, nullable=False)
    title = Column(Text)
    price = Column(Float)
    currency = Column(String(10), default="BRL")
    availability = Column(String(20), default="available")
    position_rank = Column(Integer)
    category = Column(String(100), index=True)
    keywords = Column(JSON)  # List of associated keywords
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PriceHistory(Base):
    """Price history tracking for competitor products."""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String(255), index=True, nullable=False)
    product_id = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="BRL")
    discount_percentage = Column(Float, default=0.0)
    is_promotion = Column(Boolean, default=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class KeywordCompetition(Base):
    """Keyword competition analysis."""
    __tablename__ = "keyword_competition"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), index=True, nullable=False)
    category = Column(String(100), index=True)
    competition_level = Column(String(20))  # low, medium, high
    estimated_cpc = Column(Float)
    search_volume = Column(Integer)
    difficulty_score = Column(Integer)  # 1-100
    opportunity_score = Column(Integer)  # 1-100
    top_competitors = Column(JSON)  # List of top competitors for this keyword
    last_analyzed = Column(DateTime(timezone=True), server_default=func.now())


class CompetitorStrategy(Base):
    """Competitor strategy tracking."""
    __tablename__ = "competitor_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String(255), index=True, nullable=False)
    strategy_type = Column(String(50))  # aggressive, defensive, conservative
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence_score = Column(Float)  # ML confidence in strategy detection
    indicators = Column(JSON)  # Strategy indicators detected
    duration_days = Column(Integer)  # How long this strategy has been active


class MarketMovement(Base):
    """Market movements and competitor actions."""
    __tablename__ = "market_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String(255), index=True, nullable=False)
    movement_type = Column(String(50))  # price_drop, promotion_start, ranking_change, etc.
    description = Column(Text)
    impact_score = Column(Float)  # 1-100, how significant this movement is
    category = Column(String(100), index=True)
    movement_metadata = Column(JSON)  # Additional movement data
    detected_at = Column(DateTime(timezone=True), server_default=func.now())


class SentimentAnalysis(Base):
    """Competitor sentiment analysis from reviews."""
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String(255), index=True, nullable=False)
    product_id = Column(String(100), index=True)
    review_source = Column(String(100))  # mercadolibre, amazon, etc.
    sentiment_score = Column(Float)  # -1 to 1
    positive_aspects = Column(JSON)  # List of positive points
    negative_aspects = Column(JSON)  # List of negative points
    summary = Column(Text)
    total_reviews = Column(Integer)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class UserMonitoringList(Base):
    """User-defined monitoring lists."""
    __tablename__ = "user_monitoring_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    list_name = Column(String(255), nullable=False)
    competitor_names = Column(JSON)  # List of competitor names to monitor
    product_ids = Column(JSON)  # List of specific product IDs to monitor
    keywords = Column(JSON)  # List of keywords to monitor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic models for API
class CompetitorProfileCreate(BaseModel):
    name: str
    category: str
    website: Optional[str] = None
    estimated_budget: Optional[float] = 0.0


class CompetitorProfileResponse(BaseModel):
    id: int
    name: str
    category: str
    website: Optional[str]
    estimated_budget: float
    market_share: float
    threat_level: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    id: int
    competitor_name: str
    product_id: str
    price: float
    currency: str
    discount_percentage: float
    is_promotion: bool
    recorded_at: datetime

    class Config:
        from_attributes = True


class KeywordCompetitionResponse(BaseModel):
    id: int
    keyword: str
    category: Optional[str]
    competition_level: Optional[str]
    estimated_cpc: Optional[float]
    search_volume: Optional[int]
    difficulty_score: Optional[int]
    opportunity_score: Optional[int]
    top_competitors: Optional[List[Dict[str, Any]]]
    last_analyzed: datetime

    class Config:
        from_attributes = True


class SentimentAnalysisResponse(BaseModel):
    id: int
    competitor_name: str
    product_id: Optional[str]
    review_source: Optional[str]
    sentiment_score: Optional[float]
    positive_aspects: Optional[List[str]]
    negative_aspects: Optional[List[str]]
    summary: Optional[str]
    total_reviews: Optional[int]
    analyzed_at: datetime

    class Config:
        from_attributes = True


class MonitoringListCreate(BaseModel):
    user_id: str
    list_name: str
    competitor_names: Optional[List[str]] = []
    product_ids: Optional[List[str]] = []
    keywords: Optional[List[str]] = []


class MonitoringListResponse(BaseModel):
    id: int
    user_id: str
    list_name: str
    competitor_names: List[str]
    product_ids: List[str]
    keywords: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True