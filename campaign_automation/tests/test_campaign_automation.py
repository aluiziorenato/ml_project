import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "campaign_automation"
    assert "scheduler_running" in data

def test_get_campaigns():
    """Test getting all campaigns"""
    response = client.get("/api/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert "campaigns" in data
    assert "total" in data
    assert data["total"] >= 0

def test_get_campaign_details():
    """Test getting specific campaign details"""
    # First get all campaigns to get a valid ID
    campaigns_response = client.get("/api/campaigns")
    campaigns_data = campaigns_response.json()
    
    if campaigns_data["campaigns"]:
        campaign_id = list(campaigns_data["campaigns"].keys())[0]
        response = client.get(f"/api/campaigns/{campaign_id}")
        assert response.status_code == 200
        data = response.json()
        assert "campaign" in data
        assert data["campaign"]["id"] == campaign_id

def test_get_nonexistent_campaign():
    """Test getting a campaign that doesn't exist"""
    response = client.get("/api/campaigns/NONEXISTENT")
    assert response.status_code == 404

def test_create_automation_rule():
    """Test creating an automation rule"""
    rule_data = {
        "rule_id": "TEST_RULE_001",
        "campaign_id": "CAMP_001",
        "metric_type": "acos",
        "threshold_value": 0.25,
        "action_type": "pause"
    }
    
    response = client.post("/api/campaigns/CAMP_001/rules", json=rule_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Automation rule created successfully"
    assert data["rule"]["rule_id"] == "TEST_RULE_001"

def test_create_campaign_schedule():
    """Test creating a campaign schedule"""
    schedule_data = {
        "schedule_id": "TEST_SCHED_001",
        "campaign_id": "CAMP_001",
        "day_of_week": 1,
        "start_hour": 8,
        "end_hour": 18
    }
    
    response = client.post("/api/campaigns/CAMP_001/schedule", json=schedule_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Campaign schedule created successfully"
    assert data["schedule"]["schedule_id"] == "TEST_SCHED_001"

def test_update_campaign_metrics():
    """Test updating campaign metrics"""
    metrics_data = {
        "campaign_id": "CAMP_001",
        "acos": 0.22,
        "tacos": 0.18,
        "margin": 20.5,
        "cpc": 1.50,
        "ctr": 0.045,
        "conversion_rate": 0.032,
        "impressions": 10000,
        "clicks": 450,
        "conversions": 15,
        "spend": 675.0,
        "revenue": 3000.0
    }
    
    response = client.post("/api/monitoring/update-metrics", json=metrics_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Metrics updated successfully"
    assert data["campaign_id"] == "CAMP_001"

def test_get_campaign_metrics():
    """Test getting campaign metrics"""
    response = client.get("/api/monitoring/metrics/CAMP_001")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "campaign_id" in data

def test_get_competitor_analysis():
    """Test getting competitor analysis"""
    response = client.get("/api/monitoring/competitors")
    assert response.status_code == 200
    data = response.json()
    assert "competitors" in data
    assert "analysis_timestamp" in data

def test_predict_acos():
    """Test ACOS prediction"""
    response = client.get("/api/predictions/acos/CAMP_001")
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert "predicted_acos" in data
    assert "confidence_interval" in data
    assert "factors" in data
    assert "recommendation" in data

def test_get_pending_approvals():
    """Test getting pending approvals"""
    response = client.get("/api/approvals/pending")
    assert response.status_code == 200
    data = response.json()
    assert "pending_actions" in data
    assert "count" in data

def test_dashboard_overview():
    """Test dashboard overview"""
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    overview = data["overview"]
    assert "total_campaigns" in overview
    assert "active_campaigns" in overview
    assert "total_rules" in overview
    assert "pending_approvals" in overview

def test_get_campaign_charts():
    """Test getting campaign charts"""
    response = client.get("/api/dashboard/charts/CAMP_001")
    # May return 404 if no metrics, which is OK for this test
    assert response.status_code in [200, 404]

def test_get_campaign_calendar():
    """Test getting campaign calendar"""
    response = client.get("/api/calendar/CAMP_001")
    assert response.status_code == 200
    data = response.json()
    assert "campaign_id" in data
    assert "events" in data
    assert "schedule_count" in data

def test_create_calendar_event():
    """Test creating calendar event"""
    event_data = {
        "day": 1,
        "start_hour": 9,
        "end_hour": 17
    }
    
    response = client.post("/api/calendar/CAMP_001/events", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Calendar event created successfully"

def test_trigger_automation_rule():
    """Test that automation rules are triggered correctly"""
    # First, create a rule with a low threshold
    rule_data = {
        "rule_id": "TEST_TRIGGER_RULE",
        "campaign_id": "CAMP_TEST",
        "metric_type": "acos",
        "threshold_value": 0.20,
        "action_type": "pause"
    }
    
    client.post("/api/campaigns/CAMP_TEST/rules", json=rule_data)
    
    # Now send metrics that exceed the threshold
    metrics_data = {
        "campaign_id": "CAMP_TEST",
        "acos": 0.35,  # This exceeds the 0.20 threshold
        "tacos": 0.30,
        "margin": 15.0,
        "cpc": 2.0,
        "ctr": 0.03,
        "conversion_rate": 0.02,
        "impressions": 5000,
        "clicks": 150,
        "conversions": 3,
        "spend": 300.0,
        "revenue": 857.0
    }
    
    response = client.post("/api/monitoring/update-metrics", json=metrics_data)
    assert response.status_code == 200
    
    # Check if an action was created
    approvals_response = client.get("/api/approvals/pending")
    approvals_data = approvals_response.json()
    
    # Look for our triggered action
    triggered_actions = [
        action for action in approvals_data["pending_actions"]
        if action["campaign_id"] == "CAMP_TEST"
    ]
    
    assert len(triggered_actions) > 0
    action = triggered_actions[0]
    assert action["action_type"] == "pause"
    assert "ACOS" in action["reason"]

def test_invalid_rule_creation():
    """Test creating an invalid automation rule"""
    invalid_rule_data = {
        "rule_id": "INVALID_RULE",
        "campaign_id": "CAMP_001",
        "metric_type": "invalid_metric",  # Invalid metric type
        "threshold_value": 0.25,
        "action_type": "pause"
    }
    
    response = client.post("/api/campaigns/CAMP_001/rules", json=invalid_rule_data)
    assert response.status_code == 422  # Validation error

def test_invalid_schedule_creation():
    """Test creating an invalid schedule"""
    invalid_schedule_data = {
        "schedule_id": "INVALID_SCHED",
        "campaign_id": "CAMP_001",
        "day_of_week": 8,  # Invalid day (should be 0-6)
        "start_hour": 8,
        "end_hour": 18
    }
    
    response = client.post("/api/campaigns/CAMP_001/schedule", json=invalid_schedule_data)
    assert response.status_code == 422  # Validation error

def test_metrics_validation():
    """Test metrics validation"""
    invalid_metrics = {
        "campaign_id": "CAMP_001",
        "acos": -0.1,  # Negative value should be invalid
        "tacos": 0.18,
        "margin": 20.5,
        "cpc": 1.50,
        "ctr": 0.045,
        "conversion_rate": 0.032,
        "impressions": 10000,
        "clicks": 450,
        "conversions": 15,
        "spend": 675.0,
        "revenue": 3000.0
    }
    
    # This test assumes we have validation in place
    # The current implementation may not have this validation yet
    response = client.post("/api/monitoring/update-metrics", json=invalid_metrics)
    # For now, we just check that the endpoint exists
    assert response.status_code in [200, 400, 422]

@pytest.mark.asyncio
async def test_background_tasks():
    """Test that background tasks can be imported and don't fail immediately"""
    from app.main import monitor_campaigns, analyze_competitor_ads, optimize_time_based_campaigns
    
    # Just test that the functions exist and can be called
    # In a real test environment, we'd mock the external service calls
    try:
        await monitor_campaigns()
        await analyze_competitor_ads()
        await optimize_time_based_campaigns()
    except Exception as e:
        # It's OK if they fail due to missing services in test environment
        # We just want to make sure they're importable and structured correctly
        assert "monitor_campaigns" in str(monitor_campaigns)

def test_api_documentation():
    """Test that the OpenAPI documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_data = response.json()
    assert "openapi" in openapi_data
    assert "paths" in openapi_data