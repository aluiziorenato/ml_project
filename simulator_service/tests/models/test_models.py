"""
Unit tests for Pydantic models in the Simulator Service.
Tests model creation, validation, and serialization for campaign simulation.
"""
import pytest
from pydantic import ValidationError
from typing import List, Dict, Any
import json

# Import models from the main module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import (
    CampaignSimulationRequest,
    CampaignSimulationResponse,
    ABTestRequest,
    ABTestResponse,
    ReportRequest,
    MercadoLibreHistoricalRequest,
    HistoricalData
)


@pytest.mark.models
class TestCampaignSimulationRequest:
    """Test CampaignSimulationRequest model validation and creation."""
    
    def test_create_valid_campaign_request(self):
        """Test creating a valid campaign simulation request."""
        data = {
            "product_name": "Smartphone Samsung Galaxy",
            "category": "electronics",
            "budget": 1500.50,
            "duration_days": 30,
            "target_audience": "tech_enthusiasts",
            "keywords": ["smartphone", "samsung", "galaxy", "android"]
        }
        
        request = CampaignSimulationRequest(**data)
        
        assert request.product_name == "Smartphone Samsung Galaxy"
        assert request.category == "electronics"
        assert request.budget == 1500.50
        assert request.duration_days == 30
        assert request.target_audience == "tech_enthusiasts"
        assert request.keywords == ["smartphone", "samsung", "galaxy", "android"]
    
    def test_create_minimal_campaign_request(self):
        """Test creating a request with only required fields."""
        data = {
            "product_name": "Basic Product",
            "category": "home",
            "budget": 500.0,
            "duration_days": 7,
            "target_audience": "general",
            "keywords": []
        }
        
        request = CampaignSimulationRequest(**data)
        
        assert request.product_name == "Basic Product"
        assert request.category == "home"
        assert request.budget == 500.0
        assert request.duration_days == 7
        assert request.target_audience == "general"
        assert request.keywords == []
    
    def test_campaign_request_serialization(self):
        """Test JSON serialization of campaign request."""
        data = {
            "product_name": "Test Product for Serialization",
            "category": "clothing",
            "budget": 750.25,
            "duration_days": 14,
            "target_audience": "fashion_lovers",
            "keywords": ["fashion", "style", "trendy"]
        }
        
        request = CampaignSimulationRequest(**data)
        json_str = request.model_dump_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["product_name"] == "Test Product for Serialization"
        assert parsed["budget"] == 750.25
        assert parsed["keywords"] == ["fashion", "style", "trendy"]
    
    def test_campaign_request_with_large_budget(self):
        """Test campaign request with large budget."""
        data = {
            "product_name": "Premium Product",
            "category": "electronics",
            "budget": 50000.0,
            "duration_days": 90,
            "target_audience": "enterprise",
            "keywords": ["premium", "enterprise", "professional"]
        }
        
        request = CampaignSimulationRequest(**data)
        
        assert request.budget == 50000.0
        assert request.duration_days == 90
    
    def test_campaign_request_with_many_keywords(self):
        """Test campaign request with many keywords."""
        keywords = [f"keyword_{i}" for i in range(20)]
        
        data = {
            "product_name": "Keyword Heavy Product",
            "category": "books",
            "budget": 1000.0,
            "duration_days": 21,
            "target_audience": "students",
            "keywords": keywords
        }
        
        request = CampaignSimulationRequest(**data)
        
        assert len(request.keywords) == 20
        assert request.keywords[0] == "keyword_0"
        assert request.keywords[-1] == "keyword_19"


