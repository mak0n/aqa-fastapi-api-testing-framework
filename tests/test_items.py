import uuid

import pytest

from models import Item
from schemas import ItemPublic


def test_create_item_success(regular_user, item_service):
    item = item_service.create_item(token=regular_user["token"],
                             title=f"My Unique{uuid.uuid4().hex[:6]}Title")
    assert item.status_code in (200, 201)
    ItemPublic.model_validate(item.json())
    item_service.delete_item(item_id=item.json()["id"],
                             token=regular_user["token"])

@pytest.mark.parametrize(
    ["title", "expected_status", "type_error"],
    [
        ("", 422, "string_too_short"),
        ("A"*300, 422, "string_too_long"),
    ]
)
def test_create_item_negative_validation(regular_user, item_service, title, expected_status, type_error):
    item = item_service.create_item(token=regular_user["token"],
                                    title=title)
    assert item.status_code == expected_status
    assert item.json()["detail"][0]["type"] == type_error


def test_create_item_validation(regular_user, item_service):
    item = item_service.create_item(token=regular_user["token"],
                                    title="Valid title")
    assert item.status_code == 200
    del_resp = item_service.delete_item(item_id=item.json()["id"],
                                 token=regular_user["token"])
    assert del_resp.status_code in (200, 404)


def test_update_item_and_verify_in_db(regular_user, item_service, test_item, db_session):
    item = item_service.create_item(token=regular_user["token"],
                             title=f"My Unique{uuid.uuid4().hex[:6]}Title")
    updated_item = item_service.update_item(item_id=item.json()["id"],
                                            token=regular_user["token"],
                                            title="Updated Title",
                                            description="Updated Description")
    assert updated_item.status_code == 200
    db_item = db_session.query(Item).filter(Item.id == item.json()["id"]).first()
    # or db_session.scalars(select(Item).where(Item.id == item.json()["id"])).first()
    assert db_item is not None
    assert db_item.title == "Updated Title"
    assert db_item.description == "Updated Description"


def test_delete_item(regular_user, item_service, test_item):
    del_resp = item_service.delete_item(item_id=test_item["id"],
                                        token=regular_user["token"])
    assert del_resp.status_code == 200


