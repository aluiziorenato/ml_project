"""
Automated Hyperparameter Tuning for ML Project

This module provides automated hyperparameter optimization using:
- Grid Search and Random Search
- Bayesian Optimization (with basic implementation)
- Integration with experiment tracking
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.metrics import make_scorer
import logging
import json
from datetime import datetime
from pathlib import Path
import itertools

logger = logging.getLogger(__name__)

class HyperparameterTuner:
    """Automated hyperparameter tuning for ML models"""
    
    def __init__(self, results_dir: str = "automl_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.tuning_history = []
        
    def define_parameter_space(self, model_type: str) -> Dict[str, List]:
        """Define parameter search spaces for different model types"""
        
        parameter_spaces = {
            "random_forest_classifier": {
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 5, 10, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None]
            },
            "random_forest_regressor": {
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 5, 10, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None]
            },
            "logistic_regression": {
                "C": [0.01, 0.1, 1, 10, 100],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "lbfgs"],
                "max_iter": [500, 1000, 2000]
            },
            "linear_regression": {
                "fit_intercept": [True, False],
                "normalize": [True, False]
            },
            "svm_classifier": {
                "C": [0.1, 1, 10, 100],
                "kernel": ["linear", "rbf", "poly"],
                "gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1]
            },
            "gradient_boosting": {
                "n_estimators": [50, 100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "subsample": [0.8, 0.9, 1.0]
            }
        }
        
        return parameter_spaces.get(model_type, {})
    
    def grid_search_tuning(self, 
                          model,
                          X: np.ndarray,
                          y: np.ndarray,
                          param_grid: Dict[str, List],
                          cv: int = 5,
                          scoring: str = "accuracy") -> Dict[str, Any]:
        """Perform grid search hyperparameter tuning"""
        
        logger.info(f"Starting grid search with {len(param_grid)} parameters")
        
        # Calculate total combinations
        total_combinations = 1
        for param_values in param_grid.values():
            total_combinations *= len(param_values)
            
        logger.info(f"Total parameter combinations to test: {total_combinations}")
        
        # Perform grid search
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1
        )
        
        start_time = datetime.now()
        grid_search.fit(X, y)
        end_time = datetime.now()
        
        # Extract results
        results = {
            "method": "grid_search",
            "best_params": grid_search.best_params_,
            "best_score": grid_search.best_score_,
            "total_combinations": total_combinations,
            "cv_folds": cv,
            "scoring_metric": scoring,
            "duration_seconds": (end_time - start_time).total_seconds(),
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat()
        }
        
        # Get top 5 results
        results_df = pd.DataFrame(grid_search.cv_results_)
        top_results = results_df.nlargest(5, 'mean_test_score')[
            ['params', 'mean_test_score', 'std_test_score']
        ].to_dict('records')
        
        results["top_5_results"] = top_results
        
        logger.info(f"Grid search completed. Best score: {results['best_score']:.4f}")
        
        return results
    
    def random_search_tuning(self,
                           model,
                           X: np.ndarray,
                           y: np.ndarray,
                           param_distributions: Dict[str, List],
                           n_iter: int = 50,
                           cv: int = 5,
                           scoring: str = "accuracy") -> Dict[str, Any]:
        """Perform random search hyperparameter tuning"""
        
        logger.info(f"Starting random search with {n_iter} iterations")
        
        # Perform random search
        random_search = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1,
            random_state=42
        )
        
        start_time = datetime.now()
        random_search.fit(X, y)
        end_time = datetime.now()
        
        # Extract results
        results = {
            "method": "random_search",
            "best_params": random_search.best_params_,
            "best_score": random_search.best_score_,
            "n_iterations": n_iter,
            "cv_folds": cv,
            "scoring_metric": scoring,
            "duration_seconds": (end_time - start_time).total_seconds(),
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat()
        }
        
        # Get top 5 results
        results_df = pd.DataFrame(random_search.cv_results_)
        top_results = results_df.nlargest(5, 'mean_test_score')[
            ['params', 'mean_test_score', 'std_test_score']
        ].to_dict('records')
        
        results["top_5_results"] = top_results
        
        logger.info(f"Random search completed. Best score: {results['best_score']:.4f}")
        
        return results
    
    def bayesian_optimization_simple(self,
                                   model,
                                   X: np.ndarray,
                                   y: np.ndarray,
                                   param_space: Dict[str, List],
                                   n_iter: int = 20,
                                   cv: int = 5,
                                   scoring: str = "accuracy") -> Dict[str, Any]:
        """Simple Bayesian optimization using random sampling with memory"""
        
        logger.info(f"Starting simple Bayesian optimization with {n_iter} iterations")
        
        # Track all tested parameters and scores
        tested_params = []
        tested_scores = []
        
        best_params = None
        best_score = float('-inf')
        
        start_time = datetime.now()
        
        for iteration in range(n_iter):
            # Generate random parameters for this iteration
            current_params = {}
            for param_name, param_values in param_space.items():
                current_params[param_name] = np.random.choice(param_values)
            
            # Check if we've already tested these parameters
            if current_params in tested_params:
                continue
                
            try:
                # Set model parameters
                model.set_params(**current_params)
                
                # Evaluate using cross-validation
                scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
                mean_score = np.mean(scores)
                
                # Track results
                tested_params.append(current_params.copy())
                tested_scores.append(mean_score)
                
                # Update best if this is better
                if mean_score > best_score:
                    best_score = mean_score
                    best_params = current_params.copy()
                    
                logger.info(f"Iteration {iteration + 1}/{n_iter}: Score {mean_score:.4f}")
                
            except Exception as e:
                logger.warning(f"Error in iteration {iteration + 1}: {str(e)}")
                continue
        
        end_time = datetime.now()
        
        # Prepare results
        results = {
            "method": "bayesian_optimization_simple",
            "best_params": best_params,
            "best_score": best_score,
            "n_iterations": n_iter,
            "actual_iterations": len(tested_params),
            "cv_folds": cv,
            "scoring_metric": scoring,
            "duration_seconds": (end_time - start_time).total_seconds(),
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat()
        }
        
        # Get top 5 results
        if tested_scores:
            results_data = list(zip(tested_params, tested_scores))
            results_data.sort(key=lambda x: x[1], reverse=True)
            
            top_5 = results_data[:5]
            results["top_5_results"] = [
                {
                    "params": params,
                    "mean_test_score": score,
                    "std_test_score": 0.0  # Not calculated in this simple version
                }
                for params, score in top_5
            ]
        
        logger.info(f"Bayesian optimization completed. Best score: {best_score:.4f}")
        
        return results
    
    def auto_tune_model(self,
                       model,
                       model_type: str,
                       X: np.ndarray,
                       y: np.ndarray,
                       method: str = "random_search",
                       scoring: str = "accuracy",
                       cv: int = 5) -> Dict[str, Any]:
        """Automatically tune a model using the specified method"""
        
        # Get parameter space for the model type
        param_space = self.define_parameter_space(model_type)
        
        if not param_space:
            logger.warning(f"No parameter space defined for model type: {model_type}")
            return {
                "error": f"No parameter space defined for model type: {model_type}",
                "available_types": list(self.define_parameter_space("").keys())
            }
        
        tuning_id = f"tune_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting auto-tuning for {model_type} using {method}")
        
        # Choose tuning method
        if method == "grid_search":
            results = self.grid_search_tuning(
                model=model,
                X=X,
                y=y,
                param_grid=param_space,
                cv=cv,
                scoring=scoring
            )
        elif method == "random_search":
            results = self.random_search_tuning(
                model=model,
                X=X,
                y=y,
                param_distributions=param_space,
                n_iter=50,
                cv=cv,
                scoring=scoring
            )
        elif method == "bayesian":
            results = self.bayesian_optimization_simple(
                model=model,
                X=X,
                y=y,
                param_space=param_space,
                n_iter=20,
                cv=cv,
                scoring=scoring
            )
        else:
            return {
                "error": f"Unknown tuning method: {method}",
                "available_methods": ["grid_search", "random_search", "bayesian"]
            }
        
        # Add metadata
        results.update({
            "tuning_id": tuning_id,
            "model_type": model_type,
            "data_shape": X.shape,
            "parameter_space": param_space
        })
        
        # Save results
        results_path = self.results_dir / f"{tuning_id}_tuning.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.tuning_history.append(results)
        
        return results
    
    def compare_tuning_methods(self,
                             model,
                             model_type: str,
                             X: np.ndarray,
                             y: np.ndarray,
                             scoring: str = "accuracy",
                             cv: int = 3) -> Dict[str, Any]:
        """Compare different tuning methods on the same model and data"""
        
        logger.info(f"Comparing tuning methods for {model_type}")
        
        methods = ["random_search", "bayesian"]  # Exclude grid_search for speed
        comparison_results = {}
        
        for method in methods:
            logger.info(f"Testing method: {method}")
            
            try:
                # Create a fresh copy of the model for each method
                from sklearn.base import clone
                model_copy = clone(model)
                
                results = self.auto_tune_model(
                    model=model_copy,
                    model_type=model_type,
                    X=X,
                    y=y,
                    method=method,
                    scoring=scoring,
                    cv=cv
                )
                
                comparison_results[method] = {
                    "best_score": results.get("best_score"),
                    "best_params": results.get("best_params"),
                    "duration_seconds": results.get("duration_seconds"),
                    "method_info": results.get("method")
                }
                
            except Exception as e:
                logger.error(f"Error testing method {method}: {str(e)}")
                comparison_results[method] = {"error": str(e)}
        
        # Find best overall method
        best_method = None
        best_score = float('-inf')
        
        for method, results in comparison_results.items():
            if "error" not in results and results.get("best_score", float('-inf')) > best_score:
                best_score = results["best_score"]
                best_method = method
        
        summary = {
            "comparison_id": f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "model_type": model_type,
            "data_shape": X.shape,
            "methods_compared": methods,
            "results": comparison_results,
            "best_method": best_method,
            "best_overall_score": best_score,
            "completed_at": datetime.now().isoformat()
        }
        
        # Save comparison results
        comp_path = self.results_dir / f"{summary['comparison_id']}_comparison.json"
        with open(comp_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Method comparison completed. Best method: {best_method} (score: {best_score:.4f})")
        
        return summary

# Demo function
def run_tuning_demo():
    """Run a demonstration of hyperparameter tuning"""
    
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    
    # Create demo data
    X, y = make_classification(
        n_samples=500,  # Smaller dataset for faster demo
        n_features=10,
        n_informative=5,
        n_redundant=2,
        random_state=42
    )
    
    # Initialize tuner
    tuner = HyperparameterTuner()
    
    # Create model
    model = RandomForestClassifier(random_state=42)
    
    # Run tuning comparison
    comparison_results = tuner.compare_tuning_methods(
        model=model,
        model_type="random_forest_classifier",
        X=X,
        y=y,
        scoring="accuracy",
        cv=3  # Faster for demo
    )
    
    return comparison_results

if __name__ == "__main__":
    # Run demo when script is executed directly
    print("Running Hyperparameter Tuning Demo...")
    demo_results = run_tuning_demo()
    print(f"Demo completed! Best method: {demo_results['best_method']}")
    print(f"Best score: {demo_results['best_overall_score']:.4f}")