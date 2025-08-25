from sqlalchemy import Column, Integer, String, Text, Decimal, DateTime, Date, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

class StrategicMode(Base):
    """Strategic modes configuration"""
    __tablename__ = "strategic_modes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    acos_min = Column(Decimal(5, 2))
    acos_max = Column(Decimal(5, 2))
    budget_multiplier = Column(Decimal(3, 2))
    bid_adjustment = Column(Decimal(3, 2))
    margin_threshold = Column(Decimal(5, 2))
    
    # Automation settings
    automation_rules = Column(JSON)
    alert_thresholds = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    configurations = relationship("StrategyConfiguration", back_populates="strategy")
    performance_logs = relationship("StrategyPerformanceLog", back_populates="strategy")

class SpecialDate(Base):
    """Special dates configuration"""
    __tablename__ = "special_dates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Strategy overrides
    budget_multiplier = Column(Decimal(3, 2), default=1.0)
    acos_adjustment = Column(Decimal(3, 2), default=0.0)
    strategy_override_id = Column(Integer, ForeignKey("strategic_modes.id"))
    
    # Additional settings
    peak_hours = Column(JSON)  # List of hour ranges
    priority_categories = Column(JSON)  # List of category IDs
    custom_settings = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    strategy_override = relationship("StrategicMode")

class StrategyConfiguration(Base):
    """User strategy configurations"""
    __tablename__ = "strategy_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    active_strategy_id = Column(Integer, ForeignKey("strategic_modes.id"), nullable=False)
    
    # Custom settings
    custom_settings = Column(JSON)
    special_date_overrides = Column(JSON)
    notification_channels = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_applied_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    strategy = relationship("StrategicMode", back_populates="configurations")

class StrategyPerformanceLog(Base):
    """Strategy performance tracking"""
    __tablename__ = "strategy_performance_log"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategic_modes.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    
    # Financial metrics
    total_spend = Column(Decimal(10, 2))
    total_sales = Column(Decimal(10, 2))
    average_acos = Column(Decimal(5, 2))
    roi = Column(Decimal(5, 2))
    profit = Column(Decimal(10, 2))
    
    # Campaign metrics
    campaigns_count = Column(Integer)
    active_campaigns = Column(Integer)
    paused_campaigns = Column(Integer)
    conversions = Column(Integer)
    clicks = Column(Integer)
    impressions = Column(Integer)
    
    # Additional metrics
    metrics = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    strategy = relationship("StrategicMode", back_populates="performance_logs")

class StrategyAlert(Base):
    """Strategy alerts and notifications"""
    __tablename__ = "strategy_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategic_modes.id"))
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # acos_high, margin_low, budget_exceeded, etc.
    severity = Column(String(20), nullable=False)  # info, warning, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    strategy = relationship("StrategicMode")

class AutomationAction(Base):
    """Automation actions log"""
    __tablename__ = "automation_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategic_modes.id"))
    
    # Action details
    action_type = Column(String(50), nullable=False)  # bid_adjustment, campaign_pause, budget_reallocation
    service = Column(String(50), nullable=False)  # acos_service, campaign_automation, discount_scheduler
    campaign_id = Column(String(100))
    
    # Action data
    before_state = Column(JSON)
    after_state = Column(JSON)
    parameters = Column(JSON)
    
    # Status
    status = Column(String(20), default="pending")  # pending, executed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    strategy = relationship("StrategicMode")