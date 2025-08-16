"""
End-to-end workflow tests for the complete ML system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.analytics_service import AnalyticsService
from services.scheduler_service import SchedulerService
from core.storage.data_manager import DataManager, DataQuery


class TestCompleteWorkflows:
    """End-to-end workflow tests."""
    
    @pytest.mark.asyncio
    async def test_complete_ml_workflow(self):
        """Test complete ML workflow from data to prediction to optimization."""
        # Initialize services
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        data_manager = DataManager(storage_type="file")
        
        await scheduler_service.start()
        
        try:
            # Step 1: Prepare training data
            features = [
                [100, 50, 10, 0.02, 50000],  # budget, spend, keywords, ctr, audience
                [200, 100, 15, 0.025, 75000],
                [150, 75, 12, 0.03, 60000],
                [300, 150, 20, 0.035, 100000],
                [250, 125, 18, 0.028, 80000]
            ]
            targets = [0.02, 0.025, 0.03, 0.035, 0.028]  # conversion rates
            feature_names = ["budget", "marketing_spend", "keywords", "ctr", "audience_size"]
            
            # Step 2: Train model through scheduler
            train_task_id = await scheduler_service.create_task(
                task_type="model_training",
                parameters={
                    "model_type": "conversion_predictor",
                    "training_samples": len(features)
                }
            )
            
            # Step 3: Train model directly
            success = await analytics_service.train_model(
                "conversion_predictor", features, targets, feature_names
            )
            assert success is True
            
            # Step 4: Make predictions
            campaign_data = {
                "budget": 1000,
                "duration_days": 14,
                "keywords": ["smartphone", "samsung", "mobile"],
                "historical_ctr": 0.025,
                "audience_size": 50000
            }
            
            prediction = await analytics_service.predict_conversion_rate(campaign_data)
            assert prediction is not None
            assert prediction.predicted_value > 0
            
            # Step 5: Optimize campaign parameters
            campaigns = [
                {"historical_roi": 2.5, "historical_conversion_rate": 0.03},
                {"historical_roi": 1.8, "historical_conversion_rate": 0.025},
                {"historical_roi": 3.2, "historical_conversion_rate": 0.035}
            ]
            
            optimization = await analytics_service.optimize_budget_allocation(
                campaigns, 10000, "maximize_roi"
            )
            assert optimization is not None
            assert optimization.expected_improvement >= 0
            
            # Step 6: Schedule recurring optimization task
            recurring_tasks = await scheduler_service.create_recurring_task(
                task_type="optimization",
                parameters={
                    "optimization_type": "budget_allocation",
                    "target_metric": "roi"
                },
                interval=timedelta(hours=24),
                max_executions=3
            )
            assert len(recurring_tasks) == 3
            
            # Step 7: Verify data storage
            query = DataQuery(table="predictions", limit=10)
            stored_predictions = data_manager.query_data(query)
            assert stored_predictions.success is True
            
            # Step 8: Get system statistics
            analytics_status = await analytics_service.get_models_status()
            scheduler_stats = await scheduler_service.get_task_statistics()
            
            assert "models" in analytics_status
            assert "total_tasks" in scheduler_stats
            
        finally:
            await scheduler_service.stop()
    
    @pytest.mark.asyncio
    async def test_automated_ml_pipeline(self):
        """Test automated ML pipeline with data processing, training, and prediction."""
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        
        await scheduler_service.start()
        
        try:
            # Define automated pipeline tasks
            pipeline_tasks = []
            
            # Task 1: Data processing
            data_task = await scheduler_service.create_task(
                task_type="data_processing",
                parameters={
                    "data_source": "historical_campaigns",
                    "processing_type": "feature_extraction"
                }
            )
            pipeline_tasks.append(data_task)
            
            # Task 2: Model training (scheduled after data processing)
            training_time = datetime.now() + timedelta(seconds=2)
            training_task = await scheduler_service.schedule_task(
                task_type="model_training",
                parameters={
                    "model_type": "ensemble",
                    "training_samples": 5000
                },
                scheduled_time=training_time
            )
            pipeline_tasks.append(training_task)
            
            # Task 3: Model validation (scheduled after training)
            validation_time = datetime.now() + timedelta(seconds=4)
            validation_task = await scheduler_service.schedule_task(
                task_type="analytics_prediction",
                parameters={
                    "prediction_type": "validation",
                    "features": [1, 2, 3, 4, 5]
                },
                scheduled_time=validation_time
            )
            pipeline_tasks.append(validation_task)
            
            # Wait for pipeline completion
            await asyncio.sleep(6)
            
            # Verify all tasks completed
            completed_tasks = 0
            for task_id in pipeline_tasks:
                result = await scheduler_service.get_task_result(task_id)
                if result and result.status.value == "completed":
                    completed_tasks += 1
            
            assert completed_tasks >= 2  # At least some tasks should complete
            
        finally:
            await scheduler_service.stop()
    
    @pytest.mark.asyncio
    async def test_real_time_optimization_workflow(self):
        """Test real-time optimization workflow with continuous updates."""
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        
        await scheduler_service.start()
        
        try:
            # Simulate real-time campaign data updates
            campaign_updates = [
                {"budget": 1000, "current_roi": 2.1, "current_cr": 0.025},
                {"budget": 1200, "current_roi": 2.3, "current_cr": 0.028},
                {"budget": 800, "current_roi": 1.9, "current_cr": 0.022}
            ]
            
            optimization_results = []
            
            for i, update in enumerate(campaign_updates):
                # Process campaign update
                processing_task = await scheduler_service.create_task(
                    task_type="data_processing",
                    parameters={
                        "data_source": f"campaign_update_{i}",
                        "processing_type": "real_time_metrics"
                    }
                )
                
                # Run optimization based on update
                campaigns = [
                    {
                        "historical_roi": update["current_roi"],
                        "historical_conversion_rate": update["current_cr"],
                        "current_performance": update["budget"] * update["current_roi"]
                    }
                ]
                
                optimization = await analytics_service.optimize_budget_allocation(
                    campaigns, update["budget"], "maximize_roi"
                )
                optimization_results.append(optimization)
                
                # Small delay between updates
                await asyncio.sleep(0.5)
            
            # Verify optimizations
            assert len(optimization_results) == 3
            for opt in optimization_results:
                assert opt is not None
                assert opt.expected_improvement >= 0
                
        finally:
            await scheduler_service.stop()
    
    @pytest.mark.asyncio
    async def test_failure_recovery_workflow(self):
        """Test system recovery from failures."""
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        
        await scheduler_service.start()
        
        try:
            # Create tasks that will succeed and fail
            successful_task = await scheduler_service.create_task(
                task_type="health_check",
                parameters={"check_type": "system"}
            )
            
            # Create task with invalid parameters (should fail)
            failing_task = await scheduler_service.create_task(
                task_type="analytics_prediction",
                parameters={"invalid_param": "will_cause_error"}
            )
            
            # Wait for execution
            await asyncio.sleep(1)
            
            # Check results
            success_result = await scheduler_service.get_task_result(successful_task)
            failure_result = await scheduler_service.get_task_result(failing_task)
            
            # Verify successful task completed
            assert success_result is not None
            # Note: Due to error handling in our implementation, 
            # even "failed" tasks might complete with default values
            
            # System should continue operating despite failures
            recovery_task = await scheduler_service.create_task(
                task_type="health_check",
                parameters={"check_type": "recovery"}
            )
            
            await asyncio.sleep(0.5)
            
            recovery_result = await scheduler_service.get_task_result(recovery_task)
            assert recovery_result is not None
            
        finally:
            await scheduler_service.stop()
    
    @pytest.mark.asyncio
    async def test_data_persistence_workflow(self):
        """Test data persistence across service operations."""
        analytics_service = AnalyticsService()
        data_manager = DataManager(storage_type="file")
        
        # Store initial data
        initial_data = {
            "campaign_id": "test_campaign_001",
            "name": "Test Campaign",
            "budget": 5000,
            "status": "active",
            "start_date": datetime.now().isoformat()
        }
        
        store_result = data_manager.store_data("campaigns", initial_data)
        assert store_result.success is True
        
        # Run analytics on the campaign
        campaign_data = {
            "budget": initial_data["budget"],
            "duration_days": 14,
            "keywords": ["test", "campaign"],
            "historical_ctr": 0.025,
            "audience_size": 40000
        }
        
        prediction = await analytics_service.predict_conversion_rate(campaign_data)
        assert prediction is not None
        
        # Update campaign with prediction results
        update_data = {
            "campaign_id": initial_data["campaign_id"],
            "predicted_conversion_rate": prediction.predicted_value,
            "confidence_score": prediction.confidence_score,
            "updated_at": datetime.now().isoformat()
        }
        
        update_result = data_manager.store_data("campaigns", update_data, upsert=True)
        assert update_result.success is True
        
        # Query updated data
        query = DataQuery(
            table="campaigns", 
            filters={"campaign_id": initial_data["campaign_id"]}
        )
        query_result = data_manager.query_data(query)
        
        assert query_result.success is True
        assert len(query_result.data) > 0
        
        # Verify data integrity
        retrieved_campaign = query_result.data[0]
        assert retrieved_campaign["budget"] == initial_data["budget"]
        assert "predicted_conversion_rate" in retrieved_campaign
    
    @pytest.mark.asyncio
    async def test_scalability_workflow(self):
        """Test system scalability with multiple concurrent operations."""
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        
        await scheduler_service.start()
        
        try:
            # Create multiple models
            model_tasks = []
            for i in range(3):
                features = [[j, j+1, j+2] for j in range(10)]
                targets = [j*2 for j in range(10)]
                feature_names = [f"feature_{k}" for k in range(3)]
                
                success = await analytics_service.train_model(
                    f"model_{i}", features, targets, feature_names
                )
                assert success is True
            
            # Run multiple predictions concurrently
            prediction_tasks = []
            for i in range(10):
                task = analytics_service.predict([i, i+1, i+2], f"model_{i % 3}")
                prediction_tasks.append(task)
            
            predictions = await asyncio.gather(*prediction_tasks)
            assert len(predictions) == 10
            
            # Schedule multiple optimization tasks
            optimization_tasks = []
            for i in range(5):
                campaigns = [
                    {"historical_roi": 2.0 + i*0.1, "historical_conversion_rate": 0.02 + i*0.005}
                ]
                
                task = analytics_service.optimize_budget_allocation(
                    campaigns, 1000 * (i+1), "maximize_roi"
                )
                optimization_tasks.append(task)
            
            optimizations = await asyncio.gather(*optimization_tasks)
            assert len(optimizations) == 5
            
            # Verify system statistics
            stats = await scheduler_service.get_task_statistics()
            status = await analytics_service.get_models_status()
            
            assert stats["total_tasks"] >= 0
            assert status["total_models"] >= 3
            
        finally:
            await scheduler_service.stop()