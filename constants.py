from dotenv import load_dotenv
import os

load_dotenv()

# Logging
log_dir = "./logs"

# Database
db_name = os.getenv("MONGODB_DB")
collection_js_name = os.getenv("MONGODB_COLLECTION_NODE")
collection_py_name = os.getenv("MONGODB_COLLECTION_PYTHON")
collection_system_name = os.getenv("MONGODB_COLLECTION_SYSTEM", "system_vulnerabilities")
db_url_dev = os.getenv("MONGODB_URI_DEV")
db_url_prod = os.getenv("MONGODB_URI_PROD")
