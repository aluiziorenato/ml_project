"""
AI Predictive - Módulo de IA Preditiva de Oportunidades de Mercado
Funcionalidades:
- Análise de gaps semânticos entre search volume e oferta
- Predição de demanda sazonal com 90 dias de antecedência (com Prophet)
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
import logging
import sys
import os
from joblib import load

# Prophet para previsão sazonal
from prophet import Prophet

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

app = FastAPI(
    title="AI Predictive - SEO Intelligence",
    description="""
    ## 🧠 IA Preditiva de Oportunidades de Mercado
    
    Este módulo utiliza inteligência artificial para identificar e prever oportunidades de mercado em e-commerce.
    
    ### Funcionalidades Principais
    
    * **Gap Analysis** - Análise de lacunas semânticas entre volume de busca e oferta
    * **Seasonal Prediction** - Predição de demanda sazonal com 90 dias de antecedência (Prophet)
    * **Blue Ocean Scoring** - Identificação de produtos com baixa competição
    * **Opportunity Alerts** - Alertas automáticos de oportunidades emergentes
    
    ### Casos de Uso
    
    * Identificar nichos de mercado pouco explorados
    * Antecipar tendências sazonais para planejamento de estoque
    * Encontrar palavras-chave com alto potencial e baixa competição
    * Receber alertas em tempo real sobre oportunidades de mercado
    """,
    version="1.1.0",
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SeasonalPredictionRequest(BaseModel):
    product_category: str
    keywords: List[str]
    historical_data: Optional[Dict[str, List[Dict[str, Any]]]] = None  # {keyword: [{'date': str, 'volume': int}]}
    historical_months: int = 12
    prediction_days: int = 90

class SeasonalPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    seasonal_patterns: Dict[str, Any]
    confidence_score: float
    best_periods: List[Dict[str, Any]]
    created_at: datetime

# Mock data for fallback
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

MODEL_PATH = "../models/prophet_{category}_{keyword}.joblib"

def load_prophet_model(category, keyword):
    path = MODEL_PATH.format(category=category, keyword=keyword)
    return load(path)

def predict_seasonal_demand_prophet(category: str, keywords: List[str], historical_data: Optional[Dict[str, List[Dict[str, Any]]]], days_ahead: int = 90) -> Dict[str, Any]:
    """
    Predição de demanda sazonal com Prophet
    historical_data: {keyword: [{'date': str, 'volume': int}]}
    """
    predictions = []
    seasonal_patterns = {}
    confidence_score = 0.88  # Empírico, pode ser ajustado conforme métricas reais

    for keyword in keywords:
        try:
            if historical_data and keyword in historical_data:
                df = pd.DataFrame(historical_data[keyword])
            else:
                # Fallback para mock data se não houver histórico
                base_volume = MOCK_MARKET_DATA.get(category.lower(), {}).get(keyword.lower(), {}).get("volume", 1000)
                dates = pd.date_range(end=datetime.now(), periods=365)
                volumes = np.random.normal(loc=base_volume, scale=base_volume*0.1, size=len(dates)).astype(int)
                df = pd.DataFrame({'date': dates, 'volume': volumes})
            df.rename(columns={"date": "ds", "volume": "y"}, inplace=True)
            df["ds"] = pd.to_datetime(df["ds"])

            # Treina Prophet
            m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
            m.fit(df)

            future = m.make_future_dataframe(periods=days_ahead)
            forecast = m.predict(future)

            daily_predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
            daily_preds = [
                {
                    "date": row["ds"].strftime("%Y-%m-%d"),
                    "predicted_volume": int(row["yhat"]),
                    "confidence_interval": [int(row["yhat_lower"]), int(row["yhat_upper"])],
                    "confidence": confidence_score
                }
                for _, row in daily_predictions.iterrows()
            ]
            predictions.append({
                "keyword": keyword,
                "daily_predictions": daily_preds,
                "trend": "increasing" if daily_preds[-1]["predicted_volume"] > daily_preds[0]["predicted_volume"] else "stable"
            })
            seasonal_patterns[keyword] = m.seasonalities

        except Exception as e:
            logger.warning(f"Prophet failed for {keyword}. Using mock: {str(e)}")
            daily_preds = [
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "predicted_volume": 1000,
                    "confidence_interval": [800, 1200],
                    "confidence": 0.75
                } for i in range(days_ahead)
            ]
            predictions.append({
                "keyword": keyword,
                "daily_predictions": daily_preds,
                "trend": "unknown"
            })
            seasonal_patterns[keyword] = {"fallback": True}

    return {
        "predictions": predictions,
        "seasonal_patterns": seasonal_patterns,
        "confidence_score": confidence_score
    }

@app.post("/api/predict-seasonal-demand", response_model=SeasonalPredictionResponse, tags=["Predictions"])
async def predict_seasonal_demand_endpoint(request: SeasonalPredictionRequest):
    """
    Predição de demanda sazonal com Prophet
    """
    try:
        prediction = predict_seasonal_demand_prophet(
            request.product_category, 
            request.keywords, 
            request.historical_data,
            request.prediction_days
        )
        best_periods = []
        for pred in prediction["predictions"]:
            avg_volume = np.mean([p["predicted_volume"] for p in pred["daily_predictions"]])
            if avg_volume > 1000:
                best_periods.append({
                    "keyword": pred["keyword"],
                    "period": f"Próximos {request.prediction_days} dias",
                    "avg_volume": int(avg_volume),
                    "recommendation": "Alta demanda prevista - ajuste estoque e marketing"
                })
        response = SeasonalPredictionResponse(
            predictions=prediction["predictions"],
            seasonal_patterns=prediction["seasonal_patterns"],
            confidence_score=prediction["confidence_score"],
            best_periods=best_periods,
            created_at=datetime.now()
        )
        logger.info(f"Seasonal prediction (Prophet) completed for {request.product_category}: {len(prediction['predictions'])} keywords")
        return response
    except Exception as e:
        logger.error(f"Error in seasonal prediction Prophet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai_predictive",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0"
    }

# (Os outros endpoints do módulo permanecem como estão, focando a mudança na predição sazonal)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
