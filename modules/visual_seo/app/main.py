from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from PIL import Image
import numpy as np
import io
import os

try:
    import joblib
except ImportError:
    import pickle as joblib  # fallback

app = FastAPI(title="Visual Seo", version="2.0.0")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

MODEL_PATH = os.getenv("VISUAL_SEO_MODEL_PATH", "visual_seo_model.pkl")

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

model = load_model()

def preprocess_image(image_bytes, img_size=128):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((img_size, img_size))
    arr = np.array(img) / 255.0
    arr = arr.flatten().reshape(1, -1)
    return arr

@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    img_arr = preprocess_image(image_bytes)
    if model:
        pred = model.predict(img_arr)
        prob = model.predict_proba(img_arr)
        score = float(np.max(prob))
        label = str(pred[0])
    else:
        label, score = "model_not_loaded", 0.0
    return {
        "label": label,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "visual_seo", 
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    return {
        "status": "operational", 
        "module": "visual_seo", 
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
