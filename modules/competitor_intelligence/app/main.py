"""Competitor Intelligence - Advanced Competitor Analysis Module"""
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import asyncio
import random

from .database import get_database, create_tables
from .models import (
    CompetitorProfileCreate, CompetitorProfileResponse,
    PriceHistoryResponse, KeywordCompetitionResponse, 
    SentimentAnalysisResponse, MonitoringListCreate, MonitoringListResponse
)
from .services import (
    CompetitorRadarService, StrategyEngineService, PredictionService,
    SentimentAnalysisService, BlueOceanService
)

# Initialize FastAPI app
app = FastAPI(
    title="Competitor Intelligence",
    version="2.0.0",
    description="Advanced competitor analysis and market intelligence system"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Initialize services
radar_service = CompetitorRadarService()
strategy_service = StrategyEngineService()
prediction_service = PredictionService()
sentiment_service = SentimentAnalysisService()
blue_ocean_service = BlueOceanService()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("Service will continue without database functionality")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "competitor_intelligence",
        "version": "2.0.0",
        "features": [
            "real_time_radar", "strategy_engine", "behavior_prediction",
            "sentiment_analysis", "blue_ocean_analysis", "price_war_simulator"
        ],
        "timestamp": datetime.now().isoformat()
    }

# === 1. REAL-TIME COMPETITOR RADAR ===

@app.get("/api/radar/status")
async def get_radar_status():
    """Get current monitoring status."""
    return await radar_service.get_monitoring_status()

