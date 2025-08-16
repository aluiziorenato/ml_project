from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import Optional, List, Dict, Any
from app.database import get_session
from app.routers.meli_routes import get_valid_token
from app.services.mercadolibre import (
    get_user_info, 
    get_user_products,
    get_item_details,
    get_items_batch,
    update_item,
    pause_item,
    activate_item,
    update_item_price,
    update_item_stock,
    get_user_campaigns,
    get_item_visits,
    search_items_by_seller
)
from pydantic import BaseModel
import logging
import asyncio
import httpx

logger = logging.getLogger("app.anuncios")
router = APIRouter(prefix="/api/anuncios", tags=["anuncios"])

# ============================
# Pydantic Models
# ============================

class AdUpdateRequest(BaseModel):
    price: Optional[float] = None
    available_quantity: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    pictures: Optional[List[Dict]] = None
    attributes: Optional[List[Dict]] = None

class AdActionRequest(BaseModel):
    action: str  # "pause", "activate", "update_price", "update_stock"
    value: Optional[Any] = None  # Para valores específicos (preço, estoque)

class FilterRequest(BaseModel):
    category_id: Optional[str] = None
    status: Optional[str] = None  # active, paused, closed
    listing_type_id: Optional[str] = None  # gold_special, gold_pro, etc
    shipping_mode: Optional[str] = None  # me2, not_specified, custom
    has_campaigns: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    search: Optional[str] = None  # Busca por título

class AIOptimizationRequest(BaseModel):
    original_text: str
    target_audience: Optional[str] = "general"
    product_category: Optional[str] = "electronics"
    optimization_goal: Optional[str] = "conversions"
    keywords: Optional[List[str]] = []
    segment: Optional[str] = "millennial"
    budget_range: Optional[str] = "medium"
    priority_metrics: Optional[List[str]] = ["seo", "readability", "compliance"]

# ============================
# Rotas Principais
# ============================

