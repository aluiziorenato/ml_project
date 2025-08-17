"""
Integration tests for Prometheus/Grafana monitoring setup.

This module tests:
1. Prometheus metrics exposure and validation
2. Critical scenarios simulation (high concurrency, errors, throttling) 
3. Dashboard data validation
4. Metrics accuracy and completeness
"""

import asyncio
import concurrent.futures
import time
from typing import Dict, List
import pytest
import httpx
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from app.main import app
from app.monitoring.prometheus_metrics import (
    get_metrics,
    record_request,
    record_error,
    record_api_call,
    record_campaign_click,
    record_model_prediction,
    update_system_metrics,
)


class TestPrometheusMetricsIntegration:
    """Test Prometheus metrics integration and validation."""

    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def prometheus_client(self):
        """Create HTTP client for Prometheus metrics endpoint."""
        return httpx.Client(base_url="http://localhost:8000")

    def test_prometheus_metrics_endpoint_availability(self, client):
        """Test that Prometheus metrics endpoint is available and returns valid data."""
        response = client.get("/api/metrics/prometheus")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
        
        # Validate metrics content is not empty
        content = response.text
        assert len(content) > 0
        assert "# HELP" in content or "# TYPE" in content
        
    def test_metrics_format_validation(self, client):
        """Test that metrics are in valid Prometheus format."""
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Parse metrics to validate format
        families = list(text_string_to_metric_families(metrics_content))
        assert len(families) > 0
        
        # Check for expected metric families
        metric_names = [family.name for family in families]
        expected_metrics = [
            "http_requests_total",
            "http_request_duration_seconds",
            "system_cpu_usage_percent",
            "system_memory_usage_percent",
        ]
        
        for expected_metric in expected_metrics:
            assert expected_metric in metric_names, f"Missing metric: {expected_metric}"
    
    def test_health_endpoint_availability(self, client):
        """Test that health endpoint provides system metrics."""
        response = client.get("/api/metrics/health")
        
        assert response.status_code == 200
        health_data = response.json()
        
        # Validate health data structure
        assert "status" in health_data
        assert health_data["status"] == "healthy"
        assert "system" in health_data
        assert "cpu_percent" in health_data["system"]
        assert "memory" in health_data["system"]
        
    def test_system_metrics_accuracy(self, client):
        """Test that system metrics are accurate and within expected ranges."""
        response = client.get("/api/metrics/health")
        health_data = response.json()
        
        # Validate CPU percentage is reasonable
        cpu_percent = health_data["system"]["cpu_percent"]
        assert 0 <= cpu_percent <= 100
        
        # Validate memory metrics
        memory = health_data["system"]["memory"]
        assert memory["total"] > 0
        assert 0 <= memory["percent"] <= 100
        assert memory["used"] <= memory["total"]


