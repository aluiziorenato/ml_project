from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load

app = FastAPI()

class SEOInferenceRequest(BaseModel):
    url: str
    keyword: str

class SEOInferenceResponse(BaseModel):
    score: float
    recommendations: list[str]

MODEL_PATH = "../models/seo_model.joblib"

def load_seo_model():
    return load(MODEL_PATH)

@app.post("/api/seo-inference", response_model=SEOInferenceResponse)
async def seo_inference_endpoint(request: SEOInferenceRequest):
    model = load_seo_model()
    # Exemplo: modelo retorna score e recomendações
    score = float(model.predict([[request.url, request.keyword]])[0])  # Simulação
    recommendations = ["Use a palavra-chave no título", "Melhore a meta descrição"]
    return SEOInferenceResponse(score=score, recommendations=recommendations)
