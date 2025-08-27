"""Trend Detector Module com Prophet"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd

try:
    from prophet import Prophet
except ImportError:
    raise ImportError("Você precisa instalar o pacote 'prophet'. Use: pip install prophet")

app = FastAPI(title="Trend Detector", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "trend_detector", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def get_status():
    return {"status": "operational", "module": "trend_detector", "timestamp": datetime.now().isoformat()}

@app.post("/api/detect-trend")
async def detect_trend(request: Request):
    import os
    from joblib import load
    import glob
    try:
        data = await request.json()
        df = pd.DataFrame(data)
        if "ds" not in df.columns or "y" not in df.columns:
            return {"error": "JSON deve conter as chaves 'ds' (datas) e 'y' (valores)."}
        df["ds"] = pd.to_datetime(df["ds"])
        model_files = glob.glob(os.path.join(os.path.dirname(__file__), '../models/trend_model_*.joblib'))
        if model_files:
            model_path = sorted(model_files)[-1]
            try:
                model = load(model_path)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)
                trend = forecast[["ds", "trend", "yhat"]].tail(30).to_dict(orient="records")
                return {
                    "trend": trend,
                    "timestamp": datetime.now().isoformat(),
                    "model_version": os.path.basename(model_path)
                }
            except Exception as e:
                return {"error": f"Erro ao carregar modelo Prophet: {str(e)}", "timestamp": datetime.now().isoformat()}
        else:
            # Fallback seguro: Prophet treinado na hora
            from prophet import Prophet
            model = Prophet()
            model.fit(df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            trend = forecast[["ds", "trend", "yhat"]].tail(30).to_dict(orient="records")
            return {
                "trend": trend,
                "timestamp": datetime.now().isoformat(),
                "model_version": "fallback"
            }
    except Exception as e:
        import logging
        logging.error(f"Erro na detecção de tendência: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
