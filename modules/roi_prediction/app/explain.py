import shap
import joblib
import numpy as np

def explain_roi(input_data, model_path="../models/roi_model.pkl"):
    model = joblib.load(model_path)
    explainer = shap.Explainer(model)
    shap_values = explainer(np.array([input_data]))
    return shap_values
