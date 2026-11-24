import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import hash_password


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with Session() as session:
        session.add(User(username="boss", hashed_password=hash_password("bosspass123"), role="admin"))
        session.commit()
        yield session


@pytest.fixture()
def client(db_session):
    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    yield TestClient(app)  # no `with`: skips lifespan so the real DB is never touched
    app.dependency_overrides.clear()


def _login(client, username, password):
    res = client.post("/api/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
def admin_headers(client):
    return _login(client, "boss", "bosspass123")


@pytest.fixture()
def user_headers(client):
    client.post("/api/auth/register", json={"username": "asha", "password": "ashapass123"})
    return _login(client, "asha", "ashapass123")


@pytest.fixture()
def other_headers(client):
    client.post("/api/auth/register", json={"username": "ravi", "password": "ravipass123"})
    return _login(client, "ravi", "ravipass123")
