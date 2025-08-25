"""Tests for Campaign Automation Service."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.models.campaign_models import (
    CampaignCreate, CampaignUpdate, CampaignType, OptimizationGoal, CampaignStatus
)
from src.core.campaign_manager import CampaignManager
from src.core.metrics_analyzer import MetricsAnalyzer
from src.core.competitor_monitor import CompetitorMonitor
from src.services.ai_integration import AIIntegrationService
from src.services.scheduler import SchedulerService, TaskType, TaskPriority


# Test client
client = TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing."""
    return {
        "name": "Test Campaign",
        "description": "Test campaign description",
        "campaign_type": CampaignType.SPONSORED_ADS,
        "optimization_goal": OptimizationGoal.CONVERSIONS,
        "daily_budget": 100.0,
        "keywords": ["test", "keyword"],
        "categories": ["electronics"],
        "target_audience": {"age": "25-45", "interests": ["technology"]}
    }


class TestCampaignManager:
    """Test CampaignManager functionality."""
    
    @pytest.mark.asyncio
    async def test_create_campaign(self, mock_db, sample_campaign_data):
        """Test campaign creation."""
        manager = CampaignManager(mock_db)
        
        # Mock database operations
        mock_campaign = Mock()
        mock_campaign.id = 1
        mock_campaign.name = sample_campaign_data["name"]
        mock_campaign.status = CampaignStatus.DRAFT.value
        mock_campaign.created_at = datetime.utcnow()
        mock_campaign.updated_at = datetime.utcnow()
        mock_campaign.impressions = 0
        mock_campaign.clicks = 0
        mock_campaign.conversions = 0
        mock_campaign.cost = 0.0
        mock_campaign.revenue = 0.0
        
        # Set all required attributes
        for key, value in sample_campaign_data.items():
            if hasattr(mock_campaign, key):
                setattr(mock_campaign, key, value.value if hasattr(value, 'value') else value)
            else:
                setattr(mock_campaign, key, value.value if hasattr(value, 'value') else value)
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock the campaign creation to return our mock
        with patch.object(manager, '_to_response_model') as mock_to_response:
            mock_to_response.return_value = Mock(id=1, name=sample_campaign_data["name"])
            
            campaign_create = CampaignCreate(**sample_campaign_data)
            result = await manager.create_campaign(campaign_create, "test_user")
            
            assert result.id == 1
            assert result.name == sample_campaign_data["name"]
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_campaign(self, mock_db):
        """Test getting a campaign by ID."""
        manager = CampaignManager(mock_db)
        
        mock_campaign = Mock()
        mock_campaign.id = 1
        mock_campaign.name = "Test Campaign"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campaign
        
        with patch.object(manager, '_to_response_model') as mock_to_response:
            mock_to_response.return_value = Mock(id=1, name="Test Campaign")
            
            result = await manager.get_campaign(1)
            
            assert result.id == 1
            assert result.name == "Test Campaign"
    
    @pytest.mark.asyncio
    async def test_get_campaign_not_found(self, mock_db):
        """Test getting a non-existent campaign."""
        manager = CampaignManager(mock_db)
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = await manager.get_campaign(999)
        
        assert result is None


