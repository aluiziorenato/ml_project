import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from datetime import datetime

def train_and_save_market_pulse_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    X = df[["heat", "volume"]]
    y = df["label"]
    model = RandomForestClassifier()
    model.fit(X, y)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{model_dir}/market_pulse_model_{timestamp}.pkl"
    joblib.dump(model, model_path)
    return model_path

# Exemplo de uso:
# train_and_save_market_pulse_model("../data/market_pulse_training_data.csv", "../models")
