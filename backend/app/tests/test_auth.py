import pytest
from fastapi.testclient import TestClient


def test_register_new_user(client: TestClient):
    r = client.post("/auth/register", data={
        "nom": "Dupont", "prenom": "Jean",
        "email": "jean@test.fr", "password": "Pass1234!",
        "password_confirm": "Pass1234!"
    })
    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]


def test_register_duplicate_email(client: TestClient, client_user):
    r = client.post("/auth/register", data={
        "nom": "X", "prenom": "Y",
        "email": "client@test.fr", "password": "Pass1234!",
        "password_confirm": "Pass1234!"
    })
    assert r.status_code == 400


def test_register_password_mismatch(client: TestClient):
    r = client.post("/auth/register", data={
        "nom": "X", "prenom": "Y",
        "email": "x@test.fr", "password": "Pass1234!",
        "password_confirm": "AutrePass1!"
    })
    assert r.status_code == 400


def test_register_weak_password(client: TestClient):
    r = client.post("/auth/register", data={
        "nom": "X", "prenom": "Y",
        "email": "x@test.fr", "password": "faible",
        "password_confirm": "faible"
    })
    assert r.status_code == 400


def test_login_valid(client: TestClient, client_user):
    r = client.post("/auth/login", data={
        "email": "client@test.fr", "password": "Client123!"
    })
    assert r.status_code == 302
    assert "access_token" in r.cookies


def test_login_wrong_password(client: TestClient, client_user):
    r = client.post("/auth/login", data={
        "email": "client@test.fr", "password": "wrong"
    })
    assert r.status_code == 401


def test_login_unknown_email(client: TestClient):
    r = client.post("/auth/login", data={
        "email": "nobody@test.fr", "password": "whatever"
    })
    assert r.status_code == 401


def test_logout_clears_cookie(client: TestClient, client_user):
    client.post("/auth/login", data={
        "email": "client@test.fr", "password": "Client123!"
    })
    r = client.get("/auth/logout")
    assert r.status_code == 302
    assert "access_token" not in client.cookies


def test_login_redirects_admin_to_dashboard(client: TestClient, admin_user):
    r = client.post("/auth/login", data={
        "email": "admin@test.fr", "password": "Admin123!"
    })
    assert r.status_code == 302
    assert "/admin/dashboard" in r.headers["location"]


def test_login_redirects_client_to_dashboard(client: TestClient, client_user):
    r = client.post("/auth/login", data={
        "email": "client@test.fr", "password": "Client123!"
    })
    assert r.status_code == 302
    assert "/client/dashboard" in r.headers["location"]
