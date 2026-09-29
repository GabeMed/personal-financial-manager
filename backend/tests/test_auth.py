from datetime import timedelta

from backend.app.core.oauth2 import create_access_token
from tests.conftest import API, PASSWORD


def test_register_returns_user_without_password(register):
    response = register("alice")

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert body["balance"] == 0
    assert "password" not in body and "hashed_password" not in body


def test_register_rejects_duplicate_username(register):
    register("alice")
    response = register("alice", email="other@example.com")

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_register_rejects_duplicate_email(register):
    register("alice")
    response = register("alice2", email="alice@example.com")

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_validates_payload(register):
    assert register("al").status_code == 422  # username too short
    assert register("alice", password="123").status_code == 422  # password too short
    assert register("alice", email="not-an-email").status_code == 422


def test_login_returns_bearer_token(client, register):
    register("alice")
    response = client.post(
        f"{API}/auth/token", data={"username": "alice", "password": PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_fails(client, register):
    register("alice")
    response = client.post(
        f"{API}/auth/token", data={"username": "alice", "password": "wrong-pass"}
    )

    assert response.status_code == 401


def test_login_with_unknown_user_fails(client):
    response = client.post(
        f"{API}/auth/token", data={"username": "ghost", "password": PASSWORD}
    )

    assert response.status_code == 401


def test_me_returns_current_user(client, alice):
    response = client.get(f"{API}/users/me", headers=alice)

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_protected_routes_require_a_token(client):
    for path in ("/users/me", "/categories/all", "/transactions/all"):
        assert client.get(f"{API}{path}").status_code == 401


def test_invalid_and_expired_tokens_are_rejected(client, register):
    register("alice")
    expired = create_access_token({"sub": "alice"}, timedelta(minutes=-1))
    for token in ("not-a-jwt", expired):
        response = client.get(
            f"{API}/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401


def test_token_for_deleted_user_is_rejected(client):
    token = create_access_token({"sub": "nobody"})
    response = client.get(
        f"{API}/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


def test_openapi_points_to_the_real_token_url(client):
    schemes = client.get("/openapi.json").json()["components"]["securitySchemes"]

    assert schemes["OAuth2PasswordBearer"]["flows"]["password"]["tokenUrl"] == (
        f"{API}/auth/token"
    )
