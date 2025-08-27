import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from joblib import dump

def train_and_save_seo_model(csv_path, model_path):
    df = pd.read_csv(csv_path)
    X = df[["url", "keyword"]]  # Ajuste para features reais
    y = df["score"]
    model = RandomForestRegressor()
    # Pré-processamento necessário para features textuais
    # Exemplo: X = preprocess(X)
    model.fit(X, y)
    dump(model, model_path)

# Exemplo de uso:
# train_and_save_seo_model("../data/seo_training_data.csv", "../models/seo_model.joblib")
