import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from .docker_generator import DockerfileGenerator
from .vulnerability_updater import VulnerabilityUpdater

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatchingOrchestrator:
    def __init__(self, openai_api_key: str):
        self.docker_generator = DockerfileGenerator(openai_api_key)
        self.vulnerability_updater = VulnerabilityUpdater()
        self.reports = []

    def _get_projects(self, repositories_dir: str) -> List[str]:
        """Get list of projects from repositories directory."""
        projects = []
        for item in Path(repositories_dir).iterdir():
            if item.is_dir():
                projects.append(str(item))
        return projects

    def generate_dockerfiles(self, repositories_dir: str) -> Dict[str, bool]:
        """Generate Dockerfiles for all projects."""
        results = {}
        projects = self._get_projects(repositories_dir)
        
        for project_path in projects:
            logger.info(f"Generating Dockerfile for {project_path}")
            success = self.docker_generator.generate_dockerfile(project_path) is not None
            results[project_path] = success
            
        return results

    def update_vulnerability(self, project_path: str, package_name: str, new_version: str) -> Dict:
        """Update a specific vulnerability in a project."""
        logger.info(f"Updating {package_name} to {new_version} in {project_path}")
        
        success, message, report = self.vulnerability_updater.update_vulnerability(
            project_path,
            package_name,
            new_version
        )
        
        report["project_path"] = project_path
        report["success"] = success
        report["message"] = message
        
        self.reports.append(report)
        return report

    def get_summary_report(self) -> Dict:
        """Generate summary report of all updates."""
        total_updates = len(self.reports)
        successful_updates = sum(1 for r in self.reports if r["success"])
        
        return {
            "total_updates": total_updates,
            "successful_updates": successful_updates,
            "failed_updates": total_updates - successful_updates,
            "success_rate": (successful_updates / total_updates * 100) if total_updates > 0 else 0,
            "detailed_reports": self.reports
        }

    def save_report(self, output_path: str):
        """Save the summary report to a file."""
        report = self.get_summary_report()
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {output_path}") 