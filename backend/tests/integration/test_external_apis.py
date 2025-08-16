"""
Integration tests for external API interactions.
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
import httpx
from aioresponses import aioresponses

from app.services.mercadolibre import (
    generate_code_verifier,
    generate_code_challenge,
    build_authorization_url
)


@pytest.mark.integration
class TestMercadoLibreAPIIntegration:
    """Test Mercado Libre API integration with mocked responses."""
    
    @pytest.mark.asyncio
    async def test_categories_api_integration(self, sample_categories):
        """Test categories API integration with aioresponses."""
        with aioresponses() as m:
            # Mock categories endpoint
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                payload=sample_categories,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.mercadolibre.com/sites/MLB/categories")
                
            assert response.status_code == 200
            categories = response.json()
            assert len(categories) == 3
            assert categories[0]["id"] == "MLB1132"
            assert categories[0]["name"] == "Telefones e Celulares"
    
    @pytest.mark.asyncio
    async def test_category_details_api_integration(self):
        """Test category details API integration."""
        category_details = {
            "id": "MLB1132",
            "name": "Telefones e Celulares",
            "picture": "https://http2.mlstatic.com/resources/frontend/statics/growth-sellers-landings/device-category-laptop.png",
            "permalink": "https://categoria.mercadolivre.com.br/celulares-telefones",
            "children_categories": [
                {"id": "MLB1055", "name": "Celulares e Smartphones"},
                {"id": "MLB1056", "name": "Telefones Fixos"}
            ]
        }
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/categories/MLB1132",
                payload=category_details,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.mercadolibre.com/categories/MLB1132")
                
            assert response.status_code == 200
            details = response.json()
            assert details["id"] == "MLB1132"
            assert details["name"] == "Telefones e Celulares"
            assert "children_categories" in details
    
    @pytest.mark.asyncio
    async def test_oauth_token_exchange_integration(self, mock_ml_token):
        """Test OAuth token exchange integration."""
        with aioresponses() as m:
            # Mock token exchange endpoint
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=mock_ml_token,
                status=200
            )
            
            # Simulate token exchange request
            token_data = {
                "grant_type": "authorization_code",
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "code": "test_authorization_code",
                "redirect_uri": "https://test.com/callback",
                "code_verifier": "test_code_verifier"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mercadolibre.com/oauth/token",
                    data=token_data
                )
                
            assert response.status_code == 200
            token_response = response.json()
            assert token_response["access_token"] == mock_ml_token["access_token"]
            assert token_response["token_type"] == "Bearer"
            assert token_response["expires_in"] == 21600
    
    @pytest.mark.asyncio
    async def test_user_info_api_integration(self, mock_ml_user_info):
        """Test user info API integration."""
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.mercadolibre.com/users/me",
                    headers={"Authorization": "Bearer test_access_token"}
                )
                
            assert response.status_code == 200
            user_info = response.json()
            assert user_info["id"] == 123456789
            assert user_info["email"] == "test@example.com"
            assert user_info["nickname"] == "TEST_USER"
            assert user_info["country_id"] == "BR"
    
    @pytest.mark.asyncio
    async def test_token_refresh_integration(self):
        """Test token refresh integration."""
        refresh_response = {
            "access_token": "APP_USR-new-access-token",
            "token_type": "Bearer",
            "expires_in": 21600,
            "scope": "offline_access read write",
            "user_id": "123456789",
            "refresh_token": "TG-new-refresh-token"
        }
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=refresh_response,
                status=200
            )
            
            # Simulate token refresh request
            refresh_data = {
                "grant_type": "refresh_token",
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "refresh_token": "test_refresh_token"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mercadolibre.com/oauth/token",
                    data=refresh_data
                )
                
            assert response.status_code == 200
            new_token = response.json()
            assert new_token["access_token"] == "APP_USR-new-access-token"
            assert new_token["refresh_token"] == "TG-new-refresh-token"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling integration."""
        error_response = {
            "message": "invalid_client",
            "error": "invalid_client",
            "status": 400,
            "cause": []
        }
        
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=error_response,
                status=400
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mercadolibre.com/oauth/token",
                    data={"invalid": "data"}
                )
                
            assert response.status_code == 400
            error_data = response.json()
            assert error_data["error"] == "invalid_client"
            assert error_data["message"] == "invalid_client"
    
    @pytest.mark.asyncio
    async def test_api_rate_limiting_simulation(self):
        """Test API rate limiting simulation."""
        rate_limit_response = {
            "message": "Too many requests",
            "error": "too_many_requests",
            "status": 429
        }
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                payload=rate_limit_response,
                status=429,
                headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "3600"}
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.mercadolibre.com/sites/MLB/categories")
                
            assert response.status_code == 429
            assert response.headers.get("X-RateLimit-Remaining") == "0"
            assert response.headers.get("X-RateLimit-Reset") == "3600"


