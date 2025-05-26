import os
import json
import docker
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectType(Enum):
    NODE = "node"
    PYTHON = "python"
    UNKNOWN = "unknown"

@dataclass
class ProjectConfig:
    project_type: ProjectType
    has_docker: bool
    build_files: List[str]
    dependencies: Dict[str, str]

class AutoPatcher:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.docker_client = docker.from_env()
        self.config = self._analyze_project()
        
    def _analyze_project(self) -> ProjectConfig:
        """Analyze project structure and determine configuration."""
        has_docker = (self.project_path / "Dockerfile").exists()
        build_files = []
        project_type = ProjectType.UNKNOWN
        dependencies = {}
        
        # Check for Node.js project
        if (self.project_path / "package.json").exists():
            project_type = ProjectType.NODE
            with open(self.project_path / "package.json") as f:
                pkg_data = json.load(f)
                dependencies = pkg_data.get("dependencies", {})
                build_files = ["package.json"]
                
        # Check for Python project
        elif (self.project_path / "requirements.txt").exists():
            project_type = ProjectType.PYTHON
            with open(self.project_path / "requirements.txt") as f:
                dependencies = {line.split("==")[0]: line.split("==")[1] 
                              for line in f if "==" in line}
            build_files = ["requirements.txt"]
            
        return ProjectConfig(
            project_type=project_type,
            has_docker=has_docker,
            build_files=build_files,
            dependencies=dependencies
        )
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile based on project type."""
        if self.config.project_type == ProjectType.NODE:
            return """FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]"""
        elif self.config.project_type == ProjectType.PYTHON:
            return """FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]"""
        else:
            raise ValueError("Unsupported project type")
    
    def _run_tests(self, container) -> bool:
        """Run tests in the container."""
        try:
            if self.config.project_type == ProjectType.NODE:
                exit_code, _ = container.exec_run("npm test")
            else:
                exit_code, _ = container.exec_run("python -m pytest")
            return exit_code == 0
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return False
    
    def _run_smoke_tests(self, container) -> bool:
        """Run smoke tests to verify basic functionality."""
        try:
            # Start the application
            container.start()
            # Wait for application to be ready
            time.sleep(5)
            # Run basic health check
            exit_code, _ = container.exec_run("curl -f http://localhost:3000/health")
            return exit_code == 0
        except Exception as e:
            logger.error(f"Smoke test failed: {e}")
            return False
        finally:
            container.stop()
    
    def patch_dependency(self, package_name: str, new_version: str) -> Tuple[bool, str]:
        """
        Patch a specific dependency to a new version.
        Returns (success, message)
        """
        try:
            # Update dependency in appropriate file
            if self.config.project_type == ProjectType.NODE:
                self._update_node_dependency(package_name, new_version)
            else:
                self._update_python_dependency(package_name, new_version)
            
            # Build and test in Docker
            success = self._validate_in_docker()
            if success:
                return True, f"Successfully updated {package_name} to {new_version}"
            else:
                return False, "Update failed validation tests"
                
        except Exception as e:
            return False, f"Error during patching: {str(e)}"
    
    def _update_node_dependency(self, package_name: str, new_version: str):
        """Update Node.js dependency in package.json"""
        pkg_path = self.project_path / "package.json"
        with open(pkg_path) as f:
            pkg_data = json.load(f)
        
        pkg_data["dependencies"][package_name] = new_version
        
        with open(pkg_path, "w") as f:
            json.dump(pkg_data, f, indent=2)
    
    def _update_python_dependency(self, package_name: str, new_version: str):
        """Update Python dependency in requirements.txt"""
        req_path = self.project_path / "requirements.txt"
        with open(req_path) as f:
            lines = f.readlines()
        
        with open(req_path, "w") as f:
            for line in lines:
                if line.startswith(package_name):
                    f.write(f"{package_name}=={new_version}\n")
                else:
                    f.write(line)
    
    def _validate_in_docker(self) -> bool:
        """Run validation tests in Docker container."""
        try:
            # Build Docker image
            dockerfile = self._generate_dockerfile()
            image, _ = self.docker_client.images.build(
                path=str(self.project_path),
                dockerfile=dockerfile,
                rm=True
            )
            
            # Run container
            container = self.docker_client.containers.create(
                image.id,
                detach=True
            )
            
            # Run validation tests
            unit_tests = self._run_tests(container)
            smoke_tests = self._run_smoke_tests(container)
            
            # Cleanup
            container.remove()
            self.docker_client.images.remove(image.id)
            
            return unit_tests and smoke_tests
            
        except Exception as e:
            logger.error(f"Docker validation failed: {e}")
            return False 