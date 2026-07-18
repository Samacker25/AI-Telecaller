"""API tests for health, readiness, liveness, and smoke endpoints."""


async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"]
    assert body["version"]


async def test_live_returns_alive(client):
    response = await client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_ready_returns_ready_when_database_available(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"


async def test_ping_smoke_test(client):
    response = await client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


async def test_request_id_header_is_returned(client):
    response = await client.get("/health")
    assert response.headers.get("X-Request-ID")


async def test_incoming_request_id_is_preserved(client):
    response = await client.get("/health", headers={"X-Request-ID": "test-id-123"})
    assert response.headers.get("X-Request-ID") == "test-id-123"


async def test_unknown_route_returns_standard_error_shape(client):
    response = await client.get("/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "HTTP_ERROR"