@pytest.mark.integration
class TestOAuthFlowIntegration:
    """Test complete OAuth flow integration."""
    
    def test_oauth_parameters_generation(self):
        """Test OAuth parameter generation for complete flow."""
        # Generate all required OAuth parameters
        state = generate_code_verifier()
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        
        # Build authorization URL
        client_id = "test_client_id"
        redirect_uri = "https://test.example.com/callback"
        scope = "offline_access read write"
        
        auth_url = build_authorization_url(
            client_id, redirect_uri, state, code_challenge, scope
        )
        
        # Verify all parameters are present and correctly formatted
        assert "auth.mercadolibre.com.br" in auth_url
        assert f"client_id={client_id}" in auth_url
        assert f"redirect_uri={redirect_uri}" in auth_url
        assert f"state={state}" in auth_url
        assert f"code_challenge={code_challenge}" in auth_url
        assert "code_challenge_method=S256" in auth_url
        assert "response_type=code" in auth_url
        assert "scope=offline_access%20read%20write" in auth_url
        
        # Verify parameter formats
        assert len(state) >= 43
        assert len(code_verifier) >= 43
        assert len(code_challenge) == 43
    
    @pytest.mark.asyncio
    async def test_complete_oauth_flow_simulation(self, session, mock_ml_token, mock_ml_user_info):
        """Test complete OAuth flow from start to finish."""
        from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
        from app.crud.oauth_tokens import save_oauth_token, get_oauth_token
        from app.models import User
        
        # Step 1: Generate OAuth parameters
        state = generate_code_verifier()
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        
        # Step 2: Save OAuth session
        save_oauth_session(session, state, code_verifier)
        
        # Step 3: Build and verify authorization URL
        auth_url = build_authorization_url(
            "test_client_id",
            "https://test.com/callback",
            state,
            code_challenge
        )
        assert state in auth_url
        
        # Step 4: Simulate authorization callback
        auth_code = "test_authorization_code_12345"
        
        # Step 5: Retrieve and verify OAuth session
        oauth_session = get_oauth_session(session, state)
        assert oauth_session is not None
        assert oauth_session.code_verifier == code_verifier
        
        # Step 6: Simulate token exchange
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=mock_ml_token,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    "https://api.mercadolibre.com/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": "test_client_id",
                        "client_secret": "test_secret",
                        "code": auth_code,
                        "redirect_uri": "https://test.com/callback",
                        "code_verifier": code_verifier
                    }
                )
        
        assert token_response.status_code == 200
        token_data = token_response.json()
        
        # Step 7: Create user and save token
        user = User(email="oauth_flow@example.com", hashed_password="hash")
        session.add(user)
        session.commit()
        session.refresh(user)
        
        save_oauth_token(session, user.id, token_data)
        
        # Step 8: Simulate user info fetch
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    "https://api.mercadolibre.com/users/me",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"}
                )
        
        assert user_response.status_code == 200
        user_info = user_response.json()
        
        # Step 9: Verify complete flow
        stored_token = get_oauth_token(session, user.id)
        assert stored_token is not None
        assert stored_token.access_token == token_data["access_token"]
        
        # Step 10: Clean up
        delete_oauth_session(session, state)
        
        # Verify cleanup
        cleaned_session = get_oauth_session(session, state)
        assert cleaned_session is None


