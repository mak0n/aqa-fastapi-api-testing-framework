import secrets
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import ADMIN_EMAIL, ADMIN_PASSWORD, BASE_URL, DATABASE_URL
from services.item_service import ItemService
from services.user_service import UserService
from utils.api_client import BaseApiClient
from utils.cleanup import cleanup_each


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="function")
def api_client(base_url):
    return BaseApiClient(base_url)


@pytest.fixture
def user_service(api_client):
    return UserService(api_client)


@pytest.fixture
def item_service(api_client):
    return ItemService(api_client)


@pytest.fixture
def admin_user(user_service):
    login_res = user_service.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert login_res.status_code == 200, login_res.text
    token = login_res.json()["access_token"]

    return {
        "id": None,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def user_cleanup(user_service, admin_user):
    """Запоминает id созданных пользователей и удаляет их после теста.

    Код после yield — teardown. Pytest выполняет его и когда тест прошёл,
    и когда упал на assert. Удаляет админ: обычный пользователь получает 403
    и не может убрать запись за собой.
    Повторный DELETE с 404 здесь нормален: тест мог уже удалить пользователя
    как проверяемое действие. В самом тесте 404 успехом удаления не считается.
    Ошибка одного id не прерывает цикл: остальные пользователи всё равно
    удаляются, а список провалов всплывает одним исключением в конце.
    """
    created_ids: list[str] = []

    def register(user_id: str) -> str:
        user_id = str(user_id)
        created_ids.append(user_id)
        return user_id

    yield register

    cleanup_each(
        created_ids,
        lambda user_id: user_service.delete_user(user_id=user_id, token=admin_user["token"]),
        lambda user_id: f"user {user_id}",
    )


@pytest.fixture
def regular_user(user_service, user_cleanup):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = secrets.token_hex(8)

    signup_res = user_service.signup(email=email, password=password)
    assert signup_res.status_code in (200, 201), signup_res.text
    user_id = user_cleanup(signup_res.json()["id"])

    login_res = user_service.login(email=email, password=password)
    assert login_res.status_code == 200, login_res.text
    token = login_res.json()["access_token"]

    return {
        "id": user_id,
        "email": email,
        "password": password,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def guest():
    return {
        "id": None,
        "email": None,
        "password": None,
        "token": None,
        "headers": {},
    }


@pytest.fixture
def item_cleanup(item_service, user_cleanup):
    """Запоминает items и удаляет их после теста.

    user_cleanup в аргументах задаёт порядок: pytest поднимает зависимости
    раньше, а сносит фикстуры в обратном порядке. Сначала исчезнут items,
    потом пользователи.
    """
    created: list[tuple[str, str]] = []

    def register(item_id: str, token: str) -> str:
        item_id = str(item_id)
        created.append((item_id, token))
        return item_id

    yield register

    cleanup_each(
        created,
        lambda item: item_service.delete_item(item_id=item[0], token=item[1]),
        lambda item: f"item {item[0]}",
    )


@pytest.fixture
def test_item(regular_user, item_service, item_cleanup):
    title = f"Test_item_{uuid.uuid4().hex[:8]}"
    description = "Fixture item description"
    create_resp = item_service.create_item(
        token=regular_user["token"],
        title=title,
        description=description,
    )
    assert create_resp.status_code in (200, 201), create_resp.text
    item_data = create_resp.json()
    item_cleanup(item_data["id"], regular_user["token"])
    return item_data


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
