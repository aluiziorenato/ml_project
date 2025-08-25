import httpx
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthService:
    """Service for handling authentication with the main backend"""
    
    def __init__(self):
        self.backend_url = settings.backend_url
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
    
    async def verify_token_with_backend(self, token: str) -> Optional[Dict]:
        """Verify token with the main backend service"""
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{self.backend_url}/api/auth/verify",
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token verification failed: {response.status_code}")
                    return None
            except httpx.HTTPError as e:
                logger.error(f"Error verifying token with backend: {e}")
                return None
    
    def decode_token_locally(self, token: str) -> Optional[Dict]:
        """Decode JWT token locally (fallback method)"""
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            return None
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
        """Get current authenticated user"""
        token = credentials.credentials
        
        # First try to verify with backend
        user_data = await self.verify_token_with_backend(token)
        
        if not user_data:
            # Fallback to local token decoding
            payload = self.decode_token_locally(token)
            if payload:
                # Extract user info from token
                user_data = {
                    "user_id": payload.get("sub"),
                    "seller_id": payload.get("seller_id"),
                    "access_token": payload.get("access_token"),
                    "expires_at": payload.get("exp")
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Check if token is expired
        if user_data.get("expires_at"):
            if datetime.utcnow().timestamp() > user_data["expires_at"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return user_data
    
    async def get_seller_access_token(self, seller_id: str) -> Optional[str]:
        """Get ML API access token for seller"""
        # This would integrate with the backend's token storage
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{self.backend_url}/api/auth/seller-token/{seller_id}"
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                else:
                    logger.warning(f"Could not get seller token: {response.status_code}")
                    return None
            except httpx.HTTPError as e:
                logger.error(f"Error getting seller token: {e}")
                return None
    
    def verify_seller_access(self, user_data: Dict, required_seller_id: str) -> bool:
        """Verify that user has access to specific seller account"""
        user_seller_id = user_data.get("seller_id")
        
        # User must be accessing their own seller account
        if user_seller_id != required_seller_id:
            return False
        
        return True
    
    async def refresh_token_if_needed(self, user_data: Dict) -> Dict:
        """Refresh token if it's close to expiration"""
        expires_at = user_data.get("expires_at")
        if not expires_at:
            return user_data
        
        # Check if token expires within next 5 minutes
        if datetime.utcnow().timestamp() + 300 > expires_at:
            # Request token refresh from backend
            async with httpx.AsyncClient(timeout=10) as client:
                try:
                    response = await client.post(
                        f"{self.backend_url}/api/auth/refresh",
                        json={"user_id": user_data["user_id"]}
                    )
                    if response.status_code == 200:
                        return response.json()
                except httpx.HTTPError as e:
                    logger.error(f"Error refreshing token: {e}")
        
        return user_data


# Global auth service instance
auth_service = AuthService()


# Dependency functions for FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """FastAPI dependency to get current authenticated user"""
    return await auth_service.get_current_user(credentials)


async def get_current_seller(user: Dict = Depends(get_current_user)) -> str:
    """FastAPI dependency to get current seller ID"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller ID not found in token"
        )
    return seller_id


def verify_seller_access_dependency(required_seller_id: str):
    """Create dependency to verify seller access"""
    async def _verify_access(user: Dict = Depends(get_current_user)) -> Dict:
        if not auth_service.verify_seller_access(user, required_seller_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this seller account"
            )
        return user
    return _verify_access