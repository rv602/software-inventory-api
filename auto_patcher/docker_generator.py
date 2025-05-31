import os
import json
import openai
from typing import Dict, Optional
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerfileGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        openai.api_key = self.openai_api_key

    def _analyze_project_files(self, project_path: str) -> Dict:
        """Analyze project files to determine project type and dependencies."""
        project_path = Path(project_path)
        analysis = {
            "project_type": None,
            "dependencies": {},
            "build_files": [],
            "has_docker": False,
            "test_files": []
        }

        # Check for Dockerfile
        if (project_path / "Dockerfile").exists():
            analysis["has_docker"] = True
            analysis["build_files"].append("Dockerfile")

        # Check for Node.js project
        if (project_path / "package.json").exists():
            analysis["project_type"] = "node"
            with open(project_path / "package.json") as f:
                pkg_data = json.load(f)
                analysis["dependencies"] = pkg_data.get("dependencies", {})
                analysis["build_files"].append("package.json")
                # Check for test scripts
                if "scripts" in pkg_data and "test" in pkg_data["scripts"]:
                    analysis["test_files"].append("package.json")

        # Check for Python project
        elif (project_path / "requirements.txt").exists():
            analysis["project_type"] = "python"
            with open(project_path / "requirements.txt") as f:
                deps = {}
                for line in f:
                    if "==" in line:
                        name, version = line.strip().split("==")
                        deps[name] = version
                analysis["dependencies"] = deps
                analysis["build_files"].append("requirements.txt")
                # Check for test files
                if (project_path / "tests").exists():
                    analysis["test_files"].append("tests")

        return analysis

    def _generate_llm_prompt(self, analysis: Dict) -> str:
        """Generate prompt for LLM based on project analysis."""
        prompt = f"""Generate a production-ready Dockerfile for a {analysis['project_type']} project with the following specifications:

Project Analysis:
- Type: {analysis['project_type']}
- Dependencies: {json.dumps(analysis['dependencies'], indent=2)}
- Build Files: {', '.join(analysis['build_files'])}
- Test Files: {', '.join(analysis['test_files']) if analysis['test_files'] else 'None'}

Requirements:
1. Base Image:
   - Use the latest stable base image for {analysis['project_type']}
   - Specify exact version for reproducibility

2. Build Process:
   - Multi-stage build for minimal final image
   - Copy only necessary files
   - Install dependencies in build stage
   - Optimize layer caching

3. Security:
   - Run as non-root user
   - Scan for vulnerabilities
   - Remove unnecessary build tools
   - Use .dockerignore

4. Testing:
   - Include test running capability
   - Add health check endpoint
   - Implement build verification steps
   - Add test assertions for:
     * Dependency installation
     * Build process
     * Application startup
     * Health check response

5. Environment:
   - Support both development and production
   - Use environment variables for configuration
   - Set up proper working directory
   - Configure logging

6. Optimization:
   - Minimize image size
   - Optimize layer caching
   - Use appropriate .dockerignore
   - Implement proper cleanup

Please provide only the Dockerfile content without any explanations. The Dockerfile should be production-ready and include all necessary test assertions."""

        return prompt

    def generate_dockerfile(self, project_path: str) -> Optional[str]:
        """Generate Dockerfile using LLM based on project analysis."""
        try:
            # Analyze project
            analysis = self._analyze_project_files(project_path)
            if not analysis["project_type"]:
                logger.error("Could not determine project type")
                return None

            # Generate prompt
            prompt = self._generate_llm_prompt(analysis)

            # Get LLM response
            response = openai.ChatCompletion.create(
                model="gpt-4-mini",
                messages=[
                    {"role": "system", "content": "You are a Docker expert specializing in creating secure, optimized, and testable Dockerfiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000
            )

            dockerfile_content = response.choices[0].message.content.strip()

            # Save Dockerfile
            dockerfile_path = Path(project_path) / "Dockerfile"
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)

            logger.info(f"Generated Dockerfile for {project_path}")
            return dockerfile_content

        except Exception as e:
            logger.error(f"Error generating Dockerfile: {e}")
            return None 