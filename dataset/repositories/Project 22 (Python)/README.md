# Project 22 (Python)

This is a sample Python project with the following dependencies:

- celery v5.1.2
  CVEs:
  - CVE-2022-29234 (DoS, Medium)
  - CVE-2023-52433 (RCE, Critical)
  - CVE-2024-12489 (DoS, High)
  - CVE-2024-12490 (RCE, High)

- redis v3.5.3
  CVEs:
  - CVE-2021-32762 (RCE, Critical)
  - CVE-2023-52434 (Auth Bypass, High)
  - CVE-2024-12491 (RCE, High)
  - CVE-2024-12492 (Auth Bypass, Critical)

- kombu v5.2.0
  CVEs:
  - CVE-2023-52435 (DoS, Medium)
  - CVE-2024-12493 (DoS, High)


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
