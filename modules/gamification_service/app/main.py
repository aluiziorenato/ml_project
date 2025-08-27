from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load

app = FastAPI()

class GamificationRequest(BaseModel):
    user_id: str
    activity_score: float
    engagement: float

class GamificationResponse(BaseModel):
    cluster: int
    score: float

MODEL_PATH = "../models/gamification_cluster.joblib"

def load_gamification_model():
    return load(MODEL_PATH)

@app.post("/api/gamification-score", response_model=GamificationResponse)
async def gamification_score_endpoint(request: GamificationRequest):
    model = load_gamification_model()
    # Exemplo: modelo retorna cluster e score
    cluster = int(model.predict([[request.activity_score, request.engagement]])[0])
    score = float(request.activity_score * 0.7 + request.engagement * 0.3)  # Simulação
    return GamificationResponse(cluster=cluster, score=score)
