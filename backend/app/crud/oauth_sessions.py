from sqlmodel import select
from sqlmodel import Session
from ..models import OAuthSession
from datetime import datetime, timedelta

def create_oauth_session(session: Session, oauth_session: OAuthSession) -> OAuthSession:
    session.add(oauth_session)
    session.commit()
    session.refresh(oauth_session)
    return oauth_session
def get_oauth_session(session: Session, session_id: int) -> OAuthSession | None:
    return session.get(OAuthSession, session_id)
def find_by_state(session: Session, state: str) -> OAuthSession | None:
    return session.exec(select(OAuthSession).where(OAuthSession.state == state)).first()
def update_tokens(session: Session, session_id: int, access_token: str, refresh_token: str, expires_in: int, token_type: str):
    oauth = session.get(OAuthSession, session_id)
    if not oauth:
        return None
    oauth.access_token = access_token
    oauth.refresh_token = refresh_token
    oauth.token_type = token_type
    oauth.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    session.add(oauth)
    session.commit()
    session.refresh(oauth)
    return oauth
