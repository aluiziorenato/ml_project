import httpx
from urllib.parse import urlencode
from datetime import datetime, timedelta
from fastapi import HTTPException
from ..config import settings

AUTH_BASE = "https://auth.mercadolibre.com.ar/authorization"
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

async def build_authorization_url(redirect_uri: str, state: str, scope: str | None = None):
    params = {
        "response_type": "code",
        "client_id": settings.ml_client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    if scope:
        params["scope"] = scope
    return f"{AUTH_BASE}?{urlencode(params)}"

async def exchange_code_for_token(code: str, redirect_uri: str):
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.ml_client_id,
            "client_secret": settings.ml_client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        r = await client.post(TOKEN_URL, data=data, timeout=30)
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Token exchange failed: {r.text}")
        return r.json()

async def refresh_token(refresh_token: str):
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "refresh_token",
            "client_id": settings.ml_client_id,
            "client_secret": settings.ml_client_secret,
            "refresh_token": refresh_token,
        }
        r = await client.post(TOKEN_URL, data=data, timeout=30)
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Refresh failed: {r.text}")
        return r.json()

async def proxy_api_request(access_token: str, method: str, path: str, base_url: str = "https://api.mercadolibre.com", headers: dict | None = None, json_body: dict | None = None):
    headers = headers or {}
    headers.update({"Authorization": f"Bearer {access_token}"})
    url = base_url.rstrip("/") + path
    async with httpx.AsyncClient() as client:
        r = await client.request(method, url, headers=headers, json=json_body, timeout=60)
        content_type = r.headers.get("content-type","")
        if "application/json" in content_type:
            body = r.json()
        else:
            body = r.text
        return {"status_code": r.status_code, "body": body}
