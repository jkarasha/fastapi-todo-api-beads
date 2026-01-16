from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/register",
            json={"email": "new@example.com", "password": "securepass123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={"email": "dupe@example.com", "password": "securepass123"},
        )
        response = await client.post(
            "/auth/register",
            json={"email": "dupe@example.com", "password": "anotherpass123"},
        )
        assert response.status_code == 409
        assert response.json()["code"] == "EMAIL_EXISTS"

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "securepass123"},
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/register",
            json={"email": "short@example.com", "password": "123"},
        )
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={"email": "login@example.com", "password": "securepass123"},
        )
        response = await client.post(
            "/auth/login",
            json={"email": "login@example.com", "password": "securepass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={"email": "wrong@example.com", "password": "securepass123"},
        )
        response = await client.post(
            "/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_CREDENTIALS"

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": "ghost@example.com", "password": "securepass123"},
        )
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_CREDENTIALS"


class TestMe:
    async def test_get_me_authenticated(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        response = await client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    async def test_get_me_no_token(self, client: AsyncClient) -> None:
        response = await client.get("/auth/me")
        assert response.status_code == 401
        assert response.json()["code"] == "NOT_AUTHENTICATED"

    async def test_get_me_invalid_token(self, client: AsyncClient) -> None:
        response = await client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_TOKEN"
