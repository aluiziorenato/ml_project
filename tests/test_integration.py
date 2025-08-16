"""
Integration tests for complete API and service workflow.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from api.routes.analytics import router as analytics_router
from api.routes.scheduler import router as scheduler_router
from services.analytics_service import AnalyticsService
from services.scheduler_service import SchedulerService


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.mark.asyncio
    async def test_analytics_prediction_workflow(self):
        """Test complete analytics prediction workflow."""
        # Test prediction endpoint
        service = AnalyticsService()
        
        features = [1.0, 2.0, 3.0]
        result = await service.predict(features, "linear")
        
        assert result is not None
        assert result.predicted_value > 0
        assert 0 <= result.confidence_score <= 1
        assert result.model_version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_sales_forecast_workflow(self):
        """Test sales forecasting workflow."""
        service = AnalyticsService()
        
        historical_data = {
            "sales": [100, 120, 110, 130, 140],
            "marketing_spend": [50, 60, 55, 65, 70]
        }
        
        result = await service.forecast_sales(historical_data, 30)
        
        assert result is not None
        assert result.predicted_value > 0
        assert result.metadata["forecast_days"] == 30
    
    @pytest.mark.asyncio
    async def test_optimization_workflow(self):
        """Test optimization workflow."""
        service = AnalyticsService()
        
        campaigns = [
            {"historical_roi": 2.5, "historical_conversion_rate": 0.03},
            {"historical_roi": 1.8, "historical_conversion_rate": 0.02}
        ]
        
        result = await service.optimize_budget_allocation(campaigns, 10000, "maximize_roi")
        
        assert result is not None
        assert result.expected_improvement >= 0
        assert "campaign_0_budget" in result.optimized_parameters
        assert "campaign_1_budget" in result.optimized_parameters
    
    @pytest.mark.asyncio
    async def test_scheduler_task_workflow(self):
        """Test scheduler task creation and execution workflow."""
        service = SchedulerService()
        await service.start()
        
        try:
            # Create immediate task
            task_id = await service.create_task(
                task_type="analytics_prediction",
                parameters={"prediction_type": "test", "features": [1, 2, 3]}
            )
            
            assert task_id is not None
            
            # Wait for execution
            await asyncio.sleep(0.5)
            
            # Check result
            result = await service.get_task_result(task_id)
            assert result is not None
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_scheduled_task_workflow(self):
        """Test scheduled task workflow."""
        service = SchedulerService()
        await service.start()
        
        try:
            # Schedule task for near future
            future_time = datetime.now() + timedelta(seconds=1)
            task_id = await service.schedule_task(
                task_type="data_processing",
                parameters={"data_source": "test", "processing_type": "cleanup"},
                scheduled_time=future_time
            )
            
            assert task_id is not None
            
            # Wait for execution
            await asyncio.sleep(2)
            
            # Check result
            result = await service.get_task_result(task_id)
            assert result is not None
            
        finally:
            await service.stop()


class TestServiceIntegration:
    """Integration tests for service layer."""
    
    @pytest.mark.asyncio
    async def test_analytics_service_model_training(self):
        """Test analytics service model training integration."""
        service = AnalyticsService()
        
        features = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        targets = [10, 20, 30]
        feature_names = ["feat1", "feat2", "feat3"]
        
        success = await service.train_model("test_model", features, targets, feature_names)
        assert success is True
        
        # Test prediction with trained model
        result = await service.predict([2, 3, 4], "test_model")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_analytics_service_status(self):
        """Test analytics service status reporting."""
        service = AnalyticsService()
        
        status = await service.get_models_status()
        
        assert "models" in status
        assert "total_models" in status
        assert "trained_models" in status
        assert "timestamp" in status
    
    @pytest.mark.asyncio
    async def test_scheduler_service_statistics(self):
        """Test scheduler service statistics."""
        service = SchedulerService()
        await service.start()
        
        try:
            # Create some tasks
            task1 = await service.create_task("health_check", {"check_type": "system"})
            task2 = await service.create_task("cleanup", {"cleanup_type": "logs"})
            
            await asyncio.sleep(0.5)
            
            stats = await service.get_task_statistics()
            
            assert "total_tasks" in stats
            assert "completed_tasks" in stats
            assert "storage_stats" in stats
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_cross_service_integration(self):
        """Test integration between analytics and scheduler services."""
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        
        await scheduler_service.start()
        
        try:
            # Register custom analytics task
            async def analytics_task(params):
                features = params.get("features", [1, 2, 3])
                result = await analytics_service.predict(features)
                return {
                    "prediction": result.predicted_value,
                    "confidence": result.confidence_score
                }
            
            scheduler_service.register_task_function("custom_analytics", analytics_task)
            
            # Create analytics task through scheduler
            task_id = await scheduler_service.create_task(
                task_type="custom_analytics",
                parameters={"features": [5, 10, 15]}
            )
            
            await asyncio.sleep(0.5)
            
            result = await scheduler_service.get_task_result(task_id)
            assert result is not None
            assert "prediction" in result.result_data
            assert "confidence" in result.result_data
            
        finally:
            await scheduler_service.stop()


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_analytics_service_error_handling(self):
        """Test analytics service error handling."""
        service = AnalyticsService()
        
        # Test with invalid data
        with pytest.raises(Exception):
            await service.predict(None, "invalid_model")
    
    @pytest.mark.asyncio
    async def test_scheduler_service_error_handling(self):
        """Test scheduler service error handling."""
        service = SchedulerService()
        
        # Test with invalid task type
        with pytest.raises(ValueError):
            await service.create_task("invalid_task_type", {})
    
    @pytest.mark.asyncio
    async def test_data_storage_integration(self):
        """Test data storage integration."""
        from core.storage.data_manager import DataManager, DataQuery
        
        data_manager = DataManager(storage_type="file")
        
        # Test storing data
        test_data = {
            "test_id": "test_123",
            "value": 42.0,
            "timestamp": datetime.now().isoformat()
        }
        
        result = data_manager.store_data("test_table", test_data)
        assert result.success is True
        
        # Test querying data
        query = DataQuery(table="test_table", filters={"test_id": "test_123"})
        result = data_manager.query_data(query)
        
        assert result.success is True
        assert len(result.data) > 0
        assert result.data[0]["value"] == 42.0


class TestPerformance:
    """Performance tests for integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_concurrent_predictions(self):
        """Test concurrent prediction requests."""
        service = AnalyticsService()
        
        async def make_prediction(features):
            return await service.predict(features)
        
        # Create multiple concurrent predictions
        tasks = [
            make_prediction([i, i+1, i+2])
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        for result in results:
            assert result is not None
            assert result.predicted_value is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test concurrent task execution."""
        service = SchedulerService()
        await service.start()
        
        try:
            # Create multiple concurrent tasks
            task_ids = []
            for i in range(5):
                task_id = await service.create_task(
                    task_type="health_check",
                    parameters={"check_type": f"test_{i}"}
                )
                task_ids.append(task_id)
            
            # Wait for all tasks to complete
            await asyncio.sleep(1)
            
            # Check all results
            results = []
            for task_id in task_ids:
                result = await service.get_task_result(task_id)
                results.append(result)
            
            assert len(results) == 5
            for result in results:
                assert result is not None
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_large_data_processing(self):
        """Test processing large datasets."""
        service = AnalyticsService()
        
        # Generate large historical data
        large_historical_data = {
            "sales": [100 + i for i in range(1000)],
            "marketing_spend": [50 + i*0.5 for i in range(1000)]
        }
        
        result = await service.forecast_sales(large_historical_data, 30)
        
        assert result is not None
        assert result.predicted_value > 0