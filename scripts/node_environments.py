import json
import os
import platform
import subprocess
import base64

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


def read_and_parse_paths_file():
    paths = get_node_module_paths()
    paths_with_ids = []

    for path in paths:
        id = base64.urlsafe_b64encode(os.urandom(6)).decode()
        dependencies = {}
        package_json_path = os.path.join(path, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path, "r") as f:
                package_json = json.load(f)
            if "dependencies" in package_json:
                dependencies.update(package_json["dependencies"])
            if "devDependencies" in package_json:
                dependencies.update(package_json["devDependencies"])
            for key in dependencies.keys():
                if dependencies[key].startswith('^'):
                    dependencies[key] = dependencies[key][1:]
            paths_with_ids.append({"id": id, "path": path, "dependencies": dependencies})

    return paths_with_ids

def write_parsed_paths_file(parsed_paths):
    with open("node_paths.json", "w") as f:
        json.dump(parsed_paths, f, indent=4)

def remove_empty_dependencies(json_file_path):
    with open(json_file_path, "r") as f:
        json_data = json.load(f)

    # filter out objects with empty "dependencies" attribute
    json_data = [obj for obj in json_data if obj.get("dependencies")]

    with open(json_file_path, "w") as f:
        json.dump(json_data, f)


if __name__ == "__main__":
    get_node_module_paths()
    parsed_paths = read_and_parse_paths_file()
    write_parsed_paths_file(parsed_paths)
    remove_empty_dependencies("node_paths.json")
