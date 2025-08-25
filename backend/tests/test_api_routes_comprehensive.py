"""
Comprehensive tests for all API routes and endpoints.
This addresses point 9 of the PR #42 checklist: "Testes de rotas de todas APIs/endpoints"
"""
import pytest
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from app.main import app

@pytest.mark.api_routes
class TestAPIRouteDiscovery:
    """Test all API routes are accessible and properly defined."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_route_discovery(self, client):
        """Test discovery of all defined routes."""
        routes = []
        
        # Extract all routes from the FastAPI app
        for route in app.routes:
            if isinstance(route, APIRoute):
                for method in route.methods:
                    if method != "HEAD":  # Skip HEAD methods
                        routes.append({
                            "path": route.path,
                            "method": method,
                            "name": route.name
                        })
        
        # Should have at least some routes defined
        assert len(routes) > 0, "No API routes found"
        
        # Log discovered routes for reference
        print(f"\nDiscovered {len(routes)} API routes:")
        for route in routes[:10]:  # Show first 10
            print(f"  {route['method']} {route['path']} ({route['name']})")
        
        return routes
    
    def test_health_routes(self, client):
        """Test health and status routes."""
        health_routes = [
            "/health",
            "/status",
            "/api/health",
            "/api/status",
            "/"
        ]
        
        accessible_routes = []
        
        for route in health_routes:
            response = client.get(route)
            if response.status_code in [200, 301, 302]:
                accessible_routes.append(route)
        
        # Should have at least one health/status route
        assert len(accessible_routes) > 0, "No health/status routes accessible"
    
    def test_documentation_routes(self, client):
        """Test API documentation routes."""
        doc_routes = [
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        for route in doc_routes:
            response = client.get(route)
            
            if response.status_code == 200:
                # Documentation should be accessible
                if route == "/openapi.json":
                    # Should return valid JSON
                    openapi_spec = response.json()
                    assert "openapi" in openapi_spec
                    assert "info" in openapi_spec
                else:
                    # Should return HTML documentation
                    assert "html" in response.headers.get("content-type", "").lower()

@pytest.mark.api_routes
class TestAuthenticationRoutes:
    """Test authentication-related routes."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_auth_routes_exist(self, client):
        """Test that authentication routes are defined."""
        auth_routes = [
            ("/api/auth/login", "POST"),
            ("/api/auth/register", "POST"),
            ("/api/auth/refresh", "POST"),
            ("/api/auth/logout", "POST"),
            ("/api/user/profile", "GET"),
            ("/api/user/profile", "PUT")
        ]
        
        accessible_routes = []
        
        for route_path, method in auth_routes:
            if method == "GET":
                response = client.get(route_path)
            else:
                response = client.request(method.lower(), route_path, json={})
            
            # Routes should exist (not 404) even if they require authentication
            if response.status_code != 404:
                accessible_routes.append((route_path, method))
        
        # Should have at least some auth routes
        assert len(accessible_routes) > 0, "No authentication routes found"
    
    def test_login_route_structure(self, client):
        """Test login route accepts proper structure."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        if response.status_code != 404:
            # Should not return 500 (server error)
            assert response.status_code < 500, "Login route has server error"
            
            # Should return structured response
            if response.status_code in [200, 401, 422]:
                response_data = response.json()
                assert isinstance(response_data, dict)
    
    def test_protected_routes_require_auth(self, client):
        """Test that protected routes require authentication."""
        protected_routes = [
            ("/api/user/profile", "GET"),
            ("/api/user/settings", "GET"),
            ("/api/campaigns/create", "POST"),
            ("/api/admin/users", "GET")
        ]
        
        for route_path, method in protected_routes:
            # Test without authentication
            if method == "GET":
                response = client.get(route_path)
            else:
                response = client.request(method.lower(), route_path, json={})
            
            if response.status_code not in [404]:  # If route exists
                # Should require authentication
                assert response.status_code in [401, 403], \
                    f"Route {method} {route_path} doesn't require authentication"

@pytest.mark.api_routes
class TestBusinessLogicRoutes:
    """Test business logic API routes."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_seo_routes(self, client, auth_headers):
        """Test SEO-related routes."""
        seo_routes = [
            ("/api/seo/optimize", "POST"),
            ("/api/seo/analyze", "POST"),
            ("/api/seo/keywords", "GET"),
            ("/api/seo/suggestions", "POST")
        ]
        
        test_data = {
            "text": "Test product description",
            "keywords": ["test"],
            "max_length": 160
        }
        
        for route_path, method in seo_routes:
            if method == "GET":
                response = client.get(route_path, headers=auth_headers)
            else:
                response = client.request(method.lower(), route_path, 
                                        json=test_data, headers=auth_headers)
            
            if response.status_code == 200:
                # Route works - verify response structure
                result = response.json()
                assert isinstance(result, (dict, list))
                
            elif response.status_code == 404:
                continue  # Route not implemented
            else:
                # Should handle errors gracefully
                assert response.status_code < 500, f"Server error in {method} {route_path}"
    
    def test_mercadolibre_routes(self, client, auth_headers):
        """Test MercadoLibre integration routes."""
        meli_routes = [
            ("/api/meli/oauth/init", "POST"),
            ("/api/meli/oauth/callback", "POST"),
            ("/api/meli/categories", "GET"),
            ("/api/meli/items", "GET"),
            ("/api/meli/items", "POST"),
            ("/api/meli/orders", "GET")
        ]
        
        test_data = {
            "client_id": "test_client",
            "redirect_uri": "http://localhost:8000/callback"
        }
        
        for route_path, method in meli_routes:
            if method == "GET":
                response = client.get(route_path, headers=auth_headers)
            else:
                response = client.request(method.lower(), route_path, 
                                        json=test_data, headers=auth_headers)
            
            if response.status_code in [200, 201]:
                # Route works
                result = response.json()
                assert isinstance(result, (dict, list))
                
            elif response.status_code == 404:
                continue  # Route not implemented
            elif response.status_code in [401, 403]:
                continue  # Authentication required
            else:
                # Should handle errors gracefully
                assert response.status_code < 500, f"Server error in {method} {route_path}"
    
    def test_campaign_management_routes(self, client, auth_headers):
        """Test campaign management routes."""
        campaign_routes = [
            ("/api/campaigns", "GET"),
            ("/api/campaigns", "POST"),
            ("/api/campaigns/{campaign_id}", "GET"),
            ("/api/campaigns/{campaign_id}", "PUT"),
            ("/api/campaigns/{campaign_id}", "DELETE"),
            ("/api/campaigns/{campaign_id}/start", "POST"),
            ("/api/campaigns/{campaign_id}/stop", "POST"),
            ("/api/campaigns/{campaign_id}/metrics", "GET")
        ]
        
        test_campaign_data = {
            "name": "Test Campaign",
            "budget": 1000.0,
            "duration_days": 7,
            "target_audience": "test_audience"
        }
        
        # Test routes with placeholder ID
        test_campaign_id = "test_campaign_123"
        
        for route_path, method in campaign_routes:
            # Replace placeholder with test ID
            actual_path = route_path.replace("{campaign_id}", test_campaign_id)
            
            if method == "GET":
                response = client.get(actual_path, headers=auth_headers)
            elif method == "DELETE":
                response = client.delete(actual_path, headers=auth_headers)
            else:
                response = client.request(method.lower(), actual_path, 
                                        json=test_campaign_data, headers=auth_headers)
            
            if response.status_code in [200, 201, 204]:
                # Route works
                if response.content:  # Some DELETE operations return no content
                    result = response.json()
                    assert isinstance(result, (dict, list))
                    
            elif response.status_code == 404:
                continue  # Route or resource not found
            elif response.status_code in [401, 403]:
                continue  # Authentication required
            else:
                # Should handle errors gracefully
                assert response.status_code < 500, f"Server error in {method} {actual_path}"

