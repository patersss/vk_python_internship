from httpx import AsyncClient


class TestGetUser:
    async def test_empty_list(self, client: AsyncClient):
        resp_zero_users = await client.get("/api/v1/users")

        assert resp_zero_users.status_code == 200
        assert resp_zero_users.json() == []

    async def test_returns_created_users(self, client: AsyncClient, test_user: dict):
        resp_created_user = await client.post("/api/v1/users", json=test_user)
        assert resp_created_user.status_code == 201

        resp_all_users = await client.get("/api/v1/users")

        users = resp_all_users.json()
        assert len(users) == 1
        assert users[0]["login"] == test_user["login"]
        assert "password" not in users[0]