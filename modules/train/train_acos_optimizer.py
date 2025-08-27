import pandas as pd
from sklearn.linear_model import LinearRegression
from joblib import dump

def train_and_save_acos_optimizer(csv_path, model_path):
    df = pd.read_csv(csv_path)
    X = df[["spend", "sales", "target_acos"]]
    y = df["optimized_bid"]
    model = LinearRegression()
    model.fit(X, y)
    dump(model, model_path)

# Exemplo de uso:
# train_and_save_acos_optimizer("../data/historical_data.csv", "../models/acos_optimizer.joblib")
