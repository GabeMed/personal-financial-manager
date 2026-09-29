import os

# Must be set before the app is imported: config reads them at import time.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["SEED_DEMO_DATA"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from backend.app.db.base import Base  # noqa: E402
from backend.app.db.session import get_db  # noqa: E402
from backend.app.main import app  # noqa: E402

API = "/api/v1"
PASSWORD = "secret123"


# Tests run on in-memory SQLite by default. CI also runs them on PostgreSQL:
#   TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost/db pytest
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")


@pytest.fixture
def session_factory():
    """A fresh, empty database per test."""
    if TEST_DATABASE_URL.startswith("sqlite"):
        # StaticPool keeps a single connection, so every session sees the same
        # in-memory database.
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory):
    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def register(client):
    def _register(username: str, password: str = PASSWORD, email: str | None = None):
        return client.post(
            f"{API}/users/register",
            json={
                "username": username,
                "email": email or f"{username}@example.com",
                "password": password,
            },
        )

    return _register


@pytest.fixture
def login_as(client, register):
    """Registers `username` and returns Authorization headers for it."""

    def _login_as(username: str) -> dict[str, str]:
        assert register(username).status_code == 201
        response = client.post(
            f"{API}/auth/token", data={"username": username, "password": PASSWORD}
        )
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _login_as


@pytest.fixture
def alice(login_as):
    return login_as("alice")


@pytest.fixture
def bob(login_as):
    return login_as("bob")


@pytest.fixture
def make_category(client):
    def _make_category(headers, name="Food"):
        response = client.post(
            f"{API}/categories", json={"name": name}, headers=headers
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _make_category


@pytest.fixture
def make_transaction(client):
    def _make_transaction(
        headers, category_id, type="expense", amount="10.00", **extra
    ):
        body = {"type": type, "amount": amount, "category_id": category_id, **extra}
        response = client.post(f"{API}/transactions", json=body, headers=headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _make_transaction


@pytest.fixture
def balance(client):
    def _balance(headers) -> float:
        return client.get(f"{API}/users/me", headers=headers).json()["balance"]

    return _balance
