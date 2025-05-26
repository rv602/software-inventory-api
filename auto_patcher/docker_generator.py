import os
import json
import openai
from typing import Dict, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerfileGenerator:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

    def _analyze_project_files(self, project_path: str) -> Dict:
        """Analyze project files to determine project type and dependencies."""
        project_path = Path(project_path)
        analysis = {
            "project_type": None,
            "dependencies": {},
            "build_files": [],
            "has_docker": False
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

        return analysis

    def _generate_llm_prompt(self, analysis: Dict) -> str:
        """Generate prompt for LLM based on project analysis."""
        prompt = f"""Generate a Dockerfile for a {analysis['project_type']} project with the following specifications:

Project Type: {analysis['project_type']}
Dependencies: {json.dumps(analysis['dependencies'], indent=2)}
Build Files: {', '.join(analysis['build_files'])}

Requirements:
1. Use the latest stable base image
2. Include all necessary build steps
3. Optimize for security and minimal image size
4. Include health check
5. Set up proper working directory
6. Include test running capability
7. Handle both development and production environments

Please provide only the Dockerfile content without any explanations."""

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
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Docker expert. Generate optimized Dockerfiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
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