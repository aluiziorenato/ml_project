"""
Teste básico para validar a integração do módulo de anúncios
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.services.mercadolibre import (
    get_item_details,
    update_item,
    pause_item,
    activate_item,
    get_items_batch
)

class TestAnunciosIntegration:
    """Testes de integração para o módulo de anúncios"""
    
    @pytest.mark.asyncio
    async def test_get_item_details(self):
        """Testa busca de detalhes de um item"""
        mock_response = {
            "id": "MLB123456789",
            "title": "Smartphone Samsung Galaxy",
            "price": 999.99,
            "available_quantity": 5,
            "status": "active",
            "pictures": [{"url": "https://example.com/image.jpg"}]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.get.return_value.raise_for_status = AsyncMock()
            
            result = await get_item_details("fake_token", "MLB123456789")
            assert result["id"] == "MLB123456789"
            assert result["title"] == "Smartphone Samsung Galaxy"
            assert result["price"] == 999.99
    
    @pytest.mark.asyncio 
    async def test_update_item_price(self):
        """Testa atualização de preço de um item"""
        mock_response = {
            "id": "MLB123456789",
            "price": 899.99,
            "status": "active"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.put.return_value.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.put.return_value.raise_for_status = AsyncMock()
            
            result = await update_item("fake_token", "MLB123456789", {"price": 899.99})
            assert result["price"] == 899.99
    
    @pytest.mark.asyncio
    async def test_pause_item(self):
        """Testa pausa de um item"""
        mock_response = {
            "id": "MLB123456789",
            "status": "paused"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.put.return_value.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.put.return_value.raise_for_status = AsyncMock()
            
            result = await pause_item("fake_token", "MLB123456789")
            assert result["status"] == "paused"
    
    @pytest.mark.asyncio
    async def test_activate_item(self):
        """Testa ativação de um item"""
        mock_response = {
            "id": "MLB123456789", 
            "status": "active"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.put.return_value.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.put.return_value.raise_for_status = AsyncMock()
            
            result = await activate_item("fake_token", "MLB123456789")
            assert result["status"] == "active"

    def test_anuncios_router_import(self):
        """Testa se o router de anúncios pode ser importado"""
        try:
            from app.routers.anuncios import router
            assert router is not None
            assert hasattr(router, 'prefix')
            assert router.prefix == "/api/anuncios"
        except ImportError as e:
            pytest.fail(f"Falha ao importar router de anúncios: {e}")

if __name__ == "__main__":
    # Executa alguns testes básicos
    print("🧪 Testando módulo de anúncios...")
    
    # Teste de importação
    try:
        from app.routers.anuncios import router
        print("✅ Router de anúncios importado com sucesso")
        print(f"   Prefix: {router.prefix}")
        print(f"   Tags: {router.tags}")
    except Exception as e:
        print(f"❌ Erro ao importar router: {e}")
    
    # Teste de funções do serviço
    try:
        from app.services.mercadolibre import get_item_details, update_item
        print("✅ Funções do serviço ML importadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar funções: {e}")
    
    print("🎉 Testes básicos concluídos!")