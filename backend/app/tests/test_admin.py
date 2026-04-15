import io
import pytest
from fastapi.testclient import TestClient
from app import models


def _login_admin(client):
    client.post("/auth/login", data={
        "email": "admin@test.fr", "password": "Admin123!"
    })


def _login_client(client):
    client.post("/auth/login", data={
        "email": "client@test.fr", "password": "Client123!"
    })


def test_admin_dashboard_requires_admin(client: TestClient, client_user):
    _login_client(client)
    r = client.get("/admin/dashboard")
    assert r.status_code == 403


def test_admin_dashboard_accessible(client: TestClient, admin_user):
    _login_admin(client)
    r = client.get("/admin/dashboard")
    assert r.status_code == 200


def test_add_vehicle(client: TestClient, admin_user):
    _login_admin(client)
    r = client.post("/admin/vehicles/add", data={
        "marque": "Peugeot", "modele": "208",
        "annee": "2021", "kilometrage": "30000",
        "prix_achat": "14000", "type": "achat"
    })
    assert r.status_code == 302


def test_add_vehicle_location(client: TestClient, admin_user):
    _login_admin(client)
    r = client.post("/admin/vehicles/add", data={
        "marque": "Citroen", "modele": "C3",
        "annee": "2022", "kilometrage": "10000",
        "prix_location_mensuel": "349", "type": "location"
    })
    assert r.status_code == 302


def test_toggle_vehicle_type(client: TestClient, admin_user, sample_vehicle):
    _login_admin(client)
    original_type = sample_vehicle.type
    r = client.post(f"/admin/vehicles/{sample_vehicle.id}/toggle")
    assert r.status_code == 302


def test_delete_vehicle(client: TestClient, admin_user, sample_vehicle, db):
    _login_admin(client)
    r = client.post(f"/admin/vehicles/{sample_vehicle.id}/delete")
    assert r.status_code == 302
    assert db.query(models.Vehicle).filter(
        models.Vehicle.id == sample_vehicle.id
    ).first() is None


def test_delete_nonexistent_vehicle(client: TestClient, admin_user):
    _login_admin(client)
    r = client.post("/admin/vehicles/9999/delete")
    assert r.status_code == 302


def test_admin_dossiers_list(client: TestClient, admin_user):
    _login_admin(client)
    r = client.get("/admin/dossiers")
    assert r.status_code == 200


def test_update_dossier_status(
    client: TestClient, admin_user, client_user, sample_vehicle, db
):
    # Create a dossier directly in DB
    dossier = models.Dossier(
        client_id=client_user.id,
        vehicle_id=sample_vehicle.id,
        type=models.DossierType.achat,
        status=models.DossierStatus.en_attente
    )
    db.add(dossier)
    db.commit()
    db.refresh(dossier)

    _login_admin(client)
    r = client.post(f"/admin/dossiers/{dossier.id}/update", data={
        "status": "valide",
        "commentaire_admin": "Dossier complet"
    })
    assert r.status_code == 302

    db.refresh(dossier)
    assert dossier.status == models.DossierStatus.valide
    assert dossier.commentaire_admin == "Dossier complet"


def test_update_dossier_refuse(
    client: TestClient, admin_user, client_user, sample_vehicle, db
):
    dossier = models.Dossier(
        client_id=client_user.id,
        vehicle_id=sample_vehicle.id,
        type=models.DossierType.location,
        status=models.DossierStatus.en_attente
    )
    db.add(dossier)
    db.commit()
    db.refresh(dossier)

    _login_admin(client)
    r = client.post(f"/admin/dossiers/{dossier.id}/update", data={
        "status": "refuse",
        "commentaire_admin": "Revenus insuffisants"
    })
    assert r.status_code == 302
    db.refresh(dossier)
    assert dossier.status == models.DossierStatus.refuse
