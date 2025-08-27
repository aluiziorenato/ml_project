import pandas as pd

def load_csv(path):
    return pd.read_csv(path)

def clean_data(df):
    # Exemplo de limpeza: remove NaN
    return df.dropna()

def transform_data(df, func):
    return df.apply(func, axis=1)
