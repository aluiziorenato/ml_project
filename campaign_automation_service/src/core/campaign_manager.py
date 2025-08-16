"""Campaign management core functionality."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from ..models.campaign_models import (
    Campaign, CampaignMetric, CampaignCreate, CampaignUpdate, 
    CampaignResponse, CampaignStatus, MetricsSummary
)
from ..utils.logger import logger, log_error


class CampaignManager:
    """Core campaign management functionality."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_campaign(self, campaign_data: CampaignCreate, user_id: str) -> CampaignResponse:
        """Create a new campaign."""
        try:
            # Create campaign instance
            campaign = Campaign(
                name=campaign_data.name,
                description=campaign_data.description,
                campaign_type=campaign_data.campaign_type.value,
                optimization_goal=campaign_data.optimization_goal.value,
                daily_budget=campaign_data.daily_budget,
                total_budget=campaign_data.total_budget,
                max_cpc=campaign_data.max_cpc,
                target_cpa=campaign_data.target_cpa,
                target_audience=campaign_data.target_audience or {},
                keywords=campaign_data.keywords or [],
                categories=campaign_data.categories or [],
                locations=campaign_data.locations or [],
                start_date=campaign_data.start_date,
                end_date=campaign_data.end_date,
                created_by=user_id
            )
            
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            
            logger.info("Campaign created", campaign_id=campaign.id, name=campaign.name)
            
            return self._to_response_model(campaign)
            
        except Exception as e:
            self.db.rollback()
            log_error(e, {"action": "create_campaign", "user_id": user_id})
            raise
    
    async def get_campaign(self, campaign_id: int) -> Optional[CampaignResponse]:
        """Get campaign by ID."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return None
            
            return self._to_response_model(campaign)
            
        except Exception as e:
            log_error(e, {"action": "get_campaign", "campaign_id": campaign_id})
            raise
    
    async def list_campaigns(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[CampaignStatus] = None,
        user_id: Optional[str] = None
    ) -> List[CampaignResponse]:
        """List campaigns with filters."""
        try:
            query = self.db.query(Campaign)
            
            if status:
                query = query.filter(Campaign.status == status.value)
            
            if user_id:
                query = query.filter(Campaign.created_by == user_id)
            
            campaigns = query.offset(skip).limit(limit).all()
            
            return [self._to_response_model(campaign) for campaign in campaigns]
            
        except Exception as e:
            log_error(e, {"action": "list_campaigns", "skip": skip, "limit": limit})
            raise
    
    async def update_campaign(
        self, 
        campaign_id: int, 
        campaign_data: CampaignUpdate,
        user_id: str
    ) -> Optional[CampaignResponse]:
        """Update campaign."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return None
            
            # Update only provided fields
            update_data = campaign_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(campaign, field):
                    setattr(campaign, field, value)
            
            campaign.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(campaign)
            
            logger.info("Campaign updated", campaign_id=campaign.id, user_id=user_id)
            
            return self._to_response_model(campaign)
            
        except Exception as e:
            self.db.rollback()
            log_error(e, {"action": "update_campaign", "campaign_id": campaign_id})
            raise
    
    async def delete_campaign(self, campaign_id: int, user_id: str) -> bool:
        """Delete campaign (soft delete by setting status)."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return False
            
            campaign.status = CampaignStatus.CANCELLED.value
            campaign.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info("Campaign deleted", campaign_id=campaign.id, user_id=user_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            log_error(e, {"action": "delete_campaign", "campaign_id": campaign_id})
            raise
    
    async def activate_campaign(self, campaign_id: int, user_id: str) -> Optional[CampaignResponse]:
        """Activate a campaign."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return None
            
            # Validate campaign before activation
            if not self._validate_campaign_for_activation(campaign):
                raise ValueError("Campaign validation failed")
            
            campaign.status = CampaignStatus.ACTIVE.value
            campaign.updated_at = datetime.utcnow()
            
            # Set start date if not set
            if not campaign.start_date:
                campaign.start_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(campaign)
            
            logger.info("Campaign activated", campaign_id=campaign.id, user_id=user_id)
            
            return self._to_response_model(campaign)
            
        except Exception as e:
            self.db.rollback()
            log_error(e, {"action": "activate_campaign", "campaign_id": campaign_id})
            raise
    
    async def pause_campaign(self, campaign_id: int, user_id: str) -> Optional[CampaignResponse]:
        """Pause a campaign."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return None
            
            campaign.status = CampaignStatus.PAUSED.value
            campaign.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(campaign)
            
            logger.info("Campaign paused", campaign_id=campaign.id, user_id=user_id)
            
            return self._to_response_model(campaign)
            
        except Exception as e:
            self.db.rollback()
            log_error(e, {"action": "pause_campaign", "campaign_id": campaign_id})
            raise
    
    async def get_campaign_performance(self, campaign_id: int) -> Optional[MetricsSummary]:
        """Get campaign performance summary."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return None
            
            # Calculate metrics from campaign_metrics table
            metrics = self.db.query(
                func.sum(CampaignMetric.impressions).label("total_impressions"),
                func.sum(CampaignMetric.clicks).label("total_clicks"),
                func.sum(CampaignMetric.conversions).label("total_conversions"),
                func.sum(CampaignMetric.cost).label("total_cost"),
                func.sum(CampaignMetric.revenue).label("total_revenue"),
                func.avg(CampaignMetric.ctr).label("avg_ctr"),
                func.avg(CampaignMetric.cpc).label("avg_cpc"),
                func.avg(CampaignMetric.cpa).label("avg_cpa")
            ).filter(CampaignMetric.campaign_id == campaign_id).first()
            
            if not metrics or not metrics.total_impressions:
                # Return zeros if no metrics
                return MetricsSummary(
                    campaign_id=campaign_id,
                    total_impressions=0,
                    total_clicks=0,
                    total_conversions=0,
                    total_cost=0.0,
                    total_revenue=0.0,
                    avg_ctr=0.0,
                    avg_cpc=0.0,
                    avg_cpa=0.0,
                    roas=0.0,
                    roi=0.0
                )
            
            # Calculate ROAS and ROI
            roas = metrics.total_revenue / metrics.total_cost if metrics.total_cost > 0 else 0.0
            roi = ((metrics.total_revenue - metrics.total_cost) / metrics.total_cost * 100) if metrics.total_cost > 0 else 0.0
            
            return MetricsSummary(
                campaign_id=campaign_id,
                total_impressions=metrics.total_impressions or 0,
                total_clicks=metrics.total_clicks or 0,
                total_conversions=metrics.total_conversions or 0,
                total_cost=metrics.total_cost or 0.0,
                total_revenue=metrics.total_revenue or 0.0,
                avg_ctr=metrics.avg_ctr or 0.0,
                avg_cpc=metrics.avg_cpc or 0.0,
                avg_cpa=metrics.avg_cpa or 0.0,
                roas=roas,
                roi=roi
            )
            
        except Exception as e:
            log_error(e, {"action": "get_campaign_performance", "campaign_id": campaign_id})
            raise
    
    def _validate_campaign_for_activation(self, campaign: Campaign) -> bool:
        """Validate campaign is ready for activation."""
        if not campaign.name or len(campaign.name.strip()) == 0:
            return False
        
        if not campaign.daily_budget or campaign.daily_budget <= 0:
            return False
        
        if not campaign.keywords and not campaign.target_audience:
            return False
        
        return True
    
    def _to_response_model(self, campaign: Campaign) -> CampaignResponse:
        """Convert Campaign DB model to response model."""
        # Calculate basic metrics
        ctr = (campaign.clicks / campaign.impressions * 100) if campaign.impressions > 0 else 0.0
        cpc = (campaign.cost / campaign.clicks) if campaign.clicks > 0 else 0.0
        roas = (campaign.revenue / campaign.cost) if campaign.cost > 0 else 0.0
        roi = ((campaign.revenue - campaign.cost) / campaign.cost * 100) if campaign.cost > 0 else 0.0
        
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            campaign_type=campaign.campaign_type,
            optimization_goal=campaign.optimization_goal,
            status=campaign.status,
            daily_budget=campaign.daily_budget,
            total_budget=campaign.total_budget,
            max_cpc=campaign.max_cpc,
            target_cpa=campaign.target_cpa,
            target_audience=campaign.target_audience or {},
            keywords=campaign.keywords or [],
            categories=campaign.categories or [],
            locations=campaign.locations or [],
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            impressions=campaign.impressions,
            clicks=campaign.clicks,
            conversions=campaign.conversions,
            cost=campaign.cost,
            revenue=campaign.revenue,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            ctr=round(ctr, 2),
            cpc=round(cpc, 2),
            roas=round(roas, 2),
            roi=round(roi, 2)
        )