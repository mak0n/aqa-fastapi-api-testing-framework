import secrets
import uuid

import pytest


@pytest.mark.parametrize(
    ["role_fixture", "expected_status"],
    [
        ("admin_user", 200),
        ("regular_user", 403),
        ("guest", 401),
    ],
    ids=[
        "admin",
        "regular",
        "guest",
    ],
)
def test_get_all_users_access(role_fixture, expected_status, request, user_service):
    user = request.getfixturevalue(role_fixture)
    response = user_service.get_users(token=user["token"])
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ["role_fixture", "expected_status"],
    [
        ("admin_user", 200),
        ("regular_user", 403),
        ("guest", 401),
    ],
    ids=[
        "admin",
        "regular",
        "guest",
    ],
)
def test_delete_user(role_fixture, expected_status, request, user_service, user_cleanup):
    resp = user_service.signup()
    assert resp.status_code in (200, 201), resp.text
    victim_id = user_cleanup(resp.json()["id"])
    user = request.getfixturevalue(role_fixture)
    delete_resp = user_service.delete_user(user_id=victim_id, token=user["token"])
    assert delete_resp.status_code == expected_status, delete_resp.text


def test_item_ownership(regular_user, user_service, item_service, user_cleanup, item_cleanup):
    user_b_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user_b_password = secrets.token_hex(8)
    signup = user_service.signup(email=user_b_email, password=user_b_password)
    assert signup.status_code in (200, 201), signup.text
    user_cleanup(signup.json()["id"])

    user_b_login = user_service.login(email=user_b_email, password=user_b_password)
    assert user_b_login.status_code == 200, user_b_login.text

    item = item_service.create_item(token=regular_user["token"])
    assert item.status_code in (200, 201), item.text
    item_id = item_cleanup(item.json()["id"], regular_user["token"])

    response = item_service.update_item(
        item_id=item_id,
        token=user_b_login.json()["access_token"],
        title="New title",
    )
    assert response.status_code == 400, response.text
