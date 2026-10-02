import pytest
import psycopg2
import uuid

from constants import  ADMIN_EMAIL, ADMIN_PASSWORD
from services.item_service import ItemService
from services.user_service import UserService
from utils.api_client import BaseApiClient


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8000"

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
def regular_user(user_service):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    signup_res = user_service.signup(email=email, password=password)
    assert signup_res.status_code in (200, 201)
    login_res = user_service.login(email=email, password=password)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    yield signup_res, token
    user_service.delete_user(user_id=login_res.json()["id"], token=token)

@pytest.fixture
def admin_user(user_service):
    # ТВОЯ ЗАДАЧА: Создай админа
    # 1. Signup с уникальным email
    # 2. Сделай is_superuser=True (через БД или отдельный endpoint)
    # 3. Login
    # 4. Верни {"email": ..., "token": ..., "headers": {...}}
    login_res = user_service.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert login_res.status_code == 200
    yield {"email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "headers": {"Authorization": f"Bearer {login_res.json()['access_token']}"}}


@pytest.fixture
def guest():
    return {"email": None, "token": None, "headers": {}}

@pytest.fixture
def test_item(regular_user, base_url):
    # ТВОЯ ЗАДАЧА: Создай item + cleanup
    pass

@pytest.fixture(scope="session")
def db_connection():
    connection = psycopg2.connect(
        host="45.145.65.134",
        port=5432,
        database="app",
        user="postgres",
        password="usfHO8BAY5"
    )
    yield connection
    connection.close()
