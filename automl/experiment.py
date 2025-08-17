"""
Automated Experiment Management for ML Project

This module handles automated machine learning experiments including:
- Model selection and evaluation
- Performance tracking
- Result analysis and reporting
- Integration with existing services
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
from datetime import datetime
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentManager:
    """Manages automated ML experiments and tracks results"""
    
    def __init__(self, experiment_name: str = "ml_project_automl"):
        self.experiment_name = experiment_name
        self.results_dir = Path("automl_results")
        self.results_dir.mkdir(exist_ok=True)
        self.experiments_history = []
        
    def create_experiment(self, 
                         name: str,
                         description: str,
                         dataset_info: Dict[str, Any]) -> str:
        """Create a new ML experiment"""
        
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        experiment_config = {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "dataset_info": dataset_info,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        
        # Save experiment config
        config_path = self.results_dir / f"{experiment_id}_config.json"
        with open(config_path, 'w') as f:
            json.dump(experiment_config, f, indent=2)
            
        self.experiments_history.append(experiment_config)
        logger.info(f"Created experiment: {experiment_id}")
        
        return experiment_id
    
    def run_basic_experiment(self, 
                           experiment_id: str,
                           X: np.ndarray, 
                           y: np.ndarray,
                           problem_type: str = "classification") -> Dict[str, Any]:
        """Run a basic automated ML experiment"""
        
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.linear_model import LogisticRegression, LinearRegression
        from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        results = {
            "experiment_id": experiment_id,
            "problem_type": problem_type,
            "data_shape": X.shape,
            "models_tested": [],
            "best_model": None,
            "best_score": None,
            "started_at": datetime.now().isoformat()
        }
        
        # Define models to test
        if problem_type == "classification":
            models = {
                "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "logistic_regression": LogisticRegression(random_state=42, max_iter=1000)
            }
            scoring_func = accuracy_score
        else:
            models = {
                "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
                "linear_regression": LinearRegression()
            }
            scoring_func = lambda y_true, y_pred: -mean_squared_error(y_true, y_pred)
        
        best_score = float('-inf')
        best_model_name = None
        
        # Test models
        for model_name, model in models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate score
                score = scoring_func(y_test, y_pred)
                
                model_result = {
                    "model_name": model_name,
                    "score": score,
                    "predictions_sample": y_pred[:5].tolist() if len(y_pred) > 0 else []
                }
                
                results["models_tested"].append(model_result)
                
                # Track best model
                if score > best_score:
                    best_score = score
                    best_model_name = model_name
                    
                logger.info(f"Model {model_name} scored: {score:.4f}")
                
            except Exception as e:
                logger.error(f"Error testing model {model_name}: {str(e)}")
                results["models_tested"].append({
                    "model_name": model_name,
                    "error": str(e)
                })
        
        # Update results with best model
        results.update({
            "best_model": best_model_name,
            "best_score": best_score,
            "completed_at": datetime.now().isoformat()
        })
        
        # Save results
        results_path = self.results_dir / f"{experiment_id}_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Experiment {experiment_id} completed. Best model: {best_model_name} (score: {best_score:.4f})")
        
        return results
    
    def get_experiment_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve results for a specific experiment"""
        
        results_path = self.results_dir / f"{experiment_id}_results.json"
        
        if results_path.exists():
            with open(results_path, 'r') as f:
                return json.load(f)
        return None
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments"""
        
        experiments = []
        for config_file in self.results_dir.glob("*_config.json"):
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Try to get results if available
            experiment_id = config["experiment_id"]
            results = self.get_experiment_results(experiment_id)
            
            if results:
                config["status"] = "completed"
                config["best_model"] = results.get("best_model")
                config["best_score"] = results.get("best_score")
            
            experiments.append(config)
            
        return sorted(experiments, key=lambda x: x["created_at"], reverse=True)
    
    def generate_experiment_report(self, experiment_id: str) -> str:
        """Generate a detailed report for an experiment"""
        
        config_path = self.results_dir / f"{experiment_id}_config.json"
        results_path = self.results_dir / f"{experiment_id}_results.json"
        
        if not config_path.exists():
            return f"Experiment {experiment_id} not found"
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        report = f"""
# Experiment Report: {config['name']}

**Experiment ID:** {experiment_id}
**Description:** {config['description']}
**Created:** {config['created_at']}

## Dataset Information
- Shape: {config['dataset_info'].get('shape', 'N/A')}
- Features: {config['dataset_info'].get('features', 'N/A')}
- Target: {config['dataset_info'].get('target', 'N/A')}

"""
        
        if results_path.exists():
            with open(results_path, 'r') as f:
                results = json.load(f)
                
            # Format best score safely
            best_score = results.get('best_score')
            best_score_str = f"{best_score:.4f}" if best_score is not None else 'N/A'
                
            report += f"""
## Results Summary
- **Best Model:** {results.get('best_model', 'N/A')}
- **Best Score:** {best_score_str}
- **Problem Type:** {results.get('problem_type', 'N/A')}
- **Data Shape:** {results.get('data_shape', 'N/A')}

## Models Tested
"""
            for model in results.get('models_tested', []):
                if 'error' in model:
                    report += f"- **{model['model_name']}:** Error - {model['error']}\n"
                else:
                    report += f"- **{model['model_name']}:** Score {model['score']:.4f}\n"
                    
        else:
            report += "\n## Results\nExperiment not completed yet.\n"
            
        return report

# Example usage and demo function
def run_demo_experiment():
    """Run a demonstration experiment with synthetic data"""
    
    from sklearn.datasets import make_classification
    
    # Create demo data
    X, y = make_classification(
        n_samples=1000, 
        n_features=10, 
        n_informative=5, 
        n_redundant=2, 
        random_state=42
    )
    
    # Initialize experiment manager
    manager = ExperimentManager()
    
    # Create experiment
    experiment_id = manager.create_experiment(
        name="Demo Classification Experiment",
        description="Demonstration of AutoML capabilities with synthetic classification data",
        dataset_info={
            "shape": X.shape,
            "features": 10,
            "target": "binary_classification",
            "source": "synthetic_sklearn"
        }
    )
    
    # Run experiment
    results = manager.run_basic_experiment(
        experiment_id=experiment_id,
        X=X,
        y=y,
        problem_type="classification"
    )
    
    # Generate report
    report = manager.generate_experiment_report(experiment_id)
    
    return {
        "experiment_id": experiment_id,
        "results": results,
        "report": report
    }

if __name__ == "__main__":
    # Run demo when script is executed directly
    print("Running AutoML Demo Experiment...")
    demo_results = run_demo_experiment()
    print(f"Demo completed! Experiment ID: {demo_results['experiment_id']}")
    print("\n" + "="*50)
    print(demo_results['report'])