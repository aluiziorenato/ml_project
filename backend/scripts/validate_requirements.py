#!/usr/bin/env python3
"""
Script for validating project dependencies and requirements.
This script checks if all dependencies listed in requirements.txt
can be imported and provides a comprehensive validation report.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the app directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.validate_requirements import get_validation_report
except ImportError:
    print("❌ Could not import app.validate_requirements module")
    print("Make sure you're running this script from the backend directory")
    sys.exit(1)


def check_requirements_file() -> bool:
    """Check if requirements.txt exists and is readable."""
    req_file = project_root / "requirements.txt"
    if not req_file.exists():
        print(f"❌ requirements.txt not found at {req_file}")
        return False
    
    try:
        with open(req_file, 'r') as f:
            lines = f.readlines()
        print(f"✅ requirements.txt found with {len(lines)} lines")
        return True
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False


def check_pip_install() -> bool:
    """Check if pip can install requirements (dry-run)."""
    req_file = project_root / "requirements.txt"
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '--dry-run', '-r', str(req_file)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Requirements can be installed via pip")
            return True
        else:
            print("❌ Issues with pip install:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Pip install check timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking pip install: {e}")
        return False


def main():
    """Main validation function."""
    print("🔧 Project Requirements Validation")
    print("=" * 50)
    print()
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    print(f"Project root: {project_root}")
    print()
    
    success_flags = []
    
    # Check requirements.txt
    print("📄 Checking requirements.txt...")
    req_check = check_requirements_file()
    success_flags.append(req_check)
    print()
    
    # Check pip compatibility
    print("🔧 Checking pip install compatibility...")
    pip_check = check_pip_install()
    success_flags.append(pip_check)
    print()
    
    # Run dependency validation
    print("📦 Running dependency validation...")
    report = get_validation_report()
    
    print(f"Python Version: {report['python_version']}")
    print()
    
    # Core dependencies
    print("Core Dependencies:")
    if report['core_dependencies']['success']:
        print("  ✅ All core dependencies available")
    else:
        print("  ❌ Core dependency issues:")
        for error in report['core_dependencies']['errors']:
            print(f"    - {error}")
    success_flags.append(report['core_dependencies']['success'])
    print()
    
    # App modules
    print("App Modules:")
    if report['app_modules']['success']:
        print("  ✅ All app modules can be imported")
    else:
        print("  ❌ App module issues:")
        for error in report['app_modules']['errors']:
            print(f"    - {error}")
    success_flags.append(report['app_modules']['success'])
    print()
    
    # Optional dependencies summary
    available_optional = sum(report['optional_dependencies'].values())
    total_optional = len(report['optional_dependencies'])
    print(f"Optional Dependencies: {available_optional}/{total_optional} available")
    print()
    
    # Overall result
    all_success = all(success_flags)
    print("=" * 50)
    if all_success:
        print("🎉 VALIDATION PASSED: All requirements are satisfied!")
        print()
        print("✅ You can run the application with:")
        print("   python -m uvicorn app.main:app --reload")
        print("✅ You can run tests with:")
        print("   pytest -v")
        return 0
    else:
        print("💥 VALIDATION FAILED: Issues found!")
        print()
        print("🔧 Suggested fixes:")
        if not req_check:
            print("   - Ensure you're in the backend directory")
        if not pip_check:
            print("   - Run: pip install -r requirements.txt")
        if not report['core_dependencies']['success']:
            print("   - Install missing core dependencies")
        if not report['app_modules']['success']:
            print("   - Fix import issues in app modules")
        print()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)