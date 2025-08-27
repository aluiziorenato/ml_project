from joblib import load

def explain_prediction(model_path, input_data):
    model = load(model_path)
    explanation = model.params if hasattr(model, "params") else {}
    return explanation