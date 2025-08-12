# backend/app/routers/oauth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from sqlmodel import Session
from uuid import uuid4
import logging
import os

from app.crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from app.db import get_session
from app.services.mercadolibre import (
    build_authorization_url,
    exchange_code_for_token,
    generate_code_verifier,
    generate_code_challenge,
    save_token_to_db,
)

logger = logging.getLogger("app.oauth")
logger.setLevel(logging.INFO)

ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI")  # lido do .env

router = APIRouter(prefix="/api/oauth", tags=["oauth"])


@router.get("/login")
def login(state: Optional[str] = None, session: Session = Depends(get_session)):
    """
    /api/oauth/login
    - gera state (UUID) e code_verifier
    - salva state + code_verifier em oauth_sessions
    - monta url de autorização com code_challenge (S256) e redireciona para ML
    """
    if not state:
        state = str(uuid4())

    # PKCE: gera code_verifier e code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # salva sessão PKCE (state -> code_verifier)
    save_oauth_session(session=session, state=state, code_verifier=code_verifier)

    # monta URL de autorização — usa ML_REDIRECT_URI do .env (exatamente o registrado no painel)
    authorization_url = build_authorization_url(state=state, code_challenge=code_challenge, redirect_uri=ML_REDIRECT_URI)

    logger.info("Generated authorization url: %s", authorization_url)
    # redireciona o usuário ao Mercado Livre
    return RedirectResponse(authorization_url)


@router.get("/callback")
async def callback(code: Optional[str] = None, state: Optional[str] = None, session: Session = Depends(get_session)):
    """
    /api/oauth/callback
    - recupera code_verifier pelo state salvo
    - troca code por token usando code_verifier
    - remove oauth_session
    - salva token no DB
    - devolve JSON com access_token (ou faz redirect ao frontend)
    """
    if not code or not state:
        raise HTTPException(status_code=400, detail="Código ou estado ausente")

    oauth_session = get_oauth_session(session=session, state=state)
    if not oauth_session:
        raise HTTPException(status_code=400, detail="State inválido ou expirado")

    try:
        tokens = await exchange_code_for_token(code=code, code_verifier=oauth_session.code_verifier, redirect_uri=ML_REDIRECT_URI)
    except Exception as e:
        logger.exception("Falha ao trocar código por token")
        raise HTTPException(status_code=502, detail=f"Falha na troca do código: {e}")

    # limpa sessão PKCE
    delete_oauth_session(session=session, state=state)

    # salva token no banco (usa a mesma session)
    save_token_to_db(tokens=tokens, user_id=None, session=session)

    # responda com JSON (ou redirecione para frontend se preferir)
    return JSONResponse({"status": "ok", "tokens": {"access_token": tokens.get("access_token"), "refresh_token": tokens.get("refresh_token")}})
