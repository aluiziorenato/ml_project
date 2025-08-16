"""
Integration tests for complete system workflow.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.analytics_service import AnalyticsService
from services.scheduler_service import SchedulerService
from core.storage.data_manager import DataManager


class TestCompleteSystemIntegration:
    """Integration tests for the complete ML system."""
    
    @pytest.mark.asyncio
    async def test_complete_analytics_workflow(self):
        """Test complete analytics workflow from data to prediction to optimization."""
        # Initialize services
        analytics_service = AnalyticsService()
        
        # Step 1: Make predictions
        campaign_data = {
            "budget": 1000,
            "duration_days": 14,
            "keywords": ["smartphone", "samsung", "mobile"],
            "historical_ctr": 0.025,
            "audience_size": 50000
        }
        
        prediction = await analytics_service.predict_conversion_rate(campaign_data)
        assert prediction is not None
        assert prediction.predicted_value >= 0
        
        # Step 2: Run optimization
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
        
        # Step 3: Get model status
        status = await analytics_service.get_models_status()
        assert "models" in status
        assert "total_models" in status
    
    @pytest.mark.asyncio
    async def test_complete_scheduler_workflow(self):
        """Test complete scheduler workflow with task management."""
        scheduler_service = SchedulerService()
        await scheduler_service.start()
        
        try:
            # Step 1: Create immediate task
            task_id = await scheduler_service.create_task(
                task_type="analytics_prediction",
                parameters={"prediction_type": "test", "features": [1, 2, 3]}
            )
            assert task_id is not None
            
            # Wait for execution
            await asyncio.sleep(1)
            
            # Step 2: Check result
            result = await scheduler_service.get_task_result(task_id)
            assert result is not None
            
            # Step 3: Get statistics
            stats = await scheduler_service.get_task_statistics()
            assert "total_tasks" in stats
            
        finally:
            await scheduler_service.stop()
    
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
            
            await asyncio.sleep(2)
            
            result = await scheduler_service.get_task_result(task_id)
            assert result is not None
            
        finally:
            await scheduler_service.stop()
    
    def test_data_storage_integration(self):
        """Test data storage across services."""
        data_manager = DataManager(storage_type="file")
        
        # Store test data
        test_data = {
            "campaign_id": "test_campaign_001",
            "name": "Test Campaign",
            "budget": 5000,
            "status": "active",
            "start_date": datetime.now().isoformat()
        }
        
        store_result = data_manager.store_data("campaigns", test_data)
        assert store_result.success is True
        
        # Query the data
        from core.storage.data_manager import DataQuery
        query = DataQuery(
            table="campaigns", 
            filters={"campaign_id": "test_campaign_001"}
        )
        query_result = data_manager.query_data(query)
        
        assert query_result.success is True
        assert len(query_result.data) > 0
        assert query_result.data[0]["name"] == "Test Campaign"
    
    @pytest.mark.asyncio
    async def test_performance_and_scalability(self):
        """Test system performance with multiple operations."""
        analytics_service = AnalyticsService()
        
        # Run multiple predictions concurrently
        prediction_tasks = []
        for i in range(5):
            task = analytics_service.predict([i, i+1, i+2], "linear")
            prediction_tasks.append(task)
        
        predictions = await asyncio.gather(*prediction_tasks)
        assert len(predictions) == 5
        
        for pred in predictions:
            assert pred is not None
            assert pred.predicted_value is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test system error handling and recovery."""
        analytics_service = AnalyticsService()
        
        # Test with invalid data
        try:
            result = await analytics_service.predict([], "invalid_model")
            # Should handle gracefully
            assert result is not None
        except Exception as e:
            # Or should raise appropriate exception
            assert isinstance(e, (ValueError, TypeError))
    
    @pytest.mark.asyncio  
    async def test_real_time_workflow_simulation(self):
        """Test real-time workflow simulation."""
        analytics_service = AnalyticsService()
        scheduler_service = SchedulerService()
        
        await scheduler_service.start()
        
        try:
            # Simulate real-time campaign updates
            campaign_updates = [
                {"budget": 1000, "keywords": ["test1"]},
                {"budget": 1200, "keywords": ["test2", "test3"]},
                {"budget": 800, "keywords": ["test4"]}
            ]
            
            results = []
            
            for update in campaign_updates:
                # Process each update
                prediction = await analytics_service.predict_conversion_rate(update)
                results.append(prediction)
                
                # Small delay to simulate real-time
                await asyncio.sleep(0.1)
            
            # Verify all results
            assert len(results) == 3
            for result in results:
                assert result is not None
                assert result.predicted_value >= 0
                
        finally:
            await scheduler_service.stop()
    
    def test_system_health_and_monitoring(self):
        """Test system health monitoring capabilities."""
        analytics_service = AnalyticsService()
        data_manager = DataManager(storage_type="file")
        
        # Test analytics service health
        asyncio.run(analytics_service.get_models_status())
        
        # Test data storage health
        storage_info = data_manager.get_storage_info()
        assert "storage_type" in storage_info
        assert storage_info["storage_type"] == "file"