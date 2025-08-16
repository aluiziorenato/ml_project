"""
Dynamic Optimization - Sistema de Otimização Dinâmica
Funcionalidades:
- Rewrite automático de títulos baseado em performance
- Sugestão de preços ótimos por keyword
- Timing ideal para publicação/relisting
- A/B testing contínuo de variações
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
import random
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="Dynamic Optimization - SEO Intelligence",
    description="""
    ## ⚡ Sistema de Otimização Dinâmica
    
    Este módulo utiliza inteligência artificial para otimização contínua e automática de conteúdo e estratégias.
    
    ### Funcionalidades Principais
    
    * **Title Rewriting** - Reescrita automática de títulos baseada em performance
    * **Price Optimization** - Sugestão de preços ótimos por palavra-chave
    * **Timing Optimization** - Melhor momento para publicação/relisting
    * **A/B Testing** - Testes contínuos de variações automáticas
    
    ### Casos de Uso
    
    * Melhorar CTR através de títulos otimizados
    * Maximizar conversão com preços inteligentes
    * Otimizar timing de publicações para máximo alcance
    * Executar A/B tests automáticos para melhoria contínua
    """,
    version="1.0.0",
    openapi_tags=[
        {"name": "Title Optimization", "description": "Otimização automática de títulos"},
        {"name": "Price Optimization", "description": "Sugestão de preços ótimos"},
        {"name": "Timing", "description": "Otimização de timing de publicação"},
        {"name": "A/B Testing", "description": "Testes A/B automáticos"},
        {"name": "Health", "description": "Health checks e monitoramento"}
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
class TitleOptimizationRequest(BaseModel):
    original_title: str
    category: str
    keywords: List[str]
    target_audience: str
    current_ctr: Optional[float] = None
    optimization_goal: str = "ctr"  # "ctr", "conversions", "seo"

class TitleOptimizationResponse(BaseModel):
    optimized_titles: List[Dict[str, Any]]
    best_title: str
    improvement_estimate: float
    optimization_reasoning: str
    ab_test_suggestion: Dict[str, Any]
    created_at: datetime

class PriceOptimizationRequest(BaseModel):
    product_title: str
    category: str
    current_price: float
    keywords: List[str]
    competitor_prices: Optional[List[float]] = None
    target_margin: Optional[float] = None

class PriceOptimizationResponse(BaseModel):
    optimal_price: float
    price_range: Dict[str, float]
    pricing_strategy: str
    revenue_impact: Dict[str, Any]
    competitor_analysis: Dict[str, Any]
    created_at: datetime

class TimingOptimizationRequest(BaseModel):
    product_category: str
    target_audience: str
    content_type: str  # "listing", "repost", "promotion"
    timezone: str = "America/Sao_Paulo"

class TimingOptimizationResponse(BaseModel):
    optimal_times: List[Dict[str, Any]]
    best_day_of_week: str
    best_hour: int
    reasoning: str
    engagement_estimate: float
    created_at: datetime

class ABTestRequest(BaseModel):
    test_name: str
    variations: List[Dict[str, Any]]
    test_type: str  # "title", "price", "timing", "content"
    sample_size: int = 1000
    confidence_level: float = 0.95

class ABTestResponse(BaseModel):
    test_id: str
    status: str
    variations_performance: List[Dict[str, Any]]
    winning_variation: Optional[Dict[str, Any]] = None
    statistical_significance: float
    recommendation: str
    created_at: datetime

# In-memory storage
title_optimizations = {}
price_optimizations = {}
timing_optimizations = {}
ab_tests = {}

# Mock data and patterns
TITLE_PATTERNS = {
    "electronics": [
        "{brand} {product} - {feature} | {benefit}",
        "{product} {brand} {model} - {discount}% OFF",
        "🔥 {product} {feature} - {benefit} - {urgency}",
        "{product} ORIGINAL {brand} - {feature} + FRETE GRÁTIS"
    ],
    "fashion": [
        "{product} {style} - {season} {year} | {material}",
        "✨ {product} {brand} - {style} - {color}",
        "{product} {brand} ORIGINAL - {size} ao {size2}",
        "🎯 {product} {style} - {discount}% OFF - {urgency}"
    ],
    "home": [
        "{product} {brand} - {feature} | {room}",
        "🏠 {product} COMPLETO - {feature} - {warranty}",
        "{product} {material} - {size} - {benefit}",
        "{product} PREMIUM {brand} - {feature} + INSTALAÇÃO"
    ]
}

POWER_WORDS = {
    "urgency": ["ÚLTIMAS PEÇAS", "OFERTA LIMITADA", "SÓ HOJE", "ÚLTIMA CHANCE"],
    "benefits": ["FRETE GRÁTIS", "ENTREGA RÁPIDA", "GARANTIA TOTAL", "PARCELADO"],
    "quality": ["ORIGINAL", "PREMIUM", "PROFISSIONAL", "TOP DE LINHA"],
    "emotions": ["🔥", "✨", "🎯", "💥", "⭐", "🏆"]
}

# Utility functions
def generate_title_variations(original_title: str, category: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """Generate multiple title variations with different optimization strategies"""
    variations = []
    
    # Extract product info from original title
    product_info = {
        "brand": "",
        "product": "",
        "model": "",
        "feature": "",
        "benefit": ""
    }
    
    # Simple extraction (in production, use NLP)
    words = original_title.split()
    if len(words) > 1:
        product_info["brand"] = words[0] if words[0].isupper() else ""
        product_info["product"] = words[1] if len(words) > 1 else words[0]
        product_info["model"] = words[2] if len(words) > 2 else ""
    
    patterns = TITLE_PATTERNS.get(category.lower(), TITLE_PATTERNS["electronics"])
    
    for i, pattern in enumerate(patterns[:4]):  # Limit to 4 variations
        try:
            # Fill pattern with available info and keywords
            optimized_title = pattern.format(
                brand=product_info["brand"] or keywords[0] if keywords else "PREMIUM",
                product=product_info["product"] or keywords[1] if len(keywords) > 1 else "PRODUTO",
                model=product_info["model"] or "",
                feature=keywords[0] if keywords else "ALTA QUALIDADE",
                benefit=random.choice(POWER_WORDS["benefits"]),
                discount=random.choice([10, 15, 20, 25, 30]),
                urgency=random.choice(POWER_WORDS["urgency"]),
                season="VERÃO",
                year="2024",
                material="PREMIUM",
                color="AZUL",
                size="P",
                size2="XL",
                room="SALA",
                warranty="1 ANO"
            )
            
            # Clean up formatting
            optimized_title = re.sub(r'\s+', ' ', optimized_title)
            optimized_title = re.sub(r'\s-\s-\s', ' - ', optimized_title)
            
            score = random.uniform(0.7, 0.95)  # Mock performance score
            
            variations.append({
                "title": optimized_title,
                "strategy": ["seo", "emotional", "urgency", "benefit"][i],
                "predicted_ctr": score,
                "predicted_conversions": score * 0.8,
                "seo_score": score * 0.9,
                "character_count": len(optimized_title)
            })
        except KeyError:
            # Skip if pattern couldn't be filled
            continue
    
    return sorted(variations, key=lambda x: x["predicted_ctr"], reverse=True)

def calculate_optimal_price(current_price: float, category: str, competitor_prices: List[float] = None) -> Dict[str, Any]:
    """Calculate optimal price based on market analysis"""
    if competitor_prices is None:
        # Generate mock competitor prices
        competitor_prices = [
            current_price * random.uniform(0.8, 1.2) for _ in range(5)
        ]
    
    avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
    min_competitor_price = min(competitor_prices)
    max_competitor_price = max(competitor_prices)
    
    # Price optimization strategies
    strategies = {
        "competitive": min_competitor_price * 0.95,
        "premium": avg_competitor_price * 1.1,
        "value": avg_competitor_price * 0.98,
        "market_leader": max_competitor_price * 0.9
    }
    
    # Choose best strategy based on price position
    if current_price < avg_competitor_price:
        optimal_price = strategies["value"]
        strategy = "value"
    elif current_price > avg_competitor_price * 1.1:
        optimal_price = strategies["competitive"]
        strategy = "competitive"
    else:
        optimal_price = strategies["premium"]
        strategy = "premium"
    
    return {
        "optimal_price": round(optimal_price, 2),
        "strategy": strategy,
        "price_range": {
            "min": round(optimal_price * 0.9, 2),
            "max": round(optimal_price * 1.1, 2)
        },
        "competitor_analysis": {
            "avg_price": round(avg_competitor_price, 2),
            "min_price": round(min_competitor_price, 2),
            "max_price": round(max_competitor_price, 2),
            "price_position": "below" if optimal_price < avg_competitor_price else "above"
        }
    }

def find_optimal_timing(category: str, audience: str, content_type: str) -> Dict[str, Any]:
    """Find optimal timing for content publication"""
    
    # Mock optimal times based on research patterns
    optimal_patterns = {
        "electronics": {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_hours": [10, 14, 19, 21],
            "peak_engagement": "19:00-21:00"
        },
        "fashion": {
            "best_days": ["Friday", "Saturday", "Sunday"],
            "best_hours": [12, 15, 18, 20],
            "peak_engagement": "18:00-20:00"
        },
        "home": {
            "best_days": ["Saturday", "Sunday", "Monday"],
            "best_hours": [9, 11, 16, 18],
            "peak_engagement": "16:00-18:00"
        }
    }
    
    audience_adjustments = {
        "young_adults": {"hour_shift": +2, "weekend_preference": True},
        "professionals": {"hour_shift": -1, "weekday_preference": True},
        "families": {"hour_shift": 0, "weekend_preference": True}
    }
    
    pattern = optimal_patterns.get(category.lower(), optimal_patterns["electronics"])
    adjustment = audience_adjustments.get(audience.lower(), {"hour_shift": 0, "weekend_preference": False})
    
    # Adjust hours based on audience
    adjusted_hours = [(h + adjustment["hour_shift"]) % 24 for h in pattern["best_hours"]]
    
    return {
        "best_day": random.choice(pattern["best_days"]),
        "best_hour": random.choice(adjusted_hours),
        "optimal_times": [
            {
                "day": day,
                "hour": hour,
                "engagement_score": random.uniform(0.7, 0.95)
            }
            for day in pattern["best_days"][:3]
            for hour in adjusted_hours[:2]
        ],
        "reasoning": f"Based on {category} category patterns and {audience} behavior analysis"
    }

# API Endpoints

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "dynamic_optimization",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/optimize-title", response_model=TitleOptimizationResponse, tags=["Title Optimization"])
async def optimize_title(request: TitleOptimizationRequest):
    """
    Optimize titles automatically based on performance data
    
    Generates multiple title variations using AI and predicts their performance
    to help improve CTR and conversions.
    """
    try:
        variations = generate_title_variations(
            request.original_title,
            request.category,
            request.keywords
        )
        
        if not variations:
            raise HTTPException(status_code=400, detail="Could not generate title variations")
        
        best_variation = variations[0]
        improvement = (best_variation["predicted_ctr"] - (request.current_ctr or 0.5)) * 100
        
        response = TitleOptimizationResponse(
            optimized_titles=variations,
            best_title=best_variation["title"],
            improvement_estimate=round(improvement, 1),
            optimization_reasoning=f"Optimized for {request.optimization_goal} using {best_variation['strategy']} strategy",
            ab_test_suggestion={
                "test_type": "title_ab_test",
                "variations": [request.original_title, best_variation["title"]],
                "sample_size": 1000,
                "estimated_duration": "7 days"
            },
            created_at=datetime.now()
        )
        
        # Cache result
        cache_key = f"title_{hash(request.original_title)}"
        title_optimizations[cache_key] = response
        
        logger.info(f"Title optimization completed for: {request.original_title[:50]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in title optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/optimize-price", response_model=PriceOptimizationResponse, tags=["Price Optimization"])
async def optimize_price(request: PriceOptimizationRequest):
    """
    Suggest optimal pricing based on market analysis
    
    Analyzes competitor prices and market positioning to suggest
    the optimal price point for maximum revenue.
    """
    try:
        optimization = calculate_optimal_price(
            request.current_price,
            request.category,
            request.competitor_prices
        )
        
        # Calculate revenue impact
        price_change = (optimization["optimal_price"] - request.current_price) / request.current_price
        volume_impact = -price_change * 0.5  # Elasticity assumption
        revenue_impact = price_change + volume_impact
        
        response = PriceOptimizationResponse(
            optimal_price=optimization["optimal_price"],
            price_range=optimization["price_range"],
            pricing_strategy=optimization["strategy"],
            revenue_impact={
                "estimated_change": round(revenue_impact * 100, 1),
                "confidence": 0.8,
                "time_frame": "30 days"
            },
            competitor_analysis=optimization["competitor_analysis"],
            created_at=datetime.now()
        )
        
        # Cache result
        cache_key = f"price_{hash(request.product_title)}"
        price_optimizations[cache_key] = response
        
        logger.info(f"Price optimization completed for: {request.product_title[:50]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in price optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/optimize-timing", response_model=TimingOptimizationResponse, tags=["Timing"])
async def optimize_timing(request: TimingOptimizationRequest):
    """
    Find optimal timing for content publication
    
    Analyzes audience behavior patterns to determine the best
    times for maximum engagement and visibility.
    """
    try:
        timing = find_optimal_timing(
            request.product_category,
            request.target_audience,
            request.content_type
        )
        
        response = TimingOptimizationResponse(
            optimal_times=timing["optimal_times"],
            best_day_of_week=timing["best_day"],
            best_hour=timing["best_hour"],
            reasoning=timing["reasoning"],
            engagement_estimate=random.uniform(0.8, 0.95),
            created_at=datetime.now()
        )
        
        # Cache result
        cache_key = f"timing_{request.product_category}_{request.target_audience}"
        timing_optimizations[cache_key] = response
        
        logger.info(f"Timing optimization completed for {request.product_category}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in timing optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/ab-test", response_model=ABTestResponse, tags=["A/B Testing"])
async def create_ab_test(request: ABTestRequest):
    """
    Create and manage A/B tests for continuous optimization
    
    Sets up automated A/B tests to compare different variations
    and determine the best performing options.
    """
    try:
        test_id = f"AB_{len(ab_tests) + 1:03d}_{request.test_type}"
        
        # Simulate test results (in production, this would be real data)
        variations_performance = []
        for i, variation in enumerate(request.variations):
            performance = {
                "variation_id": f"var_{i+1}",
                "variation_data": variation,
                "clicks": random.randint(400, 600),
                "conversions": random.randint(20, 50),
                "ctr": random.uniform(0.05, 0.15),
                "conversion_rate": random.uniform(0.03, 0.08)
            }
            variations_performance.append(performance)
        
        # Find winning variation
        winning_variation = max(variations_performance, key=lambda x: x["conversion_rate"])
        
        response = ABTestResponse(
            test_id=test_id,
            status="completed",  # In production: "running" -> "completed"
            variations_performance=variations_performance,
            winning_variation=winning_variation,
            statistical_significance=random.uniform(0.85, 0.99),
            recommendation=f"Implement variation {winning_variation['variation_id']} - {winning_variation['conversion_rate']:.1%} conversion rate",
            created_at=datetime.now()
        )
        
        # Store test
        ab_tests[test_id] = response
        
        logger.info(f"A/B test created: {test_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"A/B test creation failed: {str(e)}")

@app.get("/api/ab-tests", tags=["A/B Testing"])
async def list_ab_tests():
    """List all A/B tests and their status"""
    return {
        "tests": list(ab_tests.values()),
        "total_tests": len(ab_tests),
        "active_tests": len([t for t in ab_tests.values() if t.status == "running"]),
        "completed_tests": len([t for t in ab_tests.values() if t.status == "completed"])
    }

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def get_optimization_analytics():
    """Get optimization analytics dashboard"""
    return {
        "total_optimizations": len(title_optimizations) + len(price_optimizations) + len(timing_optimizations),
        "title_optimizations": len(title_optimizations),
        "price_optimizations": len(price_optimizations),
        "timing_optimizations": len(timing_optimizations),
        "ab_tests": len(ab_tests),
        "service_health": "optimal",
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)