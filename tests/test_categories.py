from httpx import AsyncClient


class TestCreateCategory:
    async def test_create_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/categories",
            json={"name": "Work"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Work"
        assert "id" in data
        assert "created_at" in data

    async def test_create_duplicate_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        await client.post("/categories", json={"name": "Work"}, headers=auth_headers)
        response = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        assert response.status_code == 409
        assert response.json()["code"] == "CATEGORY_EXISTS"

    async def test_create_category_empty_name(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/categories", json={"name": ""}, headers=auth_headers
        )
        assert response.status_code == 422

    async def test_same_name_different_users(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
    ) -> None:
        response1 = await client.post(
            "/categories", json={"name": "Shared"}, headers=auth_headers
        )
        response2 = await client.post(
            "/categories", json={"name": "Shared"}, headers=second_user_headers
        )
        assert response1.status_code == 201
        assert response2.status_code == 201


class TestListCategories:
    async def test_list_categories(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        await client.post("/categories", json={"name": "Work"}, headers=auth_headers)
        await client.post(
            "/categories", json={"name": "Personal"}, headers=auth_headers
        )

        response = await client.get("/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [c["name"] for c in data]
        assert "Work" in names
        assert "Personal" in names

    async def test_list_categories_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.get("/categories", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_categories_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
    ) -> None:
        await client.post("/categories", json={"name": "User1"}, headers=auth_headers)
        await client.post(
            "/categories", json={"name": "User2"}, headers=second_user_headers
        )

        response = await client.get("/categories", headers=auth_headers)
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "User1"


class TestGetCategory:
    async def test_get_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = create_resp.json()["id"]

        response = await client.get(
            f"/categories/{category_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Work"

    async def test_get_category_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.get("/categories/999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["code"] == "CATEGORY_NOT_FOUND"

    async def test_get_other_users_category(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
    ) -> None:
        create_resp = await client.post(
            "/categories", json={"name": "Private"}, headers=auth_headers
        )
        category_id = create_resp.json()["id"]

        response = await client.get(
            f"/categories/{category_id}", headers=second_user_headers
        )
        assert response.status_code == 404


class TestUpdateCategory:
    async def test_update_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = create_resp.json()["id"]

        response = await client.patch(
            f"/categories/{category_id}",
            json={"name": "Office"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Office"

    async def test_update_to_duplicate_name(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        await client.post("/categories", json={"name": "Work"}, headers=auth_headers)
        create_resp = await client.post(
            "/categories", json={"name": "Personal"}, headers=auth_headers
        )
        category_id = create_resp.json()["id"]

        response = await client.patch(
            f"/categories/{category_id}",
            json={"name": "Work"},
            headers=auth_headers,
        )
        assert response.status_code == 409


class TestDeleteCategory:
    async def test_delete_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = create_resp.json()["id"]

        response = await client.delete(
            f"/categories/{category_id}", headers=auth_headers
        )
        assert response.status_code == 204

        get_response = await client.get(
            f"/categories/{category_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    async def test_delete_nonexistent_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.delete("/categories/999", headers=auth_headers)
        assert response.status_code == 404
