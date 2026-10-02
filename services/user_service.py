import secrets
import uuid

from requests import Response

from utils.api_client import BaseApiClient
from utils.custom_faker import fake


class UserService:
    def __init__(self, client: BaseApiClient):
        self.client = client

    def _get_headers(self, token: str | None = None, headers: dict| None = None) -> dict:
        if headers:
            return headers
        else:
            return {"Authorization": f"Bearer {token}"}

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
        return self.client.post("api/v1/signup",
                                json={"email": email,
                                      "password": password,
                                      "full_name": full_name,
                                      **kwargs}
                                )

    def get_me(self,
               token: str | None = None,
               headers: dict | None = None,
               **kwargs) -> Response:
        if headers is None:
            if token is None:
                headers = self._get_headers(token=token)
            else:
                assert headers is not None, "Ручка защищена, нужен или токен или готовый заголовок с токеном"
        return self.client.send_request(method="GET", endpoint="/api/v1/users/", headers=headers, **kwargs)
