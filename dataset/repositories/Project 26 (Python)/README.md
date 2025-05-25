# Project 26 (Python)

This is a sample Python project with the following dependencies:

- tensorflow v2.5.0
  CVEs:
  - CVE-2022-29216 (RCE, Critical)
  - CVE-2023-52446 (Memory Corruption, High)
  - CVE-2024-12510 (RCE, High)
  - CVE-2024-12511 (Memory Corruption, Critical)

- keras v2.6.0
  CVEs:
  - CVE-2021-35044 (DoS, Medium)
  - CVE-2023-52447 (RCE, Critical)
  - CVE-2024-12512 (DoS, High)
  - CVE-2024-12513 (RCE, High)

- protobuf v3.17.3
  CVEs:
  - CVE-2023-52448 (Arbitrary Code Exec, High)
  - CVE-2024-12514 (Arbitrary Code Exec, Critical)


## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the project:
```bash
python src/main.py
```
