import json
import os
import platform
import subprocess
import base64
import requests

def get_node_module_paths():
    system = platform.system()
    paths = []

    if system == "Darwin":
        cmd = "mdfind -name node_modules | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"
    elif system == "Linux":
        cmd = "locate -r '/node_modules$' | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output_lines = result.stdout.splitlines()
    
    for line in output_lines:
        if system == "Darwin" and line.startswith("/Users"):
            paths.append(line)
        elif system == "Linux" and line.startswith("/home"):
            paths.append(line)

    return paths


def get_vulnerable_dependencies(path):
    cmd = f"npm --prefix {path} audit --json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    
    #print(f"Running on {path}")
    if output:
        audit_data = json.loads(output)
        vulnerabilities = audit_data.get("advisories", {})
        return vulnerabilities
    else:
        return {}


def get_cve_details(cve_id):
    api_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    response = requests.get(api_url)
    response_data = response.json()
    vulnerabilities = response_data.get("vulnerabilities", [])

    for vulnerability in vulnerabilities:
        cve = vulnerability.get("cve", {})
        cve_id = cve.get("id")
        description = cve.get("descriptions", [{}])[0].get("value")
        cvss_metrics = vulnerability.get("metrics", {}).get("cvssMetricV31", [])

        print("CVE ID:", cve_id)
        print("Description:", description)
        print("CVSS Metrics:")
        for metric in cvss_metrics:
            vector_string = metric.get("cvssData", {}).get("vectorString")
            base_score = metric.get("cvssData", {}).get("baseScore")
            base_severity = metric.get("cvssData", {}).get("baseSeverity")
            print("  Vector String:", vector_string)
            print("  Base Score:", base_score)
            print("  Base Severity:", base_severity)
            print("------------------------------")


def get_vulnerable_dependencies_for_paths(paths):
    vulnerable_dependencies = []

    for path in paths:
        vulnerabilities = get_vulnerable_dependencies(path)
        if vulnerabilities:
            vulnerable_dependencies.append({"path": path, "vulnerabilities": vulnerabilities})

    return vulnerable_dependencies


if __name__ == "__main__":
    node_module_paths = get_node_module_paths()
    vulnerable_dependencies = get_vulnerable_dependencies_for_paths(node_module_paths)
    
    result_data = []
    
    for dependency in vulnerable_dependencies:
        path = dependency["path"]
        vulnerabilities = dependency["vulnerabilities"]
        advisory_list = []
        
        for advisory_id, advisory in vulnerabilities.items():
            advisory_info = {
                "Advisory ID": advisory_id,
                "Title": advisory.get("title"),
                "Name": advisory.get("module_name"),
                "Version": advisory.get("findings", {})[0].get("version"),
                "Severity": advisory.get("severity"),
                "Description": advisory.get("overview"),
                "CVE IDs": advisory.get("cves", []),
            }
            #for cve_id in advisory.get("cves", []):
            #  print("  ", cve_id)
            #  get_cve_details(cve_id)
            advisory_list.append(advisory_info)
        
        dependency_data = {
            "Path": path,
            "Vulnerabilities": advisory_list,
        }
        result_data.append(dependency_data)
    
    with open("vulnerabilities.json", "w") as f:
        json.dump(result_data, f, indent=4)
        
    print("Data saved to vulnerabilities.json file.")
