from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_session
from app.models import (
    DiscountCampaign, CampaignCreate, CampaignUpdate, CampaignStatus,
    ScheduleCreate, ScheduleUpdate, CampaignSchedule,
    SuggestionResponse, MetricsResponse, PredictionResponse
)
from app.services.auth_service import get_current_user, get_current_seller
from app.services.scheduling_service import scheduling_service
from app.services.suggestions_service import suggestions_service
from app.services.metrics_service import metrics_service
from app.services.prediction_service import prediction_service
from app.services.auth_service import auth_service
from app.services.microservice_integration import microservice_integration
from app.services.keyword_service import keyword_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["Discount Campaigns"])


@router.post("/", response_model=DiscountCampaign)
async def create_campaign(
    campaign_data: CampaignCreate,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new discount campaign"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Seller ID not found")
    
    campaign = DiscountCampaign(
        seller_id=seller_id,
        item_id=campaign_data.item_id,
        campaign_name=campaign_data.campaign_name,
        discount_percentage=campaign_data.discount_percentage,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status=CampaignStatus.DRAFT
    )
    
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    logger.info(f"Created campaign {campaign.id} for seller {seller_id}")
    return campaign


@router.post("/enhanced", response_model=dict)
async def create_enhanced_campaign(
    campaign_data: CampaignCreate,
    optimize_copy: bool = Query(True, description="Apply AI copy optimization using keywords"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new discount campaign with AI optimization and microservice integration"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Seller ID not found")
    
    try:
        # Get available keywords for this seller
        keywords = keyword_service.get_keywords_for_seller(seller_id, session)
        keyword_strings = [k.keyword for k in keywords[:10]]  # Use top 10 keywords
        
        # Prepare campaign base data
        campaign_base_data = {
            "seller_id": seller_id,
            "item_id": campaign_data.item_id,
            "campaign_name": campaign_data.campaign_name,
            "discount_percentage": campaign_data.discount_percentage,
            "start_date": campaign_data.start_date.isoformat() if campaign_data.start_date else None,
            "end_date": campaign_data.end_date.isoformat() if campaign_data.end_date else None,
            "title": getattr(campaign_data, 'title', ''),
            "description": getattr(campaign_data, 'description', ''),
            "category": getattr(campaign_data, 'category', '')
        }
        
        # Orchestrate campaign creation with microservices
        orchestration_result = await microservice_integration.orchestrate_campaign_creation(
            campaign_base_data=campaign_base_data,
            keywords=keyword_strings,
            seller_id=seller_id
        )
        
        # Create the campaign in database
        campaign = DiscountCampaign(
            seller_id=seller_id,
            item_id=campaign_data.item_id,
            campaign_name=campaign_data.campaign_name,
            discount_percentage=campaign_data.discount_percentage,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            status=CampaignStatus.DRAFT
        )
        
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        
        # Return comprehensive result
        result = {
            "campaign": {
                "id": campaign.id,
                "seller_id": campaign.seller_id,
                "item_id": campaign.item_id,
                "campaign_name": campaign.campaign_name,
                "discount_percentage": campaign.discount_percentage,
                "status": campaign.status,
                "created_at": campaign.created_at
            },
            "orchestration_result": orchestration_result,
            "keywords_used": keyword_strings,
            "enhancement_summary": {
                "copy_optimized": orchestration_result.get("optimization_applied", False),
                "performance_predicted": orchestration_result.get("performance_predicted", False),
                "scheduling_configured": orchestration_result.get("scheduling_configured", False),
                "subperformance_analyzed": "subperformance_analysis" in orchestration_result
            }
        }
        
        logger.info(f"Created enhanced campaign {campaign.id} for seller {seller_id} with AI optimization")
        return result
        
    except Exception as e:
        logger.error(f"Error creating enhanced campaign: {e}")
        raise HTTPException(status_code=500, detail="Error creating enhanced campaign")


@router.get("/", response_model=List[DiscountCampaign])
async def list_campaigns(
    seller_id: str = Depends(get_current_seller),
    status: Optional[CampaignStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """List campaigns for the authenticated seller"""
    from sqlmodel import select
    
    statement = select(DiscountCampaign).where(DiscountCampaign.seller_id == seller_id)
    
    if status:
        statement = statement.where(DiscountCampaign.status == status)
    
    statement = statement.offset(skip).limit(limit).order_by(DiscountCampaign.created_at.desc())
    
    campaigns = session.exec(statement).all()
    return campaigns


@router.get("/{campaign_id}", response_model=DiscountCampaign)
async def get_campaign(
    campaign_id: int,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get a specific campaign"""
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return campaign


@router.put("/{campaign_id}", response_model=DiscountCampaign)
async def update_campaign(
    campaign_id: int,
    update_data: CampaignUpdate,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Update a campaign"""
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Delete a campaign"""
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    session.delete(campaign)
    session.commit()
    
    return {"message": "Campaign deleted successfully"}


# Schedule Management Routes

@router.post("/{campaign_id}/schedules", response_model=CampaignSchedule)
async def create_schedule(
    campaign_id: int,
    schedule_data: ScheduleCreate,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Create a schedule for a campaign"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    schedule = scheduling_service.create_schedule(
        session=session,
        campaign_id=campaign_id,
        schedule_data=schedule_data.model_dump()
    )
    
    return schedule


@router.get("/{campaign_id}/schedules", response_model=List[CampaignSchedule])
async def list_schedules(
    campaign_id: int,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """List schedules for a campaign"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    schedules = scheduling_service.get_campaign_schedules(session, campaign_id)
    return schedules


@router.put("/{campaign_id}/schedules/{schedule_id}", response_model=CampaignSchedule)
async def update_schedule(
    campaign_id: int,
    schedule_id: int,
    update_data: ScheduleUpdate,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Update a campaign schedule"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    schedule = scheduling_service.update_schedule(
        session=session,
        schedule_id=schedule_id,
        update_data=update_data.model_dump(exclude_unset=True)
    )
    
    return schedule


@router.delete("/{campaign_id}/schedules/{schedule_id}")
async def delete_schedule(
    campaign_id: int,
    schedule_id: int,
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Delete a campaign schedule"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = scheduling_service.delete_schedule(session, schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"message": "Schedule deleted successfully"}


# Metrics Routes

@router.get("/{campaign_id}/metrics", response_model=List[MetricsResponse])
async def get_campaign_metrics(
    campaign_id: int,
    days: int = Query(30, ge=1, le=365),
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get metrics for a campaign"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    metrics = metrics_service.get_campaign_metrics(session, campaign_id, days)
    return metrics


@router.post("/{campaign_id}/metrics/collect")
async def collect_campaign_metrics(
    campaign_id: int,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Manually trigger metrics collection for a campaign"""
    seller_id = user.get("seller_id")
    
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get access token
    access_token = await auth_service.get_seller_access_token(seller_id)
    if not access_token:
        raise HTTPException(status_code=400, detail="Could not get access token")
    
    try:
        metric = await metrics_service.collect_campaign_metrics(
            session=session,
            campaign_id=campaign_id,
            access_token=access_token
        )
        return {"message": "Metrics collected successfully", "metric_id": metric.id}
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        raise HTTPException(status_code=500, detail="Error collecting metrics")


# Prediction Routes

@router.get("/{campaign_id}/prediction", response_model=PredictionResponse)
async def get_performance_prediction(
    campaign_id: int,
    days: int = Query(30, ge=1, le=90),
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get performance prediction for a campaign"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    prediction = prediction_service.generate_performance_prediction(
        session=session,
        campaign_id=campaign_id,
        prediction_days=days
    )
    
    return prediction


@router.get("/{campaign_id}/prediction/comparison")
async def get_prediction_comparison(
    campaign_id: int,
    days_back: int = Query(30, ge=1, le=90),
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Compare predictions vs actual performance"""
    # Verify campaign ownership
    campaign = session.get(DiscountCampaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comparison = prediction_service.compare_prediction_vs_actual(
        session=session,
        campaign_id=campaign_id,
        days_back=days_back
    )
    
    return comparison