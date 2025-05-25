# Project 18 (Python)

This is a sample Python project with the following dependencies:

- pandas v1.2.4
  CVEs:
  - CVE-2021-34439 (Code Injection, Medium)
  - CVE-2023-52426 (DoS, High)
  - CVE-2024-12469 (Code Injection, High)
  - CVE-2024-12470 (DoS, Critical)

- scipy v1.7.1
  CVEs:
  - CVE-2021-33430 (DoS, Medium)
  - CVE-2023-52427 (Memory Corruption, High)
  - CVE-2024-12471 (DoS, High)
  - CVE-2024-12472 (Memory Corruption, Critical)

- h5py v3.6.0
  CVEs:
  - CVE-2021-27362 (Buffer Overflow, High)
  - CVE-2024-12473 (Buffer Overflow, Critical)


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
