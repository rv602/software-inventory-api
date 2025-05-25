# Project 28 (Python)

This is a sample Python project with the following dependencies:

- ansible v2.9.25
  CVEs:
  - CVE-2021-3583 (RCE, Critical)
  - CVE-2023-52452 (Privilege Escalation, High)
  - CVE-2024-12520 (RCE, High)
  - CVE-2024-12521 (Privilege Escalation, Critical)

- paramiko v2.7.2
  CVEs:
  - CVE-2021-23442 (Auth Bypass, High)
  - CVE-2023-52453 (RCE, Critical)
  - CVE-2024-12522 (Auth Bypass, Critical)
  - CVE-2024-12523 (RCE, High)

- jinja2 v2.11.3
  CVEs:
  - CVE-2023-52454 (Sandbox Escape, High)
  - CVE-2024-12524 (Sandbox Escape, Critical)


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