@pytest.mark.models
class TestCampaignSimulationResponse:
    """Test CampaignSimulationResponse model validation and creation."""
    
    def test_create_valid_campaign_response(self):
        """Test creating a valid campaign simulation response."""
        data = {
            "campaign_id": "CAMP_123456",
            "estimated_reach": 25000,
            "estimated_clicks": 1250,
            "estimated_conversions": 62,
            "estimated_revenue": 15500.75,
            "cost_per_click": 1.85,
            "roi_percentage": 125.5,
            "recommendations": [
                "Consider extending campaign duration",
                "Add more relevant keywords",
                "Optimize for mobile audience"
            ]
        }
        
        response = CampaignSimulationResponse(**data)
        
        assert response.campaign_id == "CAMP_123456"
        assert response.estimated_reach == 25000
        assert response.estimated_clicks == 1250
        assert response.estimated_conversions == 62
        assert response.estimated_revenue == 15500.75
        assert response.cost_per_click == 1.85
        assert response.roi_percentage == 125.5
        assert len(response.recommendations) == 3
    
    def test_campaign_response_with_zero_values(self):
        """Test campaign response with zero/low values."""
        data = {
            "campaign_id": "CAMP_LOW_PERF",
            "estimated_reach": 100,
            "estimated_clicks": 5,
            "estimated_conversions": 0,
            "estimated_revenue": 0.0,
            "cost_per_click": 20.0,
            "roi_percentage": -100.0,
            "recommendations": ["Increase budget", "Improve targeting"]
        }
        
        response = CampaignSimulationResponse(**data)
        
        assert response.estimated_conversions == 0
        assert response.estimated_revenue == 0.0
        assert response.roi_percentage == -100.0  # Negative ROI is valid
    
    def test_campaign_response_serialization(self):
        """Test JSON serialization of campaign response."""
        data = {
            "campaign_id": "CAMP_SERIALIZE",
            "estimated_reach": 10000,
            "estimated_clicks": 500,
            "estimated_conversions": 25,
            "estimated_revenue": 2500.0,
            "cost_per_click": 2.0,
            "roi_percentage": 50.0,
            "recommendations": ["Monitor performance closely"]
        }
        
        response = CampaignSimulationResponse(**data)
        json_str = response.model_dump_json()
        
        parsed = json.loads(json_str)
        assert parsed["campaign_id"] == "CAMP_SERIALIZE"
        assert parsed["estimated_reach"] == 10000
        assert parsed["cost_per_click"] == 2.0
        assert len(parsed["recommendations"]) == 1
    
    def test_campaign_response_high_performance(self):
        """Test campaign response with high performance metrics."""
        data = {
            "campaign_id": "CAMP_HIGH_PERF",
            "estimated_reach": 100000,
            "estimated_clicks": 10000,
            "estimated_conversions": 1000,
            "estimated_revenue": 100000.0,
            "cost_per_click": 0.50,
            "roi_percentage": 500.0,
            "recommendations": ["Scale up campaign", "Expand to new markets"]
        }
        
        response = CampaignSimulationResponse(**data)
        
        assert response.estimated_reach == 100000
        assert response.roi_percentage == 500.0
        assert response.cost_per_click == 0.50


