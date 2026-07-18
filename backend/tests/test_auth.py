"""Tests for authentication: register, login, current user, and role-based access."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, hash_password, verify_password

ADMIN = {"name": "Admin", "email": "admin@hospital.com", "password": "secure-password-1"}
STAFF = {"name": "Staff", "email": "staff@hospital.com", "password": "secure-password-2"}


async def register(client: AsyncClient, payload: dict) -> dict:
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def login(client: AsyncClient, payload: dict) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self):
        hashed = hash_password("secret-password")
        assert hashed != "secret-password"
        assert verify_password("secret-password", hashed)

    def test_wrong_password_rejected(self):
        hashed = hash_password("secret-password")
        assert not verify_password("other-password", hashed)

    def test_invalid_hash_rejected(self):
        assert not verify_password("secret-password", "not-a-bcrypt-hash")


class TestRegister:
    async def test_first_user_becomes_admin(self, client: AsyncClient):
        body = await register(client, ADMIN)
        assert body["role"] == "admin"
        assert body["email"] == ADMIN["email"]
        assert "password" not in body
        assert "password_hash" not in body

    async def test_second_user_becomes_staff(self, client: AsyncClient):
        await register(client, ADMIN)
        body = await register(client, STAFF)
        assert body["role"] == "staff"

    async def test_duplicate_email_conflict(self, client: AsyncClient):
        await register(client, ADMIN)
        response = await client.post("/api/v1/auth/register", json=ADMIN)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"

    async def test_email_is_case_insensitive(self, client: AsyncClient):
        await register(client, ADMIN)
        response = await client.post(
            "/api/v1/auth/register", json={**ADMIN, "email": ADMIN["email"].upper()}
        )
        assert response.status_code == 409

    @pytest.mark.parametrize(
        "payload",
        [
            {**ADMIN, "email": "not-an-email"},
            {**ADMIN, "password": "short"},
            {**ADMIN, "name": ""},
        ],
    )
    async def test_invalid_payload_rejected(self, client: AsyncClient, payload: dict):
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422


class TestLogin:
    async def test_login_returns_token(self, client: AsyncClient):
        await register(client, ADMIN)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": ADMIN["email"], "password": ADMIN["password"]},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["token_type"] == "Bearer"  # noqa: S105
        assert body["expires_in"] > 0

    async def test_wrong_password_unauthorized(self, client: AsyncClient):
        await register(client, ADMIN)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": ADMIN["email"], "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_unknown_email_unauthorized(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@hospital.com", "password": "irrelevant-password"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


class TestCurrentUser:
    async def test_me_returns_authenticated_user(self, client: AsyncClient):
        await register(client, ADMIN)
        token = await login(client, ADMIN)
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == ADMIN["email"]

    async def test_me_without_token_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_me_with_garbage_token_unauthorized(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_TOKEN"

    async def test_token_for_deleted_user_unauthorized(self, client: AsyncClient):
        token, _ = create_access_token(subject="00000000-0000-0000-0000-000000000000", role="admin")
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401


class TestRoleBasedAccess:
    async def test_admin_can_list_users(self, client: AsyncClient):
        await register(client, ADMIN)
        await register(client, STAFF)
        token = await login(client, ADMIN)
        response = await client.get(
            "/api/v1/auth/users", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert [user["email"] for user in response.json()] == [ADMIN["email"], STAFF["email"]]

    async def test_staff_cannot_list_users(self, client: AsyncClient):
        await register(client, ADMIN)
        await register(client, STAFF)
        token = await login(client, STAFF)
        response = await client.get(
            "/api/v1/auth/users", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"

    async def test_anonymous_cannot_list_users(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/users")
        assert response.status_code == 401
