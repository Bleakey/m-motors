import os
import uuid
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import require_auth

from app.config import TEMPLATES, UPLOAD_DIR

router    = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES))


ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE      = 5 * 1024 * 1024  # 5 Mo


async def _save_file(file: UploadFile, subfolder: str) -> str:
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non autorisé : {file.filename}. Formats acceptés : PDF, JPG, PNG"
        )
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux : {file.filename} (max 5 Mo)"
        )
    dest = UPLOAD_DIR / subfolder
    dest.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.{ext}"
    with open(dest / filename, "wb") as f:
        f.write(content)
    return f"/static/uploads/{subfolder}/{filename}"


@router.get("/nouveau/{vehicle_id}", response_class=HTMLResponse)
async def dossier_form(
    request: Request,
    vehicle_id: int,
    type: str = "achat",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_auth)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")
    return templates.TemplateResponse("dossier_form.html", {
        "request": request, "user": current_user,
        "vehicle": vehicle, "dossier_type": type
    })


@router.post("/nouveau/{vehicle_id}")
async def submit_dossier(
    request: Request,
    vehicle_id: int,
    dossier_type: str    = Form(...),
    doc_identite: UploadFile        = File(...),
    doc_permis: UploadFile          = File(...),
    doc_justif_domicile: UploadFile = File(...),
    doc_justif_revenus: UploadFile  = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_auth)
):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule introuvable")

    sub = f"user_{current_user.id}"
    dossier = models.Dossier(
        client_id           = current_user.id,
        vehicle_id          = vehicle_id,
        type                = dossier_type,
        doc_identite        = await _save_file(doc_identite,        sub),
        doc_permis          = await _save_file(doc_permis,          sub),
        doc_justif_domicile = await _save_file(doc_justif_domicile, sub),
        doc_justif_revenus  = await _save_file(doc_justif_revenus,  sub),
        status              = models.DossierStatus.en_attente
    )
    db.add(dossier)
    db.commit()
    return RedirectResponse(url="/client/dashboard?submitted=1", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
async def client_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_auth)
):
    dossiers = (
        db.query(models.Dossier)
        .filter(models.Dossier.client_id == current_user.id)
        .order_by(models.Dossier.created_at.desc())
        .all()
    )
    return templates.TemplateResponse("dashboard_client.html", {
        "request": request, "user": current_user, "dossiers": dossiers
    })
