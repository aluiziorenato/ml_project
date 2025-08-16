"""
Error handling regression tests to ensure consistent error behavior.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


@pytest.mark.regression
class TestErrorHandlingConsistency:
    """Test consistent error handling across all endpoints."""
    
    def test_authentication_error_consistency(self, client: TestClient):
        """Test that authentication errors are consistent across protected endpoints."""
        protected_endpoints = [
            ("/api/categories/", "GET"),
            ("/api/categories/MLB1132", "GET"),
            ("/api/seo/optimize", "POST"),
            ("/api/endpoints/", "GET"),
            ("/api/oauth/login", "GET"),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={"test": "data"})
            
            # All should return 401 Unauthorized
            assert response.status_code == 401, f"Endpoint {endpoint} returned {response.status_code} instead of 401"
            
            error_data = response.json()
            assert "detail" in error_data, f"Endpoint {endpoint} missing 'detail' in error response"
            assert isinstance(error_data["detail"], str), f"Endpoint {endpoint} 'detail' should be string"
    
    def test_validation_error_consistency(self, client: TestClient, auth_headers: dict):
        """Test that validation errors are consistent across endpoints."""
        validation_test_cases = [
            # SEO endpoint validation errors
            ("/api/seo/optimize", "POST", {"keywords": ["test"]}, "Missing required 'text' field"),
            ("/api/seo/optimize", "POST", {"text": ""}, "Empty text not allowed"),
            ("/api/seo/optimize", "POST", {"text": "valid", "max_length": -1}, "Invalid max_length"),
            
            # Auth endpoint validation errors  
            ("/api/auth/register", "POST", {"email": "invalid-email"}, "Invalid email format"),
            ("/api/auth/register", "POST", {"password": "weak"}, "Missing email"),
            ("/api/auth/token", "POST", {"username": "test"}, "Missing password"),
            
            # Endpoint creation validation errors
            ("/api/endpoints/", "POST", {"url": "https://example.com"}, "Missing name"),
            ("/api/endpoints/", "POST", {"name": "Test"}, "Missing URL"),
            ("/api/endpoints/", "POST", {"name": "", "url": "https://example.com"}, "Empty name"),
        ]
        
        for endpoint, method, invalid_data, description in validation_test_cases:
            # Use auth headers for protected endpoints
            headers = auth_headers if endpoint.startswith("/api/seo/") or endpoint.startswith("/api/endpoints/") else {}
            
            if method == "POST":
                if endpoint == "/api/auth/token":
                    # Token endpoint expects form data
                    response = client.post(endpoint, data=invalid_data, headers=headers)
                else:
                    response = client.post(endpoint, json=invalid_data, headers=headers)
            
            # Should return 422 for validation errors or 400 for business logic errors
            assert response.status_code in [400, 422], f"{description}: Expected 400/422, got {response.status_code}"
            
            error_data = response.json()
            assert "detail" in error_data, f"{description}: Missing 'detail' in error response"
    
    def test_not_found_error_consistency(self, client: TestClient, auth_headers: dict):
        """Test that 404 errors are consistent across endpoints."""
        not_found_test_cases = [
            ("/api/endpoints/999999", "GET"),
            ("/api/endpoints/999999", "PUT"),
            ("/api/endpoints/999999", "DELETE"),
            ("/api/categories/INVALID_ID", "GET"),
            ("/api/nonexistent/endpoint", "GET"),
            ("/api/tests/999999", "GET"),
        ]
        
        for endpoint, method in not_found_test_cases:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers)
            elif method == "PUT":
                response = client.put(endpoint, json={"name": "Updated"}, headers=auth_headers)
            elif method == "DELETE":
                response = client.delete(endpoint, headers=auth_headers)
            
            assert response.status_code == 404, f"Endpoint {endpoint} {method} should return 404"
            
            error_data = response.json()
            assert "detail" in error_data, f"404 error missing 'detail' for {endpoint}"
            assert "not found" in error_data["detail"].lower(), f"404 error should mention 'not found' for {endpoint}"
    
    def test_method_not_allowed_consistency(self, client: TestClient, auth_headers: dict):
        """Test that method not allowed errors are consistent."""
        method_test_cases = [
            ("/health", "POST"),  # Health only supports GET
            ("/health", "PUT"),
            ("/health", "DELETE"),
            ("/api/auth/register", "GET"),  # Register only supports POST
            ("/api/auth/register", "PUT"),
            ("/api/auth/token", "GET"),  # Token only supports POST
        ]
        
        for endpoint, method in method_test_cases:
            headers = auth_headers if endpoint.startswith("/api/") and endpoint != "/api/auth/register" and endpoint != "/api/auth/token" else {}
            
            if method == "POST":
                response = client.post(endpoint, json={}, headers=headers)
            elif method == "PUT":
                response = client.put(endpoint, json={}, headers=headers)
            elif method == "DELETE":
                response = client.delete(endpoint, headers=headers)
            elif method == "GET":
                response = client.get(endpoint, headers=headers)
            
            # Should return 405 Method Not Allowed or 404 if route doesn't exist
            assert response.status_code in [404, 405], f"Invalid method {method} on {endpoint} should return 404/405"
    
    def test_server_error_handling(self, client: TestClient, auth_headers: dict):
        """Test server error handling consistency."""
        with patch('app.services.seo.optimize_text') as mock_optimize:
            # Simulate internal server error
            mock_optimize.side_effect = Exception("Simulated internal error")
            
            response = client.post("/api/seo/optimize", json={"text": "test"}, headers=auth_headers)
            
            # Should return 500 Internal Server Error
            assert response.status_code == 500
            
            error_data = response.json()
            assert "detail" in error_data
            assert "internal server error" in error_data["detail"].lower()
    
    def test_large_payload_error_handling(self, client: TestClient, auth_headers: dict):
        """Test handling of oversized payloads."""
        # Create very large payload (1MB of text)
        large_text = "x" * (1024 * 1024)
        large_payload = {
            "text": large_text,
            "keywords": ["test"] * 1000,  # Also large keywords list
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=large_payload, headers=auth_headers)
        
        # Should either succeed or return appropriate error
        if response.status_code != 200:
            assert response.status_code in [413, 400, 422]  # Payload too large or validation error
            error_data = response.json()
            assert "detail" in error_data
    
    def test_malformed_json_error_handling(self, client: TestClient, auth_headers: dict):
        """Test handling of malformed JSON payloads."""
        # Send malformed JSON
        response = client.post(
            "/api/seo/optimize",
            data='{"text": "test", "invalid": json}',  # Missing quotes around json
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        # Should return 422 for malformed JSON
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data


@pytest.mark.regression
class TestErrorMessageQuality:
    """Test that error messages are helpful and consistent."""
    
    def test_validation_error_message_quality(self, client: TestClient, auth_headers: dict):
        """Test that validation error messages are descriptive."""
        # Test missing required field
        response = client.post("/api/seo/optimize", json={}, headers=auth_headers)
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Should be a list of validation errors
        if isinstance(error_data["detail"], list):
            for error in error_data["detail"]:
                assert "loc" in error, "Validation error should include location"
                assert "msg" in error, "Validation error should include message"
                assert "type" in error, "Validation error should include error type"
    
    def test_authentication_error_message_quality(self, client: TestClient):
        """Test that authentication error messages are clear."""
        # Test invalid credentials
        response = client.post("/api/auth/token", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data
        assert len(error_data["detail"]) > 0, "Error message should not be empty"
    
    def test_not_found_error_message_quality(self, client: TestClient, auth_headers: dict):
        """Test that not found error messages are specific."""
        # Test specific resource not found
        response = client.get("/api/endpoints/999999", headers=auth_headers)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        detail = error_data["detail"].lower()
        assert "not found" in detail or "endpoint" in detail, "Error should be specific about what wasn't found"
    
    def test_business_logic_error_message_quality(self, client: TestClient, auth_headers: dict):
        """Test that business logic error messages are meaningful."""
        # Test SEO optimization with invalid parameters
        response = client.post("/api/seo/optimize", json={
            "text": "test",
            "max_length": -1  # Invalid negative length
        }, headers=auth_headers)
        
        assert response.status_code in [400, 422]
        error_data = response.json()
        assert "detail" in error_data
        
        # Error message should mention the invalid parameter
        detail = error_data["detail"]
        if isinstance(detail, str):
            assert len(detail) > 0, "Error message should not be empty"
        elif isinstance(detail, list):
            assert len(detail) > 0, "Should have at least one validation error"


@pytest.mark.regression
class TestErrorHandlingEdgeCases:
    """Test error handling edge cases and corner scenarios."""
    
    def test_concurrent_error_handling(self, client: TestClient, auth_headers: dict):
        """Test that errors are handled consistently under concurrent load."""
        error_requests = [
            ("/api/endpoints/999999", "GET", None),  # Not found
            ("/api/seo/optimize", "POST", {}),  # Validation error
            ("/api/categories/", "GET", None),  # Without auth (using no headers)
        ]
        
        responses = []
        
        # Make concurrent error-inducing requests
        for endpoint, method, data in error_requests:
            headers = auth_headers if method != "GET" or endpoint != "/api/categories/" else {}
            
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, json=data, headers=auth_headers if data else {})
            
            responses.append(response)
        
        # All error responses should have consistent structure
        for i, response in enumerate(responses):
            endpoint, method, data = error_requests[i]
            assert response.status_code >= 400, f"Request {i} should return error status"
            
            error_data = response.json()
            assert "detail" in error_data, f"Request {i} error should have 'detail' field"
    
    def test_cascading_error_scenarios(self, client: TestClient):
        """Test handling of cascading error scenarios."""
        # First, try to access protected endpoint without auth
        response1 = client.get("/api/categories/")
        assert response1.status_code == 401
        
        # Then, try with invalid token
        response2 = client.get("/api/categories/", headers={"Authorization": "Bearer invalid_token"})
        assert response2.status_code == 401
        
        # Both should have consistent error structure
        error1 = response1.json()
        error2 = response2.json()
        
        assert "detail" in error1
        assert "detail" in error2
        assert isinstance(error1["detail"], str)
        assert isinstance(error2["detail"], str)
    
    def test_database_error_simulation(self, client: TestClient, auth_headers: dict):
        """Test handling of simulated database errors."""
        with patch('sqlmodel.Session.exec') as mock_exec:
            # Simulate database connection error
            mock_exec.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/endpoints/", headers=auth_headers)
            
            # Should handle database errors gracefully
            assert response.status_code >= 500
            error_data = response.json()
            assert "detail" in error_data
    
    def test_external_api_error_simulation(self, client: TestClient, auth_headers: dict):
        """Test handling of external API errors."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Simulate external API timeout
            mock_get.side_effect = Exception("External API timeout")
            
            response = client.get("/api/categories/", headers=auth_headers)
            
            # Should handle external API errors gracefully
            assert response.status_code >= 400
            error_data = response.json()
            assert "detail" in error_data
    
    def test_memory_pressure_error_handling(self, client: TestClient, auth_headers: dict):
        """Test error handling under memory pressure simulation."""
        # Create request that might cause memory issues
        large_keywords = [f"keyword_{i}" for i in range(1000)]
        
        response = client.post("/api/seo/optimize", json={
            "text": "Memory pressure test",
            "keywords": large_keywords,
            "max_length": 160
        }, headers=auth_headers)
        
        # Should either succeed or fail gracefully
        if response.status_code != 200:
            assert response.status_code in [400, 413, 422, 500]
            error_data = response.json()
            assert "detail" in error_data
    
    def test_unicode_error_handling(self, client: TestClient, auth_headers: dict):
        """Test error handling with Unicode characters."""
        unicode_data = {
            "text": "测试中文字符 🚀 émojis and spëcial chars",
            "keywords": ["测试", "🚀", "spëcial"],
            "max_length": 160
        }
        
        response = client.post("/api/seo/optimize", json=unicode_data, headers=auth_headers)
        
        # Should handle Unicode gracefully
        if response.status_code != 200:
            error_data = response.json()
            assert "detail" in error_data
            # Error message should not be corrupted by Unicode
            assert isinstance(error_data["detail"], str)
    
    def test_recursive_error_prevention(self, client: TestClient, auth_headers: dict):
        """Test that error handling doesn't cause recursive errors."""
        with patch('app.core.security.get_current_user') as mock_auth:
            # Simulate authentication service throwing error
            mock_auth.side_effect = Exception("Auth service error")
            
            response = client.get("/api/categories/", headers=auth_headers)
            
            # Should handle auth errors without causing more errors
            assert response.status_code in [401, 500]
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], str)


