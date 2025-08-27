from joblib import load
import shap
import numpy as np

def explain_prediction(model_path, input_data):
    model = load(model_path)
    explainer = shap.Explainer(model)
    shap_values = explainer(np.array([input_data]))
    return shap_values.values.tolist()
