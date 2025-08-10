from fastapi import APIRouter, HTTPException
from app.database import get_session
from app.models.meli_token import MeliToken


router = APIRouter()

@router.get("/tokens")
def get_tokens():
    session = get_session()
    with session as s:
        token = s.query(MeliToken).order_by(MeliToken.created_at.desc()).first()
        if not token:
            raise HTTPException(status_code=404, detail="No token found")
        return {
            "access_token": token.access_token,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None
        }
