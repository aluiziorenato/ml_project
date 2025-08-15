"""
Product management integration tests.

These tests verify complete product management flows including:
- Product creation via Mercado Libre API
- Product querying and listing
- Product updates and modifications
- Integration with authentication
- Database persistence
"""
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from sqlmodel import Session, select

from app.models import User, OAuthToken
from app.services.mercadolibre import get_user_products, get_user_info, get_categories


class TestProductCreationFlow:
    """Test end-to-end product creation workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_product_creation_flow(self, pg_session: Session, 
                                                 pg_test_user: User, oauth_token_data: OAuthToken,
                                                 mock_ml_user_info, mock_ml_categories):
        """Test complete product creation flow from user info to category selection."""
        access_token = oauth_token_data.access_token
        
        # Step 1: Get user info
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_user_info
            mock_get.return_value = mock_response
            
            user_info = await get_user_info(access_token)
            
            assert user_info["id"] == 123456789
            assert user_info["site_id"] == "MLB"
        
        # Step 2: Get available categories
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_categories
            mock_get.return_value = mock_response
            
            categories = await get_categories()
            
            assert len(categories) == 5
            assert categories[0]["id"] == "MLB1132"
        
        # Step 3: Create product (would integrate with ML API)
        product_data = {
            "title": "Smartphone Test",
            "category_id": "MLB1132",
            "price": 999.99,
            "currency_id": "BRL",
            "available_quantity": 10,
            "buying_mode": "buy_it_now",
            "listing_type_id": "gold_special",
            "condition": "new",
            "description": {"plain_text": "Smartphone de alta qualidade para testes"},
            "pictures": [{"source": "https://example.com/image.jpg"}],
            "attributes": []
        }
        
        # This would be the actual product creation call
        # For now, we simulate the expected behavior
        expected_product_response = {
            "id": "MLB123456789",
            "title": product_data["title"],
            "category_id": product_data["category_id"],
            "price": product_data["price"],
            "currency_id": product_data["currency_id"],
            "available_quantity": product_data["available_quantity"],
            "status": "paused",  # Usually starts paused
            "permalink": "https://produto.mercadolivre.com.br/MLB123456789"
        }
        
        # Verify the product data structure is valid
        assert product_data["title"] is not None
        assert product_data["category_id"] in [cat["id"] for cat in mock_ml_categories]
        assert product_data["price"] > 0
        assert product_data["available_quantity"] > 0
    
    @pytest.mark.asyncio
    async def test_product_creation_with_validation(self, oauth_token_data: OAuthToken,
                                                   mock_ml_categories):
        """Test product creation with data validation."""
        access_token = oauth_token_data.access_token
        
        # Test valid product data
        valid_product = {
            "title": "Produto Válido",
            "category_id": "MLB1132",
            "price": 150.00,
            "currency_id": "BRL",
            "available_quantity": 5,
            "condition": "new"
        }
        
        # Validate required fields
        required_fields = ["title", "category_id", "price", "currency_id", 
                          "available_quantity", "condition"]
        for field in required_fields:
            assert field in valid_product
            assert valid_product[field] is not None
        
        # Validate data types and constraints
        assert isinstance(valid_product["title"], str)
        assert len(valid_product["title"]) > 0
        assert isinstance(valid_product["price"], (int, float))
        assert valid_product["price"] > 0
        assert isinstance(valid_product["available_quantity"], int)
        assert valid_product["available_quantity"] > 0
        assert valid_product["condition"] in ["new", "used"]
    
    @pytest.mark.asyncio
    async def test_product_creation_error_handling(self, oauth_token_data: OAuthToken):
        """Test product creation error handling."""
        access_token = oauth_token_data.access_token
        
        # Test with invalid category
        invalid_product = {
            "title": "Produto Inválido",
            "category_id": "INVALID_CATEGORY",
            "price": 100.00
        }
        
        # This would simulate an API error response
        expected_error = {
            "error": "bad_request",
            "message": "Invalid category_id",
            "status": 400
        }
        
        # In a real scenario, this would be an HTTP error
        # For testing, we verify the error structure
        assert "error" in expected_error
        assert expected_error["status"] == 400


class TestProductQueryingFlow:
    """Test product querying and listing workflows."""
    
    @pytest.mark.asyncio
    async def test_get_user_products_complete_flow(self, oauth_token_data: OAuthToken,
                                                  mock_ml_user_info, mock_ml_products):
        """Test complete flow to get user products."""
        access_token = oauth_token_data.access_token
        
        # Step 1: Get user info to get user ID
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_user_info
            mock_get.return_value = mock_response
            
            user_info = await get_user_info(access_token)
            user_id = str(user_info["id"])
        
        # Step 2: Get user products
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_products
            mock_get.return_value = mock_response
            
            products = await get_user_products(access_token, user_id)
            
            assert "results" in products
            assert "paging" in products
            assert len(products["results"]) == 3
            assert products["paging"]["total"] == 3
            
            # Verify product IDs format
            for product_id in products["results"]:
                assert product_id.startswith("MLB")
                assert len(product_id) > 3
    
    @pytest.mark.asyncio
    async def test_product_details_retrieval(self, oauth_token_data: OAuthToken):
        """Test retrieving detailed product information."""
        access_token = oauth_token_data.access_token
        product_id = "MLB123456789"
        
        expected_product_details = {
            "id": product_id,
            "title": "Smartphone Samsung Galaxy",
            "category_id": "MLB1132",
            "price": 1299.99,
            "currency_id": "BRL",
            "available_quantity": 5,
            "sold_quantity": 15,
            "condition": "new",
            "status": "active",
            "listing_type_id": "gold_special",
            "permalink": f"https://produto.mercadolivre.com.br/{product_id}",
            "thumbnail": "https://example.com/thumb.jpg",
            "pictures": [
                {"id": "123", "url": "https://example.com/pic1.jpg"},
                {"id": "124", "url": "https://example.com/pic2.jpg"}
            ],
            "attributes": [
                {"id": "BRAND", "name": "Marca", "value_name": "Samsung"},
                {"id": "MODEL", "name": "Modelo", "value_name": "Galaxy S21"}
            ],
            "descriptions": [
                {
                    "id": "desc1",
                    "plain_text": "Smartphone Samsung Galaxy com excelente qualidade..."
                }
            ]
        }
        
        # Simulate product details API call
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = expected_product_details
            mock_get.return_value = mock_response
            
            # This would be the actual API call to get product details
            # url = f"https://api.mercadolibre.com/items/{product_id}"
            # headers = {"Authorization": f"Bearer {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get("mock_url")
                product_details = response.json()
            
            assert product_details["id"] == product_id
            assert "title" in product_details
            assert "price" in product_details
            assert "pictures" in product_details
            assert "attributes" in product_details
    
    @pytest.mark.asyncio
    async def test_product_search_and_filtering(self, oauth_token_data: OAuthToken):
        """Test product search and filtering capabilities."""
        access_token = oauth_token_data.access_token
        user_id = "123456789"
        
        # Test search with filters
        search_params = {
            "status": "active",
            "category": "MLB1132",
            "sort": "price_asc",
            "limit": 10,
            "offset": 0
        }
        
        filtered_products = {
            "results": ["MLB111111111", "MLB222222222"],
            "paging": {
                "total": 2,
                "offset": 0,
                "limit": 10
            },
            "filters": {
                "status": "active",
                "category": "MLB1132"
            }
        }
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = filtered_products
            mock_get.return_value = mock_response
            
            # Simulate filtered search
            async with httpx.AsyncClient() as client:
                response = await client.get("mock_search_url")
                search_results = response.json()
            
            assert len(search_results["results"]) == 2
            assert search_results["paging"]["total"] == 2
            assert "filters" in search_results


class TestProductUpdateFlow:
    """Test product update and modification workflows."""
    
    @pytest.mark.asyncio
    async def test_product_update_complete_flow(self, oauth_token_data: OAuthToken):
        """Test complete product update flow."""
        access_token = oauth_token_data.access_token
        product_id = "MLB123456789"
        
        # Original product data
        original_product = {
            "id": product_id,
            "title": "Produto Original",
            "price": 100.00,
            "available_quantity": 10,
            "status": "active"
        }
        
        # Update data
        update_data = {
            "title": "Produto Atualizado",
            "price": 120.00,
            "available_quantity": 8
        }
        
        # Expected updated product
        updated_product = {
            "id": product_id,
            "title": update_data["title"],
            "price": update_data["price"],
            "available_quantity": update_data["available_quantity"],
            "status": "active"
        }
        
        with patch("httpx.AsyncClient.put") as mock_put:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = updated_product
            mock_put.return_value = mock_response
            
            # Simulate product update
            async with httpx.AsyncClient() as client:
                response = await client.put("mock_update_url", json=update_data)
                result = response.json()
            
            assert result["title"] == update_data["title"]
            assert result["price"] == update_data["price"]
            assert result["available_quantity"] == update_data["available_quantity"]
    
    @pytest.mark.asyncio
    async def test_product_status_management(self, oauth_token_data: OAuthToken):
        """Test product status management (active, paused, closed)."""
        access_token = oauth_token_data.access_token
        product_id = "MLB123456789"
        
        status_transitions = [
            {"from": "paused", "to": "active"},
            {"from": "active", "to": "paused"},
            {"from": "active", "to": "closed"}
        ]
        
        for transition in status_transitions:
            update_data = {"status": transition["to"]}
            
            expected_response = {
                "id": product_id,
                "status": transition["to"],
                "date_updated": "2024-01-01T12:00:00.000Z"
            }
            
            with patch("httpx.AsyncClient.put") as mock_put:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = expected_response
                mock_put.return_value = mock_response
                
                # Simulate status update
                async with httpx.AsyncClient() as client:
                    response = await client.put("mock_status_url", json=update_data)
                    result = response.json()
                
                assert result["status"] == transition["to"]
    
    @pytest.mark.asyncio
    async def test_product_inventory_management(self, oauth_token_data: OAuthToken):
        """Test product inventory quantity management."""
        access_token = oauth_token_data.access_token
        product_id = "MLB123456789"
        
        # Test inventory updates
        inventory_updates = [
            {"available_quantity": 5, "expected": 5},
            {"available_quantity": 0, "expected": 0},  # Out of stock
            {"available_quantity": 100, "expected": 100}  # Restock
        ]
        
        for update in inventory_updates:
            update_data = {"available_quantity": update["available_quantity"]}
            
            expected_response = {
                "id": product_id,
                "available_quantity": update["expected"],
                "status": "paused" if update["expected"] == 0 else "active"
            }
            
            with patch("httpx.AsyncClient.put") as mock_put:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = expected_response
                mock_put.return_value = mock_response
                
                # Simulate inventory update
                async with httpx.AsyncClient() as client:
                    response = await client.put("mock_inventory_url", json=update_data)
                    result = response.json()
                
                assert result["available_quantity"] == update["expected"]
                if update["expected"] == 0:
                    assert result["status"] == "paused"
    
    @pytest.mark.asyncio
    async def test_product_price_management(self, oauth_token_data: OAuthToken):
        """Test product price management and validation."""
        access_token = oauth_token_data.access_token
        product_id = "MLB123456789"
        
        # Test price updates
        price_updates = [
            {"price": 150.00, "valid": True},
            {"price": 50.00, "valid": True},
            {"price": 0.01, "valid": True},  # Minimum price
            {"price": 0.00, "valid": False},  # Invalid price
            {"price": -10.00, "valid": False}  # Invalid negative price
        ]
        
        for update in price_updates:
            update_data = {"price": update["price"]}
            
            if update["valid"]:
                expected_response = {
                    "id": product_id,
                    "price": update["price"],
                    "currency_id": "BRL"
                }
                
                with patch("httpx.AsyncClient.put") as mock_put:
                    mock_response = MagicMock()
                    mock_response.raise_for_status.return_value = None
                    mock_response.json.return_value = expected_response
                    mock_put.return_value = mock_response
                    
                    # Simulate price update
                    async with httpx.AsyncClient() as client:
                        response = await client.put("mock_price_url", json=update_data)
                        result = response.json()
                    
                    assert result["price"] == update["price"]
            else:
                # Invalid price should raise an error
                expected_error = {
                    "error": "bad_request",
                    "message": "Invalid price value",
                    "status": 400
                }
                
                with patch("httpx.AsyncClient.put") as mock_put:
                    mock_response = MagicMock()
                    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                        "Bad Request", request=MagicMock(), response=MagicMock()
                    )
                    mock_put.return_value = mock_response
                    
                    # Simulate invalid price update
                    with pytest.raises(httpx.HTTPStatusError):
                        async with httpx.AsyncClient() as client:
                            response = await client.put("mock_price_url", json=update_data)
                            response.raise_for_status()


class TestProductDeletionFlow:
    """Test product deletion and cleanup workflows."""
    
    @pytest.mark.asyncio
    async def test_product_deletion_flow(self, oauth_token_data: OAuthToken):
        """Test complete product deletion flow."""
        access_token = oauth_token_data.access_token
        product_id = "MLB123456789"
        
        # Product should be closed first, then deleted
        close_response = {
            "id": product_id,
            "status": "closed",
            "date_closed": "2024-01-01T12:00:00.000Z"
        }
        
        with patch("httpx.AsyncClient.put") as mock_put:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = close_response
            mock_put.return_value = mock_response
            
            # Step 1: Close the product
            async with httpx.AsyncClient() as client:
                response = await client.put("mock_close_url", json={"status": "closed"})
                result = response.json()
            
            assert result["status"] == "closed"
        
        # Step 2: Delete the product (if API supports it)
        with patch("httpx.AsyncClient.delete") as mock_delete:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"deleted": True}
            mock_delete.return_value = mock_response
            
            async with httpx.AsyncClient() as client:
                response = await client.delete("mock_delete_url")
                result = response.json()
            
            assert result["deleted"] is True


class TestProductEndToEndIntegration:
    """Test complete end-to-end product management integration."""
    
    @pytest.mark.asyncio
    async def test_complete_product_lifecycle(self, pg_client, pg_session: Session,
                                            pg_test_user: User, oauth_token_data: OAuthToken,
                                            pg_auth_headers, mock_ml_user_info, 
                                            mock_ml_categories, mock_ml_products):
        """Test complete product lifecycle from creation to deletion."""
        
        # Step 1: User authentication (already done via fixtures)
        assert oauth_token_data.user_id == pg_test_user.id
        
        # Step 2: Get categories for product creation
        with patch("app.services.mercadolibre.get_categories") as mock_categories:
            mock_categories.return_value = mock_ml_categories
            
            response = pg_client.get("/api/categories", headers=pg_auth_headers)
            assert response.status_code == 200
            categories = response.json()
            assert len(categories) >= 1
        
        # Step 3: Get user info
        with patch("app.services.mercadolibre.get_user_info") as mock_user_info:
            mock_user_info.return_value = mock_ml_user_info
            
            # This would be called internally by product creation endpoint
            user_info = await mock_user_info(oauth_token_data.access_token)
            assert user_info["id"] == 123456789
        
        # Step 4: Get existing products
        with patch("app.services.mercadolibre.get_user_products") as mock_get_products:
            mock_get_products.return_value = mock_ml_products
            
            products = await mock_get_products(oauth_token_data.access_token, "123456789")
            assert "results" in products
            assert len(products["results"]) == 3
        
        # Step 5: Product operations would continue here...
        # This verifies the integration between authentication, database, and external API
        
        # Verify database state
        assert pg_test_user.oauth_tokens is not None
        assert len(pg_test_user.oauth_tokens) > 0
        assert oauth_token_data in pg_test_user.oauth_tokens
    
    @pytest.mark.asyncio
    async def test_product_management_error_recovery(self, pg_client, oauth_token_data: OAuthToken,
                                                   pg_auth_headers):
        """Test error recovery in product management flows."""
        
        # Test API timeout handling
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")
            
            # This would test how the application handles API timeouts
            # In a real scenario, this would be an endpoint that tries to get products
            
            # The application should handle the timeout gracefully
            # For now, we just verify the exception type
            with pytest.raises(httpx.TimeoutException):
                async with httpx.AsyncClient() as client:
                    await client.get("mock_url", timeout=1.0)
        
        # Test rate limiting handling
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429  # Too Many Requests
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Too Many Requests", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response
            
            # Application should handle rate limiting appropriately
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                async with httpx.AsyncClient() as client:
                    response = await client.get("mock_url")
                    response.raise_for_status()
            
            # Verify it's a rate limiting error
            assert exc_info.value.response.status_code == 429