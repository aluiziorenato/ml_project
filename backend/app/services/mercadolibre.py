import os
import base64
import hashlib
import secrets
from urllib.parse import urlencode
from datetime import datetime, timedelta
import httpx
import requests
from fastapi import HTTPException
from typing import Optional

from ..models.meli_token import MeliToken
from ..db import get_session
from sqlmodel import Session

ML_CLIENT_ID: str = os.getenv("ML_CLIENT_ID", "")
ML_CLIENT_SECRET: str = os.getenv("ML_CLIENT_SECRET", "")
ML_REDIRECT_URI: str = os.getenv("ML_REDIRECT_URI", "")
ML_AUTH_URL: str = os.getenv("ML_AUTH_URL", "https://auth.mercadolibre.com.br/authorization")
ML_TOKEN_URL: str = os.getenv("ML_TOKEN_URL", "https://api.mercadolibre.com/oauth/token")

def generate_code_verifier(length: int = 128) -> str:
    """
    Gera um code_verifier aleatório para PKCE (base64 url safe).
    """
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(length)).rstrip(b"=").decode("utf-8")
    return verifier[:length]  # garante tamanho máximo

def generate_code_challenge(code_verifier: str) -> str:
    """
    Gera code_challenge a partir do code_verifier usando SHA256 + base64 url safe.
    """
    sha256 = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(sha256).rstrip(b"=").decode("utf-8")
    return challenge

def build_authorization_url(state: Optional[str] = None, site_id: str = "MLB", code_challenge: Optional[str] = None) -> str:
    """
    Monta URL para autorizar no Mercado Livre com PKCE (code_challenge).
    """
    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": ML_REDIRECT_URI,
        "site_id": site_id
    }
def save_token_to_db(tokens: dict, user_id: Optional[str] = None, session: Optional[Session] = None):
    # implementação...


    if state:
        params["state"] = state
    if code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = "S256"  # obrigatório para PKCE

    return f"{ML_AUTH_URL}?{urlencode(params)}"

async def exchange_code_for_token(code: str, code_verifier: str) -> dict:
    """
    Troca o código de autorização por token usando PKCE (inclui code_verifier).
    """
    data = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ML_TOKEN_URL, 
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()

# refresh_access_token, save_token_to_db, _save_or_update_token e proxy_api_request permanecem iguais
