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

def regular_user(user_service):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    signup_res = user_service.signup(email=email, password=password)
    assert signup_res.status_code in (200, 201)
    user_id = signup_res.json()["id"]

    login_res = user_service.login(email=email, password=password)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    yield {
        "id": user_id,
        "email": email,
        "password": password,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def admin_user(user_service):
    login_res = user_service.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    yield {
        "id": None,
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def guest():
    return {
        "id": None,
        "email": None,
        "password": None,
        "token": None,
        "headers": {}
    }

@pytest.fixture
def test_item(regular_user, item_service):
    item_title = f"Test_item_{uuid.uuid4().hex[:8]}"
    create_resp = item_service.create_item(
        token=regular_user["token"],
        title=item_title,
    )
    assert create_resp.status_code in (201, 200)
    item_data = create_resp.json()

    yield item_data

    item_service.delete_item(item_id=item_data["id"], token=regular_user["token"])


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
