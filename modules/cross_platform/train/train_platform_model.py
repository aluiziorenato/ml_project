import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime

def train_and_save_platform_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    X = df[["impressions", "clicks", "conversions"]]
    y = df["ctr"]
    model = RandomForestRegressor()
    model.fit(X, y)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{model_dir}/platform_model_{timestamp}.joblib"
    joblib.dump(model, model_path)
    return model_path

# Exemplo de uso:
# train_and_save_platform_model("../data/platform_training_data.csv", "../models")
