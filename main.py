from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import subprocess
import json

app = FastAPI()
load_dotenv()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/python-environments")
def python_environments():
    try:
        subprocess.run(["python", "scripts/python_environments.py"], check=True)

        with open("python_vulnerabilities.json", "r") as f:
            python_paths = json.load(f)

        return python_paths
    except subprocess.CalledProcessError:
        return {"message": "Script execution failed."}


@app.get("/node-environments")
def node_environments():
    try:
        subprocess.run(["python", "scripts/node_environments.py"], check=True)

        with open("node_vulnerabilities.json", "r") as f:
            node_paths = json.load(f)

        return node_paths
    except subprocess.CalledProcessError:
        return {"message": "Script execution failed."}


# @app.get("/vulnerabilities")
# async def get_vulnerabilities(name: str, version: str):
#     try:
#         url = f"https://services.nvd.nist.gov/rest/json/cves/1.0?cpeMatchString=cpe%3A2.3%3Aa%3A%3A{name}%3A{version}&resultsPerPage=10"
#         headers = {
#             "Content-Type": "application/json",
#             "apiKey": os.getenv("API_KEY")
#         }

#         response = requests.get(url, headers=headers)
#         response.raise_for_status()

#         data = response.json()
#         if data["totalResults"] > 0:
#             return data

#     except requests.exceptions.RequestException as e:
#         print(f"Request exception: {e}")

#     return {"message": "No vulnerabilities found."}
