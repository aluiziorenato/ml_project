"""
Test coverage for app/services/mercadolibre.py to improve coverage from 79.17% to 100%.
Tests all service functions, external API calls, error handling, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from datetime import datetime

from app.services.mercadolibre import (
    generate_code_verifier,
    generate_code_challenge,
    build_authorization_url,
    exchange_code_for_token,
    refresh_access_token,
    save_token_to_db,
    get_user_info,
    get_user_products,
    get_categories,
    get_item_details,
    get_items_batch,
    update_item,
    pause_item,
    activate_item,
    update_item_price,
    update_item_stock,
    get_user_campaigns,
    get_item_visits,
    get_shipping_methods,
    search_items_by_seller
)


class TestPKCEFunctions:
    """Test PKCE (Proof Key for Code Exchange) functions."""
    
    def test_generate_code_verifier_default_length(self):
        """Test generating code verifier with default length."""
        verifier = generate_code_verifier()
        
        assert isinstance(verifier, str)
        assert len(verifier) > 0
        # Base64 URL safe encoding without padding
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in verifier)
    
    def test_generate_code_verifier_custom_length(self):
        """Test generating code verifier with custom length."""
        custom_length = 32
        verifier = generate_code_verifier(custom_length)
        
        assert isinstance(verifier, str)
        assert len(verifier) > 0
    
    def test_generate_code_verifier_different_lengths(self):
        """Test generating code verifiers with different lengths."""
        lengths = [16, 32, 48, 64, 128]
        
        for length in lengths:
            verifier = generate_code_verifier(length)
            assert isinstance(verifier, str)
            assert len(verifier) > 0
    
    def test_generate_code_verifier_uniqueness(self):
        """Test that code verifiers are unique."""
        verifiers = [generate_code_verifier() for _ in range(10)]
        
        # All verifiers should be unique
        assert len(set(verifiers)) == len(verifiers)
    
    def test_generate_code_challenge_valid_input(self):
        """Test generating code challenge with valid verifier."""
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        
        assert isinstance(challenge, str)
        assert len(challenge) > 0
        # Base64 URL safe encoding without padding
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in challenge)
    
    def test_generate_code_challenge_same_input_same_output(self):
        """Test that same verifier produces same challenge."""
        verifier = "test_verifier_123"
        challenge1 = generate_code_challenge(verifier)
        challenge2 = generate_code_challenge(verifier)
        
        assert challenge1 == challenge2
    
    def test_generate_code_challenge_different_input_different_output(self):
        """Test that different verifiers produce different challenges."""
        verifier1 = "test_verifier_1"
        verifier2 = "test_verifier_2"
        
        challenge1 = generate_code_challenge(verifier1)
        challenge2 = generate_code_challenge(verifier2)
        
        assert challenge1 != challenge2
    
    @patch('app.services.mercadolibre.PKCE_CODE_CHALLENGE_METHOD', 'INVALID')
    def test_generate_code_challenge_invalid_method(self):
        """Test code challenge generation with invalid method."""
        verifier = "test_verifier"
        
        with pytest.raises(ValueError) as exc_info:
            generate_code_challenge(verifier)
        
        assert "Somente o método S256 é suportado" in str(exc_info.value)


class TestAuthorizationURL:
    """Test authorization URL building."""
    
    @patch('app.services.mercadolibre.ML_CLIENT_ID', 'test_client_id')
    @patch('app.services.mercadolibre.ML_REDIRECT_URI', 'http://localhost:8000/callback')
    @patch('app.services.mercadolibre.ML_SITE_ID', 'MLB')
    @patch('app.services.mercadolibre.ML_SCOPES', 'read write')
    @patch('app.services.mercadolibre.ML_USE_PKCE', True)
    def test_build_authorization_url_with_pkce(self):
        """Test building authorization URL with PKCE enabled."""
        state = "test_state_123"
        code_challenge = "test_challenge"
        
        url = build_authorization_url(state, code_challenge)
        
        assert "response_type=code" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=http://localhost:8000/callback" in url
        assert "state=test_state_123" in url
        assert "site_id=MLB" in url
        assert "scope=read+write" in url
        assert "code_challenge=test_challenge" in url
        assert "code_challenge_method=S256" in url
    
    @patch('app.services.mercadolibre.ML_CLIENT_ID', 'test_client_id')
    @patch('app.services.mercadolibre.ML_REDIRECT_URI', 'http://localhost:8000/callback')
    @patch('app.services.mercadolibre.ML_USE_PKCE', False)
    def test_build_authorization_url_without_pkce(self):
        """Test building authorization URL with PKCE disabled."""
        state = "test_state_123"
        code_challenge = "test_challenge"
        
        url = build_authorization_url(state, code_challenge)
        
        assert "response_type=code" in url
        assert "client_id=test_client_id" in url
        assert "state=test_state_123" in url
        assert "code_challenge" not in url
        assert "code_challenge_method" not in url
    
    @patch('app.services.mercadolibre.ML_CLIENT_ID', 'test_client_id')
    @patch('app.services.mercadolibre.ML_USE_PKCE', True)
    def test_build_authorization_url_custom_redirect_uri(self):
        """Test building authorization URL with custom redirect URI."""
        state = "test_state"
        code_challenge = "test_challenge"
        custom_redirect = "http://custom.example.com/auth"
        
        url = build_authorization_url(state, code_challenge, custom_redirect)
        
        assert f"redirect_uri={custom_redirect}" in url


class TestTokenExchange:
    """Test token exchange functionality."""
    
    @patch('app.services.mercadolibre.ML_CLIENT_ID', 'test_client_id')
    @patch('app.services.mercadolibre.ML_CLIENT_SECRET', 'test_client_secret')
    @patch('app.services.mercadolibre.ML_REDIRECT_URI', 'http://localhost:8000/callback')
    @patch('app.services.mercadolibre.ML_USE_PKCE', True)
    @patch('httpx.AsyncClient')
    async def test_exchange_code_for_token_with_pkce(self, mock_client_class):
        """Test exchanging authorization code for token with PKCE."""
        # Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600
        }
        mock_client.post.return_value = mock_response
        
        result = await exchange_code_for_token("auth_code", "code_verifier")
        
        assert result["access_token"] == "test_access_token"
        assert result["refresh_token"] == "test_refresh_token"
        
        # Verify PKCE parameters were included
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["code_verifier"] == "code_verifier"
    
    @patch('app.services.mercadolibre.ML_USE_PKCE', False)
    @patch('httpx.AsyncClient')
    async def test_exchange_code_for_token_without_pkce(self, mock_client_class):
        """Test exchanging authorization code for token without PKCE."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_client.post.return_value = mock_response
        
        result = await exchange_code_for_token("auth_code", "code_verifier")
        
        assert result["access_token"] == "test_token"
        
        # Verify PKCE parameters were NOT included
        call_args = mock_client.post.call_args
        assert "code_verifier" not in call_args[1]["data"]
    
    @patch('httpx.AsyncClient')
    async def test_exchange_code_for_token_custom_redirect(self, mock_client_class):
        """Test token exchange with custom redirect URI."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_client.post.return_value = mock_response
        
        custom_redirect = "http://custom.example.com/callback"
        
        await exchange_code_for_token("auth_code", "verifier", custom_redirect)
        
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["redirect_uri"] == custom_redirect
    
    @patch('httpx.AsyncClient')
    async def test_exchange_code_for_token_http_error(self, mock_client_class):
        """Test token exchange with HTTP error."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=Mock(), response=Mock()
        )
        mock_client.post.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            await exchange_code_for_token("invalid_code", "verifier")
    
    @patch('app.services.mercadolibre.ML_CLIENT_ID', 'test_client_id')
    @patch('app.services.mercadolibre.ML_CLIENT_SECRET', 'test_client_secret')
    @patch('httpx.AsyncClient')
    async def test_refresh_access_token_success(self, mock_client_class):
        """Test successful token refresh."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_client.post.return_value = mock_response
        
        result = await refresh_access_token("old_refresh_token")
        
        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"
        
        # Verify refresh token was used
        call_args = mock_client.post.call_args
        assert call_args[1]["data"]["refresh_token"] == "old_refresh_token"
        assert call_args[1]["data"]["grant_type"] == "refresh_token"
    
    @patch('httpx.AsyncClient')
    async def test_refresh_access_token_error(self, mock_client_class):
        """Test token refresh with error."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=Mock()
        )
        mock_client.post.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            await refresh_access_token("invalid_refresh_token")