@pytest.mark.models
class TestABTestModels:
    """Test A/B testing related models."""
    
    def test_ab_test_request_creation(self):
        """Test creating A/B test request."""
        variation_a = CampaignSimulationRequest(
            product_name="Product A",
            category="electronics",
            budget=1000.0,
            duration_days=30,
            target_audience="professionals",
            keywords=["professional", "business"]
        )
        
        variation_b = CampaignSimulationRequest(
            product_name="Product B",
            category="electronics", 
            budget=1000.0,
            duration_days=30,
            target_audience="students",
            keywords=["student", "affordable"]
        )
        
        ab_test_data = {
            "test_name": "Professional vs Student Targeting",
            "variations": [variation_a, variation_b],
            "traffic_split": [60.0, 40.0]
        }
        
        ab_test = ABTestRequest(**ab_test_data)
        
        assert ab_test.test_name == "Professional vs Student Targeting"
        assert len(ab_test.variations) == 2
        assert ab_test.traffic_split == [60.0, 40.0]
        assert ab_test.variations[0].target_audience == "professionals"
        assert ab_test.variations[1].target_audience == "students"
    
    def test_ab_test_request_equal_split(self):
        """Test A/B test with equal traffic split."""
        variation_a = CampaignSimulationRequest(
            product_name="Original",
            category="clothing",
            budget=800.0,
            duration_days=21,
            target_audience="general",
            keywords=["clothing", "fashion"]
        )
        
        variation_b = CampaignSimulationRequest(
            product_name="Optimized",
            category="clothing",
            budget=800.0, 
            duration_days=21,
            target_audience="general",
            keywords=["style", "trendy", "modern"]
        )
        
        ab_test = ABTestRequest(
            test_name="Keyword Optimization Test",
            variations=[variation_a, variation_b],
            traffic_split=[50.0, 50.0]
        )
        
        assert sum(ab_test.traffic_split) == 100.0
        assert len(ab_test.variations) == 2
    
    def test_ab_test_response_creation(self):
        """Test creating A/B test response."""
        var_a_response = CampaignSimulationResponse(
            campaign_id="VAR_A_001",
            estimated_reach=15000,
            estimated_clicks=750,
            estimated_conversions=37,
            estimated_revenue=9250.0,
            cost_per_click=1.60,
            roi_percentage=85.5,
            recommendations=["Good performance for variation A"]
        )
        
        var_b_response = CampaignSimulationResponse(
            campaign_id="VAR_B_001",
            estimated_reach=14000,
            estimated_clicks=850,
            estimated_conversions=45,
            estimated_revenue=11250.0,
            cost_per_click=1.41,
            roi_percentage=95.2,
            recommendations=["Variation B shows higher performance"]
        )
        
        ab_response_data = {
            "test_id": "ABT_789012",
            "status": "completed",
            "variations_results": [var_a_response, var_b_response],
            "winner_variation": 1,
            "confidence_level": 92.5,
            "estimated_lift": 11.4
        }
        
        ab_response = ABTestResponse(**ab_response_data)
        
        assert ab_response.test_id == "ABT_789012"
        assert ab_response.status == "completed"
        assert len(ab_response.variations_results) == 2
        assert ab_response.winner_variation == 1
        assert ab_response.confidence_level == 92.5
        assert ab_response.estimated_lift == 11.4
    
    def test_ab_test_multiple_variations(self):
        """Test A/B test with multiple variations (A/B/C test)."""
        variations = []
        traffic_splits = [30.0, 35.0, 35.0]
        
        for i, audience in enumerate(["professionals", "students", "families"]):
            variation = CampaignSimulationRequest(
                product_name=f"Product for {audience}",
                category="home",
                budget=1200.0,
                duration_days=28,
                target_audience=audience,
                keywords=[audience.lower(), "home", "quality"]
            )
            variations.append(variation)
        
        abc_test = ABTestRequest(
            test_name="Multi-Audience Test",
            variations=variations,
            traffic_split=traffic_splits
        )
        
        assert len(abc_test.variations) == 3
        assert sum(abc_test.traffic_split) == 100.0
        assert abc_test.variations[0].target_audience == "professionals"
        assert abc_test.variations[1].target_audience == "students"
        assert abc_test.variations[2].target_audience == "families"


@pytest.mark.models
class TestReportModels:
    """Test report generation related models."""
    
    def test_report_request_creation(self):
        """Test creating report request."""
        data = {
            "campaign_ids": ["CAMP_001", "CAMP_002", "CAMP_003"],
            "format": "pdf",
            "include_charts": True
        }
        
        report_request = ReportRequest(**data)
        
        assert len(report_request.campaign_ids) == 3
        assert report_request.format == "pdf"
        assert report_request.include_charts == True
    
    def test_report_request_csv_format(self):
        """Test report request with CSV format."""
        data = {
            "campaign_ids": ["CAMP_CSV_01", "CAMP_CSV_02"],
            "format": "csv",
            "include_charts": False
        }
        
        report_request = ReportRequest(**data)
        
        assert report_request.format == "csv"
        assert report_request.include_charts == False
    
    def test_report_request_defaults(self):
        """Test report request with default values."""
        data = {
            "campaign_ids": ["CAMP_DEFAULT"]
        }
        
        report_request = ReportRequest(**data)
        
        assert report_request.format == "pdf"  # Default format
        assert report_request.include_charts == True  # Default value
    
    def test_report_request_excel_format(self):
        """Test report request with Excel format."""
        data = {
            "campaign_ids": ["CAMP_EXCEL"],
            "format": "excel",
            "include_charts": True
        }
        
        report_request = ReportRequest(**data)
        
        assert report_request.format == "excel"
        assert report_request.include_charts == True
    
    def test_mercadolibre_historical_request(self):
        """Test MercadoLibre historical data request."""
        data = {
            "category_id": "MLB1051",
            "period_days": 45
        }
        
        historical_request = MercadoLibreHistoricalRequest(**data)
        
        assert historical_request.category_id == "MLB1051"
        assert historical_request.period_days == 45
    
    def test_mercadolibre_historical_request_defaults(self):
        """Test historical request with default period."""
        data = {
            "category_id": "MLB1430"
        }
        
        historical_request = MercadoLibreHistoricalRequest(**data)
        
        assert historical_request.category_id == "MLB1430"
        assert historical_request.period_days == 30  # Default value


