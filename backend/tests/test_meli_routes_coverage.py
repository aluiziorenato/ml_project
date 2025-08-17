"""
Test coverage for app/routers/meli_routes.py to improve coverage from 40.91% to 100%.
Tests all routes, error handling, authentication, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime

from app.main import app
from app.models.meli_token import MeliToken
from app.models.oauth_token import OAuthToken


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestMeliRoutesAuthentication:
    """Test authentication and token validation in meli routes."""
    
    def test_get_valid_token_from_meli_token(self, db_session: Session):
        """Test getting valid token from MeliToken table."""
        from app.routers.meli_routes import get_valid_token
        
        # Create a MeliToken
        meli_token = MeliToken(
            access_token="test_meli_access_token",
            refresh_token="test_refresh_token",
            created_at=datetime.now()
        )
        db_session.add(meli_token)
        db_session.commit()
        
        # Mock the session dependency
        with patch('app.routers.meli_routes.get_session', return_value=db_session):
            token = get_valid_token(db_session)
            assert token == "test_meli_access_token"
    
    def test_get_valid_token_from_oauth_token_fallback(self, db_session: Session):
        """Test fallback to OAuthToken when MeliToken not found."""
        from app.routers.meli_routes import get_valid_token
        
        # Create an OAuthToken
        oauth_token = OAuthToken(
            access_token="test_oauth_access_token",
            refresh_token="test_oauth_refresh_token",
            created_at=datetime.now()
        )
        db_session.add(oauth_token)
        db_session.commit()
        
        with patch('app.routers.meli_routes.get_session', return_value=db_session):
            token = get_valid_token(db_session)
            assert token == "test_oauth_access_token"
    
    def test_get_valid_token_no_token_found(self, db_session: Session):
        """Test HTTPException when no token is found."""
        from app.routers.meli_routes import get_valid_token
        
        # Empty database
        with patch('app.routers.meli_routes.get_session', return_value=db_session):
            with pytest.raises(HTTPException) as exc_info:
                get_valid_token(db_session)
            
            assert exc_info.value.status_code == 404
            assert "Nenhum token válido encontrado" in str(exc_info.value.detail)
    
    def test_get_valid_token_none_access_token(self, db_session: Session):
        """Test when token exists but access_token is None."""
        from app.routers.meli_routes import get_valid_token
        
        # Create token with None access_token
        meli_token = MeliToken(
            access_token=None,
            refresh_token="test_refresh_token",
            created_at=datetime.now()
        )
        db_session.add(meli_token)
        
        oauth_token = OAuthToken(
            access_token=None,
            refresh_token="test_oauth_refresh_token",
            created_at=datetime.now()
        )
        db_session.add(oauth_token)
        db_session.commit()
        
        with patch('app.routers.meli_routes.get_session', return_value=db_session):
            with pytest.raises(HTTPException) as exc_info:
                get_valid_token(db_session)
            
            assert exc_info.value.status_code == 404


class TestMeliRoutesEndpoints:
    """Test all meli routes endpoints."""
    
    @patch('app.routers.meli_routes.get_session')
    def test_get_tokens_success(self, mock_get_session, client: TestClient):
        """Test successful token retrieval."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock MeliToken query
        mock_token = Mock()
        mock_token.access_token = "test_access_token"
        mock_token.expires_at = datetime.now()
        
        mock_query = Mock()
        mock_query.order_by.return_value.first.return_value = mock_token
        mock_session.query.return_value = mock_query
        
        response = client.get("/meli/tokens")
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert "expires_at" in data
    
    @patch('app.routers.meli_routes.get_session')
    def test_get_tokens_not_found(self, mock_get_session, client: TestClient):
        """Test token retrieval when no token exists."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock empty query result
        mock_query = Mock()
        mock_query.order_by.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        response = client.get("/meli/tokens")
        
        assert response.status_code == 404
        assert "No token found" in response.json()["detail"]
    
    @patch('app.routers.meli_routes.get_session')
    def test_get_tokens_no_expires_at(self, mock_get_session, client: TestClient):
        """Test token retrieval when expires_at is None."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock MeliToken with no expires_at
        mock_token = Mock()
        mock_token.access_token = "test_access_token"
        mock_token.expires_at = None
        
        mock_query = Mock()
        mock_query.order_by.return_value.first.return_value = mock_token
        mock_session.query.return_value = mock_query
        
        response = client.get("/meli/tokens")
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["expires_at"] is None
    
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    async def test_get_authenticated_user_success(self, mock_get_user_info, mock_get_valid_token, client: TestClient):
        """Test successful user info retrieval."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.return_value = {
            "id": 123456789,
            "nickname": "TEST_USER",
            "email": "test@example.com"
        }
        
        response = client.get("/meli/user")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["id"] == 123456789
        assert data["user"]["nickname"] == "TEST_USER"
    
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    async def test_get_authenticated_user_api_error(self, mock_get_user_info, mock_get_valid_token, client: TestClient):
        """Test user info retrieval with API error."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.side_effect = Exception("API Error")
        
        response = client.get("/meli/user")
        
        assert response.status_code == 400
        assert "Erro ao consultar dados do usuário" in response.json()["detail"]
    
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    @patch('app.services.mercadolibre.get_user_products')
    async def test_get_user_products_success(self, mock_get_user_products, mock_get_user_info, mock_get_valid_token, client: TestClient):
        """Test successful products retrieval."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.return_value = {
            "id": 123456789,
            "nickname": "TEST_USER"
        }
        mock_get_user_products.return_value = {
            "results": ["item1", "item2", "item3"],
            "paging": {"total": 3}
        }
        
        response = client.get("/meli/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == 123456789
        assert len(data["products"]["results"]) == 3
    
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    async def test_get_user_products_no_user_id(self, mock_get_user_info, mock_get_valid_token, client: TestClient):
        """Test products retrieval when user ID is missing."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.return_value = {
            "nickname": "TEST_USER"
            # Missing "id" field
        }
        
        response = client.get("/meli/products")
        
        assert response.status_code == 400
        assert "Não foi possível obter ID do usuário" in response.json()["detail"]
    
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    @patch('app.services.mercadolibre.get_user_products')
    async def test_get_user_products_api_error(self, mock_get_user_products, mock_get_user_info, mock_get_valid_token, client: TestClient):
        """Test products retrieval with API error."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.return_value = {"id": 123456789}
        mock_get_user_products.side_effect = Exception("Products API Error")
        
        response = client.get("/meli/products")
        
        assert response.status_code == 400
        assert "Erro ao consultar produtos" in response.json()["detail"]
    
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    async def test_get_user_products_user_info_error(self, mock_get_user_info, mock_get_valid_token, client: TestClient):
        """Test products retrieval when user info fails."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.side_effect = Exception("User Info Error")
        
        response = client.get("/meli/products")
        
        assert response.status_code == 400
        assert "Erro ao consultar produtos" in response.json()["detail"]


class TestMeliRoutesEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_get_valid_token_empty_access_token(self, db_session: Session):
        """Test when access_token is empty string."""
        from app.routers.meli_routes import get_valid_token
        
        # Create token with empty access_token
        meli_token = MeliToken(
            access_token="",
            refresh_token="test_refresh_token",
            created_at=datetime.now()
        )
        db_session.add(meli_token)
        db_session.commit()
        
        with patch('app.routers.meli_routes.get_session', return_value=db_session):
            with pytest.raises(HTTPException) as exc_info:
                get_valid_token(db_session)
            
            assert exc_info.value.status_code == 404
    
    @patch('app.routers.meli_routes.get_session')
    def test_get_tokens_database_error(self, mock_get_session, client: TestClient):
        """Test token retrieval with database error."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        
        # Mock database error
        mock_session.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            client.get("/meli/tokens")
    
    def test_multiple_tokens_order_by_created_at(self, db_session: Session):
        """Test that the most recent token is returned."""
        from app.routers.meli_routes import get_valid_token
        
        # Create multiple tokens
        old_token = MeliToken(
            access_token="old_token",
            created_at=datetime(2023, 1, 1)
        )
        new_token = MeliToken(
            access_token="new_token", 
            created_at=datetime(2023, 12, 31)
        )
        
        db_session.add(old_token)
        db_session.add(new_token)
        db_session.commit()
        
        with patch('app.routers.meli_routes.get_session', return_value=db_session):
            token = get_valid_token(db_session)
            assert token == "new_token"


class TestMeliRoutesLogging:
    """Test logging functionality."""
    
    @patch('app.routers.meli_routes.logger')
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    async def test_user_endpoint_error_logging(self, mock_get_user_info, mock_get_valid_token, mock_logger, client: TestClient):
        """Test that errors are properly logged."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.side_effect = Exception("Test error")
        
        response = client.get("/meli/user")
        
        assert response.status_code == 400
        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Erro ao buscar dados do usuário" in str(mock_logger.error.call_args)
    
    @patch('app.routers.meli_routes.logger')
    @patch('app.routers.meli_routes.get_valid_token')
    @patch('app.services.mercadolibre.get_user_info')
    async def test_products_endpoint_error_logging(self, mock_get_user_info, mock_get_valid_token, mock_logger, client: TestClient):
        """Test that products errors are properly logged."""
        mock_get_valid_token.return_value = "valid_token"
        mock_get_user_info.side_effect = Exception("Test error")
        
        response = client.get("/meli/products")
        
        assert response.status_code == 400
        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Erro ao buscar produtos do usuário" in str(mock_logger.error.call_args)