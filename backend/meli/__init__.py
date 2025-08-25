"""
Mercado Libre Integration Package

Este pacote contém todos os serviços organizados para integração com a API do Mercado Libre.
Estrutura modular que facilita manutenção e expansão futura.

Módulos disponíveis:
- orders_service: Gerenciamento de pedidos
- shipments_service: Gerenciamento de envios
- messages_service: Sistema de mensagens 
- questions_service: Perguntas e respostas
- inventory_service: Controle de inventário
- reputation_service: Gerenciamento de reputação
"""

from .base import BaseMeliService
from .interfaces import MeliServiceInterface

__version__ = "1.0.0"
__all__ = ["BaseMeliService", "MeliServiceInterface"]