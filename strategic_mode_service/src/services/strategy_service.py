from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.database import StrategicMode, StrategyConfiguration
from src.models.schemas import (
    StrategicModeCreate, StrategicModeUpdate, StrategicModeResponse,
    StrategyConfigurationCreate, StrategyConfigurationUpdate, StrategyConfigurationResponse
)

class StrategyService:
    """Service for managing strategic modes and configurations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_strategies(self, skip: int = 0, limit: int = 100) -> List[StrategicModeResponse]:
        """Get all strategies with pagination"""
        strategies = self.db.query(StrategicMode).offset(skip).limit(limit).all()
        return [StrategicModeResponse.from_orm(strategy) for strategy in strategies]
    
    def get_strategy(self, strategy_id: int) -> Optional[StrategicModeResponse]:
        """Get a specific strategy by ID"""
        strategy = self.db.query(StrategicMode).filter(StrategicMode.id == strategy_id).first()
        return StrategicModeResponse.from_orm(strategy) if strategy else None
    
    def create_strategy(self, strategy: StrategicModeCreate) -> StrategicModeResponse:
        """Create a new strategic mode"""
        # Check if strategy name already exists
        existing = self.db.query(StrategicMode).filter(StrategicMode.name == strategy.name).first()
        if existing:
            raise ValueError(f"Strategy with name '{strategy.name}' already exists")
        
        db_strategy = StrategicMode(**strategy.model_dump())
        self.db.add(db_strategy)
        self.db.commit()
        self.db.refresh(db_strategy)
        
        return StrategicModeResponse.from_orm(db_strategy)
    
    def update_strategy(self, strategy_id: int, strategy_update: StrategicModeUpdate) -> Optional[StrategicModeResponse]:
        """Update an existing strategy"""
        strategy = self.db.query(StrategicMode).filter(StrategicMode.id == strategy_id).first()
        if not strategy:
            return None
        
        update_data = strategy_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)
        
        self.db.commit()
        self.db.refresh(strategy)
        
        return StrategicModeResponse.from_orm(strategy)
    
    def delete_strategy(self, strategy_id: int) -> bool:
        """Delete a strategy"""
        strategy = self.db.query(StrategicMode).filter(StrategicMode.id == strategy_id).first()
        if not strategy:
            return False
        
        self.db.delete(strategy)
        self.db.commit()
        return True
    
    def get_user_configuration(self, user_id: int) -> Optional[StrategyConfigurationResponse]:
        """Get user's current strategy configuration"""
        config = self.db.query(StrategyConfiguration).filter(
            StrategyConfiguration.user_id == user_id,
            StrategyConfiguration.is_active == True
        ).first()
        
        return StrategyConfigurationResponse.from_orm(config) if config else None
    
    def create_user_configuration(self, config: StrategyConfigurationCreate) -> StrategyConfigurationResponse:
        """Create or update user's strategy configuration"""
        # Deactivate any existing active configuration
        existing_configs = self.db.query(StrategyConfiguration).filter(
            StrategyConfiguration.user_id == config.user_id,
            StrategyConfiguration.is_active == True
        ).all()
        
        for existing_config in existing_configs:
            existing_config.is_active = False
        
        # Create new configuration
        db_config = StrategyConfiguration(**config.model_dump())
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        return StrategyConfigurationResponse.from_orm(db_config)
    
    def update_user_configuration(self, user_id: int, config_update: StrategyConfigurationUpdate) -> Optional[StrategyConfigurationResponse]:
        """Update user's strategy configuration"""
        config = self.db.query(StrategyConfiguration).filter(
            StrategyConfiguration.user_id == user_id,
            StrategyConfiguration.is_active == True
        ).first()
        
        if not config:
            return None
        
        update_data = config_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        self.db.commit()
        self.db.refresh(config)
        
        return StrategyConfigurationResponse.from_orm(config)
    
    def get_strategy_by_name(self, name: str) -> Optional[StrategicModeResponse]:
        """Get strategy by name"""
        strategy = self.db.query(StrategicMode).filter(StrategicMode.name == name).first()
        return StrategicModeResponse.from_orm(strategy) if strategy else None