import json
import os
import platform
import subprocess
import base64
import requests
import uuid

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

    if output:
        audit_data = json.loads(output)
        vulnerabilities = audit_data.get("vulnerabilities", {})
        return vulnerabilities
    else:
        return {}


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

        for _, vulnerability in vulnerabilities.items():
            advisory_info = {
                "Name": vulnerability["name"],
                "Severity": vulnerability["severity"],
                "Direct": vulnerability["isDirect"],
                "Via": vulnerability["via"],
                "Range": vulnerability["range"],
                "Nodes": vulnerability["nodes"],
                "Fix Available": vulnerability["fixAvailable"],
            }

            advisory_list.append(advisory_info)

        dependency_data = {
            "ID": str(uuid.uuid4()),
            "Path": path,
            "Vulnerabilities": advisory_list,
        }
        result_data.append(dependency_data)

    with open("node_vulnerabilities.json", "w") as f:
        json.dump(result_data, f, indent=4)
