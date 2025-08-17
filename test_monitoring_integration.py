#!/usr/bin/env python3
"""
Test script for ML Project Prometheus/Grafana monitoring integration
"""

import sys
import os
import time
import requests
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_metrics_collection():
    """Test basic metrics collection without server"""
    print("🧪 Testing metrics collection...")
    
    try:
        from app.monitoring.prometheus_metrics import (
            get_metrics, record_request, record_security_event,
            set_model_accuracy, record_cache_operation
        )
        
        # Generate some test metrics
        record_request("GET", "/api/test", 200, 0.5)
        record_request("POST", "/api/auth", 401, 0.2)
        record_security_event("failed_login")
        set_model_accuracy("test_model", 0.95)
        record_cache_operation("get", "hit")
        
        # Get metrics
        metrics = get_metrics()
        
        # Validate metrics contain expected data
        metrics_str = metrics.decode()
        checks = [
            'http_requests_total',
            'http_request_duration_seconds',
            'security_events_total',
            'ml_model_accuracy',
            'cache_operations_total',
            'system_cpu_usage_percent',
            'system_memory_usage_percent'
        ]
        
        passed = 0
        for check in checks:
            if check in metrics_str:
                print(f"  ✓ {check}")
                passed += 1
            else:
                print(f"  ❌ {check}")
        
        print(f"  📊 Metrics validation: {passed}/{len(checks)} passed")
        print(f"  📏 Total metrics size: {len(metrics_str)} chars")
        
        return passed == len(checks)
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_configuration():
    """Test configuration and settings"""
    print("⚙️  Testing configuration...")
    
    try:
        from app.settings import settings
        
        # Check required settings
        checks = [
            ("metrics_api_key", len(settings.metrics_api_key) > 10),
            ("enable_metrics_auth", isinstance(settings.enable_metrics_auth, bool)),
            ("secret_key", len(settings.secret_key) > 10),
        ]
        
        passed = 0
        for setting, condition in checks:
            if condition:
                print(f"  ✓ {setting}")
                passed += 1
            else:
                print(f"  ❌ {setting}")
        
        print(f"  ⚙️  Configuration validation: {passed}/{len(checks)} passed")
        return passed == len(checks)
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_file_structure():
    """Test file structure and required files"""
    print("📁 Testing file structure...")
    
    required_files = [
        "monitoring/prometheus.yml",
        "monitoring/alert_rules.yml", 
        "monitoring/grafana/provisioning/datasources/datasources.yml",
        "monitoring/grafana/provisioning/dashboards/dashboards.yml",
        "monitoring/grafana/dashboards/ml-project-system-monitoring.json",
        "monitoring/grafana/dashboards/ml-project-api-performance.json",
        "docker-compose.monitoring.yml",
    ]
    
    passed = 0
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
            passed += 1
        else:
            print(f"  ❌ {file_path}")
    
    print(f"  📁 File structure validation: {passed}/{len(required_files)} passed")
    return passed == len(required_files)

def test_prometheus_config():
    """Test Prometheus configuration"""
    print("🎯 Testing Prometheus configuration...")
    
    try:
        import yaml
        
        # Read prometheus config
        with open("monitoring/prometheus.yml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check backend job configuration
        backend_job = None
        for job in config.get('scrape_configs', []):
            if job.get('job_name') == 'backend':
                backend_job = job
                break
        
        checks = [
            ("backend job exists", backend_job is not None),
            ("correct metrics path", backend_job and backend_job.get('metrics_path') == '/api/metrics/prometheus'),
            ("authorization configured", backend_job and 'authorization' in backend_job),
            ("alert rules file", 'alert_rules.yml' in config.get('rule_files', [])),
        ]
        
        passed = 0
        for desc, condition in checks:
            if condition:
                print(f"  ✓ {desc}")
                passed += 1
            else:
                print(f"  ❌ {desc}")
        
        print(f"  🎯 Prometheus config validation: {passed}/{len(checks)} passed")
        return passed == len(checks)
        
    except ImportError:
        print("  ⚠️  PyYAML not available, skipping detailed config test")
        return True
    except Exception as e:
        print(f"  ❌ Prometheus config error: {e}")
        return False

def test_grafana_dashboards():
    """Test Grafana dashboard configuration"""
    print("📊 Testing Grafana dashboards...")
    
    dashboard_files = [
        "monitoring/grafana/dashboards/ml-project-system-monitoring.json",
        "monitoring/grafana/dashboards/ml-project-api-performance.json"
    ]
    
    passed = 0
    total_panels = 0
    
    for dashboard_file in dashboard_files:
        try:
            with open(dashboard_file, 'r') as f:
                dashboard = json.load(f)
            
            title = dashboard.get('title', 'Unknown')
            panels = dashboard.get('panels', [])
            total_panels += len(panels)
            
            print(f"  ✓ {title}: {len(panels)} panels")
            passed += 1
            
        except Exception as e:
            print(f"  ❌ Error loading {dashboard_file}: {e}")
    
    print(f"  📊 Dashboard validation: {passed}/{len(dashboard_files)} dashboards, {total_panels} total panels")
    return passed == len(dashboard_files)

def main():
    """Run all tests"""
    print("🚀 ML Project Monitoring Integration Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("File Structure", test_file_structure), 
        ("Metrics Collection", test_metrics_collection),
        ("Prometheus Config", test_prometheus_config),
        ("Grafana Dashboards", test_grafana_dashboards),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed_count = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed_count += 1
    
    print(f"\n🎯 Overall: {passed_count}/{len(tests)} tests passed")
    
    if passed_count == len(tests):
        print("🎉 All tests passed! Monitoring system is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())