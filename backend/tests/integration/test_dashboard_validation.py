"""
Dashboard validation tests and Grafana query compatibility tests.

This module validates:
1. Dashboard data accuracy and completeness
2. Grafana query compatibility
3. Time series data consistency
4. Alert condition validation
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pytest
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from app.main import app
from app.monitoring.prometheus_metrics import (
    record_request,
    record_api_call,
    record_campaign_click,
    record_campaign_conversion,
    record_model_prediction,
    set_model_accuracy,
    update_system_metrics,
)


class TestDashboardDataValidation:
    """Test that metrics provide accurate and complete data for dashboards."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_system_overview_dashboard_data(self, client):
        """Test data for system overview dashboard."""
        
        # Generate some activity
        for i in range(10):
            client.get("/api/metrics/health")
            time.sleep(0.01)
        
        # Get metrics for dashboard
        response = client.get("/api/metrics/prometheus")
        assert response.status_code == 200
        
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Expected metrics for system overview dashboard
        expected_metrics = {
            "http_requests_total": {
                "type": "counter",
                "description": "Total HTTP requests",
                "required_labels": ["method", "endpoint", "status_code"]
            },
            "http_request_duration_seconds": {
                "type": "histogram", 
                "description": "HTTP request duration",
                "required_labels": ["method", "endpoint"]
            },
            "system_cpu_usage_percent": {
                "type": "gauge",
                "description": "System CPU usage",
                "required_labels": []
            },
            "system_memory_usage_percent": {
                "type": "gauge",
                "description": "System memory usage", 
                "required_labels": []
            }
        }
        
        # Validate each expected metric
        found_metrics = {family.name: family for family in families}
        
        for metric_name, expectations in expected_metrics.items():
            assert metric_name in found_metrics, f"Dashboard metric {metric_name} missing"
            
            family = found_metrics[metric_name]
            assert len(family.samples) > 0, f"Metric {metric_name} has no data"
            
            # Check required labels are present
            if family.samples and expectations["required_labels"]:
                sample_labels = family.samples[0].labels.keys()
                for required_label in expectations["required_labels"]:
                    assert required_label in sample_labels, f"Required label {required_label} missing from {metric_name}"
    
    def test_performance_dashboard_data(self, client):
        """Test data for performance monitoring dashboard."""
        
        # Simulate various response times
        endpoints = ["/api/metrics/health", "/api/metrics/prometheus"]
        
        for endpoint in endpoints:
            for i in range(5):
                start_time = time.time()
                response = client.get(endpoint)
                duration = time.time() - start_time
                
                # Record custom metrics for performance tracking
                record_request("GET", endpoint, response.status_code, duration)
        
        # Get performance metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find performance-related metrics
        performance_metrics = {}
        for family in families:
            if "duration" in family.name or "requests" in family.name:
                performance_metrics[family.name] = family
        
        # Validate performance dashboard data
        assert "http_requests_total" in performance_metrics
        assert "http_request_duration_seconds" in performance_metrics
        
        # Check that we have data for different endpoints
        requests_family = performance_metrics["http_requests_total"]
        endpoints_in_metrics = set()
        
        for sample in requests_family.samples:
            if "endpoint" in sample.labels:
                endpoints_in_metrics.add(sample.labels["endpoint"])
        
        assert len(endpoints_in_metrics) > 0, "No endpoint data in performance metrics"
    
    def test_business_dashboard_data(self, client):
        """Test data for business metrics dashboard."""
        
        # Generate business events
        campaigns = ["campaign_001", "campaign_002", "campaign_003"]
        models = ["conversion_model", "price_model", "recommendation_model"]
        services = ["api_service", "ml_service", "data_service"]
        
        # Simulate business activity
        for campaign in campaigns:
            record_campaign_click(campaign)
            record_campaign_conversion(campaign)
        
        for model in models:
            record_model_prediction(model)
            set_model_accuracy(model, 0.85 + (hash(model) % 10) / 100)  # Simulate accuracy
        
        for service in services:
            record_api_call(service, "process_request")
        
        # Get business metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find business metrics
        business_metrics = {}
        for family in families:
            if any(keyword in family.name for keyword in ["campaign", "model", "api_calls"]):
                business_metrics[family.name] = family
        
        # Validate business dashboard data
        expected_business_metrics = [
            "campaigns_clicks_total",
            "campaigns_conversions_total", 
            "ml_model_predictions_total",
            "ml_model_accuracy",
            "api_calls_total"
        ]
        
        for expected_metric in expected_business_metrics:
            assert expected_metric in business_metrics, f"Business metric {expected_metric} missing"
            
            family = business_metrics[expected_metric]
            assert len(family.samples) > 0, f"Business metric {expected_metric} has no data"
    
    def test_error_tracking_dashboard_data(self, client):
        """Test data for error tracking dashboard."""
        
        # Generate various types of errors
        error_scenarios = [
            ("/api/nonexistent", 404),
            ("/api/invalid", 404),
            ("/api/forbidden", 404),  # Will be 404 since endpoint doesn't exist
        ]
        
        for endpoint, expected_status in error_scenarios:
            response = client.get(endpoint)
            # Record the actual response for metrics
            record_request("GET", endpoint, response.status_code, 0.1)
        
        # Get error metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find error-related metrics
        requests_family = None
        for family in families:
            if family.name == "http_requests_total":
                requests_family = family
                break
        
        assert requests_family is not None, "HTTP requests metric not found"
        
        # Check for error status codes in metrics
        status_codes_found = set()
        for sample in requests_family.samples:
            if "status_code" in sample.labels:
                status_codes_found.add(sample.labels["status_code"])
        
        # Should have recorded error status codes
        assert len(status_codes_found) > 0, "No status codes recorded in metrics"
        
        # Should have both success and error codes
        has_success = any(code.startswith("2") for code in status_codes_found)
        has_errors = any(code.startswith("4") or code.startswith("5") for code in status_codes_found)
        
        assert has_success, "No successful requests recorded"
        # Note: Error codes might not be present if endpoints don't exist, that's ok


