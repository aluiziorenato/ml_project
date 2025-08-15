"""
JWT Authentication middleware for ML services
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class TokenData(BaseModel):
    username: Optional[str] = None
    service: Optional[str] = None
    scopes: list[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: list[str] = []

# Mock user database (in production, use a real database)
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "System Administrator",
        "disabled": False,
        "scopes": ["admin", "read", "write"]
    },
    "user": {
        "username": "user",
        "email": "user@example.com", 
        "full_name": "Regular User",
        "disabled": False,
        "scopes": ["read", "write"]
    },
    "readonly": {
        "username": "readonly",
        "email": "readonly@example.com",
        "full_name": "Read Only User", 
        "disabled": False,
        "scopes": ["read"]
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        token_data = TokenData(
            username=username,
            service=payload.get("service"),
            scopes=payload.get("scopes", [])
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token_data

def get_current_user(token_data: TokenData = Depends(verify_token)):
    """Get current user from token"""
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_scope(required_scope: str):
    """Dependency to require specific scope"""
    def scope_checker(current_user: User = Depends(get_current_active_user)):
        if required_scope not in current_user.scopes:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Required scope: {required_scope}"
            )
        return current_user
    return scope_checker

def require_scopes(*required_scopes: str):
    """Dependency to require multiple scopes"""
    def scopes_checker(current_user: User = Depends(get_current_active_user)):
        for scope in required_scopes:
            if scope not in current_user.scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}"
                )
        return current_user
    return scopes_checker

# Authentication endpoints
def add_auth_routes(app):
    """Add authentication routes to FastAPI app"""
    from fastapi import Form
    
    @app.post("/api/auth/token")
    async def login(username: str = Form(...), password: str = Form(...)):
        """Login endpoint to get JWT token"""
        # In production, verify password against database
        if username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = fake_users_db[username]
        if user["disabled"]:
            raise HTTPException(status_code=401, detail="User account disabled")
        
        # Create token with user data
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": username,
                "scopes": user["scopes"],
                "service": "ml_automation"
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scopes": user["scopes"]
        }
    
    @app.get("/api/auth/me")
    async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
        """Get current user information"""
        return current_user
    
    @app.post("/api/auth/refresh")
    async def refresh_token(current_user: User = Depends(get_current_active_user)):
        """Refresh JWT token"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": current_user.username,
                "scopes": current_user.scopes,
                "service": "ml_automation"
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scopes": current_user.scopes
        }