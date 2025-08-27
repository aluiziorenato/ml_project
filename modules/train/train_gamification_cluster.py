import pandas as pd
from sklearn.cluster import KMeans
from joblib import dump

def train_and_save_gamification_cluster(csv_path, model_path, n_clusters=3):
    df = pd.read_csv(csv_path)
    X = df[["activity_score", "engagement"]]
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X)
    dump(model, model_path)

# Exemplo de uso:
# train_and_save_gamification_cluster("../data/historical_data.csv", "../models/gamification_cluster.joblib")
