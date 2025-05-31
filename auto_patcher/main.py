import os
import json
import logging
from pathlib import Path
from docker_generator import DockerfileGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_project_mapping():
    """Load project mapping from mapping.json"""
    try:
        with open('../dataset/mapping.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading mapping.json: {e}")
        raise

def generate_dockerfiles():
    """Generate Dockerfiles for all projects in the mapping"""
    try:
        # Initialize DockerfileGenerator
        generator = DockerfileGenerator()
        
        # Load project mapping
        projects = load_project_mapping()
        
        # Process each project
        for project in projects:
            project_name = project['project_name']
            project_type = project['project_type']
            project_path = f"dataset/repositories/{project_name}"
            
            logger.info(f"Processing project: {project_name} ({project_type})")
            
            # Verify project path exists
            if not os.path.exists(project_path):
                logger.warning(f"Project path does not exist: {project_path}")
                continue
                
            # Generate Dockerfile
            try:
                dockerfile_content = generator.generate_dockerfile(project_path)
                if dockerfile_content:
                    logger.info(f"Successfully generated Dockerfile for {project_name}")
                else:
                    logger.error(f"Failed to generate Dockerfile for {project_name}")
            except Exception as e:
                logger.error(f"Error generating Dockerfile for {project_name}: {e}")
                continue

    except Exception as e:
        logger.error(f"An error occurred during Dockerfile generation: {e}")
        raise

def main():
    """Main entry point"""
    try:
        logger.info("Starting Dockerfile generation process...")
        generate_dockerfiles()
        logger.info("Dockerfile generation process completed")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 