#!/usr/bin/env python3
"""
Demo script to generate sample metrics for ML Project monitoring demonstration
"""

import sys
import time
import random
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def simulate_api_traffic():
    """Simulate realistic API traffic patterns"""
    from app.monitoring.prometheus_metrics import (
        record_request, record_user_login, record_api_call,
        record_campaign_click, record_campaign_conversion,
        record_model_prediction, set_model_accuracy,
        record_security_event, record_cache_operation,
        active_connections, campaigns_active
    )
    
    print("🎭 Generating sample metrics for demonstration...")
    
    # API endpoints to simulate
    endpoints = [
        ("/api/auth/login", "POST", [200, 401]),
        ("/api/products", "GET", [200, 404]),
        ("/api/campaigns", "GET", [200]),
        ("/api/ml/predict", "POST", [200, 500]),
        ("/api/metrics/health", "GET", [200]),
    ]
    
    # Simulate traffic over time
    for i in range(50):
        # Random API calls
        endpoint, method, status_codes = random.choice(endpoints)
        status = random.choice(status_codes)
        duration = random.uniform(0.1, 2.0) if status == 200 else random.uniform(2.0, 5.0)
        
        record_request(method, endpoint, status, duration)
        
        # User logins
        if endpoint == "/api/auth/login":
            record_user_login(status == 200)
            if status == 401:
                record_security_event("failed_login")
        
        # API service calls
        if status == 200:
            service = endpoint.split('/')[2] if len(endpoint.split('/')) > 2 else "api"
            record_api_call(service, endpoint)
        
        # Campaign interactions
        if random.random() < 0.3:
            campaign_id = f"campaign_{random.randint(1, 5)}"
            record_campaign_click(campaign_id)
            if random.random() < 0.1:  # 10% conversion rate
                record_campaign_conversion(campaign_id)
        
        # ML model predictions
        if random.random() < 0.2:
            model_name = random.choice(["recommendation_engine", "price_optimizer", "trend_analyzer"])
            record_model_prediction(model_name)
        
        # Cache operations
        if random.random() < 0.4:
            operation = random.choice(["get", "set", "delete"])
            result = "hit" if operation == "get" and random.random() < 0.8 else "miss"
            record_cache_operation(operation, result)
        
        # Set some gauge values
        active_connections.set(random.randint(10, 100))
        campaigns_active.set(random.randint(5, 20))
        
        if i % 10 == 0:
            print(f"  📊 Generated {i} metric events...")
        
        # Small delay to spread metrics over time
        time.sleep(0.1)
    
    # Set model accuracies
    set_model_accuracy("recommendation_engine", random.uniform(0.85, 0.95))
    set_model_accuracy("price_optimizer", random.uniform(0.80, 0.90))
    set_model_accuracy("trend_analyzer", random.uniform(0.75, 0.85))
    
    print("  ✅ Sample metrics generation completed!")

def display_metrics_summary():
    """Display a summary of generated metrics"""
    from app.monitoring.prometheus_metrics import get_metrics
    
    metrics = get_metrics().decode()
    
    # Count different metric types
    metric_counts = {}
    for line in metrics.split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        
        metric_name = line.split(' ')[0].split('{')[0]
        if metric_name:
            metric_counts[metric_name] = metric_counts.get(metric_name, 0) + 1
    
    print("\n📈 Generated Metrics Summary:")
    print("-" * 40)
    
    categories = {
        "HTTP Requests": ["http_requests_total", "http_request_duration_seconds"],
        "System": ["system_cpu_usage_percent", "system_memory_usage_percent", "system_disk_usage_percent"],
        "Business": ["user_logins_total", "campaigns_clicks_total", "campaigns_conversions_total"],
        "ML Models": ["ml_model_predictions_total", "ml_model_accuracy"],
        "Security": ["security_events_total", "failed_auth_attempts_total"],
        "Infrastructure": ["active_connections_total", "campaigns_active_total", "cache_operations_total"]
    }
    
    for category, metrics_list in categories.items():
        print(f"\n{category}:")
        for metric in metrics_list:
            count = sum(1 for m in metric_counts.keys() if m.startswith(metric))
            if count > 0:
                print(f"  ✓ {metric}: {count} series")
            else:
                print(f"  - {metric}: No data")
    
    print(f"\n📊 Total metrics: {len(metric_counts)} unique series")
    print(f"📏 Metrics payload size: {len(metrics)} chars")

def main():
    """Main demo function"""
    print("🎪 ML Project Monitoring Demo")
    print("=" * 40)
    
    try:
        simulate_api_traffic()
        display_metrics_summary()
        
        print("\n🎯 Demo complete! You can now:")
        print("  1. Start the services: docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d")
        print("  2. Access Grafana: http://localhost:3001 (admin/admin123)")
        print("  3. View dashboards: Dashboards → ML Project")
        print("  4. Check Prometheus: http://localhost:9090")
        print("  5. Test metrics endpoint with auth:")
        print("     curl -H 'Authorization: Bearer your-key' http://localhost:8000/api/metrics/prometheus")
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("💡 Make sure to install dependencies: pip install -r backend/requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())