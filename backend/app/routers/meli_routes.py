from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.database import get_session
from app.models.meli_token import MeliToken
from app.models.oauth_token import OAuthToken
from app.crud.oauth_tokens import get_latest_token
from app.services.mercadolibre import get_user_info, get_user_products
import logging

logger = logging.getLogger("app.meli_routes")
router = APIRouter()

def get_valid_token(session: Session = Depends(get_session)) -> str:
    """
    Helper para obter um token válido do Mercado Livre.
    Procura primeiro em MeliToken, depois em OAuthToken.
    """
    # Tenta buscar token na tabela MeliToken
    meli_token = session.query(MeliToken).order_by(MeliToken.created_at.desc()).first()
    if meli_token and meli_token.access_token:
        return meli_token.access_token
    
    # Fallback: busca token na tabela OAuthToken
    oauth_token = session.query(OAuthToken).order_by(OAuthToken.created_at.desc()).first()
    if oauth_token and oauth_token.access_token:
        return oauth_token.access_token
    
    raise HTTPException(status_code=404, detail="Nenhum token válido encontrado. Faça login no Mercado Livre primeiro.")

@router.get("/tokens")
def get_tokens(session: Session = Depends(get_session)):
    """
    Endpoint para obter informações dos tokens salvos.
    """
    token = session.query(MeliToken).order_by(MeliToken.created_at.desc()).first()
    if not token:
        raise HTTPException(status_code=404, detail="No token found")
    return {
        "access_token": token.access_token,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None
    }

@router.get("/user")
async def get_authenticated_user(token: str = Depends(get_valid_token)):
    """
    Endpoint para obter dados do usuário autenticado no Mercado Livre.
    """
    try:
        user_data = await get_user_info(token)
        return {
            "success": True,
            "user": user_data
        }
    except Exception as e:
        logger.error(f"Erro ao buscar dados do usuário: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao consultar dados do usuário: {str(e)}")

@router.get("/products")
async def get_user_products_endpoint(token: str = Depends(get_valid_token)):
    """
    Endpoint para obter produtos do vendedor autenticado no Mercado Livre.
    """
    try:
        # Primeiro obtém os dados do usuário para pegar o ID
        user_data = await get_user_info(token)
        user_id = user_data.get("id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Não foi possível obter ID do usuário")
        
        # Busca os produtos do usuário
        products_data = await get_user_products(token, str(user_id))
        return {
            "success": True,
            "user_id": user_id,
            "products": products_data
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produtos do usuário: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao consultar produtos: {str(e)}")
