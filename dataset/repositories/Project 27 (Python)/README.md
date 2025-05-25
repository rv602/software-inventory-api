# Project 27 (Python)

This is a sample Python project with the following dependencies:

- pytest v6.2.5
  CVEs:
  - CVE-2021-23441 (Arbitrary Code Exec, High)
  - CVE-2023-52449 (DoS, Medium)
  - CVE-2024-12515 (Arbitrary Code Exec, Critical)
  - CVE-2024-12516 (DoS, High)

- coverage v5.5
  CVEs:
  - CVE-2021-35045 (Code Injection, Medium)
  - CVE-2023-52450 (RCE, Critical)
  - CVE-2024-12517 (Code Injection, High)
  - CVE-2024-12518 (RCE, High)

- pytest-cov v2.12.0
  CVEs:
  - CVE-2023-52451 (XSS, Medium)
  - CVE-2024-12519 (XSS, High)


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
