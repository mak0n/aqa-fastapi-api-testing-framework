import secrets
import uuid

import pytest

from schemas import Token, UserPublic


def test_signup_success(user_service, user_cleanup):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = secrets.token_hex(8)
    signup_resp = user_service.signup(email=email, password=password)
    assert signup_resp.status_code in (200, 201), signup_resp.text
    payload = signup_resp.json()
    user_cleanup(payload["id"])
    user = UserPublic.model_validate(payload)
    assert user.email == email


def test_login_success(user_service, user_cleanup):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = secrets.token_hex(8)
    signup_resp = user_service.signup(email=email, password=password)
    assert signup_resp.status_code in (200, 201), signup_resp.text
    user_cleanup(signup_resp.json()["id"])
    login_resp = user_service.login(email=email, password=password)
    assert login_resp.status_code in (200, 201), login_resp.text
    token = Token.model_validate(login_resp.json())
    assert token.access_token is not None
    assert token.token_type == "bearer"


@pytest.mark.parametrize(
    ["email", "password"],
    [
        ("invalid_email", "ValidPass123"),
        ("", "ValidPass123"),
        (f"test_{uuid.uuid4().hex[:8]}@example.com", "123"),
        (f"test_{uuid.uuid4().hex[:8]}@example.com", ""),
    ],
    ids=[
        "invalid_email",
        "empty_email",
        "invalid_password",
        "empty_password",
    ],
)
def test_signup_validation(user_service, user_cleanup, email, password):
    signup_resp = user_service.signup(email=email, password=password)
    if signup_resp.status_code in (200, 201):
        user_cleanup(signup_resp.json()["id"])
    assert signup_resp.status_code == 422
