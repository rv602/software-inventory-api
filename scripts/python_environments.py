import subprocess
import platform
import json
import base64
import uuid

def get_python_paths():
    system = platform.system()
    paths = []

    if system == "Darwin":  # Mac
        cmd = "mdfind -name activate | grep '/bin/activate$' | xargs dirname | xargs dirname | grep -v '/\\..*/' | grep '^/Users' | sort -u"
    elif system == "Linux":  # Linux
        cmd = "locate activate | egrep '/bin/activate$' | xargs -r egrep -l nondestructive 2>/dev/null | xargs -I {} dirname {} | xargs -I {} dirname {} | grep '/home'"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output_lines = result.stdout.splitlines()

    for line in output_lines:
        paths.append(line)

    return paths

def modify_json_data(json_data):
    modified_data = []

    for path in json_data:
        last_slash_index = path.rfind("/")
        env = path[last_slash_index + 1 :]
        modified_data.append({"ID": str(uuid.uuid4()), "Path": path[:last_slash_index], "Env": env})

    return modified_data

def update_json_with_dependencies(json_data):
    for obj in json_data:
        path = obj["Path"]
        env = obj["Env"]
        activate_command = f"source {path}/{env}/bin/activate && safety check --json"
        vulnerabilities = subprocess.run(
            ["bash", "-c", activate_command], capture_output=True, text=True
        )
        vulnerabilities_data = json.loads(vulnerabilities.stdout)
        vulnerabilities_list = vulnerabilities_data["vulnerabilities"]
        filtered_vulnerabilities = []
        for vul in vulnerabilities_list:
            object = {}
            object["Name"] = vul["package_name"]
            object["Vulnerability_id"] = vul["vulnerability_id"]
            object["CVE_id"] = vul["CVE"]
            object["More_info"] = vul["more_info_url"]
            object["Severity"] = vul["severity"]
            filtered_vulnerabilities.append(object)
        obj["Vulnerabilities"] = filtered_vulnerabilities

    return json_data

def write_json_to_file(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    python_paths = get_python_paths()
    python_data = modify_json_data(python_paths)
    updated_data = update_json_with_dependencies(python_data)
    write_json_to_file(updated_data, "python_vulnerabilities.json")