@pytest.mark.models
class TestHistoricalDataModel:
    """Test HistoricalData model validation."""
    
    def test_historical_data_creation(self):
        """Test creating historical data model."""
        data = {
            "date": "2024-01-15",
            "impressions": 5000,
            "clicks": 250,
            "conversions": 12,
            "spend": 500.50,
            "category": "MLB1051"
        }
        
        historical_data = HistoricalData(**data)
        
        assert historical_data.date == "2024-01-15"
        assert historical_data.impressions == 5000
        assert historical_data.clicks == 250
        assert historical_data.conversions == 12
        assert historical_data.spend == 500.50
        assert historical_data.category == "MLB1051"
    
    def test_historical_data_zero_values(self):
        """Test historical data with zero values."""
        data = {
            "date": "2024-01-01",
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spend": 0.0,
            "category": "MLB1574"
        }
        
        historical_data = HistoricalData(**data)
        
        assert historical_data.impressions == 0
        assert historical_data.clicks == 0
        assert historical_data.conversions == 0
        assert historical_data.spend == 0.0
    
    def test_historical_data_high_values(self):
        """Test historical data with high performance values."""
        data = {
            "date": "2024-02-01",
            "impressions": 100000,
            "clicks": 8500,
            "conversions": 425,
            "spend": 17000.0,
            "category": "MLB1276"
        }
        
        historical_data = HistoricalData(**data)
        
        assert historical_data.impressions == 100000
        assert historical_data.clicks == 8500
        assert historical_data.conversions == 425
        assert historical_data.spend == 17000.0
    
    def test_historical_data_serialization(self):
        """Test historical data JSON serialization."""
        data = {
            "date": "2024-03-10",
            "impressions": 12500,
            "clicks": 625,
            "conversions": 31,
            "spend": 1250.25,
            "category": "MLB1196"
        }
        
        historical_data = HistoricalData(**data)
        json_str = historical_data.model_dump_json()
        
        parsed = json.loads(json_str)
        assert parsed["date"] == "2024-03-10"
        assert parsed["impressions"] == 12500
        assert parsed["spend"] == 1250.25
        assert parsed["category"] == "MLB1196"


