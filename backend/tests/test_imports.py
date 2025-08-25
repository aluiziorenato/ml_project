"""
Test module imports to ensure all components can be imported correctly.
This addresses point 10 of the PR #42 checklist.
"""
import pytest
import importlib.util
import sys
from pathlib import Path

@pytest.mark.unit
class TestModuleImports:
    """Test all modules can be imported without errors."""
    
    def test_app_main_import(self):
        """Test main application module imports."""
        try:
            from app.main import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.main: {e}")
    
    def test_app_models_import(self):
        """Test models module imports."""
        try:
            from app import models
            assert models is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.models: {e}")
    
    def test_app_schemas_import(self):
        """Test schemas module imports."""
        try:
            from app import schemas
            assert schemas is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.schemas: {e}")
    
    def test_app_database_import(self):
        """Test database module imports."""
        try:
            from app import database
            assert database is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.database: {e}")
    
    def test_core_security_import(self):
        """Test core security module imports."""
        try:
            from app.core import security
            assert security is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.core.security: {e}")
    
    def test_services_imports(self):
        """Test all service modules can be imported."""
        service_modules = [
            "app.services.seo",
            "app.services.mercadolibre",
        ]
        
        for module_name in service_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
    
    def test_routers_imports(self):
        """Test all router modules can be imported."""
        try:
            from app.routers import (
                api_endpoints, 
                api_tests, 
                oauth, 
                auth, 
                proxy, 
                seo, 
                categories, 
                anuncios, 
                meli_services_router, 
                metrics
            )
            # Check all routers are not None
            routers = [
                api_endpoints, api_tests, oauth, auth, proxy, 
                seo, categories, anuncios, meli_services_router, metrics
            ]
            for router in routers:
                assert router is not None
        except ImportError as e:
            pytest.fail(f"Failed to import routers: {e}")
    
    def test_monitoring_imports(self):
        """Test monitoring modules can be imported."""
        try:
            from app.monitoring import middleware
            from app.monitoring import prometheus_metrics
            from app.monitoring import loki_config
            
            assert middleware is not None
            assert prometheus_metrics is not None
            assert loki_config is not None
        except ImportError as e:
            pytest.fail(f"Failed to import monitoring modules: {e}")
    
    def test_crud_imports(self):
        """Test CRUD modules can be imported."""
        try:
            from app import crud
            assert crud is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.crud: {e}")

@pytest.mark.unit
class TestModuleFunctionality:
    """Test basic functionality of imported modules."""
    
    def test_security_functions_available(self):
        """Test security functions are available."""
        from app.core.security import (
            verify_password,
            get_password_hash,
            create_access_token,
            create_refresh_token,
            get_current_user
        )
        
        # Check functions are callable
        assert callable(verify_password)
        assert callable(get_password_hash)
        assert callable(create_access_token)
        assert callable(create_refresh_token)
        assert callable(get_current_user)
    
    def test_seo_functions_available(self):
        """Test SEO service functions are available."""
        from app.services.seo import optimize_text
        
        assert callable(optimize_text)
        
        # Test basic functionality
        result = optimize_text("Test text for SEO optimization")
        assert isinstance(result, dict)
        assert "original" in result
        assert "title" in result
        assert "meta_description" in result
    
    def test_database_components_available(self):
        """Test database components are available."""
        from app.database import Base, engine, SessionLocal
        
        assert Base is not None
        assert engine is not None
        assert SessionLocal is not None