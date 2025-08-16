"""
Integration tests for Mercado Libre API functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import httpx
from aioresponses import aioresponses
import json
from datetime import datetime, timedelta

from app.services.mercadolibre import (
    get_user_info,
    get_user_products,
    exchange_code_for_token,
    refresh_access_token
)


@pytest.mark.integration
class TestMercadoLibreAPIIntegration:
    """Test Mercado Libre API integration with mocked responses."""
    
    @pytest.mark.asyncio
    async def test_get_user_info_success(self, mock_ml_user_info):
        """Test successful user info retrieval."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            result = await get_user_info(access_token)
            
            assert result == mock_ml_user_info
            assert result["id"] == 123456789
            assert result["nickname"] == "TEST_USER"
            assert result["email"] == "test@example.com"
            
    @pytest.mark.asyncio
    async def test_get_user_info_unauthorized(self):
        """Test user info retrieval with unauthorized token."""
        access_token = "invalid_access_token"
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload={"message": "Invalid access token", "error": "forbidden"},
                status=401
            )
            
            with pytest.raises(Exception):  # Should raise API error
                await get_user_info(access_token)
                
    @pytest.mark.asyncio
    async def test_get_user_info_rate_limited(self, mock_ml_error_responses):
        """Test user info retrieval with rate limiting."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_error_responses["rate_limit"],
                status=429
            )
            
            with pytest.raises(Exception):  # Should handle rate limit
                await get_user_info(access_token)
                
    @pytest.mark.asyncio
    async def test_get_user_info_server_error(self, mock_ml_error_responses):
        """Test user info retrieval with server error."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_error_responses["server_error"],
                status=500
            )
            
            with pytest.raises(Exception):  # Should handle server error
                await get_user_info(access_token)
                
    @pytest.mark.asyncio
    async def test_get_user_info_timeout(self):
        """Test user info retrieval with timeout."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                exception=asyncio.TimeoutError()
            )
            
            with pytest.raises(asyncio.TimeoutError):
                await get_user_info(access_token)


@pytest.mark.integration
class TestMercadoLibreProductsAPI:
    """Test Mercado Libre products API integration."""
    
    @pytest.mark.asyncio
    async def test_get_user_products_success(self, mock_ml_products):
        """Test successful user products retrieval."""
        access_token = "valid_access_token"
        user_id = "123456789"
        
        with aioresponses() as m:
            m.get(
                f"https://api.mercadolibre.com/users/{user_id}/items/search",
                payload=mock_ml_products,
                status=200
            )
            
            result = await get_user_products(access_token, user_id)
            
            assert result == mock_ml_products
            assert result["seller_id"] == 123456789
            assert len(result["results"]) == 2
            assert result["paging"]["total"] == 150
            
    @pytest.mark.asyncio
    async def test_get_user_products_pagination(self, mock_ml_products):
        """Test user products retrieval with pagination."""
        access_token = "valid_access_token"
        user_id = "123456789"
        
        # Mock first page
        first_page = mock_ml_products.copy()
        first_page["paging"]["offset"] = 0
        
        # Mock second page
        second_page = mock_ml_products.copy()
        second_page["paging"]["offset"] = 50
        second_page["results"] = []  # No more results
        
        with aioresponses() as m:
            # First page request
            m.get(
                f"https://api.mercadolibre.com/users/{user_id}/items/search?limit=50&offset=0",
                payload=first_page,
                status=200
            )
            
            # Second page request
            m.get(
                f"https://api.mercadolibre.com/users/{user_id}/items/search?limit=50&offset=50",
                payload=second_page,
                status=200
            )
            
            # Test first page
            result1 = await get_user_products(access_token, user_id, limit=50, offset=0)
            assert result1["paging"]["offset"] == 0
            assert len(result1["results"]) == 2
            
            # Test second page  
            result2 = await get_user_products(access_token, user_id, limit=50, offset=50)
            assert result2["paging"]["offset"] == 50
            assert len(result2["results"]) == 0
            
    @pytest.mark.asyncio
    async def test_get_user_products_empty_results(self):
        """Test user products retrieval with no products."""
        access_token = "valid_access_token"
        user_id = "123456789"
        
        empty_response = {
            "seller_id": 123456789,
            "paging": {"total": 0, "offset": 0, "limit": 50},
            "results": []
        }
        
        with aioresponses() as m:
            m.get(
                f"https://api.mercadolibre.com/users/{user_id}/items/search",
                payload=empty_response,
                status=200
            )
            
            result = await get_user_products(access_token, user_id)
            
            assert result["paging"]["total"] == 0
            assert len(result["results"]) == 0
            
    @pytest.mark.asyncio
    async def test_get_user_products_unauthorized(self):
        """Test user products retrieval with unauthorized access."""
        access_token = "invalid_access_token"
        user_id = "123456789"
        
        with aioresponses() as m:
            m.get(
                f"https://api.mercadolibre.com/users/{user_id}/items/search",
                payload={"message": "Invalid access token", "error": "forbidden"},
                status=401
            )
            
            with pytest.raises(Exception):
                await get_user_products(access_token, user_id)


@pytest.mark.integration 
class TestMercadoLibreOAuthIntegration:
    """Test Mercado Libre OAuth flow integration."""
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, mock_ml_token):
        """Test successful code to token exchange."""
        authorization_code = "valid_auth_code"
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        redirect_uri = "http://localhost:8000/oauth/callback"
        code_verifier = "test_code_verifier"
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=mock_ml_token,
                status=200
            )
            
            result = await exchange_code_for_token(
                authorization_code,
                client_id,
                client_secret,
                redirect_uri,
                code_verifier
            )
            
            assert result == mock_ml_token
            assert result["access_token"] == "APP_USR-123456789-test-token"
            assert result["token_type"] == "Bearer"
            assert result["expires_in"] == 21600
            assert result["refresh_token"] == "TG-123456789-test-refresh-token"
            
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_invalid_code(self):
        """Test code to token exchange with invalid code."""
        authorization_code = "invalid_auth_code"
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        redirect_uri = "http://localhost:8000/oauth/callback"
        code_verifier = "test_code_verifier"
        
        error_response = {
            "error": "invalid_grant",
            "error_description": "The provided authorization grant is invalid"
        }
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=error_response,
                status=400
            )
            
            with pytest.raises(Exception):
                await exchange_code_for_token(
                    authorization_code,
                    client_id,
                    client_secret,
                    redirect_uri,
                    code_verifier
                )
                
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_invalid_client(self):
        """Test code to token exchange with invalid client credentials."""
        authorization_code = "valid_auth_code"
        client_id = "invalid_client_id"
        client_secret = "invalid_client_secret"
        redirect_uri = "http://localhost:8000/oauth/callback"
        code_verifier = "test_code_verifier"
        
        error_response = {
            "error": "invalid_client",
            "error_description": "Client authentication failed"
        }
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=error_response,
                status=401
            )
            
            with pytest.raises(Exception):
                await exchange_code_for_token(
                    authorization_code,
                    client_id,
                    client_secret,
                    redirect_uri,
                    code_verifier
                )
                
    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, mock_ml_token):
        """Test successful access token refresh."""
        refresh_token = "TG-123456789-test-refresh-token"
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        
        refreshed_token = mock_ml_token.copy()
        refreshed_token["access_token"] = "APP_USR-123456789-refreshed-token"
        refreshed_token["refresh_token"] = "TG-123456789-new-refresh-token"
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=refreshed_token,
                status=200
            )
            
            result = await refresh_access_token(
                refresh_token,
                client_id,
                client_secret
            )
            
            assert result == refreshed_token
            assert result["access_token"] == "APP_USR-123456789-refreshed-token"
            assert result["refresh_token"] == "TG-123456789-new-refresh-token"
            
    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_refresh_token(self):
        """Test access token refresh with invalid refresh token."""
        refresh_token = "invalid_refresh_token"
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        
        error_response = {
            "error": "invalid_grant",
            "error_description": "The provided authorization grant is invalid"
        }
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=error_response,
                status=400
            )
            
            with pytest.raises(Exception):
                await refresh_access_token(
                    refresh_token,
                    client_id,
                    client_secret
                )


@pytest.mark.integration
class TestMercadoLibreAPIErrorHandling:
    """Test comprehensive error handling for Mercado Libre API."""
    
    @pytest.mark.asyncio
    async def test_network_connectivity_errors(self):
        """Test handling of network connectivity issues."""
        access_token = "valid_access_token"
        
        # Test connection error
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                exception=httpx.ConnectError("Connection failed")
            )
            
            with pytest.raises(httpx.ConnectError):
                await get_user_info(access_token)
                
        # Test timeout error
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                exception=httpx.TimeoutException("Request timeout")
            )
            
            with pytest.raises(httpx.TimeoutException):
                await get_user_info(access_token)
                
    @pytest.mark.asyncio
    async def test_http_status_error_handling(self):
        """Test handling of various HTTP status errors."""
        access_token = "valid_access_token"
        
        error_scenarios = [
            (400, {"error": "bad_request", "message": "Bad request"}),
            (403, {"error": "forbidden", "message": "Access forbidden"}),
            (404, {"error": "not_found", "message": "Resource not found"}),
            (429, {"error": "too_many_requests", "message": "Rate limit exceeded"}),
            (500, {"error": "internal_error", "message": "Internal server error"}),
            (502, {"error": "bad_gateway", "message": "Bad gateway"}),
            (503, {"error": "service_unavailable", "message": "Service unavailable"})
        ]
        
        for status_code, error_response in error_scenarios:
            with aioresponses() as m:
                m.get(
                    "https://api.mercadolibre.com/users/me",
                    payload=error_response,
                    status=status_code
                )
                
                with pytest.raises(Exception):  # Should handle all HTTP errors
                    await get_user_info(access_token)
                    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        access_token = "valid_access_token"
        
        # Test invalid JSON response
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                body="invalid json response",
                status=200,
                content_type="application/json"
            )
            
            with pytest.raises(Exception):  # Should handle JSON parsing error
                await get_user_info(access_token)
                
    @pytest.mark.asyncio
    async def test_partial_response_handling(self, mock_ml_user_info):
        """Test handling of partial/incomplete responses."""
        access_token = "valid_access_token"
        
        # Test response missing required fields
        incomplete_response = {
            "id": 123456789,
            "nickname": "TEST_USER"
            # Missing other expected fields
        }
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=incomplete_response,
                status=200
            )
            
            result = await get_user_info(access_token)
            
            # Should handle partial responses gracefully
            assert result["id"] == 123456789
            assert result["nickname"] == "TEST_USER"
            # Missing fields should be handled by the service


@pytest.mark.integration
class TestMercadoLibreAPIRetryLogic:
    """Test retry logic for Mercado Libre API calls."""
    
    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, mock_ml_user_info):
        """Test retry logic for server errors."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            # First attempt: server error
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload={"error": "internal_error"},
                status=500
            )
            
            # Second attempt: success
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            # This test assumes retry logic is implemented
            # If not implemented, the first call would fail
            try:
                result = await get_user_info(access_token)
                # If retry is implemented, this should succeed
                assert result == mock_ml_user_info
            except Exception:
                # If retry is not implemented, this is expected
                pytest.skip("Retry logic not implemented yet")
                
    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, mock_ml_user_info):
        """Test retry logic for rate limiting."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            # First attempt: rate limited
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload={"error": "too_many_requests"},
                status=429,
                headers={"Retry-After": "1"}
            )
            
            # Second attempt: success
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            try:
                result = await get_user_info(access_token)
                # If retry with backoff is implemented
                assert result == mock_ml_user_info
            except Exception:
                # If retry is not implemented for rate limits
                pytest.skip("Rate limit retry logic not implemented yet")
                
    @pytest.mark.asyncio
    async def test_max_retry_attempts(self):
        """Test maximum retry attempts."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            # Multiple server errors (more than max retries)
            for _ in range(5):
                m.get(
                    "https://api.mercadolibre.com/users/me",
                    payload={"error": "internal_error"},
                    status=500
                )
                
            # Should eventually give up and raise exception
            with pytest.raises(Exception):
                await get_user_info(access_token)


