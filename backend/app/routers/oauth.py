import secrets
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..crud.oauth_sessions import create_oauth_session, find_by_state, update_tokens
from ..models import OAuthSession
from ..schemas import OAuthStartResponse
from ..services.mercadolibre import build_authorization_url, exchange_code_for_token
from ..config import settings
from ..auth import get_current_user

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

@router.post("/start", response_model=OAuthStartResponse)
async def oauth_start(endpoint_id: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    state = secrets.token_urlsafe(16)
    code_verifier = secrets.token_urlsafe(48)
    redirect_uri = f"{settings.app_base_url}/api/oauth/callback"
    oauth_session = OAuthSession(endpoint_id=endpoint_id, state=state, code_verifier=code_verifier)
    oauth_session = create_oauth_session(session, oauth_session)
    auth_url = await build_authorization_url(redirect_uri, state, scope=None)
    return {"authorization_url": auth_url, "oauth_session_id": oauth_session.id}

@router.get("/callback")
async def oauth_callback(code: str | None = None, state: str | None = None, session: Session = Depends(get_session)):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    oauth = find_by_state(session, state)
    if not oauth:
        raise HTTPException(status_code=404, detail="OAuth session not found")
    redirect_uri = f"{settings.app_base_url}/api/oauth/callback"
    token_data = await exchange_code_for_token(code, redirect_uri)
    update_tokens(session, oauth.id, token_data.get("access_token"), token_data.get("refresh_token"), token_data.get("expires_in", 3600), token_data.get("token_type", "Bearer"))
    frontend = settings.frontend_origin
    return {"success": True, "message": "Token obtained. You can close this window and return to the app."}
