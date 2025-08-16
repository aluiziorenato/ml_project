import logging
from datetime import datetime, time, timedelta
from typing import List, Optional, Dict
from sqlmodel import Session, select
from app.models import (
    DiscountCampaign, CampaignSchedule, CampaignStatus, 
    ScheduleStatus, DayOfWeek
)
from app.core.database import get_session
from app.services.ml_api_service import ml_api_service

logger = logging.getLogger(__name__)


class SchedulingService:
    """Service for managing campaign scheduling"""
    
    @staticmethod
    def get_current_day_of_week() -> DayOfWeek:
        """Get current day of week as enum"""
        days_map = {
            0: DayOfWeek.MONDAY,
            1: DayOfWeek.TUESDAY,
            2: DayOfWeek.WEDNESDAY,
            3: DayOfWeek.THURSDAY,
            4: DayOfWeek.FRIDAY,
            5: DayOfWeek.SATURDAY,
            6: DayOfWeek.SUNDAY
        }
        return days_map[datetime.now().weekday()]
    
    @staticmethod
    def get_current_time() -> time:
        """Get current time"""
        return datetime.now().time()
    
    async def check_pending_schedules(self, session: Session) -> List[Dict]:
        """Check and execute pending schedules"""
        current_day = self.get_current_day_of_week()
        current_time = self.get_current_time()
        
        # Find schedules that should be executed now
        statement = select(CampaignSchedule).where(
            CampaignSchedule.day_of_week == current_day,
            CampaignSchedule.status == ScheduleStatus.PENDING,
            CampaignSchedule.start_time <= current_time,
            CampaignSchedule.end_time >= current_time
        ).join(DiscountCampaign)
        
        schedules = session.exec(statement).all()
        results = []
        
        for schedule in schedules:
            try:
                result = await self._execute_schedule(session, schedule)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing schedule {schedule.id}: {e}")
                self._mark_schedule_failed(session, schedule, str(e))
        
        session.commit()
        return results
    
    async def _execute_schedule(self, session: Session, schedule: CampaignSchedule) -> Dict:
        """Execute a specific schedule"""
        campaign = schedule.campaign
        access_token = await self._get_seller_access_token(campaign.seller_id)
        
        if not access_token:
            raise Exception(f"No access token found for seller {campaign.seller_id}")
        
        result = {
            "schedule_id": schedule.id,
            "campaign_id": campaign.id,
            "action": schedule.action,
            "status": "success",
            "executed_at": datetime.utcnow()
        }
        
        try:
            if schedule.action == "activate":
                await self._activate_campaign(session, campaign, access_token)
                result["message"] = f"Campaign {campaign.id} activated successfully"
            elif schedule.action == "pause":
                await self._pause_campaign(session, campaign, access_token)
                result["message"] = f"Campaign {campaign.id} paused successfully"
            else:
                raise Exception(f"Unknown action: {schedule.action}")
            
            # Mark schedule as executed
            schedule.status = ScheduleStatus.EXECUTED
            schedule.last_executed = datetime.utcnow()
            session.add(schedule)
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            schedule.status = ScheduleStatus.FAILED
            session.add(schedule)
            raise
        
        return result
    
    async def _activate_campaign(self, session: Session, campaign: DiscountCampaign, access_token: str):
        """Activate a discount campaign"""
        # Create promotion via ML API
        promotion_data = await ml_api_service.create_seller_promotion(
            access_token=access_token,
            item_id=campaign.item_id,
            discount_percentage=campaign.discount_percentage
        )
        
        # Update campaign status
        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_at = datetime.utcnow()
        session.add(campaign)
        
        logger.info(f"Campaign {campaign.id} activated with promotion {promotion_data.get('id')}")
    
    async def _pause_campaign(self, session: Session, campaign: DiscountCampaign, access_token: str):
        """Pause a discount campaign"""
        # Get existing promotions and pause them
        promotions = await ml_api_service.get_seller_promotions(
            access_token=access_token,
            seller_id=campaign.seller_id
        )
        
        # Find promotion for this item and pause it
        for promotion in promotions:
            if promotion.get("item_id") == campaign.item_id:
                await ml_api_service.pause_seller_promotion(
                    access_token=access_token,
                    promotion_id=promotion["id"]
                )
                break
        
        # Update campaign status
        campaign.status = CampaignStatus.PAUSED
        campaign.updated_at = datetime.utcnow()
        session.add(campaign)
        
        logger.info(f"Campaign {campaign.id} paused")
    
    async def _get_seller_access_token(self, seller_id: str) -> Optional[str]:
        """Get access token for seller (placeholder - integrate with auth system)"""
        # TODO: Integrate with the main backend auth system
        # For now, return a mock token
        return "mock_access_token"
    
    def _mark_schedule_failed(self, session: Session, schedule: CampaignSchedule, error: str):
        """Mark a schedule as failed"""
        schedule.status = ScheduleStatus.FAILED
        session.add(schedule)
        logger.error(f"Schedule {schedule.id} failed: {error}")
    
    def create_schedule(self, session: Session, campaign_id: int, schedule_data: Dict) -> CampaignSchedule:
        """Create a new schedule for a campaign"""
        schedule = CampaignSchedule(
            campaign_id=campaign_id,
            day_of_week=schedule_data["day_of_week"],
            start_time=schedule_data["start_time"],
            end_time=schedule_data["end_time"],
            action=schedule_data["action"]
        )
        
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
        
        logger.info(f"Created schedule {schedule.id} for campaign {campaign_id}")
        return schedule
    
    def get_campaign_schedules(self, session: Session, campaign_id: int) -> List[CampaignSchedule]:
        """Get all schedules for a campaign"""
        statement = select(CampaignSchedule).where(CampaignSchedule.campaign_id == campaign_id)
        return session.exec(statement).all()
    
    def update_schedule(self, session: Session, schedule_id: int, update_data: Dict) -> CampaignSchedule:
        """Update an existing schedule"""
        schedule = session.get(CampaignSchedule, schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        for field, value in update_data.items():
            if hasattr(schedule, field) and value is not None:
                setattr(schedule, field, value)
        
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
        
        logger.info(f"Updated schedule {schedule_id}")
        return schedule
    
    def delete_schedule(self, session: Session, schedule_id: int) -> bool:
        """Delete a schedule"""
        schedule = session.get(CampaignSchedule, schedule_id)
        if not schedule:
            return False
        
        session.delete(schedule)
        session.commit()
        
        logger.info(f"Deleted schedule {schedule_id}")
        return True


# Global instance
scheduling_service = SchedulingService()