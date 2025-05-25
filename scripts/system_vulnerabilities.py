from datetime import datetime
import json
import os
import platform
import subprocess
import uuid
import time
import gzip
from typing import Dict, List, Optional
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constants import log_dir
from constants import db_url_prod, db_url_dev, db_name, collection_system_name

class SystemVulnerabilityScanner:
    def __init__(self):
        self.system = platform.system()
        self.vulnerabilities = []
        self.start_time = time.time()

    def run_command(self, cmd: str) -> Optional[str]:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"Error running command '{cmd}': {e}")
            return None

    def check_brew_vulnerabilities(self) -> List[Dict]:
        if self.system != "Darwin":
            return []

        vulnerabilities = []
        # Check for outdated packages
        outdated = self.run_command("brew outdated --json=v2")
        if outdated:
            try:
                packages = json.loads(outdated)
                for pkg in packages.get("formulae", []):
                    vulnerabilities.append({
                        "Name": pkg["name"],
                        "Current": pkg["current_version"],
                        "Latest": pkg["latest_version"],
                        "Type": "brew",
                        "Severity": "medium"  # Outdated packages are medium severity
                    })
            except json.JSONDecodeError:
                print("Error parsing brew outdated output")

        # Check for security issues
        audit = self.run_command("brew audit")
        if audit:
            for line in audit.splitlines():
                if "Error:" in line:
                    vulnerabilities.append({
                        "Name": line.split("Error:")[0].strip(),
                        "Issue": line.split("Error:")[1].strip(),
                        "Type": "brew",
                        "Severity": "high"
                    })

        return vulnerabilities

    def check_apt_vulnerabilities(self) -> List[Dict]:
        if self.system != "Linux":
            return []

        vulnerabilities = []
        # Update package lists
        self.run_command("sudo apt-get update")
        
        # Check for security updates
        security_updates = self.run_command("apt-get -s upgrade | grep -i security")
        if security_updates:
            for line in security_updates.splitlines():
                vulnerabilities.append({
                    "Name": line.split()[1],
                    "Issue": "Security update available",
                    "Type": "apt",
                    "Severity": "high"
                })

        # Check for broken packages
        broken = self.run_command("apt-get check")
        if broken and "0 broken" not in broken:
            vulnerabilities.append({
                "Name": "System Packages",
                "Issue": "Broken package dependencies detected",
                "Type": "apt",
                "Severity": "critical"
            })

        return vulnerabilities

    def check_yum_vulnerabilities(self) -> List[Dict]:
        if self.system != "Linux":
            return []

        vulnerabilities = []
        # Check for security updates
        security_updates = self.run_command("yum check-update --security")
        if security_updates and "No packages needed for security" not in security_updates:
            for line in security_updates.splitlines():
                if line.strip() and not line.startswith("Loaded plugins:"):
                    parts = line.split()
                    if len(parts) >= 1:
                        vulnerabilities.append({
                            "Name": parts[0],
                            "Issue": "Security update available",
                            "Type": "yum",
                            "Severity": "high"
                        })

        return vulnerabilities

    def check_global_python_packages(self) -> List[Dict]:
        vulnerabilities = []
        # Check for outdated packages
        outdated = self.run_command("pip list --outdated --format=json")
        if outdated:
            try:
                packages = json.loads(outdated)
                for pkg in packages:
                    vulnerabilities.append({
                        "Name": pkg["name"],
                        "Current": pkg["version"],
                        "Latest": pkg["latest_version"],
                        "Type": "python",
                        "Severity": "medium"
                    })
            except json.JSONDecodeError:
                print("Error parsing pip outdated output")

        return vulnerabilities

    def check_global_node_packages(self) -> List[Dict]:
        vulnerabilities = []
        # Check for outdated packages
        outdated = self.run_command("npm list -g --json")
        if outdated:
            try:
                packages = json.loads(outdated)
                for name, info in packages.get("dependencies", {}).items():
                    if "wanted" in info and info["wanted"] != info.get("current"):
                        vulnerabilities.append({
                            "Name": name,
                            "Current": info.get("current", "unknown"),
                            "Latest": info["wanted"],
                            "Type": "node",
                            "Severity": "medium"
                        })
            except json.JSONDecodeError:
                print("Error parsing npm list output")

        return vulnerabilities

    def check_system_security(self) -> List[Dict]:
        vulnerabilities = []
        
        # Check for common security tools
        security_tools = {
            "firewall": {
                "darwin": "pfctl -s all",
                "linux": "ufw status"
            },
            "antivirus": {
                "darwin": "ls /Applications | grep -i 'antivirus\\|security'",
                "linux": "which clamav"
            }
        }

        for tool, commands in security_tools.items():
            cmd = commands.get(self.system.lower())
            if cmd:
                result = self.run_command(cmd)
                if not result:
                    vulnerabilities.append({
                        "Name": f"Security Tool: {tool}",
                        "Issue": f"{tool} not found or not properly configured",
                        "Type": "security",
                        "Severity": "high"
                    })

        return vulnerabilities

    def scan(self) -> Dict:
        all_vulnerabilities = []
        
        # Check package manager vulnerabilities
        if self.system == "Darwin":
            all_vulnerabilities.extend(self.check_brew_vulnerabilities())
        else:
            all_vulnerabilities.extend(self.check_apt_vulnerabilities())
            all_vulnerabilities.extend(self.check_yum_vulnerabilities())

        # Check global package vulnerabilities
        all_vulnerabilities.extend(self.check_global_python_packages())
        all_vulnerabilities.extend(self.check_global_node_packages())
        
        # Check system security
        all_vulnerabilities.extend(self.check_system_security())

        return {
            "ID": str(uuid.uuid4()),
            "System": self.system,
            "Hostname": platform.node(),
            "ScanTime": datetime.utcnow().isoformat(),
            "Vulnerabilities": all_vulnerabilities
        }

def save_to_file(data: Dict):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"{log_dir}/system/{timestamp}.json.gz"
    
    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    print(f"Data saved to compressed file: {file_path}")

def main():
    scanner = SystemVulnerabilityScanner()
    result = scanner.scan()
    save_to_file(result)
    
    end_time = time.time()
    print(f"Scan completed in {end_time - scanner.start_time:.2f} seconds")
    print(f"Found {len(result['Vulnerabilities'])} potential vulnerabilities")

if __name__ == "__main__":
    main() 