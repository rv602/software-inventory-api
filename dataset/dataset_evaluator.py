import os
import time
import json
import subprocess
from typing import List, Dict, Tuple
from evaluation_metrics import ScannerResult, ProjectEvaluation, EvaluationReport

# === Config ===
PROJECT_ROOT = "/home/rav3nf0/Downloads/mock_projects"
AGENTX_CMD = "python3 agentx.py"


def run_agentx(project_path):
    start = time.time()
    subprocess.run(f"{AGENTX_CMD} \"{project_path}\"", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.time()

    # TEMPORARY: Replace with real parsing logic if available
    detected_vulns = 5
    return detected_vulns, round(end - start, 2)

def run_snyk(project_path):
    start = time.time()
    result = subprocess.run(
        ["snyk", "test", "--json", "--all-projects", "--dir", project_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    end = time.time()

    try:
        output = json.loads(result.stdout)
        issues = output.get("vulnerabilities", []) if isinstance(output, dict) else []
        return len(issues), round(end - start, 2)
    except Exception:
        return 0, round(end - start, 2)

class VulnerabilityScanner:
    def __init__(self, name: str):
        self.name = name

    def scan(self, project_path: str) -> Tuple[int, float, List[str]]:
        """Returns (vulnerabilities_found, detection_time, found_dependencies)"""
        raise NotImplementedError

class NexusIQScanner(VulnerabilityScanner):
    def __init__(self):
        super().__init__("Nexus IQ")
        self.server_url = "http://localhost:8070"
        self.application_id = "test-application"
        self.stage = "build"

    def scan(self, project_path: str) -> Tuple[int, float, List[str]]:
        start_time = time.time()
        try:
            report_file = os.path.join(project_path, "nexus-iq-report.json")
            
            result = subprocess.run(
                [
                    "nexus-iq-cli",
                    "-s", self.server_url,
                    "-a", self.application_id,
                    "-t", self.stage,
                    "-i", project_path,
                    "-r", report_file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            found_dependencies = []
            if 'components' in report:
                for component in report['components']:
                    if component.get('securityData', {}).get('securityIssues'):
                        found_dependencies.append(component.get('name', ''))
            
            detection_time = time.time() - start_time
            return len(found_dependencies), detection_time, found_dependencies
        except Exception as e:
            print(f"Error running Nexus IQ scan: {e}")
            return 0, time.time() - start_time, []

class DependabotScanner(VulnerabilityScanner):
    def __init__(self):
        super().__init__("Dependabot")

    def scan(self, project_path: str) -> Tuple[int, float, List[str]]:
        start_time = time.time()
        try:
            result = subprocess.run(
                ["dependabot", "check", "--format", "json", project_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            output = json.loads(result.stdout)
            found_dependencies = []
            if isinstance(output, dict) and 'dependencies' in output:
                for dep in output['dependencies']:
                    if dep.get('vulnerabilities'):
                        found_dependencies.append(dep.get('name', ''))
            
            detection_time = time.time() - start_time
            return len(found_dependencies), detection_time, found_dependencies
        except Exception as e:
            print(f"Error running Dependabot scan: {e}")
            return 0, time.time() - start_time, []

class VULNDETScanner(VulnerabilityScanner):
    def __init__(self):
        super().__init__("VULNDET")

    def scan(self, project_path: str) -> Tuple[int, float, List[str]]:
        start_time = time.time()
        try:
            result = subprocess.run(
                ["vulndet", "--format", "json", project_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            output = json.loads(result.stdout)
            found_dependencies = []
            if isinstance(output, dict) and 'dependencies' in output:
                for dep in output['dependencies']:
                    if dep.get('vulnerabilities'):
                        found_dependencies.append(dep.get('name', ''))
            
            detection_time = time.time() - start_time
            return len(found_dependencies), detection_time, found_dependencies
        except Exception as e:
            print(f"Error running VULNDET scan: {e}")
            return 0, time.time() - start_time, []

class DatasetEvaluator:
    def __init__(self, mapping_file: str, repositories_dir: str):
        self.mapping_file = mapping_file
        self.repositories_dir = repositories_dir
        self.scanners = [
            VULNDETScanner(),
            DependabotScanner(),
            NexusIQScanner()
        ]
        self.expected_vulnerabilities = self._load_mapping()

    def _load_mapping(self) -> Dict[str, List[str]]:
        with open(self.mapping_file, 'r') as f:
            mapping = json.load(f)
        
        # Get expected dependencies from mapping
        expected = {}
        for project in mapping:
            project_name = project['project_name']
            dependencies = [dep['name'] for dep in project['dependencies']]
            expected[project_name] = dependencies
        
        return expected

    def evaluate_project(self, project_name: str) -> Dict:
        project_path = os.path.join(self.repositories_dir, project_name)
        expected_deps = self.expected_vulnerabilities.get(project_name, [])
        
        scanner_results = []
        for scanner in self.scanners:
            vulns_found, detection_time, found_deps = scanner.scan(project_path)
            
            result = {
                "scanner_name": scanner.name,
                "vulnerabilities_found": vulns_found,
                "detection_time": round(detection_time, 1),
                "found_dependencies": found_deps
            }
            scanner_results.append(result)
        
        return {
            "project_name": project_name,
            "expected_vulnerabilities": len(expected_deps),
            "scanners": scanner_results
        }

    def evaluate_all(self) -> List[Dict]:
        results = []
        
        for project_name in self.expected_vulnerabilities.keys():
            print(f"Evaluating {project_name}...")
            evaluation = self.evaluate_project(project_name)
            results.append(evaluation)
        
        return results

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    mapping_file = os.path.join(current_dir, 'mapping.json')
    repositories_dir = os.path.join(current_dir, 'repositories')
    
    # Create and run the evaluator
    evaluator = DatasetEvaluator(mapping_file, repositories_dir)
    results = evaluator.evaluate_all()
    
    # Save results
    with open("report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Evaluation complete. Results saved to report.json")

if __name__ == "__main__":
    main()