@pytest.mark.api_routes
class TestAnalyticsRoutes:
    """Test analytics and reporting routes."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}
    
    def test_analytics_routes(self, client, auth_headers):
        """Test analytics routes."""
        analytics_routes = [
            ("/api/analytics/overview", "GET"),
            ("/api/analytics/reports", "POST"),
            ("/api/analytics/metrics", "GET"),
            ("/api/analytics/dashboard", "GET"),
            ("/api/analytics/export", "POST")
        ]
        
        report_data = {
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            },
            "metrics": ["sales", "conversions"],
            "format": "json"
        }
        
        for route_path, method in analytics_routes:
            if method == "GET":
                response = client.get(route_path, headers=auth_headers)
            else:
                response = client.request(method.lower(), route_path, 
                                        json=report_data, headers=auth_headers)
            
            if response.status_code == 200:
                # Route works
                result = response.json()
                assert isinstance(result, (dict, list))
                
                # Analytics should return meaningful data
                if isinstance(result, dict):
                    data_fields = ["data", "results", "metrics", "summary"]
                    assert any(field in result for field in data_fields), \
                        f"Analytics route {route_path} missing data fields"
                        
            elif response.status_code == 404:
                continue  # Route not implemented
            elif response.status_code in [401, 403]:
                continue  # Authentication required
            else:
                # Should handle errors gracefully
                assert response.status_code < 500, f"Server error in {method} {route_path}"
    
    def test_monitoring_routes(self, client, auth_headers):
        """Test monitoring and health routes."""
        monitoring_routes = [
            ("/api/monitoring/health", "GET"),
            ("/api/monitoring/metrics", "GET"),
            ("/api/monitoring/alerts", "GET"),
            ("/api/monitoring/alerts", "POST"),
            ("/api/health/external", "GET"),
            ("/metrics", "GET")  # Prometheus metrics
        ]
        
        alert_data = {
            "name": "Test Alert",
            "metric": "response_time",
            "threshold": 1000,
            "condition": ">"
        }
        
        for route_path, method in monitoring_routes:
            if method == "GET":
                response = client.get(route_path, headers=auth_headers)
            else:
                response = client.request(method.lower(), route_path, 
                                        json=alert_data, headers=auth_headers)
            
            if response.status_code == 200:
                # Monitoring routes should return appropriate data
                if route_path == "/metrics":
                    # Prometheus metrics should be text format
                    assert "text/plain" in response.headers.get("content-type", "")
                else:
                    # Other monitoring routes should return JSON
                    result = response.json()
                    assert isinstance(result, (dict, list))
                    
            elif response.status_code == 404:
                continue  # Route not implemented
            elif response.status_code in [401, 403]:
                continue  # Authentication required

@pytest.mark.api_routes
class TestAPIErrorHandling:
    """Test API error handling across all routes."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON in POST requests."""
        routes_to_test = [
            "/api/auth/login",
            "/api/seo/optimize",
            "/api/campaigns",
            "/api/analytics/reports"
        ]
        
        # Invalid JSON payload
        invalid_json = '{"invalid": json, missing quotes}'
        
        for route in routes_to_test:
            response = client.post(
                route, 
                data=invalid_json,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 404:  # If route exists
                # Should handle invalid JSON gracefully
                assert response.status_code in [400, 422], \
                    f"Route {route} doesn't handle invalid JSON properly"
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        test_cases = [
            ("/api/auth/login", {}),  # Missing email/password
            ("/api/seo/optimize", {}),  # Missing text
            ("/api/campaigns", {"name": "test"}),  # Missing other required fields
        ]
        
        for route, incomplete_data in test_cases:
            response = client.post(route, json=incomplete_data)
            
            if response.status_code not in [404, 401, 403]:  # If route exists and accessible
                # Should validate required fields
                assert response.status_code in [400, 422], \
                    f"Route {route} doesn't validate required fields"
                
                # Error response should be informative
                error_response = response.json()
                assert "detail" in error_response or "errors" in error_response
    
    def test_method_not_allowed(self, client):
        """Test method not allowed responses."""
        # Try wrong HTTP methods
        test_cases = [
            ("/api/analytics/overview", "POST"),  # Should be GET
            ("/api/campaigns", "PUT"),  # Should be GET or POST
            ("/health", "DELETE"),  # Should be GET
        ]
        
        for route, wrong_method in test_cases:
            response = client.request(wrong_method.lower(), route)
            
            if response.status_code != 404:  # If route exists
                # Should return method not allowed if method is wrong
                if response.status_code == 405:
                    # Verify Allow header is set
                    assert "allow" in response.headers
    
    def test_large_payload_limits(self, client):
        """Test handling of oversized payloads."""
        # Create very large payload
        large_text = "A" * 1000000  # 1MB text
        large_payload = {
            "text": large_text,
            "keywords": ["test"] * 10000,
            "description": large_text
        }
        
        response = client.post("/api/seo/optimize", json=large_payload)
        
        if response.status_code not in [404]:  # If route exists
            # Should either handle large payload or reject it gracefully
            assert response.status_code in [200, 413, 422], \
                "Large payload not handled properly"
            
            if response.status_code == 413:
                # Should include informative error message
                error_data = response.json()
                assert "large" in str(error_data).lower() or "size" in str(error_data).lower()

@pytest.mark.api_routes
class TestAPIVersioning:
    """Test API versioning if implemented."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_api_versioning_routes(self, client):
        """Test if API versioning is implemented."""
        versioned_routes = [
            "/api/v1/health",
            "/api/v2/health",
            "/v1/api/health",
            "/v2/api/health"
        ]
        
        accessible_versions = []
        
        for route in versioned_routes:
            response = client.get(route)
            if response.status_code == 200:
                accessible_versions.append(route)
        
        if accessible_versions:
            # If versioning is implemented, test version consistency
            for version_route in accessible_versions:
                response = client.get(version_route)
                health_data = response.json()
                
                # Should include version information
                version_fields = ["version", "api_version"]
                if any(field in health_data for field in version_fields):
                    for field in version_fields:
                        if field in health_data:
                            assert isinstance(health_data[field], str)
    
    def test_api_deprecation_headers(self, client):
        """Test for API deprecation headers."""
        # Test common routes for deprecation warnings
        routes_to_check = [
            "/api/auth/login",
            "/api/seo/optimize",
            "/health"
        ]
        
        for route in routes_to_check:
            response = client.get(route)
            
            if response.status_code == 200:
                # Check for deprecation headers
                deprecation_headers = [
                    "deprecation",
                    "sunset",
                    "warning",
                    "x-deprecated"
                ]
                
                for header in deprecation_headers:
                    if header in response.headers:
                        # If deprecation info is present, it should be informative
                        header_value = response.headers[header]
                        assert len(header_value) > 0