import pandas as pd
from prophet import Prophet
from joblib import dump
from datetime import datetime

def train_and_save_trend_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    df['ds'] = pd.to_datetime(df['ds'])
    model = Prophet()
    model.fit(df)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{model_dir}/trend_model_{timestamp}.joblib"
    dump(model, model_path)
    return model_path

# Exemplo de uso:
# train_and_save_trend_model("../data/trend_training_data.csv", "../models")
