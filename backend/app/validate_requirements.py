"""
Module for validating project dependencies and imports.
Provides functionality to check if all required packages are installed
and can be imported successfully.
"""
import importlib
import sys
from typing import Dict, List, Tuple


def validate_core_dependencies() -> Tuple[bool, List[str]]:
    """
    Validate core dependencies can be imported.
    
    Returns:
        Tuple[bool, List[str]]: (success, list of errors)
    """
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlmodel',
        'psycopg2',
        'pydantic',
        'pydantic_settings',
        'jose',  # python-jose module is imported as 'jose'
        'passlib',
        'httpx',
        'pytest',
    ]
    
    errors = []
    
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            errors.append(f"Failed to import {module_name}: {e}")
    
    return len(errors) == 0, errors


def validate_app_modules() -> Tuple[bool, List[str]]:
    """
    Validate internal app modules can be imported.
    
    Returns:
        Tuple[bool, List[str]]: (success, list of errors)
    """
    app_modules = [
        'app.config',
        'app.settings',
        'app.db',
        'app.main',
        'app.startup',
        'app.core.security',
        'app.auth.token',
        'app.models',
    ]
    
    errors = []
    
    for module_name in app_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            errors.append(f"Failed to import {module_name}: {e}")
    
    return len(errors) == 0, errors


def validate_optional_dependencies() -> Dict[str, bool]:
    """
    Check optional dependencies availability.
    
    Returns:
        Dict[str, bool]: Dictionary mapping dependency name to availability
    """
    optional_deps = {
        'sentry_sdk': False,
        'prometheus_client': False,
        'python_logging_loki': False,
        'psutil': False,
    }
    
    for dep_name in optional_deps:
        try:
            importlib.import_module(dep_name)
            optional_deps[dep_name] = True
        except ImportError:
            pass
    
    return optional_deps


def get_validation_report() -> Dict[str, any]:
    """
    Generate comprehensive validation report.
    
    Returns:
        Dict containing validation results
    """
    core_success, core_errors = validate_core_dependencies()
    app_success, app_errors = validate_app_modules()
    optional_deps = validate_optional_dependencies()
    
    return {
        'core_dependencies': {
            'success': core_success,
            'errors': core_errors
        },
        'app_modules': {
            'success': app_success,
            'errors': app_errors
        },
        'optional_dependencies': optional_deps,
        'overall_success': core_success and app_success,
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }


def main():
    """CLI interface for dependency validation."""
    report = get_validation_report()
    
    print("🔍 Dependency Validation Report")
    print("=" * 40)
    
    print(f"Python Version: {report['python_version']}")
    print()
    
    # Core dependencies
    print("📦 Core Dependencies:")
    if report['core_dependencies']['success']:
        print("  ✅ All core dependencies available")
    else:
        print("  ❌ Core dependency issues:")
        for error in report['core_dependencies']['errors']:
            print(f"    - {error}")
    print()
    
    # App modules
    print("🏗️  App Modules:")
    if report['app_modules']['success']:
        print("  ✅ All app modules can be imported")
    else:
        print("  ❌ App module issues:")
        for error in report['app_modules']['errors']:
            print(f"    - {error}")
    print()
    
    # Optional dependencies
    print("📋 Optional Dependencies:")
    for dep, available in report['optional_dependencies'].items():
        status = "✅" if available else "⚠️ "
        print(f"  {status} {dep}: {'Available' if available else 'Not available'}")
    print()
    
    # Overall result
    if report['overall_success']:
        print("🎉 Overall Status: ✅ PASSED")
        sys.exit(0)
    else:
        print("💥 Overall Status: ❌ FAILED")
        print("Please install missing dependencies and fix import issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()