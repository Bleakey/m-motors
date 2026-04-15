from pathlib import Path

BASE_DIR    = Path(__file__).parent.parent.parent
FRONTEND    = BASE_DIR / "frontend"
TEMPLATES   = FRONTEND / "templates"
UPLOAD_DIR  = FRONTEND / "static" / "uploads"
STATIC_DIR  = FRONTEND / "static"