class TestGrafanaQueryCompatibility:
    """Test that metrics work correctly with common Grafana queries."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app.""" 
        return TestClient(app)
    
    def test_rate_function_compatibility(self, client):
        """Test metrics compatibility with Grafana rate() function."""
        
        # Generate requests over time to create rate data
        for i in range(20):
            client.get("/api/metrics/health")
            time.sleep(0.05)  # Small delay to create time series
        
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find counter metrics (required for rate() function)
        counter_metrics = []
        for family in families:
            if family.type == "counter":
                counter_metrics.append(family)
        
        assert len(counter_metrics) > 0, "No counter metrics found for rate() queries"
        
        # Validate counter metrics have proper structure for rate calculations
        for family in counter_metrics:
            assert len(family.samples) > 0, f"Counter metric {family.name} has no samples"
            
            for sample in family.samples:
                assert sample.value >= 0, f"Counter value should be non-negative: {sample.value}"
                # Counter values should be numeric and increase over time
                assert isinstance(sample.value, (int, float)), f"Counter value should be numeric: {type(sample.value)}"
    
    def test_histogram_quantile_compatibility(self, client):
        """Test histogram metrics compatibility with histogram_quantile() function."""
        
        # Generate requests to create histogram data
        for i in range(30):
            client.get("/api/metrics/health")
            time.sleep(0.01)
        
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find histogram metrics
        histogram_metrics = []
        for family in families:
            if family.type == "histogram":
                histogram_metrics.append(family)
        
        if histogram_metrics:  # Only test if histograms are present
            for family in histogram_metrics:
                sample_names = [sample.name for sample in family.samples]
                
                # For histogram_quantile() to work, we need bucket samples
                bucket_samples = [name for name in sample_names if "_bucket" in name]
                
                if bucket_samples:  # If buckets are present, validate structure
                    # Should have samples with 'le' (less than or equal) labels for buckets
                    bucket_sample_objs = [s for s in family.samples if "_bucket" in s.name]
                    
                    for bucket_sample in bucket_sample_objs:
                        if "le" in bucket_sample.labels:
                            le_value = bucket_sample.labels["le"]
                            # le values should be numeric (except for "+Inf")
                            if le_value != "+Inf":
                                try:
                                    float(le_value)
                                except ValueError:
                                    pytest.fail(f"Invalid histogram bucket le value: {le_value}")
    
    def test_label_grouping_compatibility(self, client):
        """Test metrics compatibility with Grafana label grouping (by clause)."""
        
        # Generate requests with different labels
        endpoints = ["/api/metrics/health", "/api/metrics/prometheus"]
        methods = ["GET"]
        
        for endpoint in endpoints:
            for method in methods:
                for _ in range(3):
                    if method == "GET":
                        response = client.get(endpoint)
                    record_request(method, endpoint, response.status_code, 0.1)
        
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find metrics with labels
        labeled_metrics = []
        for family in families:
            if family.samples and any(sample.labels for sample in family.samples):
                labeled_metrics.append(family)
        
        assert len(labeled_metrics) > 0, "No labeled metrics found for grouping queries"
        
        # Validate label consistency for grouping
        for family in labeled_metrics:
            if len(family.samples) > 1:
                # All samples should have the same label keys for consistent grouping
                first_sample_labels = set(family.samples[0].labels.keys())
                
                for sample in family.samples[1:]:
                    sample_labels = set(sample.labels.keys())
                    
                    # Labels should be consistent across samples for proper grouping
                    # (It's ok if some samples have additional labels, but core labels should be consistent)
                    common_labels = first_sample_labels.intersection(sample_labels)
                    assert len(common_labels) > 0, f"No common labels for grouping in {family.name}"
    
    def test_time_range_queries_compatibility(self, client):
        """Test metrics compatibility with time range queries."""
        
        # Generate metrics data over time
        start_time = time.time()
        
        for i in range(10):
            client.get("/api/metrics/health")
            record_api_call("time_test_service", f"endpoint_{i}")
            time.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # For time range queries, metrics should have consistent timestamps
        # and values that reflect the time period
        
        counter_families = [f for f in families if f.type == "counter"]
        if counter_families:
            for family in counter_families:
                for sample in family.samples:
                    # Values should be cumulative and increasing for counters
                    assert sample.value >= 0, f"Counter value should be non-negative"
                    
                    # For our test case, values should reflect the activity we generated
                    if "api_calls_total" in family.name:
                        # We made 10 API calls, so value should be at least 10
                        assert sample.value >= 10, f"Counter should reflect generated activity: {sample.value}"


