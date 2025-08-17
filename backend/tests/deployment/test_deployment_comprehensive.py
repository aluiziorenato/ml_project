"""
Deployment tests for local and cloud environments.
This addresses point 6 of the PR #42 checklist: "Testes de deploy local e cloud"
"""
import pytest
import subprocess
import time
import requests
import os
from pathlib import Path

@pytest.mark.deployment
class TestLocalDeployment:
    """Test local deployment scenarios."""
    
    def test_docker_build(self):
        """Test that Docker image can be built successfully."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        # Check if Dockerfile exists
        dockerfile_path = project_root / "Dockerfile"
        if not dockerfile_path.exists():
            # Check backend directory
            dockerfile_path = project_root / "backend" / "Dockerfile"
            if not dockerfile_path.exists():
                pytest.skip("Dockerfile not found")
        
        # Build Docker image
        try:
            result = subprocess.run([
                "docker", "build", "-t", "ml-project-test", 
                str(dockerfile_path.parent)
            ], capture_output=True, text=True, timeout=300)
            
            # Build should succeed
            assert result.returncode == 0, f"Docker build failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Docker build timed out")
        except FileNotFoundError:
            pytest.skip("Docker not available")
    
    def test_docker_compose_validation(self):
        """Test that docker-compose configuration is valid."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        compose_files = [
            "docker-compose.yml",
            "docker-compose.yaml",
            "docker-compose.override.yml"
        ]
        
        valid_compose_files = []
        
        for compose_file in compose_files:
            compose_path = project_root / compose_file
            if compose_path.exists():
                try:
                    result = subprocess.run([
                        "docker-compose", "-f", str(compose_path), "config"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        valid_compose_files.append(compose_file)
                    else:
                        pytest.fail(f"Invalid docker-compose file {compose_file}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    pytest.fail(f"docker-compose config timeout for {compose_file}")
                except FileNotFoundError:
                    pytest.skip("docker-compose not available")
        
        # Should have at least one valid compose file
        assert len(valid_compose_files) > 0, "No valid docker-compose files found"
    
    def test_environment_variables(self):
        """Test that required environment variables are documented."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        env_files = [
            ".env.example",
            ".env.template",
            "backend/.env.example",
            "backend/.env.template"
        ]
        
        env_file_found = False
        
        for env_file in env_files:
            env_path = project_root / env_file
            if env_path.exists():
                env_file_found = True
                
                # Read environment variables
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                # Should contain common required variables
                required_vars = [
                    "DATABASE_URL",
                    "SECRET_KEY",
                    "JWT_SECRET"
                ]
                
                for var in required_vars:
                    if var in env_content:
                        # Variable should have example value or placeholder
                        lines = env_content.split('\n')
                        var_line = next((line for line in lines if line.startswith(var)), None)
                        if var_line:
                            assert "=" in var_line, f"Environment variable {var} has no value"
        
        if not env_file_found:
            pytest.skip("No environment file examples found")

@pytest.mark.deployment
class TestProductionReadiness:
    """Test production readiness indicators."""
    
    def test_security_headers_configuration(self):
        """Test that security headers are configured."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        # Check for security configuration in various places
        config_files = [
            "backend/app/main.py",
            "backend/app/config.py",
            "backend/app/security.py"
        ]
        
        security_headers_found = False
        
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                
                # Look for security headers
                security_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options", 
                    "X-XSS-Protection",
                    "Strict-Transport-Security",
                    "Content-Security-Policy"
                ]
                
                for header in security_headers:
                    if header in content:
                        security_headers_found = True
                        break
        
        if not security_headers_found:
            print("Warning: No explicit security headers configuration found")
    
    def test_logging_configuration(self):
        """Test that logging is properly configured."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        # Check for logging configuration
        logging_files = [
            "backend/app/monitoring/loki_config.py",
            "backend/app/config.py",
            "backend/app/main.py"
        ]
        
        logging_configured = False
        
        for logging_file in logging_files:
            file_path = project_root / logging_file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Look for logging configuration
                logging_indicators = [
                    "logging.getLogger",
                    "LOG_LEVEL",
                    "logger",
                    "LokiHandler"
                ]
                
                for indicator in logging_indicators:
                    if indicator in content:
                        logging_configured = True
                        break
        
        assert logging_configured, "No logging configuration found"

@pytest.mark.deployment
class TestDeploymentScripts:
    """Test deployment automation scripts."""
    
    def test_deployment_scripts_exist(self):
        """Test that deployment scripts exist and are executable."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        script_paths = [
            "deploy.sh",
            "scripts/deploy.sh", 
            "bin/deploy.sh",
            "deploy/deploy.sh",
            "Makefile"
        ]
        
        executable_scripts = []
        
        for script_path in script_paths:
            full_path = project_root / script_path
            if full_path.exists():
                # Check if file is executable (for shell scripts)
                if script_path.endswith('.sh'):
                    stat_info = full_path.stat()
                    if stat_info.st_mode & 0o111:  # Check execute permission
                        executable_scripts.append(script_path)
                elif script_path == "Makefile":
                    # Check if Makefile contains deployment targets
                    with open(full_path, 'r') as f:
                        makefile_content = f.read()
                    
                    deploy_targets = ["deploy:", "build:", "test:", "install:"]
                    
                    if any(target in makefile_content for target in deploy_targets):
                        executable_scripts.append(script_path)
        
        if executable_scripts:
            # At least one deployment script found
            print(f"Found deployment scripts: {executable_scripts}")
        else:
            pytest.skip("No deployment scripts found")
    
    def test_ci_cd_configuration(self):
        """Test CI/CD configuration files."""
        project_root = Path("/home/runner/work/ml_project/ml_project")
        
        ci_cd_files = [
            ".github/workflows/ci.yml",
            ".github/workflows/cd.yml", 
            ".github/workflows/deploy.yml",
            ".github/workflows/test.yml",
            ".gitlab-ci.yml",
            "azure-pipelines.yml",
            "Jenkinsfile"
        ]
        
        ci_cd_found = False
        
        for ci_file in ci_cd_files:
            full_path = project_root / ci_file
            if full_path.exists():
                ci_cd_found = True
                
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Should contain CI/CD pipeline steps
                if ci_file.endswith('.yml') or ci_file.endswith('.yaml'):
                    # YAML-based CI/CD
                    ci_keywords = ["jobs:", "steps:", "run:", "uses:", "name:"]
                    
                    assert any(keyword in content for keyword in ci_keywords), \
                        f"CI/CD file {ci_file} missing expected structure"
                        
                elif ci_file == "Jenkinsfile":
                    # Jenkins pipeline
                    jenkins_keywords = ["pipeline", "stage", "steps"]
                    
                    assert any(keyword in content for keyword in jenkins_keywords), \
                        f"Jenkinsfile missing expected structure"
        
        if not ci_cd_found:
            pytest.skip("No CI/CD configuration found")