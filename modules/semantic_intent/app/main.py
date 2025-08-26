"""Semantic Intent - Intent Prediction Engine with BERT Fine-Tuned Model"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from transformers import BertForSequenceClassification, BertTokenizer
import torch

app = FastAPI(title="Semantic Intent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Carrega modelo BERT ajustado e tokenizer
MODEL_PATH = "intent_model"
try:
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
except Exception as e:
    tokenizer = None
    model = None
    print(f"Erro ao carregar modelo: {e}")

# Mapeamento dos índices para nomes de intenções (adapte conforme seu banco!)
INTENT_LABELS = [
    "comprar",      # 0
    "cancelar",     # 1
    "reclamar",     # 2
    "tirar dúvida"  # 3
    # Adicione mais conforme seu treinamento
]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "semantic_intent", "timestamp": datetime.now().isoformat()}

@app.post("/api/intent-analysis")
async def analyze_intent(request: Request):
    if model is None or tokenizer is None:
        return {
            "error": "Modelo de intenção não carregado.",
            "timestamp": datetime.now().isoformat()
        }
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return {
            "error": "Campo 'text' obrigatório no corpo do POST.",
            "timestamp": datetime.now().isoformat()
        }
    # Tokeniza e prediz
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        score, pred = probs.max(dim=1)
        intent_idx = int(pred.item())
        confidence = float(score.item())
        intent_label = INTENT_LABELS[intent_idx] if intent_idx < len(INTENT_LABELS) else f"intent_{intent_idx}"

    return {
        "intent": {
            "type": intent_label,
            "confidence": round(confidence, 4)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    status = "operational" if model is not None else "model_not_loaded"
    return {"status": status, "module": "semantic_intent", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
