import secrets
import uuid

import pytest


@pytest.mark.parametrize(
    ["role_fixture", "expected_status"],
    [
        ("admin_user", 200),
        ("regular_user", 403),
        ("guest", 401)
    ],
    ids=[
        "admin",
        "regular",
        "guest"
    ])
def test_get_all_users_access(role_fixture, expected_status, request, user_service):
    user = request.getfixturevalue(role_fixture)
    response = user_service.get_users(token=user["token"])
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ["role_fixture", "expected_status"],
    [
        ("admin_user", 200),
        ("regular_user", 403),
        ("guest", 401)
    ],
    ids=[
        "admin",
        "regular",
        "guest"
    ]
)
def test_delete_user(role_fixture, expected_status, request, user_service):
    resp = user_service.signup()
    assert resp.status_code in (200, 201)
    victim_id = resp.json()["id"]
    user = request.getfixturevalue(role_fixture)
    delete_resp = user_service.delete_user(user_id=victim_id, token=user["token"])
    assert delete_resp.status_code == expected_status


def test_item_ownership(regular_user, user_service, item_service):
    user_a = regular_user
    user_b_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user_b_password = secrets.token_hex(8)
    user_service.signup(email=user_b_email, password=user_b_password)
    user_b_login = user_service.login(email=user_b_email, password=user_b_password)
    item = item_service.create_item(token=user_a["token"])
    response = item_service.update_item(item_id=item.json()["id"], token=user_b_login.json()["access_token"],
                                        title="New title")
    assert response.status_code == 400

    item_service.delete_item(item_id=item.json()["id"], token=user_a["token"])