@app.post("/api/radar/start")
async def start_competitor_monitoring(
    competitors: List[str] = Query(..., description="List of competitor names to monitor"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Start real-time competitor monitoring."""
    result = await radar_service.start_monitoring(competitors)
    return result

@app.post("/api/radar/stop")
async def stop_competitor_monitoring():
    """Stop real-time competitor monitoring."""
    return await radar_service.stop_monitoring()

@app.get("/api/radar/alerts")
async def get_recent_alerts(
    hours: int = Query(24, description="Hours to look back for alerts"),
    db: Session = Depends(get_database)
):
    """Get recent competitor alerts."""
    from .models import MarketMovement
    from sqlalchemy import desc, and_
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    alerts = db.query(MarketMovement).filter(
        and_(
            MarketMovement.detected_at >= cutoff_time,
            MarketMovement.impact_score > 30  # High impact only
        )
    ).order_by(desc(MarketMovement.detected_at)).limit(50).all()
    
    return {
        "alerts": [
            {
                "id": alert.id,
                "competitor": alert.competitor_name,
                "type": alert.movement_type,
                "description": alert.description,
                "impact_score": alert.impact_score,
                "detected_at": alert.detected_at.isoformat(),
                "metadata": alert.metadata
            }
            for alert in alerts
        ],
        "total": len(alerts),
        "period_hours": hours
    }

# === 2. DYNAMIC AI STRATEGY ADJUSTMENT ===

@app.get("/api/strategy/analyze")
async def analyze_market_strategy(
    category: str = Query(..., description="Product category to analyze"),
    db: Session = Depends(get_database)
):
    """Analyze market conditions and recommend strategy."""
    return await strategy_service.analyze_market_conditions(category, db)

@app.post("/api/strategy/auto-adjust")
async def auto_adjust_strategy(
    user_id: str = Query(..., description="User ID"),
    current_strategy: str = Query(..., description="Current strategy (aggressive/defensive/conservative)")
):
    """Automatically adjust strategy based on market conditions."""
    return await strategy_service.auto_adjust_strategy(user_id, current_strategy)

@app.get("/api/strategy/recommendations")
async def get_strategy_recommendations(
    category: str = Query(..., description="Product category"),
    user_budget: float = Query(None, description="User's monthly budget"),
    target_acos: float = Query(None, description="Target ACOS percentage")
):
    """Get personalized strategy recommendations."""
    market_analysis = await strategy_service.analyze_market_conditions(category)
    
    recommendations = []
    strategy = market_analysis["recommended_strategy"]
    
    if strategy == "aggressive":
        recommendations.extend([
            "Increase budget by 20-30% to capture market share",
            "Expand keyword targeting to include high-volume terms",
            "Consider premium ad placements",
            "Launch promotional campaigns"
        ])
    elif strategy == "defensive":
        recommendations.extend([
            "Focus on high-performing keywords only",
            "Optimize for efficiency over volume",
            "Protect core product positioning",
            "Monitor competitor moves closely"
        ])
    else:  # conservative
        recommendations.extend([
            "Maintain current spend levels",
            "Focus on organic optimization",
            "Test small budget increases gradually",
            "Wait for market stabilization"
        ])
    
    return {
        "strategy": strategy,
        "recommendations": recommendations,
        "market_analysis": market_analysis,
        "generated_at": datetime.utcnow().isoformat()
    }

# === 3. COMPETITOR BEHAVIOR PREDICTION ===

@app.get("/api/prediction/competitor-actions")
async def predict_competitor_actions(
    competitor_name: str = Query(..., description="Competitor name"),
    days_ahead: int = Query(7, description="Days to predict ahead"),
    db: Session = Depends(get_database)
):
    """Predict competitor actions using ML analysis."""
    return await prediction_service.predict_competitor_actions(competitor_name, days_ahead, db)

@app.get("/api/prediction/price-wars")
async def predict_price_wars(
    category: str = Query(..., description="Product category"),
    db: Session = Depends(get_database)
):
    """Predict likelihood of price wars in category."""
    return await prediction_service.predict_price_wars(category, db)

@app.get("/api/prediction/market-trends")
async def predict_market_trends(
    category: str = Query(..., description="Product category"),
    timeframe: int = Query(30, description="Prediction timeframe in days")
):
    """Predict market trends and competitor behavior patterns."""
    # Combine multiple prediction models
    price_war_prediction = await prediction_service.predict_price_wars(category)
    
    # Simulate trend analysis
    trends = {
        "category": category,
        "timeframe_days": timeframe,
        "predicted_trends": [
            {
                "trend_type": "pricing",
                "direction": "increasing",
                "confidence": 0.7,
                "impact": "medium"
            },
            {
                "trend_type": "competition",
                "direction": "intensifying", 
                "confidence": 0.8,
                "impact": "high"
            }
        ],
        "price_war_risk": price_war_prediction,
        "recommendations": [
            "Monitor pricing closely",
            "Prepare defensive strategies",
            "Consider market expansion"
        ],
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return trends

# === 4. INTELLIGENT BENCHMARKING ===

@app.get("/api/benchmark/performance")
async def benchmark_performance(
    user_id: str = Query(..., description="User ID"),
    category: str = Query(..., description="Product category"),
    metrics: List[str] = Query(["conversion_rate", "cpc", "acos"], description="Metrics to benchmark")
):
    """Benchmark user performance against competitors."""
    # Simulate benchmark analysis
    benchmark_data = {
        "user_id": user_id,
        "category": category,
        "benchmarks": {},
        "gaps": [],
        "opportunities": [],
        "analyzed_at": datetime.utcnow().isoformat()
    }
    
    for metric in metrics:
        user_value = round(random.uniform(2, 8), 2) if metric == "conversion_rate" else round(random.uniform(0.5, 3.0), 2)
        market_avg = round(random.uniform(3, 10), 2) if metric == "conversion_rate" else round(random.uniform(0.8, 2.5), 2)
        
        benchmark_data["benchmarks"][metric] = {
            "user_value": user_value,
            "market_average": market_avg,
            "percentile": round(random.uniform(20, 90), 1),
            "gap": round(market_avg - user_value, 2)
        }
        
        if user_value < market_avg:
            benchmark_data["gaps"].append(f"{metric.replace('_', ' ').title()} below market average")
        else:
            benchmark_data["opportunities"].append(f"Strong {metric.replace('_', ' ')} performance")
    
    return benchmark_data

@app.get("/api/benchmark/competitors")
async def benchmark_against_competitors(
    category: str = Query(..., description="Product category"),
    competitors: List[str] = Query(..., description="Specific competitors to benchmark against")
):
    """Direct benchmark against specific competitors."""
    import random
    
    benchmark_results = {
        "category": category,
        "competitor_comparison": [],
        "market_position": "middle_tier",  # top_tier, middle_tier, bottom_tier
        "improvement_areas": [],
        "competitive_advantages": [],
        "analyzed_at": datetime.utcnow().isoformat()
    }
    
    for competitor in competitors:
        comparison = {
            "competitor": competitor,
            "metrics": {
                "market_share": round(random.uniform(5, 25), 1),
                "avg_rating": round(random.uniform(3.5, 4.8), 1),
                "price_competitiveness": round(random.uniform(0.7, 1.3), 2),
                "ad_visibility": round(random.uniform(20, 80), 1)
            },
            "relative_position": random.choice(["ahead", "behind", "similar"])
        }
        benchmark_results["competitor_comparison"].append(comparison)
    
    return benchmark_results

# === 5. BLUE OCEAN OPPORTUNITIES ===

@app.get("/api/blue-ocean/keywords")
async def find_blue_ocean_keywords(
    category: str = Query(..., description="Product category"),
    limit: int = Query(50, description="Maximum number of keywords to return"),
    db: Session = Depends(get_database)
):
    """Find low competition, high opportunity keywords."""
    return await blue_ocean_service.find_low_competition_keywords(category, limit, db)

@app.get("/api/blue-ocean/market-gaps")
async def identify_market_gaps(
    category: str = Query(..., description="Product category")
):
    """Identify market gaps and blue ocean opportunities."""
    return await blue_ocean_service.identify_market_gaps(category)

@app.get("/api/blue-ocean/products")
async def suggest_blue_ocean_products(
    category: str = Query(..., description="Product category"),
    price_range: str = Query("medium", description="Price range: low, medium, high")
):
    """Suggest product opportunities in blue ocean markets."""
    import random
    
    suggestions = {
        "category": category,
        "price_range": price_range,
        "product_opportunities": [
            {
                "product_type": f"Eco-friendly {category}",
                "opportunity_score": round(random.uniform(70, 95), 1),
                "competition_level": "low",
                "market_size": "growing",
                "entry_barriers": "low"
            },
            {
                "product_type": f"Premium {category} with AI features",
                "opportunity_score": round(random.uniform(60, 85), 1),
                "competition_level": "medium",
                "market_size": "emerging",
                "entry_barriers": "medium"
            }
        ],
        "analysis_date": datetime.utcnow().isoformat()
    }
    
    return suggestions

# === 6. PRICE WAR SIMULATOR ===

@app.post("/api/simulator/price-war")
async def simulate_price_war(
    category: str = Query(..., description="Product category"),
    initial_price: float = Query(..., description="Your current price"),
    competitor_prices: List[float] = Query(..., description="Competitor prices"),
    simulation_days: int = Query(30, description="Simulation period in days")
):
    """Simulate price war scenarios and outcomes."""
    import random
    
    scenarios = []
    
    # Scenario 1: Aggressive pricing
    aggressive_price = initial_price * 0.85
    scenarios.append({
        "scenario": "aggressive_pricing",
        "new_price": aggressive_price,
        "predicted_outcomes": {
            "volume_change": round(random.uniform(15, 40), 1),
            "revenue_change": round(random.uniform(-5, 25), 1),
            "margin_impact": round(random.uniform(-25, -10), 1),
            "market_share_gain": round(random.uniform(2, 8), 1)
        },
        "risks": ["Margin compression", "Competitor retaliation", "Brand devaluation"],
        "timeline": f"{simulation_days} days"
    })
    
    # Scenario 2: Defensive pricing
    defensive_price = min(competitor_prices) * 0.98
    scenarios.append({
        "scenario": "defensive_pricing",
        "new_price": defensive_price,
        "predicted_outcomes": {
            "volume_change": round(random.uniform(5, 15), 1),
            "revenue_change": round(random.uniform(-10, 10), 1),
            "margin_impact": round(random.uniform(-15, -5), 1),
            "market_share_gain": round(random.uniform(0, 3), 1)
        },
        "risks": ["Limited growth", "Continued pressure"],
        "timeline": f"{simulation_days} days"
    })
    
    return {
        "category": category,
        "current_price": initial_price,
        "competitor_prices": competitor_prices,
        "scenarios": scenarios,
        "recommendations": [
            "Monitor competitor responses closely",
            "Prepare value-added alternatives",
            "Consider non-price differentiation"
        ],
        "simulated_at": datetime.utcnow().isoformat()
    }

# === 7. VISUAL HISTORY AND ANALYTICS ===

@app.get("/api/analytics/timeline")
async def get_competitor_timeline(
    competitor_name: str = Query(..., description="Competitor name"),
    days_back: int = Query(30, description="Days of history to retrieve"),
    db: Session = Depends(get_database)
):
    """Get visual timeline of competitor movements."""
    from .models import MarketMovement
    from sqlalchemy import desc, and_
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    movements = db.query(MarketMovement).filter(
        and_(
            MarketMovement.competitor_name == competitor_name,
            MarketMovement.detected_at >= cutoff_date
        )
    ).order_by(desc(MarketMovement.detected_at)).all()
    
    timeline = []
    for movement in movements:
        timeline.append({
            "date": movement.detected_at.isoformat(),
            "type": movement.movement_type,
            "description": movement.description,
            "impact_score": movement.impact_score,
            "metadata": movement.movement_metadata
        })
    
    return {
        "competitor": competitor_name,
        "period_days": days_back,
        "timeline": timeline,
        "total_events": len(timeline),
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/api/analytics/market-overview")
async def get_market_overview(
    category: str = Query(..., description="Product category"),
    db: Session = Depends(get_database)
):
    """Get comprehensive market overview and analytics."""
    # Get recent market data
    from .models import MarketMovement, CompetitorProfile
    from sqlalchemy import func, desc
    
    # Market activity in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(MarketMovement).filter(
        MarketMovement.detected_at >= week_ago
    ).count()
    
    # Top active competitors
    top_competitors = db.query(
        MarketMovement.competitor_name,
        func.count(MarketMovement.id).label('activity_count')
    ).filter(
        MarketMovement.detected_at >= week_ago
    ).group_by(MarketMovement.competitor_name).order_by(
        desc('activity_count')
    ).limit(10).all()
    
    return {
        "category": category,
        "market_activity": {
            "total_movements": recent_activity,
            "period": "7 days",
            "activity_level": "high" if recent_activity > 50 else "medium" if recent_activity > 20 else "low"
        },
        "top_competitors": [
            {"name": comp.competitor_name, "activity_count": comp.activity_count}
            for comp in top_competitors
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

# === 8. SENTIMENT ANALYSIS ===

@app.get("/api/sentiment/competitor")
async def analyze_competitor_sentiment(
    competitor_name: str = Query(..., description="Competitor name")
):
    """Analyze competitor sentiment from reviews and social media."""
    return await sentiment_service.analyze_competitor_reviews(competitor_name)

@app.get("/api/sentiment/comparison")
async def compare_competitor_sentiment(
    competitors: List[str] = Query(..., description="List of competitors to compare"),
    metric: str = Query("overall", description="Sentiment metric to compare")
):
    """Compare sentiment across multiple competitors."""
    comparisons = []
    
    for competitor in competitors:
        sentiment_data = await sentiment_service.analyze_competitor_reviews(competitor)
        comparisons.append({
            "competitor": competitor,
            "sentiment_score": sentiment_data["sentiment_score"],
            "total_reviews": sentiment_data["total_reviews"],
            "positive_aspects": sentiment_data["positive_aspects"],
            "negative_aspects": sentiment_data["negative_aspects"]
        })
    
    # Sort by sentiment score
    comparisons.sort(key=lambda x: x["sentiment_score"], reverse=True)
    
    return {
        "comparison_metric": metric,
        "competitors": comparisons,
        "market_leader": comparisons[0]["competitor"] if comparisons else None,
        "analysis_date": datetime.utcnow().isoformat()
    }

# === 9. MANUAL PRODUCT SELECTION ===

@app.post("/api/monitoring/lists", response_model=MonitoringListResponse)
async def create_monitoring_list(
    monitoring_list: MonitoringListCreate,
    db: Session = Depends(get_database)
):
    """Create a custom monitoring list."""
    from .models import UserMonitoringList
    
    db_list = UserMonitoringList(
        user_id=monitoring_list.user_id,
        list_name=monitoring_list.list_name,
        competitor_names=monitoring_list.competitor_names,
        product_ids=monitoring_list.product_ids,
        keywords=monitoring_list.keywords
    )
    
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    
    return db_list

@app.get("/api/monitoring/lists")
async def get_monitoring_lists(
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_database)
):
    """Get user's monitoring lists."""
    from .models import UserMonitoringList
    
    lists = db.query(UserMonitoringList).filter(
        UserMonitoringList.user_id == user_id,
        UserMonitoringList.is_active == True
    ).all()
    
    return {
        "user_id": user_id,
        "monitoring_lists": [
            {
                "id": lst.id,
                "list_name": lst.list_name,
                "competitor_names": lst.competitor_names,
                "product_ids": lst.product_ids,
                "keywords": lst.keywords,
                "created_at": lst.created_at.isoformat()
            }
            for lst in lists
        ],
        "total": len(lists)
    }

@app.delete("/api/monitoring/lists/{list_id}")
async def delete_monitoring_list(
    list_id: int,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_database)
):
    """Delete a monitoring list."""
    from .models import UserMonitoringList
    
    monitoring_list = db.query(UserMonitoringList).filter(
        UserMonitoringList.id == list_id,
        UserMonitoringList.user_id == user_id
    ).first()
    
    if not monitoring_list:
        raise HTTPException(status_code=404, detail="Monitoring list not found")
    
    monitoring_list.is_active = False
    db.commit()
    
    return {"message": "Monitoring list deleted successfully"}

# === 10. SEGMENT-SPECIFIC RECOMMENDATIONS ===

@app.get("/api/recommendations/segment")
async def get_segment_recommendations(
    segment: str = Query(..., description="Business segment: B2B, B2C, niche"),
    category: str = Query(..., description="Product category"),
    budget_range: str = Query("medium", description="Budget range: low, medium, high")
):
    """Get segment-specific competitive strategies."""
    recommendations = {
        "segment": segment,
        "category": category,
        "budget_range": budget_range,
        "strategies": [],
        "tactics": [],
        "kpis": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    
    if segment.lower() == "b2b":
        recommendations["strategies"] = [
            "Focus on value proposition over price",
            "Target decision-makers with professional content",
            "Build long-term relationships",
            "Emphasize ROI and business benefits"
        ]
        recommendations["tactics"] = [
            "LinkedIn advertising priority",
            "Industry-specific keyword targeting",
            "Content marketing emphasis",
            "Account-based marketing approach"
        ]
        recommendations["kpis"] = ["Lead quality", "Customer lifetime value", "Sales cycle length"]
        
    elif segment.lower() == "b2c":
        recommendations["strategies"] = [
            "Emotional connection and brand appeal",
            "Price competitiveness important",
            "Social proof and reviews crucial",
            "Seasonal and trend-based campaigns"
        ]
        recommendations["tactics"] = [
            "Social media advertising",
            "Influencer partnerships",
            "Promotional campaigns",
            "Mobile-first approach"
        ]
        recommendations["kpis"] = ["Conversion rate", "Brand awareness", "Customer acquisition cost"]
        
    else:  # niche
        recommendations["strategies"] = [
            "Deep specialization advantage",
            "Community building approach",
            "Expert positioning",
            "Personalized customer experience"
        ]
        recommendations["tactics"] = [
            "Long-tail keyword focus",
            "Niche platform advertising",
            "Expert content creation",
            "Direct customer engagement"
        ]
        recommendations["kpis"] = ["Market share in niche", "Customer loyalty", "Expert recognition"]
    
    return recommendations

# === LEGACY ENDPOINTS (maintained for compatibility) ===

@app.get("/api/top-sellers")
async def get_top_sellers():
    """Legacy endpoint - Get top sellers data."""
    return {
        "top_sellers": [
            {"seller": "TechStore", "products": 1500, "revenue": 2500000},
            {"seller": "ElectroMax", "products": 1200, "revenue": 1800000},
            {"seller": "GadgetWorld", "products": 980, "revenue": 1500000}
        ], 
        "timestamp": datetime.now().isoformat(),
        "note": "Legacy endpoint - consider using /api/benchmark/competitors"
    }

@app.get("/api/pricing-strategies")
async def analyze_pricing():
    """Legacy endpoint - Get pricing strategies data."""
    return {
        "strategies": [
            {"strategy": "premium", "avg_price": 899, "market_share": 0.3},
            {"strategy": "competitive", "avg_price": 649, "market_share": 0.45},
            {"strategy": "budget", "avg_price": 399, "market_share": 0.25}
        ], 
        "timestamp": datetime.now().isoformat(),
        "note": "Legacy endpoint - consider using /api/prediction/market-trends"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)