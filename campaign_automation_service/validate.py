#!/usr/bin/env python3
"""Validation script for Campaign Automation Service."""

import os
import sys
import ast


def validate_python_syntax(filepath):
    """Validate Python syntax of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    """Main validation function."""
    print("🚀 Campaign Automation Service - Validation Script")
    print("=" * 60)
    
    # Check directory structure
    required_dirs = [
        'src',
        'src/api',
        'src/core', 
        'src/models',
        'src/services',
        'src/utils',
        'tests'
    ]
    
    print("\n📁 Directory Structure Check:")
    all_dirs_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            all_dirs_exist = False
    
    # Check required files
    required_files = [
        'Dockerfile',
        'requirements.txt',
        'README.md',
        'src/main.py',
        'src/api/routes.py',
        'src/core/campaign_manager.py',
        'src/core/metrics_analyzer.py',
        'src/core/competitor_monitor.py',
        'src/models/campaign_models.py',
        'src/services/ai_integration.py',
        'src/services/scheduler.py',
        'src/utils/config.py',
        'src/utils/logger.py',
        'tests/test_campaign_automation.py'
    ]
    
    print("\n📄 Required Files Check:")
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_files_exist = False
    
    # Validate Python syntax
    print("\n🐍 Python Syntax Validation:")
    python_files = []
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for file in ['tests/test_campaign_automation.py']:
        if os.path.exists(file):
            python_files.append(file)
    
    syntax_valid = True
    for py_file in python_files:
        valid, error = validate_python_syntax(py_file)
        if valid:
            print(f"✅ {py_file}")
        else:
            print(f"❌ {py_file}: {error}")
            syntax_valid = False
    
    # Check dependencies
    print("\n📦 Dependencies Check:")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            deps = f.read().strip().split('\n')
        
        required_deps = [
            'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 
            'redis', 'celery', 'httpx', 'structlog'
        ]
        
        for dep in required_deps:
            found = any(dep in line.lower() for line in deps)
            if found:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_dirs_exist and all_files_exist and syntax_valid:
        print("🎉 Validation PASSED! Campaign Automation Service is ready.")
        print("\n🔧 Next Steps:")
        print("   1. Build Docker image: docker build -t campaign-automation .")
        print("   2. Run with docker-compose: docker-compose up campaign_automation_service")
        print("   3. Access API docs: http://localhost:8014/docs")
        return 0
    else:
        print("❌ Validation FAILED! Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())