# Project 16 (Python)

This is a sample Python project with the following dependencies:

- Django v3.2.9
  CVEs:
  - CVE-2022-34265 (SQL Injection, High)
  - CVE-2021-33203 (XSS, Medium)
  - CVE-2020-7471 (SQL Injection, High)
  - CVE-2023-31047 (CSRF, Medium)
  - CVE-2024-12455 (SQL Injection, Critical)
  - CVE-2024-12456 (XSS, High)
  - CVE-2024-12457 (SQL Injection, High)
  - CVE-2024-12458 (CSRF, High)

- djangorestframework v3.12.4
  CVEs:
  - CVE-2021-35042 (XSS, Medium)
  - CVE-2023-43665 (DoS, High)
  - CVE-2024-12459 (XSS, High)
  - CVE-2024-12460 (DoS, Critical)

- psycopg2 v2.9.0
  CVEs:
  - CVE-2021-22840 (SQL Injection, High)
  - CVE-2022-21797 (Memory Leak, Medium)
  - CVE-2024-12461 (SQL Injection, Critical)
  - CVE-2024-12462 (Memory Leak, High)


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
