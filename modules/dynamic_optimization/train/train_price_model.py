import pandas as pd
from sklearn.linear_model import LinearRegression
from joblib import dump
from datetime import datetime

def train_and_save_price_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    X = df[["current_price", "competitor_prices", "category"]]  # Ajuste para features reais
    y = df["optimal_price"]
    model = LinearRegression()
    model.fit(X, y)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{model_dir}/price_model_{timestamp}.joblib"
    dump(model, model_path)
    return model_path

# Exemplo de uso:
# train_and_save_price_model("../data/price_training_data.csv", "../models")
