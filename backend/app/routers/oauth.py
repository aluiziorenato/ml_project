from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from ..services.mercadolibre import build_authorization_url, exchange_code_for_token, save_token_to_db

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

@router.get("/login")
def login(state: Optional[str] = None):
    # retorna uma URL para o frontend redirecionar (ou redireciona direto)
    url = build_authorization_url(state=state)
    # opcional: Redirect direto
    return RedirectResponse(url)

@router.get("/callback")
async def callback(code: Optional[str] = None, state: Optional[str] = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    try:
        tokens = await exchange_code_for_token(code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"token exchange failed: {e}")

    # se tiver usuário local, associe; aqui assumimos single app — sem user
    save_token_to_db(tokens, user_id=None)
    # redirecionar para frontend ou devolver JSON
    # se frontend local espera um redirect: redirect para página de sucesso
    return JSONResponse({"status":"ok", "tokens": {"access_token": tokens.get("access_token") }})
