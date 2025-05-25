# Project 29 (Python)

This is a sample Python project with the following dependencies:

- apache-airflow v2.1.4
  CVEs:
  - CVE-2021-40899 (RCE, Critical)
  - CVE-2023-52455 (Auth Bypass, High)
  - CVE-2024-12525 (RCE, High)
  - CVE-2024-12526 (Auth Bypass, Critical)

- pyarrow v3.0.0
  CVEs:
  - CVE-2021-23443 (Memory Corruption, High)
  - CVE-2023-52456 (DoS, Medium)
  - CVE-2024-12527 (Memory Corruption, Critical)
  - CVE-2024-12528 (DoS, High)

- pandas v1.3.0
  CVEs:
  - CVE-2023-52457 (SQL Injection, High)
  - CVE-2024-12529 (SQL Injection, Critical)


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
