#!/usr/bin/env python3
"""
FastAPI Metrics Endpoint Integration Tests
Tests the actual FastAPI endpoints for metrics collection
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import httpx

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


class FastAPIMetricsEndpointTests:
    """Test suite for FastAPI metrics endpoints."""
    
    def __init__(self):
        self.test_results = []
        self.setup_mocks()
    
    def setup_mocks(self):
        """Setup mocks for external dependencies."""
        # Mock logging_loki if not available
        try:
            import logging_loki
        except ImportError:
            sys.modules['logging_loki'] = MagicMock()
    
    def log_test_result(self, test_name, passed, message=""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append((test_name, passed, message))
    
    def test_metrics_endpoint_structure(self):
        """Test that the metrics endpoint can be imported and has correct structure."""
        print("🔧 Testing metrics endpoint structure...")
        
        try:
            from app.routers.metrics import router, verify_metrics_auth
            from app.monitoring.prometheus_metrics import get_metrics
            
            # Check that router has the expected endpoints
            routes = [route.path for route in router.routes]
            expected_endpoints = ['/prometheus', '/health', '/system', '/test-metrics']
            
            all_present = True
            for endpoint in expected_endpoints:
                endpoint_present = any(endpoint in route for route in routes)
                self.log_test_result(f"Endpoint {endpoint} exists", endpoint_present)
                if not endpoint_present:
                    all_present = False
            
            # Test auth function exists and is callable
            auth_callable = callable(verify_metrics_auth)
            self.log_test_result("Auth function callable", auth_callable)
            
            # Test metrics function works
            try:
                metrics = get_metrics()
                metrics_available = len(str(metrics)) > 0
                self.log_test_result("Metrics function works", metrics_available)
            except Exception as e:
                self.log_test_result("Metrics function works", False, str(e))
                metrics_available = False
            
            return all_present and auth_callable and metrics_available
            
        except Exception as e:
            self.log_test_result("Metrics endpoint structure", False, f"Import error: {e}")
            return False
    
    def test_settings_configuration(self):
        """Test that settings are properly configured for metrics."""
        print("⚙️  Testing settings configuration...")
        
        try:
            from app.settings import settings
            
            # Check required settings exist
            settings_checks = [
                (hasattr(settings, 'metrics_api_key'), "metrics_api_key setting exists"),
                (hasattr(settings, 'enable_metrics_auth'), "enable_metrics_auth setting exists"),
                (len(settings.metrics_api_key) > 10, "metrics_api_key has reasonable length"),
                (isinstance(settings.enable_metrics_auth, bool), "enable_metrics_auth is boolean"),
            ]
            
            all_passed = True
            for check, description in settings_checks:
                self.log_test_result(description, check)
                if not check:
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test_result("Settings configuration", False, f"Error: {e}")
            return False
    
    def test_fastapi_app_creation(self):
        """Test that a FastAPI app can be created with the metrics router."""
        print("🚀 Testing FastAPI app creation...")
        
        try:
            from fastapi import FastAPI
            from app.routers.metrics import router
            
            # Create test app
            app = FastAPI(title="Test App")
            app.include_router(router)
            
            # Check that routes were added
            routes = [route.path for route in app.routes]
            metrics_routes = [route for route in routes if '/api/metrics' in route]
            
            app_created = len(metrics_routes) > 0
            self.log_test_result("FastAPI app with metrics router", app_created, 
                               f"Found {len(metrics_routes)} metrics routes")
            
            return app_created
            
        except Exception as e:
            self.log_test_result("FastAPI app creation", False, f"Error: {e}")
            return False
    
    def test_prometheus_metrics_endpoint_functionality(self):
        """Test the prometheus metrics endpoint logic."""
        print("📊 Testing Prometheus metrics endpoint functionality...")
        
        try:
            from fastapi import FastAPI, HTTPException
            from fastapi.testclient import TestClient
            from app.routers.metrics import router
            from app.settings import settings
            
            # Create test app and client
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # Test endpoint without auth (should fail if auth enabled)
            response = client.get("/api/metrics/prometheus")
            
            if settings.enable_metrics_auth:
                auth_required = response.status_code == 401
                self.log_test_result("Auth required when enabled", auth_required)
            else:
                auth_not_required = response.status_code == 200
                self.log_test_result("Auth not required when disabled", auth_not_required)
            
            # Test endpoint with valid auth
            headers = {"Authorization": f"Bearer {settings.metrics_api_key}"}
            auth_response = client.get("/api/metrics/prometheus", headers=headers)
            
            valid_auth_works = auth_response.status_code == 200
            self.log_test_result("Valid auth works", valid_auth_works)
            
            if valid_auth_works:
                # Check content type
                content_type_correct = "text/plain" in auth_response.headers.get("content-type", "")
                self.log_test_result("Correct content type", content_type_correct)
                
                # Check content has metrics
                content = auth_response.text
                has_metrics = "# HELP" in content and "# TYPE" in content
                self.log_test_result("Contains Prometheus metrics", has_metrics)
                
                return valid_auth_works and content_type_correct and has_metrics
            
            return valid_auth_works
            
        except Exception as e:
            self.log_test_result("Prometheus metrics endpoint", False, f"Error: {e}")
            return False
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        print("❤️  Testing health check endpoint...")
        
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from app.routers.metrics import router
            
            # Create test app and client
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # Test health endpoint
            response = client.get("/api/metrics/health")
            
            health_works = response.status_code == 200
            self.log_test_result("Health endpoint responds", health_works)
            
            if health_works:
                data = response.json()
                has_status = "status" in data
                has_timestamp = "timestamp" in data
                status_ok = data.get("status") == "ok"
                
                self.log_test_result("Health response has status", has_status)
                self.log_test_result("Health response has timestamp", has_timestamp)
                self.log_test_result("Health status is ok", status_ok)
                
                return has_status and has_timestamp and status_ok
            
            return health_works
            
        except Exception as e:
            self.log_test_result("Health check endpoint", False, f"Error: {e}")
            return False
    
    def test_system_metrics_endpoint(self):
        """Test the system metrics endpoint."""
        print("💻 Testing system metrics endpoint...")
        
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from app.routers.metrics import router
            
            # Create test app and client
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # Test system metrics endpoint
            response = client.get("/api/metrics/system")
            
            system_works = response.status_code == 200
            self.log_test_result("System metrics endpoint responds", system_works)
            
            if system_works:
                data = response.json()
                expected_keys = ["cpu", "memory", "disk", "network"]
                
                all_keys_present = True
                for key in expected_keys:
                    key_present = key in data
                    self.log_test_result(f"System metrics has {key}", key_present)
                    if not key_present:
                        all_keys_present = False
                
                return all_keys_present
            
            return system_works
            
        except Exception as e:
            self.log_test_result("System metrics endpoint", False, f"Error: {e}")
            return False
    
    def test_test_metrics_endpoint(self):
        """Test the test metrics generation endpoint."""
        print("🧪 Testing test metrics endpoint...")
        
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from app.routers.metrics import router
            
            # Create test app and client
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # Test test metrics endpoint
            response = client.post("/api/metrics/test-metrics")
            
            test_metrics_works = response.status_code == 200
            self.log_test_result("Test metrics endpoint responds", test_metrics_works)
            
            if test_metrics_works:
                data = response.json()
                has_status = data.get("status") == "success"
                has_metrics = "metrics" in data
                
                self.log_test_result("Test metrics status success", has_status)
                self.log_test_result("Test metrics contains data", has_metrics)
                
                if has_metrics:
                    metrics_data = data["metrics"]
                    expected_metrics = ["active_connections", "campaigns_active", "model_accuracies"]
                    
                    all_test_metrics = True
                    for metric in expected_metrics:
                        metric_present = metric in metrics_data
                        self.log_test_result(f"Test metric {metric} present", metric_present)
                        if not metric_present:
                            all_test_metrics = False
                    
                    return has_status and has_metrics and all_test_metrics
                
                return has_status and has_metrics
            
            return test_metrics_works
            
        except Exception as e:
            self.log_test_result("Test metrics endpoint", False, f"Error: {e}")
            return False
    
    def test_invalid_authentication_scenarios(self):
        """Test various invalid authentication scenarios."""
        print("🔒 Testing invalid authentication scenarios...")
        
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from app.routers.metrics import router
            from app.settings import settings
            
            # Only test if auth is enabled
            if not settings.enable_metrics_auth:
                self.log_test_result("Authentication tests", True, "Auth disabled, skipping")
                return True
            
            # Create test app and client
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # Test invalid scenarios
            test_scenarios = [
                ({"Authorization": "Bearer invalid-token"}, "Invalid token"),
                ({"Authorization": "Basic dGVzdDp0ZXN0"}, "Wrong auth type"),
                ({"Authorization": "Bearer"}, "Missing token"),
                ({}, "No auth header"),
            ]
            
            all_rejected = True
            for headers, description in test_scenarios:
                response = client.get("/api/metrics/prometheus", headers=headers)
                rejected = response.status_code in [401, 403]
                self.log_test_result(f"{description} rejected", rejected)
                if not rejected:
                    all_rejected = False
            
            return all_rejected
            
        except Exception as e:
            self.log_test_result("Invalid authentication scenarios", False, f"Error: {e}")
            return False
    
    def test_endpoint_error_handling(self):
        """Test endpoint error handling."""
        print("⚠️  Testing endpoint error handling...")
        
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from app.routers.metrics import router
            
            # Create test app and client
            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)
            
            # Test non-existent endpoint
            response = client.get("/api/metrics/nonexistent")
            not_found = response.status_code == 404
            self.log_test_result("Non-existent endpoint returns 404", not_found)
            
            # Test wrong HTTP method
            wrong_method_response = client.delete("/api/metrics/health")
            wrong_method = wrong_method_response.status_code == 405
            self.log_test_result("Wrong HTTP method returns 405", wrong_method)
            
            return not_found and wrong_method
            
        except Exception as e:
            self.log_test_result("Endpoint error handling", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all FastAPI endpoint tests."""
        print("🚀 FastAPI Metrics Endpoint Integration Tests")
        print("=" * 60)
        
        test_suites = [
            ("Metrics Endpoint Structure", self.test_metrics_endpoint_structure),
            ("Settings Configuration", self.test_settings_configuration),
            ("FastAPI App Creation", self.test_fastapi_app_creation),
            ("Prometheus Metrics Endpoint", self.test_prometheus_metrics_endpoint_functionality),
            ("Health Check Endpoint", self.test_health_check_endpoint),
            ("System Metrics Endpoint", self.test_system_metrics_endpoint),
            ("Test Metrics Endpoint", self.test_test_metrics_endpoint),
            ("Invalid Authentication Scenarios", self.test_invalid_authentication_scenarios),
            ("Endpoint Error Handling", self.test_endpoint_error_handling),
        ]
        
        suite_results = []
        for suite_name, test_func in test_suites:
            print(f"\n{suite_name}:")
            try:
                result = test_func()
                suite_results.append((suite_name, result))
            except Exception as e:
                print(f"  ❌ FAIL {suite_name} - Unexpected error: {e}")
                suite_results.append((suite_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Suite Results Summary:")
        
        passed_suites = 0
        for suite_name, result in suite_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {suite_name}")
            if result:
                passed_suites += 1
        
        print(f"\n🎯 Overall: {passed_suites}/{len(suite_results)} test suites passed")
        print(f"📊 Detailed Results: {sum(1 for _, passed, _ in self.test_results if passed)}/{len(self.test_results)} individual tests passed")
        
        if passed_suites == len(suite_results):
            print("🎉 All FastAPI endpoint tests passed! Metrics endpoints are working correctly.")
            return 0
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
            return 1


def main():
    """Main entry point."""
    try:
        test_suite = FastAPIMetricsEndpointTests()
        return test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error during test execution: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())