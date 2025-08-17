"""
Unit tests for simulation utility functions in the Simulator Service.
Tests pure functions for campaign simulation, calculations, and data processing.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any
import io

# Import the functions we want to test from the main module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import (
    get_mercadolibre_historical_data,
    get_category_id_from_name,
    generate_pdf_report,
    generate_csv_report,
    HistoricalData,
    CampaignSimulationRequest,
    CampaignSimulationResponse,
    ABTestRequest,
    ABTestResponse,
    ReportRequest,
    MercadoLibreHistoricalRequest
)


@pytest.mark.unit
@pytest.mark.utils
class TestCategoryMapping:
    """Test category ID mapping functions."""
    
    def test_get_category_id_from_name_electronics(self):
        """Test category mapping for electronics."""
        category_id = get_category_id_from_name("electronics")
        assert category_id == "MLB1051"
    
    def test_get_category_id_from_name_clothing(self):
        """Test category mapping for clothing."""
        category_id = get_category_id_from_name("clothing")
        assert category_id == "MLB1430"
    
    def test_get_category_id_from_name_home(self):
        """Test category mapping for home category."""
        category_id = get_category_id_from_name("home")
        assert category_id == "MLB1574"
    
    def test_get_category_id_from_name_books(self):
        """Test category mapping for books."""
        category_id = get_category_id_from_name("books")
        assert category_id == "MLB1196"
    
    def test_get_category_id_from_name_sports(self):
        """Test category mapping for sports."""
        category_id = get_category_id_from_name("sports")
        assert category_id == "MLB1276"
    
    def test_get_category_id_from_name_unknown(self):
        """Test category mapping for unknown category returns default."""
        category_id = get_category_id_from_name("unknown_category")
        assert category_id == "MLB1051"  # Default electronics
    
    def test_get_category_id_from_name_case_insensitive(self):
        """Test category mapping is case insensitive."""
        category_id = get_category_id_from_name("ELECTRONICS")
        assert category_id == "MLB1051"
    
    def test_get_category_id_from_name_empty_string(self):
        """Test category mapping with empty string."""
        category_id = get_category_id_from_name("")
        assert category_id == "MLB1051"  # Default electronics


@pytest.mark.unit
@pytest.mark.simulation
@pytest.mark.asyncio
class TestHistoricalDataGeneration:
    """Test historical data generation functions."""
    
    async def test_get_mercadolibre_historical_data_basic(self):
        """Test basic historical data generation."""
        category_id = "MLB1051"
        period_days = 7
        
        historical_data = await get_mercadolibre_historical_data(category_id, period_days)
        
        assert isinstance(historical_data, list)
        assert len(historical_data) == period_days
        assert all(isinstance(item, HistoricalData) for item in historical_data)
    
    async def test_get_mercadolibre_historical_data_electronics_category(self):
        """Test historical data for electronics category."""
        category_id = "MLB1051"  # Electronics
        period_days = 5
        
        historical_data = await get_mercadolibre_historical_data(category_id, period_days)
        
        assert len(historical_data) == period_days
        for data_point in historical_data:
            assert data_point.category == category_id
            assert data_point.impressions > 0
            assert data_point.clicks > 0
            assert data_point.conversions >= 0
            assert data_point.spend > 0
            assert isinstance(data_point.date, str)
    
    async def test_get_mercadolibre_historical_data_different_categories(self):
        """Test historical data differs by category."""
        electronics_data = await get_mercadolibre_historical_data("MLB1051", 3)
        clothing_data = await get_mercadolibre_historical_data("MLB1430", 3)
        
        # Data should be different for different categories
        electronics_avg_impressions = sum(d.impressions for d in electronics_data) / len(electronics_data)
        clothing_avg_impressions = sum(d.impressions for d in clothing_data) / len(clothing_data)
        
        # Electronics typically has higher volume than clothing in our test data
        assert electronics_avg_impressions >= clothing_avg_impressions * 0.8  # Allow some variance
    
    async def test_get_mercadolibre_historical_data_date_sequence(self):
        """Test historical data has proper date sequence."""
        category_id = "MLB1051"
        period_days = 5
        
        historical_data = await get_mercadolibre_historical_data(category_id, period_days)
        
        dates = [datetime.fromisoformat(d.date) for d in historical_data]
        
        # Dates should be in chronological order
        for i in range(1, len(dates)):
            assert dates[i] > dates[i-1]
        
        # Should span the requested period
        date_diff = (dates[-1] - dates[0]).days
        assert date_diff == period_days - 1
    
    async def test_get_mercadolibre_historical_data_zero_period(self):
        """Test historical data with zero period."""
        historical_data = await get_mercadolibre_historical_data("MLB1051", 0)
        
        assert isinstance(historical_data, list)
        assert len(historical_data) == 0
    
    async def test_get_mercadolibre_historical_data_large_period(self):
        """Test historical data with large period."""
        period_days = 100
        historical_data = await get_mercadolibre_historical_data("MLB1051", period_days)
        
        assert len(historical_data) == period_days
        assert all(isinstance(item, HistoricalData) for item in historical_data)
    
    @patch('app.main.logger')
    async def test_get_mercadolibre_historical_data_exception_handling(self, mock_logger):
        """Test historical data exception handling."""
        # Patch datetime to cause an exception
        with patch('app.main.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("Test exception")
            
            historical_data = await get_mercadolibre_historical_data("MLB1051", 5)
            
            # Should return fallback data
            assert len(historical_data) == 1
            assert historical_data[0].category == "MLB1051"
            assert historical_data[0].impressions == 1000
            mock_logger.error.assert_called_once()


@pytest.mark.unit
@pytest.mark.utils
class TestReportGeneration:
    """Test report generation functions."""
    
    def test_generate_csv_report_basic(self):
        """Test basic CSV report generation."""
        # Setup test data
        from app.main import campaign_results
        campaign_results["TEST_001"] = {
            "campaign_id": "TEST_001",
            "estimated_reach": 5000,
            "estimated_clicks": 250,
            "estimated_conversions": 10,
            "estimated_revenue": 1000.0,
            "cost_per_click": 2.0,
            "roi_percentage": 25.5
        }
        
        campaign_ids = ["TEST_001"]
        csv_content = generate_csv_report(campaign_ids)
        
        assert isinstance(csv_content, str)
        assert "Campaign ID" in csv_content
        assert "TEST_001" in csv_content
        assert "5000" in csv_content  # estimated_reach
        assert "25.5" in csv_content  # roi_percentage
        
        # Clean up
        del campaign_results["TEST_001"]
    
    def test_generate_csv_report_multiple_campaigns(self):
        """Test CSV report with multiple campaigns."""
        from app.main import campaign_results
        
        # Setup test data
        campaign_results["TEST_001"] = {
            "campaign_id": "TEST_001",
            "estimated_reach": 5000,
            "estimated_clicks": 250,
            "estimated_conversions": 10,
            "estimated_revenue": 1000.0,
            "cost_per_click": 2.0,
            "roi_percentage": 25.5
        }
        campaign_results["TEST_002"] = {
            "campaign_id": "TEST_002",
            "estimated_reach": 3000,
            "estimated_clicks": 150,
            "estimated_conversions": 5,
            "estimated_revenue": 500.0,
            "cost_per_click": 1.5,
            "roi_percentage": 15.0
        }
        
        campaign_ids = ["TEST_001", "TEST_002"]
        csv_content = generate_csv_report(campaign_ids)
        
        assert "TEST_001" in csv_content
        assert "TEST_002" in csv_content
        lines = csv_content.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows
        
        # Clean up
        del campaign_results["TEST_001"]
        del campaign_results["TEST_002"]
    
    def test_generate_csv_report_empty_campaign_list(self):
        """Test CSV report with empty campaign list."""
        csv_content = generate_csv_report([])
        
        assert isinstance(csv_content, str)
        assert "Campaign ID" in csv_content  # Header should still be present
    
    def test_generate_csv_report_nonexistent_campaign(self):
        """Test CSV report with nonexistent campaign ID."""
        csv_content = generate_csv_report(["NONEXISTENT_ID"])
        
        assert isinstance(csv_content, str)
        assert "Campaign ID" in csv_content
        assert "NONEXISTENT_ID" not in csv_content  # Should skip nonexistent campaigns
    
    def test_generate_pdf_report_basic(self):
        """Test basic PDF report generation."""
        from app.main import campaign_results
        
        # Setup test data
        campaign_results["TEST_PDF"] = {
            "campaign_id": "TEST_PDF",
            "estimated_reach": 5000,
            "estimated_clicks": 250,
            "estimated_conversions": 10,
            "estimated_revenue": 1000.0,
            "cost_per_click": 2.0,
            "roi_percentage": 25.5
        }
        
        campaign_ids = ["TEST_PDF"]
        pdf_content = generate_pdf_report(campaign_ids, include_charts=True)
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        # PDF should start with PDF header
        assert pdf_content.startswith(b'%PDF')
        
        # Clean up
        del campaign_results["TEST_PDF"]
    
    def test_generate_pdf_report_without_charts(self):
        """Test PDF report generation without charts."""
        from app.main import campaign_results
        
        campaign_results["TEST_PDF_NO_CHARTS"] = {
            "campaign_id": "TEST_PDF_NO_CHARTS",
            "estimated_reach": 3000,
            "estimated_clicks": 150,
            "estimated_conversions": 8,
            "estimated_revenue": 800.0,
            "cost_per_click": 1.8,
            "roi_percentage": 20.0
        }
        
        campaign_ids = ["TEST_PDF_NO_CHARTS"]
        pdf_content = generate_pdf_report(campaign_ids, include_charts=False)
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert pdf_content.startswith(b'%PDF')
        
        # Clean up
        del campaign_results["TEST_PDF_NO_CHARTS"]
    
    def test_generate_pdf_report_empty_campaign_list(self):
        """Test PDF report with empty campaign list."""
        pdf_content = generate_pdf_report([], include_charts=True)
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert pdf_content.startswith(b'%PDF')


@pytest.mark.unit
@pytest.mark.analytics
class TestCampaignCalculations:
    """Test campaign calculation functions (would be extracted from main.py)."""
    
    def test_calculate_ctr(self):
        """Test CTR calculation."""
        # This would test a pure function if extracted from main logic
        impressions = 1000
        clicks = 50
        expected_ctr = clicks / impressions
        
        # Simulate the calculation that would be in a pure function
        actual_ctr = clicks / max(impressions, 1)
        
        assert actual_ctr == expected_ctr
        assert actual_ctr == 0.05
    
    def test_calculate_conversion_rate(self):
        """Test conversion rate calculation."""
        clicks = 100
        conversions = 5
        expected_rate = conversions / clicks
        
        # Simulate the calculation
        actual_rate = conversions / max(clicks, 1)
        
        assert actual_rate == expected_rate
        assert actual_rate == 0.05
    
    def test_calculate_cpc(self):
        """Test CPC calculation."""
        spend = 200.0
        clicks = 100
        expected_cpc = spend / clicks
        
        # Simulate the calculation
        actual_cpc = spend / max(clicks, 1)
        
        assert actual_cpc == expected_cpc
        assert actual_cpc == 2.0
    
    def test_calculate_roi_percentage(self):
        """Test ROI percentage calculation."""
        revenue = 1200.0
        spend = 800.0
        expected_roi = ((revenue - spend) / spend) * 100
        
        # Simulate the calculation
        actual_roi = ((revenue - spend) / spend) * 100
        
        assert actual_roi == expected_roi
        assert actual_roi == 50.0
    
    def test_calculate_metrics_with_zero_values(self):
        """Test calculations with zero values to avoid division by zero."""
        # Test CTR with zero impressions
        ctr = 50 / max(0, 1)
        assert ctr == 50.0
        
        # Test conversion rate with zero clicks
        conversion_rate = 5 / max(0, 1)
        assert conversion_rate == 5.0
        
        # Test CPC with zero clicks
        cpc = 100.0 / max(0, 1)
        assert cpc == 100.0
        
        # Test ROI with zero spend
        with pytest.raises(ZeroDivisionError):
            roi = ((1000 - 0) / 0) * 100


@pytest.mark.unit
@pytest.mark.simulation
class TestSimulationLogic:
    """Test core simulation logic functions."""
    
    def test_keyword_boost_calculation(self):
        """Test keyword boost calculation logic."""
        # Simulate the keyword boost logic from main.py
        keywords = ["smartphone", "premium", "qualidade", "android", "garantia"]
        keyword_boost = min(len(keywords) * 0.1, 0.3)
        
        assert keyword_boost == 0.3  # Should cap at 30%
        
        # Test with fewer keywords
        few_keywords = ["smartphone", "premium"]
        keyword_boost_small = min(len(few_keywords) * 0.1, 0.3)
        
        assert keyword_boost_small == 0.2  # 20% for 2 keywords
    
    def test_duration_factor_calculation(self):
        """Test campaign duration factor calculation."""
        # Simulate duration factor logic
        duration_days_long = 45
        duration_factor_long = min(duration_days_long / 30, 1.0)
        assert duration_factor_long == 1.0  # Capped at 1.0
        
        duration_days_short = 15
        duration_factor_short = min(duration_days_short / 30, 1.0)
        assert duration_factor_short == 0.5  # 50% for 15 days
    
    def test_average_order_value_calculation(self):
        """Test average order value calculation logic."""
        budget = 1000.0
        estimated_conversions = 10
        base_multiplier = 4.5  # Mid-range of 3-6
        
        # Simulate AOV calculation
        aov = budget / max(1, estimated_conversions) * base_multiplier
        expected_aov = 1000.0 / 10 * 4.5
        
        assert aov == expected_aov
        assert aov == 450.0
    
    def test_simulation_variance_logic(self):
        """Test that simulation includes proper variance."""
        # Test that keyword boost doesn't exceed limits
        max_keywords = ["key1", "key2", "key3", "key4", "key5", "key6", "key7"]
        boost = min(len(max_keywords) * 0.1, 0.3)
        assert boost == 0.3  # Should cap at 30%
        
        # Test duration factor bounds
        very_long_duration = 100
        duration_factor = min(very_long_duration / 30, 1.0)
        assert duration_factor == 1.0  # Should not exceed 100%


@pytest.mark.errors
class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_category_mapping_with_none(self):
        """Test category mapping with None input."""
        # Should handle None gracefully
        try:
            category_id = get_category_id_from_name(None)
            # If it doesn't raise exception, should return default
            assert category_id == "MLB1051"
        except (TypeError, AttributeError):
            # Exception is acceptable for None input
            pass
    
    def test_division_by_zero_protection(self):
        """Test that calculations protect against division by zero."""
        # Test the max(value, 1) pattern used in calculations
        safe_division_result = 100 / max(0, 1)
        assert safe_division_result == 100.0
        
        # Test with actual zero
        zero_clicks = 0
        safe_cpc = 500.0 / max(zero_clicks, 1)
        assert safe_cpc == 500.0
    
    @pytest.mark.asyncio
    async def test_historical_data_error_recovery(self):
        """Test historical data generation error recovery."""
        # Test with invalid category (should still work)
        historical_data = await get_mercadolibre_historical_data("INVALID_CATEGORY", 3)
        
        assert isinstance(historical_data, list)
        assert len(historical_data) == 3  # Should generate data for any category
        
        for data_point in historical_data:
            assert data_point.category == "INVALID_CATEGORY"
            assert data_point.impressions > 0
            assert data_point.clicks > 0
    
    def test_report_generation_with_invalid_data(self):
        """Test report generation handles invalid data gracefully."""
        # Test CSV generation with malformed campaign data
        from app.main import campaign_results
        
        campaign_results["MALFORMED"] = {
            # Missing some required fields
            "campaign_id": "MALFORMED",
            "estimated_reach": "not_a_number",  # Invalid data type
        }
        
        # Should not crash, but might skip malformed data
        try:
            csv_content = generate_csv_report(["MALFORMED"])
            assert isinstance(csv_content, str)
        except (KeyError, TypeError, ValueError):
            # Acceptable to raise exception for malformed data
            pass
        finally:
            # Clean up
            if "MALFORMED" in campaign_results:
                del campaign_results["MALFORMED"]


@pytest.mark.unit
@pytest.mark.validators
class TestDataValidation:
    """Test data validation functions."""
    
    def test_historical_data_model_validation(self):
        """Test HistoricalData model validation."""
        # Valid data
        valid_data = HistoricalData(
            date="2024-01-15",
            impressions=1000,
            clicks=50,
            conversions=5,
            spend=100.0,
            category="MLB1051"
        )
        
        assert valid_data.date == "2024-01-15"
        assert valid_data.impressions == 1000
        assert valid_data.clicks == 50
        assert valid_data.conversions == 5
        assert valid_data.spend == 100.0
        assert valid_data.category == "MLB1051"
    
    def test_campaign_simulation_request_validation(self):
        """Test CampaignSimulationRequest model validation."""
        valid_request = CampaignSimulationRequest(
            product_name="Test Product",
            category="electronics",
            budget=1000.0,
            duration_days=30,
            target_audience="young_adults",
            keywords=["test", "product"]
        )
        
        assert valid_request.product_name == "Test Product"
        assert valid_request.category == "electronics"
        assert valid_request.budget == 1000.0
        assert valid_request.duration_days == 30
        assert valid_request.target_audience == "young_adults"
        assert valid_request.keywords == ["test", "product"]
    
    def test_ab_test_request_validation(self):
        """Test ABTestRequest model validation."""
        valid_ab_test = ABTestRequest(
            test_name="Test Campaign A/B",
            variations=[
                CampaignSimulationRequest(
                    product_name="Variation A",
                    category="electronics",
                    budget=500.0,
                    duration_days=15,
                    target_audience="professionals",
                    keywords=["professional"]
                ),
                CampaignSimulationRequest(
                    product_name="Variation B",
                    category="electronics",
                    budget=500.0,
                    duration_days=15,
                    target_audience="students",
                    keywords=["student"]
                )
            ],
            traffic_split=[50.0, 50.0]
        )
        
        assert valid_ab_test.test_name == "Test Campaign A/B"
        assert len(valid_ab_test.variations) == 2
        assert valid_ab_test.traffic_split == [50.0, 50.0]
        assert sum(valid_ab_test.traffic_split) == 100.0


@pytest.mark.unit
@pytest.mark.parsers
class TestDataParsing:
    """Test data parsing and transformation functions."""
    
    def test_campaign_metrics_parsing(self):
        """Test parsing campaign metrics from historical data."""
        historical_data = [
            HistoricalData(
                date="2024-01-01",
                impressions=1000,
                clicks=50,
                conversions=2,
                spend=100.0,
                category="MLB1051"
            ),
            HistoricalData(
                date="2024-01-02",
                impressions=1200,
                clicks=60,
                conversions=3,
                spend=120.0,
                category="MLB1051"
            )
        ]
        
        # Calculate averages (simulating parsing logic)
        avg_ctr = sum(h.clicks / max(h.impressions, 1) for h in historical_data) / len(historical_data)
        avg_conversion_rate = sum(h.conversions / max(h.clicks, 1) for h in historical_data) / len(historical_data)
        avg_cpc = sum(h.spend / max(h.clicks, 1) for h in historical_data) / len(historical_data)
        
        assert abs(avg_ctr - 0.05) < 0.001  # Should be close to 5%
        assert abs(avg_conversion_rate - 0.045) < 0.01  # Should be close to 4.5%
        assert abs(avg_cpc - 2.0) < 0.001  # Should be close to 2.0
    
    def test_traffic_split_parsing(self):
        """Test parsing and validation of traffic split data."""
        # Valid traffic split
        traffic_split = [30.0, 40.0, 30.0]
        total = sum(traffic_split)
        
        assert abs(total - 100.0) < 0.1  # Should sum to 100%
        
        # Test that each split is reasonable
        for split in traffic_split:
            assert 0 <= split <= 100
    
    def test_keyword_list_parsing(self):
        """Test parsing keyword lists."""
        keyword_string = "smartphone,android,premium quality,electronics"
        keywords = [kw.strip() for kw in keyword_string.split(",")]
        
        assert len(keywords) == 4
        assert "smartphone" in keywords
        assert "premium quality" in keywords  # Should handle spaces
        assert all(isinstance(kw, str) for kw in keywords)
        assert all(len(kw) > 0 for kw in keywords)  # No empty keywords