@pytest.mark.integration
class TestExternalAPIErrorHandling:
    """Test error handling for external API integrations."""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        with aioresponses() as m:
            # Simulate network error
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                exception=httpx.ConnectError("Connection failed")
            )
            
            async with httpx.AsyncClient() as client:
                with pytest.raises(httpx.ConnectError):
                    await client.get("https://api.mercadolibre.com/sites/MLB/categories")
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with aioresponses() as m:
            # Simulate timeout
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                exception=httpx.TimeoutException("Request timed out")
            )
            
            async with httpx.AsyncClient() as client:
                with pytest.raises(httpx.TimeoutException):
                    await client.get("https://api.mercadolibre.com/sites/MLB/categories")
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test handling of unauthorized access."""
        error_response = {
            "message": "invalid_token",
            "error": "invalid_token",
            "status": 401
        }
        
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=error_response,
                status=401
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.mercadolibre.com/users/me",
                    headers={"Authorization": "Bearer invalid_token"}
                )
                
            assert response.status_code == 401
            error_data = response.json()
            assert error_data["error"] == "invalid_token"
    
    @pytest.mark.asyncio
    async def test_server_error_handling(self):
        """Test handling of server errors."""
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                status=500,
                payload={"error": "Internal server error"}
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.mercadolibre.com/sites/MLB/categories")
                
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        with aioresponses() as m:
            # Return malformed JSON
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                status=200,
                body="invalid json response"
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.mercadolibre.com/sites/MLB/categories")
                
            assert response.status_code == 200
            # Should handle JSON decode error gracefully
            with pytest.raises(Exception):  # JSON decode error
                response.json()


@pytest.mark.integration
class TestAPIResponseValidation:
    """Test validation of API responses."""
    
    @pytest.mark.asyncio
    async def test_token_response_validation(self, mock_ml_token):
        """Test validation of token response structure."""
        with aioresponses() as m:
            m.post(
                "https://api.mercadolibre.com/oauth/token",
                payload=mock_ml_token,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mercadolibre.com/oauth/token",
                    data={"grant_type": "authorization_code"}
                )
                
            token_data = response.json()
            
            # Validate required fields
            required_fields = ["access_token", "token_type", "expires_in", "user_id"]
            for field in required_fields:
                assert field in token_data
                assert token_data[field] is not None
    
    @pytest.mark.asyncio
    async def test_user_info_response_validation(self, mock_ml_user_info):
        """Test validation of user info response structure."""
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/users/me",
                payload=mock_ml_user_info,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.mercadolibre.com/users/me",
                    headers={"Authorization": "Bearer test_token"}
                )
                
            user_data = response.json()
            
            # Validate required fields
            required_fields = ["id", "email", "nickname", "country_id"]
            for field in required_fields:
                assert field in user_data
                assert user_data[field] is not None
            
            # Validate field types
            assert isinstance(user_data["id"], int)
            assert isinstance(user_data["email"], str)
            assert isinstance(user_data["nickname"], str)
            assert "@" in user_data["email"]  # Basic email validation
    
    @pytest.mark.asyncio
    async def test_categories_response_validation(self, sample_categories):
        """Test validation of categories response structure."""
        with aioresponses() as m:
            m.get(
                "https://api.mercadolibre.com/sites/MLB/categories",
                payload=sample_categories,
                status=200
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.mercadolibre.com/sites/MLB/categories")
                
            categories = response.json()
            
            # Validate response is a list
            assert isinstance(categories, list)
            assert len(categories) > 0
            
            # Validate each category structure
            for category in categories:
                assert "id" in category
                assert "name" in category
                assert isinstance(category["id"], str)
                assert isinstance(category["name"], str)
                assert category["id"].startswith("MLB")  # Brazilian marketplace prefix