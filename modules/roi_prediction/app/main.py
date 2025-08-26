"""Roi Prediction Module - HistGradientBoostingRegressor Integration"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import numpy as np

import joblib

app = FastAPI(title="Roi Prediction", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Carregar modelo treinado
MODEL_PATH = "roi_model.pkl"
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Erro ao carregar modelo ROI: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "roi_prediction", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def get_status():
    status = "operational" if model is not None else "model_not_loaded"
    return {"status": status, "module": "roi_prediction", "timestamp": datetime.now().isoformat()}

@app.post("/api/predict-roi")
async def predict_roi(request: Request):
    if model is None:
        return {
            "error": "Modelo de ROI não carregado.",
            "timestamp": datetime.now().isoformat()
        }
    try:
        data = await request.json()
        # Exemplo de campos esperados - adapte conforme seu modelo!
        # Ex: investimento, cliques, conversoes, impressões
        required_fields = ["investimento", "cliques", "conversoes", "impressoes"]
        if not all(field in data for field in required_fields):
            return {
                "error": f"Campos obrigatórios: {required_fields}",
                "timestamp": datetime.now().isoformat()
            }
        input_array = np.array([
            data["investimento"],
            data["cliques"],
            data["conversoes"],
            data["impressoes"]
        ]).reshape(1, -1)
        roi_pred = model.predict(input_array)
        return {
            "roi_prediction": float(roi_pred[0]),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Erro na predição: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)
