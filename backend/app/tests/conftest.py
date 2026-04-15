import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app import models
from app.auth import hash_password


TEST_DB_URL = "sqlite:///./test.db"
engine      = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_user(db):
    user = models.User(
        nom="Admin", prenom="Test",
        email="admin@test.fr",
        hashed_password=hash_password("Admin123!"),
        role=models.UserRole.admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client_user(db):
    user = models.User(
        nom="Client", prenom="Test",
        email="client@test.fr",
        hashed_password=hash_password("Client123!"),
        role=models.UserRole.client
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_vehicle(db):
    v = models.Vehicle(
        marque="Renault", modele="Clio",
        annee=2020, kilometrage=45000,
        prix_achat=12000.0,
        prix_location_mensuel=299.0,
        carburant="Essence", transmission="Manuelle",
        couleur="Blanc", type=models.VehicleType.both
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def get_auth_cookie(test_client: TestClient, email: str, password: str) -> dict:
    """Login and return cookies dict."""
    r = test_client.post(
        "/auth/login",
        data={"email": email, "password": password}
    )
    return test_client.cookies
