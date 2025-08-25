"""
Interface definitions for Mercado Libre services.

Defines the standard contract that all Meli services should implement
to ensure consistency and maintainability.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MeliResponse:
    """Standard response format for all Meli services."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MeliPaginatedResponse(MeliResponse):
    """Paginated response format for list operations."""
    total: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    has_next: Optional[bool] = None


class MeliServiceInterface(ABC):
    """
    Interface base para todos os serviços do Mercado Libre.
    
    Define métodos padrão que todos os serviços devem implementar
    para garantir consistência na API.
    """
    
    @abstractmethod
    async def health_check(self) -> MeliResponse:
        """Verifica se o serviço está funcionando corretamente."""
        pass
    
    @abstractmethod
    async def get_service_info(self) -> MeliResponse:
        """Retorna informações sobre o serviço."""
        pass
    
    @abstractmethod
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista itens relacionados ao serviço."""
        pass
    
    @abstractmethod
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes de um item específico."""
        pass


class AnalyticsIntegrationInterface(ABC):
    """Interface para integração com serviços de analytics."""
    
    @abstractmethod
    async def send_analytics_data(
        self, 
        event_type: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Envia dados para o serviço de analytics."""
        pass
    
    @abstractmethod
    async def get_performance_metrics(
        self, 
        service_name: str, 
        time_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Obtém métricas de performance do serviço."""
        pass


class OptimizerIntegrationInterface(ABC):
    """Interface para integração com serviços de otimização."""
    
    @abstractmethod
    async def get_optimization_suggestions(
        self, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Obtém sugestões de otimização."""
        pass
    
    @abstractmethod
    async def apply_optimization(
        self, 
        optimization_id: str, 
        parameters: Dict[str, Any]
    ) -> MeliResponse:
        """Aplica uma otimização específica."""
        pass


class LearningIntegrationInterface(ABC):
    """Interface para integração com serviços de aprendizado."""
    
    @abstractmethod
    async def get_learning_insights(
        self, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Obtém insights do serviço de aprendizado."""
        pass
    
    @abstractmethod
    async def train_model_with_data(
        self, 
        training_data: List[Dict[str, Any]]
    ) -> bool:
        """Treina modelos com dados do serviço."""
        pass