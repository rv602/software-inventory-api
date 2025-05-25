# Project 21 (Python)

This is a sample Python project with the following dependencies:

- opencv-python v4.5.3.56
  CVEs:
  - CVE-2022-21999 (Buffer Overflow, High)
  - CVE-2023-52431 (RCE, Critical)
  - CVE-2024-12484 (Buffer Overflow, Critical)
  - CVE-2024-12485 (RCE, High)

- scikit-learn v0.24.2
  CVEs:
  - CVE-2021-33431 (Arbitrary Code Exec, Critical)
  - CVE-2023-52432 (DoS, Medium)
  - CVE-2024-12486 (Arbitrary Code Exec, High)
  - CVE-2024-12487 (DoS, High)

- tensorflow v2.5.0
  CVEs:
  - CVE-2022-29216 (RCE, Critical)
  - CVE-2024-12488 (RCE, High)


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
