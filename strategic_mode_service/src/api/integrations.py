from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from src.core.database import get_db
from src.services.integration_service import IntegrationService

router = APIRouter()

@router.get("/status")
async def get_integration_status():
    """Get status of all integrated services"""
    integration_service = IntegrationService()
    return await integration_service.check_all_services_status()

@router.get("/acos/status")
async def get_acos_service_status():
    """Get ACOS service status"""
    integration_service = IntegrationService()
    return await integration_service.check_acos_service()

@router.get("/campaign/status")
async def get_campaign_service_status():
    """Get Campaign Automation service status"""
    integration_service = IntegrationService()
    return await integration_service.check_campaign_service()

@router.get("/discount/status")
async def get_discount_service_status():
    """Get Discount Campaign Scheduler service status"""
    integration_service = IntegrationService()
    return await integration_service.check_discount_service()

@router.post("/acos/apply-strategy")
async def apply_strategy_to_acos(
    strategy_data: Dict[str, Any],
    user_id: int,
    db: Session = Depends(get_db)
):
    """Apply strategy configuration to ACOS service"""
    integration_service = IntegrationService()
    try:
        result = await integration_service.apply_strategy_to_acos(strategy_data, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply strategy to ACOS service: {str(e)}"
        )

@router.post("/campaign/apply-strategy")
async def apply_strategy_to_campaign(
    strategy_data: Dict[str, Any],
    user_id: int,
    db: Session = Depends(get_db)
):
    """Apply strategy configuration to Campaign Automation service"""
    integration_service = IntegrationService()
    try:
        result = await integration_service.apply_strategy_to_campaign(strategy_data, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply strategy to Campaign service: {str(e)}"
        )

@router.post("/discount/apply-strategy")
async def apply_strategy_to_discount(
    strategy_data: Dict[str, Any],
    user_id: int,
    db: Session = Depends(get_db)
):
    """Apply strategy configuration to Discount Campaign Scheduler"""
    integration_service = IntegrationService()
    try:
        result = await integration_service.apply_strategy_to_discount(strategy_data, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply strategy to Discount service: {str(e)}"
        )

@router.get("/acos/campaigns/{user_id}")
async def get_acos_campaigns(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get campaigns data from ACOS service"""
    integration_service = IntegrationService()
    try:
        campaigns = await integration_service.get_acos_campaigns(user_id)
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ACOS campaigns: {str(e)}"
        )

@router.get("/campaign/automations/{user_id}")
async def get_campaign_automations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get automation data from Campaign service"""
    integration_service = IntegrationService()
    try:
        automations = await integration_service.get_campaign_automations(user_id)
        return automations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign automations: {str(e)}"
        )

@router.get("/discount/campaigns/{user_id}")
async def get_discount_campaigns(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get discount campaigns from Discount Scheduler"""
    integration_service = IntegrationService()
    try:
        campaigns = await integration_service.get_discount_campaigns(user_id)
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get discount campaigns: {str(e)}"
        )

@router.post("/sync-all")
async def sync_all_services(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Synchronize data with all integrated services"""
    integration_service = IntegrationService()
    try:
        result = await integration_service.sync_all_services(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync services: {str(e)}"
        )

@router.get("/health-check")
async def integration_health_check():
    """Comprehensive health check of all integrations"""
    integration_service = IntegrationService()
    return await integration_service.comprehensive_health_check()