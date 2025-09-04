from sqlmodel import Session
from ..models import ApiTest
def create_test(session: Session, test: ApiTest) -> ApiTest:
    session.add(test)
    session.commit()
    session.refresh(test)
    return test
def list_tests(session: Session, limit: int = 100):
    return session.query(ApiTest).order_by(ApiTest.executed_at.desc()).limit(limit).all()
