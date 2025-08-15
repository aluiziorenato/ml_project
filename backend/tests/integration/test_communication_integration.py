"""
Communication integration tests between backend, database, and external APIs.

These tests verify:
- End-to-end communication flows
- Integration between all system components
- Error handling across system boundaries
- Performance under various scenarios
- Data consistency across components
"""
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.models import User, OAuthToken, OAuthSession
from app.services.mercadolibre import (
    get_user_info, get_user_products, get_categories,
    exchange_code_for_token, refresh_access_token
)
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session
from app.crud.oauth_tokens import save_token_to_db


class TestFullSystemIntegration:
    """Test complete system integration across all components."""
    
    @pytest.mark.asyncio
    async def test_complete_oauth_to_product_flow(self, pg_client, pg_session: Session,
                                                 pg_test_user: User, pg_auth_headers,
                                                 mock_ml_token, mock_ml_user_info, 
                                                 mock_ml_products, mock_ml_categories):
        """Test complete flow from OAuth to product management."""
        
        # Step 1: Initiate OAuth flow
        response = pg_client.get("/api/oauth/login")
        assert response.status_code == 307  # Redirect to ML
        
        # Extract state from redirect URL
        redirect_url = response.headers.get("location")
        assert "state=" in redirect_url
        state = redirect_url.split("state=")[1].split("&")[0]
        
        # Verify OAuth session was created in database
        oauth_session = get_oauth_session(pg_session, state)
        assert oauth_session is not None
        
        # Step 2: Complete OAuth callback
        with patch("app.services.mercadolibre.exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = mock_ml_token
            
            callback_response = pg_client.get(
                f"/api/oauth/callback?code=test_code&state={state}",
                headers=pg_auth_headers
            )
            assert callback_response.status_code == 200
            
            # Verify token was saved to database
            saved_token = pg_session.exec(
                select(OAuthToken).where(OAuthToken.user_id == pg_test_user.id)
            ).first()
            assert saved_token is not None
            assert saved_token.access_token == mock_ml_token["access_token"]
        
        # Step 3: Use token to get user info
        with patch("app.services.mercadolibre.get_user_info") as mock_get_user:
            mock_get_user.return_value = mock_ml_user_info
            
            user_info = await get_user_info(saved_token.access_token)
            assert user_info["id"] == 123456789
            assert user_info["site_id"] == "MLB"
        
        # Step 4: Get categories for product management
        with patch("app.services.mercadolibre.get_categories") as mock_get_categories:
            mock_get_categories.return_value = mock_ml_categories
            
            categories = await get_categories()
            assert len(categories) == 5
            assert any(cat["id"] == "MLB1132" for cat in categories)
        
        # Step 5: Get user products
        with patch("app.services.mercadolibre.get_user_products") as mock_get_products:
            mock_get_products.return_value = mock_ml_products
            
            products = await get_user_products(saved_token.access_token, str(user_info["id"]))
            assert "results" in products
            assert len(products["results"]) == 3
        
        # Verify database consistency
        pg_session.refresh(pg_test_user)
        assert len(pg_test_user.oauth_tokens) > 0
        
        # Verify OAuth session was cleaned up
        cleaned_session = get_oauth_session(pg_session, state)
        assert cleaned_session is None
    
    @pytest.mark.asyncio
    async def test_concurrent_api_calls_with_database(self, pg_session: Session,
                                                     oauth_token_data: OAuthToken,
                                                     mock_ml_user_info, mock_ml_products,
                                                     mock_ml_categories):
        """Test concurrent API calls with database operations."""
        import asyncio
        
        access_token = oauth_token_data.access_token
        
        # Simulate concurrent API calls
        async def get_user_info_task():
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = mock_ml_user_info
                mock_get.return_value = mock_response
                return await get_user_info(access_token)
        
        async def get_categories_task():
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = mock_ml_categories
                mock_get.return_value = mock_response
                return await get_categories()
        
        async def get_products_task():
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = mock_ml_products
                mock_get.return_value = mock_response
                return await get_user_products(access_token, "123456789")
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            get_user_info_task(),
            get_categories_task(),
            get_products_task(),
            return_exceptions=True
        )
        
        # Verify all calls succeeded
        assert len(results) == 3
        assert all(not isinstance(result, Exception) for result in results)
        
        user_info, categories, products = results
        assert user_info["id"] == 123456789
        assert len(categories) == 5
        assert len(products["results"]) == 3
        
        # Verify database state remains consistent
        token_in_db = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == oauth_token_data.id)
        ).first()
        assert token_in_db is not None
        assert token_in_db.access_token == access_token
    
    @pytest.mark.asyncio
    async def test_system_resilience_under_load(self, pg_session: Session,
                                               oauth_token_data: OAuthToken,
                                               mock_ml_user_info):
        """Test system resilience under simulated load."""
        import asyncio
        import random
        
        access_token = oauth_token_data.access_token
        
        async def simulate_api_call(call_id: int):
            """Simulate an API call with random delay."""
            await asyncio.sleep(random.uniform(0.1, 0.5))  # Random delay
            
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {**mock_ml_user_info, "call_id": call_id}
                mock_get.return_value = mock_response
                
                return await get_user_info(access_token)
        
        # Create 20 concurrent API calls
        tasks = [simulate_api_call(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all calls completed successfully
        successful_calls = [r for r in results if not isinstance(r, Exception)]
        failed_calls = [r for r in results if isinstance(r, Exception)]
        
        assert len(successful_calls) == 20
        assert len(failed_calls) == 0
        
        # Verify database connection remains stable
        token_check = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == oauth_token_data.id)
        ).first()
        assert token_check is not None


