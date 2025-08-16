"""Metrics analysis and performance tracking."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
import statistics

from ..models.campaign_models import Campaign, CampaignMetric
from ..utils.logger import logger, log_error


class MetricsAnalyzer:
    """Metrics analysis and performance optimization."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def record_campaign_metrics(
        self,
        campaign_id: int,
        impressions: int,
        clicks: int,
        conversions: int,
        cost: float,
        revenue: float,
        date: Optional[datetime] = None
    ) -> None:
        """Record campaign metrics for a specific time period."""
        try:
            if not date:
                date = datetime.utcnow()
            
            # Calculate derived metrics
            ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
            cpc = (cost / clicks) if clicks > 0 else 0.0
            cpa = (cost / conversions) if conversions > 0 else 0.0
            roas = (revenue / cost) if cost > 0 else 0.0
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0.0
            acos = (cost / revenue * 100) if revenue > 0 else 0.0  # Advertising Cost of Sales
            
            # Create metric record
            metric = CampaignMetric(
                campaign_id=campaign_id,
                date=date,
                hour=date.hour,
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                cost=cost,
                revenue=revenue,
                ctr=ctr,
                cpc=cpc,
                cpa=cpa,
                roas=roas,
                roi=roi,
                acos=acos
            )
            
            self.db.add(metric)
            
            # Update campaign totals
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.impressions += impressions
                campaign.clicks += clicks
                campaign.conversions += conversions
                campaign.cost += cost
                campaign.revenue += revenue
                campaign.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(
                "Metrics recorded",
                campaign_id=campaign_id,
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                cost=cost,
                revenue=revenue
            )
            
        except Exception as e:
            self.db.rollback()
            log_error(e, {"action": "record_campaign_metrics", "campaign_id": campaign_id})
            raise
    
    async def get_hourly_metrics(
        self,
        campaign_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get hourly metrics breakdown for a campaign."""
        try:
            metrics = self.db.query(CampaignMetric).filter(
                and_(
                    CampaignMetric.campaign_id == campaign_id,
                    CampaignMetric.date >= start_date,
                    CampaignMetric.date <= end_date
                )
            ).order_by(CampaignMetric.date).all()
            
            return [
                {
                    "date": metric.date.isoformat(),
                    "hour": metric.hour,
                    "impressions": metric.impressions,
                    "clicks": metric.clicks,
                    "conversions": metric.conversions,
                    "cost": metric.cost,
                    "revenue": metric.revenue,
                    "ctr": metric.ctr,
                    "cpc": metric.cpc,
                    "cpa": metric.cpa,
                    "roas": metric.roas,
                    "roi": metric.roi,
                    "acos": metric.acos
                }
                for metric in metrics
            ]
            
        except Exception as e:
            log_error(e, {"action": "get_hourly_metrics", "campaign_id": campaign_id})
            raise
    
    async def get_daily_aggregated_metrics(
        self,
        campaign_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily aggregated metrics for a campaign."""
        try:
            # Group by date and aggregate
            daily_metrics = self.db.query(
                func.date(CampaignMetric.date).label("date"),
                func.sum(CampaignMetric.impressions).label("impressions"),
                func.sum(CampaignMetric.clicks).label("clicks"),
                func.sum(CampaignMetric.conversions).label("conversions"),
                func.sum(CampaignMetric.cost).label("cost"),
                func.sum(CampaignMetric.revenue).label("revenue")
            ).filter(
                and_(
                    CampaignMetric.campaign_id == campaign_id,
                    CampaignMetric.date >= start_date,
                    CampaignMetric.date <= end_date
                )
            ).group_by(func.date(CampaignMetric.date)).all()
            
            result = []
            for metric in daily_metrics:
                ctr = (metric.clicks / metric.impressions * 100) if metric.impressions > 0 else 0.0
                cpc = (metric.cost / metric.clicks) if metric.clicks > 0 else 0.0
                cpa = (metric.cost / metric.conversions) if metric.conversions > 0 else 0.0
                roas = (metric.revenue / metric.cost) if metric.cost > 0 else 0.0
                roi = ((metric.revenue - metric.cost) / metric.cost * 100) if metric.cost > 0 else 0.0
                acos = (metric.cost / metric.revenue * 100) if metric.revenue > 0 else 0.0
                
                result.append({
                    "date": metric.date.isoformat(),
                    "impressions": metric.impressions,
                    "clicks": metric.clicks,
                    "conversions": metric.conversions,
                    "cost": metric.cost,
                    "revenue": metric.revenue,
                    "ctr": round(ctr, 2),
                    "cpc": round(cpc, 2),
                    "cpa": round(cpa, 2),
                    "roas": round(roas, 2),
                    "roi": round(roi, 2),
                    "acos": round(acos, 2)
                })
            
            return result
            
        except Exception as e:
            log_error(e, {"action": "get_daily_aggregated_metrics", "campaign_id": campaign_id})
            raise
    
    async def analyze_performance_trends(self, campaign_id: int, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends over the specified period."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get daily metrics
            daily_metrics = await self.get_daily_aggregated_metrics(campaign_id, start_date, end_date)
            
            if len(daily_metrics) < 2:
                return {
                    "trend_analysis": "insufficient_data",
                    "message": "Not enough data to analyze trends"
                }
            
            # Calculate trends
            ctr_values = [m["ctr"] for m in daily_metrics if m["ctr"] > 0]
            cpc_values = [m["cpc"] for m in daily_metrics if m["cpc"] > 0]
            roas_values = [m["roas"] for m in daily_metrics if m["roas"] > 0]
            
            analysis = {
                "period_days": days,
                "data_points": len(daily_metrics),
                "trends": {}
            }
            
            # CTR trend
            if len(ctr_values) >= 2:
                ctr_trend = "increasing" if ctr_values[-1] > ctr_values[0] else "decreasing"
                ctr_change = ((ctr_values[-1] - ctr_values[0]) / ctr_values[0] * 100) if ctr_values[0] > 0 else 0
                analysis["trends"]["ctr"] = {
                    "direction": ctr_trend,
                    "change_percent": round(ctr_change, 2),
                    "current_value": ctr_values[-1],
                    "average": round(statistics.mean(ctr_values), 2)
                }
            
            # CPC trend
            if len(cpc_values) >= 2:
                cpc_trend = "increasing" if cpc_values[-1] > cpc_values[0] else "decreasing"
                cpc_change = ((cpc_values[-1] - cpc_values[0]) / cpc_values[0] * 100) if cpc_values[0] > 0 else 0
                analysis["trends"]["cpc"] = {
                    "direction": cpc_trend,
                    "change_percent": round(cpc_change, 2),
                    "current_value": cpc_values[-1],
                    "average": round(statistics.mean(cpc_values), 2)
                }
            
            # ROAS trend
            if len(roas_values) >= 2:
                roas_trend = "increasing" if roas_values[-1] > roas_values[0] else "decreasing"
                roas_change = ((roas_values[-1] - roas_values[0]) / roas_values[0] * 100) if roas_values[0] > 0 else 0
                analysis["trends"]["roas"] = {
                    "direction": roas_trend,
                    "change_percent": round(roas_change, 2),
                    "current_value": roas_values[-1],
                    "average": round(statistics.mean(roas_values), 2)
                }
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(analysis)
            analysis["recommendations"] = recommendations
            
            return analysis
            
        except Exception as e:
            log_error(e, {"action": "analyze_performance_trends", "campaign_id": campaign_id})
            raise
    
    async def get_benchmark_comparison(self, campaign_id: int, category: str) -> Dict[str, Any]:
        """Compare campaign performance against category benchmarks."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return {"error": "Campaign not found"}
            
            # Get category benchmarks (mock data for demo)
            benchmarks = self._get_category_benchmarks(category)
            
            # Calculate current campaign performance
            total_impressions = campaign.impressions or 0
            total_clicks = campaign.clicks or 0
            total_cost = campaign.cost or 0
            total_revenue = campaign.revenue or 0
            
            current_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            current_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
            current_roas = (total_revenue / total_cost) if total_cost > 0 else 0
            
            # Compare with benchmarks
            comparison = {
                "campaign_id": campaign_id,
                "category": category,
                "performance": {
                    "ctr": {
                        "current": round(current_ctr, 2),
                        "benchmark": benchmarks["ctr"],
                        "vs_benchmark": round(((current_ctr - benchmarks["ctr"]) / benchmarks["ctr"] * 100), 2) if benchmarks["ctr"] > 0 else 0
                    },
                    "cpc": {
                        "current": round(current_cpc, 2),
                        "benchmark": benchmarks["cpc"],
                        "vs_benchmark": round(((current_cpc - benchmarks["cpc"]) / benchmarks["cpc"] * 100), 2) if benchmarks["cpc"] > 0 else 0
                    },
                    "roas": {
                        "current": round(current_roas, 2),
                        "benchmark": benchmarks["roas"],
                        "vs_benchmark": round(((current_roas - benchmarks["roas"]) / benchmarks["roas"] * 100), 2) if benchmarks["roas"] > 0 else 0
                    }
                }
            }
            
            # Add performance rating
            rating = self._calculate_performance_rating(comparison["performance"])
            comparison["overall_rating"] = rating
            
            return comparison
            
        except Exception as e:
            log_error(e, {"action": "get_benchmark_comparison", "campaign_id": campaign_id})
            raise
    
    def _generate_performance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on trend analysis."""
        recommendations = []
        trends = analysis.get("trends", {})
        
        # CTR recommendations
        if "ctr" in trends:
            ctr_data = trends["ctr"]
            if ctr_data["direction"] == "decreasing" and ctr_data["change_percent"] < -10:
                recommendations.append("CTR is declining significantly. Consider refreshing ad copy or adjusting targeting.")
            elif ctr_data["average"] < 1.0:
                recommendations.append("CTR is below industry average. Consider improving ad relevance and targeting.")
        
        # CPC recommendations
        if "cpc" in trends:
            cpc_data = trends["cpc"]
            if cpc_data["direction"] == "increasing" and cpc_data["change_percent"] > 20:
                recommendations.append("CPC is rising significantly. Consider optimizing bids or improving Quality Score.")
        
        # ROAS recommendations
        if "roas" in trends:
            roas_data = trends["roas"]
            if roas_data["direction"] == "decreasing" and roas_data["change_percent"] < -15:
                recommendations.append("ROAS is declining. Review conversion tracking and optimize for high-value actions.")
            elif roas_data["average"] < 2.0:
                recommendations.append("ROAS is below 2:1. Consider increasing conversion value or reducing costs.")
        
        if not recommendations:
            recommendations.append("Performance is stable. Continue monitoring and consider testing new optimizations.")
        
        return recommendations
    
    def _get_category_benchmarks(self, category: str) -> Dict[str, float]:
        """Get performance benchmarks for a category (mock data)."""
        # In production, this would come from a real benchmarking database
        benchmarks = {
            "electronics": {"ctr": 2.1, "cpc": 1.25, "roas": 3.2},
            "fashion": {"ctr": 1.8, "cpc": 0.95, "roas": 2.8},
            "home": {"ctr": 1.6, "cpc": 1.10, "roas": 3.0},
            "books": {"ctr": 2.3, "cpc": 0.85, "roas": 3.5},
            "sports": {"ctr": 1.9, "cpc": 1.15, "roas": 2.9},
            "default": {"ctr": 1.8, "cpc": 1.05, "roas": 3.0}
        }
        
        return benchmarks.get(category.lower(), benchmarks["default"])
    
    def _calculate_performance_rating(self, performance: Dict[str, Any]) -> str:
        """Calculate overall performance rating."""
        scores = []
        
        # CTR score
        ctr_vs_benchmark = performance["ctr"]["vs_benchmark"]
        if ctr_vs_benchmark >= 20:
            scores.append(5)
        elif ctr_vs_benchmark >= 10:
            scores.append(4)
        elif ctr_vs_benchmark >= 0:
            scores.append(3)
        elif ctr_vs_benchmark >= -10:
            scores.append(2)
        else:
            scores.append(1)
        
        # CPC score (lower is better)
        cpc_vs_benchmark = performance["cpc"]["vs_benchmark"]
        if cpc_vs_benchmark <= -20:
            scores.append(5)
        elif cpc_vs_benchmark <= -10:
            scores.append(4)
        elif cpc_vs_benchmark <= 0:
            scores.append(3)
        elif cpc_vs_benchmark <= 10:
            scores.append(2)
        else:
            scores.append(1)
        
        # ROAS score
        roas_vs_benchmark = performance["roas"]["vs_benchmark"]
        if roas_vs_benchmark >= 30:
            scores.append(5)
        elif roas_vs_benchmark >= 15:
            scores.append(4)
        elif roas_vs_benchmark >= 0:
            scores.append(3)
        elif roas_vs_benchmark >= -15:
            scores.append(2)
        else:
            scores.append(1)
        
        # Calculate average score
        avg_score = sum(scores) / len(scores) if scores else 3
        
        if avg_score >= 4.5:
            return "excellent"
        elif avg_score >= 3.5:
            return "good"
        elif avg_score >= 2.5:
            return "average"
        elif avg_score >= 1.5:
            return "below_average"
        else:
            return "poor"