import os
from dotenv import load_dotenv, find_dotenv

# Load .env file if present. Prefer backend/.env (next to this package),
# otherwise fall back to the repository root .env (if present). When a file
# is found it will be loaded so its values are available via os.environ.
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    # load and allow file values to override existing environment variables
    load_dotenv(env_path, override=True)
else:
    # try to locate a .env somewhere up the tree (e.g. project root)
    root_dotenv = find_dotenv()
    if root_dotenv:
        load_dotenv(root_dotenv, override=True)

# Directory to save uploaded files (legacy/local use)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CORS settings
_cors_raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
# Allow a comma-separated list in the env file
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

# Service endpoints configurable via environment variables. Use these in
# backend code instead of hard-coded hostnames so deployments can override
# behaviour without editing source.
STORAGE_SERVICE_URL = os.environ.get(
    "STORAGE_SERVICE_URL", "http://storage-service:8002"
)
VISION_SERVICE_URL = os.environ.get("VISION_SERVICE_URL", "http://vision-service:8001")

# API path prefixes (allow tweaking if services expose routes under a prefix)
FILES_API_PREFIX = os.environ.get("FILES_API_PREFIX", "/api/files")
REPORTS_API_PREFIX = os.environ.get("REPORTS_API_PREFIX", "/api/reports")
