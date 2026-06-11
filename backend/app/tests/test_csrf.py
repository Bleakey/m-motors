import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.csrf import verify_csrf


@pytest.fixture
def csrf_client():
    """Client SANS le bypass CSRF, pour tester la vraie protection."""
    app.dependency_overrides.pop(verify_csrf, None)
    client = TestClient(app, base_url="https://testserver", follow_redirects=False)
    yield client
    # restaure le bypass pour ne pas impacter les autres tests
    app.dependency_overrides[verify_csrf] = lambda: None


def test_post_sans_token_csrf_est_refuse(csrf_client, client_user):
    r = csrf_client.post(
        "/auth/login",
        data={"email": "client@test.fr", "password": "Client123!"},
    )
    assert r.status_code == 403


def test_post_avec_token_csrf_valide_est_accepte(csrf_client, client_user):
    # Le middleware depose le cookie csrf_token sur la page GET.
    csrf_client.get("/auth/login")
    token = csrf_client.cookies.get("csrf_token")
    assert token

    r = csrf_client.post(
        "/auth/login",
        data={
            "email": "client@test.fr",
            "password": "Client123!",
            "csrf_token": token,
        },
    )
    assert r.status_code != 403