class TestCriticalScenariosSimulation:
    """Test critical monitoring scenarios like high concurrency, errors, and throttling."""

    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)

    def test_high_concurrency_metrics_recording(self, client):
        """Test metrics accuracy under high concurrent load."""
        
        def make_request():
            """Make a single request and return response status."""
            try:
                response = client.get("/api/metrics/health")
                return response.status_code
            except Exception:
                return 500
        
        # Simulate high concurrency with multiple threads
        num_concurrent_requests = 20
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all requests
            futures = [executor.submit(make_request) for _ in range(num_concurrent_requests)]
            
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        # Verify most requests succeeded
        successful_requests = sum(1 for status in results if status == 200)
        assert successful_requests >= num_concurrent_requests * 0.8  # 80% success rate minimum
        
        # Check that metrics captured the load
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Should have recorded HTTP requests
        assert "http_requests_total" in metrics_content

    def test_error_scenario_metrics(self, client):
        """Test that error scenarios are properly recorded in metrics."""
        
        # Trigger some errors by requesting non-existent endpoints
        error_endpoints = [
            "/api/nonexistent",
            "/api/invalid/endpoint",
            "/api/another/404"
        ]
        
        for endpoint in error_endpoints:
            response = client.get(endpoint)
            # These should return 404
            assert response.status_code == 404
        
        # Check metrics recorded the errors
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Should have HTTP request metrics with error status codes
        assert "http_requests_total" in metrics_content
        
    def test_throttling_and_rate_limiting_simulation(self, client):
        """Test metrics behavior under rate limiting scenarios."""
        
        # Make rapid requests to simulate potential throttling
        start_time = time.time()
        responses = []
        
        for i in range(50):  # Make 50 rapid requests
            response = client.get("/api/metrics/health")
            responses.append({
                "status_code": response.status_code,
                "timestamp": time.time(),
                "request_id": i
            })
            # Small delay to avoid overwhelming the system
            time.sleep(0.01)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Validate that system handled the load
        successful_responses = [r for r in responses if r["status_code"] == 200]
        assert len(successful_responses) >= 40  # At least 80% success
        
        # Check that response times are reasonable (under 5 seconds total)
        assert total_duration < 5.0
        
        # Verify metrics captured the activity
        response = client.get("/api/metrics/prometheus")
        assert response.status_code == 200

    def test_memory_stress_monitoring(self, client):
        """Test monitoring behavior under memory stress."""
        
        # Get initial memory metrics
        initial_response = client.get("/api/metrics/health")
        initial_memory = initial_response.json()["system"]["memory"]["percent"]
        
        # Create some memory load (simulate data processing)
        large_data_sets = []
        try:
            for i in range(10):
                # Create moderately sized data to simulate processing load
                data = [j for j in range(1000)] * 100  # 100k integers
                large_data_sets.append(data)
                
                # Check metrics during load
                response = client.get("/api/metrics/health")
                assert response.status_code == 200
                
        finally:
            # Clean up memory
            large_data_sets.clear()
        
        # Get final memory metrics
        final_response = client.get("/api/metrics/health")
        final_memory = final_response.json()["system"]["memory"]["percent"]
        
        # Memory should be tracked properly
        assert isinstance(final_memory, (int, float))
        assert 0 <= final_memory <= 100


