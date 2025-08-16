"""
Authentication middleware for API security.
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for API endpoints."""
    
    def __init__(self, secret_key: str = "your-secret-key"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
    
    async def verify_token(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """
        Verify JWT token and return user information.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            token = credentials.credentials
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Check if token has required fields
            if "sub" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def verify_admin_token(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """
        Verify JWT token and ensure user has admin privileges.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or user is not admin
        """
        payload = await self.verify_token(credentials)
        
        # Check if user has admin role
        if not payload.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )
        
        return payload
    
    def create_token(self, user_data: dict, expires_delta: Optional[int] = None) -> str:
        """
        Create a JWT token for user.
        
        Args:
            user_data: User information to encode
            expires_delta: Token expiration time in seconds
            
        Returns:
            Encoded JWT token
        """
        import time
        
        payload = user_data.copy()
        
        if expires_delta:
            payload["exp"] = int(time.time()) + expires_delta
        else:
            payload["exp"] = int(time.time()) + 3600  # 1 hour default
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token


# Default auth middleware instance
auth_middleware = AuthMiddleware()

# Dependency functions for use in routes
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency function to verify JWT token."""
    return await auth_middleware.verify_token(credentials)


async def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency function to verify admin JWT token."""
    return await auth_middleware.verify_admin_token(credentials)


def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Optional authentication - returns None if no token provided.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Decoded token payload or None
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            auth_middleware.secret_key, 
            algorithms=[auth_middleware.algorithm]
        )
        return payload
    except jwt.JWTError:
        return None