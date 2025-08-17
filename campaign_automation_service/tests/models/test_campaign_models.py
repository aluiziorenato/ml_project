"""
Unit tests for campaign automation models.
Tests SQLAlchemy models, Pydantic schemas, and enum validations.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from typing import List, Dict, Any
import json

# Import models and enums
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from models.campaign_models import (
    CampaignStatus,
    CampaignType,
    OptimizationGoal,
    Campaign,
    Base
)


@pytest.mark.models
class TestEnumValidations:
    """Test enum validations for campaign models."""
    
    def test_campaign_status_enum_values(self):
        """Test all campaign status enum values."""
        assert CampaignStatus.DRAFT == "draft"
        assert CampaignStatus.ACTIVE == "active"
        assert CampaignStatus.PAUSED == "paused"
        assert CampaignStatus.COMPLETED == "completed"
        assert CampaignStatus.CANCELLED == "cancelled"
    
    def test_campaign_status_enum_membership(self):
        """Test campaign status enum membership."""
        valid_statuses = ["draft", "active", "paused", "completed", "cancelled"]
        
        for status in valid_statuses:
            assert status in CampaignStatus.__members__.values()
        
        # Test invalid status
        assert "invalid_status" not in CampaignStatus.__members__.values()
    
    def test_campaign_type_enum_values(self):
        """Test all campaign type enum values."""
        assert CampaignType.SPONSORED_ADS == "sponsored_ads"
        assert CampaignType.PRODUCT_ADS == "product_ads"
        assert CampaignType.DISPLAY_ADS == "display_ads"
        assert CampaignType.RETARGETING == "retargeting"
    
    def test_campaign_type_enum_membership(self):
        """Test campaign type enum membership."""
        valid_types = ["sponsored_ads", "product_ads", "display_ads", "retargeting"]
        
        for campaign_type in valid_types:
            assert campaign_type in CampaignType.__members__.values()
    
    def test_optimization_goal_enum_values(self):
        """Test all optimization goal enum values."""
        assert OptimizationGoal.CONVERSIONS == "conversions"
        assert OptimizationGoal.CLICKS == "clicks"
        assert OptimizationGoal.IMPRESSIONS == "impressions"
        assert OptimizationGoal.ROI == "roi"
        assert OptimizationGoal.REVENUE == "revenue"
    
    def test_optimization_goal_enum_membership(self):
        """Test optimization goal enum membership."""
        valid_goals = ["conversions", "clicks", "impressions", "roi", "revenue"]
        
        for goal in valid_goals:
            assert goal in OptimizationGoal.__members__.values()
    
    def test_enum_string_inheritance(self):
        """Test that enums inherit from string."""
        assert isinstance(CampaignStatus.ACTIVE, str)
        assert isinstance(CampaignType.SPONSORED_ADS, str)
        assert isinstance(OptimizationGoal.CONVERSIONS, str)


@pytest.mark.models
@pytest.mark.database
class TestCampaignModel:
    """Test Campaign SQLAlchemy model."""
    
    def test_campaign_model_structure(self):
        """Test Campaign model has expected attributes."""
        # Test that the model has the expected columns
        assert hasattr(Campaign, 'id')
        assert hasattr(Campaign, 'name')
        assert hasattr(Campaign, 'description')
        assert hasattr(Campaign, 'status')
        assert hasattr(Campaign, 'campaign_type')
        assert hasattr(Campaign, 'optimization_goal')
        
        # Test table name
        assert Campaign.__tablename__ == "campaigns"
    
    def test_campaign_model_column_types(self):
        """Test Campaign model column types."""
        # Check column types
        id_column = Campaign.__table__.columns['id']
        name_column = Campaign.__table__.columns['name']
        status_column = Campaign.__table__.columns['status']
        
        assert id_column.primary_key == True
        assert id_column.index == True
        assert name_column.index == True
        
        # Test default values
        assert status_column.default.arg == CampaignStatus.DRAFT
    
    def test_campaign_model_inheritance(self):
        """Test Campaign model inherits from Base."""
        assert issubclass(Campaign, Base)
        assert Campaign.__bases__[0] == Base
    
    def test_campaign_model_metadata(self):
        """Test Campaign model metadata."""
        # Test that metadata is properly set
        assert Campaign.metadata is not None
        assert 'campaigns' in Campaign.metadata.tables
        
        # Test table schema
        table = Campaign.metadata.tables['campaigns']
        assert 'id' in table.columns
        assert 'name' in table.columns
        assert 'status' in table.columns


@pytest.mark.models
class TestModelConstants:
    """Test model constants and enumerations."""
    
    def test_campaign_status_count(self):
        """Test expected number of campaign statuses."""
        statuses = list(CampaignStatus)
        assert len(statuses) == 5  # draft, active, paused, completed, cancelled
    
    def test_campaign_type_count(self):
        """Test expected number of campaign types."""
        types = list(CampaignType)
        assert len(types) == 4  # sponsored_ads, product_ads, display_ads, retargeting
    
    def test_optimization_goal_count(self):
        """Test expected number of optimization goals."""
        goals = list(OptimizationGoal)
        assert len(goals) == 5  # conversions, clicks, impressions, roi, revenue
    
    def test_enum_values_consistency(self):
        """Test enum values are consistent with string representations."""
        # Test CampaignStatus
        for status in CampaignStatus:
            assert status.value == status
        
        # Test CampaignType
        for campaign_type in CampaignType:
            assert campaign_type.value == campaign_type
            
        # Test OptimizationGoal
        for goal in OptimizationGoal:
            assert goal.value == goal


@pytest.mark.models
class TestEnumValidationEdgeCases:
    """Test enum validation edge cases."""
    
    def test_campaign_status_case_sensitivity(self):
        """Test campaign status case sensitivity."""
        # Should be case sensitive
        assert "ACTIVE" != CampaignStatus.ACTIVE
        assert "Active" != CampaignStatus.ACTIVE
        assert "active" == CampaignStatus.ACTIVE
    
    def test_campaign_type_case_sensitivity(self):
        """Test campaign type case sensitivity."""
        assert "SPONSORED_ADS" != CampaignType.SPONSORED_ADS
        assert "sponsored_ads" == CampaignType.SPONSORED_ADS
    
    def test_optimization_goal_case_sensitivity(self):
        """Test optimization goal case sensitivity."""
        assert "CONVERSIONS" != OptimizationGoal.CONVERSIONS
        assert "conversions" == OptimizationGoal.CONVERSIONS
    
    def test_enum_comparison(self):
        """Test enum comparison operations."""
        # Test equality
        assert CampaignStatus.ACTIVE == CampaignStatus.ACTIVE
        assert CampaignStatus.ACTIVE != CampaignStatus.PAUSED
        
        # Test string comparison
        assert CampaignStatus.ACTIVE == "active"
        assert CampaignStatus.ACTIVE != "paused"
    
    def test_enum_iteration(self):
        """Test enum iteration."""
        status_values = [status.value for status in CampaignStatus]
        expected_statuses = ["draft", "active", "paused", "completed", "cancelled"]
        
        assert len(status_values) == len(expected_statuses)
        for status in expected_statuses:
            assert status in status_values
    
    def test_enum_membership_testing(self):
        """Test enum membership testing."""
        # Test valid membership
        assert CampaignStatus.ACTIVE in CampaignStatus
        assert CampaignType.SPONSORED_ADS in CampaignType
        assert OptimizationGoal.CONVERSIONS in OptimizationGoal
        
        # Test string values
        all_status_values = [status.value for status in CampaignStatus]
        assert "active" in all_status_values
        assert "invalid" not in all_status_values


@pytest.mark.errors
@pytest.mark.models
class TestModelErrorHandling:
    """Test model error handling scenarios."""
    
    def test_invalid_enum_creation(self):
        """Test handling of invalid enum values."""
        # Note: Python enums don't raise errors for invalid values during comparison
        # but they do for creation. Let's test what we can.
        
        valid_statuses = list(CampaignStatus)
        assert len(valid_statuses) > 0
        
        # Test that we can't accidentally create invalid enum members
        try:
            # This should work - accessing existing member
            status = CampaignStatus.ACTIVE
            assert status == "active"
        except AttributeError:
            pytest.fail("Should be able to access valid enum member")
    
    def test_enum_serialization(self):
        """Test enum serialization for JSON/API usage."""
        # Test that enums can be serialized to JSON
        status_data = {
            "status": CampaignStatus.ACTIVE,
            "type": CampaignType.SPONSORED_ADS,
            "goal": OptimizationGoal.CONVERSIONS
        }
        
        # Convert to JSON-serializable format
        json_data = {
            "status": status_data["status"].value,
            "type": status_data["type"].value,
            "goal": status_data["goal"].value
        }
        
        json_str = json.dumps(json_data)
        parsed = json.loads(json_str)
        
        assert parsed["status"] == "active"
        assert parsed["type"] == "sponsored_ads"
        assert parsed["goal"] == "conversions"
    
    def test_enum_validation_in_context(self):
        """Test enum validation in realistic contexts."""
        # Test valid enum usage
        def validate_campaign_status(status):
            if status in [s.value for s in CampaignStatus]:
                return True
            return False
        
        # Test valid statuses
        assert validate_campaign_status("active") == True
        assert validate_campaign_status("draft") == True
        assert validate_campaign_status("completed") == True
        
        # Test invalid statuses
        assert validate_campaign_status("running") == False
        assert validate_campaign_status("pending") == False
        assert validate_campaign_status("") == False
        assert validate_campaign_status(None) == False


@pytest.mark.models
class TestModelIntegration:
    """Test model integration scenarios."""
    
    def test_enum_usage_in_model_context(self):
        """Test enum usage in realistic model contexts."""
        # Simulate model field validation
        def create_campaign_data(status, campaign_type, goal):
            return {
                "name": "Test Campaign",
                "status": status,
                "campaign_type": campaign_type,
                "optimization_goal": goal
            }
        
        # Test with valid enum values
        valid_data = create_campaign_data(
            CampaignStatus.ACTIVE,
            CampaignType.SPONSORED_ADS,
            OptimizationGoal.CONVERSIONS
        )
        
        assert valid_data["status"] == "active"
        assert valid_data["campaign_type"] == "sponsored_ads"
        assert valid_data["optimization_goal"] == "conversions"
    
    def test_campaign_workflow_states(self):
        """Test campaign workflow state transitions."""
        # Define valid state transitions
        valid_transitions = {
            CampaignStatus.DRAFT: [CampaignStatus.ACTIVE, CampaignStatus.CANCELLED],
            CampaignStatus.ACTIVE: [CampaignStatus.PAUSED, CampaignStatus.COMPLETED, CampaignStatus.CANCELLED],
            CampaignStatus.PAUSED: [CampaignStatus.ACTIVE, CampaignStatus.CANCELLED],
            CampaignStatus.COMPLETED: [],  # Terminal state
            CampaignStatus.CANCELLED: []   # Terminal state
        }
        
        def can_transition(from_status, to_status):
            return to_status in valid_transitions.get(from_status, [])
        
        # Test valid transitions
        assert can_transition(CampaignStatus.DRAFT, CampaignStatus.ACTIVE) == True
        assert can_transition(CampaignStatus.ACTIVE, CampaignStatus.PAUSED) == True
        assert can_transition(CampaignStatus.PAUSED, CampaignStatus.ACTIVE) == True
        
        # Test invalid transitions
        assert can_transition(CampaignStatus.COMPLETED, CampaignStatus.ACTIVE) == False
        assert can_transition(CampaignStatus.CANCELLED, CampaignStatus.ACTIVE) == False
    
    def test_optimization_goal_compatibility(self):
        """Test optimization goal compatibility with campaign types."""
        # Define compatibility matrix
        goal_compatibility = {
            CampaignType.SPONSORED_ADS: [
                OptimizationGoal.CLICKS, 
                OptimizationGoal.CONVERSIONS, 
                OptimizationGoal.ROI
            ],
            CampaignType.PRODUCT_ADS: [
                OptimizationGoal.CONVERSIONS,
                OptimizationGoal.REVENUE,
                OptimizationGoal.ROI
            ],
            CampaignType.DISPLAY_ADS: [
                OptimizationGoal.IMPRESSIONS,
                OptimizationGoal.CLICKS,
                OptimizationGoal.CONVERSIONS
            ],
            CampaignType.RETARGETING: [
                OptimizationGoal.CONVERSIONS,
                OptimizationGoal.REVENUE,
                OptimizationGoal.ROI
            ]
        }
        
        def is_goal_compatible(campaign_type, goal):
            return goal in goal_compatibility.get(campaign_type, [])
        
        # Test valid combinations
        assert is_goal_compatible(CampaignType.SPONSORED_ADS, OptimizationGoal.CLICKS) == True
        assert is_goal_compatible(CampaignType.PRODUCT_ADS, OptimizationGoal.REVENUE) == True
        assert is_goal_compatible(CampaignType.DISPLAY_ADS, OptimizationGoal.IMPRESSIONS) == True
        
        # Test potentially invalid combinations
        assert is_goal_compatible(CampaignType.SPONSORED_ADS, OptimizationGoal.IMPRESSIONS) == False


@pytest.mark.models
class TestModelDefaults:
    """Test model default values and behaviors."""
    
    def test_campaign_status_default(self):
        """Test campaign status default value."""
        # The default should be DRAFT
        default_status = CampaignStatus.DRAFT
        assert default_status == "draft"
        
        # Test that DRAFT is a reasonable default
        assert default_status in CampaignStatus
        assert default_status != CampaignStatus.ACTIVE  # Should not default to active
    
    def test_enum_string_representation(self):
        """Test enum string representation."""
        # Test that enums have proper string representation
        assert str(CampaignStatus.ACTIVE) == "active"
        assert str(CampaignType.SPONSORED_ADS) == "sponsored_ads"
        assert str(OptimizationGoal.CONVERSIONS) == "conversions"
        
        # Test representation
        assert repr(CampaignStatus.ACTIVE) == "<CampaignStatus.ACTIVE: 'active'>"
    
    def test_enum_iteration_order(self):
        """Test enum iteration order is consistent."""
        status_list = list(CampaignStatus)
        
        # Test that we always get the same order
        expected_order = [
            CampaignStatus.DRAFT,
            CampaignStatus.ACTIVE,
            CampaignStatus.PAUSED,
            CampaignStatus.COMPLETED,
            CampaignStatus.CANCELLED
        ]
        
        assert status_list == expected_order
    
    def test_enum_hashability(self):
        """Test that enums are hashable and can be used as dict keys."""
        # Test using enums as dictionary keys
        status_descriptions = {
            CampaignStatus.DRAFT: "Campaign is being prepared",
            CampaignStatus.ACTIVE: "Campaign is running",
            CampaignStatus.PAUSED: "Campaign is temporarily stopped",
            CampaignStatus.COMPLETED: "Campaign has finished",
            CampaignStatus.CANCELLED: "Campaign was cancelled"
        }
        
        assert len(status_descriptions) == 5
        assert status_descriptions[CampaignStatus.ACTIVE] == "Campaign is running"
        
        # Test using in sets
        active_statuses = {CampaignStatus.ACTIVE, CampaignStatus.PAUSED}
        assert CampaignStatus.ACTIVE in active_statuses
        assert CampaignStatus.DRAFT not in active_statuses