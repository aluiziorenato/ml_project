from sqlmodel import Session, select
from app.models.oauth_session import OAuthSession

def save_oauth_session(session: Session, state: str, code_verifier: str):
    oauth_session = OAuthSession(state=state, code_verifier=code_verifier)
    session.add(oauth_session)
    session.commit()

def get_oauth_session(session: Session, state: str) -> OAuthSession | None:
    return session.exec(select(OAuthSession).where(OAuthSession.state == state)).first()

def delete_oauth_session(session: Session, state: str):
    oauth_session = get_oauth_session(session, state)
    if oauth_session:
        session.delete(oauth_session)
        session.commit()
