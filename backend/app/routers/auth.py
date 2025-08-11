# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.db import get_session
from app.models import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.schemas import UserCreate, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(payload: UserCreate, session: Session = Depends(get_session)):
    """
    Registra um novo usuário, garantindo que o email não esteja duplicado.
    Salva o usuário com a senha hasheada.
    """
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = get_password_hash(payload.password)
    user = User(email=payload.email, hashed_password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"email": user.email}

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Autentica o usuário e retorna tokens de acesso e refresh JWT.
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
