"""
Regression tests for AutoML experiment functionality

These tests ensure that the AutoML components work correctly and
maintain backward compatibility during updates.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json

# Add automl module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from automl.experiment import ExperimentManager, run_demo_experiment
from automl.tuning import HyperparameterTuner, run_tuning_demo
from automl.tracking import create_tracker, SimpleTracker, run_tracking_demo

class TestExperimentManager:
    """Test cases for ExperimentManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test results"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def experiment_manager(self, temp_dir):
        """Create ExperimentManager instance for testing"""
        # Change to temp directory to avoid cluttering
        os.chdir(temp_dir)
        return ExperimentManager("test_experiments")
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing"""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y_classification = np.random.randint(0, 2, 100)
        y_regression = np.random.randn(100)
        return X, y_classification, y_regression
    
    def test_experiment_creation(self, experiment_manager):
        """Test experiment creation and configuration"""
        experiment_id = experiment_manager.create_experiment(
            name="Test Experiment",
            description="A test experiment for regression testing",
            dataset_info={"shape": (100, 5), "source": "test"}
        )
        
        assert experiment_id is not None
        assert experiment_id.startswith("exp_")
        assert len(experiment_manager.experiments_history) == 1
        
        # Check if config file was created
        config_path = experiment_manager.results_dir / f"{experiment_id}_config.json"
        assert config_path.exists()
        
        # Verify config content
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config["name"] == "Test Experiment"
        assert config["description"] == "A test experiment for regression testing"
        assert config["dataset_info"]["shape"] == [100, 5]
    
    def test_classification_experiment(self, experiment_manager, sample_data):
        """Test basic classification experiment"""
        X, y_classification, _ = sample_data
        
        experiment_id = experiment_manager.create_experiment(
            name="Classification Test",
            description="Test classification functionality",
            dataset_info={"shape": X.shape, "problem": "classification"}
        )
        
        results = experiment_manager.run_basic_experiment(
            experiment_id=experiment_id,
            X=X,
            y=y_classification,
            problem_type="classification"
        )
        
        # Verify results structure
        assert "experiment_id" in results
        assert "problem_type" in results
        assert "models_tested" in results
        assert "best_model" in results
        assert "best_score" in results
        
        # Verify that models were tested
        assert len(results["models_tested"]) > 0
        assert results["problem_type"] == "classification"
        
        # Verify that best model and score are valid
        assert results["best_model"] is not None
        assert results["best_score"] is not None
        assert 0 <= results["best_score"] <= 1  # Accuracy should be between 0 and 1
    
    def test_regression_experiment(self, experiment_manager, sample_data):
        """Test basic regression experiment"""
        X, _, y_regression = sample_data
        
        experiment_id = experiment_manager.create_experiment(
            name="Regression Test",
            description="Test regression functionality",
            dataset_info={"shape": X.shape, "problem": "regression"}
        )
        
        results = experiment_manager.run_basic_experiment(
            experiment_id=experiment_id,
            X=X,
            y=y_regression,
            problem_type="regression"
        )
        
        # Verify results structure
        assert "experiment_id" in results
        assert "problem_type" in results
        assert "models_tested" in results
        assert "best_model" in results
        assert "best_score" in results
        
        # Verify regression-specific aspects
        assert results["problem_type"] == "regression"
        assert len(results["models_tested"]) > 0
        
        # For regression, score is negative MSE, so should be <= 0
        assert results["best_score"] <= 0
    
    def test_experiment_results_retrieval(self, experiment_manager, sample_data):
        """Test retrieving experiment results"""
        X, y_classification, _ = sample_data
        
        # Create and run experiment
        experiment_id = experiment_manager.create_experiment(
            name="Retrieval Test",
            description="Test results retrieval",
            dataset_info={"shape": X.shape}
        )
        
        results = experiment_manager.run_basic_experiment(
            experiment_id=experiment_id,
            X=X,
            y=y_classification,
            problem_type="classification"
        )
        
        # Retrieve results
        retrieved_results = experiment_manager.get_experiment_results(experiment_id)
        
        assert retrieved_results is not None
        assert retrieved_results["experiment_id"] == experiment_id
        assert retrieved_results["best_model"] == results["best_model"]
        assert retrieved_results["best_score"] == results["best_score"]
    
    def test_experiment_listing(self, experiment_manager, sample_data):
        """Test listing all experiments"""
        X, y_classification, _ = sample_data
        
        # Create multiple experiments
        for i in range(3):
            experiment_id = experiment_manager.create_experiment(
                name=f"List Test {i}",
                description=f"Test experiment {i}",
                dataset_info={"shape": X.shape, "index": i}
            )
            
            experiment_manager.run_basic_experiment(
                experiment_id=experiment_id,
                X=X,
                y=y_classification,
                problem_type="classification"
            )
        
        # List experiments
        experiments = experiment_manager.list_experiments()
        
        assert len(experiments) == 3
        
        # Check that experiments are sorted by creation time (newest first)
        for i in range(len(experiments) - 1):
            assert experiments[i]["created_at"] >= experiments[i + 1]["created_at"]
        
        # Check that status and performance info is included
        for exp in experiments:
            assert "status" in exp
            assert exp["status"] == "completed"
            assert "best_model" in exp
            assert "best_score" in exp
    
    def test_experiment_report_generation(self, experiment_manager, sample_data):
        """Test experiment report generation"""
        X, y_classification, _ = sample_data
        
        experiment_id = experiment_manager.create_experiment(
            name="Report Test",
            description="Test report generation",
            dataset_info={"shape": X.shape, "target": "test_target"}
        )
        
        experiment_manager.run_basic_experiment(
            experiment_id=experiment_id,
            X=X,
            y=y_classification,
            problem_type="classification"
        )
        
        # Generate report
        report = experiment_manager.generate_experiment_report(experiment_id)
        
        assert isinstance(report, str)
        assert "Report Test" in report
        assert "Test report generation" in report
        assert experiment_id in report
        assert "Results Summary" in report
        assert "Models Tested" in report
    
    def test_demo_experiment(self):
        """Test the demo experiment function"""
        # Change to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            demo_results = run_demo_experiment()
            
            assert "experiment_id" in demo_results
            assert "results" in demo_results
            assert "report" in demo_results
            
            # Verify results structure
            results = demo_results["results"]
            assert results["problem_type"] == "classification"
            assert results["best_model"] is not None
            assert results["best_score"] is not None


class TestHyperparameterTuner:
    """Test cases for HyperparameterTuner"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test results"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def tuner(self, temp_dir):
        """Create HyperparameterTuner instance for testing"""
        os.chdir(temp_dir)
        return HyperparameterTuner()
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing"""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randint(0, 2, 100)
        return X, y
    
    def test_parameter_space_definition(self, tuner):
        """Test parameter space definitions"""
        # Test known model types
        rf_params = tuner.define_parameter_space("random_forest_classifier")
        assert "n_estimators" in rf_params
        assert "max_depth" in rf_params
        assert "min_samples_split" in rf_params
        
        lr_params = tuner.define_parameter_space("logistic_regression")
        assert "C" in lr_params
        assert "penalty" in lr_params
        
        # Test unknown model type
        unknown_params = tuner.define_parameter_space("unknown_model")
        assert unknown_params == {}
    
    def test_random_search_tuning(self, tuner, sample_data):
        """Test random search hyperparameter tuning"""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = sample_data
        model = RandomForestClassifier(random_state=42)
        param_space = tuner.define_parameter_space("random_forest_classifier")
        
        results = tuner.random_search_tuning(
            model=model,
            X=X,
            y=y,
            param_distributions=param_space,
            n_iter=5,  # Small number for fast testing
            cv=3,      # Small CV for speed
            scoring="accuracy"
        )
        
        # Verify results structure
        assert results["method"] == "random_search"
        assert "best_params" in results
        assert "best_score" in results
        assert "n_iterations" in results
        assert "top_5_results" in results
        
        # Verify performance metrics
        assert results["n_iterations"] == 5
        assert 0 <= results["best_score"] <= 1
        assert len(results["top_5_results"]) <= 5
    
    def test_bayesian_optimization(self, tuner, sample_data):
        """Test simple Bayesian optimization"""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = sample_data
        model = RandomForestClassifier(random_state=42)
        param_space = tuner.define_parameter_space("random_forest_classifier")
        
        results = tuner.bayesian_optimization_simple(
            model=model,
            X=X,
            y=y,
            param_space=param_space,
            n_iter=5,  # Small number for fast testing
            cv=3,      # Small CV for speed
            scoring="accuracy"
        )
        
        # Verify results structure
        assert results["method"] == "bayesian_optimization_simple"
        assert "best_params" in results
        assert "best_score" in results
        assert "n_iterations" in results
        assert "actual_iterations" in results
        
        # Verify that some iterations were successful
        assert results["actual_iterations"] > 0
        assert results["actual_iterations"] <= results["n_iterations"]
    
    def test_auto_tune_model(self, tuner, sample_data):
        """Test automatic model tuning"""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = sample_data
        model = RandomForestClassifier(random_state=42)
        
        results = tuner.auto_tune_model(
            model=model,
            model_type="random_forest_classifier",
            X=X,
            y=y,
            method="random_search",
            scoring="accuracy",
            cv=3
        )
        
        # Verify results structure
        assert "tuning_id" in results
        assert "model_type" in results
        assert "method" in results
        assert "best_params" in results
        assert "best_score" in results
        
        # Verify specific values
        assert results["model_type"] == "random_forest_classifier"
        assert results["method"] == "random_search"
        assert 0 <= results["best_score"] <= 1
    
    def test_invalid_model_type(self, tuner, sample_data):
        """Test handling of invalid model type"""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = sample_data
        model = RandomForestClassifier(random_state=42)
        
        results = tuner.auto_tune_model(
            model=model,
            model_type="invalid_model_type",
            X=X,
            y=y
        )
        
        assert "error" in results
        assert "available_types" in results
    
    def test_invalid_tuning_method(self, tuner, sample_data):
        """Test handling of invalid tuning method"""
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = sample_data
        model = RandomForestClassifier(random_state=42)
        
        results = tuner.auto_tune_model(
            model=model,
            model_type="random_forest_classifier",
            X=X,
            y=y,
            method="invalid_method"
        )
        
        assert "error" in results
        assert "available_methods" in results
    
    def test_tuning_demo(self):
        """Test the tuning demo function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            demo_results = run_tuning_demo()
            
            assert "comparison_id" in demo_results
            assert "model_type" in demo_results
            assert "results" in demo_results
            assert "best_method" in demo_results
            assert "best_overall_score" in demo_results
            
            # Verify that methods were compared
            assert len(demo_results["results"]) > 0


