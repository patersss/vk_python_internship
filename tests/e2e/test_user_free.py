from httpx import AsyncClient


class TestUserFree:
    async def test_free_unlocks_users(self, client: AsyncClient, test_user: dict):
        resp_create_user = await client.post("/api/v1/users", json=test_user)
        assert resp_create_user.status_code == 201

        resp_locked_user = await client.post("/api/v1/users/lock")
        assert resp_locked_user.status_code == 200

        resp_freed_user = await client.post("/api/v1/users/free")

        assert resp_freed_user.status_code == 200
        assert "1" in resp_freed_user.json()["detail"]

    async def test_free_empty_db(self, client: AsyncClient):
        resp_freed_zero = await client.post("/api/v1/users/free")

        assert resp_freed_zero.status_code == 200
        assert "0" in resp_freed_zero.json()["detail"]

    async def test_free_idempotent(self, client: AsyncClient, test_user: dict):
        resp_created_user = await client.post("/api/v1/users", json=test_user)
        assert resp_created_user.status_code == 201

        rest_locked_user = await client.post("/api/v1/users/lock")
        assert rest_locked_user.status_code == 200

        resp_freed_user = await client.post("/api/v1/users/free")
        assert resp_freed_user.status_code == 200

        resp_second_free = await client.post("/api/v1/users/free")

        assert resp_second_free.status_code == 200
        assert "0" in resp_second_free.json()["detail"]