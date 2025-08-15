import pytest
from fastapi.testclient import TestClient
from app.main import app, campaigns_storage


class TestSimulatorAPI:
    """Test class for Simulator Service API endpoints"""

    def setup_method(self):
        """Clear campaigns storage before each test"""
        campaigns_storage.clear()

    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "simulator_service"}

    def test_create_campaign_simulation(self, client: TestClient, sample_campaign_request):
        """Test creating a new campaign simulation"""
        response = client.post("/api/simulate", json=sample_campaign_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "campaign_id" in data
        assert data["campaign_id"].startswith("CAM_")
        assert "estimated_reach" in data
        assert "estimated_clicks" in data
        assert "estimated_conversions" in data
        assert "estimated_revenue" in data
        assert "cost_per_click" in data
        assert "roi_percentage" in data
        assert "recommendations" in data
        assert "created_at" in data
        assert data["status"] == "active"
        
        # Verify data types
        assert isinstance(data["estimated_reach"], int)
        assert isinstance(data["estimated_clicks"], int)
        assert isinstance(data["estimated_conversions"], int)
        assert isinstance(data["estimated_revenue"], (int, float))
        assert isinstance(data["cost_per_click"], (int, float))
        assert isinstance(data["roi_percentage"], (int, float))
        assert isinstance(data["recommendations"], list)

    def test_get_campaign_simulation(self, client: TestClient, sample_campaign_request):
        """Test getting a specific campaign simulation"""
        # First create a campaign
        create_response = client.post("/api/simulate", json=sample_campaign_request)
        campaign_id = create_response.json()["campaign_id"]
        
        # Then get it
        response = client.get(f"/api/simulation/{campaign_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["campaign_id"] == campaign_id

    def test_get_nonexistent_campaign(self, client: TestClient):
        """Test getting a campaign that doesn't exist"""
        response = client.get("/api/simulation/CAM_NOTFOUND")
        assert response.status_code == 404
        assert "Campaign not found" in response.json()["detail"]

    def test_list_campaigns_empty(self, client: TestClient):
        """Test listing campaigns when none exist"""
        response = client.get("/api/campaigns")
        assert response.status_code == 200
        
        data = response.json()
        assert data["campaigns"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_list_campaigns_with_data(self, client: TestClient, sample_campaign_request):
        """Test listing campaigns when some exist"""
        # Create a few campaigns
        for i in range(3):
            request = sample_campaign_request.copy()
            request["product_name"] = f"Product {i}"
            client.post("/api/simulate", json=request)
        
        response = client.get("/api/campaigns")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["campaigns"]) == 3
        assert data["total"] == 3

    def test_list_campaigns_pagination(self, client: TestClient, sample_campaign_request):
        """Test campaign listing with pagination"""
        # Create 5 campaigns
        for i in range(5):
            request = sample_campaign_request.copy()
            request["product_name"] = f"Product {i}"
            client.post("/api/simulate", json=request)
        
        # Test first page
        response = client.get("/api/campaigns?page=1&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2

        # Test second page
        response = client.get("/api/campaigns?page=2&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) == 2
        assert data["page"] == 2

    def test_list_campaigns_filter_by_status(self, client: TestClient, sample_campaign_request):
        """Test filtering campaigns by status"""
        # Create a campaign and update its status
        create_response = client.post("/api/simulate", json=sample_campaign_request)
        campaign_id = create_response.json()["campaign_id"]
        
        client.put(f"/api/simulation/{campaign_id}", json={"status": "paused"})
        
        # Test filtering by active status (should be empty)
        response = client.get("/api/campaigns?status=active")
        assert response.status_code == 200
        assert len(response.json()["campaigns"]) == 0

        # Test filtering by paused status (should have our campaign)
        response = client.get("/api/campaigns?status=paused")
        assert response.status_code == 200
        assert len(response.json()["campaigns"]) == 1

    def test_update_campaign(self, client: TestClient, sample_campaign_request, sample_campaign_update):
        """Test updating a campaign"""
        # Create a campaign
        create_response = client.post("/api/simulate", json=sample_campaign_request)
        campaign_id = create_response.json()["campaign_id"]
        
        # Update it
        response = client.put(f"/api/simulation/{campaign_id}", json=sample_campaign_update)
        assert response.status_code == 200
        
        data = response.json()
        assert data["campaign_id"] == campaign_id
        assert data["status"] == "paused"

    def test_update_nonexistent_campaign(self, client: TestClient, sample_campaign_update):
        """Test updating a campaign that doesn't exist"""
        response = client.put("/api/simulation/CAM_NOTFOUND", json=sample_campaign_update)
        assert response.status_code == 404

    def test_delete_campaign(self, client: TestClient, sample_campaign_request):
        """Test deleting a campaign"""
        # Create a campaign
        create_response = client.post("/api/simulate", json=sample_campaign_request)
        campaign_id = create_response.json()["campaign_id"]
        
        # Delete it
        response = client.delete(f"/api/simulation/{campaign_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify it's gone
        get_response = client.get(f"/api/simulation/{campaign_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_campaign(self, client: TestClient):
        """Test deleting a campaign that doesn't exist"""
        response = client.delete("/api/simulation/CAM_NOTFOUND")
        assert response.status_code == 404

    def test_campaigns_stats_empty(self, client: TestClient):
        """Test getting campaign stats when no campaigns exist"""
        response = client.get("/api/campaigns/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_campaigns"] == 0
        assert data["active_campaigns"] == 0
        assert data["total_budget"] == 0
        assert data["avg_roi"] == 0
        assert data["avg_cpc"] == 0

    def test_campaigns_stats_with_data(self, client: TestClient, sample_campaign_request):
        """Test getting campaign stats with actual data"""
        # Create some campaigns
        for i in range(3):
            request = sample_campaign_request.copy()
            request["budget"] = 1000 + (i * 500)  # Different budgets
            client.post("/api/simulate", json=request)
        
        response = client.get("/api/campaigns/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_campaigns"] == 3
        assert data["active_campaigns"] == 3
        assert data["total_budget"] > 0
        assert data["avg_roi"] > 0
        assert data["avg_cpc"] > 0

    def test_campaign_recommendations_vary_by_parameters(self, client: TestClient):
        """Test that campaign recommendations vary based on input parameters"""
        # Low budget, short duration should get specific recommendations
        low_budget_request = {
            "product_name": "Basic Product",
            "category": "home",
            "budget": 100.0,
            "duration_days": 3,
            "target_audience": "families",
            "keywords": ["cheap"]  # Few keywords
        }
        
        response = client.post("/api/simulate", json=low_budget_request)
        assert response.status_code == 200
        
        recommendations = response.json()["recommendations"]
        assert any("extending campaign duration" in rec.lower() for rec in recommendations)
        assert any("adding more relevant keywords" in rec.lower() for rec in recommendations)

    def test_category_multipliers_affect_results(self, client: TestClient, sample_campaign_request):
        """Test that different categories produce different results"""
        # Electronics category
        electronics_request = sample_campaign_request.copy()
        electronics_request["category"] = "electronics"
        
        electronics_response = client.post("/api/simulate", json=electronics_request)
        electronics_reach = electronics_response.json()["estimated_reach"]
        
        # Books category (lower multiplier)
        books_request = sample_campaign_request.copy()
        books_request["category"] = "books"
        
        books_response = client.post("/api/simulate", json=books_request)
        books_reach = books_response.json()["estimated_reach"]
        
        # Electronics should have higher reach than books
        assert electronics_reach > books_reach

    def test_invalid_campaign_data(self, client: TestClient):
        """Test creating campaign with invalid data"""
        invalid_request = {
            "product_name": "",  # Empty name
            "budget": -100,  # Negative budget
            "duration_days": 0,  # Zero duration
        }
        
        response = client.post("/api/simulate", json=invalid_request)
        assert response.status_code == 422  # Validation error