from httpx import AsyncClient


class TestUserLock:
    async def test_lock_returns_credentials(self, client: AsyncClient, test_user: dict):
        resp_create_user = await client.post("/api/v1/users", json=test_user)
        assert resp_create_user.status_code == 201

        resp_locked_user = await client.post("/api/v1/users/lock")

        assert resp_locked_user.status_code == 200
        user_body = resp_locked_user.json()
        assert user_body["login"] == test_user["login"]
        assert user_body["password"] == test_user["password"]
        assert user_body["locktime"] is not None

    async def test_lock_with_no_users(self, client: AsyncClient):
        response = await client.post("/api/v1/users/lock")

        assert response.status_code == 404

    async def test_lock_with_all_blocked_users(self, client: AsyncClient, test_user: dict):
        resp_create_user = await client.post("/api/v1/users", json=test_user)
        assert resp_create_user.status_code == 201

        resp_locked_user = await client.post("/api/v1/users/lock")
        assert resp_locked_user.status_code == 200

        response = await client.post("/api/v1/users/lock")

        assert response.status_code == 404

    async def test_two_users_locked_sequentially(self, client: AsyncClient, test_user: dict):
        payload2 = {**test_user, "login": "test222@mail.ru"}
        resp_first_create_user = await client.post("/api/v1/users", json=test_user)
        assert resp_first_create_user.status_code == 201

        resp_second_created_user = await client.post("/api/v1/users", json=payload2)
        assert resp_second_created_user.status_code == 201

        resp_first_user = await client.post("/api/v1/users/lock")
        resp_second_user = await client.post("/api/v1/users/lock")

        assert resp_first_user.status_code == 200
        assert resp_second_user.status_code == 200
        assert resp_first_user.json()["login"] != resp_second_user.json()["login"]

    async def test_lock_after_free(self, client: AsyncClient, test_user: dict):
        resp_create_user = await client.post("/api/v1/users", json=test_user)
        assert resp_create_user.status_code == 201

        res_locked_user = await client.post("/api/v1/users/lock")
        assert res_locked_user.status_code == 200
        body_locked_user = res_locked_user.json()
        assert body_locked_user["locktime"] is not None

        resp_free_user = await client.post("/api/v1/users/free")
        assert resp_free_user.status_code == 200

        resp_all_users = await client.get("/api/v1/users")
        assert resp_all_users.status_code == 200
        body_all_users = resp_all_users.json()
        assert body_all_users[0]["locktime"] is None

        resp_locked_second = await client.post("/api/v1/users/lock")

        assert resp_locked_second.status_code == 200
        assert resp_locked_second.json()["login"] == test_user["login"]