from datetime import datetime, timezone
import json
import os
import platform
import subprocess
import uuid
import time
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import gzip
import socket
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from schema.schema import ProjectData, SystemInfo, JavaScriptVulnerability
from constants import log_dir
from constants import db_url_prod, db_url_dev, db_name, collection_js_name

load_dotenv()


def get_system_info() -> SystemInfo:
    """Get system info from environment variables"""
    return {
        "hostname": os.getenv('SYSTEM_HOSTNAME'),
        "system_type": os.getenv('SYSTEM_TYPE'),
        "mac_address": os.getenv('SYSTEM_MAC'),
        "ip_address": os.getenv('SYSTEM_IP')
    }


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


def default_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")


def get_node_module_paths():
    system = platform.system()
    paths = []

    if system == "Darwin":
        cmd = r"mdfind -name node_modules | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"
    elif system == "Linux":
        cmd = r"locate -r '/node_modules$' | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"

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
            vulnerable_dependencies.append(
                {"path": path, "vulnerabilities": vulnerabilities}
            )

    return vulnerable_dependencies


def add_timestamps(data):
    current_time = datetime.utcnow()
    for item in data:
        item["createdAt"] = current_time
        item["updatedAt"] = current_time
    return data


def send_to_mongodb(data):
    try:
        if not data:
            print("No vulnerability data to send to MongoDB")
            return

        client = MongoClient(db_url_prod)
        db = client[db_name]
        collection = db[collection_js_name]

        if isinstance(data, dict):
            data = [data]

        current_time = datetime.now(timezone.utc)

        print(f"Processing {len(data)} documents for MongoDB")

        for doc in data:
            path = doc["Path"]
            vulnerabilities = doc["Vulnerabilities"]

            # Check if a document with the same Path and device exists
            existing_doc = collection.find_one({
                "Path": path,
                "SystemInfo.mac_address": doc["SystemInfo"]["mac_address"]
            })

            if existing_doc:
                # If vulnerabilities differ, update them; otherwise, just update the timestamp
                if existing_doc.get("Vulnerabilities") != vulnerabilities:
                    collection.update_one(
                        {"Path": path, "SystemInfo.mac_address": doc["SystemInfo"]["mac_address"]},
                        {
                            "$set": {
                                "Vulnerabilities": vulnerabilities,
                                "updatedAt": current_time,
                                "SystemInfo": doc["SystemInfo"],
                                "Score": doc["Score"]
                            }
                        },
                    )
                    print(f"Updated vulnerabilities for Path: {path}")
                else:
                    collection.update_one(
                        {"Path": path, "SystemInfo.mac_address": doc["SystemInfo"]["mac_address"]},
                        {"$set": {
                            "updatedAt": current_time,
                            "SystemInfo": doc["SystemInfo"]
                        }},
                    )
                    print(f"Updated only the timestamp for Path: {path}")
            else:
                collection.insert_one(doc)
                print(f"Inserted new document for Path: {path}")

        client.close()

    except Exception as e:
        print(f"Error sending data to MongoDB: {e}")
        backup_file = "scripts/node_vulnerabilities.json"
        with open(backup_file, "w") as f:
            json.dump(data, f, default=default_serializer, indent=4)
        print(f"Data saved to backup file: {backup_file}")


if __name__ == "__main__":

    if not test_mongodb_connection():
        print("Exiting script, MongoDB connection failed")
        exit()

    start_time = time.time()
    system_info = get_system_info()

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
                "Fix_Available": vulnerability["fixAvailable"],
            }

            advisory_list.append(advisory_info)

        dependency_data = {
            "ID": str(uuid.uuid4()),
            "Path": path,
            "ProjectType": "javascript",
            "SystemInfo": system_info,
            "Score": None,
            "Vulnerabilities": advisory_list,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        result_data.append(dependency_data)

    current_log_dir = "js"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"{log_dir}/{current_log_dir}/{timestamp}.json.gz"

    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, default=default_serializer)

    print(f"Data saved to compressed file: {file_path}")
    send_to_mongodb(result_data)

    json_file_path = "node_vulnerabilities.json"
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, default=default_serializer)

    end = time.time()
    print(f"Execution time: {end - start_time} seconds")
