# Project 24 (Python)

This is a sample Python project with the following dependencies:

- requests v2.26.0
  CVEs:
  - CVE-2021-33503 (SSRF, Critical)
  - CVE-2023-52440 (Auth Bypass, High)
  - CVE-2024-12500 (SSRF, High)
  - CVE-2024-12501 (Auth Bypass, Critical)

- selenium v3.141.0
  CVEs:
  - CVE-2021-35043 (Arbitrary Code Exec, High)
  - CVE-2023-52441 (XSS, Medium)
  - CVE-2024-12502 (Arbitrary Code Exec, Critical)
  - CVE-2024-12503 (XSS, High)

- urllib3 v1.26.5
  CVEs:
  - CVE-2023-52442 (DoS, High)
  - CVE-2024-12504 (DoS, Critical)


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
