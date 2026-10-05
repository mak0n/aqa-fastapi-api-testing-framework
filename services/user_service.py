import secrets
import uuid

from requests import Response

from utils.api_client import BaseApiClient
from utils.custom_faker import fake


class UserService:
    def __init__(self, client: BaseApiClient):
        self.client = client

    def signup(self,
               email: str | None = None,
               password: str | None = None,
               full_name: str | None = None,
               **kwargs) -> Response:
        if email is None:
            email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        if password is None:
            password = secrets.token_hex(8)
        if full_name is None:
            full_name = fake.name()
        payload = {"email": email, "password": password, "full_name": full_name}
        return self.client.post(
            "/api/v1/users/signup",
            json=payload,
            **kwargs
        )

    def login(self, email: str, password: str) -> Response:
        return self.client.post(
            "/api/v1/login/access-token",
            data={"username": email, "password": password}
        )

    def get_me(self, token: str | None = None, headers: dict | None = None, **kwargs) -> Response:
        return self.client.get("/api/v1/users/me", token=token, headers=headers, **kwargs)

    def get_users(self, token: str | None = None, headers: dict | None = None, params: dict | None = None,
                  **kwargs) -> Response:
        return self.client.get("/api/v1/users/", token=token, headers=headers, params=params, **kwargs)

    def delete_user(self, user_id: str, token: str | None = None, headers: dict | None = None, **kwargs) -> Response:
        return self.client.delete(f"/api/v1/users/{user_id}", token=token, headers=headers, **kwargs)