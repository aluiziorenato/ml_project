from sqlmodel import select
from sqlmodel import Session
from ..models import ApiEndpoint

def create_endpoint(session: Session, data: ApiEndpoint) -> ApiEndpoint:
    session.add(data)
    session.commit()
    session.refresh(data)
    return data
def get_endpoint(session: Session, endpoint_id: int) -> ApiEndpoint | None:
    return session.get(ApiEndpoint, endpoint_id)
def list_endpoints(session: Session) -> list[ApiEndpoint]:
    return session.exec(select(ApiEndpoint)).all()
def update_endpoint(session: Session, endpoint_id: int, payload: dict) -> ApiEndpoint | None:
    endpoint = session.get(ApiEndpoint, endpoint_id)
    if not endpoint:
        return None
    for k, v in payload.items():
        if hasattr(endpoint, k):
            setattr(endpoint, k, v)
    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)
    return endpoint
def delete_endpoint(session: Session, endpoint_id: int) -> bool:
    endpoint = session.get(ApiEndpoint, endpoint_id)
    if not endpoint:
        return False
    session.delete(endpoint)
    session.commit()
    return True
