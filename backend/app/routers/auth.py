from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserCreate, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post('/register')
def register(payload: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail='User already exists')
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"email": user.email}

@router.post('/token', response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
