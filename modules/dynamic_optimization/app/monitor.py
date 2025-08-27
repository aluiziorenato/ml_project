import os
from joblib import load
from datetime import datetime

def list_models(model_dir="../models"):
    return [f for f in os.listdir(model_dir) if f.endswith(".joblib") or f.endswith(".pkl")]

def get_model_metrics(model_path):
    model = load(model_path)
    metrics = {
        "model_path": model_path,
        "trained_at": datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat(),
        # Adicione métricas reais do modelo aqui
    }
    return metrics