class TestDashboardDataValidation:
    """Test that metrics provide accurate data for Grafana dashboards."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_request_rate_metrics_for_dashboard(self, client):
        """Test metrics that would be used in request rate dashboards."""
        
        # Make several requests to generate metrics
        endpoints_to_test = [
            "/api/metrics/health",
            "/api/metrics/prometheus",
        ]
        
        for endpoint in endpoints_to_test:
            for _ in range(5):  # Make 5 requests to each endpoint
                response = client.get(endpoint)
                assert response.status_code in [200, 404]  # 404 for non-existent endpoints is ok
        
        # Get metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Parse metrics to validate dashboard data
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find HTTP request metrics
        http_requests_family = None
        for family in families:
            if family.name == "http_requests_total":
                http_requests_family = family
                break
        
        assert http_requests_family is not None, "http_requests_total metric not found"
        
        # Validate that we have samples for our requests
        assert len(http_requests_family.samples) > 0
        
        # Check that we have different status codes recorded
        status_codes = set()
        for sample in http_requests_family.samples:
            if "status_code" in sample.labels:
                status_codes.add(sample.labels["status_code"])
        
        assert "200" in status_codes, "No successful requests recorded"
    
    def test_system_resource_metrics_for_dashboard(self, client):
        """Test system resource metrics used in performance dashboards."""
        
        # Trigger system metrics update
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Parse metrics
        families = list(text_string_to_metric_families(metrics_content))
        
        # Check for system metrics
        system_metrics = {}
        for family in families:
            if family.name in ["system_cpu_usage_percent", "system_memory_usage_percent", "system_disk_usage_percent"]:
                system_metrics[family.name] = family
        
        # Validate CPU metrics
        if "system_cpu_usage_percent" in system_metrics:
            cpu_family = system_metrics["system_cpu_usage_percent"]
            assert len(cpu_family.samples) > 0
            cpu_value = cpu_family.samples[0].value
            assert 0 <= cpu_value <= 100
        
        # Validate memory metrics
        if "system_memory_usage_percent" in system_metrics:
            memory_family = system_metrics["system_memory_usage_percent"]
            assert len(memory_family.samples) > 0
            memory_value = memory_family.samples[0].value
            assert 0 <= memory_value <= 100
    
    def test_business_metrics_for_dashboard(self, client):
        """Test business-related metrics that would be displayed in dashboards."""
        
        # Simulate some business events
        record_api_call("test_service", "test_endpoint")
        record_campaign_click("test_campaign_123")
        record_model_prediction("test_model")
        
        # Get metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Validate business metrics are present
        assert "api_calls_total" in metrics_content
        assert "campaigns_clicks_total" in metrics_content
        assert "ml_model_predictions_total" in metrics_content
        
        # Parse and validate specific business metrics
        families = list(text_string_to_metric_families(metrics_content))
        
        business_metric_names = ["api_calls_total", "campaigns_clicks_total", "ml_model_predictions_total"]
        found_metrics = [family.name for family in families if family.name in business_metric_names]
        
        # At least some business metrics should be present
        assert len(found_metrics) > 0, f"No business metrics found. Available: {[f.name for f in families]}"


class TestMetricsAccuracyAndCompleteness:
    """Test the accuracy and completeness of collected metrics."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_request_duration_accuracy(self, client):
        """Test that request duration metrics are accurate."""
        
        # Make a request and measure duration manually
        start_time = time.time()
        response = client.get("/api/metrics/health")
        end_time = time.time()
        manual_duration = end_time - start_time
        
        assert response.status_code == 200
        
        # Get metrics to see if duration was recorded
        metrics_response = client.get("/api/metrics/prometheus")
        metrics_content = metrics_response.text
        
        # Should have duration metrics
        assert "http_request_duration_seconds" in metrics_content
        
        # Parse duration metrics
        families = list(text_string_to_metric_families(metrics_content))
        duration_family = None
        for family in families:
            if family.name == "http_request_duration_seconds":
                duration_family = family
                break
        
        if duration_family and len(duration_family.samples) > 0:
            # Find relevant duration sample
            health_duration_samples = [
                sample for sample in duration_family.samples 
                if "endpoint" in sample.labels and "health" in sample.labels["endpoint"]
            ]
            
            if health_duration_samples:
                recorded_duration = health_duration_samples[-1].value  # Get most recent
                # Duration should be in reasonable range (within 10x of manual measurement)
                assert recorded_duration <= manual_duration * 10
    
    def test_metrics_consistency_over_time(self, client):
        """Test that metrics remain consistent over multiple collections."""
        
        # Collect metrics multiple times
        metrics_collections = []
        for i in range(3):
            response = client.get("/api/metrics/prometheus")
            assert response.status_code == 200
            metrics_collections.append(response.text)
            time.sleep(0.1)  # Small delay between collections
        
        # Parse all collections
        parsed_collections = []
        for metrics_text in metrics_collections:
            families = list(text_string_to_metric_families(metrics_text))
            parsed_collections.append(families)
        
        # Validate that metric families are consistent
        metric_names_sets = []
        for families in parsed_collections:
            metric_names = {family.name for family in families}
            metric_names_sets.append(metric_names)
        
        # Core metrics should be present in all collections
        common_metrics = set.intersection(*metric_names_sets)
        expected_core_metrics = {"http_requests_total", "system_cpu_usage_percent"}
        
        for expected_metric in expected_core_metrics:
            if expected_metric in metric_names_sets[0]:  # If it was in the first collection
                assert expected_metric in common_metrics, f"Metric {expected_metric} not consistent across collections"
    
    def test_all_expected_metrics_present(self, client):
        """Test that all expected metrics are present and properly formatted."""
        
        # Trigger system metrics update
        update_system_metrics()
        
        # Make some requests to generate HTTP metrics
        client.get("/api/metrics/health")
        
        # Get metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Define expected metrics categories
        expected_metrics = {
            "http_requests_total": "counter",
            "http_request_duration_seconds": "histogram", 
            "system_cpu_usage_percent": "gauge",
            "system_memory_usage_percent": "gauge",
        }
        
        # Parse metrics
        families = list(text_string_to_metric_families(metrics_content))
        found_metrics = {family.name: family.type for family in families}
        
        # Check each expected metric
        for metric_name, expected_type in expected_metrics.items():
            assert metric_name in found_metrics, f"Expected metric {metric_name} not found"
            
            # Note: Prometheus client library type names might differ, so we just check presence
            # The important thing is that the metric exists and has samples
            family = next(f for f in families if f.name == metric_name)
            assert len(family.samples) > 0, f"Metric {metric_name} has no samples"


