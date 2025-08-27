import shap
import joblib
import numpy as np

def explain_market_pulse(input_data, model_path="../models/market_pulse_model.pkl"):
    model = joblib.load(model_path)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(np.array([input_data]))
    return shap_values
