import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import Session, select
from app.models import (
    DiscountCampaign, CampaignMetric, CampaignStatus,
    MetricsResponse
)
from app.services.ml_api_service import ml_api_service

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for collecting and analyzing campaign metrics"""
    
    async def collect_campaign_metrics(self, session: Session, campaign_id: int, access_token: str) -> CampaignMetric:
        """Collect metrics for a specific campaign"""
        campaign = session.get(DiscountCampaign, campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Get item visit data from ML API
        period_days = 1  # Collect daily metrics
        visits_data = await ml_api_service.get_item_visits(
            access_token=access_token,
            item_id=campaign.item_id,
            period_days=period_days
        )
        
        # Calculate metrics from visits data
        metrics_data = self._process_visits_data(visits_data)
        
        # Create new metric record
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)
        
        metric = CampaignMetric(
            campaign_id=campaign_id,
            clicks=metrics_data.get("clicks", 0),
            impressions=metrics_data.get("impressions", 0),
            conversions=metrics_data.get("conversions", 0),
            conversion_rate=metrics_data.get("conversion_rate", 0.0),
            sales_amount=metrics_data.get("sales_amount", 0.0),
            engagement_score=metrics_data.get("engagement_score"),
            performance_index=metrics_data.get("performance_index"),
            period_start=period_start,
            period_end=period_end
        )
        
        session.add(metric)
        
        # Update campaign totals
        self._update_campaign_totals(session, campaign, metric)
        
        session.commit()
        session.refresh(metric)
        
        logger.info(f"Collected metrics for campaign {campaign_id}")
        return metric
    
    def _process_visits_data(self, visits_data: Dict) -> Dict:
        """Process raw visits data into metrics"""
        # Extract metrics from ML API response
        total_visits = visits_data.get("total_visits", 0)
        unique_visits = visits_data.get("unique_visits", 0)
        
        # Calculate derived metrics
        clicks = total_visits
        impressions = unique_visits * 2  # Estimate impressions
        conversions = int(clicks * 0.02)  # Estimate 2% conversion rate
        conversion_rate = conversions / clicks if clicks > 0 else 0.0
        sales_amount = conversions * 50.0  # Estimate $50 per conversion
        
        # Calculate engagement score (0-1 scale)
        engagement_score = min(1.0, (clicks + unique_visits) / 1000.0)
        
        # Calculate performance index (combination of metrics)
        performance_index = (conversion_rate * 0.5) + (engagement_score * 0.3) + min(1.0, sales_amount / 1000.0) * 0.2
        
        return {
            "clicks": clicks,
            "impressions": impressions,
            "conversions": conversions,
            "conversion_rate": conversion_rate,
            "sales_amount": sales_amount,
            "engagement_score": engagement_score,
            "performance_index": performance_index
        }
    
    def _update_campaign_totals(self, session: Session, campaign: DiscountCampaign, metric: CampaignMetric):
        """Update campaign total metrics"""
        campaign.total_clicks += metric.clicks
        campaign.total_impressions += metric.impressions
        campaign.total_conversions += metric.conversions
        campaign.total_sales_amount += metric.sales_amount
        campaign.updated_at = datetime.utcnow()
        
        session.add(campaign)
    
    async def collect_all_active_campaign_metrics(self, session: Session) -> List[CampaignMetric]:
        """Collect metrics for all active campaigns"""
        # Get all active campaigns
        statement = select(DiscountCampaign).where(
            DiscountCampaign.status == CampaignStatus.ACTIVE
        )
        active_campaigns = session.exec(statement).all()
        
        collected_metrics = []
        
        for campaign in active_campaigns:
            try:
                # Get access token for seller
                access_token = await self._get_seller_access_token(campaign.seller_id)
                if not access_token:
                    logger.warning(f"No access token for seller {campaign.seller_id}")
                    continue
                
                metric = await self.collect_campaign_metrics(
                    session=session,
                    campaign_id=campaign.id,
                    access_token=access_token
                )
                collected_metrics.append(metric)
                
            except Exception as e:
                logger.error(f"Error collecting metrics for campaign {campaign.id}: {e}")
        
        return collected_metrics
    
    def get_campaign_metrics(
        self, 
        session: Session, 
        campaign_id: int, 
        days: int = 30
    ) -> List[MetricsResponse]:
        """Get metrics for a campaign over specified period"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        statement = select(CampaignMetric).where(
            CampaignMetric.campaign_id == campaign_id,
            CampaignMetric.period_start >= start_date
        ).order_by(CampaignMetric.period_start)
        
        metrics = session.exec(statement).all()
        
        return [
            MetricsResponse(
                campaign_id=metric.campaign_id,
                clicks=metric.clicks,
                impressions=metric.impressions,
                conversions=metric.conversions,
                conversion_rate=metric.conversion_rate,
                sales_amount=metric.sales_amount,
                period_start=metric.period_start,
                period_end=metric.period_end
            )
            for metric in metrics
        ]
    
    def get_aggregated_metrics(
        self, 
        session: Session, 
        seller_id: str, 
        days: int = 30
    ) -> Dict:
        """Get aggregated metrics for all seller campaigns"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all campaigns for seller
        campaigns_statement = select(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id
        )
        campaigns = session.exec(campaigns_statement).all()
        campaign_ids = [c.id for c in campaigns]
        
        if not campaign_ids:
            return self._empty_aggregated_metrics()
        
        # Get metrics for all campaigns
        metrics_statement = select(CampaignMetric).where(
            CampaignMetric.campaign_id.in_(campaign_ids),
            CampaignMetric.period_start >= start_date
        )
        metrics = session.exec(metrics_statement).all()
        
        # Aggregate metrics
        total_clicks = sum(m.clicks for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_sales = sum(m.sales_amount for m in metrics)
        
        avg_conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0.0
        avg_engagement_score = sum(m.engagement_score or 0 for m in metrics) / len(metrics) if metrics else 0.0
        
        return {
            "total_campaigns": len(campaigns),
            "active_campaigns": len([c for c in campaigns if c.status == CampaignStatus.ACTIVE]),
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_conversions": total_conversions,
            "total_sales": total_sales,
            "avg_conversion_rate": avg_conversion_rate,
            "avg_engagement_score": avg_engagement_score,
            "period_start": start_date,
            "period_end": end_date
        }
    
    def _empty_aggregated_metrics(self) -> Dict:
        """Return empty aggregated metrics"""
        return {
            "total_campaigns": 0,
            "active_campaigns": 0,
            "total_clicks": 0,
            "total_impressions": 0,
            "total_conversions": 0,
            "total_sales": 0.0,
            "avg_conversion_rate": 0.0,
            "avg_engagement_score": 0.0,
            "period_start": datetime.utcnow(),
            "period_end": datetime.utcnow()
        }
    
    async def _get_seller_access_token(self, seller_id: str) -> Optional[str]:
        """Get access token for seller (placeholder - integrate with auth system)"""
        # TODO: Integrate with the main backend auth system
        # For now, return a mock token
        return "mock_access_token"
    
    def calculate_performance_trends(
        self, 
        session: Session, 
        campaign_id: int, 
        days: int = 30
    ) -> Dict:
        """Calculate performance trends for a campaign"""
        metrics = self.get_campaign_metrics(session, campaign_id, days)
        
        if len(metrics) < 2:
            return {"trend": "insufficient_data", "change_percentage": 0.0}
        
        # Calculate trends in key metrics
        recent_metrics = metrics[-7:]  # Last 7 days
        older_metrics = metrics[-14:-7] if len(metrics) >= 14 else metrics[:-7]
        
        if not older_metrics:
            return {"trend": "insufficient_data", "change_percentage": 0.0}
        
        recent_avg_conversion_rate = sum(m.conversion_rate for m in recent_metrics) / len(recent_metrics)
        older_avg_conversion_rate = sum(m.conversion_rate for m in older_metrics) / len(older_metrics)
        
        if older_avg_conversion_rate > 0:
            change_percentage = ((recent_avg_conversion_rate - older_avg_conversion_rate) / older_avg_conversion_rate) * 100
        else:
            change_percentage = 0.0
        
        trend = "improving" if change_percentage > 5 else "declining" if change_percentage < -5 else "stable"
        
        return {
            "trend": trend,
            "change_percentage": change_percentage,
            "recent_avg_conversion_rate": recent_avg_conversion_rate,
            "older_avg_conversion_rate": older_avg_conversion_rate
        }


# Global instance
metrics_service = MetricsService()