import pandas as pd
from prophet import Prophet
from joblib import dump

def train_and_save_prophet(csv_path, category, keyword, model_path):
    df = pd.read_csv(csv_path)
    model = Prophet()
    model.fit(df)
    dump(model, model_path)

# Exemplo de uso:
# train_and_save_prophet("../data/historical_data.csv", "electronics", "smartphone", "../models/prophet_electronics_smartphone.joblib")
