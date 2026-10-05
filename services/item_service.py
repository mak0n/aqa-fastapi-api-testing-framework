import uuid

from requests import Response

from utils.api_client import BaseApiClient
from utils.custom_faker import fake


class ItemService:
    def __init__(self, client: BaseApiClient):
        self._client = client

    def create_item(self,
                    token: str | None = None,
                    title: str | None = None,
                    description: str | None = "Default description",
                    **kwargs) -> Response:
        if title is None:
            title = f"Test_item_{uuid.uuid4().hex[:8]}"
        payload = {"title": title, "description": description}
        return self._client.post("api/v1/items/", json=payload, token=token, **kwargs)

    def get_items(self,
                  token: str | None= None,
                  params: dict | None = None,
                  **kwargs) -> Response:
        return self._client.get("api/v1/items/", params=params, token=token, **kwargs)

    def get_item(self,
                  item_id: str,
                  token: str | None= None,
                  **kwargs) -> Response:
        return self._client.get(f"api/v1/items/{item_id}", token=token, **kwargs)

    def update_item(self,
                    item_id: str,
                    token: str | None = None,
                    title: str | None = None,
                    description: str | None = None,
                    **kwargs) -> Response:
        payload = {"title": title, "description": description}
        return self._client.put(f"api/v1/items/{item_id}", json=payload, token=token, **kwargs)

    def delete_item(self,
                    item_id: str,
                    token: str | None = None,
                    **kwargs) -> Response:
        return self._client.delete(f"api/v1/items/{item_id}", token=token, **kwargs)
