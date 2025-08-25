"""
Unit tests for analytics module - predictor.py
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from core.analytics.predictor import MLPredictor, PredictionResult


class TestMLPredictor:
    """Test cases for MLPredictor class."""
    
    def test_init(self):
        """Test predictor initialization."""
        predictor = MLPredictor()
        assert predictor.model_type == "linear"
        assert not predictor.is_trained
        assert predictor.feature_names == []
        assert predictor.model_version == "1.0.0"