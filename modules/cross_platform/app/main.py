"""Cross Platform - Multi-Platform SEO Orchestrator"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Cross Platform SEO", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cross_platform", "timestamp": datetime.now().isoformat()}

@app.get("/api/platform-performance")
async def get_platform_performance():
    import os
    import glob
    import joblib
    import logging
    platforms = ["MercadoLibre", "Amazon", "Shopee"]
    results = []
    for platform in platforms:
        model_files = glob.glob(os.path.join(os.path.dirname(__file__), f'../models/{platform.lower()}_model_*.joblib'))
        if model_files:
            model_path = sorted(model_files)[-1]
            try:
                model = joblib.load(model_path)
                # Exemplo de dados reais (substitua por dados do banco ou arquivo)
                X = [[10000, 1500, 450]]
                ctr_pred = model.predict(X)[0]
                results.append({
                    "name": platform,
                    "ctr": round(ctr_pred, 4),
                    "conversions": 450,
                    "model_version": os.path.basename(model_path)
                })
            except Exception as e:
                logging.error(f"Erro ao carregar modelo {platform}: {str(e)}")
                results.append({
                    "name": platform,
                    "error": f"Modelo indisponível: {str(e)}"
                })
        else:
            # Fallback seguro
            results.append({
                "name": platform,
                "ctr": None,
                "conversions": None,
                "error": "Modelo não encontrado"
            })
    return {"platforms": results, "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
