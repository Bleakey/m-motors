import io
import pytest
from fastapi.testclient import TestClient


def _fake_file(name="doc.pdf"):
    return (name, io.BytesIO(b"fake content"), "application/pdf")


def _login(client, email, password):
    client.post("/auth/login", data={"email": email, "password": password})


def test_dossier_form_requires_auth(client: TestClient, sample_vehicle):
    r = client.get(f"/dossiers/nouveau/{sample_vehicle.id}?type=achat")
    assert r.status_code in (302, 401)


def test_dossier_form_authenticated(
    client: TestClient, client_user, sample_vehicle
):
    _login(client, "client@test.fr", "Client123!")
    r = client.get(f"/dossiers/nouveau/{sample_vehicle.id}?type=achat")
    assert r.status_code == 200
    assert "dossier" in r.text.lower()


def test_submit_dossier_achat(
    client: TestClient, client_user, sample_vehicle
):
    _login(client, "client@test.fr", "Client123!")
    r = client.post(
        f"/dossiers/nouveau/{sample_vehicle.id}",
        data={"dossier_type": "achat"},
        files={
            "doc_identite":        _fake_file("id.pdf"),
            "doc_permis":          _fake_file("permis.pdf"),
            "doc_justif_domicile": _fake_file("domicile.pdf"),
            "doc_justif_revenus":  _fake_file("revenus.pdf"),
        }
    )
    assert r.status_code == 302
    assert "/client/dashboard" in r.headers["location"]


def test_submit_dossier_location(
    client: TestClient, client_user, sample_vehicle
):
    _login(client, "client@test.fr", "Client123!")
    r = client.post(
        f"/dossiers/nouveau/{sample_vehicle.id}",
        data={"dossier_type": "location"},
        files={
            "doc_identite":        _fake_file("id.pdf"),
            "doc_permis":          _fake_file("permis.pdf"),
            "doc_justif_domicile": _fake_file("domicile.pdf"),
            "doc_justif_revenus":  _fake_file("revenus.pdf"),
        }
    )
    assert r.status_code == 302


def test_submit_dossier_vehicle_not_found(
    client: TestClient, client_user
):
    _login(client, "client@test.fr", "Client123!")
    r = client.post(
        "/dossiers/nouveau/9999",
        data={"dossier_type": "achat"},
        files={
            "doc_identite":        _fake_file(),
            "doc_permis":          _fake_file(),
            "doc_justif_domicile": _fake_file(),
            "doc_justif_revenus":  _fake_file(),
        }
    )
    assert r.status_code == 404


def test_client_dashboard_empty(client: TestClient, client_user):
    _login(client, "client@test.fr", "Client123!")
    r = client.get("/dossiers/dashboard")
    assert r.status_code == 200


def test_client_dashboard_with_dossier(
    client: TestClient, client_user, sample_vehicle
):
    _login(client, "client@test.fr", "Client123!")
    client.post(
        f"/dossiers/nouveau/{sample_vehicle.id}",
        data={"dossier_type": "achat"},
        files={
            "doc_identite":        _fake_file(),
            "doc_permis":          _fake_file(),
            "doc_justif_domicile": _fake_file(),
            "doc_justif_revenus":  _fake_file(),
        }
    )
    r = client.get("/dossiers/dashboard")
    assert r.status_code == 200
    assert "Clio" in r.text
