from httpx import AsyncClient


class TestUserCreation:
    async def test_user_creation(self, client: AsyncClient, test_user: dict):
        response = await client.post("/api/v1/users", json=test_user)

        assert response.status_code == 201

        response_body = response.json()
        assert response_body["login"] == test_user["login"]
        assert response_body["env"] == test_user["env"]
        assert response_body["domain"] == test_user["domain"]
        assert response_body["project_id"] == test_user["project_id"]
        assert response_body["locktime"] is None

        assert "created_at" in response_body

    async def test_user_creation_with_conflict_login(self, client: AsyncClient, test_user: dict):
        first_user_response = await client.post("/api/v1/users", json=test_user)
        assert first_user_response.status_code == 201

        second_user_response = await client.post("/api/v1/users", json=test_user)
        assert second_user_response.status_code == 409

        all_saved_users = await client.get("/api/v1/users")
        assert all_saved_users.status_code == 200

        list_of_all_users = all_saved_users.json()
        assert list_of_all_users[0]["login"] == test_user["login"]
        assert len(list_of_all_users) == 1

    async def test_user_creation_with_wrong_login(self, client: AsyncClient, test_user: dict):
        test_user["login"] = "not_a_email@"
        response = await client.post("/api/v1/users", json=test_user)
        assert response.status_code == 422

        all_saved_users = await client.get("/api/v1/users")
        assert all_saved_users.status_code == 200

        list_of_all_users = all_saved_users.json()
        assert len(list_of_all_users) == 0

    async def test_user_creation_with_missing_field(self, client: AsyncClient):
        invalid_user = {"login": "test@mail.ru", "password": "47721"}
        response = await client.post("/api/v1/users", json=invalid_user)
        assert response.status_code == 422

        all_saved_users = await client.get("/api/v1/users")
        assert all_saved_users.status_code == 200

        list_of_all_users = all_saved_users.json()
        assert len(list_of_all_users) == 0