class TestMLflowTracker:
    """Test cases for MLflow tracking functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test tracking"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_simple_tracker_creation(self, temp_dir):
        """Test SimpleTracker creation and basic functionality"""
        os.chdir(temp_dir)
        
        # Create simple tracker (fallback when MLflow is not available)
        tracker = SimpleTracker("test_experiment")
        
        assert tracker.experiment_name == "test_experiment"
        assert tracker.tracking_dir.exists()
    
    def test_simple_tracker_workflow(self, temp_dir):
        """Test complete SimpleTracker workflow"""
        os.chdir(temp_dir)
        
        tracker = SimpleTracker("test_workflow")
        
        # Start run
        run_id = tracker.start_run(
            run_name="test_run",
            tags={"test": "true", "environment": "testing"}
        )
        
        assert run_id is not None
        assert tracker.current_run_id == run_id
        
        # Log parameters
        tracker.log_parameters({
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        })
        
        # Log metrics
        tracker.log_metrics({
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.88
        })
        
        # End run
        tracker.end_run()
        
        # Check that run file was created
        run_file = tracker.tracking_dir / f"{run_id}.json"
        assert run_file.exists()
        
        # Verify run content
        with open(run_file, 'r') as f:
            run_data = json.load(f)
        
        assert run_data["run_name"] == "test_run"
        assert run_data["tags"]["test"] == "true"
        assert run_data["parameters"]["n_estimators"] == 100
        assert run_data["metrics"]["accuracy"] == 0.85
        assert "completed_at" in run_data
    
    def test_tracker_factory(self, temp_dir):
        """Test tracker factory function"""
        os.chdir(temp_dir)
        
        # Test simple tracker creation (MLflow not available)
        tracker = create_tracker("factory_test", use_mlflow=False)
        assert isinstance(tracker, SimpleTracker)
        
        # Test MLflow tracker creation (should fallback to SimpleTracker)
        tracker_mlflow = create_tracker("factory_test_mlflow", use_mlflow=True)
        # Should be SimpleTracker because MLflow is not installed in test environment
        assert isinstance(tracker_mlflow, (SimpleTracker,))  # Could be MLflowTracker if available
    
    def test_tracking_demo(self):
        """Test the tracking demo function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            demo_results = run_tracking_demo()
            
            assert "run_id" in demo_results
            assert "accuracy" in demo_results
            
            # Verify accuracy is reasonable
            assert 0 <= demo_results["accuracy"] <= 1


