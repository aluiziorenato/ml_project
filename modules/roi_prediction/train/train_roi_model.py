import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib
from datetime import datetime

def train_and_save_roi_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    X = df[["investimento", "cliques", "conversoes", "impressoes"]]
    y = df["roi"]
    model = HistGradientBoostingRegressor()
    model.fit(X, y)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{model_dir}/roi_model_{timestamp}.pkl"
    joblib.dump(model, model_path)
    return model_path

# Exemplo de uso:
# train_and_save_roi_model("../data/roi_training_data.csv", "../models")
