#!/bin/bash

echo "Running python_environments.py..."
python scripts/python_environments.py

echo "Running node_environments.py..."
python scripts/node_environments.py

echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000
