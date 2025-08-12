# backend/app/services/mercadolibre.py
import os
import base64
import hashlib
import secrets
import logging
from urllib.parse import urlencode
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import httpx
import requests
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.meli_token import MeliToken
from app.db import engine

logger = logging.getLogger("mercadolibre")
logger.setLevel(logging.INFO)

# -------------------------------------------------------------------
# Carregar variáveis do .env
# -------------------------------------------------------------------
ML_CLIENT_ID = os.getenv("ML_CLIENT_ID")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI")
ML_AUTH_URL = os.getenv("ML_AUTH_URL", "https://auth.mercadolibre.com.br/authorization")
ML_TOKEN_URL = os.getenv("ML_TOKEN_URL", "https://api.mercadolibre.com/oauth/token")
ML_SITE_ID = os.getenv("ML_SITE_ID", "MLB")
ML_USE_PKCE = os.getenv("ML_USE_PKCE", "true").lower() == "true"
PKCE_CODE_CHALLENGE_METHOD = os.getenv("PKCE_CODE_CHALLENGE_METHOD", "S256")

# -------------------------------------------------------------------
# PKCE Helpers
# -------------------------------------------------------------------
def generate_code_verifier(length: int = 64) -> str:
    if length < 43:
        length = 43
    if length > 128:
        length = 128
    return secrets.token_urlsafe(length)[:length]

def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

# -------------------------------------------------------------------
# Montar URL de autorização
# -------------------------------------------------------------------
def build_authorization_url(
    state: str,
    code_challenge: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    site_id: Optional[str] = None
) -> str:
    redirect = redirect_uri or ML_REDIRECT_URI
    site = site_id or ML_SITE_ID

    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": redirect,
        "site_id": site,
        "state": state,
    }

    if ML_USE_PKCE and code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = PKCE_CODE_CHALLENGE_METHOD

    return f"{ML_AUTH_URL}?{urlencode(params)}"

# -------------------------------------------------------------------
# Trocar code por token
# -------------------------------------------------------------------
async def exchange_code_for_token(
    code: str,
    code_verifier: Optional[str] = None,
    redirect_uri: Optional[str] = None
) -> Dict[str, Any]:
    redirect = redirect_uri or ML_REDIRECT_URI

    data = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect,
    }

    if ML_USE_PKCE and code_verifier:
        data["code_verifier"] = code_verifier

    logger.info(f"Exchanging code for token at {ML_TOKEN_URL}")
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(
                ML_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=502, detail=f"Token exchange failed: {exc.response.text}")
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Unexpected error: {exc}")

# -------------------------------------------------------------------
# Refresh token
# -------------------------------------------------------------------
async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    data = {
        "grant_type": "refresh_token",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    logger.info("Refreshing access token")
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            ML_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        resp.raise_for_status()
        return resp.json()

# -------------------------------------------------------------------
# Salvar token no banco
# -------------------------------------------------------------------
def _save_or_update_token(session: Session, tokens: dict, user_id: Optional[int], expires_at):
    existing = session.exec(select(MeliToken).where(MeliToken.user_id == user_id)).first() if user_id else None

    if existing:
        existing.access_token = tokens.get("access_token")
        existing.refresh_token = tokens.get("refresh_token")
        existing.token_type = tokens.get("token_type")
        existing.scope = tokens.get("scope")
        existing.expires_at = expires_at
    else:
        session.add(MeliToken(
            user_id=user_id,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            token_type=tokens.get("token_type"),
            scope=tokens.get("scope"),
            expires_at=expires_at,
        ))
    session.commit()

def save_token_to_db(tokens: dict, user_id: Optional[int] = None, session: Optional[Session] = None):
    expires_at = None
    if tokens.get("expires_in"):
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=int(tokens["expires_in"]))
        except Exception:
            pass

    if session:
        _save_or_update_token(session, tokens, user_id, expires_at)
    else:
        with Session(engine) as s:
            _save_or_update_token(s, tokens, user_id, expires_at)

# -------------------------------------------------------------------
# Proxy para API externa
# -------------------------------------------------------------------
def proxy_api_request(method: str, url: str, headers=None, data=None, json_body=None):
    try:
        resp = requests.request(method, url, headers=headers, data=data, json=json_body, timeout=15.0)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error("Proxy request failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

__all__ = [
    "generate_code_verifier",
    "generate_code_challenge",
    "build_authorization_url",
    "exchange_code_for_token",
    "refresh_access_token",
    "save_token_to_db",
    "proxy_api_request",
]
