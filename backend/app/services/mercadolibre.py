# backend/app/services/mercadolibre.py
import os
from urllib.parse import urlencode
from datetime import datetime, timedelta
import httpx
import requests

from ..models.meli_token import MeliToken
from ..db import get_session  # função que retorna sessão SQLModel/SQLAlchemy
from fastapi import HTTPException

def proxy_api_request(method: str, url: str, headers=None, data=None):
    try:
        response = requests.request(method, url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

ML_CLIENT_ID = os.getenv("ML_CLIENT_ID") or os.getenv("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI")
ML_AUTH_URL = os.getenv("ML_AUTH_URL", "https://auth.mercadolibre.com.br/authorization")
ML_TOKEN_URL = os.getenv("ML_TOKEN_URL", "https://api.mercadolibre.com/oauth/token")

def build_authorization_url(state: str | None = None, site_id: str = "MLB"):
    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": ML_REDIRECT_URI,
        "site_id": site_id
    }
    if state:
        params["state"] = state
    return f"{ML_AUTH_URL}?{urlencode(params)}"

async def exchange_code_for_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(ML_TOKEN_URL, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"})
        r.raise_for_status()
        return r.json()

async def refresh_access_token(refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(ML_TOKEN_URL, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"})
        r.raise_for_status()
        return r.json()

def save_token_to_db(tokens: dict, user_id: str | None = None):
    """
    tokens is dict returned by ML: access_token, refresh_token, expires_in, token_type, scope
    """
    expires_at = None
    if "expires_in" in tokens:
        expires_at = datetime.utcnow() + timedelta(seconds=int(tokens["expires_in"]))
    session = get_session()
    with session as s:
        # você pode buscar por user_id ou por refresh_token existente
        existing = None
        if user_id:
            existing = s.query(MeliToken).filter(MeliToken.user_id == user_id).first()
        if existing is None:
            token = MeliToken(
                user_id=user_id,
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token"),
                token_type=tokens.get("token_type"),
                scope=tokens.get("scope"),
                expires_at=expires_at
            )
            s.add(token)
        else:
            existing.access_token = tokens.get("access_token")
            existing.refresh_token = tokens.get("refresh_token")
            existing.token_type = tokens.get("token_type")
            existing.scope = tokens.get("scope")
            existing.expires_at = expires_at
        s.commit()
