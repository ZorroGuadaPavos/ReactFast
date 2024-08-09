from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.auth.services import generate_password_reset_token, verify_password
from src.core.config import settings
from src.users.models import User


def test_get_access_token(client: TestClient, db: Session) -> None:  # noqa: ARG001
    login_data = {
        'username': settings.FIRST_SUPERUSER,
        'password': settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f'{settings.API_V1_STR}/login/access-token', data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert 'access_token' in tokens
    assert tokens['access_token']


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        'username': settings.FIRST_SUPERUSER,
        'password': 'incorrect',
    }
    r = client.post(f'{settings.API_V1_STR}/login/access-token', data=login_data)
    assert r.status_code == 400


def test_reset_password(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    token = generate_password_reset_token(email=settings.FIRST_SUPERUSER)
    data = {'new_password': 'changethis', 'token': token}
    r = client.post(
        f'{settings.API_V1_STR}/reset-password/',
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    assert r.json() == {'message': 'Password updated successfully'}

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user = db.exec(user_query).first()
    assert user
    assert verify_password(data['new_password'], user.hashed_password)


def test_reset_password_invalid_token(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    data = {'new_password': 'changethis', 'token': 'invalid'}
    r = client.post(
        f'{settings.API_V1_STR}/reset-password/',
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert 'detail' in response
    assert r.status_code == 400
    assert response['detail'] == 'Invalid token'
