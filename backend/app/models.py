import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserRole(str, enum.Enum):
    client = "client"
    admin  = "admin"


class VehicleType(str, enum.Enum):
    achat    = "achat"
    location = "location"
    both     = "both"


class DossierType(str, enum.Enum):
    achat    = "achat"
    location = "location"


class DossierStatus(str, enum.Enum):
    en_attente = "en_attente"
    en_cours   = "en_cours"
    valide     = "valide"
    refuse     = "refuse"


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    nom             = Column(String(100), nullable=False)
    prenom          = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, index=True, nullable=False)
    telephone       = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum(UserRole), default=UserRole.client, nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    dossiers = relationship("Dossier", back_populates="client")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id                    = Column(Integer, primary_key=True, index=True)
    marque                = Column(String(100), nullable=False)
    modele                = Column(String(100), nullable=False)
    annee                 = Column(Integer, nullable=False)
    kilometrage           = Column(Integer, nullable=False)
    prix_achat            = Column(Float, nullable=True)
    prix_location_mensuel = Column(Float, nullable=True)
    carburant             = Column(String(50), nullable=True)
    transmission          = Column(String(50), nullable=True)
    couleur               = Column(String(50), nullable=True)
    description           = Column(Text, nullable=True)
    image_url             = Column(String(255), nullable=True)
    type                  = Column(Enum(VehicleType), default=VehicleType.achat)
    disponible            = Column(Boolean, default=True)
    created_at            = Column(DateTime(timezone=True), server_default=func.now())

    dossiers = relationship("Dossier", back_populates="vehicle")


class Dossier(Base):
    __tablename__ = "dossiers"

    id                  = Column(Integer, primary_key=True, index=True)
    client_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id          = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    type                = Column(Enum(DossierType), nullable=False)
    status              = Column(Enum(DossierStatus), default=DossierStatus.en_attente)
    commentaire_admin   = Column(Text, nullable=True)
    doc_identite        = Column(String(255), nullable=True)
    doc_permis          = Column(String(255), nullable=True)
    doc_justif_domicile = Column(String(255), nullable=True)
    doc_justif_revenus  = Column(String(255), nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    client  = relationship("User", back_populates="dossiers")
    vehicle = relationship("Vehicle", back_populates="dossiers")
