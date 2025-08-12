# backend/app/api/oauth.py
import os
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session

from app.services.mercadolibre import (
    build_authorization_url,
    exchange_code_for_token,
    generate_code_verifier,
    generate_code_challenge,
    save_token_to_db
)
from app.crud.oauth_sessions import (
    save_oauth_session,
    get_oauth_session,
    delete_oauth_session
)
from app.db import get_session

ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI")

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

@router.get("/login")
def login(state: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Inicia fluxo OAuth com PKCE.
    """
    if not state:
        state = str(uuid4())

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    save_oauth_session(session, state, code_verifier)

    authorization_url = build_authorization_url(
        state=state,
        code_challenge=code_challenge,
        redirect_uri=ML_REDIRECT_URI
    )

    return RedirectResponse(url=authorization_url)


@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Callback do Mercado Livre após autorização.
    """
    if not code or not state:
        raise HTTPException(status_code=400, detail="Código ou estado ausente")

    oauth_session = get_oauth_session(session, state)
    if not oauth_session:
        raise HTTPException(status_code=400, detail="State inválido ou expirado")

    try:
        tokens = await exchange_code_for_token(
            code,
            oauth_session.code_verifier,
            redirect_uri=ML_REDIRECT_URI
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao trocar código por token: {e}")

    delete_oauth_session(session, state)
    save_token_to_db(tokens, user_id=None, session=session)

    return JSONResponse({
        "status": "ok",
        "tokens": {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token")
        }
    })
