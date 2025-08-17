#!/usr/bin/env python3
"""
Simplified test runner for Prometheus/Grafana integration tests
This script runs automated tests for monitoring integration without requiring a full FastAPI server.
"""

import sys
import os
import time
import requests
import threading
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def mock_external_dependencies():
    """Mock external dependencies that might not be available in test environment."""
    # Mock Loki logging if not available
    try:
        import logging_loki
    except ImportError:
        sys.modules['logging_loki'] = MagicMock()
    
    # Mock psutil if specific functions are not available
    try:
        import psutil
        # Test if we can access all needed functions
        psutil.cpu_percent()
        psutil.virtual_memory()
        psutil.disk_usage('/')
    except (ImportError, AttributeError, OSError):
        psutil_mock = MagicMock()
        psutil_mock.cpu_percent.return_value = 50.0
        psutil_mock.virtual_memory.return_value.percent = 60.0
        psutil_mock.disk_usage.return_value.total = 1000000000
        psutil_mock.disk_usage.return_value.used = 500000000
        sys.modules['psutil'] = psutil_mock


class PrometheusMetricsTestSuite:
    """Test suite for Prometheus metrics functionality."""
    
    def __init__(self):
        mock_external_dependencies()
        self.test_results = []
    
    def log_test_result(self, test_name, passed, message=""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append((test_name, passed, message))
    
    def test_metrics_collection_basic(self):
        """Test basic metrics collection functionality."""
        print("🧪 Testing basic metrics collection...")
        
        try:
            from app.monitoring.prometheus_metrics import (
                get_metrics, record_request, record_security_event,
                set_model_accuracy, record_cache_operation
            )
            
            # Test metrics generation
            record_request("GET", "/api/test", 200, 0.5)
            record_security_event("test_event")
            set_model_accuracy("test_model", 0.95)
            record_cache_operation("get", "hit")
            
            # Get metrics
            metrics = get_metrics()
            metrics_str = metrics.decode() if isinstance(metrics, bytes) else str(metrics)
            
            # Validate expected metrics exist
            expected_metrics = [
                'http_requests_total',
                'security_events_total',
                'ml_model_accuracy',
                'cache_operations_total'
            ]
            
            all_present = True
            for metric in expected_metrics:
                if metric not in metrics_str:
                    self.log_test_result(f"Metric {metric} present", False)
                    all_present = False
                else:
                    self.log_test_result(f"Metric {metric} present", True)
            
            self.log_test_result("Basic metrics collection", all_present, f"Generated {len(metrics_str)} chars of metrics")
            return all_present
            
        except Exception as e:
            self.log_test_result("Basic metrics collection", False, f"Error: {e}")
            return False
    
    def test_prometheus_format_validation(self):
        """Test Prometheus format validation."""
        print("📊 Testing Prometheus format validation...")
        
        try:
            from app.monitoring.prometheus_metrics import get_metrics, record_request
            
            # Generate some test data
            record_request("GET", "/api/format-test", 200, 0.1)
            
            metrics = get_metrics()
            metrics_str = metrics.decode() if isinstance(metrics, bytes) else str(metrics)
            
            # Check Prometheus format requirements
            lines = metrics_str.strip().split('\n')
            help_lines = [line for line in lines if line.startswith('# HELP')]
            type_lines = [line for line in lines if line.startswith('# TYPE')]
            metric_lines = [line for line in lines if not line.startswith('#') and line.strip()]
            
            format_valid = len(help_lines) > 0 and len(type_lines) > 0 and len(metric_lines) > 0
            self.log_test_result("Prometheus format structure", format_valid)
            
            # Test metric naming conventions
            naming_valid = True
            for line in metric_lines:
                if line.strip():
                    # Basic check: should have metric name and value
                    parts = line.split()
                    if len(parts) < 2:
                        naming_valid = False
                        break
                    try:
                        float(parts[-1])  # Last part should be numeric
                    except ValueError:
                        naming_valid = False
                        break
            
            self.log_test_result("Metric naming conventions", naming_valid)
            
            return format_valid and naming_valid
            
        except Exception as e:
            self.log_test_result("Prometheus format validation", False, f"Error: {e}")
            return False
    
    def test_custom_metrics_validation(self):
        """Test custom metrics validation."""
        print("🎯 Testing custom metrics validation...")
        
        try:
            from app.monitoring.prometheus_metrics import (
                record_request, record_security_event, set_model_accuracy,
                record_cache_operation, get_metrics
            )
            
            # Test different types of custom metrics
            test_cases = [
                ("HTTP requests", lambda: record_request("POST", "/api/custom", 201, 0.3)),
                ("Security events", lambda: record_security_event("custom_security_event")),
                ("Model accuracy", lambda: set_model_accuracy("custom_model", 0.88)),
                ("Cache operations", lambda: record_cache_operation("set", "success")),
            ]
            
            all_passed = True
            for test_name, test_func in test_cases:
                try:
                    test_func()
                    self.log_test_result(f"Custom {test_name.lower()}", True)
                except Exception as e:
                    self.log_test_result(f"Custom {test_name.lower()}", False, str(e))
                    all_passed = False
            
            # Verify all metrics are captured
            metrics = get_metrics().decode()
            
            # Check for custom values in metrics
            custom_checks = [
                ('endpoint="/api/custom"' in metrics, "Custom endpoint recorded"),
                ('custom_security_event' in metrics, "Custom security event recorded"),
                ('custom_model' in metrics, "Custom model accuracy recorded"),
                ('operation="set"' in metrics, "Custom cache operation recorded"),
            ]
            
            for check, description in custom_checks:
                self.log_test_result(description, check)
                if not check:
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test_result("Custom metrics validation", False, f"Error: {e}")
            return False
    
    def test_error_and_latency_scenarios(self):
        """Test error and latency scenario handling."""
        print("⚠️  Testing error and latency scenarios...")
        
        try:
            from app.monitoring.prometheus_metrics import record_request, get_metrics, record_error
            
            # Test error scenarios
            error_scenarios = [
                ("GET", "/api/error-test", 500, 0.1),  # Server error
                ("POST", "/api/error-test", 404, 0.05), # Not found
                ("PUT", "/api/error-test", 403, 0.08),  # Forbidden
                ("DELETE", "/api/error-test", 429, 0.02), # Rate limited
            ]
            
            for method, endpoint, status, duration in error_scenarios:
                record_request(method, endpoint, status, duration)
            
            # Test application errors
            app_errors = ["database_error", "external_api_timeout", "memory_error"]
            for error_type in app_errors:
                record_error(error_type)
            
            # Test high latency scenarios
            latency_scenarios = [
                ("GET", "/api/slow", 200, 2.5),   # High latency success
                ("GET", "/api/slow", 504, 5.0),   # Timeout
                ("POST", "/api/slow", 200, 3.2),  # Slow POST
            ]
            
            for method, endpoint, status, duration in latency_scenarios:
                record_request(method, endpoint, status, duration)
            
            # Validate metrics capture errors and latency
            metrics = get_metrics().decode()
            
            error_checks = [
                ('status_code="500"' in metrics, "500 errors recorded"),
                ('status_code="404"' in metrics, "404 errors recorded"),
                ('status_code="429"' in metrics, "Rate limit errors recorded"),
                ('status_code="504"' in metrics, "Timeout errors recorded"),
                ('application_errors_total' in metrics, "Application errors recorded"),
                ('http_request_duration_seconds' in metrics, "Latency metrics recorded"),
            ]
            
            all_passed = True
            for check, description in error_checks:
                result = check
                self.log_test_result(description, result)
                if not result:
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test_result("Error and latency scenarios", False, f"Error: {e}")
            return False
    
    def test_metrics_authentication_logic(self):
        """Test metrics authentication logic (without FastAPI server)."""
        print("🔒 Testing metrics authentication logic...")
        
        try:
            from app.settings import settings
            from app.routers.metrics import verify_metrics_auth
            from fastapi.security import HTTPAuthorizationCredentials
            from fastapi import HTTPException
            
            # Test authentication enabled scenario
            original_auth_setting = settings.enable_metrics_auth
            settings.enable_metrics_auth = True
            
            # Test valid token
            try:
                valid_creds = HTTPAuthorizationCredentials(
                    scheme="Bearer", 
                    credentials=settings.metrics_api_key
                )
                result = verify_metrics_auth(valid_creds)
                self.log_test_result("Valid token accepted", result == True)
            except Exception as e:
                self.log_test_result("Valid token accepted", False, str(e))
            
            # Test invalid token
            try:
                invalid_creds = HTTPAuthorizationCredentials(
                    scheme="Bearer", 
                    credentials="invalid-token"
                )
                verify_metrics_auth(invalid_creds)
                self.log_test_result("Invalid token rejected", False, "Should have raised HTTPException")
            except HTTPException:
                self.log_test_result("Invalid token rejected", True)
            except Exception as e:
                self.log_test_result("Invalid token rejected", False, f"Wrong exception type: {e}")
            
            # Test no credentials
            try:
                verify_metrics_auth(None)
                self.log_test_result("No credentials rejected", False, "Should have raised HTTPException")
            except HTTPException:
                self.log_test_result("No credentials rejected", True)
            except Exception as e:
                self.log_test_result("No credentials rejected", False, f"Wrong exception type: {e}")
            
            # Test authentication disabled scenario
            settings.enable_metrics_auth = False
            try:
                result = verify_metrics_auth(None)
                self.log_test_result("Auth disabled bypasses check", result == True)
            except Exception as e:
                self.log_test_result("Auth disabled bypasses check", False, str(e))
            
            # Restore original setting
            settings.enable_metrics_auth = original_auth_setting
            
            return True
            
        except Exception as e:
            self.log_test_result("Metrics authentication logic", False, f"Error: {e}")
            return False
    
    def test_system_metrics_collection(self):
        """Test system metrics collection."""
        print("💻 Testing system metrics collection...")
        
        try:
            from app.monitoring.prometheus_metrics import update_system_metrics, get_metrics
            
            # Update system metrics
            update_system_metrics()
            
            # Get metrics and check for system metrics
            metrics = get_metrics().decode()
            
            system_metrics_checks = [
                ('system_cpu_usage_percent' in metrics, "CPU usage metric"),
                ('system_memory_usage_percent' in metrics, "Memory usage metric"),
                ('system_disk_usage_percent' in metrics, "Disk usage metric"),
            ]
            
            all_passed = True
            for check, description in system_metrics_checks:
                self.log_test_result(description, check)
                if not check:
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test_result("System metrics collection", False, f"Error: {e}")
            return False
    
    def test_concurrent_metrics_collection(self):
        """Test concurrent metrics collection."""
        print("🔄 Testing concurrent metrics collection...")
        
        try:
            from app.monitoring.prometheus_metrics import record_request, get_metrics
            import threading
            import time
            
            def record_metrics_worker(worker_id):
                """Worker function to record metrics concurrently."""
                for i in range(20):
                    record_request("GET", f"/api/worker{worker_id}", 200, 0.01)
                    time.sleep(0.001)  # Small delay to simulate real requests
            
            # Start multiple threads
            threads = []
            for worker_id in range(5):
                thread = threading.Thread(target=record_metrics_worker, args=(worker_id,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check that all metrics were recorded
            metrics = get_metrics().decode()
            
            # Should have recorded 20 requests per worker (5 workers = 100 total)
            # Check for presence of worker endpoints
            workers_found = 0
            for worker_id in range(5):
                if f'/api/worker{worker_id}' in metrics:
                    workers_found += 1
            
            self.log_test_result("Concurrent metrics recording", workers_found == 5, 
                               f"Found {workers_found}/5 worker endpoints")
            
            return workers_found == 5
            
        except Exception as e:
            self.log_test_result("Concurrent metrics collection", False, f"Error: {e}")
            return False
    
    def test_metrics_data_persistence(self):
        """Test that metrics data persists across multiple collections."""
        print("💾 Testing metrics data persistence...")
        
        try:
            from app.monitoring.prometheus_metrics import record_request, get_metrics
            
            # Record initial metrics
            record_request("GET", "/api/persistence-test", 200, 0.1)
            first_metrics = get_metrics().decode()
            
            # Record more metrics
            record_request("GET", "/api/persistence-test", 200, 0.1)
            second_metrics = get_metrics().decode()
            
            # Extract counter values
            import re
            pattern = r'http_requests_total\{.*endpoint="/api/persistence-test".*\} (\d+\.?\d*)'
            
            first_match = re.search(pattern, first_metrics)
            second_match = re.search(pattern, second_metrics)
            
            if first_match and second_match:
                first_value = float(first_match.group(1))
                second_value = float(second_match.group(1))
                
                persistence_works = second_value > first_value
                self.log_test_result("Metrics persistence", persistence_works,
                                   f"Counter: {first_value} -> {second_value}")
                return persistence_works
            else:
                self.log_test_result("Metrics persistence", False, "Could not extract counter values")
                return False
            
        except Exception as e:
            self.log_test_result("Metrics data persistence", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Prometheus/Grafana Integration Test Suite")
        print("=" * 60)
        
        test_suites = [
            ("Basic Metrics Collection", self.test_metrics_collection_basic),
            ("Prometheus Format Validation", self.test_prometheus_format_validation),
            ("Custom Metrics Validation", self.test_custom_metrics_validation),
            ("Error and Latency Scenarios", self.test_error_and_latency_scenarios),
            ("Metrics Authentication Logic", self.test_metrics_authentication_logic),
            ("System Metrics Collection", self.test_system_metrics_collection),
            ("Concurrent Metrics Collection", self.test_concurrent_metrics_collection),
            ("Metrics Data Persistence", self.test_metrics_data_persistence),
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
        
        # Detailed test results
        print(f"\n📊 Detailed Results: {sum(1 for _, passed, _ in self.test_results if passed)}/{len(self.test_results)} individual tests passed")
        
        if passed_suites == len(suite_results):
            print("🎉 All test suites passed! Prometheus/Grafana integration is working correctly.")
            return 0
        else:
            print("⚠️  Some test suites failed. Please review the issues above.")
            return 1


def main():
    """Main entry point."""
    try:
        test_suite = PrometheusMetricsTestSuite()
        return test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error during test execution: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())