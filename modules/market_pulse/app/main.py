"""
Market Pulse - Real-Time Market Pulse with RandomForestClassifier
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import joblib
import numpy as np

app = FastAPI(
    title="Market Pulse - Real-Time SEO Intelligence",
    description="Real-time market monitoring with ML",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega modelo RandomForest treinado
MODEL_PATH = "market_pulse_model.pkl"
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Erro ao carregar modelo Market Pulse: {e}")

# Opcional: Mapeamento de classes, conforme seu treinamento (adapte!)
CLASS_LABELS = ["em_alta", "estavel", "em_queda"]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "market_pulse",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/status")
async def get_status():
    status = "operational" if model is not None else "model_not_loaded"
    return {
        "status": status,
        "module": "market_pulse",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/classify-keyword")
async def classify_keyword(request: Request):
    if model is None:
        return {
            "error": "Modelo de classificação de mercado não carregado.",
            "timestamp": datetime.now().isoformat()
        }
    try:
        data = await request.json()
        # Campos esperados (adapte conforme seu modelo!)
        required_fields = ["heat", "volume"]
        if not all(field in data for field in required_fields):
            return {
                "error": f"Campos obrigatórios: {required_fields}",
                "timestamp": datetime.now().isoformat()
            }
        X = np.array([
            data["heat"],
            data["volume"]
        ]).reshape(1, -1)
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        label = CLASS_LABELS[pred] if pred < len(CLASS_LABELS) else str(pred)
        confidence = float(np.max(proba))
        return {
            "keyword": data.get("keyword", "N/A"),
            "classification": label,
            "confidence": round(confidence, 4),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Erro na classificação: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
