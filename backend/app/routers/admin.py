import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import require_admin

from app.config import TEMPLATES, UPLOAD_DIR

router    = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    def count_status(s):
        return db.query(models.Dossier).filter(models.Dossier.status == s).count()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "user": admin,
        "total_vehicles": db.query(models.Vehicle).count(),
        "total_clients":  db.query(models.User)
                            .filter(models.User.role == "client").count(),
        "total_dossiers": db.query(models.Dossier).count(),
        "pending":        count_status("en_attente"),
        "stats": {
            "en_attente": count_status("en_attente"),
            "en_cours":   count_status("en_cours"),
            "valide":     count_status("valide"),
            "refuse":     count_status("refuse"),
        }
    })


# ── Vehicles ──────────────────────────────────────────

@router.get("/vehicles", response_class=HTMLResponse)
async def vehicles(
    request: Request,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    return templates.TemplateResponse("admin/vehicles_manage.html", {
        "request": request, "user": admin,
        "vehicles": db.query(models.Vehicle).all()
    })


@router.post("/vehicles/add")
async def add_vehicle(
    marque: str           = Form(...),
    modele: str           = Form(...),
    annee: int            = Form(...),
    kilometrage: int      = Form(...),
    prix_achat: Optional[float]    = Form(None),
    prix_location_mensuel: Optional[float] = Form(None),
    carburant: str        = Form(""),
    transmission: str     = Form(""),
    couleur: str          = Form(""),
    description: str      = Form(""),
    type: str             = Form(...),
    image: UploadFile     = File(None),
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    image_url = None
    if image and image.filename:
        dest = UPLOAD_DIR / "vehicles"
        dest.mkdir(parents=True, exist_ok=True)
        ext      = image.filename.rsplit(".", 1)[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        with open(dest / filename, "wb") as f:
            f.write(await image.read())
        image_url = f"/static/uploads/vehicles/{filename}"

    db.add(models.Vehicle(
        marque=marque, modele=modele, annee=annee,
        kilometrage=kilometrage, prix_achat=prix_achat,
        prix_location_mensuel=prix_location_mensuel,
        carburant=carburant, transmission=transmission,
        couleur=couleur, description=description,
        type=type, image_url=image_url
    ))
    db.commit()
    return RedirectResponse(url="/admin/vehicles?added=1", status_code=302)


@router.post("/vehicles/{vid}/toggle")
async def toggle_type(
    vid: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    v = db.query(models.Vehicle).filter(models.Vehicle.id == vid).first()
    if not v:
        raise HTTPException(status_code=404)
    mapping = {
        models.VehicleType.achat:    models.VehicleType.location,
        models.VehicleType.location: models.VehicleType.both,
        models.VehicleType.both:     models.VehicleType.achat,
    }
    v.type = mapping[v.type]
    db.commit()
    return RedirectResponse(url="/admin/vehicles", status_code=302)


@router.post("/vehicles/{vid}/disponible")
async def toggle_disponible(
    vid: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    v = db.query(models.Vehicle).filter(models.Vehicle.id == vid).first()
    if not v:
        raise HTTPException(status_code=404)
    v.disponible = not v.disponible
    db.commit()
    return RedirectResponse(url="/admin/vehicles", status_code=302)


@router.post("/vehicles/{vid}/delete")
async def delete_vehicle(
    vid: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    v = db.query(models.Vehicle).filter(models.Vehicle.id == vid).first()
    if v:
        db.delete(v)
        db.commit()
    return RedirectResponse(url="/admin/vehicles", status_code=302)


# ── Dossiers ─────────────────────────────────────────

@router.get("/dossiers", response_class=HTMLResponse)
async def dossiers(
    request: Request,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    return templates.TemplateResponse("admin/dossiers_manage.html", {
        "request": request, "user": admin,
        "dossiers": db.query(models.Dossier)
                      .order_by(models.Dossier.created_at.desc()).all()
    })


@router.post("/dossiers/{did}/update")
async def update_dossier(
    did: int,
    status: str             = Form(...),
    commentaire_admin: str  = Form(""),
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    d = db.query(models.Dossier).filter(models.Dossier.id == did).first()
    if not d:
        raise HTTPException(status_code=404)
    d.status            = status
    d.commentaire_admin = commentaire_admin
    db.commit()
    return RedirectResponse(url="/admin/dossiers", status_code=302)
