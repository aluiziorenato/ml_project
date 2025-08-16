import os
import base64
import hashlib
import secrets
import httpx
import logging
from urllib.parse import urlencode
from typing import Optional, Dict
from sqlmodel import Session
from app.models import OAuthToken

logger = logging.getLogger("app.mercadolibre")
logger.setLevel(logging.INFO)

# ============================
# Configurações do Mercado Livre
# ============================
ML_CLIENT_ID = os.getenv("ML_CLIENT_ID", "")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET", "")
ML_AUTH_URL = os.getenv("ML_AUTH_URL", "https://auth.mercadolibre.com.br/authorization")
ML_TOKEN_URL = os.getenv("ML_TOKEN_URL", "https://api.mercadolibre.com/oauth/token")
ML_API_URL = os.getenv("ML_API_URL", "https://api.mercadolibre.com")
ML_SITE_ID = os.getenv("ML_SITE_ID", "MLB")
ML_SCOPES = os.getenv("ML_SCOPES", "offline_access read write")
ML_USE_PKCE = os.getenv("ML_USE_PKCE", "true").lower() == "true"
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI", "").strip().rstrip("/")

PKCE_CODE_CHALLENGE_METHOD = os.getenv("PKCE_CODE_CHALLENGE_METHOD", "S256")

# ============================
# Funções PKCE
# ============================

def generate_code_verifier(length: int = 64) -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode("utf-8").rstrip("=")

def generate_code_challenge(code_verifier: str) -> str:
    if PKCE_CODE_CHALLENGE_METHOD.upper() != "S256":
        raise ValueError("Somente o método S256 é suportado")
    sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")

# ============================
# Construir URL de autorização
# ============================

def build_authorization_url(state: str, code_challenge: str, redirect_uri: Optional[str] = None) -> str:
    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": redirect_uri or ML_REDIRECT_URI,
        "state": state,
        "site_id": ML_SITE_ID,
        "scope": ML_SCOPES,
    }
    if ML_USE_PKCE:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = PKCE_CODE_CHALLENGE_METHOD

    auth_url = f"{ML_AUTH_URL}?{urlencode(params)}"
    logger.info(f"[MercadoLibre] Authorization URL: {auth_url}")
    return auth_url

# ============================
# Troca código por token
# ============================

async def exchange_code_for_token(code: str, code_verifier: str, redirect_uri: Optional[str] = None) -> Dict:
    """
    Troca o 'authorization code' pelo 'access token' e 'refresh token'.
    Usa PKCE se habilitado.
    """
    payload = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri or ML_REDIRECT_URI,
    }
    if ML_USE_PKCE:
        payload["code_verifier"] = code_verifier

    logger.info("[MercadoLibre] Exchange code for token — sending request to ML API")
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(ML_TOKEN_URL, data=payload, headers={"Accept": "application/json"})
        resp.raise_for_status()
        tokens = resp.json()
        logger.info("[MercadoLibre] Tokens recebidos com sucesso")
        return tokens

# ============================
# Refresh token
# ============================

