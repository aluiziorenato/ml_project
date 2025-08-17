#!/usr/bin/env python3
"""
Production Readiness Validation for Prometheus/Grafana Integration
Final validation script to confirm monitoring is production-ready
"""

import sys
import os
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def validate_production_readiness():
    """Validate that monitoring integration is production-ready."""
    print("🔍 Production Readiness Validation")
    print("=" * 50)
    
    validation_results = []
    
    def log_validation(name, passed, message=""):
        status = "✅ READY" if passed else "❌ NOT READY"
        print(f"  {status} {name}")
        if message:
            print(f"    {message}")
        validation_results.append((name, passed))
    
    # 1. Configuration Validation
    print("\n📋 Configuration Validation:")
    try:
        from app.settings import settings
        
        # Check production settings
        secure_key = len(settings.metrics_api_key) >= 32
        log_validation("Secure metrics API key", secure_key, 
                      f"Key length: {len(settings.metrics_api_key)} chars")
        
        auth_enabled = settings.enable_metrics_auth
        log_validation("Authentication enabled", auth_enabled)
        
        # Check if using default keys (security risk)
        using_defaults = (
            "change-this" in settings.metrics_api_key.lower() or
            "change-this" in settings.secret_key.lower()
        )
        log_validation("Non-default security keys", not using_defaults)
        
    except Exception as e:
        log_validation("Configuration validation", False, f"Error: {e}")
    
    # 2. Metrics Functionality
    print("\n📊 Metrics Functionality:")
    try:
        from app.monitoring.prometheus_metrics import (
            get_metrics, record_request, update_system_metrics
        )
        
        # Test basic metrics generation
        record_request("GET", "/api/production-test", 200, 0.1)
        update_system_metrics()
        
        metrics = get_metrics()
        metrics_str = metrics.decode() if isinstance(metrics, bytes) else str(metrics)
        
        has_content = len(metrics_str) > 100
        log_validation("Metrics generation", has_content, 
                      f"Generated {len(metrics_str)} chars")
        
        # Check for essential metrics
        essential_metrics = [
            "http_requests_total", "system_cpu_usage_percent", 
            "system_memory_usage_percent"
        ]
        
        all_essential = all(metric in metrics_str for metric in essential_metrics)
        log_validation("Essential metrics present", all_essential)
        
        # Check Prometheus format
        prometheus_format = "# HELP" in metrics_str and "# TYPE" in metrics_str
        log_validation("Valid Prometheus format", prometheus_format)
        
    except Exception as e:
        log_validation("Metrics functionality", False, f"Error: {e}")
    
    # 3. Endpoint Accessibility
    print("\n🔗 Endpoint Accessibility:")
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routers.metrics import router
        from app.settings import settings
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Test prometheus endpoint
        headers = {"Authorization": f"Bearer {settings.metrics_api_key}"}
        prometheus_response = client.get("/api/metrics/prometheus", headers=headers)
        log_validation("Prometheus endpoint", prometheus_response.status_code == 200)
        
        # Test health endpoint
        health_response = client.get("/api/metrics/health")
        log_validation("Health endpoint", health_response.status_code == 200)
        
        # Test system endpoint
        system_response = client.get("/api/metrics/system")
        log_validation("System endpoint", system_response.status_code == 200)
        
    except Exception as e:
        log_validation("Endpoint accessibility", False, f"Error: {e}")
    
    # 4. Security Validation
    print("\n🔒 Security Validation:")
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routers.metrics import router
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Test that authentication is required
        no_auth_response = client.get("/api/metrics/prometheus")
        auth_required = no_auth_response.status_code in [401, 403]
        log_validation("Authentication required", auth_required)
        
        # Test that invalid tokens are rejected
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        invalid_response = client.get("/api/metrics/prometheus", headers=invalid_headers)
        invalid_rejected = invalid_response.status_code == 403
        log_validation("Invalid tokens rejected", invalid_rejected)
        
    except Exception as e:
        log_validation("Security validation", False, f"Error: {e}")
    
    # 5. Infrastructure Files
    print("\n📁 Infrastructure Files:")
    required_files = [
        ("monitoring/prometheus.yml", "Prometheus configuration"),
        ("monitoring/alert_rules.yml", "Alert rules"),
        ("monitoring/grafana/provisioning/datasources/datasources.yml", "Grafana datasources"),
        ("monitoring/grafana/dashboards/ml-project-system-monitoring.json", "System dashboard"),
        ("monitoring/grafana/dashboards/ml-project-api-performance.json", "API dashboard"),
        ("docker-compose.monitoring.yml", "Monitoring stack"),
    ]
    
    for file_path, description in required_files:
        file_exists = Path(file_path).exists()
        log_validation(description, file_exists, file_path)
    
    # 6. Performance Check
    print("\n⚡ Performance Check:")
    try:
        from app.monitoring.prometheus_metrics import get_metrics, record_request
        
        # Test metrics collection performance
        start_time = time.time()
        for i in range(100):
            record_request("GET", f"/api/perf-test-{i}", 200, 0.01)
        
        collection_time = time.time() - start_time
        fast_collection = collection_time < 0.5
        log_validation("Fast metrics recording", fast_collection, 
                      f"100 metrics in {collection_time:.3f}s")
        
        # Test metrics retrieval performance
        start_time = time.time()
        metrics = get_metrics()
        retrieval_time = time.time() - start_time
        fast_retrieval = retrieval_time < 2.0
        log_validation("Fast metrics retrieval", fast_retrieval, 
                      f"Retrieval in {retrieval_time:.3f}s")
        
    except Exception as e:
        log_validation("Performance check", False, f"Error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Production Readiness Summary:")
    
    passed = sum(1 for _, result in validation_results if result)
    total = len(validation_results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    for name, result in validation_results:
        status = "✅ READY" if result else "❌ NOT READY"
        print(f"  {status} {name}")
    
    print(f"\n🎯 Overall Readiness: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 PRODUCTION READY!")
        print("✨ Prometheus/Grafana monitoring integration is ready for production deployment.")
        print("\n📝 Next Steps:")
        print("  1. Deploy monitoring stack: docker-compose -f docker-compose.monitoring.yml up -d")
        print("  2. Configure production metrics key in environment variables")
        print("  3. Set up alerting rules and notification channels")
        print("  4. Import Grafana dashboards")
        print("  5. Test end-to-end monitoring pipeline")
        return 0
    else:
        print(f"\n⚠️  NOT READY FOR PRODUCTION")
        print(f"   {total - passed} validation(s) failed. Please address the issues above.")
        return 1


def main():
    """Main entry point."""
    try:
        return validate_production_readiness()
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Error during production validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())