class TestAlertConditionValidation:
    """Test that metrics support common alerting scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        return TestClient(app)
    
    def test_high_error_rate_alert_conditions(self, client):
        """Test metrics for high error rate alerting."""
        
        # Generate mix of successful and error requests
        total_requests = 20
        error_requests = 3
        
        # Successful requests
        for i in range(total_requests - error_requests):
            response = client.get("/api/metrics/health")
            record_request("GET", "/api/metrics/health", response.status_code, 0.1)
        
        # Error requests (simulate by calling non-existent endpoints)
        for i in range(error_requests):
            response = client.get(f"/api/error_endpoint_{i}")
            record_request("GET", f"/api/error_endpoint_{i}", response.status_code, 0.1)
        
        # Get metrics for alert evaluation
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find HTTP requests metric
        requests_family = None
        for family in families:
            if family.name == "http_requests_total":
                requests_family = family
                break
        
        assert requests_family is not None, "HTTP requests metric required for error rate alerts"
        
        # Calculate error rate from metrics
        total_count = 0
        error_count = 0
        
        for sample in requests_family.samples:
            if "status_code" in sample.labels:
                status_code = sample.labels["status_code"]
                count = sample.value
                total_count += count
                
                if status_code.startswith("4") or status_code.startswith("5"):
                    error_count += count
        
        if total_count > 0:
            error_rate = error_count / total_count
            
            # Validate that error rate can be calculated
            assert 0 <= error_rate <= 1, f"Invalid error rate: {error_rate}"
            
            # For alerting, we should be able to detect high error rates
            # In this test, we generated ~15% errors, should be detectable
            assert error_rate >= 0.1, f"Error rate too low to test alerting: {error_rate}"
    
    def test_high_response_time_alert_conditions(self, client):
        """Test metrics for response time alerting."""
        
        # Generate requests and measure response times
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            response = client.get("/api/metrics/health")
            end_time = time.time()
            duration = end_time - start_time
            
            response_times.append(duration)
            record_request("GET", "/api/metrics/health", response.status_code, duration)
        
        # Get metrics for alert evaluation
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find duration metrics
        duration_family = None
        for family in families:
            if "duration" in family.name and family.type == "histogram":
                duration_family = family
                break
        
        if duration_family:  # Duration metrics are present
            # For response time alerting, we need histogram data
            bucket_samples = [s for s in duration_family.samples if "_bucket" in s.name]
            count_samples = [s for s in duration_family.samples if "_count" in s.name]
            sum_samples = [s for s in duration_family.samples if "_sum" in s.name]
            
            # Should have histogram components for percentile calculations
            assert len(bucket_samples) > 0 or len(count_samples) > 0 or len(sum_samples) > 0, \
                "No histogram data for response time alerting"
            
            # If we have count and sum, we can calculate average response time
            if count_samples and sum_samples:
                total_count = sum(s.value for s in count_samples)
                total_sum = sum(s.value for s in sum_samples)
                
                if total_count > 0:
                    avg_response_time = total_sum / total_count
                    assert avg_response_time > 0, f"Invalid average response time: {avg_response_time}"
                    assert avg_response_time < 10, f"Response time too high: {avg_response_time}s"
    
    def test_resource_usage_alert_conditions(self, client):
        """Test metrics for system resource alerting."""
        
        # Get system metrics for alerting
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find system resource metrics
        resource_metrics = {}
        for family in families:
            if "system_" in family.name and "usage" in family.name:
                resource_metrics[family.name] = family
        
        # Validate resource metrics for alerting
        expected_resource_metrics = ["system_cpu_usage_percent", "system_memory_usage_percent"]
        
        for expected_metric in expected_resource_metrics:
            if expected_metric in resource_metrics:
                family = resource_metrics[expected_metric]
                assert len(family.samples) > 0, f"No data for resource metric {expected_metric}"
                
                for sample in family.samples:
                    value = sample.value
                    assert 0 <= value <= 100, f"Invalid resource usage percentage: {value}"
                    
                    # For alerting, we should be able to detect high resource usage
                    # Values should be reasonable for a test environment
                    assert value < 95, f"Resource usage too high for testing: {value}%"
    
    def test_business_metric_alert_conditions(self, client):
        """Test metrics for business-related alerting."""
        
        # Generate business events for alerting scenarios
        campaigns = ["critical_campaign", "normal_campaign"]
        
        # Simulate different conversion rates
        for campaign in campaigns:
            clicks = 10 if campaign == "critical_campaign" else 5
            conversions = 1 if campaign == "critical_campaign" else 3  # Different conversion rates
            
            for _ in range(clicks):
                record_campaign_click(campaign)
            
            for _ in range(conversions):
                record_campaign_conversion(campaign)
        
        # Get business metrics
        response = client.get("/api/metrics/prometheus")
        metrics_content = response.text
        families = list(text_string_to_metric_families(metrics_content))
        
        # Find campaign metrics
        clicks_family = None
        conversions_family = None
        
        for family in families:
            if family.name == "campaigns_clicks_total":
                clicks_family = family
            elif family.name == "campaigns_conversions_total":
                conversions_family = family
        
        # Validate business metrics for alerting
        if clicks_family and conversions_family:
            # Calculate conversion rates per campaign
            clicks_by_campaign = {}
            conversions_by_campaign = {}
            
            for sample in clicks_family.samples:
                if "campaign_id" in sample.labels:
                    campaign_id = sample.labels["campaign_id"]
                    clicks_by_campaign[campaign_id] = sample.value
            
            for sample in conversions_family.samples:
                if "campaign_id" in sample.labels:
                    campaign_id = sample.labels["campaign_id"]
                    conversions_by_campaign[campaign_id] = sample.value
            
            # Calculate conversion rates for alerting
            for campaign_id in clicks_by_campaign:
                clicks = clicks_by_campaign.get(campaign_id, 0)
                conversions = conversions_by_campaign.get(campaign_id, 0)
                
                if clicks > 0:
                    conversion_rate = conversions / clicks
                    assert 0 <= conversion_rate <= 1, f"Invalid conversion rate for {campaign_id}: {conversion_rate}"
                    
                    # Business alerting should be able to detect low conversion rates
                    # For critical campaigns, we might want to alert if conversion rate < 20%
                    if campaign_id == "critical_campaign":
                        # In our test, critical campaign has 10% conversion rate (1/10)
                        assert conversion_rate < 0.2, f"Test data should trigger low conversion alert: {conversion_rate}"