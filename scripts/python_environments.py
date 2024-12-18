import subprocess
import platform
import json
import uuid
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import time

load_dotenv()

def test_mongodb_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=5000)
        client.server_info()  # will throw an exception if connection fails
        db = client[os.getenv('MONGODB_DB')]
        collection = db['python_vulnerabilities']
        print("MongoDB connection successful")
        client.close()
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

cve_score_mapping = {
    "low": (0.1, 3.9),
    "moderate": (4.0, 6.9),
    "high": (7.0, 8.9),
    "critical": (9.0, 10.0)
}

# def get_python_paths():
#     system = platform.system()
#     paths = []

#     if system == "Darwin":  # Mac
#         cmd = r"mdfind -name activate | grep '/bin/activate$' | xargs dirname | xargs dirname | grep -v '/\..*/' | grep '^/Users' | sort -u"
#     elif system == "Linux":
#         cmd = r"locate activate | egrep '/bin/activate$' | egrep -v '/\..*/' | xargs -r egrep -l nondestructive 2>/dev/null | xargs -I {} dirname {} | xargs -I {} dirname {} | grep '/home'"

#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     output_lines = result.stdout.splitlines()

#     return [line for line in output_lines]

def get_python_paths():
    system = platform.system()
    paths = []

    if system == "Darwin":  # Mac
        cmd = r"mdfind -name activate | grep '/bin/activate$' | xargs dirname | xargs dirname | grep -v '/\..*/' | grep '^/Users' | sort -u"
    elif system == "Linux":
        cmd = r"locate activate | egrep '/bin/activate$' | egrep -v '/\..*/' | xargs -r egrep -l nondestructive 2>/dev/null | xargs -I {} dirname {} | xargs -I {} dirname {} | grep '/home'"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output_lines = result.stdout.splitlines()

    # Adjust paths for mounted host filesystem
    print(output_lines)
    return [f"/host_root{line}" for line in output_lines]


def modify_json_data(json_data):
    modified_data = []

    for path in json_data:
        last_slash_index = path.rfind("/")
        env = path[last_slash_index + 1 :]
        modified_data.append({"ID": str(uuid.uuid4()), "Path": path[:last_slash_index], "Env": env})

    return modified_data

# def update_json_with_dependencies(json_data):
#     for obj in json_data:
#         path = obj["Path"]
#         env = obj["Env"]
#         if not os.path.exists(f"{path}/requirements.txt"):
#             cmd = f"source {path}/{env}/bin/activate && pip freeze > {path}/requirements.txt && deactivate"
#             subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
#         activate_command = f"cd {path} && ochrona --exit --report_type JSON --file requirements.txt"
#         result = subprocess.run(activate_command,shell=True, capture_output=True, text=True)
#         output_lines = result.stdout.splitlines()

#         if "File: requirements.txt" in output_lines:
#             json_output = output_lines[output_lines.index("File: requirements.txt")+1:]
#             json_output = json.loads("".join(json_output))
#             result_for_json = json_output["findings"]
#             if len(result_for_json) == 0:
#                 obj["Removing"] = True
#             else:
#                 filtered_json = []
#                 for finding in result_for_json:
#                     temp_obj = {}
#                     temp_obj["Name"] = finding["name"]
#                     temp_obj["Version"] = finding["found_version"].split(finding["name"]+"==")[1]
#                     temp_obj["CVE_id"] = finding["cve_id"]
#                     temp_obj["Description"] = finding["description"]
#                     for severity, (min_score, max_score) in cve_score_mapping.items():
#                         if min_score <= finding["ochrona_severity_score"] <= max_score:
#                             temp_obj["Severity"] = severity
#                             break 
#                     temp_obj["References"] = finding["references"]
#                     filtered_json.append(temp_obj)
#                 obj["Vulnerabilities"] = filtered_json
#         else:
#             obj["Removing"] = True

#     json_data_to_return = []
#     for obj in json_data:
#         if "Removing" not in obj:
#             json_data_to_return.append(obj)
#     return json_data_to_return

def update_json_with_dependencies(json_data):
    for obj in json_data:
        path = obj["Path"]
        env = obj["Env"]
        if not os.path.exists(f"{path}/requirements.txt"):
            cmd = f"source {path}/{env}/bin/activate && pip freeze > {path}/requirements.txt && deactivate"
            subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        activate_command = f"cd {path} && ochrona --exit --report_type JSON --file requirements.txt"
        result = subprocess.run(activate_command, shell=True, capture_output=True, text=True)
        output_lines = result.stdout.splitlines()

        if "File: requirements.txt" in output_lines:
            json_output = output_lines[output_lines.index("File: requirements.txt") + 1:]
            json_output = json.loads("".join(json_output))
            result_for_json = json_output["findings"]
            if len(result_for_json) == 0:
                obj["Removing"] = True
            else:
                filtered_json = []
                for finding in result_for_json:
                    temp_obj = {}
                    temp_obj["Name"] = finding["name"]
                    temp_obj["Version"] = finding["found_version"].split(finding["name"] + "==")[1]
                    temp_obj["CVE_id"] = finding["cve_id"]
                    temp_obj["Description"] = finding["description"]
                    for severity, (min_score, max_score) in cve_score_mapping.items():
                        if min_score <= finding["ochrona_severity_score"] <= max_score:
                            temp_obj["Severity"] = severity
                            break
                    temp_obj["References"] = finding["references"]
                    filtered_json.append(temp_obj)
                obj["Vulnerabilities"] = filtered_json
        else:
            obj["Removing"] = True

    json_data_to_return = []
    for obj in json_data:
        if "Removing" not in obj:
            json_data_to_return.append(obj)
    return json_data_to_return


def write_json_to_file(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def send_to_mongodb(data):
    try:
        # If data is empty, skip MongoDB insertion
        if not data:
            print("No vulnerability data to send to MongoDB")
            return

        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('MONGODB_DB')]
        collection = db['vulnerabilities_python']
        
        # Ensure data is a list of documents
        if isinstance(data, dict):
            data = [data]
            
        # Convert ObjectId to string if present
        for doc in data:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
                
        collection.insert_many(data)
        print("Data successfully sent to MongoDB")
        client.close()
        
    except Exception as e:
        print(f"Error sending data to MongoDB: {e}")
        backup_file = "scripts/python_vulnerabilities.json"
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to backup file: {backup_file}")

if __name__ == "__main__":

    start_time = time.time()

    if not test_mongodb_connection():
        print("Exiting script.")
        sys.exit(1)
    python_paths = get_python_paths()
    python_data = modify_json_data(python_paths)
    updated_data = update_json_with_dependencies(python_data)
    write_json_to_file(updated_data, "python_vulnerabilities.json")

    send_to_mongodb(updated_data)

    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
