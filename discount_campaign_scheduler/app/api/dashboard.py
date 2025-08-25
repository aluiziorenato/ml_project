from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Dict, List
from datetime import datetime, timedelta
from app.core.database import get_session
from app.services.auth_service import get_current_seller, get_current_user, auth_service
from app.services.metrics_service import metrics_service
from app.services.scheduling_service import scheduling_service
from app.services.keyword_service import keyword_service
from app.models import Keyword, KeywordUploadBatch, DiscountCampaign, CampaignStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@router.get("/overview")
async def get_dashboard_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days for metrics"),
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get comprehensive dashboard overview with campaigns, keywords, and metrics"""
    try:
        # Get aggregated metrics
        aggregated_metrics = metrics_service.get_aggregated_metrics(
            session=session,
            seller_id=seller_id,
            days=days
        )
        
        # Get campaign statistics
        campaigns_statement = select(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id
        )
        all_campaigns = session.exec(campaigns_statement).all()
        
        campaign_stats = {
            "total_campaigns": len(all_campaigns),
            "active_campaigns": len([c for c in all_campaigns if c.status == CampaignStatus.ACTIVE]),
            "scheduled_campaigns": len([c for c in all_campaigns if c.status == CampaignStatus.SCHEDULED]),
            "completed_campaigns": len([c for c in all_campaigns if c.status == CampaignStatus.EXPIRED])
        }
        
        # Get recent campaign activity (last 5)
        recent_campaigns_statement = select(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id
        ).order_by(DiscountCampaign.updated_at.desc()).limit(5)
        recent_campaigns = session.exec(recent_campaigns_statement).all()
        
        # Get active campaigns with performance data
        active_campaigns_statement = select(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id,
            DiscountCampaign.status == CampaignStatus.ACTIVE
        )
        active_campaigns = session.exec(active_campaigns_statement).all()
        
        active_campaigns_data = []
        for campaign in active_campaigns:
            # Get latest metrics
            metrics = metrics_service.get_campaign_metrics(session, campaign.id, 7)
            latest_metric = metrics[-1] if metrics else None
            
            active_campaigns_data.append({
                "id": campaign.id,
                "campaign_name": campaign.campaign_name,
                "item_id": campaign.item_id,
                "discount_percentage": campaign.discount_percentage,
                "total_clicks": campaign.total_clicks,
                "total_conversions": campaign.total_conversions,
                "total_sales": campaign.total_sales_amount,
                "conversion_rate": (campaign.total_conversions / campaign.total_clicks) * 100 if campaign.total_clicks > 0 else 0,
                "recent_performance": {
                    "clicks": latest_metric.clicks if latest_metric else 0,
                    "conversions": latest_metric.conversions if latest_metric else 0,
                    "sales": latest_metric.sales_amount if latest_metric else 0
                } if latest_metric else None
            })
        
        # Get keyword analytics
        keywords_statement = select(Keyword).where(
            Keyword.seller_id == seller_id,
            Keyword.is_active == True
        )
        keywords = session.exec(keywords_statement).all()
        
        keyword_stats = {
            "total_keywords": len(keywords),
            "high_volume_keywords": len([k for k in keywords if k.search_volume > 1000]),
            "low_competition_keywords": len([k for k in keywords if k.competition == "Low"]),
            "avg_search_volume": sum(k.search_volume for k in keywords) / len(keywords) if keywords else 0,
            "top_keywords": [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "competition": k.competition,
                    "relevance_score": k.relevance_score
                }
                for k in sorted(keywords, key=lambda x: x.search_volume, reverse=True)[:5]
            ]
        }
        
        # Get keyword upload history
        upload_batches_statement = select(KeywordUploadBatch).where(
            KeywordUploadBatch.seller_id == seller_id
        ).order_by(KeywordUploadBatch.uploaded_at.desc()).limit(3)
        recent_uploads = session.exec(upload_batches_statement).all()
        
        upload_history = [
            {
                "batch_id": batch.id,
                "filename": batch.filename,
                "total_keywords": batch.total_keywords,
                "processed_keywords": batch.processed_keywords,
                "status": batch.status,
                "uploaded_at": batch.uploaded_at
            }
            for batch in recent_uploads
        ]
        
        # Get upcoming schedules
        from app.models import CampaignSchedule, ScheduleStatus
        
        upcoming_schedules_statement = select(CampaignSchedule).where(
            CampaignSchedule.status == ScheduleStatus.PENDING
        ).join(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id
        ).limit(10)
        
        upcoming_schedules = session.exec(upcoming_schedules_statement).all()
        
        schedules_data = [
            {
                "schedule_id": schedule.id,
                "campaign_id": schedule.campaign_id,
                "campaign_name": schedule.campaign.campaign_name if schedule.campaign else "Unknown",
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.strftime("%H:%M"),
                "action": schedule.action,
                "next_execution": schedule.next_execution
            }
            for schedule in upcoming_schedules
        ]
        
        # Generate alerts based on performance and keyword data
        alerts = []
        
        # Campaign performance alerts
        if any(c["conversion_rate"] < 1.0 for c in active_campaigns_data):
            alerts.append({
                "type": "warning",
                "category": "performance",
                "message": "Some active campaigns have low conversion rates (<1%)",
                "action_required": True
            })
        
        # Keyword alerts
        if not keywords:
            alerts.append({
                "type": "info",
                "category": "keywords",
                "message": "No keywords uploaded yet. Upload Google Keyword Planner data to enhance suggestions.",
                "action_required": True
            })
        elif len([k for k in keywords if k.search_volume > 1000]) < 5:
            alerts.append({
                "type": "info",
                "category": "keywords",
                "message": "Consider uploading more high-volume keywords for better campaign optimization.",
                "action_required": False
            })
        
        # Scheduling alerts
        if len(upcoming_schedules) == 0 and len(active_campaigns) > 0:
            alerts.append({
                "type": "info",
                "category": "scheduling",
                "message": "Active campaigns without scheduled optimization. Consider setting up automated schedules.",
                "action_required": False
            })
        
        # Performance summary with keyword enhancement
        performance_summary = {
            "period_days": days,
            "total_campaigns": len(all_campaigns),
            "keyword_enhanced_campaigns": len([c for c in all_campaigns if any(k.keyword.lower() in c.campaign_name.lower() for k in keywords)]),
            "metrics": aggregated_metrics,
            "keyword_optimization_potential": {
                "available_keywords": len(keywords),
                "campaigns_without_keywords": len(all_campaigns) - len([c for c in all_campaigns if any(k.keyword.lower() in c.campaign_name.lower() for k in keywords)]),
                "optimization_score": min(100, (len(keywords) / 50) * 100) if keywords else 0  # Score out of 50 ideal keywords
            }
        }
        
        return {
            "overview": {
                "generated_at": datetime.utcnow(),
                "period_days": days,
                "seller_id": seller_id
            },
            "campaign_stats": campaign_stats,
            "keyword_stats": keyword_stats,
            "performance_summary": performance_summary,
            "active_campaigns": active_campaigns_data,
            "recent_campaigns": [
                {
                    "id": c.id,
                    "campaign_name": c.campaign_name,
                    "status": c.status,
                    "discount_percentage": c.discount_percentage,
                    "updated_at": c.updated_at
                }
                for c in recent_campaigns
            ],
            "upload_history": upload_history,
            "upcoming_schedules": schedules_data,
            "alerts": alerts,
            "insights": {
                "keyword_integration": len(keywords) > 0,
                "active_optimization": len(active_campaigns) > 0,
                "automation_configured": len(upcoming_schedules) > 0,
                "performance_health": "good" if all(c["conversion_rate"] >= 1.0 for c in active_campaigns_data) else "needs_attention"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Error loading dashboard data")
        
        upcoming_schedules = session.exec(upcoming_schedules_statement).all()
        
        return {
            "period": {
                "days": days,
                "start_date": aggregated_metrics["period_start"],
                "end_date": aggregated_metrics["period_end"]
            },
            "summary": {
                "total_campaigns": aggregated_metrics["total_campaigns"],
                "active_campaigns": aggregated_metrics["active_campaigns"],
                "total_clicks": aggregated_metrics["total_clicks"],
                "total_impressions": aggregated_metrics["total_impressions"],
                "total_conversions": aggregated_metrics["total_conversions"],
                "total_sales": aggregated_metrics["total_sales"],
                "avg_conversion_rate": aggregated_metrics["avg_conversion_rate"] * 100,
                "avg_engagement_score": aggregated_metrics["avg_engagement_score"]
            },
            "recent_campaigns": [
                {
                    "id": campaign.id,
                    "campaign_name": campaign.campaign_name,
                    "status": campaign.status,
                    "discount_percentage": campaign.discount_percentage,
                    "updated_at": campaign.updated_at
                }
                for campaign in recent_campaigns
            ],
            "active_campaigns": active_campaigns_data,
            "upcoming_schedules": [
                {
                    "id": schedule.id,
                    "campaign_id": schedule.campaign_id,
                    "campaign_name": schedule.campaign.campaign_name,
                    "day_of_week": schedule.day_of_week,
                    "start_time": schedule.start_time.strftime("%H:%M"),
                    "action": schedule.action,
                    "next_execution": schedule.next_execution
                }
                for schedule in upcoming_schedules
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard data")


@router.get("/performance-trends")
async def get_performance_trends(
    days: int = Query(30, ge=7, le=90, description="Number of days for trend analysis"),
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get performance trends for campaigns"""
    try:
        from sqlmodel import select
        from app.models import DiscountCampaign, CampaignMetric
        
        # Get all seller campaigns
        campaigns_statement = select(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id
        )
        campaigns = session.exec(campaigns_statement).all()
        
        if not campaigns:
            return {"trends": [], "summary": {"total_campaigns": 0}}
        
        campaign_ids = [c.id for c in campaigns]
        
        # Get metrics for the specified period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        metrics_statement = select(CampaignMetric).where(
            CampaignMetric.campaign_id.in_(campaign_ids),
            CampaignMetric.period_start >= start_date
        ).order_by(CampaignMetric.period_start)
        
        metrics = session.exec(metrics_statement).all()
        
        # Group metrics by date
        daily_metrics = {}
        for metric in metrics:
            date_key = metric.period_start.date()
            if date_key not in daily_metrics:
                daily_metrics[date_key] = {
                    "date": date_key,
                    "clicks": 0,
                    "impressions": 0,
                    "conversions": 0,
                    "sales": 0.0,
                    "campaigns_count": 0
                }
            
            daily_metrics[date_key]["clicks"] += metric.clicks
            daily_metrics[date_key]["impressions"] += metric.impressions
            daily_metrics[date_key]["conversions"] += metric.conversions
            daily_metrics[date_key]["sales"] += metric.sales_amount
            daily_metrics[date_key]["campaigns_count"] += 1
        
        # Convert to list and calculate rates
        trends_data = []
        for date_key in sorted(daily_metrics.keys()):
            data = daily_metrics[date_key]
            conversion_rate = (data["conversions"] / data["clicks"]) * 100 if data["clicks"] > 0 else 0
            
            trends_data.append({
                "date": date_key.isoformat(),
                "clicks": data["clicks"],
                "impressions": data["impressions"],
                "conversions": data["conversions"],
                "sales": round(data["sales"], 2),
                "conversion_rate": round(conversion_rate, 2),
                "active_campaigns": data["campaigns_count"]
            })
        
        # Calculate summary
        total_clicks = sum(d["clicks"] for d in trends_data)
        total_conversions = sum(d["conversions"] for d in trends_data)
        total_sales = sum(d["sales"] for d in trends_data)
        
        return {
            "period": {
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "days": days
            },
            "trends": trends_data,
            "summary": {
                "total_campaigns": len(campaigns),
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "total_sales": round(total_sales, 2),
                "avg_conversion_rate": round((total_conversions / total_clicks) * 100, 2) if total_clicks > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=500, detail="Error getting trends data")


@router.get("/schedule-analysis")
async def get_schedule_analysis(
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get analysis of schedule effectiveness"""
    try:
        from sqlmodel import select
        from app.models import CampaignSchedule, DiscountCampaign, ScheduleStatus
        
        # Get all schedules for seller campaigns
        schedules_statement = select(CampaignSchedule).join(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id
        )
        schedules = session.exec(schedules_statement).all()
        
        if not schedules:
            return {
                "total_schedules": 0,
                "execution_stats": {},
                "day_analysis": {},
                "action_analysis": {}
            }
        
        # Analyze execution stats
        total_schedules = len(schedules)
        executed_schedules = len([s for s in schedules if s.status == ScheduleStatus.EXECUTED])
        failed_schedules = len([s for s in schedules if s.status == ScheduleStatus.FAILED])
        pending_schedules = len([s for s in schedules if s.status == ScheduleStatus.PENDING])
        
        # Analyze by day of week
        day_analysis = {}
        for schedule in schedules:
            day = schedule.day_of_week.value
            if day not in day_analysis:
                day_analysis[day] = {"total": 0, "executed": 0, "failed": 0, "pending": 0}
            
            day_analysis[day]["total"] += 1
            if schedule.status == ScheduleStatus.EXECUTED:
                day_analysis[day]["executed"] += 1
            elif schedule.status == ScheduleStatus.FAILED:
                day_analysis[day]["failed"] += 1
            else:
                day_analysis[day]["pending"] += 1
        
        # Analyze by action type
        action_analysis = {}
        for schedule in schedules:
            action = schedule.action
            if action not in action_analysis:
                action_analysis[action] = {"total": 0, "executed": 0, "failed": 0, "pending": 0}
            
            action_analysis[action]["total"] += 1
            if schedule.status == ScheduleStatus.EXECUTED:
                action_analysis[action]["executed"] += 1
            elif schedule.status == ScheduleStatus.FAILED:
                action_analysis[action]["failed"] += 1
            else:
                action_analysis[action]["pending"] += 1
        
        return {
            "total_schedules": total_schedules,
            "execution_stats": {
                "executed": executed_schedules,
                "failed": failed_schedules,
                "pending": pending_schedules,
                "success_rate": round((executed_schedules / total_schedules) * 100, 2) if total_schedules > 0 else 0
            },
            "day_analysis": day_analysis,
            "action_analysis": action_analysis,
            "recent_executions": [
                {
                    "id": schedule.id,
                    "campaign_id": schedule.campaign_id,
                    "action": schedule.action,
                    "day_of_week": schedule.day_of_week.value,
                    "status": schedule.status.value,
                    "last_executed": schedule.last_executed
                }
                for schedule in sorted(schedules, key=lambda x: x.last_executed or datetime.min, reverse=True)[:10]
                if schedule.last_executed
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule analysis: {e}")
        raise HTTPException(status_code=500, detail="Error getting schedule analysis")


@router.post("/trigger-schedule-check")
async def trigger_schedule_check(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Manually trigger schedule check (for testing/debugging)"""
    try:
        results = await scheduling_service.check_pending_schedules(session)
        
        return {
            "message": "Schedule check completed",
            "processed_schedules": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error triggering schedule check: {e}")
        raise HTTPException(status_code=500, detail="Error triggering schedule check")


@router.post("/collect-all-metrics")
async def collect_all_metrics(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Manually trigger metrics collection for all active campaigns"""
    try:
        collected_metrics = await metrics_service.collect_all_active_campaign_metrics(session)
        
        return {
            "message": "Metrics collection completed",
            "collected_campaigns": len(collected_metrics),
            "metrics": [
                {
                    "campaign_id": metric.campaign_id,
                    "clicks": metric.clicks,
                    "conversions": metric.conversions,
                    "sales": metric.sales_amount
                }
                for metric in collected_metrics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        raise HTTPException(status_code=500, detail="Error collecting metrics")