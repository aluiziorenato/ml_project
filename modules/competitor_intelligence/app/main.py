"""
Competitor Intelligence - Advanced Competitor Analysis Module
Refatorado para previsão temporal com ARIMA/SARIMA
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

app = FastAPI(
    title="Competitor Intelligence",
    version="2.1.0",
    description="Advanced competitor analysis and market intelligence system with ARIMA/SARIMA"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class PriceSeriesRequest(BaseModel):
    competitor_name: str
    price_history: List[float] = Field(..., description="List of historical prices (ordered by time)")
    forecast_days: int = Field(7, description="Number of days to forecast ahead")
    frequency: str = Field("D", description="Frequency: D=day, W=week")

class PriceForecastResponse(BaseModel):
    competitor_name: str
    forecast_days: int
    predicted_prices: List[float]
    model_params: Dict[str, Any]
    confidence_intervals: List[List[float]]
    generated_at: datetime

@app.post("/api/prediction/price-forecast", response_model=PriceForecastResponse)
async def predict_price_forecast(request: PriceSeriesRequest):
    """
    Previsão de preços futuros do concorrente usando ARIMA/SARIMA
    """
    try:
        # Validação
        if len(request.price_history) < 12:
            raise HTTPException(status_code=400, detail="Forneça pelo menos 12 pontos históricos para previsão robusta.")
        
        # Série temporal
        series = pd.Series(request.price_history)
        # SARIMAX: você pode ajustar (p,d,q) e (P,D,Q,S) conforme caso real
        order = (1, 1, 1)      # ARIMA(p,d,q)
        seasonal_order = (0, 0, 0, 0)  # SARIMA(P,D,Q,S) - sem sazonalidade por padrão
        
        model = SARIMAX(
            series,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        results = model.fit(disp=False)
        
        forecast = results.get_forecast(steps=request.forecast_days)
        predicted = forecast.predicted_mean.tolist()
        conf_int = forecast.conf_int().values.tolist()

        response = PriceForecastResponse(
            competitor_name=request.competitor_name,
            forecast_days=request.forecast_days,
            predicted_prices=[round(p, 2) for p in predicted],
            model_params={
                "order": order,
                "seasonal_order": seasonal_order,
                "aic": round(results.aic, 2),
                "bic": round(results.bic, 2)
            },
            confidence_intervals=[[round(l, 2), round(u, 2)] for l, u in conf_int],
            generated_at=datetime.now()
        )
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na previsão ARIMA/SARIMA: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "competitor_intelligence",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
