from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from src.models.database import StrategyPerformanceLog, StrategicMode, StrategyConfiguration, SpecialDate, StrategyAlert, AutomationAction
from src.models.schemas import (
    PerformanceReportRequest, PerformanceReportResponse,
    StrategyDashboardData, StrategyPerformanceResponse
)
from src.services.strategy_service import StrategyService
from src.services.special_dates_service import SpecialDatesService
import logging

logger = logging.getLogger(__name__)

class ReportsService:
    """Service for generating reports and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.strategy_service = StrategyService(db)
        self.special_dates_service = SpecialDatesService(db)
    
    def generate_performance_report(self, request: PerformanceReportRequest) -> PerformanceReportResponse:
        """Generate comprehensive performance report"""
        try:
            # Get performance data for the specified period
            query = self.db.query(StrategyPerformanceLog).filter(
                StrategyPerformanceLog.user_id == request.user_id,
                StrategyPerformanceLog.date >= request.start_date,
                StrategyPerformanceLog.date <= request.end_date
            )
            
            if request.strategy_ids:
                query = query.filter(StrategyPerformanceLog.strategy_id.in_(request.strategy_ids))
            
            performance_data = query.all()
            
            # Convert to response objects
            strategies = [StrategyPerformanceResponse.from_orm(perf) for perf in performance_data]
            
            # Calculate summary
            summary = self._calculate_summary(performance_data)
            
            # Generate comparison if requested
            comparison = None
            if request.include_comparison:
                comparison = self._generate_comparison(request, performance_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(performance_data)
            
            return PerformanceReportResponse(
                period={"start_date": request.start_date, "end_date": request.end_date},
                strategies=strategies,
                summary=summary,
                comparison=comparison,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise
    
    def get_dashboard_data(self, user_id: int) -> StrategyDashboardData:
        """Get dashboard data for a user"""
        try:
            # Get current strategy
            current_strategy = self.strategy_service.get_user_configuration(user_id)
            strategy_details = None
            if current_strategy:
                strategy_details = self.strategy_service.get_strategy(current_strategy.active_strategy_id)
            
            # Get active special dates
            active_special_dates = self.special_dates_service.get_active_special_dates()
            
            # Get recent alerts (last 7 days)
            recent_alerts = self.db.query(StrategyAlert).filter(
                StrategyAlert.user_id == user_id,
                StrategyAlert.created_at >= datetime.now() - timedelta(days=7)
            ).order_by(StrategyAlert.created_at.desc()).limit(10).all()
            
            # Get recent actions (last 7 days)
            recent_actions = self.db.query(AutomationAction).filter(
                AutomationAction.user_id == user_id,
                AutomationAction.created_at >= datetime.now() - timedelta(days=7)
            ).order_by(AutomationAction.created_at.desc()).limit(10).all()
            
            # Get performance summary (last 30 days)
            performance_summary = self._get_performance_summary(user_id, 30)
            
            # Calculate KPIs
            kpis = self.calculate_strategy_kpis(user_id)
            
            return StrategyDashboardData(
                current_strategy=strategy_details,
                active_special_dates=active_special_dates,
                recent_alerts=[alert for alert in recent_alerts],
                recent_actions=[action for action in recent_actions],
                performance_summary=performance_summary,
                kpis=kpis
            )
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    def get_user_performance(
        self, 
        user_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        strategy_id: Optional[int] = None
    ) -> List[StrategyPerformanceResponse]:
        """Get performance data for a user"""
        try:
            query = self.db.query(StrategyPerformanceLog).filter(
                StrategyPerformanceLog.user_id == user_id
            )
            
            if start_date:
                query = query.filter(StrategyPerformanceLog.date >= start_date)
            
            if end_date:
                query = query.filter(StrategyPerformanceLog.date <= end_date)
            
            if strategy_id:
                query = query.filter(StrategyPerformanceLog.strategy_id == strategy_id)
            
            performance_data = query.order_by(StrategyPerformanceLog.date.desc()).all()
            
            return [StrategyPerformanceResponse.from_orm(perf) for perf in performance_data]
            
        except Exception as e:
            logger.error(f"Failed to get user performance: {e}")
            raise
    
    def compare_strategies(
        self,
        user_id: int,
        strategy_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Compare performance between different strategies"""
        try:
            comparison_data = {}
            
            for strategy_id in strategy_ids:
                performance = self.get_user_performance(
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_id=strategy_id
                )
                
                strategy = self.strategy_service.get_strategy(strategy_id)
                
                if strategy and performance:
                    comparison_data[strategy.name] = {
                        "strategy": strategy,
                        "performance": performance,
                        "summary": self._calculate_summary([p for p in performance])
                    }
            
            return {
                "comparison": comparison_data,
                "period": {
                    "start_date": start_date or date.today() - timedelta(days=30),
                    "end_date": end_date or date.today()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to compare strategies: {e}")
            raise
    
    def analyze_special_dates_impact(self, user_id: int, year: Optional[int] = None) -> Dict[str, Any]:
        """Analyze impact of special dates on performance"""
        if year is None:
            year = datetime.now().year
        
        # This is a simplified implementation
        # In a real scenario, you'd analyze performance during special dates vs normal periods
        return {
            "year": year,
            "analysis": "Special dates impact analysis would be implemented here",
            "message": "Feature coming soon"
        }
    
    def get_strategy_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Get AI-powered strategy recommendations"""
        # This is a simplified implementation
        # In a real scenario, you'd use ML models to generate recommendations
        return {
            "recommendations": [
                "Consider switching to 'Maximize Profit' strategy during low-competition periods",
                "Use 'Scale Sales' strategy during high-demand periods",
                "Monitor ACOS closely during special dates campaigns"
            ],
            "confidence": "medium",
            "based_on": "historical performance analysis"
        }
    
    def analyze_performance_trends(self, user_id: int, metric: str, period_days: int) -> Dict[str, Any]:
        """Analyze performance trends"""
        # This is a simplified implementation
        return {
            "metric": metric,
            "period_days": period_days,
            "trend": "stable",
            "analysis": "Performance trends analysis would be implemented here"
        }
    
    def calculate_strategy_kpis(self, user_id: int, strategy_id: Optional[int] = None, period_days: int = 30) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        try:
            start_date = date.today() - timedelta(days=period_days)
            
            query = self.db.query(StrategyPerformanceLog).filter(
                StrategyPerformanceLog.user_id == user_id,
                StrategyPerformanceLog.date >= start_date
            )
            
            if strategy_id:
                query = query.filter(StrategyPerformanceLog.strategy_id == strategy_id)
            
            performance_data = query.all()
            
            if not performance_data:
                return {
                    "total_spend": 0,
                    "total_sales": 0,
                    "average_acos": 0,
                    "roi": 0,
                    "campaigns_count": 0,
                    "period_days": period_days
                }
            
            total_spend = sum(float(p.total_spend or 0) for p in performance_data)
            total_sales = sum(float(p.total_sales or 0) for p in performance_data)
            avg_acos = sum(float(p.average_acos or 0) for p in performance_data) / len(performance_data)
            avg_roi = sum(float(p.roi or 0) for p in performance_data) / len(performance_data)
            campaigns_count = sum(p.campaigns_count or 0 for p in performance_data)
            
            return {
                "total_spend": total_spend,
                "total_sales": total_sales,
                "average_acos": round(avg_acos, 2),
                "roi": round(avg_roi, 2),
                "campaigns_count": campaigns_count,
                "period_days": period_days
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate strategy KPIs: {e}")
            return {}
    
    def export_performance_data(self, user_id: int, format: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """Export performance data in various formats"""
        # This is a simplified implementation
        return {
            "format": format,
            "message": "Export functionality would be implemented here",
            "download_url": f"/exports/{user_id}/{format}"
        }
    
    def _calculate_summary(self, performance_data: List) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not performance_data:
            return {}
        
        total_spend = sum(float(p.total_spend or 0) for p in performance_data)
        total_sales = sum(float(p.total_sales or 0) for p in performance_data)
        avg_acos = sum(float(p.average_acos or 0) for p in performance_data) / len(performance_data)
        
        return {
            "total_spend": total_spend,
            "total_sales": total_sales,
            "average_acos": round(avg_acos, 2),
            "data_points": len(performance_data)
        }
    
    def _generate_comparison(self, request: PerformanceReportRequest, performance_data: List) -> Dict[str, Any]:
        """Generate comparison data"""
        # Compare with previous period
        previous_start = request.start_date - (request.end_date - request.start_date)
        previous_end = request.start_date
        
        # This would fetch previous period data and compare
        return {
            "previous_period": {
                "start_date": previous_start,
                "end_date": previous_end
            },
            "comparison": "Comparison logic would be implemented here"
        }
    
    def _generate_recommendations(self, performance_data: List) -> List[str]:
        """Generate recommendations based on performance data"""
        recommendations = []
        
        if not performance_data:
            recommendations.append("No performance data available for analysis")
            return recommendations
        
        avg_acos = sum(float(p.average_acos or 0) for p in performance_data) / len(performance_data)
        
        if avg_acos > 25:
            recommendations.append("Consider switching to a more conservative strategy to reduce ACOS")
        elif avg_acos < 10:
            recommendations.append("ACOS is very low - consider increasing bids to scale sales")
        
        return recommendations
    
    def _get_performance_summary(self, user_id: int, days: int) -> Dict[str, Any]:
        """Get performance summary for specified days"""
        start_date = date.today() - timedelta(days=days)
        
        performance_data = self.db.query(StrategyPerformanceLog).filter(
            StrategyPerformanceLog.user_id == user_id,
            StrategyPerformanceLog.date >= start_date
        ).all()
        
        return self._calculate_summary(performance_data)