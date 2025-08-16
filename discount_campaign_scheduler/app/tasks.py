from celery import Celery
from celery.schedules import crontab
import logging
from app.core.config import settings
from app.core.database import get_session
from app.services.scheduling_service import scheduling_service
from app.services.metrics_service import metrics_service

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "discount_campaign_scheduler",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Check schedules every 5 minutes
    "check-campaign-schedules": {
        "task": "app.tasks.check_campaign_schedules",
        "schedule": crontab(minute=f"*/{settings.schedule_check_interval_minutes}"),
        "options": {"expires": 60}
    },
    
    # Collect metrics every hour
    "collect-campaign-metrics": {
        "task": "app.tasks.collect_campaign_metrics",
        "schedule": crontab(minute=0),  # Every hour at minute 0
        "options": {"expires": 3600}
    },
    
    # Generate suggestions daily at 6 AM
    "refresh-suggestions": {
        "task": "app.tasks.refresh_suggestions_for_all_sellers",
        "schedule": crontab(hour=6, minute=0),
        "options": {"expires": 7200}
    },
    
    # Clean up old data weekly
    "cleanup-old-data": {
        "task": "app.tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday at 2 AM
        "options": {"expires": 3600}
    }
}


@celery_app.task(name="app.tasks.check_campaign_schedules")
def check_campaign_schedules():
    """Periodic task to check and execute pending campaign schedules"""
    try:
        logger.info("Starting campaign schedules check")
        
        with next(get_session()) as session:
            results = scheduling_service.check_pending_schedules(session)
            
            logger.info(f"Schedule check completed. Processed {len(results)} schedules")
            
            return {
                "status": "success",
                "processed_schedules": len(results),
                "results": results
            }
            
    except Exception as e:
        logger.error(f"Error in schedule check task: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="app.tasks.collect_campaign_metrics")
def collect_campaign_metrics():
    """Periodic task to collect metrics for all active campaigns"""
    try:
        logger.info("Starting metrics collection for active campaigns")
        
        with next(get_session()) as session:
            collected_metrics = metrics_service.collect_all_active_campaign_metrics(session)
            
            logger.info(f"Metrics collection completed. Collected for {len(collected_metrics)} campaigns")
            
            return {
                "status": "success",
                "collected_campaigns": len(collected_metrics),
                "metrics_summary": [
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
        logger.error(f"Error in metrics collection task: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="app.tasks.refresh_suggestions_for_all_sellers")
def refresh_suggestions_for_all_sellers():
    """Periodic task to refresh suggestions for all sellers"""
    try:
        from sqlmodel import select
        from app.models import DiscountCampaign
        from app.services.suggestions_service import suggestions_service
        from app.services.auth_service import auth_service
        
        logger.info("Starting suggestions refresh for all sellers")
        
        with next(get_session()) as session:
            # Get unique seller IDs from campaigns
            statement = select(DiscountCampaign.seller_id).distinct()
            seller_ids = session.exec(statement).all()
            
            refreshed_count = 0
            errors = []
            
            for seller_id in seller_ids:
                try:
                    # Get access token for seller
                    access_token = auth_service.get_seller_access_token(seller_id)
                    if not access_token:
                        continue
                    
                    # Refresh suggestions
                    suggestions = suggestions_service.generate_suggestions(
                        session=session,
                        seller_id=seller_id,
                        access_token=access_token
                    )
                    
                    refreshed_count += 1
                    logger.info(f"Refreshed {len(suggestions)} suggestions for seller {seller_id}")
                    
                except Exception as e:
                    errors.append(f"Seller {seller_id}: {str(e)}")
                    logger.warning(f"Error refreshing suggestions for seller {seller_id}: {e}")
            
            logger.info(f"Suggestions refresh completed. Refreshed for {refreshed_count} sellers")
            
            return {
                "status": "success",
                "refreshed_sellers": refreshed_count,
                "total_sellers": len(seller_ids),
                "errors": errors
            }
            
    except Exception as e:
        logger.error(f"Error in suggestions refresh task: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="app.tasks.cleanup_old_data")
def cleanup_old_data():
    """Periodic task to clean up old data"""
    try:
        from datetime import datetime, timedelta
        from sqlmodel import select
        from app.models import CampaignMetric, ItemSuggestion, PerformancePrediction
        
        logger.info("Starting old data cleanup")
        
        with next(get_session()) as session:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            cleanup_results = {}
            
            # Clean old metrics (keep last 90 days)
            old_metrics_statement = select(CampaignMetric).where(
                CampaignMetric.period_start < cutoff_date
            )
            old_metrics = session.exec(old_metrics_statement).all()
            
            for metric in old_metrics:
                session.delete(metric)
            
            cleanup_results["deleted_metrics"] = len(old_metrics)
            
            # Clean old suggestions (keep last 30 days)
            suggestion_cutoff = datetime.utcnow() - timedelta(days=30)
            old_suggestions_statement = select(ItemSuggestion).where(
                ItemSuggestion.suggested_at < suggestion_cutoff
            )
            old_suggestions = session.exec(old_suggestions_statement).all()
            
            for suggestion in old_suggestions:
                session.delete(suggestion)
            
            cleanup_results["deleted_suggestions"] = len(old_suggestions)
            
            # Clean old predictions (keep last 60 days)
            prediction_cutoff = datetime.utcnow() - timedelta(days=60)
            old_predictions_statement = select(PerformancePrediction).where(
                PerformancePrediction.prediction_date < prediction_cutoff
            )
            old_predictions = session.exec(old_predictions_statement).all()
            
            for prediction in old_predictions:
                session.delete(prediction)
            
            cleanup_results["deleted_predictions"] = len(old_predictions)
            
            session.commit()
            
            logger.info(f"Data cleanup completed: {cleanup_results}")
            
            return {
                "status": "success",
                "cleanup_results": cleanup_results
            }
            
    except Exception as e:
        logger.error(f"Error in data cleanup task: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Manual task triggers
@celery_app.task(name="app.tasks.trigger_manual_schedule_check")
def trigger_manual_schedule_check():
    """Manually trigger schedule check"""
    return check_campaign_schedules.delay()


@celery_app.task(name="app.tasks.trigger_manual_metrics_collection")
def trigger_manual_metrics_collection():
    """Manually trigger metrics collection"""
    return collect_campaign_metrics.delay()


if __name__ == "__main__":
    celery_app.start()