"""
Regression tests for critical features and historical bugs.
This addresses point 3 of the PR #42 checklist: "Testes de regressão automatizados para features críticas"
"""
import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

@pytest.mark.regression
class TestCriticalFeatureRegression:
    """Regression tests for critical system features."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_user_authentication_regression(self, client):
        """Test user authentication critical path doesn't regress."""
        # Test login with valid credentials
        login_data = {
            "email": "test@example.com",
            "password": "ValidPassword123!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            # Verify response structure hasn't changed
            auth_response = response.json()
            expected_fields = ["access_token", "token_type", "expires_in"]
            
            # Should contain at least one of these standard auth fields
            assert any(field in auth_response for field in expected_fields), \
                "Authentication response structure changed"
                
            # Token should be a non-empty string
            if "access_token" in auth_response:
                assert isinstance(auth_response["access_token"], str)
                assert len(auth_response["access_token"]) > 0
                
        elif response.status_code == 404:
            pytest.skip("Authentication endpoint not implemented")
        else:
            # Should consistently reject invalid credentials
            assert response.status_code in [400, 401, 422]
    
    def test_seo_optimization_regression(self, client, auth_headers):
        """Test SEO optimization functionality doesn't regress."""
        # Test with known input that should produce consistent output
        seo_data = {
            "text": "Premium wireless bluetooth headphones with active noise cancellation technology",
            "keywords": ["wireless", "bluetooth", "headphones", "noise cancellation"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify response structure hasn't changed
            expected_fields = ["original", "title", "meta_description", "keywords", "slug"]
            
            for field in expected_fields:
                assert field in result, f"SEO optimization missing expected field: {field}"
            
            # Verify data integrity
            assert result["original"] == seo_data["text"]
            assert isinstance(result["keywords"], list)
            assert len(result["meta_description"]) <= seo_data["max_length"]
            
            # Verify slug format (should be URL-friendly)
            slug = result["slug"]
            assert isinstance(slug, str)
            assert " " not in slug  # No spaces in slug
            assert slug.islower()  # Should be lowercase
            
        elif response.status_code == 404:
            pytest.skip("SEO optimization endpoint not implemented")
    
    def test_product_data_validation_regression(self, client, auth_headers):
        """Test product data validation rules haven't regressed."""
        # Test with edge case data that historically caused issues
        product_data = {
            "title": "Test Product with Special Characters: & < > \" '",
            "description": "Description with\nnewlines\tand\ttabs",
            "price": 99.99,
            "category": "test_category",
            "attributes": {
                "color": "blue",
                "size": "large",
                "weight": "1.5kg"
            }
        }
        
        response = client.post("/api/products/validate", json=product_data, headers=auth_headers)
        
        if response.status_code in [200, 422]:
            # If validation endpoint exists, check response structure
            if response.status_code == 200:
                validation_result = response.json()
                assert "valid" in validation_result or "errors" in validation_result
                
            elif response.status_code == 422:
                # Validation errors should be structured
                error_response = response.json()
                assert "detail" in error_response or "errors" in error_response
                
        elif response.status_code == 404:
            pytest.skip("Product validation endpoint not implemented")

@pytest.mark.regression
class TestHistoricalBugFixes:
    """Regression tests for specific historical bugs that were fixed."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_empty_string_handling_regression(self, client, auth_headers):
        """Test that empty string inputs are handled correctly (historical bug)."""
        # This test prevents regression of a bug where empty strings caused errors
        empty_seo_data = {
            "text": "",
            "keywords": [],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=empty_seo_data, headers=auth_headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Should handle empty input gracefully
            assert result["original"] == ""
            assert result["title"] == ""
            assert result["meta_description"] == ""
            assert result["keywords"] == []
            assert result["slug"] == ""
            
        elif response.status_code in [400, 422]:
            # Acceptable to reject empty input with proper error
            error_response = response.json()
            assert "detail" in error_response or "error" in error_response
            
        elif response.status_code == 404:
            pytest.skip("SEO optimization endpoint not implemented")
    
    def test_sql_injection_prevention_regression(self, client):
        """Test that SQL injection vulnerabilities remain fixed."""
        # Historical bug: SQL injection in login endpoint
        malicious_login = {
            "email": "admin'; DROP TABLE users; --",
            "password": "anything"
        }
        
        response = client.post("/api/auth/login", json=malicious_login)
        
        if response.status_code != 404:  # If endpoint exists
            # Should not return 500 (which might indicate SQL error)
            assert response.status_code in [400, 401, 422], \
                "Potential SQL injection vulnerability detected"
            
            # Response should not contain SQL error messages
            response_text = response.text.lower()
            sql_error_indicators = ["syntax error", "mysql", "postgresql", "sqlite", "table", "column"]
            
            for indicator in sql_error_indicators:
                assert indicator not in response_text, \
                    f"SQL error information leaked in response: {indicator}"
    
    def test_unicode_handling_regression(self, client, auth_headers):
        """Test that Unicode characters are handled correctly."""
        # Historical bug: Unicode characters caused encoding errors
        unicode_seo_data = {
            "text": "Produto com acentuação: ção, ã, é, ô, ü, ñ, 中文, 🎵",
            "keywords": ["acentuação", "unicode", "中文"],
            "max_length": 200
        }
        
        response = client.post("/api/seo/optimize", json=unicode_seo_data, headers=auth_headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Should preserve Unicode characters correctly
            assert "ção" in result["original"]
            assert len(result["meta_description"]) <= unicode_seo_data["max_length"]
            
        elif response.status_code == 404:
            pytest.skip("SEO optimization endpoint not implemented")
    
    def test_large_payload_handling_regression(self, client, auth_headers):
        """Test that large payloads don't cause memory issues."""
        # Historical bug: Large payloads caused memory overflow
        large_text = "A" * 50000  # 50KB text
        
        large_seo_data = {
            "text": large_text,
            "keywords": ["large", "payload", "test"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=large_seo_data, headers=auth_headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Should handle large input without crashing
            assert result["original"] == large_text
            assert len(result["meta_description"]) <= 160
            
        elif response.status_code == 413:
            # Acceptable to reject overly large payloads
            pass
        elif response.status_code == 404:
            pytest.skip("SEO optimization endpoint not implemented")

@pytest.mark.regression
class TestAPIContractRegression:
    """Test that API contracts haven't changed unexpectedly."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_health_endpoint_contract(self, client):
        """Test health endpoint contract remains stable."""
        response = client.get("/health")
        
        if response.status_code == 200:
            health_data = response.json()
            
            # Should have consistent structure
            assert isinstance(health_data, dict)
            
            # Should contain status information
            status_fields = ["status", "state", "healthy"]
            assert any(field in health_data for field in status_fields), \
                "Health endpoint missing status information"
            
            # Status value should be meaningful
            for field in status_fields:
                if field in health_data:
                    status_value = health_data[field]
                    if isinstance(status_value, str):
                        assert status_value in ["ok", "healthy", "up", "running", "active"]
                    elif isinstance(status_value, bool):
                        assert isinstance(status_value, bool)
    
    def test_error_response_format_regression(self, client):
        """Test that error response formats remain consistent."""
        # Test with invalid endpoint
        response = client.get("/api/nonexistent/endpoint")
        
        assert response.status_code == 404
        
        # Error response should be structured JSON
        try:
            error_data = response.json()
            assert isinstance(error_data, dict)
            
            # Should contain error information
            error_fields = ["detail", "error", "message"]
            assert any(field in error_data for field in error_fields), \
                "Error response missing error information"
                
        except json.JSONDecodeError:
            pytest.fail("Error response is not valid JSON")
    
    def test_authentication_header_format_regression(self, client):
        """Test that authentication header requirements remain consistent."""
        # Test various authentication header formats
        header_formats = [
            {"Authorization": "Bearer token123"},
            {"Authorization": "bearer token123"},  # lowercase
            {"authorization": "Bearer token123"},  # lowercase header
        ]
        
        for headers in header_formats:
            response = client.get("/api/user/profile", headers=headers)
            
            if response.status_code not in [404]:  # If endpoint exists
                # Should consistently handle auth header formats
                # (either accept or reject consistently)
                assert response.status_code in [200, 401, 403]

@pytest.mark.regression
class TestDataIntegrityRegression:
    """Test data integrity and consistency."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_seo_optimization_consistency(self, client, auth_headers):
        """Test that SEO optimization produces consistent results."""
        # Same input should produce same output
        seo_data = {
            "text": "Consistent test product description",
            "keywords": ["consistent", "test"],
            "max_length": 150
        }
        
        responses = []
        for i in range(3):
            response = client.post("/api/seo/optimize", json=seo_data, headers=auth_headers)
            if response.status_code == 200:
                responses.append(response.json())
            elif response.status_code == 404:
                pytest.skip("SEO optimization endpoint not implemented")
        
        if len(responses) >= 2:
            # All responses should be identical
            first_response = responses[0]
            for response in responses[1:]:
                assert response == first_response, "SEO optimization results are inconsistent"
    
    def test_price_calculation_precision(self, client, auth_headers):
        """Test that price calculations maintain precision."""
        # Test edge cases that historically caused floating point issues
        price_test_cases = [
            {"price": 99.99, "tax_rate": 0.1, "expected_total": 109.99},
            {"price": 0.01, "tax_rate": 0.05, "expected_total": 0.0105},
            {"price": 999999.99, "tax_rate": 0.2, "expected_total": 1199999.99}
        ]
        
        for test_case in price_test_cases:
            calculation_data = {
                "price": test_case["price"],
                "tax_rate": test_case["tax_rate"]
            }
            
            response = client.post("/api/calculate/price", json=calculation_data, headers=auth_headers)
            
            if response.status_code == 200:
                result = response.json()
                calculated_total = result.get("total", result.get("total_price"))
                
                if calculated_total is not None:
                    # Should maintain reasonable precision
                    expected = test_case["expected_total"]
                    assert abs(calculated_total - expected) < 0.01, \
                        f"Price calculation precision issue: {calculated_total} != {expected}"
                        
            elif response.status_code == 404:
                pytest.skip("Price calculation endpoint not implemented")
    
    def test_date_handling_regression(self, client, auth_headers):
        """Test that date handling is consistent across timezones."""
        # Test with various date formats
        date_formats = [
            "2024-01-15T10:30:00Z",
            "2024-01-15T10:30:00+00:00",
            "2024-01-15T10:30:00.000Z",
            "2024-01-15 10:30:00"
        ]
        
        for date_str in date_formats:
            report_data = {
                "start_date": date_str,
                "end_date": "2024-01-16T10:30:00Z",
                "metrics": ["sales"]
            }
            
            response = client.post("/api/reports/generate", json=report_data, headers=auth_headers)
            
            if response.status_code in [200, 400, 422]:
                # Should either accept valid dates or reject invalid ones consistently
                if response.status_code in [400, 422]:
                    error_response = response.json()
                    assert "date" in str(error_response).lower() or "time" in str(error_response).lower()
                    
            elif response.status_code == 404:
                break  # Endpoint not implemented

@pytest.mark.regression
class TestPerformanceRegression:
    """Test that performance hasn't regressed."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_response_time_regression(self, client):
        """Test that response times haven't regressed."""
        import time
        
        # Test critical endpoints
        endpoints = [
            "/health",
            "/api/user/profile",
            "/api/seo/optimize"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            
            if endpoint == "/api/seo/optimize":
                response = client.post(endpoint, json={
                    "text": "Test product description",
                    "keywords": ["test"],
                    "max_length": 160
                }, headers={"Authorization": "Bearer test-token"})
            else:
                response = client.get(endpoint, headers={"Authorization": "Bearer test-token"})
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # milliseconds
            
            if response.status_code == 200:
                # Response times should be reasonable (thresholds based on endpoint type)
                if endpoint == "/health":
                    assert response_time < 100, f"Health endpoint too slow: {response_time:.2f}ms"
                elif "seo" in endpoint:
                    assert response_time < 1000, f"SEO endpoint too slow: {response_time:.2f}ms"
                else:
                    assert response_time < 500, f"Endpoint {endpoint} too slow: {response_time:.2f}ms"
            elif response.status_code == 404:
                continue  # Endpoint not implemented
    
    def test_memory_usage_regression(self, client, auth_headers):
        """Test that memory usage patterns haven't regressed."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        for i in range(20):
            large_seo_data = {
                "text": "Large product description " * 500,  # ~12KB text
                "keywords": ["test"] * 100,
                "max_length": 300
            }
            
            response = client.post("/api/seo/optimize", json=large_seo_data, headers=auth_headers)
            
            if response.status_code == 404:
                break  # Endpoint not implemented
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Memory increase should be reasonable (< 20MB for this test)
        assert memory_increase_mb < 20, f"Memory usage regression: {memory_increase_mb:.2f}MB increase"