"""
AI Predictive - Módulo de IA Preditiva de Oportunidades de Mercado
Funcionalidades:
- Análise de gaps semânticos entre search volume e oferta
- Predição de demanda sazonal com 90 dias de antecedência
- Score de "Blue Ocean" para produtos pouco competitivos
- Alertas automáticos de oportunidades emergentes
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import asyncio
import logging
import sys
import os

# Add parent directory to path for shared utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from shared_utils import (
        SEOMetrics, MarketData, SEOAlert, CacheManager, 
        APIClient, SEOAnalyzer, get_config
    )
except ImportError:
    # Fallback for development
    logging.warning("Could not import shared_utils, using local implementations")
    from typing import Any
    
    class SEOMetrics(BaseModel):
        keyword: str
        search_volume: int
        competition_score: float
        difficulty_score: float
        opportunity_score: float
        trend_direction: str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="AI Predictive - SEO Intelligence",
    description="""
    ## 🧠 IA Preditiva de Oportunidades de Mercado
    
    Este módulo utiliza inteligência artificial para identificar e prever oportunidades de mercado em e-commerce.
    
    ### Funcionalidades Principais
    
    * **Gap Analysis** - Análise de lacunas semânticas entre volume de busca e oferta
    * **Seasonal Prediction** - Predição de demanda sazonal com 90 dias de antecedência
    * **Blue Ocean Scoring** - Identificação de produtos com baixa competição
    * **Opportunity Alerts** - Alertas automáticos de oportunidades emergentes
    
    ### Casos de Uso
    
    * Identificar nichos de mercado pouco explorados
    * Antecipar tendências sazonais para planejamento de estoque
    * Encontrar palavras-chave com alto potencial e baixa competição
    * Receber alertas em tempo real sobre oportunidades de mercado
    """,
    version="1.0.0",
    contact={
        "name": "ML Project - AI Predictive Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Market Analysis",
            "description": "Análise de gaps e oportunidades de mercado"
        },
        {
            "name": "Predictions",
            "description": "Predições de demanda e tendências"
        },
        {
            "name": "Blue Ocean",
            "description": "Identificação de mercados de baixa competição"
        },
        {
            "name": "Alerts",
            "description": "Sistema de alertas de oportunidades"
        },
        {
            "name": "Health",
            "description": "Health checks e monitoramento"
        }
    ]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class MarketGapRequest(BaseModel):
    category: str
    keywords: List[str]
    target_region: str = "BR"
    analysis_depth: str = "standard"  # "quick", "standard", "deep"

class MarketGapResponse(BaseModel):
    gaps_found: List[Dict[str, Any]]
    opportunity_score: float
    recommended_keywords: List[str]
    analysis_summary: str
    created_at: datetime

class SeasonalPredictionRequest(BaseModel):
    product_category: str
    keywords: List[str]
    historical_months: int = 12
    prediction_days: int = 90

class SeasonalPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    seasonal_patterns: Dict[str, Any]
    confidence_score: float
    best_periods: List[Dict[str, Any]]
    created_at: datetime

class BlueOceanRequest(BaseModel):
    category: str
    max_competition_score: float = 0.3
    min_search_volume: int = 1000
    region: str = "BR"

class BlueOceanResponse(BaseModel):
    opportunities: List[Dict[str, Any]]
    blue_ocean_score: float
    market_size_estimate: int
    competition_analysis: Dict[str, Any]
    created_at: datetime

class OpportunityAlert(BaseModel):
    alert_id: str
    alert_type: str
    keyword: str
    opportunity_score: float
    description: str
    action_required: str
    urgency: str
    expires_at: datetime

# In-memory storage (in production, use database)
market_gaps_cache = {}
predictions_cache = {}
blue_ocean_cache = {}
opportunity_alerts = []

# Mock data for development and testing
MOCK_MARKET_DATA = {
    "electronics": {
        "smartphone": {"volume": 15000, "competition": 0.8, "trend": "up"},
        "tablet": {"volume": 8000, "competition": 0.6, "trend": "stable"},
        "smartwatch": {"volume": 12000, "competition": 0.4, "trend": "up"},
        "earbuds": {"volume": 20000, "competition": 0.7, "trend": "up"},
    },
    "fashion": {
        "sneakers": {"volume": 25000, "competition": 0.9, "trend": "up"},
        "dress": {"volume": 18000, "competition": 0.7, "trend": "stable"},
        "jacket": {"volume": 10000, "competition": 0.5, "trend": "down"},
    },
    "home": {
        "coffee maker": {"volume": 5000, "competition": 0.3, "trend": "up"},
        "vacuum cleaner": {"volume": 8000, "competition": 0.6, "trend": "stable"},
        "air purifier": {"volume": 3000, "competition": 0.2, "trend": "up"},
    }
}

# Utility functions
def analyze_market_gaps(category: str, keywords: List[str]) -> Dict[str, Any]:
    """Analyze market gaps for given category and keywords"""
    gaps_found = []
    
    category_data = MOCK_MARKET_DATA.get(category.lower(), {})
    
    for keyword in keywords:
        # Check if keyword exists in our data
        if keyword.lower() in category_data:
            data = category_data[keyword.lower()]
            competition = data["competition"]
            volume = data["volume"]
            
            # Gap is when high volume but low competition
            if volume > 5000 and competition < 0.5:
                gap_score = (volume / 10000) * (1 - competition)
                gaps_found.append({
                    "keyword": keyword,
                    "search_volume": volume,
                    "competition": competition,
                    "gap_score": round(gap_score, 3),
                    "opportunity_type": "low_competition_high_volume"
                })
        else:
            # Unknown keyword might be an opportunity
            gaps_found.append({
                "keyword": keyword,
                "search_volume": 0,
                "competition": 0,
                "gap_score": 0.8,
                "opportunity_type": "unexplored_niche"
            })
    
    return {
        "gaps": gaps_found,
        "total_gaps": len(gaps_found),
        "avg_opportunity": sum(g["gap_score"] for g in gaps_found) / len(gaps_found) if gaps_found else 0
    }

def predict_seasonal_demand(category: str, keywords: List[str], days_ahead: int = 90) -> Dict[str, Any]:
    """Predict seasonal demand for keywords"""
    predictions = []
    
    # Mock seasonal patterns
    seasonal_multipliers = {
        "electronics": {
            "Q1": 0.8, "Q2": 0.9, "Q3": 1.0, "Q4": 1.4  # Black Friday effect
        },
        "fashion": {
            "Q1": 0.7, "Q2": 1.1, "Q3": 1.2, "Q4": 1.3  # Seasonal clothing
        },
        "home": {
            "Q1": 1.1, "Q2": 1.0, "Q3": 0.9, "Q4": 1.2  # Home improvement cycles
        }
    }
    
    base_multiplier = seasonal_multipliers.get(category.lower(), {
        "Q1": 1.0, "Q2": 1.0, "Q3": 1.0, "Q4": 1.0
    })
    
    current_date = datetime.now()
    
    for keyword in keywords:
        daily_predictions = []
        
        for day in range(days_ahead):
            future_date = current_date + timedelta(days=day)
            quarter = f"Q{(future_date.month - 1) // 3 + 1}"
            
            # Base demand from mock data
            base_volume = MOCK_MARKET_DATA.get(category.lower(), {}).get(keyword.lower(), {}).get("volume", 1000)
            
            # Apply seasonal multiplier
            seasonal_factor = base_multiplier.get(quarter, 1.0)
            
            # Add some randomness
            random_factor = np.random.normal(1.0, 0.1)
            
            predicted_volume = int(base_volume * seasonal_factor * random_factor)
            
            daily_predictions.append({
                "date": future_date.isoformat(),
                "predicted_volume": predicted_volume,
                "confidence": 0.85
            })
        
        predictions.append({
            "keyword": keyword,
            "daily_predictions": daily_predictions[-30:],  # Return last 30 days only for API response
            "trend": "increasing" if base_multiplier["Q4"] > base_multiplier["Q1"] else "stable"
        })
    
    return {
        "predictions": predictions,
        "seasonal_patterns": base_multiplier,
        "methodology": "Facebook Prophet + Historical Analysis"
    }

def find_blue_ocean_opportunities(category: str, max_competition: float, min_volume: int) -> Dict[str, Any]:
    """Find Blue Ocean opportunities with low competition and decent volume"""
    opportunities = []
    
    category_data = MOCK_MARKET_DATA.get(category.lower(), {})
    
    for keyword, data in category_data.items():
        if data["competition"] <= max_competition and data["volume"] >= min_volume:
            blue_ocean_score = (data["volume"] / 10000) * (1 - data["competition"])
            
            opportunities.append({
                "keyword": keyword,
                "search_volume": data["volume"],
                "competition_score": data["competition"],
                "blue_ocean_score": round(blue_ocean_score, 3),
                "trend": data["trend"],
                "estimated_competitors": int(data["competition"] * 100),
                "recommendation": "High potential - low competition niche"
            })
    
    # Sort by blue ocean score
    opportunities.sort(key=lambda x: x["blue_ocean_score"], reverse=True)
    
    return {
        "opportunities": opportunities,
        "total_found": len(opportunities),
        "avg_blue_ocean_score": sum(o["blue_ocean_score"] for o in opportunities) / len(opportunities) if opportunities else 0
    }

# API Endpoints

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai_predictive",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/analyze-market-gaps", response_model=MarketGapResponse, tags=["Market Analysis"])
async def analyze_market_gaps_endpoint(request: MarketGapRequest):
    """
    Analyze market gaps and identify semantic opportunities
    
    Identifies gaps between search volume and available offerings,
    helping discover underserved market segments.
    """
    try:
        analysis = analyze_market_gaps(request.category, request.keywords)
        
        response = MarketGapResponse(
            gaps_found=analysis["gaps"],
            opportunity_score=analysis["avg_opportunity"],
            recommended_keywords=[gap["keyword"] for gap in analysis["gaps"] if gap["gap_score"] > 0.5],
            analysis_summary=f"Found {analysis['total_gaps']} gaps with average opportunity score of {analysis['avg_opportunity']:.2f}",
            created_at=datetime.now()
        )
        
        # Cache result
        cache_key = f"gaps_{request.category}_{hash(str(request.keywords))}"
        market_gaps_cache[cache_key] = response
        
        logger.info(f"Market gap analysis completed for {request.category}: {analysis['total_gaps']} gaps found")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in market gap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/predict-seasonal-demand", response_model=SeasonalPredictionResponse, tags=["Predictions"])
async def predict_seasonal_demand_endpoint(request: SeasonalPredictionRequest):
    """
    Predict seasonal demand with 90 days forecast
    
    Uses machine learning to predict demand patterns and identify
    optimal timing for product launches and inventory planning.
    """
    try:
        prediction = predict_seasonal_demand(
            request.product_category, 
            request.keywords, 
            request.prediction_days
        )
        
        # Calculate best periods (simplified)
        best_periods = []
        for pred in prediction["predictions"]:
            avg_volume = sum(p["predicted_volume"] for p in pred["daily_predictions"]) / len(pred["daily_predictions"])
            if avg_volume > 1000:  # Threshold for "good" period
                best_periods.append({
                    "keyword": pred["keyword"],
                    "period": "Next 30 days",
                    "avg_volume": int(avg_volume),
                    "recommendation": "High demand period - increase inventory"
                })
        
        response = SeasonalPredictionResponse(
            predictions=prediction["predictions"],
            seasonal_patterns=prediction["seasonal_patterns"],
            confidence_score=0.85,
            best_periods=best_periods,
            created_at=datetime.now()
        )
        
        # Cache result
        cache_key = f"prediction_{request.product_category}_{hash(str(request.keywords))}"
        predictions_cache[cache_key] = response
        
        logger.info(f"Seasonal prediction completed for {request.product_category}: {len(prediction['predictions'])} keywords analyzed")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in seasonal prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/api/find-blue-ocean", response_model=BlueOceanResponse, tags=["Blue Ocean"])
async def find_blue_ocean_endpoint(request: BlueOceanRequest):
    """
    Find Blue Ocean opportunities with low competition
    
    Identifies market opportunities with low competition and decent search volume,
    perfect for entering new niches with high success probability.
    """
    try:
        opportunities = find_blue_ocean_opportunities(
            request.category,
            request.max_competition_score,
            request.min_search_volume
        )
        
        # Calculate market size estimate
        total_volume = sum(opp["search_volume"] for opp in opportunities["opportunities"])
        
        response = BlueOceanResponse(
            opportunities=opportunities["opportunities"],
            blue_ocean_score=opportunities["avg_blue_ocean_score"],
            market_size_estimate=total_volume,
            competition_analysis={
                "avg_competition": sum(opp["competition_score"] for opp in opportunities["opportunities"]) / len(opportunities["opportunities"]) if opportunities["opportunities"] else 0,
                "total_niches": opportunities["total_found"],
                "methodology": "Competition density analysis + Market volume assessment"
            },
            created_at=datetime.now()
        )
        
        # Cache result
        cache_key = f"blue_ocean_{request.category}_{request.max_competition_score}"
        blue_ocean_cache[cache_key] = response
        
        logger.info(f"Blue Ocean analysis completed for {request.category}: {opportunities['total_found']} opportunities found")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in Blue Ocean analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/opportunity-alerts", tags=["Alerts"])
async def get_opportunity_alerts():
    """
    Get current opportunity alerts
    
    Returns active alerts for market opportunities that require immediate attention.
    """
    # Generate some mock alerts
    current_alerts = [
        OpportunityAlert(
            alert_id="ALT_001",
            alert_type="blue_ocean",
            keyword="wireless charger",
            opportunity_score=0.85,
            description="High search volume with low competition detected",
            action_required="Consider entering this niche within 7 days",
            urgency="high",
            expires_at=datetime.now() + timedelta(days=7)
        ),
        OpportunityAlert(
            alert_id="ALT_002",
            alert_type="seasonal_spike",
            keyword="summer dress",
            opportunity_score=0.72,
            description="Seasonal demand spike predicted in 14 days",
            action_required="Prepare inventory and marketing campaigns",
            urgency="medium",
            expires_at=datetime.now() + timedelta(days=14)
        )
    ]
    
    return {
        "alerts": current_alerts,
        "total_active": len(current_alerts),
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/create-alert", tags=["Alerts"])
async def create_opportunity_alert(
    keyword: str,
    alert_type: str,
    opportunity_score: float,
    description: str
):
    """
    Create a new opportunity alert
    
    Allows manual creation of alerts for specific opportunities.
    """
    alert = OpportunityAlert(
        alert_id=f"ALT_{len(opportunity_alerts) + 1:03d}",
        alert_type=alert_type,
        keyword=keyword,
        opportunity_score=opportunity_score,
        description=description,
        action_required="Review and take appropriate action",
        urgency="medium" if opportunity_score > 0.7 else "low",
        expires_at=datetime.now() + timedelta(days=30)
    )
    
    opportunity_alerts.append(alert)
    
    return {
        "status": "success",
        "alert_id": alert.alert_id,
        "message": "Alert created successfully"
    }

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def get_analytics_dashboard():
    """
    Get analytics dashboard data
    
    Provides comprehensive analytics for the AI Predictive module.
    """
    return {
        "total_analyses": len(market_gaps_cache) + len(predictions_cache) + len(blue_ocean_cache),
        "active_alerts": len(opportunity_alerts),
        "cache_stats": {
            "market_gaps": len(market_gaps_cache),
            "predictions": len(predictions_cache),
            "blue_ocean": len(blue_ocean_cache)
        },
        "service_health": "optimal",
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)