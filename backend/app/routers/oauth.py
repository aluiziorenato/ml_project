from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from sqlmodel import Session
from uuid import uuid4
import logging
import os

from app.db import get_session
from app.models.user import User
from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from app.crud.oauth_tokens import save_token_to_db
from app.services.mercadolibre import (
    build_authorization_url,
    exchange_code_for_token,
    generate_code_verifier,
    generate_code_challenge
)
from app.core.security import get_current_user  # função que retorna o usuário logado

logger = logging.getLogger("app.oauth")
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI", "").rstrip("/")

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

@router.get("/login")
def login(state: Optional[str] = None, session: Session = Depends(get_session)):
    if not state:
        state = str(uuid4())

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    save_oauth_session(session=session, state=state, code_verifier=code_verifier)
    authorization_url = build_authorization_url(state=state, code_challenge=code_challenge, redirect_uri=ML_REDIRECT_URI)
    logger.info(f"[OAuth] URL gerada: {authorization_url}")
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Código ou estado ausente")

    oauth_session = get_oauth_session(session=session, state=state)
    if not oauth_session:
        raise HTTPException(status_code=400, detail="State inválido ou expirado")

    tokens = await exchange_code_for_token(code=code, code_verifier=oauth_session.code_verifier, redirect_uri=ML_REDIRECT_URI)

    delete_oauth_session(session=session, state=state)
    save_token_to_db(tokens=tokens, user_id=current_user.id, session=session)

    return JSONResponse({"status": "ok", "tokens": tokens})
