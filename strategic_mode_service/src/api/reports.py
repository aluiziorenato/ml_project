from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from src.core.database import get_db
from src.models.schemas import (
    PerformanceReportRequest, PerformanceReportResponse,
    StrategyDashboardData, StrategyPerformanceResponse
)
from src.services.reports_service import ReportsService

router = APIRouter()

@router.post("/performance", response_model=PerformanceReportResponse)
async def generate_performance_report(
    report_request: PerformanceReportRequest,
    db: Session = Depends(get_db)
):
    """Generate performance report for strategies"""
    reports_service = ReportsService(db)
    try:
        return reports_service.generate_performance_report(report_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate performance report: {str(e)}"
        )

@router.get("/dashboard/{user_id}", response_model=StrategyDashboardData)
async def get_dashboard_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get dashboard data for a user"""
    reports_service = ReportsService(db)
    try:
        return reports_service.get_dashboard_data(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.get("/performance/{user_id}", response_model=List[StrategyPerformanceResponse])
async def get_user_performance(
    user_id: int,
    start_date: Optional[date] = Query(None, description="Start date for performance data"),
    end_date: Optional[date] = Query(None, description="End date for performance data"),
    strategy_id: Optional[int] = Query(None, description="Filter by specific strategy"),
    db: Session = Depends(get_db)
):
    """Get performance data for a user"""
    reports_service = ReportsService(db)
    try:
        return reports_service.get_user_performance(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            strategy_id=strategy_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user performance: {str(e)}"
        )

@router.get("/comparison/{user_id}")
async def get_strategy_comparison(
    user_id: int,
    strategy_ids: List[int] = Query(..., description="Strategy IDs to compare"),
    start_date: Optional[date] = Query(None, description="Start date for comparison"),
    end_date: Optional[date] = Query(None, description="End date for comparison"),
    db: Session = Depends(get_db)
):
    """Compare performance between different strategies"""
    reports_service = ReportsService(db)
    try:
        return reports_service.compare_strategies(
            user_id=user_id,
            strategy_ids=strategy_ids,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare strategies: {str(e)}"
        )

@router.get("/special-dates-impact/{user_id}")
async def get_special_dates_impact(
    user_id: int,
    year: Optional[int] = Query(None, description="Year to analyze (defaults to current year)"),
    db: Session = Depends(get_db)
):
    """Get impact analysis of special dates on performance"""
    reports_service = ReportsService(db)
    try:
        return reports_service.analyze_special_dates_impact(user_id, year)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze special dates impact: {str(e)}"
        )

@router.get("/recommendations/{user_id}")
async def get_strategy_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get AI-powered strategy recommendations"""
    reports_service = ReportsService(db)
    try:
        return reports_service.get_strategy_recommendations(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy recommendations: {str(e)}"
        )

@router.get("/trends/{user_id}")
async def get_performance_trends(
    user_id: int,
    metric: str = Query("acos", description="Metric to analyze trends (acos, roi, spend, sales)"),
    period_days: int = Query(30, description="Period in days to analyze"),
    db: Session = Depends(get_db)
):
    """Get performance trends analysis"""
    reports_service = ReportsService(db)
    try:
        return reports_service.analyze_performance_trends(
            user_id=user_id,
            metric=metric,
            period_days=period_days
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze performance trends: {str(e)}"
        )

@router.get("/kpis/{user_id}")
async def get_strategy_kpis(
    user_id: int,
    strategy_id: Optional[int] = Query(None, description="Specific strategy ID"),
    period_days: int = Query(30, description="Period in days for KPI calculation"),
    db: Session = Depends(get_db)
):
    """Get key performance indicators for strategies"""
    reports_service = ReportsService(db)
    try:
        return reports_service.calculate_strategy_kpis(
            user_id=user_id,
            strategy_id=strategy_id,
            period_days=period_days
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate strategy KPIs: {str(e)}"
        )

@router.get("/export/{user_id}")
async def export_performance_data(
    user_id: int,
    format: str = Query("csv", description="Export format (csv, xlsx, json)"),
    start_date: Optional[date] = Query(None, description="Start date for export"),
    end_date: Optional[date] = Query(None, description="End date for export"),
    db: Session = Depends(get_db)
):
    """Export performance data in various formats"""
    if format not in ["csv", "xlsx", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be one of: csv, xlsx, json"
        )
    
    reports_service = ReportsService(db)
    try:
        return reports_service.export_performance_data(
            user_id=user_id,
            format=format,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export performance data: {str(e)}"
        )