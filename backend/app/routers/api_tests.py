from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..db import get_session
from ..crud.tests import create_test, list_tests
from ..models import ApiTest
from ..schemas import ApiTestCreate, ApiTestRead
from ..auth import get_current_user

router = APIRouter(prefix="/api/tests", tags=["tests"])

@router.get("/", response_model=list[ApiTestRead])
def tests_list(session: Session = Depends(get_session), user=Depends(get_current_user)):
    tests = list_tests(session)
    return tests

@router.post("/", response_model=ApiTestRead)
def tests_create(payload: ApiTestCreate, session: Session = Depends(get_session), user=Depends(get_current_user)):
    model = ApiTest.from_orm(payload)
    t = create_test(session, model)
    return t
