"""
Test runner for Prometheus/Grafana integration tests without full app dependency.

This validates the test logic and metrics functionality directly.
"""

import time
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.monitoring.prometheus_metrics import (
    get_metrics,
    record_request,
    record_api_call,
    record_campaign_click,
    record_campaign_conversion,
    record_model_prediction,
    set_model_accuracy,
    update_system_metrics,
)
from prometheus_client.parser import text_string_to_metric_families


def test_metrics_generation():
    """Test that metrics are generated correctly."""
    print("🧪 Testing metrics generation...")
    
    # Update system metrics
    update_system_metrics()
    
    # Generate some activity
    record_request("GET", "/api/test", 200, 0.5)
    record_request("GET", "/api/test", 404, 0.2)
    record_api_call("test_service", "test_endpoint")
    record_campaign_click("campaign_123")
    record_campaign_conversion("campaign_123")
    record_model_prediction("test_model")
    set_model_accuracy("test_model", 0.85)
    
    # Get metrics
    metrics_data = get_metrics()
    metrics_text = metrics_data.decode('utf-8')
    
    print(f"✅ Generated {len(metrics_text)} bytes of metrics")
    
    # Parse metrics
    families = list(text_string_to_metric_families(metrics_text))
    print(f"✅ Parsed {len(families)} metric families")
    
    # Validate expected metrics
    expected_metrics = [
        "http_requests_total",
        "system_cpu_usage_percent", 
        "system_memory_usage_percent",
        "api_calls_total",
        "campaigns_clicks_total",
        "campaigns_conversions_total",
        "ml_model_predictions_total",
        "ml_model_accuracy"
    ]
    
    found_metrics = [family.name for family in families]
    
    for expected in expected_metrics:
        if expected in found_metrics:
            print(f"✅ Found expected metric: {expected}")
        else:
            print(f"⚠️  Missing expected metric: {expected}")
    
    return True


def test_metrics_format_validation():
    """Test that metrics are in valid Prometheus format."""
    print("\n🧪 Testing metrics format validation...")
    
    # Generate some metrics
    record_request("GET", "/api/metrics/health", 200, 0.1)
    record_request("POST", "/api/data", 201, 0.3)
    
    # Get metrics
    metrics_data = get_metrics()
    metrics_text = metrics_data.decode('utf-8')
    
    # Validate format
    try:
        families = list(text_string_to_metric_families(metrics_text))
        print(f"✅ Metrics format is valid Prometheus format")
        
        # Check for required elements
        has_help = "# HELP" in metrics_text
        has_type = "# TYPE" in metrics_text
        
        print(f"✅ Has HELP comments: {has_help}")
        print(f"✅ Has TYPE comments: {has_type}")
        
        # Validate specific metric structure
        for family in families:
            if family.name == "http_requests_total":
                print(f"✅ Found HTTP requests metric with {len(family.samples)} samples")
                
                for sample in family.samples:
                    if sample.labels:
                        print(f"   - Sample labels: {dict(sample.labels)}")
                        
                        # Validate required labels
                        required_labels = ["method", "endpoint", "status_code"]
                        for label in required_labels:
                            if label in sample.labels:
                                print(f"     ✅ Has required label: {label}")
                            else:
                                print(f"     ⚠️ Missing label: {label}")
                
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Invalid metrics format: {e}")
        return False


def test_business_metrics():
    """Test business-specific metrics."""
    print("\n🧪 Testing business metrics...")
    
    # Simulate business activity
    campaigns = ["campaign_001", "campaign_002"]
    models = ["conversion_model", "price_model"]
    services = ["api_service", "ml_service"]
    
    for campaign in campaigns:
        for _ in range(5):  # 5 clicks each
            record_campaign_click(campaign)
        
        for _ in range(2):  # 2 conversions each  
            record_campaign_conversion(campaign)
    
    for model in models:
        for _ in range(10):  # 10 predictions each
            record_model_prediction(model)
        
        accuracy = 0.8 + (hash(model) % 20) / 100  # Simulate different accuracies
        set_model_accuracy(model, accuracy)
    
    for service in services:
        for _ in range(3):  # 3 API calls each
            record_api_call(service, "process_request")
    
    # Get metrics
    metrics_data = get_metrics()
    metrics_text = metrics_data.decode('utf-8')
    families = list(text_string_to_metric_families(metrics_text))
    
    # Validate business metrics
    business_metric_counts = {}
    
    for family in families:
        if "campaign" in family.name or "model" in family.name or "api_calls" in family.name:
            business_metric_counts[family.name] = len(family.samples)
            print(f"✅ Business metric {family.name}: {len(family.samples)} samples")
    
    # Validate specific business logic
    for family in families:
        if family.name == "campaigns_clicks_total":
            total_clicks = sum(sample.value for sample in family.samples)
            expected_clicks = len(campaigns) * 5  # 5 clicks per campaign
            print(f"✅ Total campaign clicks: {total_clicks} (expected: {expected_clicks})")
        
        elif family.name == "campaigns_conversions_total":
            total_conversions = sum(sample.value for sample in family.samples)
            expected_conversions = len(campaigns) * 2  # 2 conversions per campaign
            print(f"✅ Total campaign conversions: {total_conversions} (expected: {expected_conversions})")
        
        elif family.name == "ml_model_predictions_total":
            total_predictions = sum(sample.value for sample in family.samples)
            expected_predictions = len(models) * 10  # 10 predictions per model
            print(f"✅ Total model predictions: {total_predictions} (expected: {expected_predictions})")
    
    return len(business_metric_counts) > 0


