"""
Tests for Mercado Libre services integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from meli.orders_service import orders_service
from meli.shipments_service import shipments_service
from meli.messages_service import messages_service
from meli.questions_service import questions_service
from meli.inventory_service import inventory_service
from meli.reputation_service import reputation_service


class TestMeliServices:
    """Test suite for all Meli services."""
    
    @pytest.mark.asyncio
    async def test_orders_service_health(self):
        """Test orders service health check."""
        result = await orders_service.health_check()
        assert result.success is True
        assert result.data["service"] == "orders_service"
        assert result.data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_shipments_service_health(self):
        """Test shipments service health check."""
        result = await shipments_service.health_check()
        assert result.success is True
        assert result.data["service"] == "shipments_service"
        assert result.data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_messages_service_health(self):
        """Test messages service health check."""
        result = await messages_service.health_check()
        assert result.success is True
        assert result.data["service"] == "messages_service"
        assert result.data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_questions_service_health(self):
        """Test questions service health check."""
        result = await questions_service.health_check()
        assert result.success is True
        assert result.data["service"] == "questions_service"
        assert result.data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_inventory_service_health(self):
        """Test inventory service health check."""
        result = await inventory_service.health_check()
        assert result.success is True
        assert result.data["service"] == "inventory_service"
        assert result.data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_reputation_service_health(self):
        """Test reputation service health check."""
        result = await reputation_service.health_check()
        assert result.success is True
        assert result.data["service"] == "reputation_service"
        assert result.data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_service_info(self):
        """Test service info endpoint."""
        result = await orders_service.get_service_info()
        assert result.success is True
        assert result.data["name"] == "orders_service"
        assert "endpoints" in result.data
    
    def test_service_endpoints(self):
        """Test that all services have required endpoints."""
        services = [
            orders_service,
            shipments_service,
            messages_service,
            questions_service,
            inventory_service,
            reputation_service
        ]
        
        for service in services:
            endpoints = service._get_available_endpoints()
            assert "health" in endpoints
            assert "info" in endpoints
            # Each service should have specific endpoints
            assert len(endpoints) >= 2


class TestMeliInterfaces:
    """Test interfaces and base classes."""
    
    def test_meli_response_structure(self):
        """Test MeliResponse structure."""
        from meli.interfaces import MeliResponse
        
        response = MeliResponse(success=True, data={"test": "value"})
        assert response.success is True
        assert response.data["test"] == "value"
        assert response.error is None
    
    def test_meli_paginated_response_structure(self):
        """Test MeliPaginatedResponse structure."""
        from meli.interfaces import MeliPaginatedResponse
        
        response = MeliPaginatedResponse(
            success=True,
            data=[{"item": 1}],
            total=100,
            offset=0,
            limit=50
        )
        assert response.success is True
        assert response.total == 100
        assert response.has_next is None  # Should be calculated


@pytest.mark.asyncio
async def test_service_integration():
    """Test basic service integration."""
    # Test that all services can be imported and instantiated
    services = {
        "orders": orders_service,
        "shipments": shipments_service,
        "messages": messages_service,
        "questions": questions_service,
        "inventory": inventory_service,
        "reputation": reputation_service
    }
    
    for name, service in services.items():
        assert service is not None
        assert hasattr(service, 'health_check')
        assert hasattr(service, 'get_service_info')
        assert hasattr(service, 'list_items')
        assert hasattr(service, 'get_item_details')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])