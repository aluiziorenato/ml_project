#!/usr/bin/env python3
"""
Simple Coverage Automation Validation

This script validates that our coverage automation workflow components work correctly.
It tests the core functionality without complex dependencies.
"""

import os
import tempfile
import shutil
from pathlib import Path
import subprocess
import sys

def test_basic_coverage_generation():
    """Test basic coverage generation without complex dependencies."""
    print("🧪 Testing basic coverage generation...")
    
    # Create a simple test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

if __name__ == "__main__":
    print(add(2, 3))
    print(multiply(4, 5))
""")
        test_file = f.name
    
    # Create a simple test for the function
    test_dir = Path(tempfile.mkdtemp())
    test_script = test_dir / "test_simple.py"
    
    with open(test_script, 'w') as f:
        f.write(f"""
import sys
sys.path.append('{Path(test_file).parent}')
import {Path(test_file).stem}

def test_add():
    assert {Path(test_file).stem}.add(2, 3) == 5

def test_multiply():
    assert {Path(test_file).stem}.multiply(4, 5) == 20
""")
    
    try:
        # Run coverage on the simple test
        cmd = [
            sys.executable, "-m", "coverage", "run", "-m", "pytest", 
            str(test_script), "-v"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=test_dir,
            timeout=30
        )
        
        print(f"Coverage run result: {result.returncode}")
        
        # Generate HTML report
        html_cmd = [sys.executable, "-m", "coverage", "html"]
        html_result = subprocess.run(
            html_cmd,
            capture_output=True,
            text=True,
            cwd=test_dir,
            timeout=30
        )
        
        print(f"HTML generation result: {html_result.returncode}")
        
        # Generate XML report
        xml_cmd = [sys.executable, "-m", "coverage", "xml"]
        xml_result = subprocess.run(
            xml_cmd,
            capture_output=True,
            text=True,
            cwd=test_dir,
            timeout=30
        )
        
        print(f"XML generation result: {xml_result.returncode}")
        
        # Check if reports were generated
        html_dir = test_dir / "htmlcov"
        xml_file = test_dir / "coverage.xml"
        
        html_exists = html_dir.exists() and (html_dir / "index.html").exists()
        xml_exists = xml_file.exists()
        
        print(f"HTML report exists: {html_exists}")
        print(f"XML report exists: {xml_exists}")
        
        if html_exists and xml_exists:
            print("✅ Basic coverage generation successful")
            return True
        else:
            print("❌ Coverage report generation failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Coverage generation timed out")
        return False
    except Exception as e:
        print(f"❌ Coverage generation failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.unlink(test_file)
            shutil.rmtree(test_dir)
        except:
            pass

def test_workflow_file_syntax():
    """Test that our workflow file has valid YAML syntax."""
    print("🧪 Testing workflow file syntax...")
    
    workflow_file = Path("../.github/workflows/test-coverage-automation.yml")
    
    if not workflow_file.exists():
        print("❌ Workflow file not found")
        return False
    
    try:
        import yaml
        with open(workflow_file, 'r') as f:
            yaml.safe_load(f)
        print("✅ Workflow YAML syntax is valid")
        return True
    except ImportError:
        print("⚠️ PyYAML not available, skipping YAML validation")
        return True
    except Exception as e:
        print(f"❌ Workflow YAML syntax error: {e}")
        return False

def test_documentation_exists():
    """Test that required documentation exists."""
    print("🧪 Testing documentation existence...")
    
    docs_to_check = [
        "../docs/coverage-artifacts-guide.md",
        "../checklist_testes.md"
    ]
    
    missing_docs = []
    for doc_path in docs_to_check:
        if not Path(doc_path).exists():
            missing_docs.append(doc_path)
    
    if missing_docs:
        print(f"❌ Missing documentation: {missing_docs}")
        return False
    
    print("✅ Required documentation exists")
    return True

def test_automation_scripts_exist():
    """Test that our automation scripts exist."""
    print("🧪 Testing automation scripts existence...")
    
    scripts_to_check = [
        "../tests/test_coverage_automation.py",
        "tests/test_backend_coverage_automation.py"
    ]
    
    missing_scripts = []
    for script_path in scripts_to_check:
        if not Path(script_path).exists():
            missing_scripts.append(script_path)
    
    if missing_scripts:
        print(f"❌ Missing automation scripts: {missing_scripts}")
        return False
    
    print("✅ Automation scripts exist")
    return True

def main():
    """Run all validation tests."""
    print("🚀 Starting Coverage Automation Validation")
    print("=" * 50)
    
    tests = [
        ("Basic Coverage Generation", test_basic_coverage_generation),
        ("Workflow File Syntax", test_workflow_file_syntax),
        ("Documentation Existence", test_documentation_exists),
        ("Automation Scripts Existence", test_automation_scripts_exist)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n📊 Validation Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("✅ Coverage automation validation successful!")
        print("🎯 Ready for deployment to CI/CD pipeline.")
        return True
    else:
        print("❌ Some validation tests failed.")
        print("🔧 Review and fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)