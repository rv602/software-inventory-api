# software-inventory-api

This is the backend of the software inventory system. It is built using FastAPI, designed to scan and analyze third-party dependencies in software projects for vulnerabilities. The system supports multiple programming languages, including Python and JavaScript, with ongoing efforts to expand support for Go and other frameworks.

Software Inventory --> <a href="https://github.com/rv602/software-inventory">Repository</a>

The backend performs automated scans of project directories, leveraging tools like npm audit for JavaScript and Ochrona for Python. It identifies vulnerabilities, categorizes them by CVE ID, and provides detailed descriptions, reference links, and recommended fixes. All vulnerability data is stored in a centralized MongoDB database, allowing system administrators to monitor and address issues effectively.

In phase two, the backend integrates a scalable master-slave architecture for server-level deployments. Slave VMs perform periodic scans, and the data is synchronized with the master server, ensuring a unified view for administrators. The system also features robust authentication mechanisms, enabling secure access and maintaining data integrity.

This backend forms the core of the inventory system, empowering users to proactively manage software vulnerabilities while remaining platform-agnostic and scalable.

## Implementation

1. JavaScript Projects Detection

    Node.js projects are identified by scanning directories for the presence of a package.json file, which is the primary configuration file for Node.js applications and includes critical information about the project’s dependencies. The detection script performs a structured directory search, where it validates each package.json file by ensuring the absence of a node_modules directory in any parent directory. This validation step distinguishes primary Node.js projects from nested dependencies within node_modules directories, which may contain packages not directly related to the main project.

    <img width="549" alt="image" src="https://github.com/user-attachments/assets/8c1730b1-6377-45fe-822e-4edf5fca2b4f">

    Once a primary Node.js project is confirmed, it is added to a project list that will undergo further processing. For each valid project, the system parses the package.json file to retrieve a list of dependencies along with their versions, which are then cross-checked for known vulnerabilities using npm audit. This tool provides detailed reports of vulnerabilities, including severity levels and recommended updates, which are recorded for later analysis and remediation.

2. Python Projects Detection

    Finding virtual environments and looking for requirements.txt files in project directories are the two methods used to identify Python projects. This is Because the virtual environment functions as a separate Python environment and global libraries can't interfere with the identification of project-specific dependencies. To verify that a directory is a Python project, the detection script looks for the activate.sh file, which is frequently found in Python virtual environments.

    <img width="563" alt="image" src="https://github.com/user-attachments/assets/b7ea2fc4-d678-4f68-9cd0-6198cc4bafe3">


    If there isn't a requirements.txt file, the system creates one by running the command pip freeze > requirements.txt and turning on the virtual environment. This script creates a record that is necessary for vulnerability research by capturing an exhaustive list of installed dependencies together with their particular versions. An organized list of dependencies is then created by parsing the requirements.txt file, whether it is generated or already exists.

## Installation Guide

1. Create a virtual environment and activate it

```
python3 -m venv venv
source venv/bin/activate
```

2. Install the requirements

```
pip install -r requirements.txt
```

3. Create .env file
```
touch .env
```
4. Add environment vairables (Get the key from [NVD_Key](https://nvd.nist.gov/developers/request-an-api-key) or Contact for the key)
```
API_KEY=...
```

5. Run the application

```
uvicorn main:app --reload
```

