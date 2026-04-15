from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import (
    hash_password, verify_password,
    create_access_token, get_current_user
)

from app.config import TEMPLATES

router    = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request, db)
    if user:
        return RedirectResponse(
            url="/admin/dashboard" if user.role == models.UserRole.admin
            else "/client/dashboard",
            status_code=302
        )
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str    = Form(...),
    password: str = Form(...),
    db: Session   = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Email ou mot de passe incorrect"},
            status_code=401
        )
    token    = create_access_token({"sub": user.email})
    redirect = "/admin/dashboard" if user.role == models.UserRole.admin \
               else "/client/dashboard"
    response = RedirectResponse(url=redirect, status_code=302)
    response.set_cookie(
        key="access_token", value=token,
        httponly=True, max_age=3600
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    nom: str       = Form(...),
    prenom: str    = Form(...),
    email: str     = Form(...),
    telephone: str = Form(""),
    password: str  = Form(...),
    db: Session    = Depends(get_db)
):
    if db.query(models.User).filter(models.User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email déjà utilisé"},
            status_code=400
        )
    db.add(models.User(
        nom=nom, prenom=prenom, email=email,
        telephone=telephone,
        hashed_password=hash_password(password),
        role=models.UserRole.client
    ))
    db.commit()
    return RedirectResponse(url="/auth/login?registered=1", status_code=302)


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response