async def refresh_access_token(refresh_token: str) -> Dict:
    payload = {
        "grant_type": "refresh_token",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(ML_TOKEN_URL, data=payload, headers={"Accept": "application/json"})
        resp.raise_for_status()
        return resp.json()

# ============================
# Salvar tokens no banco
# ============================

def save_token_to_db(tokens: Dict, user_id: Optional[int], session: Session):
    """
    Salva ou atualiza o token no banco.
    """
    logger.info(f"[MercadoLibre] Salvando tokens no banco para user_id={user_id}")
    token_entry = OAuthToken(
        user_id=user_id,
        access_token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        token_type=tokens.get("token_type", "bearer"),
        expires_in=tokens.get("expires_in"),
        scope=tokens.get("scope"),
    )
    session.add(token_entry)
    session.commit()
    session.refresh(token_entry)
    return token_entry

# ============================
# Funções de API do Mercado Livre
# ============================

async def get_user_info(access_token: str) -> Dict:
    """
    Busca informações do usuário autenticado no Mercado Livre.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info("[MercadoLibre] Buscando informações do usuário")
        response = await client.get(f"{ML_API_URL}/users/me", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        logger.info(f"[MercadoLibre] Dados do usuário obtidos: ID {user_data.get('id')}")
        return user_data

async def get_user_products(access_token: str, user_id: str) -> Dict:
    """
    Busca produtos do vendedor autenticado no Mercado Livre.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info(f"[MercadoLibre] Buscando produtos do usuário {user_id}")
        response = await client.get(f"{ML_API_URL}/users/{user_id}/items/search", headers=headers)
        response.raise_for_status()
        products_data = response.json()
        logger.info(f"[MercadoLibre] {len(products_data.get('results', []))} produtos encontrados")
        return products_data

async def get_categories() -> Dict:
    """
    Busca categorias disponíveis no Mercado Livre.
    """
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info("[MercadoLibre] Buscando categorias")
        response = await client.get(f"{ML_API_URL}/sites/{ML_SITE_ID}/categories")
        response.raise_for_status()
        categories_data = response.json()
        logger.info(f"[MercadoLibre] {len(categories_data)} categorias encontradas")
        return categories_data

# ============================
# Funções Específicas para Gerenciamento de Anúncios
# ============================

async def get_item_details(access_token: str, item_id: str) -> Dict:
    """
    Busca detalhes completos de um item específico.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info(f"[MercadoLibre] Buscando detalhes do item {item_id}")
        response = await client.get(f"{ML_API_URL}/items/{item_id}", headers=headers)
        response.raise_for_status()
        item_data = response.json()
        logger.info(f"[MercadoLibre] Detalhes do item {item_id} obtidos")
        return item_data

async def get_items_batch(access_token: str, item_ids: list) -> Dict:
    """
    Busca detalhes de múltiplos items em lote.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    items_str = ",".join(item_ids)
    async with httpx.AsyncClient(timeout=30) as client:
        logger.info(f"[MercadoLibre] Buscando {len(item_ids)} items em lote")
        response = await client.get(f"{ML_API_URL}/items?ids={items_str}", headers=headers)
        response.raise_for_status()
        items_data = response.json()
        logger.info(f"[MercadoLibre] {len(items_data)} items obtidos em lote")
        return items_data

async def update_item(access_token: str, item_id: str, update_data: Dict) -> Dict:
    """
    Atualiza um item específico.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=30) as client:
        logger.info(f"[MercadoLibre] Atualizando item {item_id}")
        response = await client.put(f"{ML_API_URL}/items/{item_id}", 
                                  json=update_data, headers=headers)
        response.raise_for_status()
        updated_item = response.json()
        logger.info(f"[MercadoLibre] Item {item_id} atualizado com sucesso")
        return updated_item

async def pause_item(access_token: str, item_id: str) -> Dict:
    """
    Pausa um item (status = paused).
    """
    return await update_item(access_token, item_id, {"status": "paused"})

async def activate_item(access_token: str, item_id: str) -> Dict:
    """
    Ativa um item (status = active).
    """
    return await update_item(access_token, item_id, {"status": "active"})

async def update_item_price(access_token: str, item_id: str, new_price: float) -> Dict:
    """
    Atualiza apenas o preço de um item.
    """
    return await update_item(access_token, item_id, {"price": new_price})

async def update_item_stock(access_token: str, item_id: str, new_stock: int) -> Dict:
    """
    Atualiza apenas o estoque de um item.
    """
    return await update_item(access_token, item_id, {"available_quantity": new_stock})

async def get_user_campaigns(access_token: str, user_id: str) -> Dict:
    """
    Busca campanhas de publicidade do usuário.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info(f"[MercadoLibre] Buscando campanhas do usuário {user_id}")
        response = await client.get(f"{ML_API_URL}/advertising/campaigns", headers=headers)
        response.raise_for_status()
        campaigns_data = response.json()
        logger.info(f"[MercadoLibre] {len(campaigns_data.get('results', []))} campanhas encontradas")
        return campaigns_data

async def get_item_visits(access_token: str, item_id: str) -> Dict:
    """
    Busca estatísticas de visitas de um item.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info(f"[MercadoLibre] Buscando visitas do item {item_id}")
        response = await client.get(f"{ML_API_URL}/visits/items", 
                                  params={"item": item_id}, headers=headers)
        response.raise_for_status()
        visits_data = response.json()
        logger.info(f"[MercadoLibre] Estatísticas de visitas obtidas para item {item_id}")
        return visits_data

async def get_shipping_methods(access_token: str, category_id: str = None) -> Dict:
    """
    Busca métodos de envio disponíveis.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {}
    if category_id:
        params["category_id"] = category_id
    
    async with httpx.AsyncClient(timeout=20) as client:
        logger.info("[MercadoLibre] Buscando métodos de envio")
        response = await client.get(f"{ML_API_URL}/sites/{ML_SITE_ID}/shipping_methods", 
                                  params=params, headers=headers)
        response.raise_for_status()
        shipping_data = response.json()
        logger.info(f"[MercadoLibre] {len(shipping_data)} métodos de envio encontrados")
        return shipping_data

async def search_items_by_seller(access_token: str, seller_id: str, 
                                filters: Dict = None, offset: int = 0, limit: int = 50) -> Dict:
    """
    Busca items de um vendedor com filtros avançados.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "seller_id": seller_id,
        "offset": offset,
        "limit": limit
    }
    
    if filters:
        params.update(filters)
    
    async with httpx.AsyncClient(timeout=30) as client:
        logger.info(f"[MercadoLibre] Buscando items do vendedor {seller_id} com filtros")
        response = await client.get(f"{ML_API_URL}/sites/{ML_SITE_ID}/search", 
                                  params=params, headers=headers)
        response.raise_for_status()
        search_data = response.json()
        logger.info(f"[MercadoLibre] {search_data.get('paging', {}).get('total', 0)} items encontrados")
        return search_data
