# Project 19 (Python)

This is a sample Python project with the following dependencies:

- fastapi v0.68.1
  CVEs:
  - CVE-2022-24761 (Open Redirect, High)
  - CVE-2023-52428 (SSRF, Critical)
  - CVE-2024-12474 (Open Redirect, Critical)
  - CVE-2024-12475 (SSRF, High)

- uvicorn v0.15.0
  CVEs:
  - CVE-2021-41184 (DoS, Medium)
  - CVE-2023-52429 (RCE, Critical)
  - CVE-2024-12476 (DoS, High)
  - CVE-2024-12477 (RCE, High)

- pydantic v1.9.0
  CVEs:
  - CVE-2023-52430 (Arbitrary Code Exec, High)
  - CVE-2024-12478 (Arbitrary Code Exec, Critical)


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
