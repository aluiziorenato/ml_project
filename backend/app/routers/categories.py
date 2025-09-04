"""
Categories routes for product categorization.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Dict
from app.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.services.mercadolibre import get_categories as get_ml_categories
import logging

logger = logging.getLogger("app.routers.categories")
router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/")
async def get_categories(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[Dict]:
    """
    Get available product categories from Mercado Libre.
    
    Returns a list of categories that can be used for product classification.
    """
    try:
        # For now, return static categories. In a real implementation,
        # this would fetch from Mercado Libre API
        categories = [
            {"id": "MLB1132", "name": "Telefones e Celulares"},
            {"id": "MLB1144", "name": "Eletrodomésticos"},
            {"id": "MLB1196", "name": "Música, Filmes e Seriados"},
            {"id": "MLB1276", "name": "Esportes e Fitness"},
            {"id": "MLB1384", "name": "Bebês"},
            {"id": "MLB1403", "name": "Industrias e Escritórios"},
            {"id": "MLB1430", "name": "Roupas e Acessórios"},
            {"id": "MLB1499", "name": "Beleza e Cuidado Pessoal"},
            {"id": "MLB1574", "name": "Casa, Móveis e Decoração"},
            {"id": "MLB1648", "name": "Informática"},
            {"id": "MLB1953", "name": "Ferramentas"},
            {"id": "MLB3937", "name": "Eletrônicos, Áudio e Vídeo"},
            {"id": "MLB5726", "name": "Livros, Revistas e Comics"},
            {"id": "MLB9304", "name": "Antiguidades e Coleções"},
            {"id": "MLB264586", "name": "Saúde"},
        ]
        
        logger.info(f"Categories retrieved for user {current_user.email}")
        return categories
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@router.get("/{category_id}")
async def get_category_details(
    category_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict:
    """
    Get details for a specific category.
    """
    try:
        # Static category details for testing
        category_details = {
            "id": category_id,
            "name": f"Category {category_id}",
            "path_from_root": [
                {"id": "MLB", "name": "Brasil"},
                {"id": category_id, "name": f"Category {category_id}"}
            ],
            "children_categories": [],
            "attribute_types": "required_attributes",
            "settings": {
                "adult_content": False,
                "buying_allowed": True,
                "buying_modes": ["buy_it_now", "auction"],
                "catalog_domain": "active",
                "coverage_areas": "all",
                "currencies": ["BRL"],
                "fragile": False,
                "immediate_payment": "required",
                "item_conditions": ["new", "used"],
                "items_reviews_allowed": True,
                "listing_allowed": True,
                "max_description_length": 50000,
                "max_pictures_per_item": 12,
                "max_sub_title_length": 70,
                "max_title_length": 60,
                "max_variations_allowed": 200,
                "maximum_price": None,
                "minimum_price": 1,
                "mirror_category": None,
                "mirror_master_category": None,
                "mirror_slave_categories": [],
                "price": "required",
                "reservation_allowed": "not_allowed",
                "restrictions": [],
                "rounded_address": False,
                "seller_contact_allowed": True,
                "shipping_modes": ["custom", "me1", "me2"],
                "shipping_options": ["free", "custom"],
                "shipping_profile": "optional",
                "show_contact_information": True,
                "simple_shipping": "required",
                "stock": "required",
                "sub_vertical": None,
                "subscribable": False,
                "tags": [],
                "vertical": "marketplace",
                "vip_subdomain": "marketplace",
                "buyer_protection_programs": ["mercado_pago"]
            }
        }
        
        logger.info(f"Category details retrieved for {category_id} by user {current_user.email}")
        return category_details
        
    except Exception as e:
        logger.error(f"Error retrieving category details for {category_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve category details")