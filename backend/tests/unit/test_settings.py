"""
Unit tests for app.settings module.
Tests Pydantic Settings with environment variables and defaults.
"""
import pytest
from unittest.mock import patch, MagicMock
import os
from pydantic import ValidationError


@pytest.mark.unit
class TestSettingsModule:
    """Test the app.settings module and Settings class."""
    
    def test_settings_import(self):
        """Test that settings module imports successfully."""
        from app.settings import Settings, settings
        assert Settings is not None
        assert settings is not None
    
    def test_settings_class_structure(self):
        """Test Settings class has required fields."""
        from app.settings import Settings
        
        # Check that Settings is a Pydantic BaseSettings subclass
        from pydantic_settings import BaseSettings
        assert issubclass(Settings, BaseSettings)
        
        # Check required fields exist
        required_fields = [
            'database_url', 'secret_key', 'jwt_algorithm',
            'access_token_expire_minutes', 'admin_email', 'env'
        ]
        
        # Create instance to check fields
        settings_instance = Settings()
        for field in required_fields:
            assert hasattr(settings_instance, field), f"Missing field: {field}"
    
    def test_settings_default_values(self):
        """Test Settings class default values."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Database defaults
        assert settings.database_url.startswith('postgresql')
        assert 'postgres' in settings.database_url
        
        # JWT defaults
        assert settings.jwt_algorithm == 'HS256'
        assert settings.access_token_expire_minutes == 60
        assert settings.refresh_token_expire_days == 7
        
        # Environment defaults
        assert settings.env == 'development'
        assert settings.frontend_origin == 'http://localhost:3000'
        assert settings.app_base_url == 'http://localhost:8000'
        
        # Admin defaults
        assert settings.admin_email == 'admin@example.com'
    
    @patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql://custom:custom@localhost/custom_db',
        'SECRET_KEY': 'custom-secret-key',
        'JWT_ALGORITHM': 'RS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '120',
        'ENV': 'production',
        'ADMIN_EMAIL': 'custom@admin.com',
        'ADMIN_PASSWORD': 'custom-password'
    })
    def test_settings_environment_override(self):
        """Test Settings class respects environment variables."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Check environment overrides
        assert settings.database_url == 'postgresql://custom:custom@localhost/custom_db'
        assert settings.secret_key == 'custom-secret-key'
        assert settings.jwt_algorithm == 'RS256'
        assert settings.access_token_expire_minutes == 120
        assert settings.env == 'production'
        assert settings.admin_email == 'custom@admin.com'
        assert settings.admin_password == 'custom-password'
    
    def test_settings_field_aliases(self):
        """Test that Settings uses proper field aliases."""
        from app.settings import Settings
        
        # Test with environment variables using aliases
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://alias:test@localhost/alias_db',
            'ML_CLIENT_ID': 'test-client-id',
            'FRONTEND_ORIGIN': 'http://localhost:3001'
        }):
            settings = Settings()
            assert 'alias_db' in settings.database_url
            assert settings.ml_client_id == 'test-client-id'
            assert settings.frontend_origin == 'http://localhost:3001'
    
    def test_settings_model_config(self):
        """Test Settings model configuration."""
        from app.settings import Settings
        
        # Check model config
        config = Settings.model_config
        assert 'env_file' in config
        assert config['env_file'] == '.env'
        assert config['env_file_encoding'] == 'utf-8'
    
    def test_settings_optional_fields(self):
        """Test optional fields in Settings."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Optional fields should be None or have defaults
        assert settings.admin_password is None or isinstance(settings.admin_password, str)
        assert settings.sentry_dsn is None or isinstance(settings.sentry_dsn, str)
    
    def test_settings_mercado_libre_config(self):
        """Test Mercado Libre configuration fields."""
        from app.settings import Settings
        
        settings = Settings()
        
        # ML fields should exist
        assert hasattr(settings, 'ml_client_id')
        assert hasattr(settings, 'ml_client_secret')
        assert hasattr(settings, 'ml_redirect_uri')
        
        # Should have defaults (empty strings are acceptable)
        assert isinstance(settings.ml_client_id, str)
        assert isinstance(settings.ml_client_secret, str)
        assert isinstance(settings.ml_redirect_uri, str)
    
    def test_settings_jwt_configuration(self):
        """Test JWT-related configuration."""
        from app.settings import Settings
        
        settings = Settings()
        
        # JWT fields
        assert settings.jwt_algorithm in ['HS256', 'RS256', 'ES256']
        assert isinstance(settings.access_token_expire_minutes, int)
        assert settings.access_token_expire_minutes > 0
        assert isinstance(settings.refresh_token_expire_days, int)
        assert settings.refresh_token_expire_days > 0
    
    def test_settings_cors_configuration(self):
        """Test CORS configuration fields."""
        from app.settings import Settings
        
        settings = Settings()
        
        # CORS field
        assert hasattr(settings, 'frontend_origin')
        assert isinstance(settings.frontend_origin, str)
        assert settings.frontend_origin.startswith('http')
    
    def test_settings_monitoring_config(self):
        """Test monitoring and observability configuration."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Monitoring fields
        if hasattr(settings, 'sentry_dsn'):
            assert settings.sentry_dsn is None or isinstance(settings.sentry_dsn, str)
        
        if hasattr(settings, 'metrics_api_key'):
            assert isinstance(settings.metrics_api_key, str)
        
        if hasattr(settings, 'enable_metrics_auth'):
            assert isinstance(settings.enable_metrics_auth, bool)
    
    @patch.dict(os.environ, {'ACCESS_TOKEN_EXPIRE_MINUTES': 'invalid'})
    def test_settings_validation_error(self):
        """Test that invalid values raise validation errors."""
        from app.settings import Settings
        
        with pytest.raises(ValidationError):
            Settings()
    
    def test_settings_instance_consistency(self):
        """Test that settings instance is consistent."""
        from app.settings import settings
        
        # Settings should be properly instantiated
        assert settings is not None
        
        # Should have all required attributes
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'secret_key')
        assert hasattr(settings, 'env')
    
    def test_settings_database_url_variations(self):
        """Test different database URL configurations."""
        from app.settings import Settings
        
        # Test default (Docker)
        settings_default = Settings()
        assert '@db:' in settings_default.database_url or '@localhost:' in settings_default.database_url
        
        # Test with localhost override
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db'}):
            settings_local = Settings()
            assert '@localhost:' in settings_local.database_url
    
    def test_settings_secret_key_validation(self):
        """Test secret key validation and security."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Secret key should exist and be non-empty
        assert settings.secret_key is not None
        assert len(settings.secret_key) > 0
        
        # Should not be the placeholder value in production
        if settings.env == 'production':
            assert settings.secret_key != 'change-this-secret-key-in-production'
    
    def test_settings_admin_configuration_validation(self):
        """Test admin user configuration validation."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Admin email should be valid format
        assert '@' in settings.admin_email
        assert '.' in settings.admin_email
        
        # Admin password handling
        if settings.admin_password:
            assert len(settings.admin_password) > 0


