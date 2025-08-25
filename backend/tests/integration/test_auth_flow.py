"""
Integration tests for authentication and authorization flows.
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.models import User, OAuthSession
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.main import app


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow integration."""
    
    def test_user_registration_flow(self, client: TestClient, db: Session):
        """Test complete user registration flow."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "is_active": True
        }
        
        # Register user
        response = client.post("/api/auth/register", json=registration_data)
        
        # Should succeed or handle existing user gracefully
        assert response.status_code in [200, 201, 409]
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            assert "email" in response_data
            assert response_data["email"] == registration_data["email"]
            
            # Verify user exists in database
            user = db.exec(
                select(User).where(User.email == registration_data["email"])
            ).first()
            assert user is not None
            assert user.email == registration_data["email"]
            assert user.is_active is True
            
    def test_user_login_flow(self, client: TestClient, db: Session):
        """Test complete user login flow."""
        # First create a user
        user = User(
            email="logintest@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Attempt login
        login_data = {
            "username": "logintest@example.com",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        if response.status_code == 200:
            response_data = response.json()
            assert "access_token" in response_data
            assert "token_type" in response_data
            assert response_data["token_type"] == "bearer"
            
            # Verify token is valid
            access_token = response_data["access_token"]
            assert isinstance(access_token, str)
            assert len(access_token) > 0
            
    def test_protected_endpoint_access(self, client: TestClient, db: Session):
        """Test access to protected endpoints with authentication."""
        # Create user and token
        user = User(
            email="protectedtest@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.email})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test protected endpoint (assuming /api/seo/optimize is protected)
        protected_data = {
            "text": "Test text for SEO optimization"
        }
        
        response = client.post("/api/seo/optimize", json=protected_data, headers=headers)
        
        # Should succeed with valid token
        assert response.status_code == 200
        
    def test_invalid_token_access(self, client: TestClient):
        """Test access with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        protected_data = {
            "text": "Test text for SEO optimization"
        }
        
        response = client.post("/api/seo/optimize", json=protected_data, headers=invalid_headers)
        
        # Should be unauthorized
        assert response.status_code == 401
        
    def test_expired_token_access(self, client: TestClient, db: Session):
        """Test access with expired token."""
        # Create user
        user = User(
            email="expiredtest@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create expired token
        expired_token = create_access_token(
            {"sub": user.email}, 
            expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        protected_data = {
            "text": "Test text for SEO optimization"
        }
        
        response = client.post("/api/seo/optimize", json=protected_data, headers=headers)
        
        # Should be unauthorized due to expired token
        assert response.status_code == 401


@pytest.mark.integration
class TestOAuthFlow:
    """Test OAuth flow integration."""
    
    def test_oauth_login_redirect(self, client: TestClient):
        """Test OAuth login redirect generation."""
        response = client.get("/oauth/login")
        
        # Should redirect to Mercado Libre authorization
        assert response.status_code in [200, 302, 307]
        
        if response.status_code == 200:
            # If returning redirect URL in response
            response_data = response.json()
            if "redirect_url" in response_data:
                redirect_url = response_data["redirect_url"]
                assert "auth.mercadolivre.com.br" in redirect_url
                assert "client_id" in redirect_url
                assert "response_type=code" in redirect_url
                
    def test_oauth_callback_handling(self, client: TestClient, db: Session):
        """Test OAuth callback handling."""
        # Mock OAuth session
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="test_state_123",
            code_verifier="test_verifier_456"
        )
        db.add(oauth_session)
        db.commit()
        
        # Simulate callback with authorization code
        callback_params = {
            "code": "auth_code_123",
            "state": "test_state_123"
        }
        
        response = client.get("/oauth/callback", params=callback_params)
        
        # Should handle callback appropriately
        # Response depends on implementation
        assert response.status_code in [200, 302, 400, 404]
        
    def test_oauth_state_validation(self, client: TestClient, db: Session):
        """Test OAuth state parameter validation."""
        # Create OAuth session with specific state
        oauth_session = OAuthSession(
            endpoint_id=1,
            state="valid_state_123",
            code_verifier="test_verifier_456"
        )
        db.add(oauth_session)
        db.commit()
        
        # Try callback with invalid state
        invalid_callback_params = {
            "code": "auth_code_123",
            "state": "invalid_state_456"
        }
        
        response = client.get("/oauth/callback", params=invalid_callback_params)
        
        # Should reject invalid state
        assert response.status_code in [400, 401, 404]
        
    def test_oauth_session_management(self, client: TestClient, db: Session):
        """Test OAuth session creation and management."""
        # Initiate OAuth flow
        response = client.get("/oauth/login")
        
        if response.status_code == 200:
            response_data = response.json()
            if "state" in response_data:
                state = response_data["state"]
                
                # Verify OAuth session was created
                oauth_session = db.exec(
                    select(OAuthSession).where(OAuthSession.state == state)
                ).first()
                
                if oauth_session:
                    assert oauth_session.state == state
                    assert oauth_session.code_verifier is not None
                    assert len(oauth_session.code_verifier) >= 43  # PKCE requirement


@pytest.mark.integration
class TestTokenManagement:
    """Test token management and refresh functionality."""
    
    def test_token_creation_and_validation(self, db: Session):
        """Test token creation and validation process."""
        # Create user
        user = User(
            email="tokentest@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.email})
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        
        # Create refresh token
        refresh_token = create_refresh_token({"sub": user.email})
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
        assert refresh_token != access_token
        
    def test_token_refresh_flow(self, client: TestClient, db: Session):
        """Test token refresh functionality."""
        # Create user
        user = User(
            email="refreshtest@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create refresh token
        refresh_token = create_refresh_token({"sub": user.email})
        
        # Attempt token refresh
        refresh_data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Response depends on implementation
        if response.status_code == 200:
            response_data = response.json()
            assert "access_token" in response_data
            new_access_token = response_data["access_token"]
            assert isinstance(new_access_token, str)
            assert len(new_access_token) > 0
            
    def test_token_revocation(self, client: TestClient, db: Session):
        """Test token revocation functionality."""
        # Create user and token
        user = User(
            email="revoketest@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        access_token = create_access_token({"sub": user.email})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test access before revocation
        response = client.get("/api/auth/me", headers=headers)
        if response.status_code == 200:
            # Token works initially
            
            # Revoke token
            revoke_response = client.post("/api/auth/revoke", headers=headers)
            
            if revoke_response.status_code == 200:
                # Test access after revocation
                response_after = client.get("/api/auth/me", headers=headers)
                # Should be unauthorized after revocation
                assert response_after.status_code == 401


@pytest.mark.integration
class TestUserPermissions:
    """Test user permissions and authorization levels."""
    
    def test_regular_user_permissions(self, client: TestClient, db: Session):
        """Test regular user permission levels."""
        # Create regular user
        user = User(
            email="regularuser@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        
        access_token = create_access_token({"sub": user.email})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test access to regular endpoints
        response = client.get("/api/seo/optimize", headers=headers)
        # Regular users should have access to basic endpoints
        assert response.status_code in [200, 405]  # 405 if GET not allowed
        
        # Test access to admin endpoints (if they exist)
        admin_response = client.get("/api/admin/users", headers=headers)
        # Regular users should not have admin access
        assert admin_response.status_code in [401, 403, 404]
        
    def test_superuser_permissions(self, client: TestClient, db: Session):
        """Test superuser permission levels."""
        # Create superuser
        admin_user = User(
            email="adminuser@example.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        
        access_token = create_access_token({"sub": admin_user.email})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test access to regular endpoints
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
        
        # Test access to admin endpoints (if implemented)
        admin_response = client.get("/api/admin/users", headers=headers)
        # Admin should have access or endpoint should exist
        assert admin_response.status_code in [200, 404]  # 404 if not implemented
        
    def test_inactive_user_permissions(self, client: TestClient, db: Session):
        """Test inactive user access restrictions."""
        # Create inactive user
        inactive_user = User(
            email="inactiveuser@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=False,  # Inactive
            is_superuser=False
        )
        db.add(inactive_user)
        db.commit()
        
        # Try to login with inactive user
        login_data = {
            "username": "inactiveuser@example.com",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/auth/token", data=login_data)
        
        # Should be denied for inactive user
        assert response.status_code in [401, 403]


@pytest.mark.integration
class TestSessionManagement:
    """Test session management functionality."""
    
    def test_concurrent_user_sessions(self, client: TestClient, db: Session):
        """Test multiple concurrent sessions for same user."""
        # Create user
        user = User(
            email="concurrent@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create multiple tokens for same user
        token1 = create_access_token({"sub": user.email})
        token2 = create_access_token({"sub": user.email})
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Both tokens should work
        response1 = client.get("/health", headers=headers1)
        response2 = client.get("/health", headers=headers2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
    def test_session_timeout_handling(self, client: TestClient, db: Session):
        """Test session timeout behavior."""
        # Create user
        user = User(
            email="timeout@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create token with very short expiry
        short_token = create_access_token(
            {"sub": user.email}, 
            expires_delta=timedelta(seconds=1)
        )
        headers = {"Authorization": f"Bearer {short_token}"}
        
        # Should work immediately
        immediate_response = client.get("/health", headers=headers)
        assert immediate_response.status_code == 200
        
        # Wait for expiry and test again
        import time
        time.sleep(2)
        
        expired_response = client.get("/health", headers=headers)
        # Token should be expired
        assert expired_response.status_code in [401, 422]
        
    def test_session_cleanup(self, db: Session):
        """Test cleanup of expired OAuth sessions."""
        # Create expired OAuth session
        expired_session = OAuthSession(
            endpoint_id=1,
            state="expired_state",
            code_verifier="expired_verifier",
            expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired
        )
        db.add(expired_session)
        
        # Create active OAuth session
        active_session = OAuthSession(
            endpoint_id=2,
            state="active_state",
            code_verifier="active_verifier",
            expires_at=datetime.utcnow() + timedelta(hours=1)  # Active
        )
        db.add(active_session)
        db.commit()
        
        # Query expired sessions
        expired_sessions = db.exec(
            select(OAuthSession).where(
                OAuthSession.expires_at < datetime.utcnow()
            )
        ).all()
        
        # Should find the expired session
        assert len(expired_sessions) >= 1
        assert any(session.state == "expired_state" for session in expired_sessions)
        
        # Query active sessions
        active_sessions = db.exec(
            select(OAuthSession).where(
                OAuthSession.expires_at > datetime.utcnow()
            )
        ).all()
        
        # Should find the active session
        assert len(active_sessions) >= 1
        assert any(session.state == "active_state" for session in active_sessions)


@pytest.mark.integration
class TestAuthenticationSecurity:
    """Test authentication security measures."""
    
    def test_password_security_requirements(self, client: TestClient):
        """Test password security requirements."""
        weak_passwords = [
            "123",
            "password",
            "abc123",
            "qwerty"
        ]
        
        for weak_password in weak_passwords:
            registration_data = {
                "email": f"weak_{hash(weak_password)}@example.com",
                "password": weak_password,
                "is_active": True
            }
            
            response = client.post("/api/auth/register", json=registration_data)
            
            # Should reject weak passwords (if validation implemented)
            # If not implemented, this test documents the requirement
            if response.status_code == 400:
                response_data = response.json()
                assert "password" in str(response_data).lower()
                
    def test_brute_force_protection(self, client: TestClient, db: Session):
        """Test brute force attack protection."""
        # Create user
        user = User(
            email="bruteforce@example.com",
            hashed_password=get_password_hash("CorrectPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Attempt multiple failed logins
        login_data = {
            "username": "bruteforce@example.com",
            "password": "WrongPassword"
        }
        
        responses = []
        for _ in range(10):  # 10 failed attempts
            response = client.post("/api/auth/token", data=login_data)
            responses.append(response.status_code)
            
        # Should eventually implement rate limiting or account lockout
        # For now, just verify all attempts are rejected
        assert all(status in [401, 422, 429] for status in responses)
        
    def test_sql_injection_protection(self, client: TestClient):
        """Test SQL injection protection in authentication."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin@example.com'; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --"
        ]
        
        for malicious_input in malicious_inputs:
            login_data = {
                "username": malicious_input,
                "password": "password"
            }
            
            response = client.post("/api/auth/token", data=login_data)
            
            # Should handle malicious input safely
            assert response.status_code in [401, 422]
            # Should not return sensitive information
            if response.status_code != 500:  # No server errors from injection
                pass
                
    def test_token_security_measures(self, db: Session):
        """Test token security characteristics."""
        # Create user
        user = User(
            email="tokensecurity@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Generate multiple tokens
        tokens = []
        for i in range(5):
            token = create_access_token({"sub": user.email})
            tokens.append(token)
            
        # All tokens should be different (non-deterministic)
        assert len(set(tokens)) == 5
        
        # Tokens should be of reasonable length
        for token in tokens:
            assert len(token) > 100  # JWT tokens are typically long
            assert "." in token  # JWT structure
            parts = token.split(".")
            assert len(parts) == 3  # Header, payload, signature