import os
import argparse
import logging
from pathlib import Path
from orchestrator import PatchingOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Automated Vulnerability Patching Tool')
    parser.add_argument('--repositories', type=str, required=True,
                      help='Path to the repositories directory')
    parser.add_argument('--openai-key', type=str, required=True,
                      help='OpenAI API key')
    parser.add_argument('--output', type=str, default='patch_report.json',
                      help='Output file for the patch report (default: patch_report.json)')
    parser.add_argument('--package', type=str,
                      help='Package name to update (optional)')
    parser.add_argument('--version', type=str,
                      help='New version of the package (optional)')
    parser.add_argument('--project', type=str,
                      help='Specific project to update (optional)')

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = PatchingOrchestrator(args.openai_key)

    try:
        # Step 1: Generate Dockerfiles for all projects
        logger.info("Generating Dockerfiles for all projects...")
        dockerfile_results = orchestrator.generate_dockerfiles(args.repositories)
        
        # Log Dockerfile generation results
        for project, success in dockerfile_results.items():
            status = "successfully" if success else "failed to"
            logger.info(f"{status} generate Dockerfile for {project}")

        # Step 2: If package and version are specified, update the vulnerability
        if args.package and args.version:
            if args.project:
                # Update specific project
                project_path = os.path.join(args.repositories, args.project)
                if not os.path.exists(project_path):
                    logger.error(f"Project {args.project} not found")
                    return
                
                logger.info(f"Updating {args.package} to {args.version} in {args.project}")
                report = orchestrator.update_vulnerability(
                    project_path,
                    args.package,
                    args.version
                )
                logger.info(f"Update result: {report['message']}")
            else:
                # Update all projects
                logger.info(f"Updating {args.package} to {args.version} in all projects")
                for project in dockerfile_results.keys():
                    if dockerfile_results[project]:  # Only update projects with successful Dockerfile generation
                        report = orchestrator.update_vulnerability(
                            project,
                            args.package,
                            args.version
                        )
                        logger.info(f"Update result for {project}: {report['message']}")

        # Step 3: Generate and save report
        logger.info("Generating patch report...")
        orchestrator.save_report(args.output)
        logger.info(f"Report saved to {args.output}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 