@pytest.mark.unit
class TestSettingsEnvironmentHandling:
    """Test environment variable handling in Settings."""
    
    def test_docker_vs_local_database_config(self):
        """Test database configuration for Docker vs local environments."""
        from app.settings import Settings
        
        # Test Docker configuration (default)
        settings_docker = Settings()
        # Should work with either db (Docker) or localhost
        assert ('@db:' in settings_docker.database_url or 
                '@localhost:' in settings_docker.database_url)
        
        # Test local configuration override
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://postgres:postgres@localhost:5432/ml_db'
        }):
            settings_local = Settings()
            assert '@localhost:' in settings_local.database_url
    
    def test_environment_specific_settings(self):
        """Test environment-specific configuration."""
        from app.settings import Settings
        
        # Development environment
        with patch.dict(os.environ, {'ENV': 'development'}):
            settings_dev = Settings()
            assert settings_dev.env == 'development'
        
        # Production environment  
        with patch.dict(os.environ, {'ENV': 'production'}):
            settings_prod = Settings()
            assert settings_prod.env == 'production'
        
        # Testing environment
        with patch.dict(os.environ, {'ENV': 'testing'}):
            settings_test = Settings()
            assert settings_test.env == 'testing'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_clean_environment_defaults(self):
        """Test behavior with completely clean environment."""
        from app.settings import Settings
        
        settings = Settings()
        
        # Should fall back to sensible defaults
        assert settings.env == 'development'
        assert settings.database_url.startswith('postgresql')
        assert settings.frontend_origin.startswith('http://localhost')
        assert settings.jwt_algorithm == 'HS256'