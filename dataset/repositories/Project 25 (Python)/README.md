# Project 25 (Python)

This is a sample Python project with the following dependencies:

- numpy v1.21.2
  CVEs:
  - CVE-2022-21699 (Memory Leak, High)
  - CVE-2023-52443 (Buffer Overflow, Critical)
  - CVE-2024-12505 (Memory Leak, Critical)
  - CVE-2024-12506 (Buffer Overflow, High)

- matplotlib v3.4.3
  CVEs:
  - CVE-2021-23440 (XSS, Medium)
  - CVE-2023-52444 (DoS, High)
  - CVE-2024-12507 (XSS, High)
  - CVE-2024-12508 (DoS, Critical)

- pytz v2021.3
  CVEs:
  - CVE-2023-52445 (Time Zone Manipulation, Medium)
  - CVE-2024-12509 (Time Zone Manipulation, High)


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
