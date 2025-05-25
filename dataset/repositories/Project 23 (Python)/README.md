# Project 23 (Python)

This is a sample Python project with the following dependencies:

- scrapy v2.5.1
  CVEs:
  - CVE-2022-34526 (SSRF, High)
  - CVE-2023-52436 (RCE, Critical)
  - CVE-2023-52437 (DoS, Medium)
  - CVE-2024-12494 (SSRF, Critical)
  - CVE-2024-12495 (RCE, High)
  - CVE-2024-12496 (DoS, High)

- beautifulsoup4 v4.9.3
  CVEs:
  - CVE-2021-23439 (XSS, Medium)
  - CVE-2023-52438 (Memory Corruption, High)
  - CVE-2024-12497 (XSS, High)
  - CVE-2024-12498 (Memory Corruption, Critical)

- lxml v4.6.3
  CVEs:
  - CVE-2023-52439 (Arbitrary Code Exec, Critical)
  - CVE-2024-12499 (Arbitrary Code Exec, High)


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
