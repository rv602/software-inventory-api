import json
import os
import platform
import subprocess
import time
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def test_mongodb_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=5000)
        client.server_info()
        client.close()
        print("MongoDB connection successful")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

# def get_node_module_paths():
#     system = platform.system()
#     paths = []

#     if system == "Darwin":
#         cmd = "mdfind -name node_modules | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"
#     elif system == "Linux":
#         cmd = "locate -r '/node_modules$' | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"

# def get_node_module_paths():
#     system = platform.system()
#     paths = []

#     if system == "Darwin":
#         cmd = r"mdfind -name node_modules | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*\/'"
#     elif system == "Linux":
#         cmd = r"locate -r '/node_modules$' | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*\/'"

#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     output_lines = result.stdout.splitlines()

#     for line in output_lines:
#         if system == "Darwin" and line.startswith("/Users"):
#             paths.append(line)
#         elif system == "Linux" and line.startswith("/home"):
#             paths.append(line)

#     return paths

# def get_node_module_paths():
#     system = platform.system()
#     paths = []

#     if system == "Darwin":
#         cmd = r"mdfind -name node_modules | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"
#     elif system == "Linux":
#         cmd = r"locate -r '/node_modules$' | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"

#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     output_lines = result.stdout.splitlines()

#     return [line for line in output_lines if (system == "Darwin" and line.startswith("/Users")) or 
#             (system == "Linux" and line.startswith("/home"))]

def get_node_module_paths():
    system = platform.system()
    paths = []

    if system == "Darwin":
        cmd = r"mdfind -name node_modules | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"
    elif system == "Linux":
        cmd = r"locate -r '/node_modules$' | xargs dirname | grep -v '/node_modules$' | grep -v '/node_modules/' | grep -v '/\..*/'"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output_lines = result.stdout.splitlines()

    # Adjust paths for mounted host filesystem
    return [f"/host_root{line}" for line in output_lines if (system == "Darwin" and line.startswith("/Users")) or 
            (system == "Linux" and line.startswith("/home"))]



# def get_vulnerable_dependencies(path):
#     cmd = f"npm --prefix {path} audit --json"
#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     output = result.stdout.strip()

#     if output:
#         audit_data = json.loads(output)
#         vulnerabilities = audit_data.get("vulnerabilities", {})
#         return vulnerabilities
#     else:
#         return {}

def get_vulnerable_dependencies(path):
    cmd = f"npm --prefix {path} audit --json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()

    if output:
        audit_data = json.loads(output)
        vulnerabilities = audit_data.get("vulnerabilities", {})
        print(f"Found vulnerabilities for {path}: {vulnerabilities}")  # Debug line
        return vulnerabilities
    else:
        return {}



def get_vulnerable_dependencies_for_paths(paths):
    vulnerable_dependencies = []

    for path in paths:
        vulnerabilities = get_vulnerable_dependencies(path)
        if vulnerabilities:
            vulnerable_dependencies.append({"path": path, "vulnerabilities": vulnerabilities})
            print(f"Found vulnerabilities for {path}: {vulnerabilities}")  # Debug line
        else:
            print(f"No vulnerabilities found for {path}")  # Debug line

    print(f"Found {len(vulnerable_dependencies)} vulnerable Node.js environments")
    return vulnerable_dependencies


def send_to_mongodb(data):
    print("data", data)
    try:
        # If data is empty, skip MongoDB insertion
        if not data:
            print("No vulnerability data to send to MongoDB")
            return

        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('MONGODB_DB')]
        collection = db['vulnerabilities_node']
        
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
        backup_file = "scripts/node_vulnerabilities.json"
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to backup file: {backup_file}")

if __name__ == "__main__":
    start_time = time.time()
    
    if not test_mongodb_connection():
        print("Aborting script due to MongoDB connection failure")
        sys.exit(1)
    
    node_module_paths = get_node_module_paths()
    print(f"Found {len(node_module_paths)} Node.js environments")
    
    vulnerable_dependencies = get_vulnerable_dependencies_for_paths(node_module_paths)
    
    # Save backup
    with open("scripts/node_vulnerabilities.json", "w") as f:
        json.dump(vulnerable_dependencies, f, indent=4)
    
    send_to_mongodb(vulnerable_dependencies)
    
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")