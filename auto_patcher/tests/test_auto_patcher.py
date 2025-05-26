import os
import pytest
from pathlib import Path
from src.auto_patcher import AutoPatcher, ProjectType
import json

@pytest.fixture
def sample_node_project(tmp_path):
    """Create a sample Node.js project for testing."""
    project_dir = tmp_path / "node_project"
    project_dir.mkdir()
    
    # Create package.json
    package_json = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "express": "4.17.1",
            "lodash": "4.17.21"
        }
    }
    
    with open(project_dir / "package.json", "w") as f:
        json.dump(package_json, f)
    
    return project_dir

@pytest.fixture
def sample_python_project(tmp_path):
    """Create a sample Python project for testing."""
    project_dir = tmp_path / "python_project"
    project_dir.mkdir()
    
    # Create requirements.txt
    requirements = """flask==2.0.1
requests==2.26.0
pytest==6.2.5"""
    
    with open(project_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    return project_dir

def test_project_analysis_node(sample_node_project):
    """Test project analysis for Node.js project."""
    patcher = AutoPatcher(str(sample_node_project))
    assert patcher.config.project_type == ProjectType.NODE
    assert not patcher.config.has_docker
    assert "package.json" in patcher.config.build_files
    assert "express" in patcher.config.dependencies

def test_project_analysis_python(sample_python_project):
    """Test project analysis for Python project."""
    patcher = AutoPatcher(str(sample_python_project))
    assert patcher.config.project_type == ProjectType.PYTHON
    assert not patcher.config.has_docker
    assert "requirements.txt" in patcher.config.build_files
    assert "flask" in patcher.config.dependencies

def test_dockerfile_generation_node(sample_node_project):
    """Test Dockerfile generation for Node.js project."""
    patcher = AutoPatcher(str(sample_node_project))
    dockerfile = patcher._generate_dockerfile()
    assert "FROM node:18" in dockerfile
    assert "npm install" in dockerfile

def test_dockerfile_generation_python(sample_python_project):
    """Test Dockerfile generation for Python project."""
    patcher = AutoPatcher(str(sample_python_project))
    dockerfile = patcher._generate_dockerfile()
    assert "FROM python:3.9" in dockerfile
    assert "pip install" in dockerfile

def test_dependency_update_node(sample_node_project):
    """Test dependency update for Node.js project."""
    patcher = AutoPatcher(str(sample_node_project))
    success, message = patcher.patch_dependency("express", "4.18.2")
    assert success
    assert "Successfully updated" in message
    
    # Verify package.json was updated
    with open(sample_node_project / "package.json") as f:
        pkg_data = json.load(f)
        assert pkg_data["dependencies"]["express"] == "4.18.2"

def test_dependency_update_python(sample_python_project):
    """Test dependency update for Python project."""
    patcher = AutoPatcher(str(sample_python_project))
    success, message = patcher.patch_dependency("flask", "2.1.0")
    assert success
    assert "Successfully updated" in message
    
    # Verify requirements.txt was updated
    with open(sample_python_project / "requirements.txt") as f:
        content = f.read()
        assert "flask==2.1.0" in content 