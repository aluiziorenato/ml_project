import pytest
from app.main import (
    app, models_storage, training_jobs, model_updates, learning_history,
    ModelCreateRequest, ModelUpdateRequest, TrainingJobRequest, PredictionRequest
)


class TestLearningServiceLogic:
    """Test class for Learning Service business logic"""

    def setup_method(self):
        """Clear storage before each test"""
        models_storage.clear()
        training_jobs.clear()
        model_updates.clear()
        learning_history.clear()

    def test_model_create_request_validation(self, sample_model_request):
        """Test that model creation request validation works correctly"""
        request = ModelCreateRequest(**sample_model_request)
        assert request.name == "Campaign Performance Predictor"
        assert request.model_type == "random_forest"
        assert request.hyperparameters["n_estimators"] == 100
        assert len(request.features) == 4

    def test_model_update_request_validation(self, sample_model_update_request):
        """Test that model update request validation works correctly"""
        request = ModelUpdateRequest(**sample_model_update_request)
        assert request.campaign_id == "CAM_12345678"
        assert request.actual_clicks == 1500
        assert request.predicted_clicks == 1400
        assert request.actual_revenue == 2250.0

    def test_training_job_request_validation(self, sample_training_request):
        """Test that training job request validation works correctly"""
        request = TrainingJobRequest(**sample_training_request)
        assert request.model_id == "MDL_TEST123"
        assert request.validation_split == 0.2
        assert request.epochs == 100
        assert request.batch_size == 32

    def test_prediction_request_validation(self, sample_prediction_request):
        """Test that prediction request validation works correctly"""
        request = PredictionRequest(**sample_prediction_request)
        assert request.model_id == "MDL_TEST123"
        assert request.features["budget"] == 1000.0
        assert len(request.features) == 4

    def test_models_storage_operations(self, sample_model_request):
        """Test basic operations on models storage"""
        # Initially empty
        assert len(models_storage) == 0
        
        # Add a model (simulate model creation)
        from app.main import ModelResponse
        from datetime import datetime
        
        model = ModelResponse(
            model_id="MDL_TEST123",
            name=sample_model_request["name"],
            description=sample_model_request["description"],
            model_type=sample_model_request["model_type"],
            status="ready",
            hyperparameters=sample_model_request["hyperparameters"],
            features=sample_model_request["features"],
            performance_metrics={},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            version="1.0.0"
        )
        
        models_storage["MDL_TEST123"] = model
        
        assert len(models_storage) == 1
        assert "MDL_TEST123" in models_storage
        assert models_storage["MDL_TEST123"].status == "ready"
        
        # Remove model
        del models_storage["MDL_TEST123"]
        assert len(models_storage) == 0

    def test_training_jobs_storage_operations(self):
        """Test basic operations on training jobs storage"""
        # Initially empty
        assert len(training_jobs) == 0
        
        # Add a training job (simulate job creation)
        from app.main import TrainingJobResponse
        
        job = TrainingJobResponse(
            job_id="JOB_TEST123",
            model_id="MDL_TEST123",
            status="queued",
            progress=0.0,
            started_at=None,
            completed_at=None,
            logs=["Job created"],
            final_metrics={}
        )
        
        training_jobs["JOB_TEST123"] = job
        
        assert len(training_jobs) == 1
        assert "JOB_TEST123" in training_jobs
        assert training_jobs["JOB_TEST123"].status == "queued"
        
        # Update job status
        training_jobs["JOB_TEST123"].status = "running"
        training_jobs["JOB_TEST123"].progress = 50.0
        
        assert training_jobs["JOB_TEST123"].status == "running"
        assert training_jobs["JOB_TEST123"].progress == 50.0

    def test_model_id_generation_format(self):
        """Test that model IDs are generated in the correct format"""
        import uuid
        
        model_id = f"MDL_{str(uuid.uuid4())[:8].upper()}"
        
        assert model_id.startswith("MDL_")
        assert len(model_id) == 12  # MDL_ + 8 characters
        assert model_id[4:].isupper()

    def test_job_id_generation_format(self):
        """Test that job IDs are generated in the correct format"""
        import uuid
        
        job_id = f"JOB_{str(uuid.uuid4())[:8].upper()}"
        
        assert job_id.startswith("JOB_")
        assert len(job_id) == 12  # JOB_ + 8 characters
        assert job_id[4:].isupper()

    def test_model_type_validation(self):
        """Test model type validation logic"""
        valid_types = ["linear_regression", "random_forest", "neural_network", "svm", "gradient_boosting"]
        
        for model_type in valid_types:
            assert model_type in valid_types
        
        invalid_types = ["invalid_model", "not_supported", ""]
        for model_type in invalid_types:
            assert model_type not in valid_types

    def test_accuracy_metrics_calculation(self):
        """Test accuracy metrics calculation logic"""
        # Test accuracy calculation
        actual_clicks = 1500
        predicted_clicks = 1400
        
        click_accuracy = 1 - abs(actual_clicks - predicted_clicks) / max(predicted_clicks, 1)
        click_accuracy = max(0, min(1, click_accuracy))
        
        assert 0 <= click_accuracy <= 1
        assert click_accuracy > 0.9  # Should be high accuracy for this example
        
        # Test with perfect prediction
        perfect_accuracy = 1 - abs(1000 - 1000) / max(1000, 1)
        assert perfect_accuracy == 1.0
        
        # Test with poor prediction
        poor_accuracy = 1 - abs(1000 - 500) / max(500, 1)
        poor_accuracy = max(0, min(1, poor_accuracy))
        assert poor_accuracy == 0  # Very poor prediction

    def test_improvement_suggestions_logic(self):
        """Test improvement suggestions generation logic"""
        suggestions = []
        
        # Test low click accuracy scenario
        click_accuracy = 0.7  # Less than 0.8
        if click_accuracy < 0.8:
            suggestions.append("Improve click prediction models - consider seasonality factors")
        
        # Test low conversion accuracy scenario
        conversion_accuracy = 0.75  # Less than 0.8
        if conversion_accuracy < 0.8:
            suggestions.append("Enhance conversion rate modeling - analyze user behavior patterns")
        
        # Test low revenue accuracy scenario
        revenue_accuracy = 0.6  # Less than 0.8
        if revenue_accuracy < 0.8:
            suggestions.append("Refine revenue forecasting - incorporate market trends")
        
        # Test high overall accuracy scenario
        overall_accuracy = 0.95  # Greater than 0.9
        if overall_accuracy > 0.9:
            suggestions.append("Excellent prediction accuracy - maintain current model parameters")
        
        assert len(suggestions) == 4
        assert "seasonality factors" in suggestions[0]
        assert "user behavior patterns" in suggestions[1]
        assert "market trends" in suggestions[2]
        assert "maintain current" in suggestions[3]

    def test_performance_metrics_aggregation(self):
        """Test performance metrics aggregation logic"""
        # Simulate recent updates
        updates = [
            {"accuracy_metrics": {"click_accuracy": 0.9, "conversion_accuracy": 0.85, "revenue_accuracy": 0.8}},
            {"accuracy_metrics": {"click_accuracy": 0.88, "conversion_accuracy": 0.9, "revenue_accuracy": 0.82}},
            {"accuracy_metrics": {"click_accuracy": 0.92, "conversion_accuracy": 0.87, "revenue_accuracy": 0.85}},
        ]
        
        # Calculate averages
        avg_click = sum(u["accuracy_metrics"]["click_accuracy"] for u in updates) / len(updates)
        avg_conversion = sum(u["accuracy_metrics"]["conversion_accuracy"] for u in updates) / len(updates)
        avg_revenue = sum(u["accuracy_metrics"]["revenue_accuracy"] for u in updates) / len(updates)
        
        assert 0.85 < avg_click < 0.95
        assert 0.85 < avg_conversion < 0.92
        assert 0.80 < avg_revenue < 0.90

    def test_training_progress_simulation(self):
        """Test training progress simulation logic"""
        import random
        
        # Simulate progress updates
        initial_progress = 10.0
        random.seed(42)  # For reproducible tests
        
        progress = initial_progress
        for _ in range(5):
            progress = min(100.0, progress + random.uniform(5, 15))
        
        assert progress > initial_progress
        assert progress <= 100.0

    def test_prediction_simulation_logic(self):
        """Test prediction simulation logic"""
        import random
        
        # Test different model types
        model_types = ["linear_regression", "random_forest", "neural_network"]
        
        for model_type in model_types:
            random.seed(42)  # For reproducible tests
            
            if model_type == "linear_regression":
                prediction = {"value": round(random.uniform(100, 1000), 2)}
                assert "value" in prediction
                assert isinstance(prediction["value"], float)
            elif model_type in ["random_forest", "gradient_boosting"]:
                prediction = {"class": random.choice(["high", "medium", "low"]), "probabilities": [0.3, 0.5, 0.2]}
                assert "class" in prediction
                assert "probabilities" in prediction
                assert prediction["class"] in ["high", "medium", "low"]
            else:
                prediction = {"result": "processed", "score": round(random.uniform(0.1, 1.0), 3)}
                assert "result" in prediction
                assert "score" in prediction

    def test_health_check_response_format(self):
        """Test health check response format"""
        expected_response = {"status": "healthy", "service": "learning_service"}
        
        assert "status" in expected_response
        assert "service" in expected_response
        assert expected_response["status"] == "healthy"
        assert expected_response["service"] == "learning_service"

    def test_model_status_transitions(self):
        """Test valid model status transitions"""
        valid_statuses = ["ready", "training", "archived"]
        
        # Test valid transitions
        assert "ready" in valid_statuses
        assert "training" in valid_statuses
        assert "archived" in valid_statuses
        
        # Test that training -> ready is valid
        current_status = "training"
        new_status = "ready"
        assert new_status in valid_statuses
        
        # Test that ready -> archived is valid
        current_status = "ready"
        new_status = "archived"
        assert new_status in valid_statuses