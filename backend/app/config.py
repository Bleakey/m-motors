import os
from pathlib import Path

# Locally: m-motors/  |  Docker: /app  (set APP_BASE_DIR in docker-compose)
BASE_DIR   = Path(os.getenv("APP_BASE_DIR", str(Path(__file__).parent.parent.parent)))
FRONTEND   = BASE_DIR / "frontend"
TEMPLATES  = FRONTEND / "templates"
UPLOAD_DIR = FRONTEND / "static" / "uploads"
STATIC_DIR = FRONTEND / "static"
