from dataclasses import dataclass
from typing import List, Dict
import json
from collections import defaultdict

@dataclass
class ScannerMetrics:
    scanner_name: str
    total_vulnerabilities_found: int
    total_detection_time: float
    average_detection_time: float
    detection_rate: float  # percentage of vulnerabilities found
    total_projects_scanned: int
    found_dependencies: Dict[str, int]  # dependency name -> count of times found

class EvaluationMetrics:
    def __init__(self, report_file: str):
        self.report_file = report_file
        self.scanner_metrics: Dict[str, ScannerMetrics] = {}
        self.total_projects = 0
        self.total_expected_vulnerabilities = 0
        self.load_report()

    def load_report(self):
        with open(self.report_file, 'r') as f:
            report = json.load(f)

        self.total_projects = len(report)
        
        # Initialize metrics for each scanner
        scanner_names = set()
        for project in report:
            self.total_expected_vulnerabilities += project['expected_vulnerabilities']
            for scanner in project['scanners']:
                scanner_names.add(scanner['scanner_name'])

        for scanner_name in scanner_names:
            self.scanner_metrics[scanner_name] = ScannerMetrics(
                scanner_name=scanner_name,
                total_vulnerabilities_found=0,
                total_detection_time=0,
                average_detection_time=0,
                detection_rate=0,
                total_projects_scanned=0,
                found_dependencies=defaultdict(int)
            )

        # Calculate metrics
        for project in report:
            for scanner in project['scanners']:
                metrics = self.scanner_metrics[scanner['scanner_name']]
                metrics.total_vulnerabilities_found += scanner['vulnerabilities_found']
                metrics.total_detection_time += scanner['detection_time']
                metrics.total_projects_scanned += 1
                
                # Count found dependencies
                for dep in scanner['found_dependencies']:
                    metrics.found_dependencies[dep] += 1

        # Calculate averages and rates
        for metrics in self.scanner_metrics.values():
            metrics.average_detection_time = metrics.total_detection_time / metrics.total_projects_scanned
            metrics.detection_rate = (metrics.total_vulnerabilities_found / self.total_expected_vulnerabilities) * 100

    def print_summary(self):
        print("\n=== Scanner Performance Summary ===")
        print(f"Total Projects Scanned: {self.total_projects}")
        print(f"Total Expected Vulnerabilities: {self.total_expected_vulnerabilities}")
        print("\nScanner Metrics:")
        
        for scanner_name, metrics in self.scanner_metrics.items():
            print(f"\n{scanner_name}:")
            print(f"  Total Vulnerabilities Found: {metrics.total_vulnerabilities_found}")
            print(f"  Detection Rate: {metrics.detection_rate:.1f}%")
            print(f"  Average Detection Time: {metrics.average_detection_time:.1f} seconds")
            print(f"  Most Common Dependencies Found:")
            # Sort dependencies by count and show top 5
            sorted_deps = sorted(metrics.found_dependencies.items(), key=lambda x: x[1], reverse=True)
            for dep, count in sorted_deps[:5]:
                print(f"    - {dep}: found {count} times")

    def save_summary(self, output_file: str):
        summary = {
            "total_projects": self.total_projects,
            "total_expected_vulnerabilities": self.total_expected_vulnerabilities,
            "scanner_metrics": {
                name: {
                    "total_vulnerabilities_found": metrics.total_vulnerabilities_found,
                    "detection_rate": metrics.detection_rate,
                    "average_detection_time": metrics.average_detection_time,
                    "total_projects_scanned": metrics.total_projects_scanned,
                    "most_common_dependencies": dict(sorted(metrics.found_dependencies.items(), 
                                                          key=lambda x: x[1], 
                                                          reverse=True)[:5])
                }
                for name, metrics in self.scanner_metrics.items()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

def main():
    # Analyze the report
    metrics = EvaluationMetrics("/report.json")
    
    # Print summary to console
    metrics.print_summary()
    
    # Save summary to file
    metrics.save_summary("scanner_summary.json")
    print("\n✅ Summary saved to scanner_summary.json")

if __name__ == "__main__":
    main()
 