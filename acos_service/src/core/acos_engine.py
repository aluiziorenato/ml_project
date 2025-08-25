"""ACOS automation engine for campaign optimization."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
import asyncio
import httpx
import logging

from ..models.acos_models import (
    ACOSRule, ACOSRuleExecution, ACOSAlert, ACOSActionType, 
    ACOSAlertSeverity, ACOSThresholdType, ACOSAnalysis
)
from ...campaign_automation_service.src.models.campaign_models import Campaign, CampaignMetric
from ...campaign_automation_service.src.core.metrics_analyzer import MetricsAnalyzer
from ..utils.logger import logger

class ACOSAutomationEngine:
    """ACOS-based campaign automation engine."""
    
    def __init__(self, db: Session, metrics_analyzer: MetricsAnalyzer):
        self.db = db
        self.metrics_analyzer = metrics_analyzer
        self.logger = logging.getLogger(__name__)
    
    async def evaluate_all_rules(self) -> Dict[str, Any]:
        """Evaluate all active ACOS rules and execute actions."""
        try:
            active_rules = self.db.query(ACOSRule).filter(ACOSRule.is_active == True).all()
            
            results = {
                "rules_evaluated": len(active_rules),
                "actions_taken": 0,
                "alerts_created": 0,
                "errors": []
            }
            
            for rule in active_rules:
                try:
                    rule_result = await self._evaluate_rule(rule)
                    results["actions_taken"] += rule_result["actions_taken"]
                    results["alerts_created"] += rule_result["alerts_created"]
                except Exception as e:
                    error_msg = f"Error evaluating rule {rule.id}: {str(e)}"
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in evaluate_all_rules: {e}")
            raise
    
    async def _evaluate_rule(self, rule: ACOSRule) -> Dict[str, Any]:
        """Evaluate a single ACOS rule."""
        result = {"actions_taken": 0, "alerts_created": 0}
        
        # Get campaigns to evaluate
        campaigns = await self._get_campaigns_for_rule(rule)
        
        for campaign in campaigns:
            # Calculate current ACOS for the evaluation period
            current_acos = await self._calculate_campaign_acos(
                campaign.id, 
                rule.evaluation_period_hours
            )
            
            if current_acos is None:
                continue
            
            # Check if rule threshold is met
            threshold_met = self._check_threshold(
                current_acos, 
                rule.threshold_value, 
                rule.threshold_type
            )
            
            if threshold_met:
                # Check minimum spend requirement
                period_spend = await self._get_campaign_spend(
                    campaign.id, 
                    rule.evaluation_period_hours
                )
                
                if period_spend >= rule.minimum_spend:
                    # Execute the action
                    action_result = await self._execute_action(
                        rule, campaign, current_acos, period_spend
                    )
                    
                    if action_result["success"]:
                        result["actions_taken"] += 1
                    
                    # Create alert if configured
                    if rule.action_type in [ACOSActionType.SEND_ALERT]:
                        await self._create_alert(rule, campaign, current_acos)
                        result["alerts_created"] += 1
        
        return result
    
    async def _get_campaigns_for_rule(self, rule: ACOSRule) -> List[Campaign]:
        """Get campaigns that should be evaluated for the rule."""
        query = self.db.query(Campaign)
        
        # Filter by specific campaign IDs if specified
        if rule.campaign_ids:
            query = query.filter(Campaign.id.in_(rule.campaign_ids))
        
        # Filter by categories if specified
        if rule.categories:
            # Assuming categories are stored as JSON array in Campaign model
            for category in rule.categories:
                query = query.filter(Campaign.categories.contains([category]))
        
        # Only active campaigns
        query = query.filter(Campaign.status == "active")
        
        return query.all()
    
    async def _calculate_campaign_acos(
        self, 
        campaign_id: int, 
        period_hours: int
    ) -> Optional[float]:
        """Calculate ACOS for a campaign over the specified period."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=period_hours)
            
            # Get aggregated metrics for the period
            metrics = self.db.query(
                func.sum(CampaignMetric.cost).label("total_cost"),
                func.sum(CampaignMetric.revenue).label("total_revenue")
            ).filter(
                and_(
                    CampaignMetric.campaign_id == campaign_id,
                    CampaignMetric.date >= start_date,
                    CampaignMetric.date <= end_date
                )
            ).first()
            
            if metrics.total_cost and metrics.total_revenue and metrics.total_revenue > 0:
                return (metrics.total_cost / metrics.total_revenue) * 100
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating ACOS for campaign {campaign_id}: {e}")
            return None
    
    async def _get_campaign_spend(self, campaign_id: int, period_hours: int) -> float:
        """Get total spend for a campaign over the specified period."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=period_hours)
            
            spend = self.db.query(
                func.sum(CampaignMetric.cost)
            ).filter(
                and_(
                    CampaignMetric.campaign_id == campaign_id,
                    CampaignMetric.date >= start_date,
                    CampaignMetric.date <= end_date
                )
            ).scalar()
            
            return spend or 0.0
            
        except Exception as e:
            self.logger.error(f"Error getting spend for campaign {campaign_id}: {e}")
            return 0.0
    
    def _check_threshold(
        self, 
        current_acos: float, 
        threshold_value: float, 
        threshold_type: ACOSThresholdType
    ) -> bool:
        """Check if ACOS threshold is met."""
        if threshold_type == ACOSThresholdType.MAXIMUM:
            return current_acos > threshold_value
        elif threshold_type == ACOSThresholdType.MINIMUM:
            return current_acos < threshold_value
        
        return False
    
    async def _execute_action(
        self, 
        rule: ACOSRule, 
        campaign: Campaign, 
        current_acos: float,
        period_spend: float
    ) -> Dict[str, Any]:
        """Execute the automation action."""
        action_result = {
            "success": False,
            "action": rule.action_type,
            "details": {}
        }
        
        try:
            if rule.action_type == ACOSActionType.PAUSE_CAMPAIGN:
                action_result = await self._pause_campaign(campaign)
            
            elif rule.action_type == ACOSActionType.ADJUST_BID:
                action_result = await self._adjust_campaign_bid(campaign, rule.action_config)
            
            elif rule.action_type == ACOSActionType.ADJUST_BUDGET:
                action_result = await self._adjust_campaign_budget(campaign, rule.action_config)
            
            elif rule.action_type == ACOSActionType.OPTIMIZE_KEYWORDS:
                action_result = await self._optimize_keywords(campaign, current_acos)
            
            elif rule.action_type == ACOSActionType.SEND_ALERT:
                action_result = {"success": True, "action": "alert", "details": {"alert_created": True}}
            
            # Log the execution
            await self._log_execution(rule, campaign, current_acos, action_result)
            
            return action_result
            
        except Exception as e:
            error_msg = f"Error executing action {rule.action_type} for campaign {campaign.id}: {e}"
            self.logger.error(error_msg)
            
            await self._log_execution(
                rule, campaign, current_acos, 
                {"success": False, "error": error_msg}
            )
            
            return {"success": False, "error": error_msg}
    
    async def _pause_campaign(self, campaign: Campaign) -> Dict[str, Any]:
        """Pause a campaign due to high ACOS."""
        try:
            campaign.status = "paused"
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": True,
                "action": "pause_campaign",
                "details": {"campaign_id": campaign.id, "new_status": "paused"}
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def _adjust_campaign_bid(
        self, 
        campaign: Campaign, 
        action_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust campaign bid based on ACOS performance."""
        try:
            adjustment_type = action_config.get("adjustment_type", "percentage")
            adjustment_value = action_config.get("adjustment_value", -10)  # Default: reduce by 10%
            
            if adjustment_type == "percentage":
                new_cpc = campaign.max_cpc * (1 + adjustment_value / 100)
            else:  # absolute
                new_cpc = campaign.max_cpc + adjustment_value
            
            # Apply minimum and maximum limits
            min_cpc = action_config.get("min_cpc", 0.10)
            max_cpc = action_config.get("max_cpc", campaign.max_cpc * 2)
            
            new_cpc = max(min_cpc, min(max_cpc, new_cpc))
            
            old_cpc = campaign.max_cpc
            campaign.max_cpc = new_cpc
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": True,
                "action": "adjust_bid",
                "details": {
                    "campaign_id": campaign.id,
                    "old_cpc": old_cpc,
                    "new_cpc": new_cpc,
                    "adjustment_percentage": ((new_cpc - old_cpc) / old_cpc) * 100
                }
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def _adjust_campaign_budget(
        self, 
        campaign: Campaign, 
        action_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust campaign budget based on ACOS performance."""
        try:
            adjustment_type = action_config.get("adjustment_type", "percentage")
            adjustment_value = action_config.get("adjustment_value", -15)  # Default: reduce by 15%
            
            if adjustment_type == "percentage":
                new_budget = campaign.daily_budget * (1 + adjustment_value / 100)
            else:  # absolute
                new_budget = campaign.daily_budget + adjustment_value
            
            # Apply minimum and maximum limits
            min_budget = action_config.get("min_budget", 10.0)
            max_budget = action_config.get("max_budget", campaign.daily_budget * 2)
            
            new_budget = max(min_budget, min(max_budget, new_budget))
            
            old_budget = campaign.daily_budget
            campaign.daily_budget = new_budget
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": True,
                "action": "adjust_budget",
                "details": {
                    "campaign_id": campaign.id,
                    "old_budget": old_budget,
                    "new_budget": new_budget,
                    "adjustment_percentage": ((new_budget - old_budget) / old_budget) * 100
                }
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def _optimize_keywords(
        self, 
        campaign: Campaign, 
        current_acos: float
    ) -> Dict[str, Any]:
        """Optimize keywords based on ACOS performance."""
        try:
            # This would integrate with AI modules for keyword optimization
            # For now, returning a placeholder implementation
            
            optimization_suggestions = [
                "Remove low-performing keywords with ACOS > 50%",
                "Increase bids on high-converting keywords",
                "Add negative keywords for irrelevant searches"
            ]
            
            return {
                "success": True,
                "action": "optimize_keywords",
                "details": {
                    "campaign_id": campaign.id,
                    "current_acos": current_acos,
                    "suggestions": optimization_suggestions
                }
            }
            
        except Exception as e:
            raise e
    
    async def _create_alert(
        self, 
        rule: ACOSRule, 
        campaign: Campaign, 
        current_acos: float
    ) -> None:
        """Create an ACOS alert."""
        try:
            # Determine severity based on how much ACOS exceeds threshold
            threshold_ratio = current_acos / rule.threshold_value
            
            if threshold_ratio >= 2.0:
                severity = ACOSAlertSeverity.CRITICAL
            elif threshold_ratio >= 1.5:
                severity = ACOSAlertSeverity.HIGH
            elif threshold_ratio >= 1.2:
                severity = ACOSAlertSeverity.MEDIUM
            else:
                severity = ACOSAlertSeverity.LOW
            
            alert = ACOSAlert(
                campaign_id=campaign.id,
                rule_id=rule.id,
                alert_type="acos_threshold_exceeded",
                severity=severity,
                title=f"ACOS Alert: {campaign.name}",
                message=f"Campaign ACOS ({current_acos:.2f}%) exceeds threshold ({rule.threshold_value:.2f}%)",
                current_acos=current_acos,
                threshold_acos=rule.threshold_value,
                period_hours=rule.evaluation_period_hours,
                recommended_actions=[
                    "Review keyword performance",
                    "Consider adjusting bids",
                    "Optimize product listings",
                    "Analyze competitor activity"
                ]
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating alert: {e}")
            raise e
    
    async def _log_execution(
        self, 
        rule: ACOSRule, 
        campaign: Campaign, 
        current_acos: float, 
        action_result: Dict[str, Any]
    ) -> None:
        """Log rule execution."""
        try:
            execution = ACOSRuleExecution(
                rule_id=rule.id,
                campaign_id=campaign.id,
                triggered_acos=current_acos,
                threshold_value=rule.threshold_value,
                action_taken=rule.action_type,
                action_result=action_result,
                status="success" if action_result["success"] else "failed",
                error_message=action_result.get("error")
            )
            
            self.db.add(execution)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error logging execution: {e}")
    
    async def analyze_campaign_acos(self, campaign_id: int, period_hours: int = 168) -> ACOSAnalysis:
        """Analyze ACOS performance for a campaign."""
        try:
            current_acos = await self._calculate_campaign_acos(campaign_id, 24)
            week_acos = await self._calculate_campaign_acos(campaign_id, period_hours)
            
            # Determine performance status
            performance_status = "good"
            if current_acos and current_acos > 30:
                performance_status = "critical"
            elif current_acos and current_acos > 20:
                performance_status = "warning"
            
            # Generate optimization suggestions
            suggestions = []
            if current_acos and current_acos > 25:
                suggestions.extend([
                    "Consider reducing bid amounts to lower ACOS",
                    "Review and optimize keyword targeting",
                    "Analyze product listing optimization opportunities"
                ])
            
            if week_acos and current_acos and current_acos > week_acos:
                suggestions.append("ACOS is trending upward - investigate recent changes")
            
            return ACOSAnalysis(
                campaign_id=campaign_id,
                current_acos=current_acos or 0.0,
                target_acos=20.0,  # Default target
                performance_status=performance_status,
                trend_analysis={
                    "current_24h": current_acos,
                    "weekly_average": week_acos,
                    "trend": "increasing" if (current_acos or 0) > (week_acos or 0) else "decreasing"
                },
                optimization_suggestions=suggestions,
                projected_impact={
                    "bid_reduction_10pct": -2.0,  # Estimated ACOS reduction
                    "budget_optimization": -1.5
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing ACOS for campaign {campaign_id}: {e}")
            raise