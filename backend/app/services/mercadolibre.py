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

ML_CLIENT_ID: str = os.getenv("ML_CLIENT_ID", "")
ML_CLIENT_SECRET: str = os.getenv("ML_CLIENT_SECRET", "")
ML_REDIRECT_URI: str = os.getenv("ML_REDIRECT_URI", "")
ML_AUTH_URL: str = os.getenv("ML_AUTH_URL", "https://auth.mercadolibre.com/authorization")
ML_TOKEN_URL: str = os.getenv("ML_TOKEN_URL", "https://api.mercadolibre.com/oauth/token")
ML_SITE_ID: str = os.getenv("ML_SITE_ID", "MLB")


# PKCE helpers
def generate_code_verifier(length: int = 64) -> str:
    if length < 43:
        length = 43
    if length > 128:
        length = 128
    verifier = secrets.token_urlsafe(length)
    return verifier[:length]


def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return challenge


# Authorization URL builder
def build_authorization_url(state: str, code_challenge: str, redirect_uri: Optional[str] = None, site_id: Optional[str] = None) -> str:
    redirect = redirect_uri or ML_REDIRECT_URI
    site = site_id or ML_SITE_ID

    params = {
        "response_type": "code",
        "client_id": ML_CLIENT_ID,
        "redirect_uri": redirect,
        "site_id": site,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    return f"{ML_AUTH_URL}?{urlencode(params)}"


# Exchange code -> token
async def exchange_code_for_token(code: str, code_verifier: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    redirect = redirect_uri or ML_REDIRECT_URI
    data = {
        "grant_type": "authorization_code",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect,
        "code_verifier": code_verifier,
    }

    logger.info("Exchanging code for token; POST %s", ML_TOKEN_URL)
    logger.debug("Token request payload: %s", {k: ("<hidden>" if k == "client_secret" else v) for k, v in data.items()})

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(ML_TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
            resp.raise_for_status()
            logger.info("Token exchange success (status=%s)", resp.status_code)
            return resp.json()
        except httpx.HTTPStatusError as exc:
            text = exc.response.text
            logger.error("Token exchange HTTP error %s: %s", exc.response.status_code, text)
            raise HTTPException(status_code=502, detail=f"token exchange failed: {text}")
        except Exception as exc:
            logger.exception("Unexpected error during token exchange")
            raise HTTPException(status_code=502, detail=f"token exchange failed: {exc}")


# Refresh token
async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    data = {
        "grant_type": "refresh_token",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    logger.info("Refreshing access token")
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(ML_TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp.raise_for_status()
        return resp.json()


# Save token to DB
def _save_or_update_token(session: Session, tokens: dict, user_id: Optional[int], expires_at):
    existing = None
    if user_id is not None:
        existing = session.exec(select(MeliToken).where(MeliToken.user_id == user_id)).first()

    if existing is None:
        token = MeliToken(
            user_id=user_id,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            token_type=tokens.get("token_type"),
            scope=tokens.get("scope"),
            expires_at=expires_at,
        )
        session.add(token)
    else:
        existing.access_token = tokens.get("access_token")
        existing.refresh_token = tokens.get("refresh_token")
        existing.token_type = tokens.get("token_type")
        existing.scope = tokens.get("scope")
        existing.expires_at = expires_at
    session.commit()


def save_token_to_db(tokens: dict, user_id: Optional[int] = None, session: Optional[Session] = None):
    expires_at = None
    if "expires_in" in tokens and tokens.get("expires_in") is not None:
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=int(tokens["expires_in"]))
        except Exception:
            expires_at = None

    if session is not None:
        _save_or_update_token(session, tokens, user_id, expires_at)
    else:
        with Session(engine) as s:
            _save_or_update_token(s, tokens, user_id, expires_at)


# Proxy helper (opcional)
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
