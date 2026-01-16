from httpx import AsyncClient


class TestCreateTodo:
    async def test_create_todo_minimal(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/todos",
            json={"title": "Buy groceries"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["status"] == "pending"
        assert data["priority"] is None
        assert data["due_date"] is None
        assert data["category_id"] is None

    async def test_create_todo_full(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        cat_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = cat_resp.json()["id"]

        response = await client.post(
            "/todos",
            json={
                "title": "Finish report",
                "description": "Q4 sales report",
                "priority": 1,
                "due_date": "2024-12-31",
                "category_id": category_id,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Finish report"
        assert data["description"] == "Q4 sales report"
        assert data["priority"] == 1
        assert data["due_date"] == "2024-12-31"
        assert data["category_id"] == category_id

    async def test_create_todo_invalid_priority(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/todos",
            json={"title": "Test", "priority": 5},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_todo_nonexistent_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/todos",
            json={"title": "Test", "category_id": 999},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["code"] == "CATEGORY_NOT_FOUND"


class TestListTodos:
    async def test_list_todos(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        await client.post("/todos", json={"title": "Todo 1"}, headers=auth_headers)
        await client.post("/todos", json={"title": "Todo 2"}, headers=auth_headers)

        response = await client.get("/todos", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_list_todos_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.get("/todos", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_filter_by_status(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        resp1 = await client.post(
            "/todos", json={"title": "Pending"}, headers=auth_headers
        )
        todo_id = resp1.json()["id"]
        await client.patch(
            f"/todos/{todo_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        await client.post("/todos", json={"title": "Also pending"}, headers=auth_headers)

        response = await client.get(
            "/todos", params={"status": "pending"}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Also pending"

    async def test_filter_by_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        cat_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = cat_resp.json()["id"]

        await client.post(
            "/todos",
            json={"title": "Work todo", "category_id": category_id},
            headers=auth_headers,
        )
        await client.post(
            "/todos", json={"title": "No category"}, headers=auth_headers
        )

        response = await client.get(
            "/todos", params={"category_id": category_id}, headers=auth_headers
        )
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Work todo"

    async def test_filter_by_priority(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        await client.post(
            "/todos", json={"title": "High", "priority": 0}, headers=auth_headers
        )
        await client.post(
            "/todos", json={"title": "Low", "priority": 4}, headers=auth_headers
        )

        response = await client.get(
            "/todos", params={"priority": 0}, headers=auth_headers
        )
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "High"

    async def test_todos_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
    ) -> None:
        await client.post("/todos", json={"title": "User1"}, headers=auth_headers)
        await client.post("/todos", json={"title": "User2"}, headers=second_user_headers)

        response = await client.get("/todos", headers=auth_headers)
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "User1"


class TestGetTodo:
    async def test_get_todo(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Test"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.get(f"/todos/{todo_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Test"

    async def test_get_todo_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.get("/todos/999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["code"] == "TODO_NOT_FOUND"

    async def test_get_other_users_todo(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Private"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.get(f"/todos/{todo_id}", headers=second_user_headers)
        assert response.status_code == 404


class TestUpdateTodo:
    async def test_update_todo_title(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Original"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.patch(
            f"/todos/{todo_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    async def test_update_todo_status_to_completed(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Task"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.patch(
            f"/todos/{todo_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    async def test_update_todo_status_back_to_pending(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Task"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        await client.patch(
            f"/todos/{todo_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        response = await client.patch(
            f"/todos/{todo_id}",
            json={"status": "pending"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["completed_at"] is None

    async def test_update_todo_category(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        cat_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = cat_resp.json()["id"]

        create_resp = await client.post(
            "/todos", json={"title": "Task"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.patch(
            f"/todos/{todo_id}",
            json={"category_id": category_id},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["category_id"] == category_id


class TestDeleteTodo:
    async def test_delete_todo(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Delete me"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.delete(f"/todos/{todo_id}", headers=auth_headers)
        assert response.status_code == 204

        get_response = await client.get(f"/todos/{todo_id}", headers=auth_headers)
        assert get_response.status_code == 404

    async def test_delete_nonexistent_todo(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.delete("/todos/999", headers=auth_headers)
        assert response.status_code == 404

    async def test_delete_other_users_todo(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
    ) -> None:
        create_resp = await client.post(
            "/todos", json={"title": "Mine"}, headers=auth_headers
        )
        todo_id = create_resp.json()["id"]

        response = await client.delete(
            f"/todos/{todo_id}", headers=second_user_headers
        )
        assert response.status_code == 404

        # Verify it wasn't deleted
        get_response = await client.get(f"/todos/{todo_id}", headers=auth_headers)
        assert get_response.status_code == 200


class TestCategoryDeletion:
    async def test_delete_category_nullifies_todos(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        cat_resp = await client.post(
            "/categories", json={"name": "Work"}, headers=auth_headers
        )
        category_id = cat_resp.json()["id"]

        todo_resp = await client.post(
            "/todos",
            json={"title": "Task", "category_id": category_id},
            headers=auth_headers,
        )
        todo_id = todo_resp.json()["id"]

        await client.delete(f"/categories/{category_id}", headers=auth_headers)

        response = await client.get(f"/todos/{todo_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["category_id"] is None
