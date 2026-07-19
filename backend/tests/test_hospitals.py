"""Tests for hospital profile CRUD and hospital settings."""

from httpx import AsyncClient

HOSPITAL = {
    "name": "City Hospital",
    "address": "1 Main Street",
    "phone": "+911234567890",
    "email": "info@cityhospital.com",
    "website": "https://cityhospital.com",
}

WORKING_HOURS = {
    "monday": [
        {"start": "09:00", "end": "13:00"},
        {"start": "14:00", "end": "18:00"},
    ],
    "sunday": [],
}


class TestCreateHospital:
    async def test_requires_authentication(self, client: AsyncClient):
        response = await client.post("/api/v1/hospitals", json=HOSPITAL)
        assert response.status_code == 401

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers):
        response = await client.post("/api/v1/hospitals", json=HOSPITAL, headers=staff_headers)
        assert response.status_code == 403

    async def test_admin_creates_hospital(self, client: AsyncClient, admin_headers):
        response = await client.post("/api/v1/hospitals", json=HOSPITAL, headers=admin_headers)
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["name"] == HOSPITAL["name"]
        assert body["email"] == HOSPITAL["email"]
        assert "settings" not in body

    async def test_second_hospital_conflicts(self, client: AsyncClient, admin_headers, hospital):
        response = await client.post("/api/v1/hospitals", json=HOSPITAL, headers=admin_headers)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "HOSPITAL_ALREADY_EXISTS"


class TestReadHospital:
    async def test_list_is_public(self, client: AsyncClient, hospital):
        response = await client.get("/api/v1/hospitals")
        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [hospital["id"]]

    async def test_get_is_public(self, client: AsyncClient, hospital):
        response = await client.get(f"/api/v1/hospitals/{hospital['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == hospital["name"]

    async def test_unknown_hospital_not_found(self, client: AsyncClient, hospital):
        response = await client.get("/api/v1/hospitals/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "HOSPITAL_NOT_FOUND"


class TestUpdateHospital:
    async def test_partial_update(self, client: AsyncClient, admin_headers, hospital):
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}",
            json={"address": "2 New Street"},
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["address"] == "2 New Street"
        assert body["name"] == hospital["name"]
        assert body["phone"] == hospital["phone"]

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers, hospital):
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}",
            json={"name": "Renamed"},
            headers=staff_headers,
        )
        assert response.status_code == 403

    async def test_unknown_hospital_not_found(self, client: AsyncClient, admin_headers, hospital):
        response = await client.put(
            "/api/v1/hospitals/00000000-0000-0000-0000-000000000000",
            json={"name": "Renamed"},
            headers=admin_headers,
        )
        assert response.status_code == 404


class TestHospitalSettings:
    async def test_get_requires_authentication(self, client: AsyncClient, hospital):
        response = await client.get(f"/api/v1/hospitals/{hospital['id']}/settings")
        assert response.status_code == 401

    async def test_defaults_are_empty(self, client: AsyncClient, admin_headers, hospital):
        response = await client.get(
            f"/api/v1/hospitals/{hospital['id']}/settings", headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json() == {
            "working_hours": None,
            "emergency_contact": None,
            "escalation_email": None,
        }

    async def test_update_and_read_back(
        self, client: AsyncClient, admin_headers, staff_headers, hospital
    ):
        payload = {"working_hours": WORKING_HOURS, "emergency_contact": "+911112223334"}
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}/settings",
            json=payload,
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text

        # Staff can read the stored settings back.
        response = await client.get(
            f"/api/v1/hospitals/{hospital['id']}/settings", headers=staff_headers
        )
        assert response.status_code == 200
        body = response.json()
        assert body["emergency_contact"] == "+911112223334"
        monday = body["working_hours"]["monday"]
        assert [slot["start"] for slot in monday] == ["09:00:00", "14:00:00"]
        assert body["working_hours"]["sunday"] == []

    async def test_staff_cannot_update(self, client: AsyncClient, staff_headers, hospital):
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}/settings",
            json={"emergency_contact": "+911112223334"},
            headers=staff_headers,
        )
        assert response.status_code == 403

    async def test_slot_end_must_be_after_start(self, client: AsyncClient, admin_headers, hospital):
        payload = {"working_hours": {"monday": [{"start": "10:00", "end": "09:00"}]}}
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}/settings",
            json=payload,
            headers=admin_headers,
        )
        assert response.status_code == 422

    async def test_overlapping_slots_rejected(self, client: AsyncClient, admin_headers, hospital):
        payload = {
            "working_hours": {
                "monday": [
                    {"start": "09:00", "end": "13:00"},
                    {"start": "12:00", "end": "17:00"},
                ]
            }
        }
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}/settings",
            json=payload,
            headers=admin_headers,
        )
        assert response.status_code == 422

    async def test_unknown_settings_keys_rejected(
        self, client: AsyncClient, admin_headers, hospital
    ):
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}/settings",
            json={"unexpected": "value"},
            headers=admin_headers,
        )
        assert response.status_code == 422
