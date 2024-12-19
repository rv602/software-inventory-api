#!/bin/bash

# Define paths to scripts and JSON files
PYTHON_ENV_SCRIPT="/Users/abhinavpandey/Developer/software-inventory-api/scripts/python_environments.py"
NODE_ENV_SCRIPT="/Users/abhinavpandey/Developer/software-inventory-api/scripts/node_environments.py"
PYTHON_JSON_OUTPUT="/Users/abhinavpandey/Developer/software-inventory-api/python_vulnerabilities.json"
NODE_JSON_OUTPUT="/Users/abhinavpandey/Developer/software-inventory-api/node_vulnerabilities.json"

# Run the Python scripts to generate JSON output files
python3 "$PYTHON_ENV_SCRIPT"
if [ $? -ne 0 ]; then
  echo "Failed to run $PYTHON_ENV_SCRIPT"
  exit 1
fi

python3 "$NODE_ENV_SCRIPT"
if [ $? -ne 0 ]; then
  echo "Failed to run $NODE_ENV_SCRIPT"
  exit 1
fi

# Check if JSON files are generated
if [[ ! -f "$PYTHON_JSON_OUTPUT" || ! -f "$NODE_JSON_OUTPUT" ]]; then
  echo "JSON output files not found."
  exit 1
fi

# Combine JSON outputs using jq
combined_json=$(jq -n --slurpfile python "$PYTHON_JSON_OUTPUT" --slurpfile node "$NODE_JSON_OUTPUT" \
  '{python_environments: $python[0], node_environments: $node[0]}')

# Define MongoDB Atlas connection
MONGO_CONNECTION_STRING="mongodb+srv://meronaamabhinav:admin@cluster0.tk5f0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME="SystemData"
COLLECTION_NAME="Vulnerabilities"

# Store combined JSON in MongoDB 
echo $combined_json | python -c "import sys, json; from pymongo import MongoClient; client = MongoClient('$MONGO_CONNECTION_STRING'); db = client['$DATABASE_NAME']; collection = db['$COLLECTION_NAME']; collection.insert_one(json.load(sys.stdin))"

# Check if JSON is stored in MongoDB
if [ $? -ne 0 ]; then
  echo "Failed to store JSON in MongoDB"
  exit 1
fi