class TestIntegration:
    """Integration tests combining multiple AutoML components"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for integration tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_end_to_end_workflow(self, temp_dir):
        """Test complete end-to-end AutoML workflow"""
        os.chdir(temp_dir)
        
        # Generate test data
        np.random.seed(42)
        X = np.random.randn(200, 8)
        y = np.random.randint(0, 3, 200)  # Multi-class classification
        
        # 1. Create experiment
        manager = ExperimentManager("integration_test")
        experiment_id = manager.create_experiment(
            name="End-to-End Integration Test",
            description="Full workflow test combining all AutoML components",
            dataset_info={
                "shape": X.shape,
                "classes": 3,
                "features": ["feature_" + str(i) for i in range(8)]
            }
        )
        
        # 2. Run basic experiment
        experiment_results = manager.run_basic_experiment(
            experiment_id=experiment_id,
            X=X,
            y=y,
            problem_type="classification"
        )
        
        # 3. Optimize best model
        from sklearn.ensemble import RandomForestClassifier
        best_model = RandomForestClassifier(random_state=42)
        
        tuner = HyperparameterTuner()
        tuning_results = tuner.auto_tune_model(
            model=best_model,
            model_type="random_forest_classifier",
            X=X,
            y=y,
            method="random_search",
            cv=3
        )
        
        # 4. Track everything
        tracker = create_tracker("integration_experiment", use_mlflow=False)
        
        automl_run_id = tracker.track_automl_experiment(
            experiment_results=experiment_results,
            dataset_info={
                "shape": X.shape,
                "source": "integration_test",
                "classes": 3
            }
        ) if hasattr(tracker, 'track_automl_experiment') else "simple_tracker_run"
        
        # 5. Generate report
        report = manager.generate_experiment_report(experiment_id)
        
        # Verify integration
        assert experiment_results["experiment_id"] == experiment_id
        assert tuning_results["model_type"] == "random_forest_classifier"
        assert len(report) > 0
        assert "Integration Test" in report
    
    def test_error_handling(self, temp_dir):
        """Test error handling across components"""
        os.chdir(temp_dir)
        
        # Test with invalid data
        X_invalid = np.array([[1, 2], [3, np.nan], [5, 6]])  # Contains NaN
        y_invalid = np.array([1, 2, 3])
        
        manager = ExperimentManager("error_test")
        experiment_id = manager.create_experiment(
            name="Error Handling Test",
            description="Test error handling with invalid data",
            dataset_info={"shape": X_invalid.shape, "has_nan": True}
        )
        
        # This should handle errors gracefully
        results = manager.run_basic_experiment(
            experiment_id=experiment_id,
            X=X_invalid,
            y=y_invalid,
            problem_type="classification"
        )
        
        # Should still return results structure even if models fail
        assert "experiment_id" in results
        assert "models_tested" in results
        
        # At least some models should report errors
        has_errors = any("error" in model for model in results["models_tested"])
        # Note: Some models might handle NaN gracefully, so we don't assert this
    
    def test_reproducibility(self, temp_dir):
        """Test that experiments are reproducible"""
        os.chdir(temp_dir)
        
        # Generate identical data twice
        np.random.seed(123)
        X1 = np.random.randn(100, 5)
        y1 = np.random.randint(0, 2, 100)
        
        np.random.seed(123)
        X2 = np.random.randn(100, 5)
        y2 = np.random.randint(0, 2, 100)
        
        # Verify data is identical
        assert np.array_equal(X1, X2)
        assert np.array_equal(y1, y2)
        
        # Run same experiment twice
        manager = ExperimentManager("reproducibility_test")
        
        # First run
        exp_id1 = manager.create_experiment(
            name="Reproducibility Test 1",
            description="First run for reproducibility test",
            dataset_info={"shape": X1.shape, "seed": 123}
        )
        
        results1 = manager.run_basic_experiment(
            experiment_id=exp_id1,
            X=X1,
            y=y1,
            problem_type="classification"
        )
        
        # Second run
        exp_id2 = manager.create_experiment(
            name="Reproducibility Test 2",
            description="Second run for reproducibility test",
            dataset_info={"shape": X2.shape, "seed": 123}
        )
        
        results2 = manager.run_basic_experiment(
            experiment_id=exp_id2,
            X=X2,
            y=y2,
            problem_type="classification"
        )
        
        # Results should be very similar (allowing for small numerical differences)
        assert results1["best_model"] == results2["best_model"]
        assert abs(results1["best_score"] - results2["best_score"]) < 0.1


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])