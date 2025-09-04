from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.db import get_session
from app.schemas import ApiEndpointCreate, ApiEndpointRead
from app.models import ApiEndpoint
from app.crud.endpoints import create_endpoint, get_endpoint, list_endpoints, update_endpoint, delete_endpoint
from app.core.security import get_current_user
from app.models import User

router = APIRouter(prefix="/api/endpoints", tags=["endpoints"])


@router.get("/", response_model=List[ApiEndpointRead])
def endpoint_list(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return list_endpoints(session)


@router.post("/", response_model=ApiEndpointRead)
def endpoint_create(
    payload: ApiEndpointCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    model = ApiEndpoint.from_orm(payload)
    return create_endpoint(session, model)


@router.get("/{endpoint_id}", response_model=ApiEndpointRead)
def endpoint_get(
    endpoint_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    e = get_endpoint(session, endpoint_id)
    if not e:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return e


@router.put("/{endpoint_id}", response_model=ApiEndpointRead)
def endpoint_update(
    endpoint_id: int,
    payload: ApiEndpointCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    data = payload.dict()
    e = update_endpoint(session, endpoint_id, data)
    if not e:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return e


@router.delete("/{endpoint_id}")
def endpoint_delete(
    endpoint_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    ok = delete_endpoint(session, endpoint_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return {"deleted": True}
