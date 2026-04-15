from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models
from app.auth import get_current_user

from app.config import TEMPLATES

router    = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES))


@router.get("/", response_class=HTMLResponse)
async def list_vehicles(
    request: Request,
    type:     Optional[str]   = Query(None),
    marque:   Optional[str]   = Query(None),
    prix_max: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    user  = await get_current_user(request, db)
    query = db.query(models.Vehicle).filter(models.Vehicle.disponible == True)

    if type in ("achat", "location"):
        query = query.filter(
            (models.Vehicle.type == type) |
            (models.Vehicle.type == models.VehicleType.both)
        )
    if marque:
        query = query.filter(models.Vehicle.marque.ilike(f"%{marque}%"))
    if prix_max:
        query = query.filter(models.Vehicle.prix_achat <= prix_max)

    vehicles = query.all()
    marques  = sorted({v.marque for v in vehicles})

    return templates.TemplateResponse("vehicles.html", {
        "request": request, "user": user,
        "vehicles": vehicles, "marques": marques,
        "current_type": type, "current_marque": marque,
        "current_prix_max": prix_max
    })


@router.get("/{vehicle_id}", response_class=HTMLResponse)
async def vehicle_detail(
    request: Request,
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    user    = await get_current_user(request, db)
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id
    ).first()
    if not vehicle:
        return templates.TemplateResponse(
            "base.html",
            {"request": request, "user": user, "error": "Véhicule non trouvé"},
            status_code=404
        )
    return templates.TemplateResponse("vehicle_detail.html", {
        "request": request, "user": user, "vehicle": vehicle
    })