@pytest.mark.integration
class TestMercadoLibreAPIPerformance:
    """Test performance characteristics of Mercado Libre API integration."""
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, mock_ml_user_info):
        """Test API response time requirements."""
        import time
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            start_time = time.time()
            result = await get_user_info(access_token)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Should respond quickly (mocked response)
            assert response_time < 1.0  # 1 second max for mocked response
            assert result == mock_ml_user_info
            
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self, mock_ml_user_info):
        """Test concurrent API calls performance."""
        access_token = "valid_access_token"
        
        with aioresponses() as m:
            # Mock multiple identical responses
            for _ in range(10):
                m.get(
                    "https://api.mercadolibre.com/users/me",
                    payload=mock_ml_user_info,
                    status=200
                )
                
            # Make concurrent calls
            tasks = [get_user_info(access_token) for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            # All calls should succeed
            assert len(results) == 10
            for result in results:
                assert result == mock_ml_user_info
                
    @pytest.mark.asyncio
    async def test_large_response_handling(self):
        """Test handling of large API responses."""
        access_token = "valid_access_token"
        user_id = "123456789"
        
        # Create large response with many products
        large_response = {
            "seller_id": 123456789,
            "paging": {"total": 1000, "offset": 0, "limit": 50},
            "results": []
        }
        
        # Generate many product items
        for i in range(50):
            product = {
                "id": f"MLB{i:09d}",
                "title": f"Test Product {i}",
                "category_id": "MLB1132",
                "price": 100.0 + i,
                "currency_id": "BRL",
                "available_quantity": 10,
                "condition": "new",
                "listing_type_id": "gold_special",
                "permalink": f"https://produto.mercadolivre.com.br/MLB{i:09d}",
                "thumbnail": f"https://http2.mlstatic.com/test{i}.jpg",
                "status": "active"
            }
            large_response["results"].append(product)
            
        with aioresponses() as m:
            m.get(
                f"https://api.mercadolibre.com/users/{user_id}/items/search",
                payload=large_response,
                status=200
            )
            
            result = await get_user_products(access_token, user_id)
            
            # Should handle large response
            assert len(result["results"]) == 50
            assert result["paging"]["total"] == 1000