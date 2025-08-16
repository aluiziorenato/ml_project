"""
Core analytics module for ML project.
Provides predictive analytics and optimization capabilities.
"""

from .predictor import MLPredictor, PredictionResult
from .optimizer import MLOptimizer, OptimizationResult

__all__ = [
    "MLPredictor",
    "PredictionResult", 
    "MLOptimizer",
    "OptimizationResult"
]