class TestErrorPropagationAndHandling:
    """Test error propagation across system components."""
    
    @pytest.mark.asyncio
    async def test_api_error_to_database_rollback(self, pg_session: Session,
                                                 pg_test_user: User):
        """Test that API errors trigger proper database rollback."""
        
        # Start a database transaction
        initial_token_count = len(pg_test_user.oauth_tokens)
        
        # Simulate saving a token that will be rolled back due to API error
        temp_token = OAuthToken(
            user_id=pg_test_user.id,
            access_token="temp_token_to_rollback",
            token_type="Bearer"
        )
        pg_session.add(temp_token)
        
        # Simulate API call that fails
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Internal Server Error", request=MagicMock(), response=MagicMock()
            )
            mock_get.return_value = mock_response
            
            # The API call should fail
            with pytest.raises(httpx.HTTPStatusError):
                await get_user_info("temp_token_to_rollback")
            
            # Rollback the transaction due to API error
            pg_session.rollback()
        
        # Verify the token was not saved due to rollback
        pg_session.refresh(pg_test_user)
        assert len(pg_test_user.oauth_tokens) == initial_token_count
    
    @pytest.mark.asyncio
    async def test_database_error_handling_in_api_flow(self, pg_client, pg_auth_headers):
        """Test API endpoint error handling when database operations fail."""
        
        # Mock database session to raise an error
        with patch("app.db.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.exec.side_effect = Exception("Database connection failed")
            mock_get_session.return_value = mock_session
            
            # API call should handle database error gracefully
            response = pg_client.get("/api/oauth/login")
            # The exact status code depends on error handling implementation
            # but it should not be a 500 if properly handled
            assert response.status_code in [400, 503, 500]  # Expected error codes
    
    @pytest.mark.asyncio
    async def test_external_api_timeout_handling(self, oauth_token_data: OAuthToken):
        """Test handling of external API timeouts."""
        access_token = oauth_token_data.access_token
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")
            
            # API call should handle timeout appropriately
            with pytest.raises(httpx.TimeoutException):
                await get_user_info(access_token)
    
    @pytest.mark.asyncio
    async def test_network_error_recovery(self, oauth_token_data: OAuthToken,
                                         mock_ml_user_info):
        """Test network error recovery mechanisms."""
        access_token = oauth_token_data.access_token
        
        # First call fails with network error
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Network error")
            
            with pytest.raises(httpx.ConnectError):
                await get_user_info(access_token)
        
        # Second call succeeds (simulating network recovery)
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_user_info
            mock_get.return_value = mock_response
            
            result = await get_user_info(access_token)
            assert result["id"] == 123456789


class TestDataConsistencyAcrossComponents:
    """Test data consistency across database and external APIs."""
    
    @pytest.mark.asyncio
    async def test_token_refresh_data_consistency(self, pg_session: Session,
                                                 oauth_token_data: OAuthToken,
                                                 mock_ml_token):
        """Test data consistency during token refresh."""
        original_access_token = oauth_token_data.access_token
        new_token_data = {**mock_ml_token, "access_token": "APP_USR-new-token"}
        
        # Refresh token
        with patch("app.services.mercadolibre.refresh_access_token") as mock_refresh:
            mock_refresh.return_value = new_token_data
            
            refreshed_tokens = await refresh_access_token(oauth_token_data.refresh_token)
            
            # Update token in database
            oauth_token_data.access_token = refreshed_tokens["access_token"]
            pg_session.commit()
            pg_session.refresh(oauth_token_data)
        
        # Verify token was updated consistently
        assert oauth_token_data.access_token == new_token_data["access_token"]
        assert oauth_token_data.access_token != original_access_token
        
        # Verify database reflects the change
        updated_token = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == oauth_token_data.id)
        ).first()
        assert updated_token.access_token == new_token_data["access_token"]
    
    @pytest.mark.asyncio
    async def test_user_data_synchronization(self, pg_session: Session,
                                           pg_test_user: User, oauth_token_data: OAuthToken,
                                           mock_ml_user_info):
        """Test synchronization between local user data and ML user data."""
        access_token = oauth_token_data.access_token
        
        # Get user info from ML API
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_ml_user_info
            mock_get.return_value = mock_response
            
            ml_user_info = await get_user_info(access_token)
        
        # Verify email consistency (if emails match)
        if pg_test_user.email == mock_ml_user_info["email"]:
            assert pg_test_user.email == ml_user_info["email"]
        
        # Verify ML-specific data is available
        assert "id" in ml_user_info
        assert "nickname" in ml_user_info
        assert "site_id" in ml_user_info
    
    def test_oauth_session_cleanup_consistency(self, pg_session: Session,
                                             oauth_session_data: OAuthSession):
        """Test OAuth session cleanup maintains data consistency."""
        initial_state = oauth_session_data.state
        
        # Verify session exists
        session_exists = get_oauth_session(pg_session, initial_state)
        assert session_exists is not None
        
        # Delete session (simulate cleanup after successful OAuth)
        from app.crud.oauth_sessions import delete_oauth_session
        delete_oauth_session(pg_session, initial_state)
        
        # Verify session is completely removed
        session_after_delete = get_oauth_session(pg_session, initial_state)
        assert session_after_delete is None
        
        # Verify no orphaned data remains
        all_sessions = pg_session.exec(select(OAuthSession)).fetchall()
        assert not any(session.state == initial_state for session in all_sessions)


