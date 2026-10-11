import uuid

import pytest

from models import Item
from schemas import ItemPublic


def test_create_item_success(regular_user, item_service, item_cleanup):
    title = f"My Unique{uuid.uuid4().hex[:6]}Title"
    description = "Created from API test"
    response = item_service.create_item(
        token=regular_user["token"],
        title=title,
        description=description,
    )
    assert response.status_code in (200, 201), response.text
    payload = response.json()
    item_cleanup(payload["id"], regular_user["token"])
    item = ItemPublic.model_validate(payload)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == regular_user["id"]


@pytest.mark.parametrize(
    ["title", "expected_status", "type_error"],
    [
        ("", 422, "string_too_short"),
        ("A" * 300, 422, "string_too_long"),
    ],
)
def test_create_item_negative_validation(
    regular_user, item_service, item_cleanup, title, expected_status, type_error
):
    response = item_service.create_item(token=regular_user["token"], title=title)
    if response.status_code in (200, 201):
        item_cleanup(response.json()["id"], regular_user["token"])
    assert response.status_code == expected_status
    assert response.json()["detail"][0]["type"] == type_error


def test_create_item_validation(regular_user, item_service, item_cleanup):
    title = "Valid title"
    description = "Valid description"
    response = item_service.create_item(
        token=regular_user["token"],
        title=title,
        description=description,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    item_cleanup(payload["id"], regular_user["token"])
    item = ItemPublic.model_validate(payload)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == regular_user["id"]


def test_update_item_and_verify_in_db(regular_user, item_service, test_item, db_session):
    updated_item = item_service.update_item(
        item_id=test_item["id"],
        token=regular_user["token"],
        title="Updated Title",
        description="Updated Description",
    )
    assert updated_item.status_code == 200, updated_item.text
    db_item = db_session.query(Item).filter(Item.id == test_item["id"]).first()
    assert db_item is not None
    assert db_item.title == "Updated Title"
    assert db_item.description == "Updated Description"


def test_delete_item(regular_user, item_service, test_item):
    item_id = test_item["id"]
    del_resp = item_service.delete_item(item_id=item_id, token=regular_user["token"])
    # Удаление только что созданного item обязано вернуть 200.
    # 404 означал бы, что записи уже не было, и тест это проглотил бы.
    assert del_resp.status_code == 200, del_resp.text

    get_resp = item_service.get_item(item_id=item_id, token=regular_user["token"])
    assert get_resp.status_code == 404, get_resp.text
