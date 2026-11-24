import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import create_token
from app.models import User

def register(client, email="owner@example.com", organization_name="North Fleet"):
    return client.post("/api/v1/auth/register", json={"email": email, "password": "a-strong-password-123", "organization_name": organization_name})

def test_register_creates_owner_with_hashed_password(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    assert "fleetcore_refresh" not in response.json()
    assert client.cookies.get("fleetcore_refresh")
    profile = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {response.json()['access_token']}"})
    assert profile.status_code == 200 and profile.json()["organization"]["role"] == "owner"
    assert "hashed_password" not in profile.json()
    with Session(client.app.state.test_engine) as db:
        user = db.scalar(select(User).where(User.email == "owner@example.com"))
        assert user.hashed_password.startswith("$argon2id$")

def test_register_rejects_existing_email(client):
    assert register(client).status_code == 201
    assert register(client, email="OWNER@example.com").status_code == 409

def test_login_success_and_wrong_password(client):
    register(client)
    good = client.post("/api/v1/auth/login", json={"email": "OWNER@example.com", "password": "a-strong-password-123"})
    bad = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "wrong-password"})
    assert good.status_code == 200 and good.json().get("access_token")
    assert bad.status_code == 401

def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401

def test_refresh_rotates_refresh_token(client):
    register(client)
    old_refresh = client.cookies.get("fleetcore_refresh")
    refreshed = client.post("/api/v1/auth/refresh")
    new_refresh = client.cookies.get("fleetcore_refresh")
    assert refreshed.status_code == 200 and new_refresh != old_refresh
    client.cookies.set("fleetcore_refresh", old_refresh, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401

def test_logout_revokes_refresh_token(client):
    register(client)
    refresh_token = client.cookies.get("fleetcore_refresh")
    assert client.post("/api/v1/auth/logout").status_code == 204
    client.cookies.set("fleetcore_refresh", refresh_token, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401

def test_user_cannot_use_access_token_for_another_organization(client):
    a = register(client, email="a@example.com", organization_name="A Corp")
    b = register(client, email="b@example.com", organization_name="B Corp")
    profile_a = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {a.json()['access_token']}"}).json()
    profile_b = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {b.json()['access_token']}"}).json()
    assert profile_a["organization"]["id"] != profile_b["organization"]["id"]
    forged, _ = create_token(user_id=uuid.UUID(profile_a["id"]), organization_id=uuid.UUID(profile_b["organization"]["id"]), token_type="access", lifetime=900)
    denied = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert denied.status_code == 401