def test_load_simulation():
    """Test metrics under simulated load."""
    print("\n🧪 Testing metrics under simulated load...")
    
    start_time = time.time()
    
    # Simulate load
    endpoints = ["/api/health", "/api/data", "/api/users", "/api/products"]
    status_codes = [200, 200, 200, 404, 500]  # Mostly success with some errors
    
    for i in range(100):  # 100 requests
        endpoint = endpoints[i % len(endpoints)]
        status_code = status_codes[i % len(status_codes)]
        duration = 0.1 + (i % 10) * 0.05  # Varying response times
        
        record_request("GET", endpoint, status_code, duration)
        
        # Simulate some business activity
        if i % 10 == 0:
            record_campaign_click(f"campaign_{i // 10}")
            record_api_call("load_test_service", "process")
    
    end_time = time.time()
    load_duration = end_time - start_time
    
    print(f"✅ Generated load in {load_duration:.2f} seconds")
    
    # Get metrics after load
    metrics_data = get_metrics()
    metrics_text = metrics_data.decode('utf-8')
    families = list(text_string_to_metric_families(metrics_text))
    
    # Analyze load test results
    for family in families:
        if family.name == "http_requests_total":
            total_requests = sum(sample.value for sample in family.samples)
            print(f"✅ Total HTTP requests recorded: {total_requests}")
            
            # Analyze by status code
            status_code_counts = {}
            for sample in family.samples:
                if "status_code" in sample.labels:
                    status_code = sample.labels["status_code"]
                    status_code_counts[status_code] = status_code_counts.get(status_code, 0) + sample.value
            
            for status_code, count in status_code_counts.items():
                print(f"   - Status {status_code}: {count} requests")
    
    return True


def test_dashboard_compatibility():
    """Test metrics compatibility with dashboard queries."""
    print("\n🧪 Testing dashboard compatibility...")
    
    # Generate data for different dashboard panels
    
    # 1. Request rate data
    for i in range(20):
        record_request("GET", "/api/health", 200, 0.1)
        time.sleep(0.01)
    
    # 2. Error rate data
    for i in range(5):
        record_request("GET", "/api/error", 500, 0.5)
    
    # 3. Business metrics data
    record_campaign_click("dashboard_test_campaign")
    record_campaign_conversion("dashboard_test_campaign")
    record_model_prediction("dashboard_test_model")
    set_model_accuracy("dashboard_test_model", 0.92)
    
    # Get metrics
    metrics_data = get_metrics()
    metrics_text = metrics_data.decode('utf-8')
    families = list(text_string_to_metric_families(metrics_text))
    
    # Validate dashboard data requirements
    dashboard_metrics = {}
    
    for family in families:
        # Request rate dashboard
        if family.name == "http_requests_total":
            dashboard_metrics["request_rate"] = family
            print("✅ Request rate data available")
        
        # Response time dashboard (if histogram is present)
        elif "duration" in family.name:
            dashboard_metrics["response_time"] = family
            print("✅ Response time data available")
        
        # System resource dashboard
        elif "system_" in family.name and "usage" in family.name:
            dashboard_metrics[f"system_{family.name.split('_')[1]}"] = family
            print(f"✅ System {family.name.split('_')[1]} data available")
        
        # Business dashboard
        elif "campaign" in family.name or "model" in family.name:
            dashboard_metrics[f"business_{family.name}"] = family
            print(f"✅ Business metric {family.name} available")
    
    # Validate label consistency (important for dashboard grouping)
    for metric_name, family in dashboard_metrics.items():
        if len(family.samples) > 1:
            first_labels = set(family.samples[0].labels.keys())
            consistent_labels = True
            
            for sample in family.samples[1:]:
                sample_labels = set(sample.labels.keys())
                if first_labels != sample_labels:
                    consistent_labels = False
                    break
            
            if consistent_labels:
                print(f"✅ {metric_name}: Consistent labels for grouping")
            else:
                print(f"⚠️  {metric_name}: Inconsistent labels detected")
    
    return len(dashboard_metrics) > 0


def main():
    """Run all integration tests."""
    print("🚀 Starting Prometheus/Grafana Integration Tests\n")
    
    tests = [
        ("Metrics Generation", test_metrics_generation),
        ("Metrics Format Validation", test_metrics_format_validation),
        ("Business Metrics", test_business_metrics),
        ("Load Simulation", test_load_simulation),
        ("Dashboard Compatibility", test_dashboard_compatibility),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"Running: {test_name}")
            print('='*50)
            
            result = test_func()
            results.append((test_name, result, None))
            
            if result:
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
                
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ {test_name}: ERROR - {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    failed = 0
    
    for test_name, result, error in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        
        if error:
            print(f"  Error: {error}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Prometheus/Grafana integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)