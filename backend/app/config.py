import os

# Directory to save uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CORS settings
CORS_ORIGINS = ["http://localhost:3000"]
