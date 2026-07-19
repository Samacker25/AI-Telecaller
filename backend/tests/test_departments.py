"""Tests for department CRUD."""

import pytest
from httpx import AsyncClient

CARDIOLOGY = {"name": "Cardiology", "description": "Heart care"}


@pytest.fixture
async def department(client: AsyncClient, admin_headers, hospital) -> dict:
    response = await client.post("/api/v1/departments", json=CARDIOLOGY, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response.json()


class TestCreateDepartment:
    async def test_requires_authentication(self, client: AsyncClient):
        response = await client.post("/api/v1/departments", json=CARDIOLOGY)
        assert response.status_code == 401

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers):
        response = await client.post("/api/v1/departments", json=CARDIOLOGY, headers=staff_headers)
        assert response.status_code == 403

    async def test_requires_hospital_profile(self, client: AsyncClient, admin_headers):
        response = await client.post("/api/v1/departments", json=CARDIOLOGY, headers=admin_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "HOSPITAL_NOT_CONFIGURED"

    async def test_admin_creates_department(self, client: AsyncClient, admin_headers, hospital):
        response = await client.post("/api/v1/departments", json=CARDIOLOGY, headers=admin_headers)
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["name"] == "Cardiology"
        assert body["hospital_id"] == hospital["id"]

    async def test_duplicate_name_conflicts_case_insensitive(
        self, client: AsyncClient, admin_headers, department
    ):
        response = await client.post(
            "/api/v1/departments", json={"name": "cardiology"}, headers=admin_headers
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "DEPARTMENT_ALREADY_EXISTS"


class TestReadDepartment:
    async def test_list_is_public(self, client: AsyncClient, department):
        response = await client.get("/api/v1/departments")
        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [department["id"]]

    async def test_get_is_public(self, client: AsyncClient, department):
        response = await client.get(f"/api/v1/departments/{department['id']}")
        assert response.status_code == 200
        assert response.json()["description"] == "Heart care"

    async def test_unknown_department_not_found(self, client: AsyncClient, department):
        response = await client.get("/api/v1/departments/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


class TestUpdateDepartment:
    async def test_partial_update(self, client: AsyncClient, admin_headers, department):
        response = await client.put(
            f"/api/v1/departments/{department['id']}",
            json={"description": "Cardiac care and surgery"},
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["description"] == "Cardiac care and surgery"
        assert body["name"] == "Cardiology"

    async def test_rename_to_existing_name_conflicts(
        self, client: AsyncClient, admin_headers, department
    ):
        await client.post("/api/v1/departments", json={"name": "Neurology"}, headers=admin_headers)
        response = await client.put(
            f"/api/v1/departments/{department['id']}",
            json={"name": "Neurology"},
            headers=admin_headers,
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "DEPARTMENT_ALREADY_EXISTS"

    async def test_rename_changing_only_case_is_allowed(
        self, client: AsyncClient, admin_headers, department
    ):
        response = await client.put(
            f"/api/v1/departments/{department['id']}",
            json={"name": "CARDIOLOGY"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "CARDIOLOGY"

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers, department):
        response = await client.put(
            f"/api/v1/departments/{department['id']}",
            json={"name": "Renamed"},
            headers=staff_headers,
        )
        assert response.status_code == 403


class TestDeleteDepartment:
    async def test_delete(self, client: AsyncClient, admin_headers, department):
        response = await client.delete(
            f"/api/v1/departments/{department['id']}", headers=admin_headers
        )
        assert response.status_code == 204
        response = await client.get(f"/api/v1/departments/{department['id']}")
        assert response.status_code == 404

    async def test_delete_with_doctors_conflicts(
        self, client: AsyncClient, admin_headers, department
    ):
        response = await client.post(
            "/api/v1/doctors",
            json={
                "department_id": department["id"],
                "name": "Dr. Asha Rao",
                "specialization": "Cardiologist",
            },
            headers=admin_headers,
        )
        assert response.status_code == 201, response.text

        response = await client.delete(
            f"/api/v1/departments/{department['id']}", headers=admin_headers
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "DEPARTMENT_HAS_DOCTORS"

    async def test_staff_forbidden(self, client: AsyncClient, staff_headers, department):
        response = await client.delete(
            f"/api/v1/departments/{department['id']}", headers=staff_headers
        )
        assert response.status_code == 403