class TestDatabaseOperations:
    """Test database operations for token storage."""
    
    def test_save_token_to_db_success(self):
        """Test successful token saving to database."""
        from app.models import OAuthToken
        
        mock_session = Mock()
        
        tokens = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "read write"
        }
        
        result = save_token_to_db(tokens, 123, mock_session)
        
        # Verify session operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Verify token object creation
        added_token = mock_session.add.call_args[0][0]
        assert added_token.user_id == 123
        assert added_token.access_token == "test_access_token"
        assert added_token.refresh_token == "test_refresh_token"
        assert added_token.token_type == "bearer"
    
    def test_save_token_to_db_none_user_id(self):
        """Test saving token with None user ID."""
        mock_session = Mock()
        
        tokens = {"access_token": "test_token"}
        
        result = save_token_to_db(tokens, None, mock_session)
        
        added_token = mock_session.add.call_args[0][0]
        assert added_token.user_id is None
    
    def test_save_token_to_db_minimal_tokens(self):
        """Test saving minimal token data."""
        mock_session = Mock()
        
        tokens = {"access_token": "test_token"}
        
        result = save_token_to_db(tokens, 123, mock_session)
        
        added_token = mock_session.add.call_args[0][0]
        assert added_token.access_token == "test_token"
        assert added_token.token_type == "bearer"  # default value


