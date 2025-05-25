# Project 20 (Python)

This is a sample Python project with the following dependencies:

- torch v1.9.0
  CVEs:
  - CVE-2022-29217 (Memory Corruption, Critical)
  - CVE-2023-31480 (DoS, High)
  - CVE-2024-12479 (Memory Corruption, High)
  - CVE-2024-12480 (DoS, Critical)

- pillow v8.3.2
  CVEs:
  - CVE-2021-23437 (Buffer Overflow, High)
  - CVE-2023-50447 (RCE, Critical)
  - CVE-2024-12481 (Buffer Overflow, Critical)
  - CVE-2024-12482 (RCE, High)

- torchvision v0.10.0
  CVEs:
  - CVE-2022-29218 (Memory Corruption, High)
  - CVE-2024-12483 (Memory Corruption, Critical)


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
