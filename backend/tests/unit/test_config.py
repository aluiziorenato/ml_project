"""
Unit tests for app.config module.
Tests configuration loading, validation, and export functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
import os


@pytest.mark.unit
class TestConfigModule:
    """Test the app.config module functionality."""
    
    def test_config_module_import(self):
        """Test that config module can be imported successfully."""
        from app.config import settings
        assert settings is not None
    
    def test_config_exports_settings(self):
        """Test that config module exports settings object."""
        from app import config
        
        # Check that settings is available
        assert hasattr(config, 'settings')
        assert config.settings is not None
        
        # Check that __all__ includes settings
        assert hasattr(config, '__all__')
        assert 'settings' in config.__all__
    
    def test_settings_object_type(self):
        """Test that settings object is of correct type."""
        from app.config import settings
        from app.settings import Settings
        
        assert isinstance(settings, Settings)
    
    def test_config_module_structure(self):
        """Test the structure of the config module."""
        import app.config as config_module
        
        # Should have settings
        assert hasattr(config_module, 'settings')
        
        # Should have __all__ for clean imports
        assert hasattr(config_module, '__all__')
        assert isinstance(config_module.__all__, list)
        assert len(config_module.__all__) > 0
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_with_clean_environment(self):
        """Test config loading with clean environment."""
        # Import with clean environment
        from app.config import settings
        
        # Should use default values
        assert settings.env == "development"
        assert settings.database_url.startswith("postgresql")
    
    @patch.dict(os.environ, {
        'ENV': 'testing',
        'DATABASE_URL': 'postgresql://test:test@localhost/test_db'
    })
    def test_config_with_environment_override(self):
        """Test config loading with environment variables."""
        # Need to reload the module to pick up new env vars
        import importlib
        import app.config
        importlib.reload(app.config)
        
        from app.config import settings
        
        # Should use environment values
        assert settings.env == "testing"
        assert "test_db" in settings.database_url
    
    def test_config_settings_immutability(self):
        """Test that settings object is properly configured."""
        from app.config import settings
        
        # Settings should be a singleton-like object
        from app.config import settings as settings2
        assert settings is settings2
    
    def test_config_validation_on_import(self):
        """Test that configuration is validated on import."""
        # This test ensures no exceptions are raised during import
        try:
            from app.config import settings
            # Basic validation - should have required fields
            assert hasattr(settings, 'database_url')
            assert hasattr(settings, 'secret_key')
            assert hasattr(settings, 'env')
        except Exception as e:
            pytest.fail(f"Config validation failed on import: {e}")
    
    def test_config_field_types(self):
        """Test that config fields have correct types."""
        from app.config import settings
        
        # String fields
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.secret_key, str)
        assert isinstance(settings.env, str)
        
        # Integer fields
        assert isinstance(settings.access_token_expire_minutes, int)
        
        # Boolean fields if any
        if hasattr(settings, 'enable_metrics_auth'):
            assert isinstance(settings.enable_metrics_auth, bool)
    
    @patch.dict(os.environ, {'SECRET_KEY': 'test-secret-123'})
    def test_config_secret_key_override(self):
        """Test secret key can be overridden via environment."""
        import importlib
        import app.config
        importlib.reload(app.config)
        
        from app.config import settings
        assert settings.secret_key == 'test-secret-123'
    
    def test_config_database_url_validation(self):
        """Test database URL has proper format."""
        from app.config import settings
        
        # Should be a valid PostgreSQL URL format
        assert settings.database_url.startswith('postgresql')
        assert '@' in settings.database_url
        assert '/' in settings.database_url


@pytest.mark.unit 
class TestConfigDefaults:
    """Test configuration default values."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_default_values(self):
        """Test that default configuration values are sensible."""
        import importlib
        import app.config
        importlib.reload(app.config)
        
        from app.config import settings
        
        # Environment should default to development
        assert settings.env == "development"
        
        # Database URL should be for development
        assert "postgresql" in settings.database_url
        
        # JWT settings should have sensible defaults
        assert settings.jwt_algorithm == "HS256"
        assert settings.access_token_expire_minutes > 0
        
        # CORS should allow localhost for development
        assert "localhost" in settings.frontend_origin
    
    def test_default_admin_configuration(self):
        """Test default admin configuration."""
        from app.config import settings
        
        # Should have admin email default
        assert settings.admin_email is not None
        assert "@" in settings.admin_email
        
        # Admin password might be None (requiring environment override)
        # This is acceptable for security
    
    def test_default_security_settings(self):
        """Test default security-related settings."""
        from app.config import settings
        
        # Secret key should exist (even if placeholder)
        assert settings.secret_key is not None
        assert len(settings.secret_key) > 10
        
        # JWT algorithm should be secure
        assert settings.jwt_algorithm in ["HS256", "RS256"]
        
        # Token expiry should be reasonable
        assert 5 <= settings.access_token_expire_minutes <= 1440  # 5 min to 24 hours