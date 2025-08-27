import os
from datetime import datetime

def get_model_metrics(model_dir="../models"):
    metrics = {}
    for f in os.listdir(model_dir):
        if f.endswith(".pkl"):
            metrics[f] = {
                "path": os.path.join(model_dir, f),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(os.path.join(model_dir, f))).isoformat()
            }
    # Adicione métricas reais do modelo (acurácia, uso, drift) conforme necessário
    return metrics
