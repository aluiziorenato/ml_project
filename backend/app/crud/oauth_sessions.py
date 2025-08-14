# backend/app/crud/oauth_sessions.py
from sqlmodel import Session, select
from typing import Optional

from app.models.oauth_session import OAuthSession

def save_oauth_session(session: Session, state: str, code_verifier: str, endpoint_id: Optional[int] = None):
    """
    Save or overwrite an OAuth session (state -> code_verifier).
    endpoint_id is optional.
    """
    # try update if exists
    existing = session.exec(select(OAuthSession).where(OAuthSession.state == state)).first()
    if existing:
        existing.code_verifier = code_verifier
        existing.endpoint_id = endpoint_id
    else:
        oauth_session = OAuthSession(state=state, code_verifier=code_verifier, endpoint_id=endpoint_id)
        session.add(oauth_session)
    session.commit()

def get_oauth_session(session: Session, state: str) -> Optional[OAuthSession]:
    return session.exec(select(OAuthSession).where(OAuthSession.state == state)).first()

def delete_oauth_session(session: Session, state: str):
    obj = get_oauth_session(session, state)
    if obj:
        session.delete(obj)
        session.commit()
