"""Tests for doctor CRUD, filters, and OPD schedule validation."""

import pytest
from httpx import AsyncClient

OPD_SCHEDULE = {"monday": [{"start": "09:00", "end": "12:00"}]}


@pytest.fixture
async def department(client: AsyncClient, admin_headers, hospital) -> dict:
    response = await client.post(
        "/api/v1/departments", json={"name": "Cardiology"}, headers=admin_headers
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
async def doctor(client: AsyncClient, admin_headers, department) -> dict:
    response = await client.post(
        "/api/v1/doctors",
        json={
            "department_id": department["id"],
            "name": "Dr. Asha Rao",
            "specialization": "Cardiologist",
            "qualification": "MD, DM",
            "opd_schedule": OPD_SCHEDULE,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestCreateDoctor:
    async def test_requires_authentication(self, client: AsyncClient, department):
        response = await client.post(
            "/api/v1/doctors",
            json={"department_id": department["id"], "name": "Dr. X", "specialization": "GP"},
        )
        assert response.status_code == 401

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers, department):
        response = await client.post(
            "/api/v1/doctors",
            json={"department_id": department["id"], "name": "Dr. X", "specialization": "GP"},
            headers=staff_headers,
        )
        assert response.status_code == 403

    async def test_admin_creates_doctor(self, client: AsyncClient, hospital, doctor):
        assert doctor["name"] == "Dr. Asha Rao"
        assert doctor["hospital_id"] == hospital["id"]
        assert doctor["is_available"] is True
        assert [slot["start"] for slot in doctor["opd_schedule"]["monday"]] == ["09:00:00"]

    async def test_unknown_department_not_found(self, client: AsyncClient, admin_headers, hospital):
        response = await client.post(
            "/api/v1/doctors",
            json={
                "department_id": "00000000-0000-0000-0000-000000000000",
                "name": "Dr. X",
                "specialization": "GP",
            },
            headers=admin_headers,
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"

    async def test_invalid_schedule_rejected(self, client: AsyncClient, admin_headers, department):
        response = await client.post(
            "/api/v1/doctors",
            json={
                "department_id": department["id"],
                "name": "Dr. X",
                "specialization": "GP",
                "opd_schedule": {"monday": [{"start": "12:00", "end": "09:00"}]},
            },
            headers=admin_headers,
        )
        assert response.status_code == 422


class TestReadDoctors:
    async def test_list_is_public(self, client: AsyncClient, doctor):
        response = await client.get("/api/v1/doctors")
        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [doctor["id"]]

    async def test_get_is_public(self, client: AsyncClient, doctor):
        response = await client.get(f"/api/v1/doctors/{doctor['id']}")
        assert response.status_code == 200
        assert response.json()["qualification"] == "MD, DM"

    async def test_unknown_doctor_not_found(self, client: AsyncClient, doctor):
        response = await client.get("/api/v1/doctors/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "DOCTOR_NOT_FOUND"

    async def test_filter_by_department(self, client: AsyncClient, admin_headers, doctor):
        other = await client.post(
            "/api/v1/departments", json={"name": "Neurology"}, headers=admin_headers
        )
        await client.post(
            "/api/v1/doctors",
            json={
                "department_id": other.json()["id"],
                "name": "Dr. Neuro",
                "specialization": "Neurologist",
            },
            headers=admin_headers,
        )

        response = await client.get(
            "/api/v1/doctors", params={"department_id": doctor["department_id"]}
        )
        assert [item["id"] for item in response.json()] == [doctor["id"]]

    async def test_filter_by_specialization_case_insensitive(self, client: AsyncClient, doctor):
        response = await client.get("/api/v1/doctors", params={"specialization": "cardiologist"})
        assert [item["id"] for item in response.json()] == [doctor["id"]]

        response = await client.get("/api/v1/doctors", params={"specialization": "dermatologist"})
        assert response.json() == []

    async def test_filter_by_availability(self, client: AsyncClient, admin_headers, doctor):
        await client.put(
            f"/api/v1/doctors/{doctor['id']}",
            json={"is_available": False},
            headers=admin_headers,
        )
        response = await client.get("/api/v1/doctors", params={"available": True})
        assert response.json() == []
        response = await client.get("/api/v1/doctors", params={"available": False})
        assert [item["id"] for item in response.json()] == [doctor["id"]]


class TestUpdateDoctor:
    async def test_partial_update(self, client: AsyncClient, admin_headers, doctor):
        response = await client.put(
            f"/api/v1/doctors/{doctor['id']}",
            json={"is_available": False},
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["is_available"] is False
        assert body["name"] == doctor["name"]
        assert body["opd_schedule"] == doctor["opd_schedule"]

    async def test_move_to_another_department(self, client: AsyncClient, admin_headers, doctor):
        other = await client.post(
            "/api/v1/departments", json={"name": "Neurology"}, headers=admin_headers
        )
        response = await client.put(
            f"/api/v1/doctors/{doctor['id']}",
            json={"department_id": other.json()["id"]},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["department_id"] == other.json()["id"]

    async def test_move_to_unknown_department_not_found(
        self, client: AsyncClient, admin_headers, doctor
    ):
        response = await client.put(
            f"/api/v1/doctors/{doctor['id']}",
            json={"department_id": "00000000-0000-0000-0000-000000000000"},
            headers=admin_headers,
        )
        assert response.status_code == 404

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers, doctor):
        response = await client.put(
            f"/api/v1/doctors/{doctor['id']}",
            json={"is_available": False},
            headers=staff_headers,
        )
        assert response.status_code == 403


class TestDeleteDoctor:
    async def test_delete(self, client: AsyncClient, admin_headers, doctor):
        response = await client.delete(f"/api/v1/doctors/{doctor['id']}", headers=admin_headers)
        assert response.status_code == 204
        response = await client.get(f"/api/v1/doctors/{doctor['id']}")
        assert response.status_code == 404

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers, doctor):
        response = await client.delete(f"/api/v1/doctors/{doctor['id']}", headers=staff_headers)
        assert response.status_code == 403
