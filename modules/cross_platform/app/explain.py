import joblib
import shap
import numpy as np

def explain_platform_performance(input_data, model_path):
    model = joblib.load(model_path)
    explainer = shap.Explainer(model)
    shap_values = explainer(np.array([input_data]))
    return shap_values
