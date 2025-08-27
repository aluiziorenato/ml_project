from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load

app = FastAPI()

class ACOSOptimizationRequest(BaseModel):
    campaign_id: str
    spend: float
    sales: float
    target_acos: float

class ACOSOptimizationResponse(BaseModel):
    optimized_bid: float
    expected_acos: float

MODEL_PATH = "../models/acos_optimizer.joblib"

def load_acos_model():
    return load(MODEL_PATH)

@app.post("/api/optimize-acos", response_model=ACOSOptimizationResponse)
async def optimize_acos_endpoint(request: ACOSOptimizationRequest):
    model = load_acos_model()
    # Exemplo: modelo retorna bid otimizado e ACOS esperado
    # Substitua por lógica real do modelo
    optimized_bid = model.predict([[request.spend, request.sales, request.target_acos]])[0]
    expected_acos = request.target_acos  # Simulação
    return ACOSOptimizationResponse(optimized_bid=optimized_bid, expected_acos=expected_acos)
