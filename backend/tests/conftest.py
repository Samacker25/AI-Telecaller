"""Shared test fixtures.

Tests run against an in-memory SQLite database via aiosqlite,
so no external services are required.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.session import get_db
from app.main import create_app
from app.models import Base


@pytest.fixture
async def app():
    application = create_app()

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncIterator:
        async with session_factory() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db
    yield application
    await engine.dispose()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


_ADMIN_ACCOUNT = {"name": "Admin", "email": "admin@hospital.com", "password": "secure-password-1"}
_STAFF_ACCOUNT = {"name": "Staff", "email": "staff@hospital.com", "password": "secure-password-2"}


async def _register_and_login(client: AsyncClient, account: dict) -> dict[str, str]:
    response = await client.post("/api/v1/auth/register", json=account)
    assert response.status_code == 201, response.text
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": account["email"], "password": account["password"]},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
async def admin_headers(client: AsyncClient) -> dict[str, str]:
    """Auth headers for an admin (the first registered account)."""
    return await _register_and_login(client, _ADMIN_ACCOUNT)


@pytest.fixture
async def staff_headers(client: AsyncClient, admin_headers) -> dict[str, str]:
    """Auth headers for a staff account (registered after the admin)."""
    return await _register_and_login(client, _STAFF_ACCOUNT)


@pytest.fixture
async def hospital(client: AsyncClient, admin_headers) -> dict:
    """The single MVP hospital profile, created by the admin."""
    response = await client.post(
        "/api/v1/hospitals",
        json={"name": "City Hospital", "phone": "+911234567890"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()
