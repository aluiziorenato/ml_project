from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.models.schemas import (
    StrategicModeCreate, StrategicModeUpdate, StrategicModeResponse,
    StrategyConfigurationCreate, StrategyConfigurationUpdate, StrategyConfigurationResponse,
    StrategyApplicationRequest, StrategyApplicationResponse
)
from src.services.strategy_service import StrategyService
from src.services.strategy_coordinator import StrategyCoordinator

router = APIRouter()

@router.get("/", response_model=List[StrategicModeResponse])
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all available strategies"""
    strategy_service = StrategyService(db)
    return strategy_service.get_strategies(skip=skip, limit=limit)

@router.get("/{strategy_id}", response_model=StrategicModeResponse)
async def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific strategy by ID"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    return strategy

@router.post("/", response_model=StrategicModeResponse)
async def create_strategy(
    strategy: StrategicModeCreate,
    db: Session = Depends(get_db)
):
    """Create a new strategy"""
    strategy_service = StrategyService(db)
    try:
        return strategy_service.create_strategy(strategy)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{strategy_id}", response_model=StrategicModeResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategicModeUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing strategy"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.update_strategy(strategy_id, strategy_update)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    return strategy

@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Delete a strategy"""
    strategy_service = StrategyService(db)
    success = strategy_service.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    return {"message": "Strategy deleted successfully"}

@router.post("/apply", response_model=StrategyApplicationResponse)
async def apply_strategy(
    application: StrategyApplicationRequest,
    db: Session = Depends(get_db)
):
    """Apply a strategy to user's campaigns"""
    coordinator = StrategyCoordinator()
    try:
        return await coordinator.apply_strategy(application, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply strategy: {str(e)}"
        )

@router.get("/users/{user_id}/configuration", response_model=StrategyConfigurationResponse)
async def get_user_strategy_configuration(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's current strategy configuration"""
    strategy_service = StrategyService(db)
    config = strategy_service.get_user_configuration(user_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User configuration not found"
        )
    return config

@router.post("/users/{user_id}/configuration", response_model=StrategyConfigurationResponse)
async def create_user_strategy_configuration(
    user_id: int,
    config: StrategyConfigurationCreate,
    db: Session = Depends(get_db)
):
    """Create or update user's strategy configuration"""
    if config.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID mismatch"
        )
    
    strategy_service = StrategyService(db)
    try:
        return strategy_service.create_user_configuration(config)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/users/{user_id}/configuration", response_model=StrategyConfigurationResponse)
async def update_user_strategy_configuration(
    user_id: int,
    config_update: StrategyConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Update user's strategy configuration"""
    strategy_service = StrategyService(db)
    config = strategy_service.update_user_configuration(user_id, config_update)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User configuration not found"
        )
    return config

@router.get("/presets/default")
async def get_default_strategies():
    """Get default strategy presets"""
    return {
        "strategies": [
            {
                "name": "Maximizar Lucro",
                "description": "Foco na maximização da margem de lucro por venda",
                "acos_min": 10,
                "acos_max": 15,
                "budget_multiplier": 0.7,
                "bid_adjustment": -20,
                "margin_threshold": 40,
                "automation_rules": {
                    "bid_adjustment": {"acos_threshold": 15, "action": "decrease", "percent": 10},
                    "campaign_pause": {"acos_threshold": 20, "action": "pause"},
                    "budget_reallocation": {"roi_threshold": 1.5, "action": "increase_budget"}
                }
            },
            {
                "name": "Escalar Vendas",
                "description": "Maximizar volume de vendas mantendo rentabilidade",
                "acos_min": 15,
                "acos_max": 25,
                "budget_multiplier": 0.85,
                "bid_adjustment": 15,
                "margin_threshold": 30,
                "automation_rules": {
                    "bid_adjustment": {"conversion_rate": 0.05, "action": "increase", "percent": 15},
                    "keyword_expansion": {"performance_score": 8, "action": "expand"},
                    "budget_increase": {"sales_growth": 0.2, "action": "increase_budget"}
                }
            },
            {
                "name": "Proteger Margem",
                "description": "Manter margem mesmo com aumento de competição",
                "acos_min": 8,
                "acos_max": 12,
                "budget_multiplier": 0.6,
                "bid_adjustment": -30,
                "margin_threshold": 45,
                "automation_rules": {
                    "competitor_monitoring": {"price_change": 0.1, "action": "adjust_bids"},
                    "campaign_pause": {"acos_threshold": 15, "action": "pause"},
                    "margin_protection": {"margin_drop": 0.25, "action": "reduce_bids"}
                }
            },
            {
                "name": "Campanhas Agressivas",
                "description": "Conquistar market share através de investimento agressivo",
                "acos_min": 25,
                "acos_max": 40,
                "budget_multiplier": 1.2,
                "bid_adjustment": 50,
                "margin_threshold": 20,
                "automation_rules": {
                    "max_bids": {"position": 3, "action": "increase_to_top"},
                    "keyword_activation": {"suggested_keywords": True, "action": "activate_all"},
                    "continuous_campaigns": {"special_dates": True, "action": "24_7_campaigns"}
                }
            }
        ]
    }