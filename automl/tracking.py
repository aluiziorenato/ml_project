"""
MLflow Integration for Experiment Tracking

This module provides experiment tracking capabilities using MLflow:
- Track model parameters, metrics, and artifacts
- Compare different model runs
- Store model versions and metadata
- Integration with AutoML experiments
"""

# Try to import MLflow, fall back to None if not available
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.pytorch
    MLFLOW_AVAILABLE = True
except ImportError:
    mlflow = None
    MLFLOW_AVAILABLE = False

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime
from pathlib import Path
import os
import tempfile

logger = logging.getLogger(__name__)

class MLflowTracker:
    """MLflow-based experiment tracking system"""
    
    def __init__(self, 
                 experiment_name: str = "ml_project_automl",
                 tracking_uri: Optional[str] = None):
        """
        Initialize MLflow tracker
        
        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: MLflow tracking server URI (defaults to local file store)
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError("MLflow is not available. Install with: pip install mlflow")
            
        self.experiment_name = experiment_name
        
        # Set tracking URI
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        else:
            # Use local file store
            tracking_dir = Path("mlruns")
            tracking_dir.mkdir(exist_ok=True)
            mlflow.set_tracking_uri(f"file://{tracking_dir.absolute()}")
        
        # Set or create experiment
        try:
            self.experiment = mlflow.set_experiment(experiment_name)
            logger.info(f"Using MLflow experiment: {experiment_name}")
        except Exception as e:
            logger.error(f"Error setting up MLflow experiment: {e}")
            # Fallback to default experiment
            self.experiment = mlflow.set_experiment("Default")
    
    def start_run(self, 
                  run_name: Optional[str] = None,
                  tags: Optional[Dict[str, str]] = None) -> str:
        """Start a new MLflow run"""
        
        run = mlflow.start_run(run_name=run_name, tags=tags)
        logger.info(f"Started MLflow run: {run.info.run_id}")
        return run.info.run_id
    
    def log_parameters(self, params: Dict[str, Any]):
        """Log model parameters"""
        try:
            # Convert complex objects to strings
            clean_params = {}
            for key, value in params.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    clean_params[key] = value
                else:
                    clean_params[key] = str(value)
            
            mlflow.log_params(clean_params)
            logger.debug(f"Logged {len(clean_params)} parameters")
        except Exception as e:
            logger.error(f"Error logging parameters: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log model metrics"""
        try:
            mlflow.log_metrics(metrics, step=step)
            logger.debug(f"Logged {len(metrics)} metrics")
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
    
    def log_model(self, 
                  model, 
                  artifact_path: str = "model",
                  model_type: str = "sklearn"):
        """Log a trained model"""
        try:
            if model_type == "sklearn":
                mlflow.sklearn.log_model(model, artifact_path)
            elif model_type == "pytorch":
                mlflow.pytorch.log_model(model, artifact_path)
            else:
                # Generic python model
                mlflow.pyfunc.log_model(artifact_path, python_model=model)
            
            logger.info(f"Logged {model_type} model to {artifact_path}")
        except Exception as e:
            logger.error(f"Error logging model: {e}")
    
    def log_artifact(self, 
                     local_path: str, 
                     artifact_path: Optional[str] = None):
        """Log an artifact (file)"""
        try:
            mlflow.log_artifact(local_path, artifact_path)
            logger.debug(f"Logged artifact: {local_path}")
        except Exception as e:
            logger.error(f"Error logging artifact: {e}")
    
    def log_dict(self, 
                 dictionary: Dict, 
                 artifact_file: str):
        """Log a dictionary as JSON artifact"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(dictionary, f, indent=2, default=str)
                temp_path = f.name
            
            mlflow.log_artifact(temp_path, artifact_file)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            logger.debug(f"Logged dictionary as {artifact_file}")
        except Exception as e:
            logger.error(f"Error logging dictionary: {e}")
    
    def end_run(self):
        """End the current MLflow run"""
        try:
            mlflow.end_run()
            logger.debug("Ended MLflow run")
        except Exception as e:
            logger.error(f"Error ending run: {e}")
    
    def track_automl_experiment(self,
                               experiment_results: Dict[str, Any],
                               model=None,
                               dataset_info: Optional[Dict] = None) -> str:
        """Track a complete AutoML experiment"""
        
        run_name = f"automl_{experiment_results.get('experiment_id', 'unknown')}"
        tags = {
            "experiment_type": "automl",
            "problem_type": experiment_results.get("problem_type", "unknown")
        }
        
        if dataset_info:
            tags.update({
                "dataset_shape": str(dataset_info.get("shape", "unknown")),
                "dataset_source": dataset_info.get("source", "unknown")
            })
        
        run_id = self.start_run(run_name=run_name, tags=tags)
        
        try:
            # Log experiment metadata
            metadata = {
                "experiment_id": experiment_results.get("experiment_id"),
                "problem_type": experiment_results.get("problem_type"),
                "data_shape": experiment_results.get("data_shape"),
                "started_at": experiment_results.get("started_at"),
                "completed_at": experiment_results.get("completed_at")
            }
            self.log_parameters(metadata)
            
            # Log best model metrics
            if experiment_results.get("best_score") is not None:
                self.log_metrics({
                    "best_score": experiment_results["best_score"],
                    "models_tested": len(experiment_results.get("models_tested", []))
                })
            
            # Log individual model results
            for i, model_result in enumerate(experiment_results.get("models_tested", [])):
                if "score" in model_result:
                    self.log_metrics({
                        f"model_{model_result['model_name']}_score": model_result["score"]
                    }, step=i)
            
            # Log the model if provided
            if model:
                self.log_model(model, "best_model")
            
            # Log full experiment results as artifact
            self.log_dict(experiment_results, "experiment_results.json")
            
            # Log dataset info if provided
            if dataset_info:
                self.log_dict(dataset_info, "dataset_info.json")
            
            logger.info(f"Successfully tracked AutoML experiment: {run_id}")
            
        except Exception as e:
            logger.error(f"Error tracking AutoML experiment: {e}")
        finally:
            self.end_run()
        
        return run_id
    
    def track_hyperparameter_tuning(self,
                                   tuning_results: Dict[str, Any],
                                   best_model=None) -> str:
        """Track hyperparameter tuning results"""
        
        run_name = f"tuning_{tuning_results.get('tuning_id', 'unknown')}"
        tags = {
            "experiment_type": "hyperparameter_tuning",
            "tuning_method": tuning_results.get("method", "unknown"),
            "model_type": tuning_results.get("model_type", "unknown")
        }
        
        run_id = self.start_run(run_name=run_name, tags=tags)
        
        try:
            # Log tuning configuration
            config = {
                "tuning_id": tuning_results.get("tuning_id"),
                "method": tuning_results.get("method"),
                "model_type": tuning_results.get("model_type"),
                "cv_folds": tuning_results.get("cv_folds"),
                "scoring_metric": tuning_results.get("scoring_metric")
            }
            self.log_parameters(config)
            
            # Log best parameters
            if tuning_results.get("best_params"):
                self.log_parameters({"best_" + k: v for k, v in tuning_results["best_params"].items()})
            
            # Log performance metrics
            metrics = {}
            if tuning_results.get("best_score") is not None:
                metrics["best_score"] = tuning_results["best_score"]
            if tuning_results.get("duration_seconds") is not None:
                metrics["duration_seconds"] = tuning_results["duration_seconds"]
            if tuning_results.get("total_combinations"):
                metrics["total_combinations"] = tuning_results["total_combinations"]
            
            if metrics:
                self.log_metrics(metrics)
            
            # Log top results progression
            for i, result in enumerate(tuning_results.get("top_5_results", [])):
                if "mean_test_score" in result:
                    self.log_metrics({
                        f"top_{i+1}_score": result["mean_test_score"]
                    }, step=i)
            
            # Log the best model if provided
            if best_model:
                self.log_model(best_model, "tuned_model")
            
            # Log full tuning results as artifact
            self.log_dict(tuning_results, "tuning_results.json")
            
            logger.info(f"Successfully tracked hyperparameter tuning: {run_id}")
            
        except Exception as e:
            logger.error(f"Error tracking hyperparameter tuning: {e}")
        finally:
            self.end_run()
        
        return run_id
    
    def get_experiment_runs(self, 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """Get runs from the current experiment"""
        try:
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment.experiment_id],
                max_results=max_results,
                order_by=["start_time DESC"]
            )
            
            return runs.to_dict('records') if not runs.empty else []
        except Exception as e:
            logger.error(f"Error getting experiment runs: {e}")
            return []
    
    def compare_runs(self, 
                     run_ids: List[str],
                     metrics: List[str] = ["best_score"]) -> pd.DataFrame:
        """Compare multiple runs"""
        try:
            runs_data = []
            
            for run_id in run_ids:
                run = mlflow.get_run(run_id)
                run_data = {
                    "run_id": run_id,
                    "run_name": run.data.tags.get("mlflow.runName", ""),
                    "start_time": run.info.start_time,
                    "end_time": run.info.end_time,
                    "status": run.info.status
                }
                
                # Add requested metrics
                for metric in metrics:
                    run_data[metric] = run.data.metrics.get(metric)
                
                # Add some key parameters
                for param in ["model_type", "method", "problem_type"]:
                    run_data[param] = run.data.params.get(param)
                
                runs_data.append(run_data)
            
            return pd.DataFrame(runs_data)
            
        except Exception as e:
            logger.error(f"Error comparing runs: {e}")
            return pd.DataFrame()
    
    def get_best_run(self, 
                     metric: str = "best_score",
                     ascending: bool = False) -> Optional[Dict[str, Any]]:
        """Get the best run based on a metric"""
        try:
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment.experiment_id],
                order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"],
                max_results=1
            )
            
            if not runs.empty:
                return runs.iloc[0].to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting best run: {e}")
            return None
    
    def generate_experiment_summary(self) -> Dict[str, Any]:
        """Generate a summary of all experiments"""
        try:
            runs = self.get_experiment_runs()
            
            if not runs:
                return {"message": "No runs found"}
            
            summary = {
                "experiment_name": self.experiment_name,
                "total_runs": len(runs),
                "experiment_types": {},
                "model_types": {},
                "best_scores": [],
                "generated_at": datetime.now().isoformat()
            }
            
            for run in runs:
                # Count experiment types
                exp_type = run.get("tags.experiment_type", "unknown")
                summary["experiment_types"][exp_type] = summary["experiment_types"].get(exp_type, 0) + 1
                
                # Count model types
                model_type = run.get("params.model_type", "unknown")
                summary["model_types"][model_type] = summary["model_types"].get(model_type, 0) + 1
                
                # Collect best scores
                if run.get("metrics.best_score") is not None:
                    summary["best_scores"].append(run["metrics.best_score"])
            
            # Calculate statistics for best scores
            if summary["best_scores"]:
                summary["score_statistics"] = {
                    "mean": np.mean(summary["best_scores"]),
                    "std": np.std(summary["best_scores"]),
                    "min": np.min(summary["best_scores"]),
                    "max": np.max(summary["best_scores"])
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating experiment summary: {e}")
            return {"error": str(e)}

# Simplified MLflow tracker for cases where MLflow is not available
class SimpleTracker:
    """Simple file-based tracker as fallback when MLflow is not available"""
    
    def __init__(self, experiment_name: str = "ml_project_simple"):
        self.experiment_name = experiment_name
        self.tracking_dir = Path("simple_tracking")
        self.tracking_dir.mkdir(exist_ok=True)
        self.current_run_id = None
        self.current_run_data = {}
        
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict] = None) -> str:
        self.current_run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_run_data = {
            "run_id": self.current_run_id,
            "run_name": run_name or self.current_run_id,
            "tags": tags or {},
            "parameters": {},
            "metrics": {},
            "started_at": datetime.now().isoformat()
        }
        return self.current_run_id
    
    def log_parameters(self, params: Dict[str, Any]):
        if self.current_run_data:
            self.current_run_data["parameters"].update(params)
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        if self.current_run_data:
            for key, value in metrics.items():
                if step is not None:
                    key = f"{key}_step_{step}"
                self.current_run_data["metrics"][key] = value
    
    def end_run(self):
        if self.current_run_data:
            self.current_run_data["completed_at"] = datetime.now().isoformat()
            
            # Save run data
            run_file = self.tracking_dir / f"{self.current_run_id}.json"
            with open(run_file, 'w') as f:
                json.dump(self.current_run_data, f, indent=2, default=str)
            
            self.current_run_data = {}
            self.current_run_id = None

# Factory function to create appropriate tracker
def create_tracker(experiment_name: str = "ml_project_automl", 
                  use_mlflow: bool = True) -> Any:
    """Create an appropriate tracker based on availability"""
    
    if use_mlflow and MLFLOW_AVAILABLE:
        try:
            return MLflowTracker(experiment_name)
        except Exception as e:
            logger.warning(f"MLflow initialization failed: {e}, falling back to simple tracker")
            return SimpleTracker(experiment_name)
    else:
        return SimpleTracker(experiment_name)

# Demo function
def run_tracking_demo():
    """Run a demonstration of experiment tracking"""
    
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    
    # Create demo data
    X, y = make_classification(n_samples=500, n_features=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create tracker
    tracker = create_tracker("tracking_demo")
    
    # Track a simple experiment
    run_id = tracker.start_run(
        run_name="demo_random_forest",
        tags={"demo": "true", "model_type": "random_forest"}
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Log everything
    tracker.log_parameters({
        "n_estimators": 100,
        "random_state": 42,
        "model_type": "RandomForestClassifier"
    })
    
    tracker.log_metrics({
        "accuracy": accuracy,
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    })
    
    # End run
    tracker.end_run()
    
    print(f"Demo tracking completed! Run ID: {run_id}")
    print(f"Accuracy: {accuracy:.4f}")
    
    return {"run_id": run_id, "accuracy": accuracy}

if __name__ == "__main__":
    # Run demo when script is executed directly
    print("Running MLflow Tracking Demo...")
    demo_results = run_tracking_demo()
    print(f"Demo completed! Accuracy: {demo_results['accuracy']:.4f}")