@router.get("/list")
async def list_ads(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    token: str = Depends(get_valid_token)
):
    """
    Lista todos os anúncios do usuário com detalhes completos.
    
    Retorna informações como:
    - Detalhes básicos (título, preço, estoque, status)
    - Categoria e modalidade
    - Tipo de frete
    - Campanhas ativas
    - Estatísticas de performance
    """
    try:
        # Primeiro busca informações do usuário
        user_data = await get_user_info(token)
        user_id = str(user_data.get("id"))
        
        # Busca lista básica de produtos
        products_response = await get_user_products(token, user_id)
        item_ids = products_response.get("results", [])
        
        if not item_ids:
            return {
                "success": True,
                "ads": [],
                "total": 0,
                "user_id": user_id
            }
        
        # Aplica paginação
        paginated_ids = item_ids[offset:offset + limit]
        
        # Busca detalhes completos dos items em lote
        if len(paginated_ids) > 20:  # ML API limit for batch requests
            # Divide em lotes menores
            detailed_ads = []
            for i in range(0, len(paginated_ids), 20):
                batch_ids = paginated_ids[i:i + 20]
                batch_details = await get_items_batch(token, batch_ids)
                detailed_ads.extend(batch_details)
        else:
            detailed_ads = await get_items_batch(token, paginated_ids)
        
        # Busca campanhas do usuário
        try:
            campaigns_data = await get_user_campaigns(token, user_id)
            campaigns = campaigns_data.get("results", [])
        except Exception as e:
            logger.warning(f"Erro ao buscar campanhas: {e}")
            campaigns = []
        
        # Enriquece dados dos anúncios
        enriched_ads = []
        for ad in detailed_ads:
            if isinstance(ad, dict) and "body" in ad:
                ad_data = ad["body"]
            else:
                ad_data = ad
                
            # Adiciona informações de campanha
            ad_campaigns = [c for c in campaigns if c.get("product_id") == ad_data.get("id")]
            
            enriched_ad = {
                "id": ad_data.get("id"),
                "title": ad_data.get("title"),
                "price": ad_data.get("price"),
                "available_quantity": ad_data.get("available_quantity"),
                "sold_quantity": ad_data.get("sold_quantity", 0),
                "status": ad_data.get("status"),
                "condition": ad_data.get("condition"),
                "listing_type_id": ad_data.get("listing_type_id"),
                "permalink": ad_data.get("permalink"),
                "thumbnail": ad_data.get("thumbnail"),
                "pictures": ad_data.get("pictures", []),
                "category_id": ad_data.get("category_id"),
                "currency_id": ad_data.get("currency_id"),
                "shipping": ad_data.get("shipping", {}),
                "attributes": ad_data.get("attributes", []),
                "campaigns": ad_campaigns,
                "has_campaigns": len(ad_campaigns) > 0,
                "created_date": ad_data.get("date_created"),
                "last_updated": ad_data.get("last_updated")
            }
            enriched_ads.append(enriched_ad)
        
        return {
            "success": True,
            "ads": enriched_ads,
            "total": len(item_ids),
            "offset": offset,
            "limit": limit,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar anúncios: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao listar anúncios: {str(e)}")

@router.get("/{item_id}")
async def get_ad_details(
    item_id: str,
    token: str = Depends(get_valid_token)
):
    """
    Busca detalhes completos de um anúncio específico.
    """
    try:
        # Busca detalhes do item
        item_data = await get_item_details(token, item_id)
        
        # Busca estatísticas de visitas
        try:
            visits_data = await get_item_visits(token, item_id)
        except Exception as e:
            logger.warning(f"Erro ao buscar visitas para item {item_id}: {e}")
            visits_data = {}
        
        return {
            "success": True,
            "ad": item_data,
            "visits": visits_data
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do anúncio {item_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao buscar anúncio: {str(e)}")

@router.put("/{item_id}")
async def update_ad(
    item_id: str,
    update_data: AdUpdateRequest,
    token: str = Depends(get_valid_token)
):
    """
    Atualiza um anúncio com as informações fornecidas.
    """
    try:
        # Constrói dados de atualização
        update_dict = {}
        if update_data.price is not None:
            update_dict["price"] = update_data.price
        if update_data.available_quantity is not None:
            update_dict["available_quantity"] = update_data.available_quantity
        if update_data.title is not None:
            update_dict["title"] = update_data.title
        if update_data.description is not None:
            update_dict["description"] = update_data.description
        if update_data.pictures is not None:
            update_dict["pictures"] = update_data.pictures
        if update_data.attributes is not None:
            update_dict["attributes"] = update_data.attributes
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        # Atualiza o item
        updated_item = await update_item(token, item_id, update_dict)
        
        return {
            "success": True,
            "updated_ad": updated_item,
            "message": f"Anúncio {item_id} atualizado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar anúncio {item_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar anúncio: {str(e)}")

@router.post("/{item_id}/action")
async def perform_ad_action(
    item_id: str,
    action_data: AdActionRequest,
    token: str = Depends(get_valid_token)
):
    """
    Executa ações diretas no anúncio (pausar, ativar, atualizar preço/estoque).
    """
    try:
        action = action_data.action.lower()
        
        if action == "pause":
            result = await pause_item(token, item_id)
            message = f"Anúncio {item_id} pausado com sucesso"
            
        elif action == "activate":
            result = await activate_item(token, item_id)
            message = f"Anúncio {item_id} ativado com sucesso"
            
        elif action == "update_price":
            if action_data.value is None:
                raise HTTPException(status_code=400, detail="Valor do preço é obrigatório")
            result = await update_item_price(token, item_id, float(action_data.value))
            message = f"Preço do anúncio {item_id} atualizado para {action_data.value}"
            
        elif action == "update_stock":
            if action_data.value is None:
                raise HTTPException(status_code=400, detail="Valor do estoque é obrigatório")
            result = await update_item_stock(token, item_id, int(action_data.value))
            message = f"Estoque do anúncio {item_id} atualizado para {action_data.value}"
            
        else:
            raise HTTPException(status_code=400, detail=f"Ação '{action}' não suportada")
        
        return {
            "success": True,
            "action": action,
            "result": result,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Erro ao executar ação {action_data.action} no anúncio {item_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao executar ação: {str(e)}")

@router.post("/filter")
async def filter_ads(
    filters: FilterRequest,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    token: str = Depends(get_valid_token)
):
    """
    Filtra anúncios com base nos critérios fornecidos.
    """
    try:
        user_data = await get_user_info(token)
        user_id = str(user_data.get("id"))
        
        # Constrói filtros para a API do ML
        search_filters = {}
        if filters.category_id:
            search_filters["category"] = filters.category_id
        if filters.listing_type_id:
            search_filters["listing_type"] = filters.listing_type_id
        
        # Busca com filtros básicos
        search_results = await search_items_by_seller(
            token, user_id, search_filters, offset, limit
        )
        
        # Se não há resultados básicos, retorna vazio
        if not search_results.get("results"):
            return {
                "success": True,
                "ads": [],
                "total": 0,
                "filters_applied": filters.dict()
            }
        
        # Busca detalhes completos
        item_ids = [item["id"] for item in search_results["results"]]
        detailed_ads = await get_items_batch(token, item_ids)
        
        # Aplica filtros adicionais localmente
        filtered_ads = []
        for ad in detailed_ads:
            if isinstance(ad, dict) and "body" in ad:
                ad_data = ad["body"]
            else:
                ad_data = ad
            
            # Filtro por status
            if filters.status and ad_data.get("status") != filters.status:
                continue
                
            # Filtro por preço
            price = ad_data.get("price", 0)
            if filters.min_price and price < filters.min_price:
                continue
            if filters.max_price and price > filters.max_price:
                continue
                
            # Filtro por estoque
            stock = ad_data.get("available_quantity", 0)
            if filters.min_stock and stock < filters.min_stock:
                continue
            if filters.max_stock and stock > filters.max_stock:
                continue
                
            # Filtro por modo de envio
            if filters.shipping_mode:
                shipping = ad_data.get("shipping", {})
                mode = shipping.get("mode", "not_specified")
                if mode != filters.shipping_mode:
                    continue
                    
            # Filtro por busca no título
            if filters.search:
                title = ad_data.get("title", "").lower()
                if filters.search.lower() not in title:
                    continue
            
            filtered_ads.append(ad_data)
        
        return {
            "success": True,
            "ads": filtered_ads,
            "total": len(filtered_ads),
            "filters_applied": filters.dict()
        }
        
    except Exception as e:
        logger.error(f"Erro ao filtrar anúncios: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao filtrar anúncios: {str(e)}")

@router.get("/stats/summary")
async def get_ads_summary(token: str = Depends(get_valid_token)):
    """
    Retorna resumo estatístico dos anúncios do usuário.
    """
    try:
        user_data = await get_user_info(token)
        user_id = str(user_data.get("id"))
        
        # Busca lista básica
        products_response = await get_user_products(token, user_id)
        item_ids = products_response.get("results", [])
        
        if not item_ids:
            return {
                "success": True,
                "summary": {
                    "total_ads": 0,
                    "active_ads": 0,
                    "paused_ads": 0,
                    "total_stock": 0,
                    "avg_price": 0,
                    "categories": {}
                }
            }
        
        # Busca detalhes em lotes
        all_ads = []
        for i in range(0, len(item_ids), 20):
            batch_ids = item_ids[i:i + 20]
            batch_details = await get_items_batch(token, batch_ids)
            all_ads.extend(batch_details)
        
        # Calcula estatísticas
        total_ads = len(all_ads)
        active_ads = 0
        paused_ads = 0
        total_stock = 0
        total_price = 0
        categories = {}
        
        for ad in all_ads:
            if isinstance(ad, dict) and "body" in ad:
                ad_data = ad["body"]
            else:
                ad_data = ad
                
            status = ad_data.get("status", "")
            if status == "active":
                active_ads += 1
            elif status == "paused":
                paused_ads += 1
                
            stock = ad_data.get("available_quantity", 0)
            total_stock += stock
            
            price = ad_data.get("price", 0)
            total_price += price
            
            category = ad_data.get("category_id", "unknown")
            categories[category] = categories.get(category, 0) + 1
        
        avg_price = total_price / total_ads if total_ads > 0 else 0
        
        return {
            "success": True,
            "summary": {
                "total_ads": total_ads,
                "active_ads": active_ads,
                "paused_ads": paused_ads,
                "closed_ads": total_ads - active_ads - paused_ads,
                "total_stock": total_stock,
                "avg_price": round(avg_price, 2),
                "categories": categories
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao buscar resumo: {str(e)}")

# ============================
# Endpoints de Otimização IA
# ============================

@router.post("/{item_id}/optimize")
async def optimize_ad_with_ai(
    item_id: str,
    optimization_request: AIOptimizationRequest,
    token: str = Depends(get_valid_token)
):
    """
    Otimiza um anúncio usando o serviço de IA.
    """
    try:
        # Busca detalhes atuais do item
        item_data = await get_item_details(token, item_id)
        
        # Configura dados para otimização IA
        ai_request = {
            "original_text": optimization_request.original_text or item_data.get("title", ""),
            "target_audience": optimization_request.target_audience,
            "product_category": optimization_request.product_category,
            "optimization_goal": optimization_request.optimization_goal,
            "keywords": optimization_request.keywords,
            "segment": optimization_request.segment,
            "budget_range": optimization_request.budget_range,
            "priority_metrics": optimization_request.priority_metrics
        }
        
        # Chama serviço de otimização IA
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://optimizer_ai:8003/api/optimize-copy",
                json=ai_request
            )
            response.raise_for_status()
            ai_result = response.json()
        
        return {
            "success": True,
            "original_item": item_data,
            "optimization": ai_result,
            "item_id": item_id
        }
        
    except Exception as e:
        logger.error(f"Erro ao otimizar anúncio {item_id} com IA: {e}")
        raise HTTPException(status_code=400, detail=f"Erro na otimização IA: {str(e)}")

@router.post("/{item_id}/apply-optimization")
async def apply_ai_optimization(
    item_id: str,
    optimized_data: Dict[str, Any],
    token: str = Depends(get_valid_token)
):
    """
    Aplica otimização IA a um anúncio específico.
    """
    try:
        # Atualiza o item com dados otimizados
        updated_item = await update_item(token, item_id, optimized_data)
        
        return {
            "success": True,
            "updated_item": updated_item,
            "message": f"Otimização aplicada ao anúncio {item_id}"
        }
        
    except Exception as e:
        logger.error(f"Erro ao aplicar otimização ao anúncio {item_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao aplicar otimização: {str(e)}")

@router.post("/generate-keywords")
async def generate_keywords_for_ad(
    request: Dict[str, Any],
    token: str = Depends(get_valid_token)
):
    """
    Gera sugestões de palavras-chave para um produto usando IA.
    """
    try:
        # Chama serviço de sugestão de palavras-chave
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://optimizer_ai:8003/api/keywords/suggest",
                json=request
            )
            response.raise_for_status()
            keywords_result = response.json()
        
        return {
            "success": True,
            "keywords": keywords_result
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar palavras-chave: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao gerar palavras-chave: {str(e)}")

@router.post("/bulk-optimize")
async def bulk_optimize_ads(
    item_ids: List[str],
    optimization_request: AIOptimizationRequest,
    token: str = Depends(get_valid_token)
):
    """
    Otimiza múltiplos anúncios em lote usando IA.
    """
    try:
        optimization_results = []
        
        for item_id in item_ids:
            try:
                # Otimiza cada item individualmente
                item_result = await optimize_ad_with_ai(item_id, optimization_request, token)
                optimization_results.append({
                    "item_id": item_id,
                    "success": True,
                    "optimization": item_result["optimization"]
                })
            except Exception as e:
                optimization_results.append({
                    "item_id": item_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful_optimizations = [r for r in optimization_results if r["success"]]
        failed_optimizations = [r for r in optimization_results if not r["success"]]
        
        return {
            "success": True,
            "total_processed": len(item_ids),
            "successful": len(successful_optimizations),
            "failed": len(failed_optimizations),
            "results": optimization_results
        }
        
    except Exception as e:
        logger.error(f"Erro na otimização em lote: {e}")
        raise HTTPException(status_code=400, detail=f"Erro na otimização em lote: {str(e)}")