class TestMercadoLibreAPIFunctions:
    """Test Mercado Libre API function calls."""
    
    @patch('httpx.AsyncClient')
    async def test_get_user_info_success(self, mock_client_class):
        """Test successful user info retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 123456789,
            "nickname": "TEST_USER",
            "email": "test@example.com"
        }
        mock_client.get.return_value = mock_response
        
        result = await get_user_info("test_access_token")
        
        assert result["id"] == 123456789
        assert result["nickname"] == "TEST_USER"
        
        # Verify API call
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "/users/me" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_access_token"
    
    @patch('httpx.AsyncClient')
    async def test_get_user_products_success(self, mock_client_class):
        """Test successful user products retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": ["item1", "item2", "item3"],
            "paging": {"total": 3}
        }
        mock_client.get.return_value = mock_response
        
        result = await get_user_products("test_token", "123456789")
        
        assert len(result["results"]) == 3
        assert result["paging"]["total"] == 3
        
        # Verify API call
        call_args = mock_client.get.call_args
        assert "/users/123456789/items/search" in call_args[0][0]
    
    @patch('httpx.AsyncClient')
    async def test_get_categories_success(self, mock_client_class):
        """Test successful categories retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "MLB1234", "name": "Electronics"},
            {"id": "MLB5678", "name": "Books"}
        ]
        mock_client.get.return_value = mock_response
        
        result = await get_categories()
        
        assert len(result) == 2
        assert result[0]["name"] == "Electronics"
        
        # Verify no authentication header for public endpoint
        call_args = mock_client.get.call_args
        assert "headers" not in call_args[1] or "Authorization" not in call_args[1].get("headers", {})
    
    @patch('httpx.AsyncClient')
    async def test_get_item_details_success(self, mock_client_class):
        """Test successful item details retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "MLB123456",
            "title": "Test Product",
            "price": 99.99
        }
        mock_client.get.return_value = mock_response
        
        result = await get_item_details("test_token", "MLB123456")
        
        assert result["id"] == "MLB123456"
        assert result["title"] == "Test Product"
        
        call_args = mock_client.get.call_args
        assert "/items/MLB123456" in call_args[0][0]
    
    @patch('httpx.AsyncClient')
    async def test_get_items_batch_success(self, mock_client_class):
        """Test successful batch items retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = [
            {"body": {"id": "MLB1", "title": "Item 1"}},
            {"body": {"id": "MLB2", "title": "Item 2"}}
        ]
        mock_client.get.return_value = mock_response
        
        item_ids = ["MLB1", "MLB2"]
        result = await get_items_batch("test_token", item_ids)
        
        assert len(result) == 2
        
        call_args = mock_client.get.call_args
        assert "MLB1,MLB2" in call_args[0][0]
    
    @patch('httpx.AsyncClient')
    async def test_update_item_success(self, mock_client_class):
        """Test successful item update."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "MLB123456",
            "title": "Updated Product"
        }
        mock_client.put.return_value = mock_response
        
        update_data = {"title": "Updated Product"}
        result = await update_item("test_token", "MLB123456", update_data)
        
        assert result["title"] == "Updated Product"
        
        call_args = mock_client.put.call_args
        assert "/items/MLB123456" in call_args[0][0]
        assert call_args[1]["json"] == update_data
    
    @patch('app.services.mercadolibre.update_item')
    async def test_pause_item(self, mock_update_item):
        """Test item pausing."""
        mock_update_item.return_value = {"status": "paused"}
        
        result = await pause_item("test_token", "MLB123456")
        
        mock_update_item.assert_called_once_with("test_token", "MLB123456", {"status": "paused"})
        assert result["status"] == "paused"
    
    @patch('app.services.mercadolibre.update_item')
    async def test_activate_item(self, mock_update_item):
        """Test item activation."""
        mock_update_item.return_value = {"status": "active"}
        
        result = await activate_item("test_token", "MLB123456")
        
        mock_update_item.assert_called_once_with("test_token", "MLB123456", {"status": "active"})
        assert result["status"] == "active"
    
    @patch('app.services.mercadolibre.update_item')
    async def test_update_item_price(self, mock_update_item):
        """Test item price update."""
        mock_update_item.return_value = {"price": 199.99}
        
        result = await update_item_price("test_token", "MLB123456", 199.99)
        
        mock_update_item.assert_called_once_with("test_token", "MLB123456", {"price": 199.99})
        assert result["price"] == 199.99
    
    @patch('app.services.mercadolibre.update_item')
    async def test_update_item_stock(self, mock_update_item):
        """Test item stock update."""
        mock_update_item.return_value = {"available_quantity": 50}
        
        result = await update_item_stock("test_token", "MLB123456", 50)
        
        mock_update_item.assert_called_once_with("test_token", "MLB123456", {"available_quantity": 50})
        assert result["available_quantity"] == 50


