import logging
import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import Base, engine, get_db
from app import models
from app.auth import hash_password, get_current_user
from app.routers import auth, vehicles, dossiers, admin
from app.config import TEMPLATES, STATIC_DIR, UPLOAD_DIR

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")]
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="M-Motors", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES))

app.include_router(auth.router,     prefix="/auth",     tags=["auth"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
app.include_router(dossiers.router, prefix="/dossiers", tags=["dossiers"])
app.include_router(admin.router,    prefix="/admin",    tags=["admin"])


@app.on_event("startup")
async def seed_admin():
    db = next(get_db())
    try:
        if not db.query(models.User).filter(
            models.User.email == "admin@m-motors.fr"
        ).first():
            db.add(models.User(
                nom="Admin", prenom="M-Motors",
                email="admin@m-motors.fr",
                hashed_password=hash_password("Admin123!"),
                role=models.UserRole.admin
            ))
            db.commit()
            logger.info("Admin créé : admin@m-motors.fr / Admin123!")
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    db       = next(get_db())
    user     = await get_current_user(request, db)
    featured = db.query(models.Vehicle).filter(
        models.Vehicle.disponible == True
    ).limit(6).all()
    return templates.TemplateResponse("index.html", {
        "request": request, "user": user, "featured": featured
    })


@app.get("/client/dashboard", response_class=HTMLResponse)
async def client_dashboard_redirect(request: Request):
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dossiers/dashboard", status_code=302)
