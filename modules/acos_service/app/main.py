from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load
import httpx

app = FastAPI()

class ACOSOptimizationRequest(BaseModel):
    campaign_id: str
    spend: float
    sales: float
    target_acos: float
    acos_real: float = None  # opcional, para feedback

class ACOSOptimizationResponse(BaseModel):
    optimized_bid: float
    expected_acos: float

MODEL_PATH = "../models/acos_optimizer.joblib"

def load_acos_model():
    return load(MODEL_PATH)

async def get_bid_from_learning_service(request: ACOSOptimizationRequest):
    url = "http://localhost:8008/api/learning/predict"
    params = {
        "campaign_id": request.campaign_id,
        "spend": request.spend,
        "sales": request.sales,
        "target_acos": request.target_acos
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("optimized_bid")
    except Exception:
        pass
    return None

async def send_feedback_to_learning_service(request: ACOSOptimizationRequest, optimized_bid: float):
    url = "http://localhost:8008/api/learning/update"
    payload = {
        "campaign_id": request.campaign_id,
        "spend": request.spend,
        "sales": request.sales,
        "target_acos": request.target_acos,
        "optimized_bid": optimized_bid,
        "acos_real": request.acos_real
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(url, json=payload)
    except Exception:
        pass
@app.post("/api/optimize-acos", response_model=ACOSOptimizationResponse)
async def optimize_acos_endpoint(request: ACOSOptimizationRequest):
    # 1. Tenta obter o bid recomendado pelo learning_service
    optimized_bid = await get_bid_from_learning_service(request)
    if optimized_bid is None:
        # 2. Fallback para modelo local
        model = load_acos_model()
        optimized_bid = model.predict([[request.spend, request.sales, request.target_acos]])[0]
    expected_acos = request.target_acos  # Simulação
    # 3. Envia feedback para o learning_service
    await send_feedback_to_learning_service(request, optimized_bid)
    return ACOSOptimizationResponse(optimized_bid=optimized_bid, expected_acos=expected_acos)
