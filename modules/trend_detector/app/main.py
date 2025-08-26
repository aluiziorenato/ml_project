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
    try:
        # Espera JSON com 'ds' (datas) e 'y' (valores)
        data = await request.json()
        df = pd.DataFrame(data)
        if "ds" not in df.columns or "y" not in df.columns:
            return {"error": "JSON deve conter as chaves 'ds' (datas) e 'y' (valores)."}

        # Ajusta tipo das datas
        df["ds"] = pd.to_datetime(df["ds"])
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # Retorna tendências, previsão e datas
        trend = forecast[["ds", "trend", "yhat"]].tail(30).to_dict(orient="records")
        return {
            "trend": trend,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
