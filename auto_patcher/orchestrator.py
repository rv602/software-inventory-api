import json
import os
import subprocess
from typing import List, Dict
from datetime import datetime
import shutil

BASE_PATH = "/Users/abhinavpandey/Developer/software-inventory-api/dataset/repositories"
REPORT_PATH = "/Users/abhinavpandey/Developer/software-inventory-api/auto_patcher/reports"

def backup_package_json(project_path: str):
    src = os.path.join(project_path, "package.json")
    backup = os.path.join(project_path, "package.json.bak")
    shutil.copy(src, backup)

def restore_package_json(project_path: str):
    backup = os.path.join(project_path, "package.json.bak")
    original = os.path.join(project_path, "package.json")
    if os.path.exists(backup):
        shutil.move(backup, original)

def update_package_json(project_path: str, dependencies: List[Dict]) -> List[Dict]:
    pkg_json_path = os.path.join(project_path, "package.json")
    with open(pkg_json_path, "r") as f:
        package_json = json.load(f)

    report = []

    for dep in dependencies:
        name = dep["name"]
        new_version = dep["version"]
        old_version = None
        status = "not found"

        if name in package_json.get("dependencies", {}):
            old_version = package_json["dependencies"][name]
            package_json["dependencies"][name] = new_version
            status = "updated"
        elif name in package_json.get("devDependencies", {}):
            old_version = package_json["devDependencies"][name]
            package_json["devDependencies"][name] = new_version
            status = "updated"

        report.append({
            "name": name,
            "old_version": old_version,
            "new_version": new_version,
            "status": status
        })

    with open(pkg_json_path, "w") as f:
        json.dump(package_json, f, indent=2)

    return report

def build_docker_image(project_name: str, project_path: str) -> (bool, str):
    sanitized_name = project_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
    tag = f"test-{sanitized_name}"
    try:
        output = subprocess.check_output(["docker", "build", "-t", tag, project_path], stderr=subprocess.STDOUT)
        return True, output.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()

def run_tests_in_container(tag: str) -> (bool, str):
    try:
        result = subprocess.check_output(["docker", "run", "--rm", tag], stderr=subprocess.STDOUT)
        return True, result.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()

def commit_changes(project_path: str, dependencies: List[Dict]):
    try:
        subprocess.run(["git", "-C", project_path, "add", "package.json"], check=True)
        msg = f"Upgrade dependencies: {', '.join([d['name'] for d in dependencies])}"
        subprocess.run(["git", "-C", project_path, "commit", "-m", msg], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def save_report(project_name: str, report_data: Dict):
    project_dir = os.path.join(REPORT_PATH, project_name.replace(" ", "_"))
    os.makedirs(project_dir, exist_ok=True)
    report_file = os.path.join(project_dir, "report.json")
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)

def test_project(project: Dict):
    project_name = project["project_name"]
    project_path = os.path.join(BASE_PATH, project_name)

    print(f"🔧 Processing: {project_name}")
    backup_package_json(project_path)
    dep_report = update_package_json(project_path, project["dependencies"])

    sanitized_name = project_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
    tag = f"test-{sanitized_name}"
    build_success, build_logs = build_docker_image(project_name, project_path)
    run_success = False
    run_logs = ""

    if build_success:
        run_success, run_logs = run_tests_in_container(tag)

    if not (build_success and run_success):
        print(f"❌ Build or test failed. Reverting package.json for {project_name}")
        restore_package_json(project_path)

    if build_success and run_success:
        commit_changes(project_path, project["dependencies"])

    report = {
        "project": project_name,
        "timestamp": datetime.now().isoformat(),
        "build_status": "success" if build_success else "failed",
        "test_status": "passed" if run_success else "failed",
        "dependencies": dep_report,
        "build_logs": build_logs,
        "test_logs": run_logs
    }

    save_report(project_name, report)
    print(f"📄 Report saved to: {os.path.join(REPORT_PATH, project_name.replace(' ', '_'), 'report.json')}")