class TestMetricsAnalyzer:
    """Test MetricsAnalyzer functionality."""
    
    @pytest.mark.asyncio
    async def test_record_campaign_metrics(self, mock_db):
        """Test recording campaign metrics."""
        analyzer = MetricsAnalyzer(mock_db)
        
        mock_campaign = Mock()
        mock_campaign.impressions = 0
        mock_campaign.clicks = 0
        mock_campaign.conversions = 0
        mock_campaign.cost = 0.0
        mock_campaign.revenue = 0.0
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campaign
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        
        await analyzer.record_campaign_metrics(
            campaign_id=1,
            impressions=1000,
            clicks=50,
            conversions=5,
            cost=25.0,
            revenue=100.0
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Check campaign totals were updated
        assert mock_campaign.impressions == 1000
        assert mock_campaign.clicks == 50
        assert mock_campaign.conversions == 5
        assert mock_campaign.cost == 25.0
        assert mock_campaign.revenue == 100.0
    
    @pytest.mark.asyncio
    async def test_analyze_performance_trends(self, mock_db):
        """Test performance trend analysis."""
        analyzer = MetricsAnalyzer(mock_db)
        
        with patch.object(analyzer, 'get_daily_aggregated_metrics') as mock_get_metrics:
            mock_get_metrics.return_value = [
                {"date": "2023-01-01", "ctr": 2.0, "cpc": 1.0, "roas": 3.0},
                {"date": "2023-01-02", "ctr": 2.5, "cpc": 0.9, "roas": 3.5},
                {"date": "2023-01-03", "ctr": 3.0, "cpc": 0.8, "roas": 4.0}
            ]
            
            result = await analyzer.analyze_performance_trends(1, 7)
            
            assert "trends" in result
            assert "ctr" in result["trends"]
            assert result["trends"]["ctr"]["direction"] == "increasing"
            assert len(result["recommendations"]) > 0


class TestCompetitorMonitor:
    """Test CompetitorMonitor functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_competitor(self, mock_db):
        """Test competitor analysis."""
        monitor = CompetitorMonitor(mock_db)
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        
        result = await monitor.analyze_competitor(
            competitor_name="Test Competitor",
            category="electronics",
            keywords=["laptop", "computer"]
        )
        
        assert result.competitor_name == "Test Competitor"
        assert result.category == "electronics"
        assert result.threat_level in ["low", "medium", "high"]
        assert isinstance(result.opportunity_score, float)
        assert isinstance(result.recommendations, list)
    
    @pytest.mark.asyncio
    async def test_get_keyword_competition_analysis(self, mock_db):
        """Test keyword competition analysis."""
        monitor = CompetitorMonitor(mock_db)
        
        result = await monitor.get_keyword_competition_analysis(
            keywords=["laptop", "computer"],
            category="electronics"
        )
        
        assert "competition_data" in result
        assert "insights" in result
        assert len(result["competition_data"]) == 2
        assert "laptop" in result["competition_data"]
        assert "computer" in result["competition_data"]


class TestAIIntegrationService:
    """Test AIIntegrationService functionality."""
    
    @pytest.mark.asyncio
    async def test_optimize_campaign_copy(self):
        """Test campaign copy optimization."""
        service = AIIntegrationService()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "optimized_text": "Optimized copy text",
                "improvement_score": 85,
                "seo_score": 90,
                "suggestions": ["Use action words", "Add urgency"]
            }
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await service.optimize_campaign_copy(
                campaign_id=1,
                current_copy="Original copy text",
                target_audience={"demographics": "young_adults"},
                category="electronics"
            )
            
            assert result["success"] is True
            assert result["optimized_copy"] == "Optimized copy text"
            assert result["improvement_score"] == 85
    
    @pytest.mark.asyncio
    async def test_simulate_campaign_performance(self):
        """Test campaign performance simulation."""
        service = AIIntegrationService()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "campaign_id": "SIM_123456",
                "estimated_reach": 10000,
                "estimated_clicks": 500,
                "estimated_conversions": 25,
                "roi_percentage": 150.0,
                "recommendations": ["Increase budget", "Optimize keywords"]
            }
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await service.simulate_campaign_performance({
                "name": "Test Campaign",
                "category": "electronics",
                "daily_budget": 100,
                "keywords": ["laptop"]
            })
            
            assert result["success"] is True
            assert result["estimated_impressions"] == 10000
            assert result["estimated_clicks"] == 500
            assert result["roi_percentage"] == 150.0


class TestSchedulerService:
    """Test SchedulerService functionality."""
    
    @pytest.mark.asyncio
    async def test_schedule_task(self):
        """Test task scheduling."""
        with patch('redis.from_url') as mock_redis:
            mock_redis_client = Mock()
            mock_redis.return_value = mock_redis_client
            mock_redis_client.hset.return_value = None
            
            scheduler = SchedulerService()
            scheduler.redis_client = mock_redis_client
            
            task_id = await scheduler.schedule_task(
                task_type=TaskType.CAMPAIGN_OPTIMIZATION,
                campaign_id=1,
                parameters={"optimization_type": "general"},
                priority=TaskPriority.MEDIUM
            )
            
            assert task_id.startswith("campaign_optimization_1_")
            mock_redis_client.hset.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_status(self):
        """Test getting task status."""
        with patch('redis.from_url') as mock_redis:
            mock_redis_client = Mock()
            mock_redis.return_value = mock_redis_client
            
            task_data = {
                "id": "test_task_123",
                "status": "completed",
                "result": {"success": True}
            }
            mock_redis_client.hget.return_value = '{"id": "test_task_123", "status": "completed"}'
            
            scheduler = SchedulerService()
            scheduler.redis_client = mock_redis_client
            
            result = await scheduler.get_task_status("test_task_123")
            
            assert result["id"] == "test_task_123"
            assert result["status"] == "completed"


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Campaign Automation Service"
        assert "features" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "campaign_automation_service"
    
    def test_service_info_endpoint(self):
        """Test service info endpoint."""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Campaign Automation Service"
        assert "features" in data
        assert "endpoints" in data
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "requests_total" in data
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test integration workflow between components."""
    # This would test the complete workflow of creating a campaign,
    # analyzing performance, and optimizing it
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])