import pytest
import asyncio
from datetime import datetime, time
from sqlmodel import Session, create_engine, SQLModel
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_session
from app.models import (
    DiscountCampaign, CampaignSchedule, CampaignStatus, 
    DayOfWeek, ScheduleStatus, ItemSuggestion
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers for testing"""
    return {
        "Authorization": "Bearer mock_token"
    }


@pytest.fixture
def sample_campaign(session):
    """Create a sample campaign for testing"""
    campaign = DiscountCampaign(
        seller_id="TEST_SELLER_123",
        item_id="MLB123456789",
        campaign_name="Test Campaign",
        discount_percentage=15.0,
        status=CampaignStatus.DRAFT
    )
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign


class TestCampaignAPI:
    """Test campaign management API endpoints"""
    
    def test_create_campaign(self, client, mock_auth_headers):
        """Test campaign creation"""
        campaign_data = {
            "item_id": "MLB123456789",
            "campaign_name": "Test Discount Campaign",
            "discount_percentage": 20.0
        }
        
        # Mock the auth dependency
        def mock_get_current_user():
            return {"seller_id": "TEST_SELLER_123", "user_id": "user123"}
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.post(
            "/api/campaigns/",
            json=campaign_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == campaign_data["item_id"]
        assert data["campaign_name"] == campaign_data["campaign_name"]
        assert data["discount_percentage"] == campaign_data["discount_percentage"]
        assert data["status"] == "draft"
    
    def test_list_campaigns(self, client, mock_auth_headers, sample_campaign):
        """Test listing campaigns"""
        def mock_get_current_seller():
            return "TEST_SELLER_123"
        
        app.dependency_overrides[get_current_seller] = mock_get_current_seller
        
        response = client.get("/api/campaigns/", headers=mock_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["seller_id"] == "TEST_SELLER_123"
    
    def test_get_campaign(self, client, mock_auth_headers, sample_campaign):
        """Test getting a specific campaign"""
        def mock_get_current_seller():
            return "TEST_SELLER_123"
        
        app.dependency_overrides[get_current_seller] = mock_get_current_seller
        
        response = client.get(
            f"/api/campaigns/{sample_campaign.id}",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_campaign.id
        assert data["campaign_name"] == sample_campaign.campaign_name
    
    def test_update_campaign(self, client, mock_auth_headers, sample_campaign):
        """Test updating a campaign"""
        def mock_get_current_seller():
            return "TEST_SELLER_123"
        
        app.dependency_overrides[get_current_seller] = mock_get_current_seller
        
        update_data = {
            "campaign_name": "Updated Campaign Name",
            "discount_percentage": 25.0,
            "status": "active"
        }
        
        response = client.put(
            f"/api/campaigns/{sample_campaign.id}",
            json=update_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaign_name"] == update_data["campaign_name"]
        assert data["discount_percentage"] == update_data["discount_percentage"]
        assert data["status"] == update_data["status"]


class TestSchedulingService:
    """Test campaign scheduling functionality"""
    
    def test_create_schedule(self, session, sample_campaign):
        """Test creating a campaign schedule"""
        from app.services.scheduling_service import scheduling_service
        
        schedule_data = {
            "day_of_week": DayOfWeek.MONDAY,
            "start_time": time(9, 0),
            "end_time": time(17, 0),
            "action": "activate"
        }
        
        schedule = scheduling_service.create_schedule(
            session=session,
            campaign_id=sample_campaign.id,
            schedule_data=schedule_data
        )
        
        assert schedule.campaign_id == sample_campaign.id
        assert schedule.day_of_week == DayOfWeek.MONDAY
        assert schedule.action == "activate"
        assert schedule.status == ScheduleStatus.PENDING
    
    def test_get_campaign_schedules(self, session, sample_campaign):
        """Test getting schedules for a campaign"""
        from app.services.scheduling_service import scheduling_service
        
        # Create multiple schedules
        schedule_data_1 = {
            "day_of_week": DayOfWeek.MONDAY,
            "start_time": time(9, 0),
            "end_time": time(17, 0),
            "action": "activate"
        }
        
        schedule_data_2 = {
            "day_of_week": DayOfWeek.TUESDAY,
            "start_time": time(18, 0),
            "end_time": time(23, 59),
            "action": "pause"
        }
        
        scheduling_service.create_schedule(session, sample_campaign.id, schedule_data_1)
        scheduling_service.create_schedule(session, sample_campaign.id, schedule_data_2)
        
        schedules = scheduling_service.get_campaign_schedules(session, sample_campaign.id)
        
        assert len(schedules) == 2
        assert schedules[0].action in ["activate", "pause"]


class TestSuggestionsService:
    """Test strategic suggestions functionality"""
    
    def test_store_and_retrieve_suggestions(self, session):
        """Test storing and retrieving suggestions"""
        from app.services.suggestions_service import suggestions_service
        
        # Mock suggestions data
        suggestions_data = [
            {
                "id": "MLB123456789",
                "title": "Test Product 1",
                "price": 99.99,
                "category_id": "MLB1051",
                "thumbnail": "https://example.com/image1.jpg",
                "visits": 150,
                "unique_visits": 100,
                "potential_score": 0.85,
                "engagement_trend": 1.2
            },
            {
                "id": "MLB987654321",
                "title": "Test Product 2", 
                "price": 149.99,
                "category_id": "MLB1648",
                "thumbnail": "https://example.com/image2.jpg",
                "visits": 200,
                "unique_visits": 120,
                "potential_score": 0.78,
                "engagement_trend": 1.1
            }
        ]
        
        stored_suggestions = suggestions_service._store_suggestions(
            session=session,
            seller_id="TEST_SELLER_123",
            suggestions=suggestions_data
        )
        
        assert len(stored_suggestions) == 2
        assert stored_suggestions[0].potential_score == 0.85
        assert stored_suggestions[1].potential_score == 0.78
        
        # Test retrieval
        retrieved_suggestions = suggestions_service.get_stored_suggestions(
            session=session,
            seller_id="TEST_SELLER_123"
        )
        
        assert len(retrieved_suggestions) == 2
        assert retrieved_suggestions[0].potential_score == 0.85


class TestMetricsService:
    """Test metrics collection and analysis"""
    
    def test_process_visits_data(self):
        """Test processing of visits data into metrics"""
        from app.services.metrics_service import metrics_service
        
        visits_data = {
            "total_visits": 1000,
            "unique_visits": 600
        }
        
        processed_metrics = metrics_service._process_visits_data(visits_data)
        
        assert processed_metrics["clicks"] == 1000
        assert processed_metrics["impressions"] == 1200  # 600 * 2
        assert processed_metrics["conversions"] == 20  # 2% of 1000
        assert processed_metrics["conversion_rate"] == 0.02
        assert processed_metrics["sales_amount"] == 1000.0  # 20 * 50
        assert 0 <= processed_metrics["engagement_score"] <= 1
        assert 0 <= processed_metrics["performance_index"] <= 1


class TestPredictionService:
    """Test performance prediction functionality"""
    
    def test_generate_baseline_prediction(self):
        """Test baseline prediction generation"""
        from app.services.prediction_service import prediction_service
        
        prediction = prediction_service._generate_baseline_prediction(
            campaign_id=1,
            prediction_days=30
        )
        
        assert prediction.campaign_id == 1
        assert prediction.prediction_period_days == 30
        assert prediction.predicted_clicks > 0
        assert prediction.predicted_impressions > 0
        assert prediction.predicted_conversions > 0
        assert prediction.predicted_sales > 0
        assert prediction.confidence_score == 0.5


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Discount Campaign Scheduler"
        assert data["status"] == "active"
        assert "features" in data
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "discount-campaign-scheduler"
    
    def test_api_health_check(self, client):
        """Test API health check endpoint"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


if __name__ == "__main__":
    pytest.main([__file__])