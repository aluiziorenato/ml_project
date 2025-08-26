from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from PIL import Image
import io

from transformers import BlipProcessor, BlipForConditionalGeneration

app = FastAPI(title="Visual Seo Captioning", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Carrega BLIP da Hugging Face uma vez ao iniciar
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def gerar_caption(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

@app.post("/api/generate-caption")
async def generate_caption(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        caption = gerar_caption(image_bytes)
    except Exception as e:
        return {
            "error": f"Erro ao gerar título/descrição: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

    # BLIP normalmente gera uma descrição curta, que pode ser usada como título ou descrição.
    # Para título: geralmente os primeiros termos, para descrição: pode usar o texto completo.
    return {
        "title": caption,
        "description": caption,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "visual_seo_captioning",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    return {
        "status": "operational",
        "module": "visual_seo_captioning",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
