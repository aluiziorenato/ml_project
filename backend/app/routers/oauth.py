from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from sqlmodel import Session
from uuid import uuid4

from ..services.mercadolibre import (
    build_authorization_url,
    exchange_code_for_token,
    generate_code_verifier,
    generate_code_challenge,
)
from ..crud.oauth_sessions import save_oauth_session, get_oauth_session, delete_oauth_session
from ..db import get_session

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

@router.get("/login")
def login(state: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Inicia fluxo OAuth com PKCE:
    - gera state se não informado
    - gera code_verifier e code_challenge
    - salva state + code_verifier no banco
    - retorna redirect para Mercado Livre com code_challenge
    """
    if not state:
        state = str(uuid4())  # gera state aleatório

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    save_oauth_session(session, state, code_verifier)

    url = build_authorization_url(state=state, code_challenge=code_challenge)
    return RedirectResponse(url)

@router.get("/callback")
async def callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    session: Session = Depends(get_session),
):
    from ..services.mercadolibre import save_token_to_db  # import local para evitar loop

    """
    Callback do ML após autorização:
    - valida presence de code e state
    - recupera code_verifier do banco usando state
    - troca código por token usando code_verifier
    - deleta sessão OAuth
    - salva token no banco
    - retorna tokens para frontend
    """
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    oauth_session = get_oauth_session(session, state)
    if not oauth_session:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    try:
        tokens = await exchange_code_for_token(code, oauth_session.code_verifier)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"token exchange failed: {e}")

    delete_oauth_session(session, state)
    save_token_to_db(tokens, user_id=None, session=session)

    return JSONResponse(
        {"status": "ok", "tokens": {"access_token": tokens.get("access_token")}}
    )
