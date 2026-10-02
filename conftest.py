import pytest
import requests
import psycopg2
import uuid

@pytest.fixture(scope="session")
def base_url():
    return "https://localhost:8000"

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

@pytest.fixture
def admin_user(base_url):
    # ТВОЯ ЗАДАЧА: Создай админа
    # 1. Signup с уникальным email
    # 2. Сделай is_superuser=True (через БД или отдельный endpoint)
    # 3. Login
    # 4. Верни {"email": ..., "token": ..., "headers": {...}}
    pass

@pytest.fixture
def regular_user(base_url):
    # ТВОЯ ЗАДАЧА: Создай обычного пользователя
    pass

@pytest.fixture
def guest():
    return {"email": None, "token": None, "headers": {}}

@pytest.fixture
def test_item(regular_user, base_url):
    # ТВОЯ ЗАДАЧА: Создай item + cleanup
    pass