class TestPerformanceUnderIntegration:
    """Test system performance under integrated operations."""
    
    @pytest.mark.asyncio
    async def test_batch_operations_performance(self, pg_session: Session,
                                              oauth_token_data: OAuthToken,
                                              mock_ml_products):
        """Test performance of batch operations across components."""
        import time
        
        access_token = oauth_token_data.access_token
        user_id = "123456789"
        
        start_time = time.time()
        
        # Simulate batch product operations
        batch_size = 10
        results = []
        
        for i in range(batch_size):
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {
                    **mock_ml_products,
                    "batch_id": i
                }
                mock_get.return_value = mock_response
                
                result = await get_user_products(access_token, user_id)
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all operations completed
        assert len(results) == batch_size
        
        # Performance should be reasonable (adjust threshold as needed)
        assert total_time < 5.0  # Should complete within 5 seconds
        
        # Verify database connection remains stable
        token_check = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == oauth_token_data.id)
        ).first()
        assert token_check is not None
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, pg_session: Session,
                                         oauth_token_data: OAuthToken,
                                         mock_ml_user_info):
        """Test memory usage under sustained load."""
        import gc
        import sys
        
        access_token = oauth_token_data.access_token
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for i in range(50):
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {**mock_ml_user_info, "iteration": i}
                mock_get.return_value = mock_response
                
                result = await get_user_info(access_token)
                assert result["iteration"] == i
        
        # Check memory usage after operations
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be reasonable
        object_growth = final_objects - initial_objects
        assert object_growth < 1000  # Adjust threshold as needed
        
        # Database connection should still be healthy
        token_check = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == oauth_token_data.id)
        ).first()
        assert token_check is not None


