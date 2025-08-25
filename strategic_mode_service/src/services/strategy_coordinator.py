from sqlalchemy.orm import Session
from typing import Dict, Any
from src.models.schemas import (
    StrategyApplicationRequest, StrategyApplicationResponse,
    AutomationActionCreate, StrategyAlertCreate
)
from src.services.strategy_service import StrategyService
from src.services.integration_service import IntegrationService
import logging

logger = logging.getLogger(__name__)

class StrategyCoordinator:
    """Coordinates strategy application across all services"""
    
    def __init__(self):
        self.integration_service = IntegrationService()
    
    async def apply_strategy(self, application: StrategyApplicationRequest, db: Session) -> StrategyApplicationResponse:
        """Apply a strategy to all relevant services"""
        try:
            strategy_service = StrategyService(db)
            strategy = strategy_service.get_strategy(application.strategy_id)
            
            if not strategy:
                raise ValueError(f"Strategy {application.strategy_id} not found")
            
            if application.simulate_only:
                return await self._simulate_strategy_application(strategy, application, db)
            
            # Apply strategy to all services
            results = await self._apply_to_all_services(strategy, application, db)
            
            return StrategyApplicationResponse(
                success=True,
                message=f"Strategy '{strategy.name}' applied successfully",
                actions_performed=results.get("actions", []),
                alerts_generated=results.get("alerts", []),
                estimated_impact=results.get("impact", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to apply strategy: {e}")
            return StrategyApplicationResponse(
                success=False,
                message=f"Failed to apply strategy: {str(e)}",
                actions_performed=[],
                alerts_generated=[],
                estimated_impact={}
            )
    
    async def _apply_to_all_services(self, strategy, application: StrategyApplicationRequest, db: Session) -> Dict[str, Any]:
        """Apply strategy to all integrated services"""
        strategy_data = {
            "id": strategy.id,
            "name": strategy.name,
            "acos_min": float(strategy.acos_min),
            "acos_max": float(strategy.acos_max),
            "budget_multiplier": float(strategy.budget_multiplier),
            "bid_adjustment": float(strategy.bid_adjustment),
            "margin_threshold": float(strategy.margin_threshold),
            "automation_rules": strategy.automation_rules or {},
            "alert_thresholds": strategy.alert_thresholds or {}
        }
        
        # Apply to ACOS service
        acos_result = await self.integration_service.apply_strategy_to_acos(
            strategy_data, application.user_id
        )
        
        # Apply to Campaign service
        campaign_result = await self.integration_service.apply_strategy_to_campaign(
            strategy_data, application.user_id
        )
        
        # Apply to Discount service
        discount_result = await self.integration_service.apply_strategy_to_discount(
            strategy_data, application.user_id
        )
        
        # Log results and create action records
        actions = []
        alerts = []
        
        if acos_result.get("success"):
            logger.info(f"Strategy applied to ACOS service for user {application.user_id}")
        else:
            logger.error(f"Failed to apply strategy to ACOS service: {acos_result.get('error')}")
        
        if campaign_result.get("success"):
            logger.info(f"Strategy applied to Campaign service for user {application.user_id}")
        else:
            logger.error(f"Failed to apply strategy to Campaign service: {campaign_result.get('error')}")
        
        if discount_result.get("success"):
            logger.info(f"Strategy applied to Discount service for user {application.user_id}")
        else:
            logger.error(f"Failed to apply strategy to Discount service: {discount_result.get('error')}")
        
        return {
            "actions": actions,
            "alerts": alerts,
            "impact": {
                "acos_service": acos_result,
                "campaign_service": campaign_result,
                "discount_service": discount_result
            }
        }
    
    async def _simulate_strategy_application(self, strategy, application: StrategyApplicationRequest, db: Session) -> StrategyApplicationResponse:
        """Simulate strategy application without actually applying it"""
        estimated_impact = {
            "estimated_acos_change": f"{strategy.acos_min}% - {strategy.acos_max}%",
            "estimated_budget_change": f"{(float(strategy.budget_multiplier) - 1) * 100:+.1f}%",
            "estimated_bid_change": f"{float(strategy.bid_adjustment):+.1f}%",
            "margin_protection": f"Campaigns paused if margin < {strategy.margin_threshold}%",
            "automation_rules": len(strategy.automation_rules or {}),
            "alert_thresholds": len(strategy.alert_thresholds or {})
        }
        
        return StrategyApplicationResponse(
            success=True,
            message=f"Strategy simulation completed for '{strategy.name}'",
            actions_performed=[],
            alerts_generated=[],
            estimated_impact=estimated_impact
        )