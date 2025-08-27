import pandas as pd
from xgboost import XGBClassifier
from joblib import dump
from datetime import datetime

def train_and_save_title_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    X = df[["title", "category", "keywords"]]  # Ajuste para features reais
    y = df["ctr"]
    # Pré-processamento necessário para features textuais
    # Exemplo: X = preprocess(X)
    model = XGBClassifier()
    model.fit(X, y)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{model_dir}/title_model_{timestamp}.joblib"
    dump(model, model_path)
    return model_path

# Exemplo de uso:
# train_and_save_title_model("../data/title_training_data.csv", "../models")
