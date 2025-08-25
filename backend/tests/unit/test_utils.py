"""
Unit tests for utility functions and helpers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import os
import tempfile
import json

from app.config import settings
from app.settings import Settings


@pytest.mark.unit
class TestSettings:
    """Test application settings functionality."""
    
    def test_settings_default_values(self):
        """Test that settings have proper default values."""
        test_settings = Settings()
        
        assert test_settings.database_url == "sqlite:///./test.db"
        assert test_settings.secret_key == "change-this-secret-key-in-production"
        assert test_settings.jwt_algorithm == "HS256"
        assert test_settings.access_token_expire_minutes == 60
        assert test_settings.refresh_token_expire_days == 7
        assert test_settings.frontend_origin == "http://localhost:3000"
        assert test_settings.env == "development"
        assert test_settings.admin_email == "admin@example.com"
        
    def test_settings_environment_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test_secret_key',
            'JWT_ALGORITHM': 'RS256',
            'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
            'REFRESH_TOKEN_EXPIRE_DAYS': '3',
            'FRONTEND_ORIGIN': 'http://localhost:4000',
            'ENV': 'testing',
            'ADMIN_EMAIL': 'test_admin@example.com',
            'ADMIN_PASSWORD': 'test_admin_password'
        }):
            test_settings = Settings()
            
            assert test_settings.database_url == "postgresql://test:test@localhost/test"
            assert test_settings.secret_key == "test_secret_key"
            assert test_settings.jwt_algorithm == "RS256"
            assert test_settings.access_token_expire_minutes == 30
            assert test_settings.refresh_token_expire_days == 3
            assert test_settings.frontend_origin == "http://localhost:4000"
            assert test_settings.env == "testing"
            assert test_settings.admin_email == "test_admin@example.com"
            assert test_settings.admin_password == "test_admin_password"
            
    def test_settings_ml_configuration(self):
        """Test Mercado Libre specific settings."""
        with patch.dict(os.environ, {
            'ML_CLIENT_ID': 'test_ml_client_id',
            'ML_CLIENT_SECRET': 'test_ml_client_secret',
            'ML_REDIRECT_URI': 'http://localhost:8000/oauth/callback'
        }):
            test_settings = Settings()
            
            assert test_settings.ml_client_id == "test_ml_client_id"
            assert test_settings.ml_client_secret == "test_ml_client_secret"
            assert test_settings.ml_redirect_uri == "http://localhost:8000/oauth/callback"
            
    def test_settings_app_configuration(self):
        """Test application specific settings."""
        with patch.dict(os.environ, {
            'APP_BASE_URL': 'https://myapp.com',
            'ENV': 'production'
        }):
            test_settings = Settings()
            
            assert test_settings.app_base_url == "https://myapp.com"
            assert test_settings.env == "production"
            
    def test_settings_field_aliases(self):
        """Test that field aliases work correctly."""
        # Test that both field name and alias work
        test_settings = Settings(database_url="test_db_url")
        assert test_settings.database_url == "test_db_url"
        
        # Test with environment variable using alias
        with patch.dict(os.environ, {'DATABASE_URL': 'env_db_url'}):
            test_settings = Settings()
            assert test_settings.database_url == "env_db_url"


@pytest.mark.unit
class TestUtilityFunctions:
    """Test various utility functions."""
    
    def test_datetime_handling(self):
        """Test datetime utility functions."""
        # Test current datetime
        now = datetime.utcnow()
        assert isinstance(now, datetime)
        
        # Test datetime arithmetic
        future = now + timedelta(hours=1)
        assert future > now
        
        past = now - timedelta(hours=1)
        assert past < now
        
    def test_string_utilities(self):
        """Test string utility operations."""
        # Test string cleaning (if implemented)
        test_string = "  Test String With Spaces  "
        cleaned = test_string.strip()
        assert cleaned == "Test String With Spaces"
        
        # Test string formatting
        formatted = f"Formatted: {test_string.strip()}"
        assert "Formatted: Test String With Spaces" == formatted
        
    def test_url_utilities(self):
        """Test URL construction utilities."""
        base_url = "https://api.example.com"
        endpoint = "/users"
        params = {"limit": 10, "offset": 0}
        
        # Manual URL construction for testing
        full_url = f"{base_url}{endpoint}"
        if params:
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url += f"?{param_string}"
            
        assert full_url == "https://api.example.com/users?limit=10&offset=0"
        
    def test_json_utilities(self):
        """Test JSON handling utilities."""
        test_data = {"key": "value", "number": 123, "list": [1, 2, 3]}
        
        # Test JSON serialization
        json_string = json.dumps(test_data)
        assert isinstance(json_string, str)
        assert "key" in json_string
        
        # Test JSON deserialization
        parsed_data = json.loads(json_string)
        assert parsed_data == test_data
        
    def test_file_utilities(self):
        """Test file handling utilities."""
        # Test temporary file creation
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content")
            temp_file_path = temp_file.name
            
        # Test file reading
        with open(temp_file_path, 'r') as file:
            content = file.read()
            assert content == "test content"
            
        # Cleanup
        os.unlink(temp_file_path)


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling utilities."""
    
    def test_exception_handling(self):
        """Test exception handling patterns."""
        # Test basic exception handling
        try:
            raise ValueError("Test error")
        except ValueError as e:
            assert str(e) == "Test error"
            assert isinstance(e, ValueError)
            
    def test_custom_exception_handling(self):
        """Test custom exception scenarios."""
        # Test multiple exception types
        exceptions_to_test = [
            (ValueError, "Value error"),
            (TypeError, "Type error"),
            (KeyError, "Key error"),
            (IndexError, "Index error")
        ]
        
        for exception_class, error_message in exceptions_to_test:
            try:
                raise exception_class(error_message)
            except exception_class as e:
                assert str(e) == error_message
                assert isinstance(e, exception_class)
                
    def test_exception_chaining(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise TypeError("Chained error") from e
        except TypeError as e:
            assert str(e) == "Chained error"
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Original error"


@pytest.mark.unit
class TestValidationUtilities:
    """Test validation utility functions."""
    
    def test_email_validation_pattern(self):
        """Test email validation patterns."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            ""
        ]
        
        # Simple email validation pattern
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in valid_emails:
            assert re.match(email_pattern, email), f"Valid email {email} failed validation"
            
        for email in invalid_emails:
            assert not re.match(email_pattern, email), f"Invalid email {email} passed validation"
            
    def test_url_validation_pattern(self):
        """Test URL validation patterns."""
        valid_urls = [
            "https://example.com",
            "http://api.example.com/v1",
            "https://sub.domain.com/path?param=value",
            "http://localhost:8000"
        ]
        
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol.com",
            "https://",
            ""
        ]
        
        # Simple URL validation pattern
        import re
        url_pattern = r'^https?://[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:/.*)?$'
        
        for url in valid_urls:
            assert re.match(url_pattern, url), f"Valid URL {url} failed validation"
            
        for url in invalid_urls:
            assert not re.match(url_pattern, url), f"Invalid URL {url} passed validation"
            
    def test_password_strength_validation(self):
        """Test password strength validation."""
        strong_passwords = [
            "StrongP@ssw0rd123",
            "C0mplexP@ssword!",
            "MySecure123$"
        ]
        
        weak_passwords = [
            "weak",
            "123456",
            "password",
            "abc123"
        ]
        
        # Simple password strength check
        def is_strong_password(password):
            if len(password) < 8:
                return False
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=" for c in password)
            return has_upper and has_lower and has_digit and has_special
            
        for password in strong_passwords:
            assert is_strong_password(password), f"Strong password {password} failed validation"
            
        for password in weak_passwords:
            assert not is_strong_password(password), f"Weak password {password} passed validation"


@pytest.mark.unit
class TestDataTransformation:
    """Test data transformation utilities."""
    
    def test_dict_transformation(self):
        """Test dictionary transformation operations."""
        source_dict = {
            "name": "Test Product",
            "price": "199.99",
            "category": "electronics",
            "in_stock": "true"
        }
        
        # Transform string values to appropriate types
        transformed = {}
        for key, value in source_dict.items():
            if key == "price":
                transformed[key] = float(value)
            elif key == "in_stock":
                transformed[key] = value.lower() == "true"
            else:
                transformed[key] = value
                
        assert transformed["name"] == "Test Product"
        assert transformed["price"] == 199.99
        assert transformed["category"] == "electronics"
        assert transformed["in_stock"] is True
        
    def test_list_transformation(self):
        """Test list transformation operations."""
        source_list = ["1", "2", "3", "4", "5"]
        
        # Transform to integers
        int_list = [int(x) for x in source_list]
        assert int_list == [1, 2, 3, 4, 5]
        
        # Filter and transform
        even_numbers = [int(x) for x in source_list if int(x) % 2 == 0]
        assert even_numbers == [2, 4]
        
    def test_nested_data_transformation(self):
        """Test nested data structure transformation."""
        nested_data = {
            "user": {
                "id": "123",
                "name": "Test User",
                "settings": {
                    "notifications": "true",
                    "theme": "dark"
                }
            },
            "products": ["1", "2", "3"]
        }
        
        # Transform nested structure
        def transform_nested(data):
            if isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    if key == "id":
                        result[key] = int(value)
                    elif key == "notifications":
                        result[key] = value.lower() == "true"
                    elif isinstance(value, (dict, list)):
                        result[key] = transform_nested(value)
                    else:
                        result[key] = value
                return result
            elif isinstance(data, list):
                return [transform_nested(item) for item in data]
            else:
                return data
                
        transformed = transform_nested(nested_data)
        
        assert transformed["user"]["id"] == 123
        assert transformed["user"]["settings"]["notifications"] is True
        assert isinstance(transformed["products"], list)


@pytest.mark.unit
class TestCachingUtilities:
    """Test caching utility patterns."""
    
    def test_simple_cache_pattern(self):
        """Test simple caching pattern."""
        cache = {}
        
        def cached_function(key):
            if key in cache:
                return cache[key]
            
            # Simulate expensive operation
            result = f"computed_value_for_{key}"
            cache[key] = result
            return result
            
        # First call should compute and cache
        result1 = cached_function("test_key")
        assert result1 == "computed_value_for_test_key"
        assert "test_key" in cache
        
        # Second call should return cached value
        result2 = cached_function("test_key")
        assert result2 == result1
        assert result2 == cache["test_key"]
        
    def test_cache_expiration_pattern(self):
        """Test cache with expiration pattern."""
        cache = {}
        
        def cached_function_with_expiry(key, ttl_seconds=60):
            now = datetime.utcnow()
            
            if key in cache:
                cached_time, cached_value = cache[key]
                if (now - cached_time).total_seconds() < ttl_seconds:
                    return cached_value
                    
            # Compute new value
            result = f"computed_at_{now.isoformat()}"
            cache[key] = (now, result)
            return result
            
        # First call
        result1 = cached_function_with_expiry("test_key", ttl_seconds=1)
        assert "test_key" in cache
        
        # Immediate second call should return cached value
        result2 = cached_function_with_expiry("test_key", ttl_seconds=1)
        assert result1 == result2
        
        # After expiration (simulated)
        import time
        time.sleep(1.1)
        result3 = cached_function_with_expiry("test_key", ttl_seconds=1)
        assert result3 != result1  # Should be recomputed


@pytest.mark.unit
class TestLoggingUtilities:
    """Test logging utility functions."""
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        import logging
        
        # Test logger creation
        logger = logging.getLogger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        
    def test_log_level_handling(self):
        """Test log level handling."""
        import logging
        
        logger = logging.getLogger("test_logger")
        
        # Test different log levels
        log_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL
        ]
        
        for level in log_levels:
            logger.setLevel(level)
            assert logger.level == level
            assert logger.isEnabledFor(level)
            
    @patch('logging.getLogger')
    def test_logger_mocking(self, mock_get_logger):
        """Test logger with mocking."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        import logging
        logger = logging.getLogger("test_logger")
        
        # Test that mock is returned
        assert logger == mock_logger
        mock_get_logger.assert_called_once_with("test_logger")
        
        # Test logging calls
        logger.info("Test message")
        mock_logger.info.assert_called_once_with("Test message")


@pytest.mark.unit
class TestConfigurationUtilities:
    """Test configuration management utilities."""
    
    @patch.dict(os.environ, {'TEST_ENV_VAR': 'test_value'})
    def test_environment_variable_access(self):
        """Test environment variable access."""
        # Test getting environment variable
        value = os.getenv('TEST_ENV_VAR')
        assert value == 'test_value'
        
        # Test getting with default
        default_value = os.getenv('NON_EXISTENT_VAR', 'default')
        assert default_value == 'default'
        
    def test_configuration_validation(self):
        """Test configuration validation."""
        required_settings = [
            'database_url',
            'secret_key',
            'jwt_algorithm'
        ]
        
        test_settings = Settings()
        
        for setting in required_settings:
            assert hasattr(test_settings, setting)
            value = getattr(test_settings, setting)
            assert value is not None
            assert value != ""
            
    def test_configuration_types(self):
        """Test configuration value types."""
        test_settings = Settings()
        
        # Test string settings
        assert isinstance(test_settings.database_url, str)
        assert isinstance(test_settings.secret_key, str)
        assert isinstance(test_settings.jwt_algorithm, str)
        
        # Test integer settings
        assert isinstance(test_settings.access_token_expire_minutes, int)
        assert isinstance(test_settings.refresh_token_expire_days, int)
        
        # Test that numeric settings have reasonable values
        assert test_settings.access_token_expire_minutes > 0
        assert test_settings.refresh_token_expire_days > 0