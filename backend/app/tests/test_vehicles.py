import pytest
from fastapi.testclient import TestClient
from app import models


def test_vehicles_page_public(client: TestClient):
    r = client.get("/vehicles/")
    assert r.status_code == 200


def test_vehicles_filter_by_type(client: TestClient, sample_vehicle):
    r = client.get("/vehicles/?type=achat")
    assert r.status_code == 200
    assert "Renault" in r.text


def test_vehicles_filter_location(client: TestClient, sample_vehicle):
    r = client.get("/vehicles/?type=location")
    assert r.status_code == 200


def test_vehicles_filter_by_marque(client: TestClient, sample_vehicle):
    r = client.get("/vehicles/?marque=Renault")
    assert r.status_code == 200
    assert "Renault" in r.text


def test_vehicles_filter_no_results(client: TestClient, sample_vehicle):
    r = client.get("/vehicles/?marque=Ferrari")
    assert r.status_code == 200


def test_vehicle_detail_found(client: TestClient, sample_vehicle):
    r = client.get(f"/vehicles/{sample_vehicle.id}")
    assert r.status_code == 200
    assert "Clio" in r.text


def test_vehicle_detail_not_found(client: TestClient):
    r = client.get("/vehicles/9999")
    assert r.status_code == 404


def test_vehicles_filter_prix_max(client: TestClient, sample_vehicle):
    r = client.get("/vehicles/?prix_max=15000")
    assert r.status_code == 200
    assert "Renault" in r.text


def test_vehicles_filter_prix_max_too_low(client: TestClient, sample_vehicle):
    r = client.get("/vehicles/?prix_max=1000")
    assert r.status_code == 200
    assert "Renault" not in r.text
