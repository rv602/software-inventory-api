import subprocess
import platform
import json
import uuid
import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import gzip
from datetime import datetime, timezone

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constants import log_dir
from constants import db_url_prod, db_url_dev, db_name, collection_py_name

load_dotenv()

def default_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")

datetime.now(timezone.utc)


def test_mongodb_connection():
    try:
        client = MongoClient(db_url_prod)
        client.server_info()
        client.close()
        print("MongoDB connection successful")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False


def send_to_mongodb(data):
    try:
        client = MongoClient(db_url_prod)
        db = client[db_name]
        collection = db[collection_py_name]

        for entry in data:
            # Add createdAt and updatedAt timestamps
            # entry["createdAt"] = entry.get("createdAt", datetime.utcnow())
            # entry["updatedAt"] = datetime.utcnow()
            entry["createdAt"] = entry.get("createdAt", datetime.now(timezone.utc))
            entry["updatedAt"] = datetime.now(timezone.utc)

            # Check if entry exists
            existing = collection.find_one({"Path": entry["Path"]})

            if existing:
                # Compare vulnerabilities excluding createdAt and updatedAt
                old_entry = {
                    k: v
                    for k, v in existing.items()
                    if k not in ["createdAt", "updatedAt"]
                }
                new_entry = {
                    k: v
                    for k, v in entry.items()
                    if k not in ["createdAt", "updatedAt"]
                }

                if old_entry == new_entry:
                    # Update only updatedAt if data hasn't changed
                    collection.update_one(
                        {"Path": entry["Path"]},
                        {"$set": {"updatedAt": entry["updatedAt"]}},
                    )
                else:
                    # Replace document if data has changed
                    collection.replace_one({"Path": entry["Path"]}, entry)
            else:
                # Insert new document with createdAt and updatedAt
                collection.insert_one(entry)

        print("Data successfully processed in MongoDB")
        client.close()

    except Exception as e:
        print(f"Error sending data to MongoDB: {e}")
        backup_file = "python_vulnerabilities.json"
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to backup file: {backup_file}")


cve_score_mapping = {
    "low": (0.1, 3.9),
    "moderate": (4.0, 6.9),
    "high": (7.0, 8.9),
    "critical": (9.0, 10.0),
}


def get_python_paths():
    system = platform.system()
    paths = []

    if system == "Darwin":  # Mac
        cmd = r"mdfind -name activate | grep '/bin/activate$' | xargs dirname | xargs dirname | grep -v '/\\..*/' | grep '^/Users' | sort -u"
    elif system == "Linux":  # Linux
        cmd = r"locate activate | egrep '/bin/activate$' | egrep -v '/\..+/' | xargs -r egrep -l nondestructive 2>/dev/null | xargs -I {} dirname {} | xargs -I {} dirname {} | grep '/home'"

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
        modified_data.append(
            {"ID": str(uuid.uuid4()), "Path": path[:last_slash_index], "Env": env}
        )

    return modified_data


def update_json_with_dependencies(json_data):
    for obj in json_data:
        path = obj["Path"]
        env = obj["Env"]
        if not os.path.exists(f"{path}/requirements.txt"):
            cmd = f"source {path}/{env}/bin/activate && pip freeze > {path}/requirements.txt && deactivate"
            subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        activate_command = (
            f"cd {path} && ochrona --exit --report_type JSON --file requirements.txt"
        )
        result = subprocess.run(
            activate_command, shell=True, capture_output=True, text=True
        )
        output_lines = result.stdout.splitlines()

        if "File: requirements.txt" in output_lines:
            json_output = output_lines[
                output_lines.index("File: requirements.txt") + 1 :
            ]
            json_output = json.loads("".join(json_output))
            result_for_json = json_output["findings"]
            if len(result_for_json) == 0:
                obj["Removing"] = True
            else:
                filtered_json = []
                for finding in result_for_json:
                    temp_obj = {}
                    temp_obj["Name"] = finding["name"]
                    temp_obj["Version"] = finding["found_version"].split(
                        finding["name"] + "=="
                    )[1]
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
    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    start_time = time.time()

    if not test_mongodb_connection():
        print("Aborting script due to MongoDB connection failure")
        sys.exit(1)

    python_paths = get_python_paths()
    print(f"Found {len(python_paths)} Python environments")

    python_data = modify_json_data(python_paths)
    updated_data = update_json_with_dependencies(python_data)

    # Create a structured filename with timestamp
    current_log_dir = "py"
    os.makedirs(log_dir, exist_ok=True)  # Ensure the logs directory exists
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"{log_dir}/{current_log_dir}/{timestamp}.json.gz"

    # Save backup with structured filename
    write_json_to_file(updated_data, file_path)
    print(f"Backup saved to: {file_path}")

    # Send to MongoDB
    send_to_mongodb(updated_data)

    json_file_path = "python_vulnerabilities.json"
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, default=default_serializer, indent=4)
    print(f"Data saved to file: {json_file_path}")

    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
