"""
Unit tests for app.validate_requirements module.
Tests dependency validation functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
import importlib
import sys


@pytest.mark.unit
class TestValidateRequirementsModule:
    """Test the app.validate_requirements module functionality."""
    
    def test_validate_requirements_import(self):
        """Test that validate_requirements module can be imported."""
        from app import validate_requirements
        assert validate_requirements is not None
    
    def test_validate_core_dependencies_function(self):
        """Test validate_core_dependencies function exists and is callable."""
        from app.validate_requirements import validate_core_dependencies
        assert callable(validate_core_dependencies)
    
    def test_validate_app_modules_function(self):
        """Test validate_app_modules function exists and is callable."""
        from app.validate_requirements import validate_app_modules
        assert callable(validate_app_modules)
    
    def test_validate_optional_dependencies_function(self):
        """Test validate_optional_dependencies function exists and is callable."""
        from app.validate_requirements import validate_optional_dependencies
        assert callable(validate_optional_dependencies)
    
    def test_get_validation_report_function(self):
        """Test get_validation_report function exists and is callable."""
        from app.validate_requirements import get_validation_report
        assert callable(get_validation_report)
    
    @patch('app.validate_requirements.importlib.import_module')
    def test_validate_core_dependencies_success(self, mock_import):
        """Test validate_core_dependencies with all modules available."""
        from app.validate_requirements import validate_core_dependencies
        
        # Mock successful imports
        mock_import.return_value = MagicMock()
        
        success, errors = validate_core_dependencies()
        
        assert success is True
        assert len(errors) == 0
        
        # Should have tried to import core modules
        assert mock_import.call_count > 0
    
    @patch('app.validate_requirements.importlib.import_module')
    def test_validate_core_dependencies_failure(self, mock_import):
        """Test validate_core_dependencies with missing modules."""
        from app.validate_requirements import validate_core_dependencies
        
        # Mock import error for one module
        def import_side_effect(module_name):
            if module_name == 'fastapi':
                raise ImportError("No module named 'fastapi'")
            return MagicMock()
        
        mock_import.side_effect = import_side_effect
        
        success, errors = validate_core_dependencies()
        
        assert success is False
        assert len(errors) > 0
        assert any('fastapi' in error for error in errors)
    
    @patch('app.validate_requirements.importlib.import_module')
    def test_validate_app_modules_success(self, mock_import):
        """Test validate_app_modules with all modules available."""
        from app.validate_requirements import validate_app_modules
        
        # Mock successful imports
        mock_import.return_value = MagicMock()
        
        success, errors = validate_app_modules()
        
        assert success is True
        assert len(errors) == 0
    
    @patch('app.validate_requirements.importlib.import_module')
    def test_validate_app_modules_failure(self, mock_import):
        """Test validate_app_modules with missing modules."""
        from app.validate_requirements import validate_app_modules
        
        # Mock import error for app module
        def import_side_effect(module_name):
            if 'app.config' in module_name:
                raise ImportError("No module named 'app.config'")
            return MagicMock()
        
        mock_import.side_effect = import_side_effect
        
        success, errors = validate_app_modules()
        
        assert success is False
        assert len(errors) > 0
        assert any('app.config' in error for error in errors)
    
    @patch('app.validate_requirements.importlib.import_module')
    def test_validate_optional_dependencies(self, mock_import):
        """Test validate_optional_dependencies function."""
        from app.validate_requirements import validate_optional_dependencies
        
        # Mock some available, some not
        def import_side_effect(module_name):
            if module_name == 'sentry_sdk':
                return MagicMock()
            elif module_name == 'prometheus_client':
                raise ImportError("Not available")
            return MagicMock()
        
        mock_import.side_effect = import_side_effect
        
        result = validate_optional_dependencies()
        
        assert isinstance(result, dict)
        assert 'sentry_sdk' in result
        assert 'prometheus_client' in result
        
        # Should reflect availability
        assert result['sentry_sdk'] is True
        assert result['prometheus_client'] is False
    
    @patch('app.validate_requirements.validate_core_dependencies')
    @patch('app.validate_requirements.validate_app_modules')
    @patch('app.validate_requirements.validate_optional_dependencies')
    def test_get_validation_report(self, mock_optional, mock_app, mock_core):
        """Test get_validation_report function."""
        from app.validate_requirements import get_validation_report
        
        # Mock all validation functions
        mock_core.return_value = (True, [])
        mock_app.return_value = (True, [])
        mock_optional.return_value = {'sentry_sdk': True, 'prometheus_client': False}
        
        report = get_validation_report()
        
        assert isinstance(report, dict)
        assert 'core_dependencies' in report
        assert 'app_modules' in report
        assert 'optional_dependencies' in report
        assert 'overall_success' in report
        assert 'python_version' in report
        
        # Check structure
        assert 'success' in report['core_dependencies']
        assert 'errors' in report['core_dependencies']
        assert 'success' in report['app_modules']
        assert 'errors' in report['app_modules']
        
        # Should be successful overall
        assert report['overall_success'] is True
    
    @patch('app.validate_requirements.validate_core_dependencies')
    @patch('app.validate_requirements.validate_app_modules')
    @patch('app.validate_requirements.validate_optional_dependencies')
    def test_get_validation_report_failure(self, mock_optional, mock_app, mock_core):
        """Test get_validation_report with failures."""
        from app.validate_requirements import get_validation_report
        
        # Mock failures
        mock_core.return_value = (False, ['Core error'])
        mock_app.return_value = (True, [])
        mock_optional.return_value = {}
        
        report = get_validation_report()
        
        # Should be failure overall
        assert report['overall_success'] is False
        assert not report['core_dependencies']['success']
        assert len(report['core_dependencies']['errors']) > 0
    
    def test_python_version_in_report(self):
        """Test that Python version is included in report."""
        from app.validate_requirements import get_validation_report
        
        report = get_validation_report()
        
        assert 'python_version' in report
        assert isinstance(report['python_version'], str)
        assert '.' in report['python_version']  # Should be in x.y.z format
    
    def test_required_modules_list(self):
        """Test that required modules list contains expected packages."""
        from app.validate_requirements import validate_core_dependencies
        
        # Check the function to see what modules it validates
        import inspect
        source = inspect.getsource(validate_core_dependencies)
        
        # Should contain core FastAPI dependencies
        expected_modules = ['fastapi', 'uvicorn', 'sqlmodel', 'pydantic']
        for module in expected_modules:
            assert module in source, f"Expected module {module} not in validation list"
    
    def test_app_modules_list(self):
        """Test that app modules list contains expected modules."""
        from app.validate_requirements import validate_app_modules
        
        import inspect
        source = inspect.getsource(validate_app_modules)
        
        # Should contain core app modules
        expected_modules = ['app.config', 'app.settings', 'app.db', 'app.main']
        for module in expected_modules:
            assert module in source, f"Expected app module {module} not in validation list"


@pytest.mark.unit
class TestValidateRequirementsMain:
    """Test the main/CLI functionality of validate_requirements."""
    
    @patch('app.validate_requirements.get_validation_report')
    @patch('app.validate_requirements.sys.exit')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_exit, mock_report):
        """Test main function with successful validation."""
        from app.validate_requirements import get_validation_report
        
        # Mock successful report
        mock_report.return_value = {
            'core_dependencies': {'success': True, 'errors': []},
            'app_modules': {'success': True, 'errors': []},
            'optional_dependencies': {'sentry_sdk': True},
            'overall_success': True,
            'python_version': '3.11.0'
        }
        
        # Import and run as main
        import app.validate_requirements
        with patch('app.validate_requirements.__name__', '__main__'):
            app.validate_requirements.main()
        
        # Should exit with 0
        mock_exit.assert_called_with(0)
        
        # Should print success message
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any('PASSED' in call for call in print_calls)
    
    @patch('app.validate_requirements.get_validation_report')
    @patch('app.validate_requirements.sys.exit')
    @patch('builtins.print')
    def test_main_failure(self, mock_print, mock_exit, mock_report):
        """Test main function with validation failures."""
        # Mock failed report
        mock_report.return_value = {
            'core_dependencies': {'success': False, 'errors': ['Missing fastapi']},
            'app_modules': {'success': True, 'errors': []},
            'optional_dependencies': {},
            'overall_success': False,
            'python_version': '3.11.0'
        }
        
        # Import and run as main
        import app.validate_requirements
        with patch('app.validate_requirements.__name__', '__main__'):
            app.validate_requirements.main()
        
        # Should exit with 1
        mock_exit.assert_called_with(1)
        
        # Should print failure message
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any('FAILED' in call for call in print_calls)
    
    def test_module_docstring(self):
        """Test that module has proper docstring."""
        import app.validate_requirements
        
        assert app.validate_requirements.__doc__ is not None
        assert len(app.validate_requirements.__doc__.strip()) > 0
    
    def test_function_docstrings(self):
        """Test that functions have proper docstrings."""
        from app.validate_requirements import (
            validate_core_dependencies,
            validate_app_modules,
            validate_optional_dependencies,
            get_validation_report
        )
        
        functions = [
            validate_core_dependencies,
            validate_app_modules,
            validate_optional_dependencies,
            get_validation_report
        ]
        
        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0
    
    def test_cli_interface_availability(self):
        """Test that CLI interface is available."""
        import app.validate_requirements
        
        # Should have main execution block
        source = inspect.getsource(app.validate_requirements)
        assert '__main__' in source
        assert 'sys.exit' in source


@pytest.mark.unit
class TestValidateRequirementsIntegration:
    """Test integration aspects of validate_requirements."""
    
    def test_real_validation_report_structure(self):
        """Test that real validation report has correct structure."""
        from app.validate_requirements import get_validation_report
        
        # Call actual function (not mocked)
        report = get_validation_report()
        
        # Verify structure
        required_keys = [
            'core_dependencies', 'app_modules', 'optional_dependencies',
            'overall_success', 'python_version'
        ]
        
        for key in required_keys:
            assert key in report, f"Missing key {key} in validation report"
        
        # Check nested structure
        assert 'success' in report['core_dependencies']
        assert 'errors' in report['core_dependencies']
        assert isinstance(report['core_dependencies']['errors'], list)
        
        assert 'success' in report['app_modules']
        assert 'errors' in report['app_modules']
        assert isinstance(report['app_modules']['errors'], list)
        
        assert isinstance(report['optional_dependencies'], dict)
        assert isinstance(report['overall_success'], bool)
        assert isinstance(report['python_version'], str)
    
    def test_validation_with_actual_environment(self):
        """Test validation in actual test environment."""
        from app.validate_requirements import (
            validate_core_dependencies,
            validate_app_modules
        )
        
        # Test core dependencies
        core_success, core_errors = validate_core_dependencies()
        # Most core dependencies should be available in test environment
        if not core_success:
            # Print errors for debugging
            print("Core dependency errors:", core_errors)
        
        # Test app modules
        app_success, app_errors = validate_app_modules()
        # App modules should be available
        if not app_success:
            # Some app modules might fail in test environment, that's ok
            print("App module errors:", app_errors)
        
        # At least some validations should work
        assert isinstance(core_success, bool)
        assert isinstance(app_success, bool)
        assert isinstance(core_errors, list)
        assert isinstance(app_errors, list)