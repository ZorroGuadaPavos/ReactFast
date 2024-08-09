from fastapi.testclient import TestClient
from sqlmodel import Session

from src.core.config import settings


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