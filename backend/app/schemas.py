from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import UserRole, VehicleType, DossierType, DossierStatus


class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    password: str


class UserOut(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class VehicleCreate(BaseModel):
    marque: str
    modele: str
    annee: int
    kilometrage: int
    prix_achat: Optional[float] = None
    prix_location_mensuel: Optional[float] = None
    carburant: Optional[str] = None
    transmission: Optional[str] = None
    couleur: Optional[str] = None
    description: Optional[str] = None
    type: VehicleType


class VehicleOut(BaseModel):
    id: int
    marque: str
    modele: str
    annee: int
    kilometrage: int
    prix_achat: Optional[float]
    prix_location_mensuel: Optional[float]
    carburant: Optional[str]
    transmission: Optional[str]
    couleur: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    type: VehicleType
    disponible: bool

    class Config:
        from_attributes = True


class DossierOut(BaseModel):
    id: int
    vehicle_id: int
    type: DossierType
    status: DossierStatus
    commentaire_admin: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
