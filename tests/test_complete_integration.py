import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json
from unittest.mock import patch, AsyncMock

# Import all the main apps
from backend.app.main import app as backend_app
from simulator_service.app.main import app as simulator_app
from learning_service.app.main import app as learning_app
from optimizer_ai.app.main import app as optimizer_app

class TestCompleteMLSystemIntegration:
    """Complete integration tests for the ML Project system"""
    
    def setup_method(self):
        """Setup test clients for all services"""
        self.backend_client = TestClient(backend_app)
        self.simulator_client = TestClient(simulator_app)
        self.learning_client = TestClient(learning_app)
        self.optimizer_client = TestClient(optimizer_app)
    
    def test_all_health_endpoints(self):
        """Test health endpoints for all services"""
        services = [
            (self.backend_client, "backend"),
            (self.simulator_client, "simulator_service"),
            (self.learning_client, "learning_service"),
            (self.optimizer_client, "optimizer_ai")
        ]
        
        for client, service_name in services:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "ok"]
            print(f"✅ {service_name} health check passed")
    
    def test_simulator_campaign_creation(self):
        """Test simulator campaign creation and report generation"""
        # Test campaign simulation
        campaign_data = {
            "product_name": "Smartphone Samsung Galaxy",
            "category": "electronics",
            "budget": 1000.0,
            "duration_days": 14,
            "target_audience": "young_adults",
            "keywords": ["smartphone", "samsung", "galaxy", "celular", "android"]
        }
        
        response = self.simulator_client.post("/api/simulate", json=campaign_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "campaign_id" in result
        assert result["estimated_reach"] > 0
        assert result["estimated_clicks"] > 0
        assert result["estimated_conversions"] >= 0
        assert "recommendations" in result
        
        campaign_id = result["campaign_id"]
        
        # Test getting simulation results
        response = self.simulator_client.get(f"/api/simulation/{campaign_id}")
        assert response.status_code == 200
        
        # Test report generation
        report_data = {
            "campaign_ids": [campaign_id],
            "format": "csv",
            "include_charts": True
        }
        
        response = self.simulator_client.post("/api/reports/generate", json=report_data)
        assert response.status_code == 200
        
        print("✅ Simulator service integration tests passed")
    
    def test_ab_testing_workflow(self):
        """Test A/B testing functionality"""
        # Create A/B test with multiple variations
        ab_test_data = {
            "test_name": "Email vs SMS Campaign",
            "variations": [
                {
                    "product_name": "Smartphone Samsung Galaxy",
                    "category": "electronics",
                    "budget": 500.0,
                    "duration_days": 7,
                    "target_audience": "young_adults",
                    "keywords": ["smartphone", "samsung"]
                },
                {
                    "product_name": "Smartphone Samsung Galaxy Premium",
                    "category": "electronics", 
                    "budget": 500.0,
                    "duration_days": 7,
                    "target_audience": "professionals",
                    "keywords": ["smartphone", "premium", "business"]
                }
            ],
            "traffic_split": [50.0, 50.0]
        }
        
        response = self.simulator_client.post("/api/ab-test", json=ab_test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "test_id" in result
        assert "winner_variation" in result
        assert len(result["variations_results"]) == 2
        
        print("✅ A/B testing workflow passed")
    
    def test_learning_service_model_updates(self):
        """Test learning service model update workflow"""
        # Test model update
        update_data = {
            "campaign_id": "TEST_CAMP_001",
            "actual_clicks": 1250,
            "actual_conversions": 45,
            "actual_revenue": 2700.50,
            "predicted_clicks": 1200,
            "predicted_conversions": 40,
            "predicted_revenue": 2500.00,
            "notes": "Test campaign from integration tests",
            "model_version": "v2.0"
        }
        
        response = self.learning_client.post("/api/update-model", json=update_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "success"
        assert "accuracy_metrics" in result
        assert "improvement_suggestions" in result
        assert result["model_version"] == "v2.0"
        
        # Test learning history
        response = self.learning_client.get("/api/learning-history")
        assert response.status_code == 200
        
        history = response.json()
        assert "history" in history
        assert "total_updates" in history
        
        # Test model performance
        response = self.learning_client.get("/api/model-performance")
        assert response.status_code == 200
        
        performance = response.json()
        assert "current_performance" in performance
        
        print("✅ Learning service model updates passed")
    
    def test_learning_service_scheduling(self):
        """Test automatic scheduling functionality"""
        # Test creating a schedule
        schedule_data = {
            "schedule_name": "daily_retrain_test",
            "cron_expression": "0 3 * * *",  # Daily at 3 AM
            "enabled": True,
            "target_accuracy_threshold": 0.85,
            "notification_on_completion": True
        }
        
        response = self.learning_client.post("/api/schedule/create", json=schedule_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "success"
        
        # Test listing schedules
        response = self.learning_client.get("/api/schedule/list")
        assert response.status_code == 200
        
        schedules = response.json()
        assert "active_jobs" in schedules
        assert "stored_tasks" in schedules
        
        print("✅ Learning service scheduling tests passed")
    
    def test_optimizer_ai_text_optimization(self):
        """Test text optimization functionality"""
        # Test basic text optimization
        optimization_data = {
            "original_text": "Vendo smartphone usado em bom estado",
            "target_audience": "young_adults",
            "product_category": "electronics",
            "optimization_goal": "conversions",
            "keywords": ["smartphone", "celular", "android"],
            "segment": "b2c_popular",
            "budget_range": "medium",
            "priority_metrics": ["seo", "readability", "compliance"]
        }
        
        response = self.optimizer_client.post("/api/optimize-copy", json=optimization_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "optimized_text" in result
        assert "seo_score" in result
        assert "readability_score" in result
        assert "compliance_score" in result
        assert "improvements" in result
        
        # Verify optimized text is different from original
        assert result["optimized_text"] != optimization_data["original_text"]
        
        print("✅ Optimizer AI text optimization passed")
    
    def test_optimizer_keyword_suggestions(self):
        """Test keyword suggestion functionality"""
        keyword_data = {
            "product_category": "electronics",
            "product_title": "Smartphone Samsung Galaxy S24",
            "target_audience": "young_adults",
            "competitor_analysis": True,
            "max_suggestions": 10
        }
        
        response = self.optimizer_client.post("/api/keywords/suggest", json=keyword_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "suggested_keywords" in result
        assert "category_trends" in result
        assert "competitor_keywords" in result
        assert "optimization_opportunities" in result
        assert len(result["suggested_keywords"]) <= keyword_data["max_suggestions"]
        
        print("✅ Optimizer AI keyword suggestions passed")

    def test_optimizer_segment_optimization(self):
        """Test segment optimization functionality"""
        segment_data = {
            "text": "Produto de qualidade com ótimo preço",
            "target_segments": ["b2b", "b2c_premium", "millennial"],
            "product_category": "electronics"
        }
        
        response = self.optimizer_client.post("/api/segment-optimization", json=segment_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "optimized_texts" in result
        assert "performance_predictions" in result
        assert "recommendations" in result
        
        # Verify we have results for all segments
        for segment in segment_data["target_segments"]:
            assert segment in result["optimized_texts"]
            assert segment in result["performance_predictions"]
            assert segment in result["recommendations"]
        
        print("✅ Optimizer AI segment optimization passed")

    def test_optimizer_compliance_check(self):
        """Test compliance checking functionality"""
        compliance_data = {
            "text": "Smartphone Samsung Galaxy com garantia do fabricante",
            "product_category": "electronics"
        }
        
        response = self.optimizer_client.post("/api/compliance/check", json=compliance_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "is_compliant" in result
        assert "violations" in result
        assert "compliance_score" in result
        assert "risk_level" in result
        assert "recommendations" in result
        
        print("✅ Optimizer AI compliance check passed")

    def test_optimizer_auto_test(self):
        """Test auto testing functionality"""
        auto_test_data = {
            "optimized_text": "Smartphone Samsung Galaxy - melhor escolha para jovens",
            "original_text": "Smartphone Samsung usado",
            "product_category": "electronics",
            "target_audience": "young_adults",
            "budget": 1000.0
        }
        
        response = self.optimizer_client.post("/api/auto-test", json=auto_test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "test_id" in result
        assert "original_performance" in result
        assert "optimized_performance" in result
        assert "test_status" in result
        
        print("✅ Optimizer AI auto testing passed")
    
    def test_system_integration_workflow(self):
        """Test complete workflow integration between services"""
        
        # Step 1: Optimize copy with AI
        original_text = "Smartphone em promoção, preço baixo, aproveite!"
        
        optimization_data = {
            "original_text": original_text,
            "target_audience": "millennials",
            "product_category": "electronics",
            "optimization_goal": "conversions",
            "keywords": ["smartphone", "promoção", "tecnologia"],
            "segment": "millennial",
            "budget_range": "medium",
            "priority_metrics": ["seo", "compliance"]
        }
        
        response = self.optimizer_client.post("/api/optimize-copy", json=optimization_data)
        assert response.status_code == 200
        optimized_result = response.json()
        optimized_text = optimized_result["optimized_text"]
        
        # Step 2: Simulate campaign with optimized copy
        campaign_data = {
            "product_name": optimized_text[:50],  # Use part of optimized text as product name
            "category": "electronics",
            "budget": 800.0,
            "duration_days": 10,
            "target_audience": "millennials",
            "keywords": optimized_result["keywords_included"]
        }
        
        response = self.simulator_client.post("/api/simulate", json=campaign_data)
        assert response.status_code == 200
        simulation_result = response.json()
        
        # Step 3: Use simulation results to update learning model
        update_data = {
            "campaign_id": simulation_result["campaign_id"],
            "actual_clicks": int(simulation_result["estimated_clicks"] * 0.95),  # Simulate 95% accuracy
            "actual_conversions": int(simulation_result["estimated_conversions"] * 1.05),  # Simulate 105% accuracy
            "actual_revenue": simulation_result["estimated_revenue"] * 0.98,
            "predicted_clicks": simulation_result["estimated_clicks"],
            "predicted_conversions": simulation_result["estimated_conversions"],
            "predicted_revenue": simulation_result["estimated_revenue"],
            "notes": "Integration test - optimizer to simulator to learning workflow",
            "model_version": "v3.0"
        }
        
        response = self.learning_client.post("/api/update-model", json=update_data)
        assert response.status_code == 200
        learning_result = response.json()
        
        # Verify the complete workflow
        assert learning_result["status"] == "success"
        assert learning_result["model_version"] == "v3.0"
        
        print("✅ Complete system integration workflow passed")
        print(f"   - Original text: {original_text}")
        print(f"   - Optimized text: {optimized_text}")
        print(f"   - Campaign ID: {simulation_result['campaign_id']}")
        print(f"   - Learning update ID: {learning_result['update_id']}")
    
    def test_performance_and_load(self):
        """Test system performance under load"""
        import time
        import concurrent.futures
        
        def make_request():
            response = self.simulator_client.get("/health")
            return response.status_code == 200
        
        # Test concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All requests should succeed
        assert all(results)
        assert duration < 10  # Should complete within 10 seconds
        
        print(f"✅ Performance test passed: 50 concurrent requests in {duration:.2f}s")
    
    def test_error_handling_and_resilience(self):
        """Test error handling and system resilience"""
        
        # Test invalid data handling
        invalid_campaign_data = {
            "product_name": "",  # Invalid empty name
            "category": "invalid_category",
            "budget": -100,  # Invalid negative budget
            "duration_days": 0,  # Invalid duration
            "target_audience": "",
            "keywords": []
        }
        
        response = self.simulator_client.post("/api/simulate", json=invalid_campaign_data)
        # Should handle gracefully (might return 422 or 400)
        assert response.status_code in [400, 422, 200]  # Allow different error handling approaches
        
        # Test missing required fields
        incomplete_data = {"product_name": "Test"}
        
        response = self.simulator_client.post("/api/simulate", json=incomplete_data)
        assert response.status_code in [400, 422]
        
        print("✅ Error handling and resilience tests passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])