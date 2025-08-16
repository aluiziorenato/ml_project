"""
Main router for Mercado Libre services integration.

Consolidates all ML services into organized endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import Optional, Dict, Any
from app.database import get_session
from app.models.oauth_token import OAuthToken

# Import all ML services
from meli.orders_service import orders_service
from meli.shipments_service import shipments_service
from meli.messages_service import messages_service
from meli.questions_service import questions_service
from meli.inventory_service import inventory_service
from meli.reputation_service import reputation_service

import logging

logger = logging.getLogger("app.meli_services_router")
router = APIRouter()


def get_valid_token(session: Session = Depends(get_session)) -> str:
    """Helper para obter um token válido do Mercado Livre."""
    oauth_token = session.query(OAuthToken).order_by(OAuthToken.created_at.desc()).first()
    if oauth_token and oauth_token.access_token:
        return oauth_token.access_token
    
    raise HTTPException(status_code=404, detail="Nenhum token válido encontrado. Faça login no Mercado Livre primeiro.")


# ============================
# Orders Service Endpoints
# ============================

@router.get("/orders_service/health")
async def orders_health():
    """Health check do serviço de pedidos."""
    return await orders_service.health_check()

@router.get("/orders_service/info")
async def orders_info():
    """Informações do serviço de pedidos."""
    return await orders_service.get_service_info()

@router.get("/orders_service/orders")
async def list_orders(
    user_id: str = Query(..., description="ID do vendedor"),
    offset: int = Query(0, description="Página"),
    limit: int = Query(50, description="Itens por página"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    date_from: Optional[str] = Query(None, description="Data inicial"),
    date_to: Optional[str] = Query(None, description="Data final"),
    token: str = Depends(get_valid_token)
):
    """Lista pedidos do vendedor."""
    filters = {}
    if status:
        filters["status"] = status
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    result = await orders_service.list_items(token, user_id, offset, limit, filters)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "success": True,
        "data": result.data,
        "pagination": {
            "total": result.total,
            "offset": result.offset,
            "limit": result.limit,
            "has_next": result.has_next
        },
        "metadata": result.metadata
    }

@router.get("/orders_service/orders/{order_id}")
async def get_order_details(
    order_id: str,
    token: str = Depends(get_valid_token)
):
    """Obtém detalhes de um pedido."""
    result = await orders_service.get_item_details(token, order_id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result

@router.get("/orders_service/analytics")
async def get_orders_analytics(
    user_id: str = Query(..., description="ID do vendedor"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    token: str = Depends(get_valid_token)
):
    """Analytics de pedidos."""
    result = await orders_service.get_order_analytics(token, user_id, date_from, date_to)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


# ============================
# Shipments Service Endpoints
# ============================

@router.get("/shipments_service/health")
async def shipments_health():
    """Health check do serviço de envios."""
    return await shipments_service.health_check()

@router.get("/shipments_service/shipments")
async def list_shipments(
    user_id: str = Query(..., description="ID do vendedor"),
    offset: int = Query(0),
    limit: int = Query(50),
    status: Optional[str] = Query(None),
    shipping_method: Optional[str] = Query(None),
    token: str = Depends(get_valid_token)
):
    """Lista envios do vendedor."""
    filters = {}
    if status:
        filters["status"] = status
    if shipping_method:
        filters["shipping_method"] = shipping_method
    
    result = await shipments_service.list_items(token, user_id, offset, limit, filters)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "success": True,
        "data": result.data,
        "pagination": {
            "total": result.total,
            "offset": result.offset,
            "limit": result.limit,
            "has_next": result.has_next
        }
    }

@router.get("/shipments_service/shipments/{shipment_id}/tracking")
async def get_tracking_info(
    shipment_id: str,
    token: str = Depends(get_valid_token)
):
    """Rastreamento de envio."""
    result = await shipments_service.get_tracking_info(token, shipment_id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result

@router.get("/shipments_service/shipping_options")
async def get_shipping_options(
    item_id: str = Query(...),
    zip_code: str = Query(...),
    token: str = Depends(get_valid_token)
):
    """Opções de envio."""
    result = await shipments_service.get_shipping_options(token, item_id, zip_code)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


# ============================
# Messages Service Endpoints
# ============================

@router.get("/messages_service/health")
async def messages_health():
    """Health check do serviço de mensagens."""
    return await messages_service.health_check()

@router.get("/messages_service/messages")
async def list_messages(
    user_id: str = Query(..., description="ID do usuário"),
    offset: int = Query(0),
    limit: int = Query(50),
    status: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    token: str = Depends(get_valid_token)
):
    """Lista mensagens."""
    filters = {}
    if status:
        filters["status"] = status
    if unread_only:
        filters["unread_only"] = True
    
    result = await messages_service.list_items(token, user_id, offset, limit, filters)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "success": True,
        "data": result.data,
        "pagination": {
            "total": result.total,
            "offset": result.offset,
            "limit": result.limit,
            "has_next": result.has_next
        },
        "metadata": result.metadata
    }

@router.get("/messages_service/ai_suggestions")
async def get_ai_suggestions(
    message_content: str = Query(..., description="Conteúdo da mensagem"),
    token: str = Depends(get_valid_token)
):
    """Sugestões de resposta com IA."""
    result = await messages_service.get_automated_response_suggestions(token, message_content)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


# ============================
# Questions Service Endpoints
# ============================

@router.get("/questions_service/health")
async def questions_health():
    """Health check do serviço de perguntas."""
    return await questions_service.health_check()

@router.get("/questions_service/questions")
async def list_questions(
    user_id: str = Query(..., description="ID do vendedor"),
    offset: int = Query(0),
    limit: int = Query(50),
    status: Optional[str] = Query(None),
    unanswered_only: bool = Query(False),
    token: str = Depends(get_valid_token)
):
    """Lista perguntas."""
    filters = {}
    if status:
        filters["status"] = status
    if unanswered_only:
        filters["unanswered_only"] = True
    
    result = await questions_service.list_items(token, user_id, offset, limit, filters)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "success": True,
        "data": result.data,
        "pagination": {
            "total": result.total,
            "offset": result.offset,
            "limit": result.limit,
            "has_next": result.has_next
        },
        "metadata": result.metadata
    }

@router.post("/questions_service/answers")
async def answer_question(
    question_data: Dict[str, Any],
    token: str = Depends(get_valid_token)
):
    """Responde uma pergunta."""
    question_id = question_data.get("question_id")
    answer_text = question_data.get("answer")
    
    if not question_id or not answer_text:
        raise HTTPException(status_code=400, detail="question_id e answer são obrigatórios")
    
    result = await questions_service.answer_question(token, question_id, answer_text)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result

@router.get("/questions_service/ai_suggestions")
async def get_question_ai_suggestions(
    question_text: str = Query(..., description="Texto da pergunta"),
    token: str = Depends(get_valid_token)
):
    """Sugestões de resposta com IA."""
    result = await questions_service.get_automated_answer_suggestions(token, question_text)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


# ============================
# Inventory Service Endpoints
# ============================

@router.get("/inventory_service/health")
async def inventory_health():
    """Health check do serviço de inventário."""
    return await inventory_service.health_check()

@router.get("/inventory_service/inventory")
async def list_inventory(
    user_id: str = Query(..., description="ID do vendedor"),
    offset: int = Query(0),
    limit: int = Query(50),
    low_stock: bool = Query(False, description="Apenas itens com estoque baixo"),
    token: str = Depends(get_valid_token)
):
    """Lista inventário."""
    filters = {}
    if low_stock:
        filters["low_stock"] = True
    
    result = await inventory_service.list_items(token, user_id, offset, limit, filters)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "success": True,
        "data": result.data,
        "pagination": {
            "total": result.total,
            "offset": result.offset,
            "limit": result.limit,
            "has_next": result.has_next
        },
        "metadata": result.metadata
    }

@router.get("/inventory_service/alerts")
async def get_stock_alerts(
    user_id: str = Query(..., description="ID do vendedor"),
    token: str = Depends(get_valid_token)
):
    """Alertas de estoque."""
    result = await inventory_service.get_stock_alerts(token, user_id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


# ============================
# Reputation Service Endpoints
# ============================

@router.get("/reputation_service/health")
async def reputation_health():
    """Health check do serviço de reputação."""
    return await reputation_service.health_check()

@router.get("/reputation_service/reputation/{user_id}")
async def get_reputation(
    user_id: str,
    token: str = Depends(get_valid_token)
):
    """Dados de reputação."""
    result = await reputation_service.get_item_details(token, user_id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result

@router.get("/reputation_service/analytics")
async def get_reputation_analytics(
    user_id: str = Query(..., description="ID do vendedor"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    token: str = Depends(get_valid_token)
):
    """Analytics de reputação."""
    result = await reputation_service.get_reputation_analytics(token, user_id, date_from, date_to)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result


# ============================
# Global Service Status
# ============================

@router.get("/status")
async def get_all_services_status():
    """Status de todos os serviços ML."""
    services = [
        ("orders_service", orders_service),
        ("shipments_service", shipments_service),
        ("messages_service", messages_service),
        ("questions_service", questions_service),
        ("inventory_service", inventory_service),
        ("reputation_service", reputation_service)
    ]
    
    statuses = {}
    for service_name, service in services:
        try:
            health_check = await service.health_check()
            statuses[service_name] = {
                "status": "healthy" if health_check.success else "unhealthy",
                "details": health_check.data
            }
        except Exception as e:
            statuses[service_name] = {
                "status": "error",
                "error": str(e)
            }
    
    return {
        "success": True,
        "timestamp": "2024-01-15T10:30:00Z",
        "services": statuses
    }