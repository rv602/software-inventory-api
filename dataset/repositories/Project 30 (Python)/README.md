# Project 30 (Python)

This is a sample Python project with the following dependencies:

- sanic v20.12.3
  CVEs:
  - CVE-2021-35046 (DoS, Medium)
  - CVE-2023-52458 (RCE, Critical)
  - CVE-2024-12530 (DoS, High)
  - CVE-2024-12531 (RCE, High)

- aiohttp v3.7.4
  CVEs:
  - CVE-2021-23444 (SSRF, High)
  - CVE-2023-52459 (Memory Leak, Medium)
  - CVE-2024-12532 (SSRF, Critical)
  - CVE-2024-12533 (Memory Leak, High)

- uvloop v0.16.0
  CVEs:
  - CVE-2023-52460 (DoS, High)
  - CVE-2024-12534 (DoS, Critical)


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
