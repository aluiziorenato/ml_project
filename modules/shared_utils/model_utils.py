from joblib import load, dump

def save_model(model, path):
    dump(model, path)

def load_model(path):
    return load(path)