@pytest.mark.errors
@pytest.mark.models
class TestModelValidationErrors:
    """Test model validation error scenarios."""
    
    def test_campaign_request_missing_required_fields(self):
        """Test creating request with missing required fields."""
        data = {
            "product_name": "Incomplete Product"
            # Missing required fields like category, budget, etc.
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CampaignSimulationRequest(**data)
        
        error = exc_info.value
        assert len(error.errors()) > 0
    
    def test_campaign_request_invalid_budget_type(self):
        """Test campaign request with invalid budget type."""
        data = {
            "product_name": "Test Product",
            "category": "electronics",
            "budget": "not_a_number",  # Should be float
            "duration_days": 30,
            "target_audience": "general",
            "keywords": []
        }
        
        with pytest.raises(ValidationError):
            CampaignSimulationRequest(**data)
    
    def test_campaign_request_negative_budget(self):
        """Test campaign request with negative budget."""
        data = {
            "product_name": "Test Product",
            "category": "electronics", 
            "budget": -100.0,  # Negative budget
            "duration_days": 30,
            "target_audience": "general",
            "keywords": []
        }
        
        # Model might accept negative values, business logic should validate
        request = CampaignSimulationRequest(**data)
        assert request.budget == -100.0
    
    def test_campaign_request_zero_duration(self):
        """Test campaign request with zero duration."""
        data = {
            "product_name": "Test Product",
            "category": "electronics",
            "budget": 1000.0,
            "duration_days": 0,  # Zero duration
            "target_audience": "general",
            "keywords": []
        }
        
        # Model might accept zero, business logic should validate
        request = CampaignSimulationRequest(**data)
        assert request.duration_days == 0
    
    def test_ab_test_request_mismatched_splits(self):
        """Test A/B test with mismatched variations and splits."""
        variation = CampaignSimulationRequest(
            product_name="Single Variation",
            category="electronics",
            budget=1000.0,
            duration_days=30,
            target_audience="general",
            keywords=[]
        )
        
        data = {
            "test_name": "Mismatched Test",
            "variations": [variation],  # 1 variation
            "traffic_split": [60.0, 40.0]  # 2 splits
        }
        
        # Model should accept this, business logic should validate
        ab_test = ABTestRequest(**data)
        assert len(ab_test.variations) == 1
        assert len(ab_test.traffic_split) == 2
    
    def test_historical_data_invalid_date_format(self):
        """Test historical data with invalid date format."""
        data = {
            "date": "invalid-date-format",
            "impressions": 1000,
            "clicks": 50,
            "conversions": 5,
            "spend": 100.0,
            "category": "MLB1051"
        }
        
        # Model accepts string dates, business logic should validate format
        historical_data = HistoricalData(**data)
        assert historical_data.date == "invalid-date-format"
    
    def test_report_request_empty_campaign_list(self):
        """Test report request with empty campaign list."""
        data = {
            "campaign_ids": [],  # Empty list
            "format": "pdf",
            "include_charts": True
        }
        
        report_request = ReportRequest(**data)
        assert len(report_request.campaign_ids) == 0


@pytest.mark.models 
class TestModelDefaults:
    """Test model default values."""
    
    def test_report_request_defaults(self):
        """Test all default values in report request."""
        data = {
            "campaign_ids": ["TEST_001"]
        }
        
        request = ReportRequest(**data)
        
        assert request.format == "pdf"
        assert request.include_charts == True
    
    def test_mercadolibre_historical_request_defaults(self):
        """Test default values in historical request."""
        data = {
            "category_id": "MLB1051"
        }
        
        request = MercadoLibreHistoricalRequest(**data)
        
        assert request.period_days == 30


@pytest.mark.models
class TestModelComplexScenarios:
    """Test complex model interaction scenarios."""
    
    def test_full_ab_test_workflow(self):
        """Test complete A/B test workflow with all models."""
        # Create variations
        variation_a = CampaignSimulationRequest(
            product_name="Original Campaign",
            category="electronics",
            budget=2000.0,
            duration_days=30,
            target_audience="tech_enthusiasts",
            keywords=["smartphone", "tech", "innovation"]
        )
        
        variation_b = CampaignSimulationRequest(
            product_name="Optimized Campaign",
            category="electronics",
            budget=2000.0,
            duration_days=30,
            target_audience="tech_enthusiasts", 
            keywords=["mobile", "device", "cutting-edge", "premium"]
        )
        
        # Create A/B test request
        ab_request = ABTestRequest(
            test_name="Keyword Optimization A/B Test",
            variations=[variation_a, variation_b],
            traffic_split=[50.0, 50.0]
        )
        
        # Create response results
        result_a = CampaignSimulationResponse(
            campaign_id="VAR_A_ORIGINAL",
            estimated_reach=20000,
            estimated_clicks=1000,
            estimated_conversions=50,
            estimated_revenue=12500.0,
            cost_per_click=2.0,
            roi_percentage=62.5,
            recommendations=["Original performing well"]
        )
        
        result_b = CampaignSimulationResponse(
            campaign_id="VAR_B_OPTIMIZED",
            estimated_reach=22000,
            estimated_clicks=1200,
            estimated_conversions=65,
            estimated_revenue=16250.0,
            cost_per_click=1.67,
            roi_percentage=81.25,
            recommendations=["Optimized version shows improvement"]
        )
        
        # Create A/B test response
        ab_response = ABTestResponse(
            test_id="ABT_KEYWORD_OPT",
            status="completed",
            variations_results=[result_a, result_b],
            winner_variation=1,
            confidence_level=88.5,
            estimated_lift=30.0
        )
        
        # Verify the complete workflow
        assert ab_request.test_name == "Keyword Optimization A/B Test"
        assert len(ab_request.variations) == 2
        assert ab_response.winner_variation == 1
        assert ab_response.estimated_lift == 30.0
        assert len(ab_response.variations_results) == 2
    
    def test_report_generation_scenario(self):
        """Test report generation with multiple campaigns."""
        campaign_ids = ["CAMP_001", "CAMP_002", "CAMP_003"]
        
        # PDF report request
        pdf_request = ReportRequest(
            campaign_ids=campaign_ids,
            format="pdf",
            include_charts=True
        )
        
        # CSV report request
        csv_request = ReportRequest(
            campaign_ids=campaign_ids,
            format="csv",
            include_charts=False
        )
        
        # Excel report request
        excel_request = ReportRequest(
            campaign_ids=campaign_ids,
            format="excel",
            include_charts=True
        )
        
        assert pdf_request.format == "pdf"
        assert pdf_request.include_charts == True
        assert csv_request.format == "csv"
        assert csv_request.include_charts == False
        assert excel_request.format == "excel"
        
        # All should have same campaign IDs
        assert pdf_request.campaign_ids == csv_request.campaign_ids == excel_request.campaign_ids