class TestAdvancedAPIFunctions:
    """Test advanced API functions."""
    
    @patch('httpx.AsyncClient')
    async def test_get_user_campaigns_success(self, mock_client_class):
        """Test successful user campaigns retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1, "name": "Campaign 1"}],
            "paging": {"total": 1}
        }
        mock_client.get.return_value = mock_response
        
        result = await get_user_campaigns("test_token", "123456789")
        
        assert len(result["results"]) == 1
        
        call_args = mock_client.get.call_args
        assert "/advertising/campaigns" in call_args[0][0]
    
    @patch('httpx.AsyncClient')
    async def test_get_item_visits_success(self, mock_client_class):
        """Test successful item visits retrieval."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "item_id": "MLB123456",
            "total_visits": 150
        }
        mock_client.get.return_value = mock_response
        
        result = await get_item_visits("test_token", "MLB123456")
        
        assert result["total_visits"] == 150
        
        call_args = mock_client.get.call_args
        assert "/visits/items" in call_args[0][0]
        assert call_args[1]["params"]["item"] == "MLB123456"
    
    @patch('httpx.AsyncClient')
    async def test_get_shipping_methods_without_category(self, mock_client_class):
        """Test shipping methods without category filter."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "normal", "name": "Standard Shipping"}
        ]
        mock_client.get.return_value = mock_response
        
        result = await get_shipping_methods("test_token")
        
        assert len(result) == 1
        
        call_args = mock_client.get.call_args
        assert "params" not in call_args[1] or call_args[1]["params"] == {}
    
    @patch('httpx.AsyncClient')
    async def test_get_shipping_methods_with_category(self, mock_client_class):
        """Test shipping methods with category filter."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "express", "name": "Express Shipping"}
        ]
        mock_client.get.return_value = mock_response
        
        result = await get_shipping_methods("test_token", "MLB1234")
        
        assert len(result) == 1
        
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["category_id"] == "MLB1234"
    
    @patch('httpx.AsyncClient')
    async def test_search_items_by_seller_basic(self, mock_client_class):
        """Test basic seller items search."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": ["item1", "item2"],
            "paging": {"total": 2}
        }
        mock_client.get.return_value = mock_response
        
        result = await search_items_by_seller("test_token", "123456789")
        
        assert len(result["results"]) == 2
        
        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["seller_id"] == "123456789"
        assert params["offset"] == 0
        assert params["limit"] == 50
    
    @patch('httpx.AsyncClient')
    async def test_search_items_by_seller_with_filters(self, mock_client_class):
        """Test seller items search with filters."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "paging": {"total": 0}}
        mock_client.get.return_value = mock_response
        
        filters = {"category": "MLB1234", "condition": "new"}
        
        result = await search_items_by_seller("test_token", "123456789", filters, 10, 20)
        
        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["seller_id"] == "123456789"
        assert params["offset"] == 10
        assert params["limit"] == 20
        assert params["category"] == "MLB1234"
        assert params["condition"] == "new"


class TestErrorHandling:
    """Test error handling across all functions."""
    
    @patch('httpx.AsyncClient')
    async def test_api_function_http_error(self, mock_client_class):
        """Test HTTP error handling in API functions."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=Mock()
        )
        mock_client.get.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            await get_user_info("invalid_token")
    
    @patch('httpx.AsyncClient')
    async def test_api_function_timeout(self, mock_client_class):
        """Test timeout handling in API functions."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_client.get.side_effect = httpx.TimeoutException("Request timeout")
        
        with pytest.raises(httpx.TimeoutException):
            await get_categories()
    
    @patch('httpx.AsyncClient')
    async def test_api_function_connection_error(self, mock_client_class):
        """Test connection error handling."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(httpx.ConnectError):
            await get_user_products("test_token", "123456789")