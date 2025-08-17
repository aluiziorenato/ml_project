"""
Comprehensive tests for Prometheus/Grafana monitoring integration

Tests cover:
- FastAPI metrics endpoint functionality
- Custom metrics collection validation
- Latency and error scenario simulation
- Metrics endpoint authentication/authorization
- Grafana dashboard data flow validation
"""

import pytest
import asyncio
import time
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import httpx
import aioresponses

# Import the backend app and dependencies
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.routers.metrics import router as metrics_router
from app.monitoring.prometheus_metrics import (
    get_metrics, record_request, record_security_event,
    set_model_accuracy, record_cache_operation,
    update_system_metrics, record_error
)
from app.settings import settings


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    app = FastAPI()
    app.include_router(metrics_router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for metrics endpoint."""
    return {"Authorization": f"Bearer {settings.metrics_api_key}"}


@pytest.fixture
def invalid_auth_headers():
    """Create invalid authentication headers."""
    return {"Authorization": "Bearer invalid-token"}


class TestMetricsEndpoint:
    """Test suite for FastAPI metrics endpoint."""

    def test_prometheus_metrics_endpoint_with_auth(self, client, auth_headers):
        """Test that metrics endpoint works with valid authentication."""
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        
        # Validate Prometheus format
        content = response.text
        assert "# HELP" in content
        assert "# TYPE" in content
        assert "http_requests_total" in content
        assert "system_cpu_usage_percent" in content

    def test_prometheus_metrics_endpoint_without_auth(self, client):
        """Test that metrics endpoint requires authentication when enabled."""
        # Test without any auth header
        response = client.get("/api/metrics/prometheus")
        assert response.status_code == 401
        
        # Test with invalid auth
        response = client.get(
            "/api/metrics/prometheus", 
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 403

    def test_prometheus_metrics_endpoint_auth_disabled(self, client):
        """Test metrics endpoint when authentication is disabled."""
        with patch.object(settings, 'enable_metrics_auth', False):
            response = client.get("/api/metrics/prometheus")
            assert response.status_code == 200
            assert "text/plain" in response.headers.get("content-type", "")

    def test_health_check_endpoint(self, client):
        """Test health check endpoint accessibility."""
        response = client.get("/api/metrics/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "uptime" in data

    def test_system_metrics_endpoint(self, client):
        """Test system metrics endpoint."""
        response = client.get("/api/metrics/system")
        assert response.status_code == 200
        
        data = response.json()
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "network" in data

    def test_test_metrics_generation(self, client):
        """Test the test metrics generation endpoint."""
        response = client.post("/api/metrics/test-metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data
        assert data["metrics"]["active_connections"] == 42
        assert data["metrics"]["campaigns_active"] == 15


class TestCustomMetricsCollection:
    """Test suite for custom metrics collection validation."""

    def test_http_request_metrics_recording(self):
        """Test that HTTP request metrics are properly recorded."""
        # Record some test requests
        record_request("GET", "/api/test", 200, 0.5)
        record_request("POST", "/api/auth", 401, 0.2)
        record_request("GET", "/api/test", 500, 1.0)
        
        # Get metrics and validate
        metrics_data = get_metrics().decode()
        
        # Check that request counts are recorded
        assert 'http_requests_total{endpoint="/api/test",method="GET",status_code="200"} 1.0' in metrics_data
        assert 'http_requests_total{endpoint="/api/auth",method="POST",status_code="401"} 1.0' in metrics_data
        assert 'http_requests_total{endpoint="/api/test",method="GET",status_code="500"} 1.0' in metrics_data

    def test_security_event_metrics(self):
        """Test security event metrics recording."""
        record_security_event("failed_login")
        record_security_event("suspicious_activity")
        record_security_event("failed_login")  # Record another failed login
        
        metrics_data = get_metrics().decode()
        
        # Check security events are recorded
        assert 'security_events_total{event_type="failed_login"} 2.0' in metrics_data
        assert 'security_events_total{event_type="suspicious_activity"} 1.0' in metrics_data

    def test_ml_model_accuracy_metrics(self):
        """Test ML model accuracy metrics."""
        set_model_accuracy("recommendation_engine", 0.87)
        set_model_accuracy("price_optimizer", 0.92)
        set_model_accuracy("recommendation_engine", 0.89)  # Update existing model
        
        metrics_data = get_metrics().decode()
        
        # Check model accuracy metrics
        assert 'ml_model_accuracy{model_name="recommendation_engine"} 0.89' in metrics_data
        assert 'ml_model_accuracy{model_name="price_optimizer"} 0.92' in metrics_data

    def test_cache_operation_metrics(self):
        """Test cache operation metrics."""
        record_cache_operation("get", "hit")
        record_cache_operation("get", "miss")
        record_cache_operation("set", "success")
        record_cache_operation("get", "hit")  # Another hit
        
        metrics_data = get_metrics().decode()
        
        # Check cache operation metrics
        assert 'cache_operations_total{operation="get",result="hit"} 2.0' in metrics_data
        assert 'cache_operations_total{operation="get",result="miss"} 1.0' in metrics_data
        assert 'cache_operations_total{operation="set",result="success"} 1.0' in metrics_data

    def test_system_metrics_update(self):
        """Test system metrics are updated correctly."""
        update_system_metrics()
        
        metrics_data = get_metrics().decode()
        
        # Check that system metrics are present and have reasonable values
        assert "system_cpu_usage_percent" in metrics_data
        assert "system_memory_usage_percent" in metrics_data
        assert "system_disk_usage_percent" in metrics_data


class TestLatencyAndErrorSimulation:
    """Test suite for latency and error scenario simulation."""

    @pytest.mark.asyncio
    async def test_high_latency_scenario(self, client, auth_headers):
        """Test metrics collection under high latency conditions."""
        # Simulate high latency requests
        start_time = time.time()
        
        # Record requests with varying latencies
        record_request("GET", "/api/slow-endpoint", 200, 2.5)
        record_request("GET", "/api/slow-endpoint", 200, 3.0)
        record_request("GET", "/api/slow-endpoint", 504, 5.0)  # Timeout
        
        # Get metrics
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        assert response.status_code == 200
        
        metrics_data = response.text
        
        # Verify latency metrics are recorded
        assert 'http_request_duration_seconds' in metrics_data
        assert 'http_requests_total' in metrics_data
        
        # Should include timeout status codes
        assert 'status_code="504"' in metrics_data

    def test_error_rate_simulation(self, client, auth_headers):
        """Test metrics during high error rate scenarios."""
        # Simulate various error conditions
        record_request("GET", "/api/failing", 500, 0.1)
        record_request("POST", "/api/failing", 500, 0.2)
        record_request("GET", "/api/failing", 503, 0.1)
        record_request("PUT", "/api/failing", 429, 0.05)  # Rate limit
        
        # Record application errors
        record_error("database_connection")
        record_error("external_api_timeout")
        record_error("memory_limit")
        
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        assert response.status_code == 200
        
        metrics_data = response.text
        
        # Verify error metrics are captured
        assert 'status_code="500"' in metrics_data
        assert 'status_code="503"' in metrics_data
        assert 'status_code="429"' in metrics_data
        assert 'application_errors_total' in metrics_data

    @pytest.mark.asyncio
    async def test_concurrent_requests_metrics(self, client, auth_headers):
        """Test metrics accuracy under concurrent load."""
        async def make_request():
            """Make a single request and record metrics."""
            record_request("GET", "/api/load-test", 200, 0.1)
            return True
        
        # Simulate concurrent requests
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 50
        
        # Get metrics and verify count accuracy
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        metrics_data = response.text
        
        # Should show 50 requests to the load-test endpoint
        assert 'http_requests_total{endpoint="/api/load-test",method="GET",status_code="200"} 50.0' in metrics_data

    def test_memory_pressure_simulation(self, client, auth_headers):
        """Test metrics behavior under memory pressure."""
        with patch('psutil.virtual_memory') as mock_memory:
            # Simulate high memory usage (90%)
            mock_memory.return_value.percent = 90.0
            
            update_system_metrics()
            
            response = client.get("/api/metrics/prometheus", headers=auth_headers)
            metrics_data = response.text
            
            # Verify high memory usage is recorded
            assert 'system_memory_usage_percent 90.0' in metrics_data


class TestMetricsAuthentication:
    """Test suite for metrics endpoint authentication and authorization."""

    def test_bearer_token_authentication(self, client):
        """Test Bearer token authentication mechanism."""
        valid_token = settings.metrics_api_key
        
        # Test valid token
        response = client.get(
            "/api/metrics/prometheus",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 200

    def test_invalid_token_rejection(self, client):
        """Test that invalid tokens are properly rejected."""
        invalid_tokens = [
            "invalid-token",
            "",
            "wrong-bearer-token",
            "Bearer invalid",  # Note: should be sent without Bearer prefix in header value
        ]
        
        for token in invalid_tokens:
            response = client.get(
                "/api/metrics/prometheus",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 403

    def test_missing_authorization_header(self, client):
        """Test behavior when Authorization header is missing."""
        response = client.get("/api/metrics/prometheus")
        assert response.status_code == 401
        
        error_data = response.json()
        assert "Authentication required" in error_data["detail"]

    def test_malformed_authorization_header(self, client):
        """Test handling of malformed Authorization headers."""
        malformed_headers = [
            {"Authorization": "invalid-format"},
            {"Authorization": "Basic dGVzdDp0ZXN0"},  # Basic auth instead of Bearer
            {"Authorization": "Bearer"},  # Missing token
        ]
        
        for headers in malformed_headers:
            response = client.get("/api/metrics/prometheus", headers=headers)
            assert response.status_code in [401, 403]

    def test_authentication_bypass_when_disabled(self, client):
        """Test that authentication can be disabled in configuration."""
        with patch.object(settings, 'enable_metrics_auth', False):
            # Should work without any authentication
            response = client.get("/api/metrics/prometheus")
            assert response.status_code == 200


class TestPrometheusFormatValidation:
    """Test suite for Prometheus metrics format validation."""

    def test_prometheus_exposition_format(self, client, auth_headers):
        """Test that metrics are in valid Prometheus exposition format."""
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        assert response.status_code == 200
        
        content = response.text
        lines = content.strip().split('\n')
        
        # Validate Prometheus format structure
        help_lines = [line for line in lines if line.startswith('# HELP')]
        type_lines = [line for line in lines if line.startswith('# TYPE')]
        metric_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        
        assert len(help_lines) > 0, "Should have HELP comments"
        assert len(type_lines) > 0, "Should have TYPE comments"
        assert len(metric_lines) > 0, "Should have metric data"

    def test_metric_naming_conventions(self, client, auth_headers):
        """Test that metrics follow Prometheus naming conventions."""
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        content = response.text
        
        # Check for expected metric names
        expected_metrics = [
            "http_requests_total",
            "http_request_duration_seconds",
            "system_cpu_usage_percent",
            "system_memory_usage_percent",
            "ml_model_accuracy",
            "security_events_total",
            "cache_operations_total"
        ]
        
        for metric in expected_metrics:
            assert metric in content, f"Missing expected metric: {metric}"

    def test_metric_labels_format(self, client, auth_headers):
        """Test that metric labels are properly formatted."""
        # Generate some labeled metrics
        record_request("GET", "/api/test", 200, 0.1)
        record_security_event("test_event")
        
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        content = response.text
        
        # Check label format in metrics
        lines = content.split('\n')
        metric_lines = [line for line in lines if not line.startswith('#') and '=' in line]
        
        for line in metric_lines:
            if '{' in line and '}' in line:
                # Extract labels part
                labels_part = line[line.find('{')+1:line.find('}')]
                if labels_part:  # If there are labels
                    # Labels should be in format key="value"
                    assert '"' in labels_part, f"Labels should be quoted: {line}"

    def test_metric_values_are_numeric(self, client, auth_headers):
        """Test that all metric values are valid numbers."""
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        content = response.text
        
        lines = content.split('\n')
        metric_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        
        for line in metric_lines:
            if ' ' in line:
                parts = line.split()
                if len(parts) >= 2:
                    value = parts[-1]  # Last part should be the value
                    try:
                        float(value)
                    except ValueError:
                        pytest.fail(f"Invalid metric value '{value}' in line: {line}")


class TestGrafanaDashboardDataFlow:
    """Test suite for Grafana dashboard data flow validation."""

    @pytest.mark.asyncio
    async def test_prometheus_data_source_connectivity(self):
        """Test that Prometheus data source can be reached (mock)."""
        # This would normally test actual Prometheus connectivity
        # For unit testing, we'll mock the HTTP request
        
        prometheus_url = "http://prometheus:9090"
        
        with aioresponses.aioresponses() as m:
            m.get(f"{prometheus_url}/api/v1/query?query=up", payload={
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [{"metric": {"__name__": "up"}, "value": [1234567890, "1"]}]
                }
            })
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{prometheus_url}/api/v1/query?query=up")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"

    def test_dashboard_query_compatibility(self):
        """Test that generated metrics are compatible with dashboard queries."""
        # Generate test data that should be queryable by dashboard
        record_request("GET", "/api/campaigns", 200, 0.1)
        record_request("POST", "/api/auth", 200, 0.2)
        set_model_accuracy("recommendation", 0.85)
        update_system_metrics()
        
        metrics_data = get_metrics().decode()
        
        # Test queries that would be used in Grafana dashboards
        dashboard_queries = [
            "rate(http_requests_total[5m])",  # Request rate
            "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",  # 95th percentile latency
            "ml_model_accuracy",  # Model accuracy gauge
            "system_cpu_usage_percent",  # CPU usage
        ]
        
        # Verify that base metrics needed for these queries exist
        assert "http_requests_total" in metrics_data
        assert "http_request_duration_seconds" in metrics_data
        assert "ml_model_accuracy" in metrics_data
        assert "system_cpu_usage_percent" in metrics_data

    def test_alert_rule_compatibility(self):
        """Test that metrics are compatible with alerting rules."""
        # Generate conditions that would trigger alerts
        record_request("GET", "/api/test", 500, 0.1)  # Error
        record_request("GET", "/api/test", 200, 5.0)   # High latency
        
        with patch('psutil.cpu_percent', return_value=95.0):  # High CPU
            update_system_metrics()
        
        metrics_data = get_metrics().decode()
        
        # Verify metrics that alerts would query exist
        assert 'status_code="500"' in metrics_data  # For error rate alerts
        assert "http_request_duration_seconds" in metrics_data  # For latency alerts
        assert "system_cpu_usage_percent 95.0" in metrics_data  # For CPU alerts

    def test_metrics_retention_and_consistency(self, client, auth_headers):
        """Test that metrics remain consistent across multiple collections."""
        # Generate initial metrics
        record_request("GET", "/api/consistent", 200, 0.1)
        first_response = client.get("/api/metrics/prometheus", headers=auth_headers)
        first_content = first_response.text
        
        # Generate more metrics
        record_request("GET", "/api/consistent", 200, 0.1)
        second_response = client.get("/api/metrics/prometheus", headers=auth_headers)
        second_content = second_response.text
        
        # The counter should have incremented
        # Extract the counter value from both responses
        import re
        pattern = r'http_requests_total\{.*endpoint="/api/consistent".*\} (\d+\.?\d*)'
        
        first_match = re.search(pattern, first_content)
        second_match = re.search(pattern, second_content)
        
        if first_match and second_match:
            first_value = float(first_match.group(1))
            second_value = float(second_match.group(1))
            assert second_value > first_value, "Counter should increment"


class TestEndToEndScenarios:
    """End-to-end test scenarios for complete monitoring workflow."""

    @pytest.mark.asyncio
    async def test_complete_monitoring_workflow(self, client, auth_headers):
        """Test complete monitoring workflow from request to metrics collection."""
        # Step 1: Simulate application activity
        record_request("GET", "/api/products", 200, 0.3)
        record_request("POST", "/api/campaigns", 201, 0.8)
        record_request("GET", "/api/metrics", 200, 0.1)
        record_security_event("user_login")
        set_model_accuracy("price_prediction", 0.91)
        record_cache_operation("get", "hit")
        
        # Step 2: Collect system metrics
        update_system_metrics()
        
        # Step 3: Retrieve metrics via API
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        assert response.status_code == 200
        
        # Step 4: Validate complete metrics payload
        content = response.text
        
        # Verify all types of metrics are present
        assert "http_requests_total" in content
        assert "security_events_total" in content
        assert "ml_model_accuracy" in content
        assert "cache_operations_total" in content
        assert "system_cpu_usage_percent" in content
        
        # Step 5: Verify metrics are in valid Prometheus format
        lines = content.strip().split('\n')
        help_lines = [l for l in lines if l.startswith('# HELP')]
        type_lines = [l for l in lines if l.startswith('# TYPE')]
        data_lines = [l for l in lines if not l.startswith('#') and l.strip()]
        
        assert len(help_lines) > 0
        assert len(type_lines) > 0
        assert len(data_lines) > 0

    def test_monitoring_system_reliability(self, client, auth_headers):
        """Test monitoring system reliability under various conditions."""
        # Test that metrics collection doesn't fail with edge cases
        test_scenarios = [
            ("very-long-endpoint-name-" + "x" * 100, 200, 0.1),
            ("", 404, 0.05),  # Empty endpoint
            ("/api/unicode-テスト", 200, 0.2),  # Unicode in endpoint
            ("/api/special!@#$%^&*()", 400, 0.1),  # Special characters
        ]
        
        for endpoint, status, duration in test_scenarios:
            try:
                record_request("GET", endpoint, status, duration)
            except Exception as e:
                pytest.fail(f"Metrics recording failed for endpoint '{endpoint}': {e}")
        
        # Should still be able to get metrics
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        assert response.status_code == 200
        
        # Metrics should contain recorded data
        content = response.text
        assert "http_requests_total" in content

    def test_high_throughput_metrics_collection(self, client, auth_headers):
        """Test metrics collection under high throughput."""
        # Generate a large number of metrics quickly
        for i in range(1000):
            record_request("GET", f"/api/endpoint{i % 10}", 200, 0.001)
            if i % 100 == 0:
                record_security_event("bulk_test")
        
        # System should handle the load and still return metrics
        response = client.get("/api/metrics/prometheus", headers=auth_headers)
        assert response.status_code == 200
        
        content = response.text
        # Should have aggregated the requests properly
        assert "http_requests_total" in content
        assert "security_events_total" in content
        
        # Response should be reasonably sized (not excessively large)
        assert len(content) < 1_000_000  # Less than 1MB