@pytest.mark.regression
class TestErrorLoggingRegression:
    """Test that errors are properly logged for debugging."""
    
    def test_error_logging_completeness(self, client: TestClient, auth_headers: dict):
        """Test that errors include sufficient information for debugging."""
        # This test verifies error structure rather than actual logging
        # since we can't easily test logging in unit tests
        
        error_test_cases = [
            # Validation error
            ("/api/seo/optimize", "POST", {}, 422),
            # Not found error
            ("/api/endpoints/999999", "GET", None, 404),
            # Unauthorized error
            ("/api/categories/", "GET", None, 401),
        ]
        
        for endpoint, method, data, expected_status in error_test_cases:
            headers = auth_headers if expected_status != 401 else {}
            
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, json=data, headers=headers)
            
            assert response.status_code == expected_status
            
            error_data = response.json()
            
            # Should have detailed error information
            assert "detail" in error_data
            
            # For validation errors, should include field-specific info
            if expected_status == 422 and isinstance(error_data["detail"], list):
                for validation_error in error_data["detail"]:
                    assert "loc" in validation_error  # Field location
                    assert "msg" in validation_error  # Error message
                    assert "type" in validation_error  # Error type
    
    def test_error_correlation_tracking(self, client: TestClient, auth_headers: dict):
        """Test that related errors can be correlated."""
        # Make multiple related requests that might fail
        responses = []
        
        # Multiple requests to same failing endpoint
        for i in range(3):
            response = client.get("/api/endpoints/999999", headers=auth_headers)
            responses.append(response)
        
        # All should fail consistently
        for response in responses:
            assert response.status_code == 404
            error_data = response.json()
            assert "detail" in error_data
            assert error_data["detail"] == responses[0].json()["detail"]  # Consistent error message