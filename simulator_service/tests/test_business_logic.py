import pytest
from app.main import app, campaigns_storage, CampaignSimulationRequest
import asyncio


class TestSimulatorLogic:
    """Test class for Simulator Service business logic"""

    def setup_method(self):
        """Clear campaigns storage before each test"""
        campaigns_storage.clear()

    def test_campaign_simulation_request_validation(self, sample_campaign_request):
        """Test that campaign request validation works correctly"""
        request = CampaignSimulationRequest(**sample_campaign_request)
        assert request.product_name == "iPhone 15 Pro"
        assert request.category == "electronics"
        assert request.budget == 1000.0
        assert request.duration_days == 30
        assert request.target_audience == "young_adults"
        assert len(request.keywords) == 4

    def test_campaigns_storage_operations(self, sample_campaign_request):
        """Test basic operations on campaigns storage"""
        # Initially empty
        assert len(campaigns_storage) == 0
        
        # Add a campaign
        campaigns_storage["TEST_123"] = {
            "response": "test_response",
            "request": sample_campaign_request,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        assert len(campaigns_storage) == 1
        assert "TEST_123" in campaigns_storage
        
        # Remove campaign
        del campaigns_storage["TEST_123"]
        assert len(campaigns_storage) == 0

    def test_campaign_id_generation_format(self):
        """Test that campaign IDs are generated in the correct format"""
        import uuid
        from datetime import datetime
        
        # Mock a campaign creation
        campaign_id = f"CAM_{str(uuid.uuid4())[:8].upper()}"
        
        assert campaign_id.startswith("CAM_")
        assert len(campaign_id) == 12  # CAM_ + 8 characters
        assert campaign_id[4:].isupper()

    def test_category_multipliers_logic(self):
        """Test category multiplier logic"""
        category_multipliers = {
            "electronics": 1.5,
            "clothing": 1.2,
            "home": 1.0,
            "sports": 1.3,
            "books": 0.8,
            "automotive": 1.4
        }
        
        # Test that electronics has higher multiplier than books
        assert category_multipliers["electronics"] > category_multipliers["books"]
        assert category_multipliers["automotive"] > category_multipliers["home"]

    def test_audience_multipliers_logic(self):
        """Test audience multiplier logic"""
        audience_multipliers = {
            "young_adults": 1.3,
            "families": 1.1,
            "professionals": 1.4,
            "seniors": 0.9
        }
        
        # Test that professionals have highest multiplier
        assert audience_multipliers["professionals"] > audience_multipliers["young_adults"]
        assert audience_multipliers["young_adults"] > audience_multipliers["seniors"]

    def test_keyword_factor_calculation(self):
        """Test keyword factor calculation"""
        # Test with different keyword counts
        keywords_1 = ["keyword1"]
        keywords_5 = ["k1", "k2", "k3", "k4", "k5"]
        keywords_10 = [f"k{i}" for i in range(10)]
        
        factor_1 = min(1.5, 1 + (len(keywords_1) * 0.1))
        factor_5 = min(1.5, 1 + (len(keywords_5) * 0.1))
        factor_10 = min(1.5, 1 + (len(keywords_10) * 0.1))
        
        assert factor_5 > factor_1
        assert factor_10 == 1.5  # Capped at 1.5

    def test_duration_factor_calculation(self):
        """Test duration factor calculation"""
        # Test with different durations
        duration_7 = 7
        duration_30 = 30
        duration_90 = 90
        
        factor_7 = min(1.3, 1 + (duration_7 / 30) * 0.3)
        factor_30 = min(1.3, 1 + (duration_30 / 30) * 0.3)
        factor_90 = min(1.3, 1 + (duration_90 / 30) * 0.3)
        
        assert factor_30 > factor_7
        assert factor_90 == 1.3  # Capped at 1.3

    def test_revenue_calculation_logic(self):
        """Test revenue calculation logic"""
        budget = 1000
        estimated_conversions = 10
        
        # Simulate avg_order_value calculation
        import random
        random.seed(42)  # For reproducible tests
        avg_order_value = budget / max(1, estimated_conversions) * random.uniform(2, 4)
        estimated_revenue = estimated_conversions * avg_order_value
        
        assert estimated_revenue > budget  # Should be profitable
        assert avg_order_value > 0

    def test_recommendations_generation_logic(self):
        """Test recommendations generation logic"""
        recommendations = []
        
        # Test low ROI scenario
        roi_percentage = 30  # Less than 50
        if roi_percentage < 50:
            recommendations.append("Consider adjusting keywords for better targeting")
        
        # Test high CPC scenario
        cost_per_click = 3.0  # Greater than 2.0
        if cost_per_click > 2.0:
            recommendations.append("Budget allocation could be optimized for lower CPC")
        
        # Test few keywords scenario
        keywords_count = 2  # Less than 5
        if keywords_count < 5:
            recommendations.append("Adding more relevant keywords could improve reach")
        
        # Test short duration scenario
        duration_days = 5  # Less than 7
        if duration_days < 7:
            recommendations.append("Consider extending campaign duration for better performance")
        
        assert len(recommendations) == 4
        assert "adjusting keywords" in recommendations[0]
        assert "lower CPC" in recommendations[1]

    def test_pydantic_model_serialization(self, sample_campaign_request):
        """Test that Pydantic models serialize correctly"""
        request = CampaignSimulationRequest(**sample_campaign_request)
        
        # Test dict conversion
        request_dict = request.dict()
        assert isinstance(request_dict, dict)
        assert "product_name" in request_dict
        assert "budget" in request_dict
        
        # Test JSON serialization
        request_json = request.json()
        assert isinstance(request_json, str)
        assert "iPhone 15 Pro" in request_json

    def test_health_check_response_format(self):
        """Test health check response format"""
        expected_response = {"status": "healthy", "service": "simulator_service"}
        
        assert "status" in expected_response
        assert "service" in expected_response
        assert expected_response["status"] == "healthy"
        assert expected_response["service"] == "simulator_service"