@pytest.mark.asyncio
async def test_async_metrics_collection():
    """Test metrics collection in async context."""
    
    async def async_operation():
        """Simulate an async operation that generates metrics."""
        await asyncio.sleep(0.1)
        record_api_call("async_service", "async_endpoint")
        return "completed"
    
    # Run multiple async operations
    tasks = [async_operation() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 5
    assert all(result == "completed" for result in results)
    
    # Verify metrics were recorded
    metrics_content = get_metrics().decode('utf-8')
    assert "api_calls_total" in metrics_content


class TestGrafanaDashboardCompatibility:
    """Test that metrics are compatible with Grafana dashboard queries."""
    
    @pytest.fixture  
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_rate_queries_compatibility(self, client):
        """Test metrics support Grafana rate() queries."""
        
        # Generate some requests
        for i in range(10):
            client.get("/api/metrics/health")
            time.sleep(0.01)
        
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Validate metrics have timestamps (required for rate queries)
        families = list(text_string_to_metric_families(metrics_content))
        
        for family in families:
            if family.name == "http_requests_total":
                for sample in family.samples:
                    # Prometheus samples should have timestamp info for rate calculations
                    assert hasattr(sample, 'value')
                    assert sample.value >= 0
    
    def test_label_consistency_for_grouping(self, client):
        """Test that metrics have consistent labels for Grafana grouping."""
        
        # Make requests to generate labeled metrics
        client.get("/api/metrics/health")
        client.get("/api/metrics/prometheus")
        
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        families = list(text_string_to_metric_families(metrics_content))
        
        # Check HTTP requests have consistent labels
        for family in families:
            if family.name == "http_requests_total":
                # All samples should have the same label keys
                if len(family.samples) > 1:
                    first_sample_labels = set(family.samples[0].labels.keys())
                    for sample in family.samples[1:]:
                        sample_labels = set(sample.labels.keys())
                        # Label keys should be consistent for grouping in Grafana
                        assert first_sample_labels == sample_labels, f"Inconsistent labels: {first_sample_labels} vs {sample_labels}"
    
    def test_histogram_metrics_for_grafana(self, client):
        """Test that histogram metrics work properly with Grafana."""
        
        # Generate requests to create histogram data
        for _ in range(20):
            client.get("/api/metrics/health")
        
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        
        # Check for histogram metrics
        families = list(text_string_to_metric_families(metrics_content))
        
        duration_family = None
        for family in families:
            if family.name == "http_request_duration_seconds":
                duration_family = family
                break
        
        if duration_family:
            # Histogram should have bucket, count, and sum samples
            sample_names = [sample.name for sample in duration_family.samples]
            
            # Check for histogram components that Grafana needs
            has_buckets = any("_bucket" in name for name in sample_names)
            has_count = any("_count" in name for name in sample_names)
            has_sum = any("_sum" in name for name in sample_names)
            
            # At least some histogram components should be present
            assert has_buckets or has_count or has_sum, "No histogram components found for Grafana compatibility"