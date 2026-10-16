import secrets
import uuid

from sqlalchemy import select

from models import Item, User
from schemas import UserPublic
from utils.custom_faker import fake
from utils.retry_helpers import get_user_with_retry


def test_success_signup_user_in_db(user_service, user_cleanup, db_session):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = secrets.token_hex(8)
    full_name = fake.name()
    sign_resp = user_service.signup(
        email=email,
        password=password,
        full_name=full_name,
    )
    assert sign_resp.status_code == 200, sign_resp.text
    user_cleanup(sign_resp.json()["id"])
    user_db = db_session.scalars(select(User).where(User.email == email)).first()
    assert user_db is not None
    assert str(user_db.id) == sign_resp.json()["id"]
    assert user_db.full_name == full_name
    assert user_db.is_active is True


def test_read_user_authorized(regular_user, user_service, db_session):
    get_resp = user_service.get_me(token=regular_user["token"])
    assert get_resp.status_code == 200, get_resp.text
    user_api = UserPublic.model_validate(get_resp.json())
    assert user_api.id == regular_user["id"]
    assert user_api.email == regular_user["email"]

    user_db = db_session.scalars(
        select(User).where(User.email == regular_user["email"])
    ).first()
    assert user_db is not None
    assert str(user_db.id) == user_api.id
    assert user_db.email == user_api.email


def test_cascade_verification(
    regular_user, admin_user, user_service, item_service, item_cleanup, db_session
):
    items_list = []
    for _ in range(2):
        response = item_service.create_item(token=regular_user["token"])
        assert response.status_code in (200, 201), response.text
        item_cleanup(response.json()["id"], regular_user["token"])
        items_list.append(response)

    user = db_session.scalars(select(User).where(User.email == regular_user["email"])).first()
    assert user is not None
    items = db_session.scalars(select(Item).where(Item.owner_id == user.id)).all()
    assert len(items) == len(items_list)
    db_item_ids = [str(item.id) for item in items]
    assert items_list[0].json()["id"] in db_item_ids
    assert items_list[1].json()["id"] in db_item_ids

    delete_resp = user_service.delete_user(
        user_id=regular_user["id"],
        token=admin_user["token"],
    )
    assert delete_resp.status_code == 200, delete_resp.text
    user_after_delete = db_session.scalars(
        select(User).where(User.email == regular_user["email"])
    ).first()
    assert user_after_delete is None
    items_after_delete = db_session.scalars(select(Item).where(Item.owner_id == user.id)).all()
    assert not items_after_delete


def test_get_user(regular_user, user_service):
    resp = get_user_with_retry(user_service, regular_user["token"])
    user = UserPublic.model_validate(resp.json())
    assert user.id == regular_user["id"]
    assert user.email == regular_user["email"]