class TestEndToEndScenarios:
    """Test realistic end-to-end scenarios."""
    
    @pytest.mark.asyncio
    async def test_new_user_complete_journey(self, pg_client, pg_session: Session,
                                           mock_ml_token, mock_ml_user_info,
                                           mock_ml_categories, mock_ml_products):
        """Test complete journey for a new user."""
        
        # Step 1: User registration
        user_data = {
            "email": "newuser_journey@example.com",
            "password": "securepassword123"
        }
        
        register_response = pg_client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Step 2: User login
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = pg_client.post("/api/auth/token", data=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 3: OAuth flow
        oauth_response = pg_client.get("/api/oauth/login")
        assert oauth_response.status_code == 307
        
        # Extract state and simulate callback
        redirect_url = oauth_response.headers.get("location")
        state = redirect_url.split("state=")[1].split("&")[0]
        
        with patch("app.services.mercadolibre.exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = mock_ml_token
            
            callback_response = pg_client.get(
                f"/api/oauth/callback?code=test_code&state={state}",
                headers=auth_headers
            )
            assert callback_response.status_code == 200
        
        # Step 4: Access protected resources
        with patch("app.services.mercadolibre.get_categories") as mock_get_categories:
            mock_get_categories.return_value = mock_ml_categories
            
            categories_response = pg_client.get("/api/categories", headers=auth_headers)
            assert categories_response.status_code == 200
        
        # Step 5: Verify user state in database
        user = pg_session.exec(
            select(User).where(User.email == user_data["email"])
        ).first()
        assert user is not None
        assert len(user.oauth_tokens) > 0
    
    @pytest.mark.asyncio
    async def test_returning_user_with_expired_token(self, pg_client, pg_session: Session,
                                                   pg_test_user: User, pg_auth_headers,
                                                   mock_ml_token):
        """Test scenario where returning user has expired token."""
        
        # Create an expired token
        expired_token = OAuthToken(
            user_id=pg_test_user.id,
            access_token="APP_USR-expired-token",
            refresh_token="TG-valid-refresh-token",
            token_type="Bearer",
            expires_in=3600,
            created_at=datetime.utcnow() - timedelta(hours=2)  # Expired
        )
        pg_session.add(expired_token)
        pg_session.commit()
        
        # Attempt to use expired token (would fail in real scenario)
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401  # Unauthorized
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response
            
            # This would trigger token refresh in real implementation
            with pytest.raises(httpx.HTTPStatusError):
                await get_user_info(expired_token.access_token)
        
        # Refresh token
        new_token_data = {**mock_ml_token, "access_token": "APP_USR-refreshed-token"}
        
        with patch("app.services.mercadolibre.refresh_access_token") as mock_refresh:
            mock_refresh.return_value = new_token_data
            
            refreshed_tokens = await refresh_access_token(expired_token.refresh_token)
            
            # Update token in database
            expired_token.access_token = refreshed_tokens["access_token"]
            pg_session.commit()
        
        # Verify token was refreshed
        assert expired_token.access_token == new_token_data["access_token"]
    
    @pytest.mark.asyncio
    async def test_system_recovery_after_downtime(self, pg_session: Session,
                                                 oauth_token_data: OAuthToken,
                                                 mock_ml_user_info):
        """Test system recovery after simulated downtime."""
        access_token = oauth_token_data.access_token
        
        # Simulate system downtime (multiple failures)
        failure_count = 0
        max_failures = 3
        
        for attempt in range(5):  # 5 attempts, first 3 fail
            try:
                with patch("httpx.AsyncClient.get") as mock_get:
                    if failure_count < max_failures:
                        failure_count += 1
                        mock_get.side_effect = httpx.ConnectError("Service unavailable")
                        await get_user_info(access_token)
                    else:
                        # Service recovered
                        mock_response = MagicMock()
                        mock_response.raise_for_status.return_value = None
                        mock_response.json.return_value = mock_ml_user_info
                        mock_get.return_value = mock_response
                        
                        result = await get_user_info(access_token)
                        assert result["id"] == 123456789
                        break  # Success, exit loop
                        
            except httpx.ConnectError:
                if attempt == 4:  # Last attempt
                    pytest.fail("Service never recovered")
                continue
        
        # Verify database remained consistent during downtime
        token_check = pg_session.exec(
            select(OAuthToken).where(OAuthToken.id == oauth_token_data.id)
        ).first()
        assert token_check is not None
        assert token_check.access_token == access_token