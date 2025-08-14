from sqlmodel import Session, select
from app.models.oauth_token import OAuthToken

def save_token_to_db(tokens: dict, user_id: int, session: Session):
    token_obj = OAuthToken(
        user_id=user_id,
        access_token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        expires_in=tokens.get("expires_in"),
        scope=tokens.get("scope"),
        token_type=tokens.get("token_type"),
    )
    session.add(token_obj)
    session.commit()
    session.refresh(token_obj)
    return token_obj

def get_latest_token(user_id: int, session: Session):
    return session.exec(
        select(OAuthToken)
        .where(OAuthToken.user_id == user_id)
        .order_by(OAuthToken.created_at.desc())
    ).first()
