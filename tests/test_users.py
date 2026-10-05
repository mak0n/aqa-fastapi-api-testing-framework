import secrets
import uuid

from pydantic import BaseModel
from sqlalchemy import select

from conftest import item_service
from models import User, Item
from schemas import UserPublic
from utils.custom_faker import fake
from utils.retry_helpers import get_user_with_retry


def test_success_signup_user_in_db(user_service, db_session):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = secrets.token_hex(8)
    full_name = fake.name()
    sign_resp = user_service.signup(email=email,
                                    password=password,
                                    full_name=full_name)
    assert sign_resp.status_code == 200
    user_db = db_session.scalars(select(User).where(User.email == email)).first()
    assert user_db is not None
    assert user_db.email == email # Стоит ли такое писать? Если в бд был запрос User.email == email
    assert user_db.full_name == full_name
    assert user_db.is_active == True


def test_read_user_authorized(regular_user, user_service, db_session):
    get_resp = user_service.get_me(token=regular_user["token"])
    assert get_resp.status_code == 200
    user = db_session.scalars(select(User).where(User.email == regular_user["email"])).first()
    UserPublic.model_validate(get_resp.json())
    assert user.email == regular_user["email"]


def test_cascade_verification(regular_user, admin_user, user_service, item_service, db_session):
    items_list = [item_service.create_item(token=regular_user["token"]) for _ in range(2)]
    user = db_session.scalars(select(User).where(User.email == regular_user["email"])).first()
    items = db_session.scalars(select(Item).where(Item.owner_id == user.id)).all()
    assert len(items) == len(items_list)
    db_item_ids = [str(item.id) for item in items]
    assert items_list[0].json()["id"] in db_item_ids
    assert items_list[1].json()["id"] in db_item_ids

    delete_resp = user_service.delete_user(user_id=regular_user["id"],
                                           token=admin_user["token"])
    assert delete_resp.status_code == 200
    user_after_delete = db_session.scalars(select(User).where(User.email == regular_user["email"])).first()
    assert user_after_delete is None
    items_after_delete = db_session.scalars(select(Item).where(Item.owner_id == user.id)).all()
    assert not items_after_delete


def test_get_user(regular_user, user_service):
   resp = get_user_with_retry(user_service, regular_user["token"])
   assert regular_user["email"] == resp.json()["email"]