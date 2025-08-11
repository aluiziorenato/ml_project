from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
##from ..services.mercadolibre import proxy_api_request
from ..models import OAuthSession
from ..auth import get_current_user

router = APIRouter(prefix="/api/proxy", tags=["proxy"])

@router.post('/')
async def proxy_call(endpoint_id: int, method: str = 'GET', path: str = '/', json_body: dict | None = None, session: Session = Depends(get_session), user=Depends(get_current_user)):
    oauth = session.exec(select(OAuthSession).where(OAuthSession.endpoint_id == endpoint_id)).first()
    if not oauth or not oauth.access_token:
        raise HTTPException(status_code=400, detail='No access token available for endpoint')
    res = await proxy_api_request(oauth.access_token, method, path, base_url="https://api.mercadolibre.com", headers=None, json_body=json_body)
    return res
